import aiohttp


from homeassistant.core import HomeAssistant
from .flight_data import FlightInfo, WaitTime


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
    ) -> FlightInfo:
        base_url = "https://api.swedavia.se/flightinfo/v2/query"
        flight_type = 'D'
        filter_params = f"airport eq '{airport}' and scheduled eq '{scheduled}' and flightType eq '{flight_type}' and flightId eq '{flight_number}'"
        url = f"{base_url}?filter={filter_params}"
    
        headers = {
            "Accept": "application/json",
            "Cache-Control": "no-cache",
            "Ocp-Apim-Subscription-Key": self.flight_info_api_key,
        }
    
        async with client_session.get(url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                return FlightInfo.from_dict(data)
    
            else:
                raise Exception(
                    f"Failed to fetch flight info. Status code: {response.status}"
                )

    async def async_get_wait_time(
        self, airport: str, flight_number: str, date: str
    ) -> [WaitTime]:
        url = f"https://api.swedavia.se/waittimepublic/v2/airports/{airport}/flights?flightid={flight_number}&date={date}"

        headers = {
            'Accept': 'application/json',
            'Cache-Control': 'no-cache',
            'Ocp-Apim-Subscription-Key': self.wait_time_api_key,
        }

        async with client_session.get(url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                return [WaitTime.from_dict(wait_time) for wait_time in data.get("waitTimes")]
            else:
                raise Exception(f"Failed to fetch wait times. Status code: {response.status}")


class InvalidWaitTimeKey(Exception):
    pass


class InvalidFlightInfoKey(Exception):
    pass


class InvalidtFlightNumber(Exception):
    pass


class InvalidAirport(Exception):
    pass
