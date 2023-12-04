"""Dataclasses and associated methods for the Swedavia integration."""
from dataclasses import dataclass
from datetime import date
from typing import Any, List, Optional, TypeVar, Callable, Type, cast
from datetime import datetime
import dateutil.parser


T = TypeVar("T")


def from_str(x: Any) -> str:
    """Returns string from input."""
    #assert isinstance(x, str)
    return x


def from_datetime(x: Any) -> datetime:
    """Returns datetime from input, current datetime if input invalid."""
    if not x:
        return datetime.now()
    return dateutil.parser.parse(x)


def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    """Returns new list based on function f applied on list x, returns empty list if x is None."""
    if x is None:
        return []
    assert isinstance(x, list)
    return [f(y) for y in x]


def to_class(c: Type[T], x: Any) -> dict:
    """Returns dict containing objects of class c."""
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


def from_none(x: Any) -> Any:
    """Asserts None input."""
    assert x is None
    return x


def from_union(fs, x):
    """Iterates through functions on x."""
    for f in fs:
        try:
            return f(x)
        except:
            pass
    assert False


class AirlineOperator:
    """Class for Swedavia airline operators and helper methods."""
    iata: str
    icao: str
    name: str

    def __init__(self, iata: str, icao: str, name: str) -> None:
        self.iata = iata
        self.icao = icao
        self.name = name

    @staticmethod
    def from_dict(obj: Any) -> "AirlineOperator":
        """Return AirlineOperator object from dict."""
        assert isinstance(obj, dict)
        iata = from_str(obj.get("iata"))
        icao = from_str(obj.get("icao"))
        name = from_str(obj.get("name"))
        return AirlineOperator(iata, icao, name)

    def to_dict(self) -> dict:
        """Add AirlineOperator data to dict item."""
        result: dict = {}
        result["iata"] = from_str(self.iata)
        result["icao"] = from_str(self.icao)
        result["name"] = from_str(self.name)
        return result


class Time:
    """Class for UTC time."""
    scheduled_utc: datetime

    def __init__(self, scheduled_utc: datetime) -> None:
        self.scheduled_utc = scheduled_utc

    @staticmethod
    def from_dict(obj: Any) -> str:
        """Return formatted datetime string."""
        assert isinstance(obj, dict)
        scheduled_utc = from_str(obj.get("scheduledUtc"))
        formatted_string = datetime.strptime(scheduled_utc, "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d %H:%M:%S")
        return formatted_string

    def to_dict(self) -> dict:
        """Add schduledUtc to dict item."""
        result: dict = {}
        result["scheduledUtc"] = self.scheduled_utc.isoformat()
        return result


class Baggage:
    """Class for Swedavia Baggage."""
    pass

    def __init__(
        self,
    ) -> None:
        pass

    @staticmethod
    def from_dict(obj: Any) -> "Baggage":
        """Returns Baggage object."""
        assert isinstance(obj, dict)
        return Baggage()

    def to_dict(self) -> dict:
        """Add Baggage to dict item."""
        result: dict = {}
        return result


