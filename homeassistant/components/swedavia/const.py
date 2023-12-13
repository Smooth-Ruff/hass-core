"""Adds constants for Swedavia integration."""
from homeassistant.const import Platform

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
