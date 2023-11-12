"""The trafikverket_train component."""
from __future__ import annotations


from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    DOMAIN,
    PLATFORMS,
    CONF_FLIGHTINFO_APIKEY,
    CONF_HOMEAIRPORT,
    CONF_WAIT_TIME_APIKEY,
    CONF_FLIGHTNUMBER,
    CONF_DATE,
)

from .coordinator import SwedaviaDataUpdateCoordinator
from .swedavia_wrapper import (
    SwedaviaWrapper,
    InvalidAirport,
    InvalidFlightInfoKey,
    InvalidtFlightNumber,
    InvalidWaitTimeKey,
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Trafikverket Train from a config entry."""

    http_session = async_get_clientsession(hass)
    swedavia_api = SwedaviaWrapper(
        client_session=http_session,
        flight_info_api_key=entry.data[CONF_FLIGHTINFO_APIKEY],
        wait_time_api_key=entry.data[CONF_WAIT_TIME_APIKEY],
    )

    try:
        await swedavia_api.async_get_flight_info(
            airport=entry.data[CONF_HOMEAIRPORT],
            flight_number=entry.data[CONF_FLIGHTNUMBER],
            date=entry.data[CONF_DATE],
        )
        await swedavia_api.async_get_wait_time(
            airport=entry.data[CONF_HOMEAIRPORT],
            flight_number=entry.data[CONF_FLIGHTNUMBER],
            date=entry.data[CONF_DATE],
        )
    except (InvalidFlightInfoKey, InvalidWaitTimeKey) as error:
        raise ConfigEntryAuthFailed from error
    except (InvalidtFlightNumber, InvalidAirport) as error:
        raise ConfigEntryNotReady(
            f"Problem when looking up flight {entry.data[CONF_FLIGHTNUMBER]} from"
            f" {entry.data[CONF_HOMEAIRPORT]}. Error: {error} "
        ) from error

    coordinator = SwedaviaDataUpdateCoordinator(
        hass,
        entry,
        airport=entry.data[CONF_HOMEAIRPORT],
        flight_number=entry.data[CONF_FLIGHTNUMBER],
        date=entry.data[CONF_DATE],
    )
    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    entity_reg = er.async_get(hass)
    entries = er.async_entries_for_config_entry(entity_reg, entry.entry_id)
    for entity in entries:
        if not entity.unique_id.startswith(entry.entry_id):
            entity_reg.async_update_entity(
                entity.entity_id,
                new_unique_id=f"{entry.entry_id}-flight-info-and-wait-times",
            )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(update_listener))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload Trafikverket Weatherstation config entry."""

    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)
