from dataclasses import dataclass
from datetime import date
from typing import Any, List, Optional, TypeVar, Callable, Type, cast
from datetime import datetime
import dateutil.parser


T = TypeVar("T")


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def from_datetime(x: Any) -> datetime:
    return dateutil.parser.parse(x)


def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    assert isinstance(x, list)
    return [f(y) for y in x]


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


def from_none(x: Any) -> Any:
    assert x is None
    return x


def from_union(fs, x):
    for f in fs:
        try:
            return f(x)
        except:
            pass
    assert False


class AirlineOperator:
    iata: str
    icao: str
    name: str

    def __init__(self, iata: str, icao: str, name: str) -> None:
        self.iata = iata
        self.icao = icao
        self.name = name

    @staticmethod
    def from_dict(obj: Any) -> 'AirlineOperator':
        assert isinstance(obj, dict)
        iata = from_str(obj.get("iata"))
        icao = from_str(obj.get("icao"))
        name = from_str(obj.get("name"))
        return AirlineOperator(iata, icao, name)

    def to_dict(self) -> dict:
        result: dict = {}
        result["iata"] = from_str(self.iata)
        result["icao"] = from_str(self.icao)
        result["name"] = from_str(self.name)
        return result


class Time:
    scheduled_utc: datetime

    def __init__(self, scheduled_utc: datetime) -> None:
        self.scheduled_utc = scheduled_utc

    @staticmethod
    def from_dict(obj: Any) -> 'Time':
        assert isinstance(obj, dict)
        scheduled_utc = from_datetime(obj.get("scheduledUtc"))
        return Time(scheduled_utc)

    def to_dict(self) -> dict:
        result: dict = {}
        result["scheduledUtc"] = self.scheduled_utc.isoformat()
        return result


class Baggage:
    pass

    def __init__(self, ) -> None:
        pass

    @staticmethod
    def from_dict(obj: Any) -> 'Baggage':
        assert isinstance(obj, dict)
        return Baggage()

    def to_dict(self) -> dict:
        result: dict = {}
        return result


class FlightLegIdentifier:
    callsign: str
    flight_id: str
    flight_departure_date_utc: datetime
    departure_airport_iata: str
    arrival_airport_iata: str
    departure_airport_icao: str
    arrival_airport_icao: str

    def __init__(self, callsign: str, flight_id: str, flight_departure_date_utc: datetime, departure_airport_iata: str, arrival_airport_iata: str, departure_airport_icao: str, arrival_airport_icao: str) -> None:
        self.callsign = callsign
        self.flight_id = flight_id
        self.flight_departure_date_utc = flight_departure_date_utc
        self.departure_airport_iata = departure_airport_iata
        self.arrival_airport_iata = arrival_airport_iata
        self.departure_airport_icao = departure_airport_icao
        self.arrival_airport_icao = arrival_airport_icao

    @staticmethod
    def from_dict(obj: Any) -> 'FlightLegIdentifier':
        assert isinstance(obj, dict)
        callsign = from_str(obj.get("callsign"))
        flight_id = from_str(obj.get("flightId"))
        flight_departure_date_utc = from_datetime(obj.get("flightDepartureDateUtc"))
        departure_airport_iata = from_str(obj.get("departureAirportIata"))
        arrival_airport_iata = from_str(obj.get("arrivalAirportIata"))
        departure_airport_icao = from_str(obj.get("departureAirportIcao"))
        arrival_airport_icao = from_str(obj.get("arrivalAirportIcao"))
        return FlightLegIdentifier(callsign, flight_id, flight_departure_date_utc, departure_airport_iata, arrival_airport_iata, departure_airport_icao, arrival_airport_icao)

    def to_dict(self) -> dict:
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
    terminal: str
    flight_leg_status: str
    flight_leg_status_swedish: str
    flight_leg_status_english: str

    def __init__(self, terminal: str, flight_leg_status: str, flight_leg_status_swedish: str, flight_leg_status_english: str) -> None:
        self.terminal = terminal
        self.flight_leg_status = flight_leg_status
        self.flight_leg_status_swedish = flight_leg_status_swedish
        self.flight_leg_status_english = flight_leg_status_english

    @staticmethod
    def from_dict(obj: Any) -> 'LocationAndStatus':
        assert isinstance(obj, dict)
        terminal = from_str(obj.get("terminal"))
        flight_leg_status = from_str(obj.get("flightLegStatus"))
        flight_leg_status_swedish = from_str(obj.get("flightLegStatusSwedish"))
        flight_leg_status_english = from_str(obj.get("flightLegStatusEnglish"))
        return LocationAndStatus(terminal, flight_leg_status, flight_leg_status_swedish, flight_leg_status_english)

    def to_dict(self) -> dict:
        result: dict = {}
        result["terminal"] = from_str(self.terminal)
        result["flightLegStatus"] = from_str(self.flight_leg_status)
        result["flightLegStatusSwedish"] = from_str(self.flight_leg_status_swedish)
        result["flightLegStatusEnglish"] = from_str(self.flight_leg_status_english)
        return result


