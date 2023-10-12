"""Support for ESPHome lights."""
from __future__ import annotations

from typing import Any, cast

from aioesphomeapi import (
    APIVersion,
    EntityInfo,
    LightColorCapability,
    LightInfo,
    LightState,
)

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_COLOR_TEMP_KELVIN,
    ATTR_EFFECT,
    ATTR_FLASH,
    ATTR_RGB_COLOR,
    ATTR_RGBW_COLOR,
    ATTR_RGBWW_COLOR,
    ATTR_TRANSITION,
    ATTR_WHITE,
    FLASH_LONG,
    FLASH_SHORT,
    ColorMode,
    LightEntity,
    LightEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .entity import EsphomeEntity, esphome_state_property, platform_async_setup_entry

FLASH_LENGTHS = {FLASH_SHORT: 2, FLASH_LONG: 10}


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up ESPHome lights based on a config entry."""
    await platform_async_setup_entry(
        hass,
        entry,
        async_add_entities,
        info_type=LightInfo,
        entity_type=EsphomeLight,
        state_type=LightState,
    )


_COLOR_MODE_MAPPING = {
    ColorMode.ONOFF: [
        LightColorCapability.ON_OFF,
    ],
    ColorMode.BRIGHTNESS: [
        LightColorCapability.ON_OFF | LightColorCapability.BRIGHTNESS,
        # for compatibility with older clients (2021.8.x)
        LightColorCapability.BRIGHTNESS,
    ],
    ColorMode.COLOR_TEMP: [
        LightColorCapability.ON_OFF
        | LightColorCapability.BRIGHTNESS
        | LightColorCapability.COLOR_TEMPERATURE,
        LightColorCapability.ON_OFF
        | LightColorCapability.BRIGHTNESS
        | LightColorCapability.COLD_WARM_WHITE,
    ],
    ColorMode.RGB: [
        LightColorCapability.ON_OFF
        | LightColorCapability.BRIGHTNESS
        | LightColorCapability.RGB,
    ],
    ColorMode.RGBW: [
        LightColorCapability.ON_OFF
        | LightColorCapability.BRIGHTNESS
        | LightColorCapability.RGB
        | LightColorCapability.WHITE,
    ],
    ColorMode.RGBWW: [
        LightColorCapability.ON_OFF
        | LightColorCapability.BRIGHTNESS
        | LightColorCapability.RGB
        | LightColorCapability.WHITE
        | LightColorCapability.COLOR_TEMPERATURE,
        LightColorCapability.ON_OFF
        | LightColorCapability.BRIGHTNESS
        | LightColorCapability.RGB
        | LightColorCapability.COLD_WARM_WHITE,
    ],
    ColorMode.WHITE: [
        LightColorCapability.ON_OFF
        | LightColorCapability.BRIGHTNESS
        | LightColorCapability.WHITE
    ],
}


def _mired_to_kelvin(mired_temperature: float) -> int:
    """Convert absolute mired shift to degrees kelvin.

    This function rounds the converted value instead of flooring the value as
    is done in homeassistant.util.color.color_temperature_mired_to_kelvin().

    If the value of mired_temperature is less than or equal to zero, return
    the original value to avoid a divide by zero.
    """
    if mired_temperature <= 0:
        return round(mired_temperature)
    return round(1000000 / mired_temperature)


def _color_mode_to_ha(mode: int) -> str:
    """Convert an esphome color mode to a HA color mode constant.

    Choses the color mode that best matches the feature-set.
    """
    candidates = []
    for ha_mode, cap_lists in _COLOR_MODE_MAPPING.items():
        for caps in cap_lists:
            if caps == mode:
                # exact match
                return ha_mode
            if (mode & caps) == caps:
                # all requirements met
                candidates.append((ha_mode, caps))

    if not candidates:
        return ColorMode.UNKNOWN

    # choose the color mode with the most bits set
    candidates.sort(key=lambda key: bin(key[1]).count("1"))
    return candidates[-1][0]


def _filter_color_modes(
    supported: list[int], features: LightColorCapability
) -> list[int]:
    """Filter the given supported color modes.

    Excluding all values that don't have the requested features.
    """
    return [mode for mode in supported if (mode & features) == features]


class EsphomeLight(EsphomeEntity[LightInfo, LightState], LightEntity):
    """A light implementation for ESPHome."""

    _native_supported_color_modes: list[int]
    _supports_color_mode = False

    @property
    @esphome_state_property
    def is_on(self) -> bool | None:
        """Return true if the light is on."""
        return self._state.state

    def _apply_brightness(
        self, data: dict[str, Any], brightness_ha: Any, color_modes: list[int]
    ) -> bool:
        """Apply a brightness setting if requested."""

        data["brightness"] = brightness_ha / 255
        color_modes[:] = _filter_color_modes(
            color_modes, LightColorCapability.BRIGHTNESS
        )
        return False

    def _apply_flash(
        self, data: dict[str, Any], flash: str, _color_modes: list[int]
    ) -> bool:
        """Apply a flash setting if requested."""

        data["flash_length"] = FLASH_LENGTHS[flash]
        return False

    def _apply_rgb_color(
        self, data: dict[str, Any], rgb_ha: Any, color_modes: list[int]
    ) -> bool:
        """Apply an RGB color setting if requested."""

        rgb = tuple(x / 255 for x in rgb_ha)
        color_bri = max(rgb)
        # normalize rgb
        data["rgb"] = tuple(x / (color_bri or 1) for x in rgb)
        data["color_brightness"] = color_bri
        color_modes[:] = _filter_color_modes(color_modes, LightColorCapability.RGB)
        return True

    def _apply_rgbw_color(
        self, data: dict[str, Any], rgbw_ha: Any, color_modes: list[int]
    ) -> bool:
        """Apply an RGBW color setting if requested."""

        *rgb, w = tuple(x / 255 for x in rgbw_ha)
        color_bri = max(rgb)
        # normalize rgb
        data["rgb"] = tuple(x / (color_bri or 1) for x in rgb)
        data["white"] = w
        data["color_brightness"] = color_bri
        color_modes[:] = _filter_color_modes(
            color_modes, LightColorCapability.RGB | LightColorCapability.WHITE
        )
        return True

    def _apply_rgbww_color(
        self, data: dict[str, Any], rgbww_ha: Any, color_modes: list[int]
    ) -> bool:
        """Apply an RGBWW color setting if requested."""

        *rgb, cw, ww = tuple(x / 255 for x in rgbww_ha)
        color_bri = max(rgb)
        # normalize rgb
        data["rgb"] = tuple(x / (color_bri or 1) for x in rgb)
        color_modes[:] = _filter_color_modes(color_modes, LightColorCapability.RGB)
        if _filter_color_modes(color_modes, LightColorCapability.COLD_WARM_WHITE):
            # Device supports setting cwww values directly
            data["cold_white"] = cw
            data["warm_white"] = ww
            color_modes[:] = _filter_color_modes(
                color_modes, LightColorCapability.COLD_WARM_WHITE
            )
        else:
            # need to convert cw+ww part to white+color_temp
            white = data["white"] = max(cw, ww)
            if white != 0:
                static_info = self._static_info
                min_ct = static_info.min_mireds
                max_ct = static_info.max_mireds
                ct_ratio = ww / (cw + ww)
                data["color_temperature"] = min_ct + ct_ratio * (max_ct - min_ct)
            color_modes[:] = _filter_color_modes(
                color_modes,
                LightColorCapability.COLOR_TEMPERATURE | LightColorCapability.WHITE,
            )

        data["color_brightness"] = color_bri
        return True

    def _apply_transition(
        self, data: dict[str, Any], transition: Any, _color_modes: list[int]
    ) -> bool:
        """Apply a transition."""

        data["transition_length"] = transition
        return False

    def _apply_temperature(
        self, data: dict[str, Any], color_temp_k: Any, color_modes: list[int]
    ) -> bool:
        """Apply a temperature (in kelvins)."""

        # Do not use kelvin_to_mired here to prevent precision loss
        data["color_temperature"] = 1000000.0 / color_temp_k
        if _filter_color_modes(color_modes, LightColorCapability.COLOR_TEMPERATURE):
            color_modes[:] = _filter_color_modes(
                color_modes, LightColorCapability.COLOR_TEMPERATURE
            )
        else:
            color_modes[:] = _filter_color_modes(
                color_modes, LightColorCapability.COLD_WARM_WHITE
            )
        return True

    def _apply_effect(
        self, data: dict[str, Any], effect: Any, _color_modes: list[int]
    ) -> bool:
        """Apply an effect."""
        data["effect"] = effect
        return False

    def _apply_white(
        self, data: dict[str, Any], white_ha: Any, color_modes: list[int]
    ) -> bool:
        # ESPHome multiplies brightness and white together for final brightness
        # HA only sends `white` in turn_on, and reads total brightness
        # through brightness property.
        data["brightness"] = white_ha / 255
        data["white"] = 1.0
        color_modes[:] = _filter_color_modes(
            color_modes,
            LightColorCapability.BRIGHTNESS | LightColorCapability.WHITE,
        )
        return True

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the entity on."""
        data: dict[str, Any] = {"key": self._key, "state": True}
        # The list of color modes that would fit this service call
        color_modes = self._native_supported_color_modes
        try_keep_current_mode = True

        # rgb/brightness input is in range 0-255, but esphome uses 0-1

        # attribute_appliers: dict[
        #   str, Callable[[dict[str, Any], Any, list[int]], bool]
        # ] =

        for key, applier in {
            ATTR_BRIGHTNESS: self._apply_brightness,
            ATTR_FLASH: self._apply_flash,
            ATTR_RGB_COLOR: self._apply_rgb_color,
            ATTR_RGBW_COLOR: self._apply_rgbw_color,
            ATTR_RGBWW_COLOR: self._apply_rgbww_color,
            ATTR_TRANSITION: self._apply_transition,
            ATTR_COLOR_TEMP_KELVIN: self._apply_temperature,
            ATTR_EFFECT: self._apply_effect,
            ATTR_WHITE: self._apply_white,
        }.items():
            if (value := kwargs.get(key)) is None:
                continue
            discard_current_mode = applier(data, value, color_modes)
            if discard_current_mode:
                try_keep_current_mode = False

        if self._supports_color_mode and color_modes:
            if (
                try_keep_current_mode
                and self._state is not None
                and self._state.color_mode in color_modes
            ):
                # if possible, stay with the color mode that is already set
                data["color_mode"] = self._state.color_mode
            else:
                # otherwise try the color mode with the least complexity
                # (fewest capabilities set)
                # popcount with bin() function because it appears
                # to be the best way: https://stackoverflow.com/a/9831671
                color_modes.sort(key=lambda mode: bin(mode).count("1"))
                data["color_mode"] = color_modes[0]

        await self._client.light_command(**data)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the entity off."""
        data: dict[str, Any] = {"key": self._key, "state": False}
        if ATTR_FLASH in kwargs:
            data["flash_length"] = FLASH_LENGTHS[kwargs[ATTR_FLASH]]
        if ATTR_TRANSITION in kwargs:
            data["transition_length"] = kwargs[ATTR_TRANSITION]
        await self._client.light_command(**data)

    @property
    @esphome_state_property
    def brightness(self) -> int | None:
        """Return the brightness of this light between 0..255."""
        return round(self._state.brightness * 255)

    @property
    @esphome_state_property
    def color_mode(self) -> str | None:
        """Return the color mode of the light."""
        if not self._supports_color_mode:
            if not (supported := self.supported_color_modes):
                return None
            return next(iter(supported))

        return _color_mode_to_ha(self._state.color_mode)

    @property
    @esphome_state_property
    def rgb_color(self) -> tuple[int, int, int] | None:
        """Return the rgb color value [int, int, int]."""
        state = self._state
        if not self._supports_color_mode:
            return (
                round(state.red * 255),
                round(state.green * 255),
                round(state.blue * 255),
            )

        return (
            round(state.red * state.color_brightness * 255),
            round(state.green * state.color_brightness * 255),
            round(state.blue * state.color_brightness * 255),
        )

    @property
    @esphome_state_property
    def rgbw_color(self) -> tuple[int, int, int, int] | None:
        """Return the rgbw color value [int, int, int, int]."""
        white = round(self._state.white * 255)
        rgb = cast("tuple[int, int, int]", self.rgb_color)
        return (*rgb, white)

    @property
    @esphome_state_property
    def rgbww_color(self) -> tuple[int, int, int, int, int] | None:
        """Return the rgbww color value [int, int, int, int, int]."""
        state = self._state
        rgb = cast("tuple[int, int, int]", self.rgb_color)
        if not _filter_color_modes(
            self._native_supported_color_modes, LightColorCapability.COLD_WARM_WHITE
        ):
            # Try to reverse white + color temp to cwww
            static_info = self._static_info
            min_ct = static_info.min_mireds
            max_ct = static_info.max_mireds
            color_temp = min(max(state.color_temperature, min_ct), max_ct)
            white = state.white

            ww_frac = (color_temp - min_ct) / (max_ct - min_ct)
            cw_frac = 1 - ww_frac

            return (
                *rgb,
                round(white * cw_frac / max(cw_frac, ww_frac) * 255),
                round(white * ww_frac / max(cw_frac, ww_frac) * 255),
            )
        return (
            *rgb,
            round(state.cold_white * 255),
            round(state.warm_white * 255),
        )

    @property
    @esphome_state_property
    def color_temp_kelvin(self) -> int:
        """Return the CT color value in Kelvin."""
        return _mired_to_kelvin(self._state.color_temperature)

    @property
    @esphome_state_property
    def effect(self) -> str | None:
        """Return the current effect."""
        return self._state.effect

    @callback
    def _on_static_info_update(self, static_info: EntityInfo) -> None:
        """Set attrs from static info."""
        super()._on_static_info_update(static_info)
        static_info = self._static_info
        self._supports_color_mode = self._api_version >= APIVersion(1, 6)
        self._native_supported_color_modes = static_info.supported_color_modes_compat(
            self._api_version
        )
        flags = LightEntityFeature.FLASH

        # All color modes except UNKNOWN,ON_OFF support transition
        modes = self._native_supported_color_modes
        if any(m not in (0, LightColorCapability.ON_OFF) for m in modes):
            flags |= LightEntityFeature.TRANSITION
        if static_info.effects:
            flags |= LightEntityFeature.EFFECT
        self._attr_supported_features = flags

        supported = set(map(_color_mode_to_ha, self._native_supported_color_modes))
        if ColorMode.ONOFF in supported and len(supported) > 1:
            supported.remove(ColorMode.ONOFF)
        if ColorMode.BRIGHTNESS in supported and len(supported) > 1:
            supported.remove(ColorMode.BRIGHTNESS)
        if ColorMode.WHITE in supported and len(supported) == 1:
            supported.remove(ColorMode.WHITE)
        self._attr_supported_color_modes = supported
        self._attr_effect_list = static_info.effects
        self._attr_min_mireds = round(static_info.min_mireds)
        self._attr_max_mireds = round(static_info.max_mireds)
        if ColorMode.COLOR_TEMP in supported:
            self._attr_min_color_temp_kelvin = _mired_to_kelvin(static_info.max_mireds)
            self._attr_max_color_temp_kelvin = _mired_to_kelvin(static_info.min_mireds)
