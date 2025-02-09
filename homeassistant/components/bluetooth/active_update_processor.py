"""A Bluetooth passive processor coordinator.

Collects data from advertisements but can also poll.
"""
from __future__ import annotations

from collections.abc import Callable, Coroutine
from typing import Any, Generic, TypeVar

from bleak import BleakError

from homeassistant.core import callback
from homeassistant.helpers.debounce import Debouncer
from homeassistant.util.dt import monotonic_time_coarse

from . import BluetoothChange, BluetoothServiceInfoBleak, BluetoothUpdateArgs
from .passive_update_processor import PassiveBluetoothProcessorCoordinator

POLL_DEFAULT_COOLDOWN = 10
POLL_DEFAULT_IMMEDIATE = True

_T = TypeVar("_T")


class ActiveBluetoothProcessorCoordinator(
    Generic[_T], PassiveBluetoothProcessorCoordinator[_T]
):
    """A processor coordinator that parses passive data.

    Parses passive data from advertisements but can also poll.

    Every time an advertisement is received, needs_poll_method is called to work
    out if a poll is needed. This should return True if it is and False if it is
    not needed.

    def needs_poll_method(
        svc_info: BluetoothServiceInfoBleak,
        last_poll: float | None
    ) -> bool:
        return True

    If there has been no poll since HA started, `last_poll` will be None.
    Otherwise it is the number of seconds since one was last attempted.

    If a poll is needed, the coordinator will call poll_method. This is a coroutine.
    It should return the same type of data as your update_method. The expectation is
    that data from advertisements and from polling are being parsed and fed into a
    shared object that represents the current state of the device.

    async def poll_method(svc_info: BluetoothServiceInfoBleak) -> YourDataType:
        return YourDataType(....)

    BluetoothServiceInfoBleak.device contains a BLEDevice. You should use this in
    your poll function, as it is the most efficient way to get a BleakClient.
    """

    # Ignore the 'Too many arguments'
    # Because it couldn't get down any lower from the previous 10
    # 6 is a 40% improvement compared to 10.
    def __init__(  # noqa: PLR0913
        self,
        bluetoothArgs: BluetoothUpdateArgs,
        *,
        update_method: Callable[[BluetoothServiceInfoBleak], _T],
        needs_poll_method: Callable[[BluetoothServiceInfoBleak, float | None], bool],
        poll_method: Callable[
            [BluetoothServiceInfoBleak],
            Coroutine[Any, Any, _T],
        ]
        | None = None,
        poll_debouncer: Debouncer[Coroutine[Any, Any, None]] | None = None,
    ) -> None:
        """Initialize the processor."""
        super().__init__(
            bluetoothArgs,
            update_method,
        )

        self.bluetoothArgs = bluetoothArgs
        self._needs_poll_method = needs_poll_method
        self._poll_method = poll_method
        self._last_poll: float | None = None
        self.last_poll_successful = True

        # We keep the last service info in case the poller needs to refer to
        # e.g. its BLEDevice
        self._last_service_info: BluetoothServiceInfoBleak | None = None

        if poll_debouncer is None:
            poll_debouncer = Debouncer(
                bluetoothArgs.hass,
                bluetoothArgs.logger,
                cooldown=POLL_DEFAULT_COOLDOWN,
                immediate=POLL_DEFAULT_IMMEDIATE,
                function=self._async_poll,
            )
        else:
            poll_debouncer.function = self._async_poll

        self._debounced_poll = poll_debouncer

    def needs_poll(self, service_info: BluetoothServiceInfoBleak) -> bool:
        """Return true if time to try and poll."""
        if self.bluetoothArgs.hass.is_stopping:
            return False
        poll_age: float | None = None
        if self._last_poll:
            poll_age = service_info.time - self._last_poll
        return self._needs_poll_method(service_info, poll_age)

    async def _async_poll_data(
        self, last_service_info: BluetoothServiceInfoBleak
    ) -> _T:
        """Fetch the latest data from the source."""
        if self._poll_method is None:
            raise NotImplementedError("Poll method not implemented")
        return await self._poll_method(last_service_info)

    async def _async_poll(self) -> None:
        """Poll the device to retrieve any extra data."""
        assert self._last_service_info

        try:
            update = await self._async_poll_data(self._last_service_info)
        except BleakError as exc:
            if self.last_poll_successful:
                self.bluetoothArgs.logger.error(
                    "%s: Bluetooth error whilst polling: %s",
                    self.bluetoothArgs.address,
                    str(exc),
                )
                self.last_poll_successful = False
            return
        except Exception:  # pylint: disable=broad-except
            if self.last_poll_successful:
                self.bluetoothArgs.logger.exception(
                    "%s: Failure while polling", self.bluetoothArgs.address
                )
                self.last_poll_successful = False
            return
        finally:
            self._last_poll = monotonic_time_coarse()

        if not self.last_poll_successful:
            self.bluetoothArgs.logger.debug(
                "%s: Polling recovered", self.bluetoothArgs.address
            )
            self.last_poll_successful = True

        for processor in self._processors:
            processor.async_handle_update(update)

    @callback
    def _async_handle_bluetooth_event(
        self,
        service_info: BluetoothServiceInfoBleak,
        change: BluetoothChange,
    ) -> None:
        """Handle a Bluetooth event."""
        super()._async_handle_bluetooth_event(service_info, change)

        self._last_service_info = service_info

        # See if its time to poll
        # We use bluetooth events to trigger the poll so that we scan as soon as
        # possible after a device comes online or back in range, if a poll is due
        if self.needs_poll(service_info):
            self.bluetoothArgs.hass.async_create_task(self._debounced_poll.async_call())

    @callback
    def _async_stop(self) -> None:
        """Cancel debouncer and stop the callbacks."""
        self._debounced_poll.async_cancel()
        super()._async_stop()