class FlightLegIdentifier:
    """Class for Swedavia Flight Information."""
    callsign: str
    flight_id: str
    flight_departure_date_utc: datetime
    departure_airport_iata: str
    arrival_airport_iata: str
    departure_airport_icao: str
    arrival_airport_icao: str

    def __init__(
        self,
        callsign: str,
        flight_id: str,
        flight_departure_date_utc: datetime,
        departure_airport_iata: str,
        arrival_airport_iata: str,
        departure_airport_icao: str,
        arrival_airport_icao: str,
    ) -> None:
        self.callsign = callsign
        self.flight_id = flight_id
        self.flight_departure_date_utc = flight_departure_date_utc
        self.departure_airport_iata = departure_airport_iata
        self.arrival_airport_iata = arrival_airport_iata
        self.departure_airport_icao = departure_airport_icao
        self.arrival_airport_icao = arrival_airport_icao

    @staticmethod
    def from_dict(obj: Any) -> "FlightLegIdentifier":
        """Returns FlightLegIdentifier object."""
        assert isinstance(obj, dict)
        callsign = from_str(obj.get("callsign"))
        flight_id = from_str(obj.get("flightId"))
        flight_departure_date_utc = from_datetime(obj.get("flightDepartureDateUtc", ""))
        departure_airport_iata = from_str(obj.get("departureAirportIata"))
        arrival_airport_iata = from_str(obj.get("arrivalAirportIata"))
        departure_airport_icao = from_str(obj.get("departureAirportIcao"))
        arrival_airport_icao = from_str(obj.get("arrivalAirportIcao"))
        return FlightLegIdentifier(
            callsign,
            flight_id,
            flight_departure_date_utc,
            departure_airport_iata,
            arrival_airport_iata,
            departure_airport_icao,
            arrival_airport_icao,
        )

    def to_dict(self) -> dict:
        """Add FlightLegIdentifier data to dict item."""
        result: dict = {}
        result["callsign"] = from_str(self.callsign)
        result["flightId"] = from_str(self.flight_id)
        result["flightDepartureDateUtc"] = self.flight_departure_date_utc.isoformat()
        result["departureAirportIata"] = from_str(self.departure_airport_iata)
        result["arrivalAirportIata"] = from_str(self.arrival_airport_iata)
        result["departureAirportIcao"] = from_str(self.departure_airport_icao)
        result["arrivalAirportIcao"] = from_str(self.arrival_airport_icao)
        return result


class LocationAndStatus:
    """Class for Swedavia Airport Information."""
    terminal: str
    flight_leg_status: str
    flight_leg_status_swedish: str
    flight_leg_status_english: str

    def __init__(
        self,
        terminal: str,
        flight_leg_status: str,
        flight_leg_status_swedish: str,
        flight_leg_status_english: str,
    ) -> None:
        self.terminal = terminal
        self.flight_leg_status = flight_leg_status
        self.flight_leg_status_swedish = flight_leg_status_swedish
        self.flight_leg_status_english = flight_leg_status_english

    @staticmethod
    def from_dict(obj: Any) -> "LocationAndStatus":
        """Returns LocationAndStatus object."""
        assert isinstance(obj, dict)
        terminal = from_str(obj.get("terminal"))
        flight_leg_status = from_str(obj.get("flightLegStatus"))
        flight_leg_status_swedish = from_str(obj.get("flightLegStatusSwedish"))
        flight_leg_status_english = from_str(obj.get("flightLegStatusEnglish"))
        return LocationAndStatus(
            terminal,
            flight_leg_status,
            flight_leg_status_swedish,
            flight_leg_status_english,
        )

    def to_dict(self) -> dict:
        """Add LocationAndStatus data to dict item."""
        result: dict = {}
        result["terminal"] = from_str(self.terminal)
        result["flightLegStatus"] = from_str(self.flight_leg_status)
        result["flightLegStatusSwedish"] = from_str(self.flight_leg_status_swedish)
        result["flightLegStatusEnglish"] = from_str(self.flight_leg_status_english)
        return result


