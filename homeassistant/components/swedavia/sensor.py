"""Support for Swedavia API """
from __future__ import annotations

from datetime import timedelta
import logging


from .coordinator import SwedaviaDataUpdateCoordinator
import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorEntity
from homeassistant.core import HomeAssistant
from typing import Any
from collections.abc import Mapping
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.util import Throttle
from .flight_data import FlightAndWaitTime, Departure
from homeassistant.config_entries import ConfigEntry


from .const import (
    CONF_FLIGHTINFO_APIKEY,
    CONF_FLIGHTNUMBER,
    CONF_HOMEAIRPORT,
    CONF_WAIT_TIME_APIKEY,
    CONF_DATE,
)


_LOGGER = logging.getLogger(__name__)

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
    _: DiscoveryInfoType | None = None,
) -> None:
    """Set up the flight info sensor."""
    sensors = []

    mapping = dict()
    mapping[CONF_FLIGHTINFO_APIKEY] = config.get(CONF_FLIGHTINFO_APIKEY)
    mapping[CONF_WAIT_TIME_APIKEY] = config.get(CONF_WAIT_TIME_APIKEY)

    config_entry: ConfigEntry = ConfigEntry(
        domain=DOMAIN, data=mapping, version=1, title=DOMAIN, source=DOMAIN
    )

    sensors.append(
        SwedaviaFlightandWaitTimeInfoSensor(
            SwedaviaDataUpdateCoordinator(
                hass=hass,
                entry=config_entry,
                airport=str(config.get(CONF_HOMEAIRPORT)),
                flight_number=str(config.get(CONF_FLIGHTNUMBER)),
                date=str(config.get(CONF_DATE)),
            ),
            str(config.get(CONF_FLIGHTNUMBER)),
            str(config.get(CONF_HOMEAIRPORT)),
            str(config.get(CONF_DATE)),
        )
    )
    add_entities(sensors, True)


class SwedaviaFlightandWaitTimeInfoSensor(SensorEntity):
    """Implementation of a Swedavia Flight and WaitTime Info Sensor."""

    _attr_attribution = "Data provided by Swedavia"
    _attr_icon = "mdi:flight"

    def __init__(
        self: SwedaviaFlightandWaitTimeInfoSensor,
        swedavia_coordinator: SwedaviaDataUpdateCoordinator,
        flight_number: str,
        airport: str,
        date: str,
    ) -> None:
        """Initialize the sensor."""
        self._coordinator: SwedaviaDataUpdateCoordinator = swedavia_coordinator
        self._name = flight_number or airport
        self._state: str | None = None
        self._attributes: dict[Any, Any] = dict()
        self._date = date

    @property
    def name(self: SwedaviaFlightandWaitTimeInfoSensor) -> str:
        """Return the name of the sensor."""
        return self._name

    @property
    def extra_state_attributes(
        self: SwedaviaFlightandWaitTimeInfoSensor,
    ) -> Mapping[str, Any] | None:
        """Return the state attributes."""
        return self._attributes

    @property
    def native_value(
        self: SwedaviaFlightandWaitTimeInfoSensor,
    ) -> str | None:
        """Return the next departure time."""
        return self._state

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self: SwedaviaFlightandWaitTimeInfoSensor) -> None:
        """Get the departure board."""
        update: FlightAndWaitTime = self._coordinator.update_data()
        self._attributes = object_to_dict(update)
        self._state = (
            update.flight_info.flights[
                0
            ].departure.location_and_status.flight_leg_status
            if len(update.flight_info.flights) >= 1
            and hasattr(update.flight_info.flights[0], "departure")
            and type(update.flight_info.flights[0].departure) is Departure
            else "Unknown"
        )


def object_to_dict(obj: FlightAndWaitTime) -> dict[Any, Any | list[Any]]:
    result: dict[Any, Any | list[Any]] = dict()
    result["flight_info"] = obj.flight_info.to_dict()
    result["wait_info"] = [i.to_dict() for i in obj.wait_info]
    return result
