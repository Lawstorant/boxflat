from evdev import ecodes
from boxflat.components.hid.device import HidDevice
from enum import StrEnum, auto
from boxflat.devices.types import DeviceType


class Events(StrEnum):
    REVERSE = auto()
    NEUTRAL = auto()
    GEAR    = auto()


class HidHPattern(HidDevice):
    def __init__(self, device_name: str, range_start: int, range_end: int, reverse: int):
        super().__init__(device_name)
        self._device_type = DeviceType.HPATTERN

        self._register_events(*[e.value for e in Events])
        self.subscribe(f"button-{reverse}", self._notify_hpattern, -1)

        self._gears = range_end - range_start + 1;
        for i in range(self._gears):
            self.subscribe(f"button-{range_start+i}", self._notify_hpattern, i+1)


    def _notify_hpattern(self, gear: int, state: int) -> None:
        if state == 0:
            self._dispatch(Events.NEUTRAL)

        if gear == -1:
            self._dispatch(Events.REVERSE)

        self._dispatch(Events.GEAR, gear)
