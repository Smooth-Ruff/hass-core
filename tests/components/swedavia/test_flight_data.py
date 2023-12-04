"""Testing Flight Data parsing."""
import pytest

from homeassistant.components.swedavia.flight_data import Flight, WaitTime


@pytest.mark.parametrize(
    "raw_wait_info",
    [
        {
            "id": 2,
            "queueName": "Security Landvetter FastTrack",
            "currentTime": "2023-12-04T09:52:47Z",
            "currentProjectedWaitTime": 2,
            "isFastTrack": True,
            "terminal": None,
            "latitude": 57.66869,
            "longitude": 12.29521,
            "overflow": False,
        },
        {
            "id": 3,
            "queueName": "Security Landvetter",
            "currentTime": "2023-12-04T09:52:47Z",
            "currentProjectedWaitTime": 7,
            "isFastTrack": False,
            "terminal": None,
            "latitude": 57.66869,
            "longitude": 12.29521,
            "overflow": False,
        },
    ],
)
def test_wait_info(raw_wait_info: dict):
    """Test parsing wait info data."""
    wait_info_object = WaitTime.from_dict(raw_wait_info)
    result = WaitTime.to_dict(wait_info_object)

    assert result["id"] == raw_wait_info["id"]
    assert result["queueName"] == raw_wait_info["queueName"]
    assert result["terminal"] == raw_wait_info["terminal"]
    assert result["isFastTrack"] == raw_wait_info["isFastTrack"]
    assert result["latitude"] == raw_wait_info["latitude"]
    assert result["longitude"] == raw_wait_info["longitude"]
    assert result["overflow"] == raw_wait_info["overflow"]


@pytest.mark.parametrize(
    "raw_flight_info",
    [
        {
            "departure": {
                "flightId": "SK431",
                "arrivalAirportSwedish": "Köpenhamn",
                "arrivalAirportEnglish": "Copenhagen",
                "airlineOperator": {
                    "iata": "SK",
                    "icao": "SAS",
                    "name": "SAS Scandinavian Airlines",
                },
                "locationAndStatus": {
                    "terminal": "T1",
                    "flightLegStatus": "SCH",
                    "flightLegStatusSwedish": "Planerad",
                    "flightLegStatusEnglish": "Scheduled",
                },
                "checkIn": {"checkInDeskFrom": 33, "checkInDeskTo": 38},
                "codeShareData": ["FI7503", "LH6229", "LX4771", "OS7570"],
                "flightLegIdentifier": {
                    "callsign": "SAS431",
                    "aircraftRegistration": "ESATE",
                    "flightId": "SK431",
                    "departureAirportIata": "GOT",
                    "arrivalAirportIata": "CPH",
                    "departureAirportIcao": "ESGG",
                    "arrivalAirportIcao": "EKCH",
                },
                "viaDestinations": [],
                "remarksEnglish": [],
                "remarksSwedish": [],
                "diIndicator": "S",
            }
        }
    ],
)
def test_flight_info(raw_flight_info: dict):
    """Test parsing flight info data."""
    flight_object = Flight.from_dict(raw_flight_info)

    if hasattr(raw_flight_info, "arrival"):
        assert hasattr(flight_object, "arrival")
        assert flight_object.arrival.flight_id == raw_flight_info["arrival"]["flightId"]
        assert (
            flight_object.arrival.airline_operator.iata
            == raw_flight_info["arrival"]["airline_operator"]["iata"]
        )

    if hasattr(raw_flight_info, "departure"):
        assert hasattr(flight_object, "departure")
        assert (
            flight_object.departure.flight_id
            == raw_flight_info["departure"]["flightId"]
        )
        assert (
            flight_object.departure.airline_operator.iata
            == raw_flight_info["departure"]["airline_operator"]["iata"]
        )
