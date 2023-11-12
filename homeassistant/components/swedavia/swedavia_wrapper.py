import aiohttp


from homeassistant.core import HomeAssistant
from .flight_data import Flight, WaitTime


class SwedaviaWrapper:
    """Class used to communicate with Swedavia's api."""

    client_session: aiohttp.ClientSession
    flight_info_api_key: str
    wait_time_api_key: str

    
    def __init__(
        self,
        client_session: aiohttp.ClientSession,
        flight_info_api_key: str,
        wait_time_api_key: str,
    ) -> None:
        self.client_session = client_session
        self.flight_info_api_key = flight_info_api_key
        self.wait_time_api_key = wait_time_api_key

    async def async_get_client_session(
        self, hass: HomeAssistant, verify_ssl=True
    ) -> aiohttp.ClientSession:
        return self.client_session

    async def async_get_flight_info(
        self, airport: str, flight_number: str, date: str
    ) -> Flight:
        pass

    async def async_get_wait_time(
        self, airport: str, flight_number: str, date: str
    ) -> WaitTime:
        pass


class InvalidWaitTimeKey(Exception):
    pass


class InvalidFlightInfoKey(Exception):
    pass


class InvalidtFlightNumber(Exception):
    pass


class InvalidAirport(Exception):
    pass
