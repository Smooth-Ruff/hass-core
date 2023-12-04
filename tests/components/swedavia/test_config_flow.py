"""Test the Swedavia config flow."""

from unittest.mock import patch

from homeassistant import config_entries
from homeassistant.components.swedavia.const import (
    CONF_DATE,
    CONF_FLIGHTINFO_APIKEY,
    CONF_FLIGHTNUMBER,
    CONF_HOMEAIRPORT,
    CONF_WAIT_TIME_APIKEY,
    DOMAIN,
)
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from tests.common import MockConfigEntry


async def test_form(hass: HomeAssistant) -> None:
    """Ensure that we get the form."""

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {}

    with patch(
        "homeassistant.components.swedavia.SwedaviaWrapper.async_get_client_session"
    ), patch(
        "homeassistant.components.swedavia.SwedaviaWrapper.async_get_flight_info"
    ), patch(
        "homeassistant.components.swedavia.SwedaviaWrapper.async_get_wait_time",
    ) as mock_setup_entry:
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_FLIGHTINFO_APIKEY: "123456789",
                CONF_WAIT_TIME_APIKEY: "123456789",
                CONF_DATE: "23-01-01",
                CONF_FLIGHTNUMBER: "FN123",
                CONF_HOMEAIRPORT: "HOM",
            },
        )
        await hass.async_block_till_done()

    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == "Swedavia"
    assert result["data"] == {
        "flight_info_key": "123456789",
        "wait_time_key": "123456789",
        "home_airport": "HOM",
        "flight_number": "FN123",
        "flight_date": "23-01-01",
    }

    assert len(mock_setup_entry.mock_calls) == 8  # 8 total calls are expected


async def test_form_entry_already_exists(hass: HomeAssistant) -> None:
    """Test flow aborts when an identical entry eixsts."""

    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_FLIGHTINFO_APIKEY: "123456789",
            CONF_WAIT_TIME_APIKEY: "123456789",
            CONF_DATE: "23-01-01",
            CONF_FLIGHTNUMBER: "FN123",
            CONF_HOMEAIRPORT: "HOM",
        },
        unique_id="HOM-FN123-23-01-01",
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {}

    with patch(
        "homeassistant.components.swedavia.SwedaviaWrapper.async_get_client_session"
    ), patch(
        "homeassistant.components.swedavia.SwedaviaWrapper.async_get_flight_info"
    ), patch(
        "homeassistant.components.swedavia.SwedaviaWrapper.async_get_wait_time"
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_FLIGHTINFO_APIKEY: "123456789",
                CONF_WAIT_TIME_APIKEY: "123456789",
                CONF_DATE: "23-01-01",
                CONF_FLIGHTNUMBER: "FN123",
                CONF_HOMEAIRPORT: "HOM",
            },
        )
        await hass.async_block_till_done()

    assert result["type"] == FlowResultType.ABORT
    assert result["reason"] == "already_configured"
