from evdev import ecodes
from boxflat.components.hid.device import HidDevice
from enum import StrEnum, auto
from boxflat.devices.types import DeviceType
from threading import Thread
from time import sleep


class Events(StrEnum):
    THROTTLE = auto()
    BRAKE    = auto()
    CLUTCH   = auto()


class HidPedals(HidDevice):
    def __init__(self, device_name: str, throttle_axis: int, brake_axis: int, clutch_axis: int):
        super().__init__(device_name)
        self._device_type = DeviceType.PEDALS

        self._axis_map = {
            Events.THROTTLE : throttle_axis,
            Events.BRAKE    : brake_axis,
            Events.CLUTCH   : clutch_axis
        }

        self._register_events(*[e.value for e in Events])
        self.subscribe(ecodes.EV_ABS[throttle_axis], self._dispatch, Events.THROTTLE)
        self.subscribe(ecodes.EV_ABS[brake_axis], self._dispatch, Events.BRAKE)
        self.subscribe(ecodes.EV_ABS[clutch_axis], self._dispatch, Events.CLUTCH)


    def insert_event(self, event: str, value: int) -> None:
        self.insert_axis_event(self._axis_map[event], value)


    def throttle_blip(self, level: int, duration: int) -> None:
        Thread(daemon=True, target=self.insert_event, args=[level, duration]).start()

    def __throttle_blip(self, level: int, duration: int) -> None:
        axis = self._axis_map[Events.THROTTLE]
        axis_min = self._device.absinfo(axis).min
        axis_max = self._device.absinfo(axis).max

        self.insert_axis_event(axis, (axis_max - axis_min) * (level/100))
        sleep(duration/1000)
        self.insert_axis_event(axis, axis_min)
