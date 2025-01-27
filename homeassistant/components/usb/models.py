"""Models helper class for the usb integration."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True, kw_only=True)
class USBDevice:
    """A usb device."""

    device: str
    vid: str
    pid: str
    serial_number: str | None
    manufacturer: str | None
    description: str | None
