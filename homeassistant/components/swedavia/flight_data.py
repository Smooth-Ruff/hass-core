from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class AirlineOperator:
    iata: str
    icao: str
    name: str


@dataclass
class FlightTime:
    scheduled_utc: date
    estimated_utc: date
    actual_utc: date


@dataclass
class DepartureLocationAndStatus:
    terminal: str
    gate: str
    gate_action: str
    gate_action_swedish: str
    gate_action_english: str
    gate_open_utc: date
    gate_close_utc: date
    flight_leg_status: str
    flight_leg_status_swedish: str
    flight_leg_status_english: str


@dataclass
class Baggage:
    estimated_first_bag_utc: date
    baggage_claim_unit: date
    first_bag_utc: Optional[date]
    last_bag_utc: Optional[date]


@dataclass
class CheckIn:
    status: str
    status_swedish: str
    status_english: str
    desk_from: int
    desk_to: int


@dataclass
class FlightLegIdentifier:
    ifpl_id: str
    callsign: str
    aircraft_registration: str
    ssr_code: str
    flight_id: str
    flight_departure_date_utc: date
    departure_airport_iata: str
    arrival_airport_iata: str
    departure_airport_icao: str
    arrival_airport_icao: str


@dataclass
class ViaDestination:
    airport_iata: str
    airport_swedish: str
    airport_english: str


@dataclass
class Remark:
    text: str
    indicator: str


@dataclass
class ArrivalFlight:
    flight_id: str
    departure_airport_swedish: str
    departure_airport_english: str
    airline_operator: AirlineOperator
    arrival_time: FlightTime
    location_and_status: DepartureLocationAndStatus
    baggage: Optional[Baggage]
    code_share_data: [str]
    flight_leg_identifier: FlightLegIdentifier
    remarks_english: [Remark]
    remarks_swedish: [Remark]
    via_destinations: [ViaDestination]
    di_indicator: str


@dataclass
class DepartureFlight:
    flight_id: str
    arrival_airport_swedish: str
    arrival_airport_english: str
    airline_operator: AirlineOperator
    departure_time: FlightTime
    location_and_status: DepartureLocationAndStatus
    checkin: Optional[CheckIn]
    code_share_data: [str]
    flight_leg_identifier: FlightLegIdentifier
    via_destinations: [ViaDestination]
    remarks_english: [Remark]
    remarks_swedish: [Remark]
    di_indicator: str


@dataclass
class Flight:
    arrival: Optional[ArrivalFlight]
    departure: Optional[DepartureFlight]
    scheduled_date: date


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
