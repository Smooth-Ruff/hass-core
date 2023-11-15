"""Utils for trafikverket_train."""
from __future__ import annotations

from datetime import date, time, timedelta, datetime
from homeassistant.util import dt as dt_util

from homeassistant.const import WEEKDAYS


def create_unique_id(
    from_station: str, to_station: str, depart_time: time | str | None, weekdays: list
) -> str:
    """Create unique id."""
    timestr = str(depart_time) if depart_time else ""
    return (
        f"{from_station.casefold().replace(' ', '')}-{to_station.casefold().replace(' ', '')}"
        f"-{timestr.casefold().replace(' ', '')}-{str(weekdays)}"
    )


def next_weekday(fromdate: date, weekday: int) -> date:
    """Return the date of the next time a specific weekday happen."""
    days_ahead = weekday - fromdate.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    return fromdate + timedelta(days_ahead)


def next_departuredate(departure: list[str]) -> date:
    """Calculate the next departuredate from an array input of short days."""
    today_date = datetime.now(tz=dt_util.DEFAULT_TIME_ZONE).date()
    today_weekday = date.weekday(today_date)
    if WEEKDAYS[today_weekday] in departure:
        return today_date
    for day in departure:
        next_departure = WEEKDAYS.index(day)
        if next_departure > today_weekday:
            return next_weekday(today_date, next_departure)
    return next_weekday(today_date, WEEKDAYS.index(departure[0]))


def fill_date(date_variable: str | None) -> str:
    if date_variable is None:
        today = datetime.now(tz=dt_util.DEFAULT_TIME_ZONE).date()
        date_variable = today.strftime("%y-%m-%d")
    return date_variable
