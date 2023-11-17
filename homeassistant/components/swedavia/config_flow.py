import voluptuous as vol
from homeassistant import config_entries
from .const import (
    DOMAIN,
    CONF_FLIGHTINFO_APIKEY,
    CONF_WAIT_TIME_APIKEY,
    CONF_HOMEAIRPORT,
    CONF_FLIGHTNUMBER,
    CONF_DATE,
)


class SwedaviaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Swedavia integration."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            api_key_1: str = user_input[CONF_FLIGHTINFO_APIKEY]
            api_key_2: str = user_input[CONF_WAIT_TIME_APIKEY]
            home_airport: str = user_input[CONF_HOMEAIRPORT]
            flight_number: str = user_input[CONF_FLIGHTNUMBER]
            date: str = user_input[CONF_DATE]
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

        data_schema = vol.Schema(
            {
                vol.Required(CONF_FLIGHTINFO_APIKEY): str,
                vol.Required(CONF_WAIT_TIME_APIKEY): str,
                vol.Required(CONF_HOMEAIRPORT): str,
                vol.Required(CONF_FLIGHTNUMBER): str,
                vol.Required(CONF_DATE): str,
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )
