"""Support for controlling GPIO pins of a Raspberry Pi."""
from gpiozero import LED, PWMLED, DigitalInputDevice
from gpiozero.pins.pigpio import PiGPIOFactory

from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

CONF_BOUNCETIME = "bouncetime"
CONF_INVERT_LOGIC = "invert_logic"
CONF_PULL_MODE = "pull_mode"
CONF_FREQUENCY = "frequency"

DEFAULT_BOUNCETIME = 50
DEFAULT_INVERT_LOGIC = False
DEFAULT_PULL_MODE = "UP"
DEFAULT_FREQUENCY = 10_000

DOMAIN = "remote_rpi_gpio"


def setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Raspberry Pi Remote GPIO component."""
    return True


def setup_output(address, port, invert_logic):
    """Set up a GPIO as output."""

    try:
        return LED(
            port, active_high=not invert_logic, pin_factory=PiGPIOFactory(address)
        )
    except (ValueError, IndexError, KeyError):
        return None


def setup_pwm_output(address, port, invert_logic, frequency):
    """Set up a GPIO as PWM output."""

    try:
        return PWMLED(
            port,
            active_high=not invert_logic,
            frequency=frequency,
            pin_factory=PiGPIOFactory(address),
        )
    except (ValueError, IndexError, KeyError):
        return None


def setup_input(address, port, pull_mode, bouncetime):
    """Set up a GPIO as input."""

    if pull_mode == "UP":
        pull_gpio_up = True
    elif pull_mode == "DOWN":
        pull_gpio_up = False

    try:
        return DigitalInputDevice(
            port,
            pull_up=pull_gpio_up,
            bounce_time=bouncetime,
            pin_factory=PiGPIOFactory(address),
        )
    except (ValueError, IndexError, KeyError, OSError):
        return None


def write_output(switch, value):
    """Write a value to a GPIO."""
    if value == 1:
        switch.on()
    if value == 0:
        switch.off()


def write_pwm_output(led, value):
    """Write a value to a PWM GPIO."""
    if 0.0 <= value <= 1.0:
        led.value = value


def read_input(sensor):
    """Read a value from a GPIO."""
    return sensor.value
