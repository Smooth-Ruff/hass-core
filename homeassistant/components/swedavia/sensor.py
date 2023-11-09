"""Support for Swedavia API """
from __future__ import annotations

from datetime import timedelta
import logging
import aiohttp


from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .coordinator import SwedaviaDataUpdateCoordinator
from .swedavia_wrapper import SwedaviaWrapper
import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorEntity
from homeassistant.const import CONF_DELAY, CONF_NAME
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.util import Throttle
from homeassistant.util.dt import now
from .flight_data import FlightAndWaitTime, Flight, WaitTime

_LOGGER = logging.getLogger(__name__)

ATTR_ACCESSIBILITY = "accessibility"
ATTR_DIRECTION = "direction"
ATTR_LINE = "line"
ATTR_TRACK = "track"

CONF_DEPARTURES = "departures"
CONF_FROM = "from"
CONF_HEADING = "heading"
CONF_LINES = "lines"
CONF_KEY = "key"
CONF_SECRET = "secret"

CONF_FLIGHT_NUMBER = "flight_number"
CONF_AIRPORT = "home_airport"
CONF_DATE = "date"

DOMAIN = "swedavia"

DEFAULT_DELAY = 0


MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=120)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_KEY): cv.string,
        vol.Required(CONF_SECRET): cv.string,
        vol.Required(CONF_DEPARTURES): [
            {
                vol.Required(CONF_FROM): cv.string,
                vol.Optional(CONF_DELAY, default=DEFAULT_DELAY): cv.positive_int,
                vol.Optional(CONF_HEADING): cv.string,
                vol.Optional(CONF_LINES, default=[]): vol.All(
                    cv.ensure_list, [cv.string]
                ),
                vol.Optional(CONF_NAME): cv.string,
            }
        ],
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

    coordinator: SwedaviaDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    sensors.append(
        SwedaviaFlightandWaitTimeInfoSensor(
            SwedaviaDataUpdateCoordinator(
                hass=hass,
                entry=?,
                airport=config.get(CONF_AIRPORT),
                flight_number=config.get(CONF_FLIGHT_NUMBER),
                date=config.get(CONF_DATE),
            ),
            config.get(CONF_FLIGHT_NUMBER),
            config.get(CONF_AIRPORT),
            config.get(CONF_DATE),
        )
    )
    add_entities(sensors, True)


class SwedaviaFlightandWaitTimeInfoSensor(SensorEntity):
    """Implementation of a Swedavia Flight and WaitTime Info Sensor."""

    _attr_attribution = "Data provided by Swedavia"
    _attr_icon = "mdi:flight"

    def __init__(self, swedavia_coordinator, flight_number, airport, date):
        """Initialize the sensor."""
        self._coordinator = swedavia_coordinator
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
        self._state = self._coordinator._async_update_data()
