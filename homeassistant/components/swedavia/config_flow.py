"""Handles the Swedavia integration setup from config entries."""

from typing import Any
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from .const import (
    DOMAIN,
    CONF_FLIGHTINFO_APIKEY,
    CONF_WAIT_TIME_APIKEY,
    CONF_HOMEAIRPORT,
    CONF_FLIGHTNUMBER,
    CONF_DATE,
)

data_schema = vol.Schema(
    {
        vol.Required(CONF_FLIGHTINFO_APIKEY): str,
        vol.Required(CONF_WAIT_TIME_APIKEY): str,
        vol.Required(CONF_HOMEAIRPORT): str,
        vol.Required(CONF_FLIGHTNUMBER): str,
        vol.Required(CONF_DATE): str,
    }
)


class SwedaviaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Swedavia integration."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(
        self,  # noqa: ANN101
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Setup steps for user config flow, creates entry based on user input. Involves inserts of API keys, home airport, designated flight number and travel date."""
        errors: dict[str, str] = {}
        if user_input is not None:
            api_key_1: str = user_input[CONF_FLIGHTINFO_APIKEY]
            api_key_2: str = user_input[CONF_WAIT_TIME_APIKEY]
            home_airport: str = user_input[CONF_HOMEAIRPORT]
            flight_number: str = user_input[CONF_FLIGHTNUMBER]
            date: str = user_input[CONF_DATE]

            unique_id = f"{home_airport}-{flight_number}-{date}"
            await self.async_set_unique_id(unique_id)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title="Swedavia",
                data={
                    CONF_FLIGHTINFO_APIKEY: api_key_1,
                    CONF_WAIT_TIME_APIKEY: api_key_2,
                    CONF_HOMEAIRPORT: home_airport,
                    CONF_FLIGHTNUMBER: flight_number,
                    CONF_DATE: date,
                },
            )

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )
