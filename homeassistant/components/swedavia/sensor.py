"""Support for Swedavia API """
from __future__ import annotations

from datetime import timedelta
from datetime import datetime
import logging

from attr import dataclass

from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity


from .coordinator import SwedaviaDataUpdateCoordinator


from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.core import HomeAssistant, callback
from typing import Any
from collections.abc import Callable

from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.util import Throttle
from .flight_data import FlightAndWaitTime
from homeassistant.config_entries import ConfigEntry


from .const import (
    CONF_FLIGHTNUMBER,
    CONF_HOMEAIRPORT,
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
class SWRequiredKeysMixin:
    """Mixin for required keys."""

    key: str
    title: str
    image: str
    value_fn: Callable[[FlightAndWaitTime], StateType | datetime]


@dataclass
class SWSensorEntityDescription(SensorEntityDescription, SWRequiredKeysMixin):
    """Describes Swedavia sensor entity."""


SENSOR_TYPES: tuple[SWSensorEntityDescription, ...] = (
    SWSensorEntityDescription(
        key="wait_time",
        title="Projected Wait Time",
        image="mdi:airplane-clock",
        value_fn=lambda data: data.wait_info[0].current_projected_wait_time,
    ),
    SWSensorEntityDescription(
        key="current_time",
        title="Current Time",
        image="mdi:clock",
        value_fn=lambda data: data.wait_info[0].current_time,
    ),
    SWSensorEntityDescription(
        key="flight_id",
        title="Flight ID",
        image="mdi:airplane",
        value_fn=lambda data: data.flight_info[0].flight_id,
    ),
    SWSensorEntityDescription(
        key="departure_time",
        title="Departure Time",
        image="mdi:airplane",
        value_fn=lambda data: data.flight_info[0].departure_time,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the Swedavia sensor entry."""

    coordinator: SwedaviaDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        [
            SwedaviaFlightandWaitTimeInfoSensor(
                coordinator,
                entry.data[CONF_FLIGHTNUMBER],
                entry.data[CONF_HOMEAIRPORT],
                entry.entry_id,
                entry.data[CONF_DATE],
                description,
            )
            for description in SENSOR_TYPES
        ]
    )


class SwedaviaFlightandWaitTimeInfoSensor(
    CoordinatorEntity[SwedaviaDataUpdateCoordinator], SensorEntity
):
    """Implementation of a Swedavia FlightInfo and WaitTime Info Sensor."""

    _attr_attribution = "Data provided by Swedavia"
    _attr_icon = "mdi:airplane"
    _state = "Placeholder state"

    def __init__( # noqa
        self: Any,
        coordinator: SwedaviaDataUpdateCoordinator,
        flight_number: str,
        airport: str,
        entry_id: str,
        date: str,
        description: SWSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_icon = description.image
        self._state = super().state
        self.description = description
        self._attr_unique_id = f"{entry_id}--{description.key}"
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
        """Returns the name of the sensor."""
        return self.description.title

    @property
    def native_value(
        self: SwedaviaFlightandWaitTimeInfoSensor,
    ) -> str | None:
        """Returns the next departure time."""
        return self._state

    @callback
    def _update_attr(self: Any) -> None:
        """Updates sensor attributes."""
        self._attr_native_value = self.description.value_fn(self.coordinator.data)
        self._state = self.description.value_fn(self.coordinator.data)

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def _handle_coordinator_update(self: Any) -> None:
        """Calls for coordinator update with updated attributes."""
        self._update_attr()
        return super()._handle_coordinator_update()


def object_to_dict(obj: FlightAndWaitTime) -> dict[Any, Any | list[Any]]:
    """Add FlightAndWaitTime object data to dict item."""
    result: dict[Any, Any | list[Any]] = dict()
    result["flight_info"] = [i.to_dict() for i in obj.flight_info]
    result["wait_info"] = [i.to_dict() for i in obj.wait_info]
    return result