class Arrival:
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

    def __init__(self, flight_id: str, departure_airport_swedish: str, departure_airport_english: str, airline_operator: AirlineOperator, arrival_time: Time, location_and_status: LocationAndStatus, baggage: Baggage, code_share_data: List[Any], flight_leg_identifier: FlightLegIdentifier, remarks_english: List[Any], remarks_swedish: List[Any], via_destinations: List[Any], di_indicator: str) -> None:
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
    def from_dict(obj: Any) -> 'Arrival':
        assert isinstance(obj, dict)
        flight_id = from_str(obj.get("flightId"))
        departure_airport_swedish = from_str(obj.get("departureAirportSwedish"))
        departure_airport_english = from_str(obj.get("departureAirportEnglish"))
        airline_operator = AirlineOperator.from_dict(obj.get("airlineOperator"))
        arrival_time = Time.from_dict(obj.get("arrivalTime"))
        location_and_status = LocationAndStatus.from_dict(obj.get("locationAndStatus"))
        baggage = Baggage.from_dict(obj.get("baggage"))
        code_share_data = from_list(lambda x: x, obj.get("codeShareData"))
        flight_leg_identifier = FlightLegIdentifier.from_dict(obj.get("flightLegIdentifier"))
        remarks_english = from_list(lambda x: x, obj.get("remarksEnglish"))
        remarks_swedish = from_list(lambda x: x, obj.get("remarksSwedish"))
        via_destinations = from_list(lambda x: x, obj.get("viaDestinations"))
        di_indicator = from_str(obj.get("diIndicator"))
        return Arrival(flight_id, departure_airport_swedish, departure_airport_english, airline_operator, arrival_time, location_and_status, baggage, code_share_data, flight_leg_identifier, remarks_english, remarks_swedish, via_destinations, di_indicator)

    def to_dict(self) -> dict:
        result: dict = {}
        result["flightId"] = from_str(self.flight_id)
        result["departureAirportSwedish"] = from_str(self.departure_airport_swedish)
        result["departureAirportEnglish"] = from_str(self.departure_airport_english)
        result["airlineOperator"] = to_class(AirlineOperator, self.airline_operator)
        result["arrivalTime"] = to_class(Time, self.arrival_time)
        result["locationAndStatus"] = to_class(LocationAndStatus, self.location_and_status)
        result["baggage"] = to_class(Baggage, self.baggage)
        result["codeShareData"] = from_list(lambda x: x, self.code_share_data)
        result["flightLegIdentifier"] = to_class(FlightLegIdentifier, self.flight_leg_identifier)
        result["remarksEnglish"] = from_list(lambda x: x, self.remarks_english)
        result["remarksSwedish"] = from_list(lambda x: x, self.remarks_swedish)
        result["viaDestinations"] = from_list(lambda x: x, self.via_destinations)
        result["diIndicator"] = from_str(self.di_indicator)
        return result


