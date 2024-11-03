# Copyright (c) 2024, Tomasz Pakuła Using Arch BTW

import evdev
import re
from time import sleep

from evdev.ecodes import *
from evdev.device import AbsInfo
from .subscription import EventDispatcher, Observable

from threading import Thread, Lock, Event
from collections import namedtuple
from typing import Self

BTN_JOYSTICK = 0x120
BTN_DEAD = 0x12f
KEY_NEXT_FAVORITE = 0x270


class MozaHidDevice():
    BASE = "gudsen (moza )?r[0-9]{1,2} (base|racing wheel and pedals)"
    PEDALS = "gudsen moza (srp|sr-p|crp)[0-9]? pedals"
    HANDBRAKE = "hbp handbrake"
    HPATTERN = "hgp shifter"
    SEQUENTIAL = "sgp shifter"
    HUB = "gudsen universal hub"
    STALK = "IDK"


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


_HpatternButtons = namedtuple("HpatternButtons", "base hpattern")
_ButtonsSpecifier = namedtuple("ButtonsSpecifier", "start end range")

MOZA_BUTTON_COUNT = 128
MOZA_GEARS = 7
MOZA_HPATTERN_BUTTONS = _HpatternButtons(
    _ButtonsSpecifier(114, 120, [i for i in range(114, 120+1)]),
    _ButtonsSpecifier(6, 12, [i for i in range(6, 12+1)])
)



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



class BlipData():
    def __init__(self) -> None:
        self.enabled = False
        self.duration = 0
        self.level = 0


    def copy(self, data: Self) -> None:
        self.enabled = data.enabled
        self.duration = data.duration
        self.level = data.level



class HidHandler(EventDispatcher):
    def __init__(self):
        super().__init__()

        self._axis_values: dict[str, AxisValue] = {}
        for i in range(MOZA_BUTTON_COUNT):
            self._register_event(f"button-{i+1}")

        for name in MOZA_AXIS_LIST:
            self._axis_values[name] = AxisValue(name)
            self._register_event(name)

        for i in range(MOZA_GEARS):
            self._register_event(f"gear-{i+1}")
            self.subscribe(f"gear-{i+1}", print, f"gear {i+1} yeah")

        self._running = Event()
        self._update_rate = 10
        self._base = None
        self._device_count = Observable(0)
        self._device_count.subscribe(self._device_count_changed)

        self._virtual_devices = {}
        self._devices = {}
        self._blip = BlipData()
        self._last_gear = 0


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

        devices: list[evdev.InputDevice] = [evdev.InputDevice(path) for path in evdev.list_devices()]

        for hid in devices:
            if not re.search(pattern, hid.name.lower()):
                continue

            print(f"HID device found: {hid.name}")
            self._configure_device(hid, pattern)


    def _configure_device(self, device: evdev.InputDevice, pattern: str):
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
        Thread(daemon=True, target=self._hid_read_loop, args=[device, pattern]).start()


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


    def _notify_button(self, number: int, state: int, pattern: str):
        if number <= BTN_DEAD:
            number -= BTN_JOYSTICK - 1
        else:
            number -= KEY_NEXT_FAVORITE - (BTN_DEAD - BTN_JOYSTICK) - 2

        #print(f"button {number}, state: {state}")
        self._dispatch(f"button-{number}", state)

        if pattern == MozaHidDevice.BASE and number in MOZA_HPATTERN_BUTTONS.base.range:
            self._dispatch(f"gear-{number - MOZA_HPATTERN_BUTTONS.base.start + 1}")

        elif pattern == MozaHidDevice.HPATTERN and number in MOZA_HPATTERN_BUTTONS.hpattern.range:
            self._dispatch(f"gear-{number - MOZA_HPATTERN_BUTTONS.hpattern.start + 1}")


    def _hid_read_loop(self, device: evdev.InputDevice, pattern: str):
        sleep(0.3)
        self._devices[pattern] = device
        self.detection_fix(pattern)
        try:
            for event in device.read_loop():
                if pattern in self._virtual_devices:
                    self._virtual_devices[pattern].write_event(event)

                if event.type == EV_ABS:
                    self._update_axis(device, event.code, event.value)

                elif event.type == EV_KEY:
                    self._notify_button(event.code, event.value, pattern)

        except Exception as e:
            # print(e)
            pass

        print(f"HID device disconnected: " + device.name)
        self._device_count.value -= 1
        if device == self._base:
            self._base = None

        self._devices.pop(pattern)
        self.detection_fix(pattern, enabled=False)


    # Driver mode stuff
    def driver_mode_enabled(self, enabled: bool) -> None:
        pass


    def detection_fix(self, pattern: str, enabled: bool=True) -> None:
        if not enabled:
            try:
                self._virtual_devices.pop(pattern).close()
            except KeyError:
                pass
            return

        # Get device capabilities
        device = self._devices[pattern]
        cap: dict = device.capabilities()

        # Return if detection fix is unnecessary
        if EV_ABS in cap and EV_KEY in cap:
            return

        # Remove unneeded event types
        cap.pop(EV_SYN)
        cap.pop(EV_MSC)

        # Add necessary event types
        if not EV_ABS in cap:
            cap[EV_ABS] = [(ABS_Z, AbsInfo(0, 0, 255, 8 ,8, 0))]

        if not EV_KEY in cap:
            cap[EV_KEY] = [BTN_JOYSTICK]

        # Create new device
        new_device = evdev.UInput(cap, vendor=device.info.vendor, product=device.info.product, name=device.name)
        device.grab()
        self._virtual_devices[pattern] = new_device


    def update_blip_data(data: BlipData) -> None:
        self._blip.copy(data)


    def _blip_handler(self) -> None:
        if not self._blip.enabled:
            return

        device: evdev.InputDevice = None
        axis = None

        if MozaHidDevice.PEDALS in self._devices:
            device = self._devices[MozaHidDevice.PEDALS]
            axis = ABS_RX

        elif MozaHidDevice.BASE in self._devices:
            device = self._devices[MozaHidDevice.BASE]
            axis = ABS_Z

        if not device:
            return

        device.write(EV_ABS, axis, self._blip.level)
        device.write(EV_SYN, SYN_REPORT, 0)

        sleep(self._blip.duration/1000)

        device.write(EV_ABS, axis, 0)
        device.write(EV_SYN, SYN_REPORT, 0)



