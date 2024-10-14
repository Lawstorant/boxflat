# Copyright (c) 2024, Tomasz Pakuła Using Arch BTW

import evdev
import re
from time import sleep

from evdev.ecodes import *
from .subscription import EventDispatcher, Observable

from threading import Thread, Lock, Event


BTN_JOYSTICK = 0x120
BTN_DEAD = 0x12f
KEY_NEXT_FAVORITE = 0x270


class MozaHidDevice():
    BASE = "gudsen moza .* base"
    PEDALS = "gudsen moza .* pedals"
    HANDBRAKE = "hbp handbrake"
    HPATTERN = "hgp shifter"
    SEQUENTIAL = "sgp shifter"
    ESTOP = "IDK"
    STALK = "IDK"
    HUB = "IDK"


class AxisData():
    def __init__(self, name: str, device: str):
        self.name = name
        self.device = device


class MozaAxis():
    STEERING         = AxisData("steering", MozaHidDevice.BASE)
    THROTTLE         = AxisData("throttle", MozaHidDevice.PEDALS)
    BRAKE            = AxisData("brake", MozaHidDevice.PEDALS)
    CLUTCH           = AxisData("clutch", MozaHidDevice.PEDALS)
    COMBINED_PADDLES = AxisData("combined", MozaHidDevice.BASE)
    LEFT_PADDLE      = AxisData("left_paddle", MozaHidDevice.BASE)
    RIGHT_PADDLE     = AxisData("right_paddle", MozaHidDevice.BASE)
    LEFT_STICK_X     = AxisData("stick_x", MozaHidDevice.BASE)
    LEFT_STICK_Y     = AxisData("stick_y", MozaHidDevice.BASE)
    HANDBRAKE        = AxisData("handbrake", MozaHidDevice.HANDBRAKE)


MOZA_AXIS_LIST = [
    "steering",
    "throttle",
    "brake",
    "clutch",
    "combined",
    "left_paddle",
    "right_paddle",
    "stick_x",
    "stick_y",
    "handbrake"
]


MOZA_AXIS_CODES = {
    "ABS_RX"     : MozaAxis.THROTTLE.name,
    "ABS_RY"     : MozaAxis.BRAKE.name,
    "ABS_RZ"     : MozaAxis.CLUTCH.name,
    "ABS_RUDDER" : MozaAxis.HANDBRAKE.name
}


MOZA_AXIS_BASE_CODES = {
    "ABS_X"        : MozaAxis.STEERING.name,
    "ABS_Z"        : MozaAxis.THROTTLE.name,
    "ABS_RZ"       : MozaAxis.BRAKE.name,
    "ABS_THROTTLE" : MozaAxis.CLUTCH.name,
    "ABS_Y"        : MozaAxis.COMBINED_PADDLES.name,
    "ABS_RY"       : MozaAxis.LEFT_PADDLE.name,
    "ABS_RX"       : MozaAxis.RIGHT_PADDLE.name,
    "ABS_HAT0X"    : MozaAxis.LEFT_STICK_X.name,
    "ABS_HAT0Y"    : MozaAxis.LEFT_STICK_Y.name,
    "ABS_RUDDER"   : MozaAxis.HANDBRAKE.name
}


MOZA_BUTTON_COUNT = 128


class AxisValue():
    def __init__(self, name: str):
        self.name = name
        self._lock = Lock()
        self._value = 0


    @property
    def value(self) -> int:
        with self._lock:
            return self._value


    @value.setter
    def value(self, new_value: int):
        with self._lock:
            self._value = new_value


    @property
    def data(self) -> tuple[str, int]:
        return self.name, self.value


class HidHandler(EventDispatcher):
    def __init__(self):
        super().__init__()

        self._axis_values: dict[str, AxisValue] = {}
        for i in range(0, MOZA_BUTTON_COUNT):
            self._register_event(f"button-{i}")

        for name in MOZA_AXIS_LIST:
            self._axis_values[name] = AxisValue(name)
            self._register_event(name)

        self._running = Event()
        self._update_rate = 10
        self._base = None
        self._device_count = Observable(0)
        self._device_count.subscribe(self._device_count_changed)


    def __del__(self):
        self.stop()


    def _device_count_changed(self, new_count):
        if new_count == 0:
            self.stop()

        elif not self._running.is_set():
            Thread(target=self._axis_data_polling, daemon=True).start()


    def stop(self):
        self._running.clear()


    def get_update_rate(self) -> int:
        return self._update_rate


    def set_update_rate(self, rate: int) -> bool:
        if not 0 <= rate <= 1000:
            return False

        self._update_rate = rate
        return True


    def add_device(self, pattern: MozaHidDevice):
        Thread(target=self._add_device, args=[pattern], daemon=True).start()


    def _add_device(self, pattern: MozaHidDevice):
        if not pattern:
            return

        device = None
        # devices: list[evdev.InputDevice] = [evdev.InputDevice(path) for path in evdev.list_devices()]
        for path in evdev.list_devices():
            hid = evdev.InputDevice(path)
            if not re.search(pattern, hid.name.lower()):
                continue

            print(f"HID device found: {hid.name}")
            device = hid
            break

        if device is None:
            return

        if pattern == MozaHidDevice.BASE:
            self._base = device

        capabilities = device.capabilities(absinfo=True, verbose=False)
        if 3 not in capabilities[0]:
            capabilities = []
        else:
            capabilities = capabilities[3]

        for axis in capabilities:
            ecode = axis[0]

            if device.absinfo(ecode).flat > 0:
                device.set_absinfo(ecode, flat=0)

            fuzz = 8
            if device == self._base and ecode == ABS_X:
                fuzz = 0

            # detect current fuzz. Needed for ABS_HAT axes
            if device.absinfo(ecode).fuzz > fuzz:
                device.set_absinfo(ecode, fuzz=fuzz)

        self._device_count.value += 1
        self._hid_read_loop(device)
        # Thread(daemon=True, target=self._hid_read_loop, args=[device]).start()


    def _axis_data_polling(self):
        self._running.set()
        while self._running.is_set():
            sleep(1/self._update_rate)
            for axis in self._axis_values.values():
                self._dispatch(*axis.data)


    def _update_axis(self, device: evdev.InputDevice, code: int, value: int):
        axis_min = device.absinfo(code).min
        code = evdev.ecodes.ABS[code]
        name = ""

        if axis_min < 0:
            value += abs(axis_min)

        if device == self._base:
            name = MOZA_AXIS_BASE_CODES[code]
        else:
            name = MOZA_AXIS_CODES[code]

        # print(f"axis {name} ({code}), value: {value}, min: {axis_min}")
        self._axis_values[name].value = value


    def _notify_button(self, number: int, state: int):
        if number <= BTN_DEAD:
            number -= BTN_JOYSTICK - 1
        else:
            number -= KEY_NEXT_FAVORITE - (BTN_DEAD - BTN_JOYSTICK) - 2

        #print(f"button {number}, state: {state}")
        self._dispatch(f"button-{number}", state)


    def _hid_read_loop(self, device: evdev.InputDevice):
        sleep(0.5)
        try:
            for event in device.read_loop():
                if event.type == EV_ABS:
                    self._update_axis(device, event.code, event.value)

                elif event.type == EV_KEY:
                    self._notify_button(event.code, event.value)

        except Exception as e:
            # print(e)
            pass

        print(f"HID device disconnected: " + device.name)
        self._device_count.value -= 1
        if device == self._base:
            self._base = None
