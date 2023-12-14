"""Handles calls to the Swedavia APIs"""

import aiohttp

from typing import Any
from .flight_data import Departure, WaitTime
from .const import OK_HTTP


class SwedaviaWrapper:
    """Class used to communicate with Swedavia API."""

    client_session: aiohttp.ClientSession
    flight_info_api_key: str
    wait_time_api_key: str

    def __init__(
        self: Any,
        client_session: aiohttp.ClientSession,
        flight_info_api_key: str,
        wait_time_api_key: str,
    ) -> None:
        self.client_session = client_session
        self.flight_info_api_key = flight_info_api_key
        self.wait_time_api_key = wait_time_api_key

    async def async_get_client_session(self: Any) -> aiohttp.ClientSession:
        return self.client_session

    async def async_get_flight_info(
        self: Any, airport: str, date: str
    ) -> list[Departure]:
        """Fetches Swedavia FlightInfo API data through query call based on config entries."""
        url = f"https://api.swedavia.se/flightinfo/v2/{airport}/departures/{date}"

        headers = {
            "Accept": "application/json",
            "Cache-Control": "no-cache",
            "Ocp-Apim-Subscription-Key": self.flight_info_api_key,
        }

        async with self.client_session.get(url, headers=headers) as response:
            if response.status == OK_HTTP:
                data = await response.json()
                return Departure.from_dict(data)

            raise ValueError(
                f"Failed to fetch flight info. Status code: {response.status}"
            )

    async def async_get_wait_time(
        self: Any, airport: str, flight_number: str, date: str
    ) -> list[WaitTime]:
        """Fetches Swedavia WaitTime API data through call based on config entries."""
        url = f"https://api.swedavia.se/waittimepublic/v2/airports/{airport}/flights?flightid={flight_number}&date={date}"

        headers = {
            "Accept": "application/json",
            "Cache-Control": "no-cache",
            "Ocp-Apim-Subscription-Key": self.wait_time_api_key,
        }

        async with self.client_session.get(url, headers=headers) as response:
            if response.status == OK_HTTP:
                data = await response.json()
                return [
                    WaitTime.from_dict(wait_time) for wait_time in data.get("waitTimes")
                ]

            raise ValueError(
                f"Failed to fetch wait times. Status code: {response.status}"
            )


class InvalidWaitTimeKeyError(Exception):
    pass


class InvalidFlightInfoKeyError(Exception):
    pass


class InvalidtFlightNumberError(Exception):
    pass


class InvalidAirportError(Exception):
    pass
