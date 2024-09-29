import evdev
import re
from time import sleep

from evdev.ecodes import *
from .subscription import SubscribtionList

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
    name: str
    device: str
    base_offset: int

    def __init__(self, n, d):
        self.name = n
        self.device = d


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


MozaAxisCodes = {
    "ABS_RX"     : MozaAxis.THROTTLE.name,
    "ABS_RY"     : MozaAxis.BRAKE.name,
    "ABS_RZ"     : MozaAxis.CLUTCH.name,
    "ABS_RUDDER" : MozaAxis.HANDBRAKE.name
}


MozaAxisBaseCodes = {
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


class HidHandler():
    def __init__(self):
        self._axis_subs = {}
        self._axis_values = {}
        self._button_subs = {}
        self._button_values = {}

        self._running = Event()
        self._update_rate = 120

        self._device_patterns = []
        self._devices = []
        self._base = None

        self._axis_values_lock = Lock()


    def __del__(self):
        self.stop()


    def start(self):
        self._running.set()
        Thread(target=self._notify_axis, daemon=True).start()
        # Thread(target=self._notify_button, daemon=True).start()

    def stop(self):
        self._running.clear()


    def get_update_rate(self) -> int:
        return self._update_rate


    def set_update_rate(self, rate: int) -> bool:
        if rate < 0:
            return False

        self._update_rate = rate
        return True


    def add_device(self, pattern: MozaHidDevice) -> None:
        if not pattern:
            return

        devices = [evdev.InputDevice(path) for path in evdev.list_devices()]

        device = None

        for hid in devices:
            if re.search(pattern, hid.name.lower()):
                print(f"HID device \"{hid.name}\" found")
                device = hid

        if device != None:
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
                if device.absinfo(ecode).fuzz > 8:
                    device.set_absinfo(ecode, fuzz=fuzz)

            Thread(daemon=True, target=self._read_loop, args=[device]).start()


    def subscribe_axis(self, axis: AxisData, callback: callable, *args) -> None:
        if not axis.name in self._axis_subs:
            self._axis_subs[axis.name] = SubscribtionList()
            self._axis_values[axis.name] = 0

        self._axis_subs[axis.name].append(callback, *args)


    def subscribe_button(self, number, callback: callable, *args) -> None:
        if not button in self._button_subs:
            self._button_subs[number] = SubscribtionList()

        self._button_subs[number].append(callback, *args)


    def _notify_axis(self) -> None:
        axis_values = {}
        while self._running.is_set():
            sleep(1/self._update_rate)

            with self._axis_values_lock:
                axis_values = self._axis_values.copy()

            for axis, value in axis_values.items():
                self._axis_subs[axis].call_with_value(value)


    def _notify_button(self) -> None:
        while self._running.is_set():
            sleep(1/self._update_rate)
            for button, value in self._button_values.items():
                self._button_subs[button].call_with_value(value)


    def _update_axis(self, device: evdev.InputDevice, code: int, value: int) -> None:
        axis_min = device.absinfo(code).min
        code = evdev.ecodes.ABS[code]
        name = ""

        if axis_min < 0:
            value += abs(axis_min)

        if device == self._base:
            name = MozaAxisBaseCodes[code]
        else:
            name = MozaAxisCodes[code]

        # print(f"axis {name} ({code}), value: {value}, min: {axis_min}")

        if name in self._axis_values:
            with self._axis_values_lock:
                self._axis_values[name] = value


    def _update_button(self, number: int, state: int) -> None:
        if number <= BTN_DEAD:
            number -= BTN_JOYSTICK - 1
        else:
            number -= KEY_NEXT_FAVORITE - (BTN_DEAD - BTN_JOYSTICK) -2

        # print(f"button {number}, state: {state}")

        if number in self._button_values:
            self._button_values[number] = state


    def _read_loop(self, device: evdev.InputDevice) -> None:
        sleep(1)
        try:
            for event in device.read_loop():
                if event.type == EV_ABS:
                    self._update_axis(device, event.code, event.value)

                # elif event.type == EV_KEY:
                #     self._update_button(event.code, event.value)

        except Exception as e:
            # print(e)
            pass

        print(f"HID device \"{device.name}\" disconnected")
        if device == self._base:
            self._base = None
