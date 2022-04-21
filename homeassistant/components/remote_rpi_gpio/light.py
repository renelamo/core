"""Allows to configure a light using RPi GPIO."""

from __future__ import annotations

import voluptuous as vol

from homeassistant.components import light
from homeassistant.const import CONF_HOST, DEVICE_DEFAULT_NAME
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from . import CONF_FREQUENCY, CONF_INVERT_LOGIC, DEFAULT_FREQUENCY, DEFAULT_INVERT_LOGIC
from .. import remote_rpi_gpio

CONF_PORTS = "ports"

_SENSORS_SCHEMA = vol.Schema({cv.string: [cv.positive_int]})

light.PLATFORM_SCHEMA = light.PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_PORTS): _SENSORS_SCHEMA,
        vol.Optional(CONF_INVERT_LOGIC, default=DEFAULT_INVERT_LOGIC): cv.boolean,
        vol.Optional(CONF_FREQUENCY, default=DEFAULT_FREQUENCY): cv.positive_int,
    }
)


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the Remote Raspberry PI GPIO devices."""
    address = config[CONF_HOST]
    invert_logic = config[CONF_INVERT_LOGIC]
    ports = config[CONF_PORTS]
    frequency = config[CONF_FREQUENCY]

    devices = []
    for name, port in ports.items():
        try:
            leds = []
            for pin in port:
                led = remote_rpi_gpio.setup_pwm_output(
                    address, pin, invert_logic, frequency
                )
                leds.append(led)
        except (ValueError, IndexError, KeyError, OSError):
            return
        new_light = RemoteRPiGPIOLight(name, tuple(leds))
        devices.append(new_light)

    add_entities(devices)


class RemoteRPiGPIOLight(light.LightEntity):
    """Representation of a Light controlled by PWM GPIOs."""

    _attr_supported_color_modes = {light.ColorMode.BRIGHTNESS, light.ColorMode.RGB}
    _attr_color_mode = light.COLOR_MODE_RGB
    _attr_should_poll = False
    _attr_assumed_state = True

    def __init__(self, name, pins):
        """Initialize the pins."""
        self._attr_name = name or DEVICE_DEFAULT_NAME
        if len(pins) != 3:
            raise ValueError("This entity only supports 3-pins (RGB) hardware.")
        self._pins = pins
        self._attr_brightness = 255
        self._attr_rgb_color = (255, 255, 255)
        self._attr_is_on = False

    def turn_on(self, **kwargs):
        """Turn the device on."""

        if light.ATTR_RGB_COLOR in kwargs:
            self._attr_rgb_color = kwargs[light.ATTR_RGB_COLOR]

        if light.ATTR_BRIGHTNESS in kwargs:
            self._attr_brightness = kwargs[light.ATTR_BRIGHTNESS]

        for i, pin in enumerate(self._pins):
            remote_rpi_gpio.write_pwm_output(
                pin, self._attr_rgb_color[i] / 255.0 * self._attr_brightness / 255.0
            )

        self._attr_is_on = True
        self.schedule_update_ha_state()

    def turn_off(self, **kwargs):
        """Turn the device off."""
        for pin in self._pins:
            remote_rpi_gpio.write_pwm_output(pin, 0.0)
        self._attr_is_on = False
        self.schedule_update_ha_state()
