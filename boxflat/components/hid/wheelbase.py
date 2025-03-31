from evdev import ecodes
from boxflat.components.hid.device import HidDevice
from enum import StrEnum, auto
from boxflat.devices.types import DeviceType


class Events(StrEnum):
    STEERING = auto()

class HidWheelase(HidDevice):
    def __init__(self, device_name: str, axis: int):
        super().__init__(device_name)
        self._device_type = DeviceType.WHEELBASE

        self._register_events(*[e.value for e in Events])

        self.subscribe(ecodes.EV_ABS[axis], self._dispatch, Events.STEERING)

        if button is not None:
            self.subscribe(f"button-{button}", lambda s: self._dispatch(Events.HANDBRAKE, s*65535))
