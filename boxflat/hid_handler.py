import evdev
import re
from time import sleep
from enum import StrEnum, auto

from threading import Thread
from threading import Lock
from threading import Event


BTN_JOYSTICK = 0x120
BTN_DEAD = 0x12f
KEY_NEXT_FAVORITE = 0x270


class MozaHidDevice():
    BASE = "gudsen moza .* base"
    PEDALS = "gudsen moza .* pedals"
    HANDBRAKE = "hbp handbrake"
    HPATTERN = "hgp shifter"
    SEQUENTIAL = "sgp shifter"
    STALK = "IDK yet"


class AxisData():
    name: str
    device: str

    def __init__(self, n, d):
        self.name = n
        self.device = d


class MozaAxis():
    STEERING =         AxisData("steering", MozaHidDevice.BASE)
    THROTTLE =         AxisData("throttle", MozaHidDevice.PEDALS)
    BRAKE    =         AxisData("brake", MozaHidDevice.PEDALS)
    CLUTCH   =         AxisData("clutch", MozaHidDevice.PEDALS)
    COMBINED_PADDLES = AxisData("combined", MozaHidDevice.BASE)
    LEFT_PADDLE  =     AxisData("left_paddle", MozaHidDevice.BASE)
    RIGHT_PADDLE =     AxisData("right_paddle", MozaHidDevice.BASE)
    LEFT_STICK_X =     AxisData("stick_x", MozaHidDevice.BASE)
    LEFT_STICK_Y =     AxisData("stick_y", MozaHidDevice.BASE)
    HANDBRAKE    =     AxisData("handbrake", MozaHidDevice.HANDBRAKE)


MozaAxisCodes = {
    "ABS_X" : MozaAxis.STEERING.name,
    "ABS_RX" : MozaAxis.THROTTLE.name,
    "ABS_RZ" : MozaAxis.BRAKE.name,
    "ABS_RY" : MozaAxis.CLUTCH.name,
    "ABS_Y" : MozaAxis.COMBINED_PADDLES.name,
    "ABS_RY" : MozaAxis.LEFT_PADDLE.name,
    "ABS_RX" : MozaAxis.RIGHT_PADDLE.name,
    "ABS_HAT0X" : MozaAxis.LEFT_STICK_X.name,
    "ABS_HAT0Y" : MozaAxis.LEFT_STICK_Y.name,
    "ABS_RUDDER" : MozaAxis.HANDBRAKE.name
}


MozaAxisBaseCodes = {
    "ABS_X" : MozaAxis.STEERING.name,
    "ABS_Z" : MozaAxis.THROTTLE.name,
    "ABS_RZ" : MozaAxis.BRAKE.name,
    "ABS_THROTTLE" : MozaAxis.CLUTCH.name,
    "ABS_Y" : MozaAxis.COMBINED_PADDLES.name,
    "ABS_RY" : MozaAxis.LEFT_PADDLE.name,
    "ABS_RX" : MozaAxis.RIGHT_PADDLE.name,
    "ABS_HAT0X" : MozaAxis.LEFT_STICK_X.name,
    "ABS_HAT0Y" : MozaAxis.LEFT_STICK_Y.name,
    "ABS_RUDDER" : MozaAxis.HANDBRAKE.name
}


class HidHandler():
    def __init__(self):
        self._axis_subs = {}
        self._button_subs = {}
        self._shutdown = False
        self._device_patterns = []
        self._devices = []
        self._base = None

        self._read_thread = Thread(target=self._read_loop)


    def __del__(self):
        self.shutdown()


    def start(self):
        self._read_thread.start()


    def shutdown(self):
        self._shutdown = True


    def _find_devices(self) -> None:
        self._devices = []
        self._base = None

        devices = [evdev.InputDevice(path) for path in evdev.list_devices()]

        for hid in devices:
            for pattern in self._device_patterns:
                if re.search(pattern, hid.name.lower()):
                    self._devices.append(evdev.InputDevice(hid.path))

            if re.search(MozaHidDevice.BASE, hid.name.lower()):
                self._base = evdev.InputDevice(hid.path)

        for device in self._devices:
            if device == None:
                device = self._base


    def subscribe_axis(self, axis: AxisData, callback: callable, *args) -> None:
        if axis.device not in self._device_patterns:
            self._device_patterns.append(axis.device)

        # self._find_devices()
        # device = self._devices[self._device_patterns.index(axis.device)]

        if not axis.name in self._axis_subs:
            self._axis_subs[axis.name] = []

        self._axis_subs[axis.name].append((callback, args))


    def subscribe_button(self, number, callback: callable, *args) -> None:
        # if not button in self._button_subs:
        #     self._button_subs[number] = []

        # self._button_subs[number].append((callback, args))
        pass


    def _notify_axis(self, device: evdev.InputDevice, code: int, value: int) -> None:
        code = evdev.ecodes.ABS[code]
        # print(f"axis {code}, value: {value}")
        name = ""

        if device == self._base:
            name = MozaAxisBaseCodes[code]
        else:
            name = MozaAxisCodes[code]

        if name in self._axis_subs:
            for sub in self._axis_subs[name]:
                sub[0](value, *sub[1])


    def _notify_button(self, device: evdev.InputDevice, number: int, state: int) -> None:
        if number <= BTN_DEAD:
            number -= BTN_JOYSTICK - 1
        else:
            number -= KEY_NEXT_FAVORITE + (BTN_DEAD - BTN_JOYSTICK)

        print(f"button {number}, state: {state}")

        # if number in self._button_subs.keys():
        #     for sub in self._button_subs[number]:
        #         sub[0](number, state*sub[1])


    def _read_loop(self) -> None:
        find = True

        while not self._shutdown:
            sleep(1/500)

            if len(self._devices) == 0:
                find = True

            if find:
                find = False
                sleep(1)
                self._find_devices()

            for device in self._devices:
                try:
                    event = device.read_one()
                except Exception as error:
                    print("HID device not found")
                    find = True
                    continue

                if not event:
                    continue

                if event.type == evdev.ecodes.EV_KEY:
                    self._notify_button(device, event.code, event.value)

                elif event.type == evdev.ecodes.EV_ABS:
                    self._notify_axis(device, event.code, event.value)
