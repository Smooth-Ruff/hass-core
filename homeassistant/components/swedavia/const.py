"""Adds constants for Swedavia integration."""
from homeassistant.const import Platform
from .flight_data import FlightInfo

DOMAIN = "swedavia"
PLATFORMS = [Platform.SENSOR]
ATTRIBUTION = "Data provided by Swedavia"

CONF_FROM = "from"
CONF_TO = "to"
CONF_TIME = "time"
CONF_FILTER_PRODUCT = "filter_product"

CONF_FLIGHTNUMBER = "flight_number"
CONF_HOMEAIRPORT = "home_airport"
CONF_FLIGHTINFO_APIKEY = "flight_info_key"
CONF_WAIT_TIME_APIKEY = "wait_time_key"
CONF_DATE = "flight_date"


MOCK_FLIGHTINFO = {
    "flights": [{
        "departure": {
            "flightId": "LH817",
            "arrivalAirportSwedish": "Frankfurt",
            "arrivalAirportEnglish": "Frankfurt",
            "airlineOperator": {
                "iata": "LH",
                "icao": "DLH",
                "name": "Lufthansa"
            },
            "departureTime": {
                "scheduledUtc": "2023-11-24T13:00:00Z"
            },
            "locationAndStatus": {
                "terminal": "T1",
                "flightLegStatus": "SCH",
                "flightLegStatusSwedish": "Planerad",
                "flightLegStatusEnglish": "Scheduled"
            },
            "checkIn": {
                "checkInDeskFrom": 39,
                "checkInDeskTo": 44
            },
            "codeShareData": ["A31461", "AC9613", "EY3793", "NH6192", "OS7480", "SK3619", "TP7503", "UA8803"],
            "flightLegIdentifier": {
                "callsign": "DLH6EK",
                "flightId": "LH817",
                "flightDepartureDateUtc": "2023-11-24T00:00:00Z",
                "departureAirportIata": "GOT",
                "arrivalAirportIata": "FRA",
                "departureAirportIcao": "ESGG",
                "arrivalAirportIcao": "EDDF"
            },
            "viaDestinations": [],
            "remarksEnglish": [],
            "remarksSwedish": [],
            "diIndicator": "S"
        }
    }],
    "continuationtoken": "H4sIAAAAAAAEADM0NzAwNzQyMrfQMU40MElNMjI1MzVNTU4zNTMAAgCnsq+6HwAAAA=="
}