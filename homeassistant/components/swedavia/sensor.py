"""Support for Swedavia API """
from __future__ import annotations

from datetime import timedelta
import logging


from .coordinator import SwedaviaDataUpdateCoordinator
import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorEntity
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.util import Throttle
from .flight_data import FlightAndWaitTime
from homeassistant.config_entries import ConfigEntry

_LOGGER = logging.getLogger(__name__)


from .const import (
    CONF_FLIGHTINFO_APIKEY,
    CONF_FLIGHTNUMBER,
    CONF_HOMEAIRPORT,
    CONF_WAIT_TIME_APIKEY,
    CONF_DATE,
)

ATTR_ACCESSIBILITY = "accessibility"
ATTR_DIRECTION = "direction"
ATTR_LINE = "line"
ATTR_TRACK = "track"


DOMAIN = "swedavia"

DEFAULT_DELAY = 0


MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=120)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_FLIGHTINFO_APIKEY): cv.string,
        vol.Required(CONF_WAIT_TIME_APIKEY): cv.string,
        vol.Required(CONF_HOMEAIRPORT): cv.string,
        vol.Required(CONF_FLIGHTNUMBER): cv.string,
        vol.Optional(CONF_DATE): cv.string,
    }
)


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the flight info sensor."""
    sensors = []

    mapping = dict()
    mapping[CONF_FLIGHTINFO_APIKEY] = config.get(CONF_FLIGHTINFO_APIKEY)
    mapping[CONF_WAIT_TIME_APIKEY] = config.get(CONF_WAIT_TIME_APIKEY)

    configEntry: ConfigEntry = ConfigEntry(
        domain=DOMAIN, data=mapping, version="0.1", title=DOMAIN, source=DOMAIN
    )

    sensors.append(
        SwedaviaFlightandWaitTimeInfoSensor(
            SwedaviaDataUpdateCoordinator(
                hass=hass,
                entry=configEntry,
                airport=config.get(CONF_HOMEAIRPORT),
                flight_number=config.get(CONF_FLIGHTNUMBER),
                date=config.get(CONF_DATE),
            ),
            config.get(CONF_FLIGHTNUMBER),
            config.get(CONF_HOMEAIRPORT),
            config.get(CONF_DATE),
        )
    )
    add_entities(sensors, True)


class SwedaviaFlightandWaitTimeInfoSensor(SensorEntity):
    """Implementation of a Swedavia Flight and WaitTime Info Sensor."""

    _attr_attribution = "Data provided by Swedavia"
    _attr_icon = "mdi:flight"

    def __init__(
        self,
        swedavia_coordinator: SwedaviaDataUpdateCoordinator,
        flight_number,
        airport,
        date,
    ) -> None:
        """Initialize the sensor."""
        self._coordinator: SwedaviaDataUpdateCoordinator = swedavia_coordinator
        self._name = flight_number or airport
        self._state: FlightAndWaitTime | None = None
        self._attributes = None
        self._date = date

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return self._attributes

    @property
    def native_value(self):
        """Return the next departure time."""
        return self._state

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self) -> None:
        """Get the departure board."""
        update : FlightAndWaitTime = self._coordinator._update_data()
        self._attributes = object_to_dict(update)
        self._state = update.flight_info.flights[0].departure.location_and_status.flight_leg_status if len(update.flight_info.flights)>=1 and hasattr(update.flight_info.flights[0],"departure") else "Unknown"


def object_to_dict(obj):
    if isinstance(obj, (int, float, str, bool)):
        return obj
    elif isinstance(obj, list):
        return [object_to_dict(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(object_to_dict(item) for item in obj)
    elif isinstance(obj, dict):
        return {key: object_to_dict(value) for key, value in obj.items()}
    elif obj is None:
        return None
    elif hasattr(obj, "__dict__"):
        return object_to_dict(obj.__dict__)
    else:
        return str(obj)
