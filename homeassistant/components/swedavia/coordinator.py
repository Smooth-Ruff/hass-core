"""DataUpdateCoordinator for the Trafikverket Train integration."""
from __future__ import annotations

from datetime import timedelta
import logging

import asyncio

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, CONF_WAIT_TIME_APIKEY, CONF_FLIGHTINFO_APIKEY
from .util import fill_date
from .flight_data import FlightAndWaitTime, WaitTime, FlightInfo
from .swedavia_wrapper import (
    SwedaviaWrapper,
    InvalidAirport,
    InvalidFlightInfoKey,
    InvalidtFlightNumber,
    InvalidWaitTimeKey,
)


_LOGGER = logging.getLogger(__name__)
TIME_BETWEEN_UPDATES = timedelta(minutes=5)


class SwedaviaDataUpdateCoordinator(DataUpdateCoordinator[FlightAndWaitTime]):
    """A Swedavia Data Update Coordinator."""

    def __init__(  # noqa: PLR0913
        self: SwedaviaDataUpdateCoordinator,
        hass: HomeAssistant,
        entry: ConfigEntry,
        airport: str,
        flight_number: str,
        date: str,
    ) -> None:
        """Initialize the Swedavia coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=TIME_BETWEEN_UPDATES,
        )
        self._swedavia_api = SwedaviaWrapper(
            async_get_clientsession(hass),
            flight_info_api_key=entry.data[CONF_FLIGHTINFO_APIKEY],
            wait_time_api_key=entry.data[CONF_WAIT_TIME_APIKEY],
        )

        self.airport: str = airport
        self.flight_number: str = flight_number

        self.hass = hass
        self._date: str = fill_date(date)

    def _update_data(self: SwedaviaDataUpdateCoordinator) -> FlightAndWaitTime:
        """Fetch data from Swedavia."""

        try:
            flight_info_state: FlightInfo = asyncio.run_coroutine_threadsafe(
                self._swedavia_api.async_get_flight_info(
                    airport=self.airport,
                    flight_number=self.flight_number,
                    date=self._date,
                ),
                self.hass.loop,
            ).result()

            wait_time_state: WaitTime = asyncio.run_coroutine_threadsafe(
                self._swedavia_api.async_get_wait_time(
                    airport=self.airport,
                    flight_number=self.flight_number,
                    date=self._date,
                ),
                self.hass.loop,
            ).result()

        except (InvalidFlightInfoKey, InvalidWaitTimeKey) as error:
            raise ConfigEntryAuthFailed from error
        except (InvalidtFlightNumber, InvalidAirport) as error:
            raise UpdateFailed(
                f" Error fetching information related to flight {self.flight_number} from {self.airport}: {error}"
            ) from error

        return FlightAndWaitTime(
            flight_info=flight_info_state,
            wait_info=wait_time_state,
        )