class Arrival:
    """Class for Swedavia Flight Arrival Information."""
    flight_id: str
    departure_airport_swedish: str
    departure_airport_english: str
    airline_operator: AirlineOperator
    arrival_time: Time
    location_and_status: LocationAndStatus
    baggage: Baggage
    code_share_data: List[Any]
    flight_leg_identifier: FlightLegIdentifier
    remarks_english: List[Any]
    remarks_swedish: List[Any]
    via_destinations: List[Any]
    di_indicator: str

    def __init__(
        self,
        flight_id: str,
        departure_airport_swedish: str,
        departure_airport_english: str,
        airline_operator: AirlineOperator,
        arrival_time: Time,
        location_and_status: LocationAndStatus,
        baggage: Baggage,
        code_share_data: List[Any],
        flight_leg_identifier: FlightLegIdentifier,
        remarks_english: List[Any],
        remarks_swedish: List[Any],
        via_destinations: List[Any],
        di_indicator: str,
    ) -> None:
        self.flight_id = flight_id
        self.departure_airport_swedish = departure_airport_swedish
        self.departure_airport_english = departure_airport_english
        self.airline_operator = airline_operator
        self.arrival_time = arrival_time
        self.location_and_status = location_and_status
        self.baggage = baggage
        self.code_share_data = code_share_data
        self.flight_leg_identifier = flight_leg_identifier
        self.remarks_english = remarks_english
        self.remarks_swedish = remarks_swedish
        self.via_destinations = via_destinations
        self.di_indicator = di_indicator

    @staticmethod
    def from_dict(obj: Any) -> "Arrival":
        """Returns Arrival object."""
        assert isinstance(obj, dict)
        flight_id = from_str(obj.get("flightId"))
        departure_airport_swedish = from_str(obj.get("departureAirportSwedish"))
        departure_airport_english = from_str(obj.get("departureAirportEnglish"))
        airline_operator = AirlineOperator.from_dict(obj.get("airlineOperator"))
        arrival_time = Time.from_dict(obj.get("arrivalTime"))
        location_and_status = LocationAndStatus.from_dict(obj.get("locationAndStatus"))
        baggage = Baggage.from_dict(obj.get("baggage"))
        code_share_data = from_list(lambda x: x, obj.get("codeShareData"))
        flight_leg_identifier = FlightLegIdentifier.from_dict(
            obj.get("flightLegIdentifier")
        )
        remarks_english = from_list(lambda x: x, obj.get("remarksEnglish"))
        remarks_swedish = from_list(lambda x: x, obj.get("remarksSwedish"))
        via_destinations = from_list(lambda x: x, obj.get("viaDestinations"))
        di_indicator = from_str(obj.get("diIndicator"))
        return Arrival(
            flight_id,
            departure_airport_swedish,
            departure_airport_english,
            airline_operator,
            arrival_time,
            location_and_status,
            baggage,
            code_share_data,
            flight_leg_identifier,
            remarks_english,
            remarks_swedish,
            via_destinations,
            di_indicator,
        )

    def to_dict(self) -> dict:
        """Add Arrival data to dict item."""
        result: dict = {}
        result["flightId"] = from_str(self.flight_id)
        result["departureAirportSwedish"] = from_str(self.departure_airport_swedish)
        result["departureAirportEnglish"] = from_str(self.departure_airport_english)
        result["airlineOperator"] = to_class(AirlineOperator, self.airline_operator)
        result["arrivalTime"] = to_class(Time, self.arrival_time)
        result["locationAndStatus"] = to_class(
            LocationAndStatus, self.location_and_status
        )
        result["baggage"] = to_class(Baggage, self.baggage)
        result["codeShareData"] = from_list(lambda x: x, self.code_share_data)
        result["flightLegIdentifier"] = to_class(
            FlightLegIdentifier, self.flight_leg_identifier
        )
        result["remarksEnglish"] = from_list(lambda x: x, self.remarks_english)
        result["remarksSwedish"] = from_list(lambda x: x, self.remarks_swedish)
        result["viaDestinations"] = from_list(lambda x: x, self.via_destinations)
        result["diIndicator"] = from_str(self.di_indicator)
        return result

