from evdev import ecodes
from boxflat.components.hid.device import HidDevice
from enum import StrEnum, auto
from boxflat.devices.types import DeviceType


class Events(StrEnum):
    GEAR_DOWN = auto()
    GEAR_UP   = auto()


class HidSequential(HidDevice):
    def __init__(self, device_name: str, button_up: int, button_down: int):
        super().__init__(device_name)
        self._device_type = DeviceType.SEQUENTIAL

        self._register_events(*[e.value for e in Events])
        self.subscribe(f"button-{button_up}", self._notify_seq, Events.GEAR_UP)
        self.subscribe(f"button-{button_down}", self._notify_seq, Events.GEAR_DOWN)


    def _notify_seq(self, event: str, state: int) -> None:
        if state == 0:
            return

        self._dispatch(event)
