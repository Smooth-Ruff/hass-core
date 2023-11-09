"""Adds constants for Swedavia integration."""
from homeassistant.const import Platform

DOMAIN = "swedavia"
PLATFORMS = [Platform.SENSOR]
ATTRIBUTION = "Data provided by Swedavia"

CONF_FROM = "from"
CONF_TO = "to"
CONF_TIME = "time"
CONF_FILTER_PRODUCT = "filter_product"
