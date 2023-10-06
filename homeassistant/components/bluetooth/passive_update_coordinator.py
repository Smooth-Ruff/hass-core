"""Passive update coordinator for the Bluetooth integration."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar

from homeassistant.core import CALLBACK_TYPE, callback
from homeassistant.helpers.update_coordinator import (
    BaseCoordinatorEntity,
    BaseDataUpdateCoordinatorProtocol,
)

from .update_coordinator import BasePassiveBluetoothCoordinator

if TYPE_CHECKING:
    from collections.abc import Callable, Generator

    from . import BluetoothChange, BluetoothServiceInfoBleak, BluetoothUpdateArgs

_PassiveBluetoothDataUpdateCoordinatorT = TypeVar(
    "_PassiveBluetoothDataUpdateCoordinatorT",
    bound="PassiveBluetoothDataUpdateCoordinator",
)


class PassiveBluetoothDataUpdateCoordinator(
    BasePassiveBluetoothCoordinator, BaseDataUpdateCoordinatorProtocol
):
    """Class to manage passive bluetooth advertisements.

    This coordinator is responsible for dispatching the bluetooth data
    and tracking devices.
    """

    def __init__(
        self,
        bluetoothArgs: BluetoothUpdateArgs,
    ) -> None:
        """Initialize PassiveBluetoothDataUpdateCoordinator."""
        super().__init__(bluetoothArgs)

        self.bluetoothArgs = bluetoothArgs
        self._listeners: dict[CALLBACK_TYPE, tuple[CALLBACK_TYPE, object | None]] = {}

    @callback
    def async_update_listeners(self) -> None:
        """Update all registered listeners."""
        for update_callback, _ in list(self._listeners.values()):
            update_callback()

    @callback
    def _async_handle_unavailable(
        self, service_info: BluetoothServiceInfoBleak
    ) -> None:
        """Handle the device going unavailable."""
        super()._async_handle_unavailable(service_info)
        self.async_update_listeners()

    @callback
    def async_add_listener(
        self, update_callback: CALLBACK_TYPE, context: Any = None
    ) -> Callable[[], None]:
        """Listen for data updates."""

        @callback
        def remove_listener() -> None:
            """Remove update listener."""
            self._listeners.pop(remove_listener)

        self._listeners[remove_listener] = (update_callback, context)
        return remove_listener

    def async_contexts(self) -> Generator[Any, None, None]:
        """Return all registered contexts."""
        yield from (
            context for _, context in self._listeners.values() if context is not None
        )

    @callback
    def _async_handle_bluetooth_event(
        self,
        _: BluetoothServiceInfoBleak,
        __: BluetoothChange,
    ) -> None:
        """Handle a Bluetooth event."""
        self._available = True
        self.async_update_listeners()


class PassiveBluetoothCoordinatorEntity(
    BaseCoordinatorEntity[_PassiveBluetoothDataUpdateCoordinatorT]
):
    """A class for entities using DataUpdateCoordinator."""

    async def async_update(self) -> None:
        """All updates are passive."""

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.available
