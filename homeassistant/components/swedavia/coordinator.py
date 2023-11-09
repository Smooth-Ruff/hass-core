"""DataUpdateCoordinator for the Trafikverket Train integration."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time, timedelta
import logging


from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import CONF_TIME, DOMAIN
from .util import fill_date
from .flight_data import FlightAndWaitTime
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

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        airport: str | None,
        flight_number: str | None,
        date: str | None,
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
            flight_info_api_key=entry.data[CONF_API_KEY],
            wait_time_api_key=entry.data[CONF_API_KEY],  # TODO Separate the two keys
        )

        self.airport: str = airport
        self.flight_number: str = flight_number

        self._date: date = fill_date(date)

    async def _async_update_data(self) -> FlightAndWaitTime:
        """Fetch data from Swedavia."""

        try:
            flight_info_state = await self._swedavia_api.async_get_flight_info(
                airport=self.airport,
                flight_number=self.flight_number,
                date=self._date,
            )
            wait_time_state = await self._swedavia_api.async_get_wait_time(
                airport=self.airport,
                flight_number=self.flight_number,
                date=self._date,
            )
        except (InvalidFlightInfoKey, InvalidWaitTimeKey) as error:
            raise ConfigEntryAuthFailed from error
        except (InvalidtFlightNumber, InvalidAirport) as error:
            raise UpdateFailed(
                f" Error fetching information related to flight {self.flight_number} from {self.airport}: {error}"
            ) from error

        states = FlightAndWaitTime(
            flight_info=flight_info_state,
            wait_time=wait_time_state,
        )

        return states