@dataclass
class Departure:
    """Class for Swedavia Flight Departure Information."""
    flight_id: str
    arrival_airport_swedish: str
    arrival_airport_english: str
    airline_operator: AirlineOperator
    departure_time: Time
    location_and_status: LocationAndStatus
    check_in: Baggage
    code_share_data: List[Any]
    flight_leg_identifier: FlightLegIdentifier
    via_destinations: List[Any]
    remarks_english: List[Any]
    remarks_swedish: List[Any]
    di_indicator: str

    def __init__(
        self,
        flight_id: str,
        arrival_airport_swedish: str,
        arrival_airport_english: str,
        airline_operator: AirlineOperator,
        departure_time: datetime,
        location_and_status: LocationAndStatus,
        check_in: Baggage,
        code_share_data: List[Any],
        flight_leg_identifier: FlightLegIdentifier,
        via_destinations: List[Any],
        remarks_english: List[Any],
        remarks_swedish: List[Any],
        di_indicator: str,
    ) -> None:
        self.flight_id = flight_id
        self.arrival_airport_swedish = arrival_airport_swedish
        self.arrival_airport_english = arrival_airport_english
        self.airline_operator = airline_operator
        self.departure_time = departure_time
        self.location_and_status = location_and_status
        self.check_in = check_in
        self.code_share_data = code_share_data
        self.flight_leg_identifier = flight_leg_identifier
        self.via_destinations = via_destinations
        self.remarks_english = remarks_english
        self.remarks_swedish = remarks_swedish
        self.di_indicator = di_indicator

    @staticmethod
    def from_dict(obj: Any):
        """Returns list of updated departing flights."""
        assert isinstance(obj, dict)
        departures_dict = obj.get("flights", [])
        flight_arr = []

        for flight_data in departures_dict:
            flight = Departure(
                flight_id=from_str(flight_data.get("flightId")),
                arrival_airport_swedish=from_str(flight_data.get("arrivalAirportSwedish")),
                arrival_airport_english=from_str(flight_data.get("arrivalAirportEnglish")),
                airline_operator=AirlineOperator.from_dict(flight_data.get("airlineOperator", {})),
                departure_time=Time.from_dict(flight_data.get("departureTime")) if "departureTime" in flight_data else datetime.now(),
                location_and_status=LocationAndStatus.from_dict(flight_data.get("locationAndStatus", {})),
                check_in=Baggage.from_dict(flight_data.get("checkIn", {})),
                code_share_data=from_list(lambda x: x, flight_data.get("codeShareData", [])),
                flight_leg_identifier=FlightLegIdentifier.from_dict(flight_data.get("flightLegIdentifier", {})),
                via_destinations=from_list(lambda x: x, flight_data.get("viaDestinations", [])),
                remarks_english=from_list(lambda x: x, flight_data.get("remarksEnglish", [])),
                remarks_swedish=from_list(lambda x: x, flight_data.get("remarksSwedish", [])),
                di_indicator=from_str(flight_data.get("diIndicator", {}))
            )
            flight_arr.append(flight)

        return flight_arr

    def to_dict(self) -> dict:
        """Add Departure data to dict item."""
        result: dict = {}
        result["flightId"] = from_str(self.flight_id)
        result["arrivalAirportSwedish"] = from_str(self.arrival_airport_swedish)
        result["arrivalAirportEnglish"] = from_str(self.arrival_airport_english)
        result["airlineOperator"] = to_class(AirlineOperator, self.airline_operator)
        result["departureTime"] = to_class(Time, self.departure_time)
        result["locationAndStatus"] = to_class(
            LocationAndStatus, self.location_and_status
        )
        result["checkIn"] = to_class(Baggage, self.check_in)
        result["codeShareData"] = from_list(lambda x: x, self.code_share_data)
        result["flightLegIdentifier"] = to_class(
            FlightLegIdentifier, self.flight_leg_identifier
        )
        result["viaDestinations"] = from_list(lambda x: x, self.via_destinations)
        result["remarksEnglish"] = from_list(lambda x: x, self.remarks_english)
        result["remarksSwedish"] = from_list(lambda x: x, self.remarks_swedish)
        result["diIndicator"] = from_str(self.di_indicator)
        return result


class Flight:
    """Class for a Swedavia Flight."""
    departure: Optional[Departure]
    arrival: Optional[Arrival]

    def __init__(
        self, departure: Optional[Departure], arrival: Optional[Arrival]
    ) -> None:
        self.departure = departure
        self.arrival = arrival

    @staticmethod
    def from_dict(obj: Any) -> "Flight":
        """Returns Flight object based on data from Departure and Arrival classes."""
        assert isinstance(obj, dict)
        departure = from_union([Departure.from_dict, from_none], obj.get("departure"))
        arrival = from_union([Arrival.from_dict, from_none], obj.get("arrival"))
        return Flight(departure, arrival)

    def to_dict(self) -> dict:
        """Add Flight data to dict item."""
        result: dict = {}
        if self.departure is not None:
            result["departure"] = from_union(
                [lambda x: to_class(Departure, x), from_none], self.departure
            )
        if self.arrival is not None:
            result["arrival"] = from_union(
                [lambda x: to_class(Arrival, x), from_none], self.arrival
            )
        return result

