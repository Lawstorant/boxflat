# Copyright (c) 2024, Tomasz Pakuła Using Arch BTW

import evdev
import re
from time import sleep
from math import ceil

from evdev.ecodes import *
from evdev.device import AbsInfo
from .subscription import EventDispatcher, Observable

from threading import Thread, Lock, Event
from collections import namedtuple
from typing import Self

JOYSTICK_RANGE = (BTN_DEAD - BTN_JOYSTICK) - 1


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


_HpatternButtons = namedtuple("HpatternButtons", "base hpattern hub")
_ButtonsSpecifier = namedtuple("ButtonsSpecifier", "start end range")

MOZA_BUTTON_COUNT = 128
MOZA_GEARS = 7
MOZA_HPATTERN_BUTTONS = _HpatternButtons(
    _ButtonsSpecifier(113, 120, [i for i in range(113, 120+1)]),
    _ButtonsSpecifier(5, 12, [i for i in range(5, 12+1)]),
    _ButtonsSpecifier(5, 12, [i for i in range(5, 12+1)])
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
        self.level = 0
        self.duration = 0


    def copy(self, data: Self) -> None:
        self.enabled = data.enabled
        self.level = data.level
        self.duration = data.duration


    def check(self) -> bool:
        return self.enabled and self.level > 0 and self.duration > 0



class HidHandler(EventDispatcher):
    def __init__(self):
        super().__init__()

        self._axis_values: dict[str, AxisValue] = {}
        for i in range(MOZA_BUTTON_COUNT):
            self._register_event(f"button-{i+1}")

        for name in MOZA_AXIS_LIST:
            self._axis_values[name] = AxisValue(name)
            self._register_event(name)

        self._register_event("gear")
        self.subscribe("gear", self._blip_handler)

        self._running = Event()
        self._update_rate = 10
        self._device_count = Observable(0)
        self._device_count.subscribe(self._device_count_changed)

        self._virtual_devices: dict[evdev.UInput] = {}
        self._devices: dict[evdev.InputDevice] = {}
        self._shutdowns: dict[Event] = {}

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


    def remove_device(self, pattern: MozaHidDevice) -> None:
        if pattern in self._shutdowns:
            self._shutdowns[pattern].set()

        pattern = f"{pattern}_2"
        if pattern in self._shutdowns:
            self._shutdowns[pattern].set()


    def _configure_device(self, device: evdev.InputDevice, pattern: str):
        capabilities = device.capabilities(absinfo=True, verbose=False)
        if EV_ABS not in capabilities[0]:
            capabilities = []
        else:
            capabilities = capabilities[EV_ABS]

        for axis in capabilities:
            ecode = axis[0]

            if device.absinfo(ecode).flat > 0:
                device.set_absinfo(ecode, flat=0)

            fuzz = 8
            if pattern == MozaHidDevice.BASE and ecode == ABS_X:
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


    def _update_axis(self, code: int, value: int, pattern: str):
        code = evdev.ecodes.ABS[code]
        name = ""

        if pattern in (MozaHidDevice.BASE, MozaHidDevice.HUB):
            name = MOZA_AXIS_BASE_CODES[code]
        else:
            name = MOZA_AXIS_CODES[code]

        print(f"axis {name} ({code}), value: {value}")
        self._axis_values[name].value = value


    def _notify_button(self, number: int, state: int, pattern: str):
        if number <= BTN_DEAD:
            number -= BTN_JOYSTICK - 1
        else:
            if pattern == MozaHidDevice.BASE:
                number -= KEY_NEXT_FAVORITE - JOYSTICK_RANGE - 1
            else:
                number -= BTN_TRIGGER_HAPPY - JOYSTICK_RANGE - 1

        # print(f"button {number}, state: {state}")
        self._dispatch(f"button-{number}", state)

        if pattern == MozaHidDevice.BASE and number in MOZA_HPATTERN_BUTTONS.base.range:
            gear = number - MOZA_HPATTERN_BUTTONS.base.start

        elif pattern == MozaHidDevice.HPATTERN and number in MOZA_HPATTERN_BUTTONS.hpattern.range:
            gear = number - MOZA_HPATTERN_BUTTONS.hpattern.start

        elif MozaHidDevice.HUB in pattern and number in MOZA_HPATTERN_BUTTONS.hub.range:
            gear = number - MOZA_HPATTERN_BUTTONS.hub.start

        else:
            return

        self._blip_handler(gear, state)
        self._dispatch("gear", gear, state)


    def _try_open(self, device_path: str) -> evdev.InputDevice:
        try:
            return evdev.InputDevice(device_path)
        except:
            pass


    def _hid_read_loop(self, device: evdev.InputDevice, pattern: str):
        sleep(0.3)
        if pattern in self._devices:
            pattern = f"{pattern}_2"

        self._devices[pattern] = device
        shutdown = Event()
        self._shutdowns[pattern] = shutdown

        self.detection_fix(pattern)
        device_path = device.path
        name = device.name

        while not shutdown.is_set():
            if device is None:
                sleep(0.3)
                device = self._try_open(device_path)
                continue

            try:
                for event in device.read_loop():
                    if pattern in self._virtual_devices:
                        self._virtual_devices[pattern].write_event(event)

                    if event.type == EV_ABS:
                        offset = -device.absinfo(event.code).min
                        self._update_axis(event.code, int(event.value) + offset, pattern)

                    elif event.type == EV_KEY:
                        self._notify_button(event.code, event.value, pattern)

            except:
                device.close()
                device = None


        print(f"HID device disconnected: " + name)
        self._device_count.value -= 1

        self._devices.pop(pattern)
        self._shutdowns.pop(pattern)
        self.detection_fix(pattern, enabled=False)


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
        if EV_ABS not in cap:
            cap[EV_ABS] = [(ABS_Z, AbsInfo(0, 0, 255, 8 ,8, 0))]

        if EV_KEY not in cap:
            cap[EV_KEY] = [BTN_JOYSTICK]

        # Create new device
        new_device = evdev.UInput(cap, vendor=device.info.vendor, product=device.info.product, name=device.name)
        device.grab()
        self._virtual_devices[pattern] = new_device


    def copy_blip_data(data: BlipData) -> None:
        self._blip.copy(data)


    def update_blip_data(self, enabled: bool=None, level: int=None, duration: int=None) -> None:
        if enabled is not None:
            self._blip.enabled = enabled

        if level is not None:
            if 0 <= level <= 100:
                self._blip.level = level

        if duration is not None:
            if 0 <= duration <= 1000:
                self._blip.duration = duration


    def _blip_handler(self, gear: int, state: int) -> None:
        Thread(target=self._blip_handler_worker, args=[gear, state], daemon=True).start()


    def _blip_handler_worker(self, gear: int, state: int) -> None:
        if not self._blip.check():
            return

        if state != 1 or gear < 1:
            return

        last_gear = self._last_gear
        self._last_gear = gear
        print(f"Last gear: {last_gear}, Gear: {gear}, state: {state}")

        if gear + 1 != last_gear:
            return

        print(f"BLIP! Level {self._blip.level}%, Duration: {self._blip.duration}ms")
        device: evdev.InputDevice = None
        axis = None

        if MozaHidDevice.PEDALS in self._devices:
            device = self._devices[MozaHidDevice.PEDALS]
            axis = ABS_RX

        elif MozaHidDevice.HUB in self._devices:
            device = self._devices[MozaHidDevice.HUB]
            axis = ABS_Z

        elif MozaHidDevice.BASE in self._devices:
            device = self._devices[MozaHidDevice.BASE]
            axis = ABS_Z

        if not device:
            return

        info = device.absinfo(axis)
        level = ceil((self._blip.level / 100) * (info.max - info.min) + info.min)
        # print(f"Computed level: {level} ({info.min}:{info.max})")

        device.write(EV_ABS, axis, level)
        device.write(EV_SYN, SYN_REPORT, 0)

        sleep(self._blip.duration/1000)

        device.write(EV_ABS, axis, info.min)
        device.write(EV_SYN, SYN_REPORT, 0)
