"""Support for Swedavia API """
from __future__ import annotations

from datetime import timedelta
from datetime import datetime
import logging

from attr import dataclass

from homeassistant.components.sensor.const import SensorDeviceClass
from homeassistant.const import CONF_NAME
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity


from .coordinator import SwedaviaDataUpdateCoordinator
import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorEntity, SensorEntityDescription
from homeassistant.core import HomeAssistant, callback
from typing import Any, Callable
from collections.abc import Mapping
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType, StateType
from homeassistant.util import Throttle
from .flight_data import FlightAndWaitTime, Departure
from homeassistant.config_entries import ConfigEntry
from .flight_data import FlightInfo, WaitTime


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

MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=10)

@dataclass
class SWRequiredKeysMixinWT:
    """Mixin for required keys."""

    value_fn: Callable[[WaitTime], StateType | datetime]

@dataclass
class SWSensorEntityDescription(
    SensorEntityDescription, SWRequiredKeysMixinWT
):
    """Describes Swedavia sensor entity."""

"""
SENSOR_TYPES: tuple[SWSensorEntityDescription, ...] = (
    SWSensorEntityDescription(
        key="current_time",
        icon="mdi:clock",
        device_class=SensorDeviceClass.TIMESTAMP,
        value_fn=lambda data: data.current_time,
    ),
)
"""

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the Swedavia sensor entry."""

    coordinator: SwedaviaDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities([SwedaviaFlightandWaitTimeInfoSensor(coordinator,
                                                            entry.data[CONF_FLIGHTNUMBER],
                                                            entry.data[CONF_HOMEAIRPORT],
                                                            entry.entry_id,
                                                            entry.data[CONF_DATE])])

class SwedaviaFlightandWaitTimeInfoSensor(CoordinatorEntity[SwedaviaDataUpdateCoordinator], SensorEntity):
    """Implementation of a Swedavia Flight and WaitTime Info Sensor."""

    _attr_attribution = "Data provided by Swedavia"
    _attr_icon = "mdi:airplane"
    _state = "Placeholder state"

    def __init__(
        self,
        coordinator: SwedaviaDataUpdateCoordinator,
        flight_number: str,
        airport: str,
        entry_id: str,
        date: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._state = super().state
        self._attr_unique_id = entry_id
        self.flight_number = flight_number
        self.airport = airport
        self.date = date
        self._attr_device_info = DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, entry_id)},
        )
        self._update_attr()

    @property
    def name(self: SwedaviaFlightandWaitTimeInfoSensor) -> str:
        """Return the name of the sensor."""
        #return f"{self.airport} : {self.flight_number}"
        return "Projected waittime"
    """
    @property
    def extra_state_attributes(
        self: SwedaviaFlightandWaitTimeInfoSensor,
    ) -> Mapping[str, Any] | None:
        return self._attributes
    """

    @property
    def native_value(
        self: SwedaviaFlightandWaitTimeInfoSensor,
    ) -> str | None:
        """Return the next departure time."""
        return self._state
    @callback
    def _update_attr(self) -> None:
        self._attr_native_value = self.coordinator.data.flight_info.flights
        self._state = self.coordinator.data.wait_info[0].current_projected_wait_time

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def _handle_coordinator_update(self) -> None:
        self._update_attr()
        return super()._handle_coordinator_update()


def object_to_dict(obj: FlightAndWaitTime) -> dict[Any, Any | list[Any]]:
    result: dict[Any, Any | list[Any]] = dict()
    result["flight_info"] = obj.flight_info.to_dict()
    result["wait_info"] = [i.to_dict() for i in obj.wait_info]
    return result