@dataclass
class FlightInfo:
    """Class for the Swedavia FlightInfo API, containing list of Flight objects and a token."""
    flights: List[Flight]
    continuationtoken: str

    def __init__(self, flights: List[Flight], continuationtoken: str) -> None:
        self.flights = flights
        self.continuationtoken = continuationtoken

    @staticmethod
    def from_dict(obj: Any) -> "FlightInfo":
        """Returns FlightInfo object."""
        assert isinstance(obj, dict)
        flights = from_list(Flight.from_dict, obj.get("flights"))
        continuationtoken = from_str(obj.get("continuationtoken"))
        return FlightInfo(flights, continuationtoken)

    def to_dict(self) -> dict:
        """Add FlightInfo data to dict item."""
        result: dict = {}
        result["flights"] = from_list(lambda x: to_class(Flight, x), self.flights)
        result["continuationtoken"] = from_str(self.continuationtoken)
        return result


def flight_info_from_dict(s: Any) -> FlightInfo:
    return FlightInfo.from_dict(s)


def flight_info_to_dict(x: FlightInfo) -> Any:
    return to_class(FlightInfo, x)


@dataclass
class WaitTime:
    """Class for Swedavia WaitTime API."""
    id_: int
    queue_name: str
    current_time: datetime
    current_projected_wait_time: int
    is_fast_track: bool
    terminal: str
    latitude: float
    longitude: float
    overflow: bool

    def __init__(
        self,
        id_: str,
        queue_name: str,
        current_time: datetime,
        current_projected_wait_time: int,
        is_fast_track: bool,
        terminal: str,
        latitude: float,
        longitude: float,
        overflow: bool,
    ) -> None:
        self.id_ = id_
        self.queue_name = queue_name
        self.current_time = current_time
        self.current_projected_wait_time = current_projected_wait_time
        self.is_fast_track = is_fast_track
        self.terminal = terminal
        self.latitude = latitude
        self.longitude = longitude
        self.overflow = overflow

    @staticmethod
    def from_dict(d: dict) -> "WaitTime":
        """"Returns WaitTime object."""
        return WaitTime(
            d.get("id"),
            d.get("queueName"),
            datetime.strptime(d.get("currentTime"), "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d %H:%M:%S"),
            d.get("currentProjectedWaitTime"),
            d.get("isFastTrack"),
            d.get("terminal"),
            d.get("latitude"),
            d.get("longitude"),
            d.get("overflow"),
        )

    def to_dict(self) -> dict:
        """Return WaitTime data as dict item."""
        return {
            "id": self.id_,
            "queueName": self.queue_name,
            "currentTime": self.current_time,
            "currentProjectedWaitTime": self.current_projected_wait_time,
            "isFastTrack": self.is_fast_track,
            "terminal": self.terminal,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "overflow": self.overflow,
        }


@dataclass
class FlightAndWaitTime:
    """Combined class of FlightInfo (currently only Departure flights) and WaitTime."""
    flight_info: List[Departure]  # Change the type to a list of Departure
    wait_info: List[WaitTime]

    def __init__(self, flight_info: List[Departure], wait_info: List[WaitTime]) -> None:
        self.flight_info = flight_info
        self.wait_info = wait_info

    @staticmethod
    def from_dict(obj: Any) -> "FlightAndWaitTime":
        """Returns FlightAndWaitTime object."""
        assert isinstance(obj, dict)
        flight_info = from_list(Departure.from_dict, obj.get("flight_info"))
        wait_info = from_list(WaitTime.from_dict, obj.get("wait_info"))
        return FlightAndWaitTime(flight_info, wait_info)

    def to_dict(self) -> dict:
        """Add FlightAndWaitTime data to dict item."""
        result: dict = {}
        result["flight_info"] = from_list(lambda x: to_class(Departure, x), self.flight_info)
        result["wait_info"] = from_list(lambda x: to_class(WaitTime, x), self.wait_info)
        return result