class Departure:
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

    def __init__(self, flight_id: str, arrival_airport_swedish: str, arrival_airport_english: str, airline_operator: AirlineOperator, departure_time: Time, location_and_status: LocationAndStatus, check_in: Baggage, code_share_data: List[Any], flight_leg_identifier: FlightLegIdentifier, via_destinations: List[Any], remarks_english: List[Any], remarks_swedish: List[Any], di_indicator: str) -> None:
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
    def from_dict(obj: Any) -> 'Departure':
        assert isinstance(obj, dict)
        flight_id = from_str(obj.get("flightId"))
        arrival_airport_swedish = from_str(obj.get("arrivalAirportSwedish"))
        arrival_airport_english = from_str(obj.get("arrivalAirportEnglish"))
        airline_operator = AirlineOperator.from_dict(obj.get("airlineOperator"))
        departure_time = Time.from_dict(obj.get("departureTime"))
        location_and_status = LocationAndStatus.from_dict(obj.get("locationAndStatus"))
        check_in = Baggage.from_dict(obj.get("checkIn"))
        code_share_data = from_list(lambda x: x, obj.get("codeShareData"))
        flight_leg_identifier = FlightLegIdentifier.from_dict(obj.get("flightLegIdentifier"))
        via_destinations = from_list(lambda x: x, obj.get("viaDestinations"))
        remarks_english = from_list(lambda x: x, obj.get("remarksEnglish"))
        remarks_swedish = from_list(lambda x: x, obj.get("remarksSwedish"))
        di_indicator = from_str(obj.get("diIndicator"))
        return Departure(flight_id, arrival_airport_swedish, arrival_airport_english, airline_operator, departure_time, location_and_status, check_in, code_share_data, flight_leg_identifier, via_destinations, remarks_english, remarks_swedish, di_indicator)

    def to_dict(self) -> dict:
        result: dict = {}
        result["flightId"] = from_str(self.flight_id)
        result["arrivalAirportSwedish"] = from_str(self.arrival_airport_swedish)
        result["arrivalAirportEnglish"] = from_str(self.arrival_airport_english)
        result["airlineOperator"] = to_class(AirlineOperator, self.airline_operator)
        result["departureTime"] = to_class(Time, self.departure_time)
        result["locationAndStatus"] = to_class(LocationAndStatus, self.location_and_status)
        result["checkIn"] = to_class(Baggage, self.check_in)
        result["codeShareData"] = from_list(lambda x: x, self.code_share_data)
        result["flightLegIdentifier"] = to_class(FlightLegIdentifier, self.flight_leg_identifier)
        result["viaDestinations"] = from_list(lambda x: x, self.via_destinations)
        result["remarksEnglish"] = from_list(lambda x: x, self.remarks_english)
        result["remarksSwedish"] = from_list(lambda x: x, self.remarks_swedish)
        result["diIndicator"] = from_str(self.di_indicator)
        return result


class Flight:
    departure: Optional[Departure]
    arrival: Optional[Arrival]

    def __init__(self, departure: Optional[Departure], arrival: Optional[Arrival]) -> None:
        self.departure = departure
        self.arrival = arrival

    @staticmethod
    def from_dict(obj: Any) -> 'Flight':
        assert isinstance(obj, dict)
        departure = from_union([Departure.from_dict, from_none], obj.get("departure"))
        arrival = from_union([Arrival.from_dict, from_none], obj.get("arrival"))
        return Flight(departure, arrival)

    def to_dict(self) -> dict:
        result: dict = {}
        if self.departure is not None:
            result["departure"] = from_union([lambda x: to_class(Departure, x), from_none], self.departure)
        if self.arrival is not None:
            result["arrival"] = from_union([lambda x: to_class(Arrival, x), from_none], self.arrival)
        return result


class FlightInfo:
    flights: List[Flight]
    continuationtoken: str

    def __init__(self, flights: List[Flight], continuationtoken: str) -> None:
        self.flights = flights
        self.continuationtoken = continuationtoken

    @staticmethod
    def from_dict(obj: Any) -> 'FlightInfo':
        assert isinstance(obj, dict)
        flights = from_list(Flight.from_dict, obj.get("flights"))
        continuationtoken = from_str(obj.get("continuationtoken"))
        return FlightInfo(flights, continuationtoken)

    def to_dict(self) -> dict:
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
    id_: int
    queue_name: str
    current_time: date
    current_projected_wait_time: int
    is_fast_track: bool
    terminal: str
    latitude: float
    longitude: float
    overflow: bool

    def __init__(self,
                 id_: str,
                 queue_name: str,
                 current_time: date,
                 current_projected_wait_time: int,
                 is_fast_track: bool,
                 terminal: str,
                 latitude: float,
                 longitude: float,
                 overflow: bool):
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
    def from_dict(d: dict) -> 'WaitTime':
        return WaitTime(
                d.get("id"),
                d.get("queueName"),
                d.get("currentTime"),
                d.get("currentProjectedWaitTime"),
                d.get("isFastTrack"),
                d.get("terminal"),
                d.get("latitude"),
                d.get("longitude"),
                d.get("overflow"))
    
    def to_dict(self) -> dict:
        return {
            "id": self.id_,
            "queueName": self.queue_name,
            "currentTime": self.current_time,
            "currentProjectedWaitTime": self.current_projected_wait_time,
            "isFastTrack": self.is_fast_track,
            "terminal": self.terminal,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "overflow": self.overflow
        }
@dataclass
class FlightAndWaitTime:
    flight_info: Flight
    wait_info: WaitTime
