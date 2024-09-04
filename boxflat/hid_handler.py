import evdev
import re
from time import sleep

from evdev.ecodes import *

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
    "ABS_RX" : MozaAxis.THROTTLE.name,
    "ABS_RY" : MozaAxis.BRAKE.name,
    "ABS_RZ" : MozaAxis.CLUTCH.name,
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

MozaAxisBaseOffsets = [
    MozaAxis.THROTTLE.name,
    MozaAxis.BRAKE.name,
    MozaAxis.CLUTCH.name,
    MozaAxis.COMBINED_PADDLES.name,
    MozaAxis.LEFT_PADDLE.name,
    MozaAxis.RIGHT_PADDLE.name,
    MozaAxis.HANDBRAKE.name,
]


class HidHandler():
    def __init__(self):
        self._axis_subs = {}
        self._button_subs = {}
        self._shutdown = False
        self._device_patterns = []
        self._devices = []
        self._base = None

    def __del__(self):
        self.shutdown()


    def start(self):
        return
        self.find_devices()


    def add_device(self, pattern: MozaHidDevice) -> None:
        if not pattern:
            return

        devices = [evdev.InputDevice(path) for path in evdev.list_devices()]

        device = None

        for hid in devices:
            if re.search(pattern, hid.name.lower()):
                print("HID device added")
                device = hid

        if device != None:
            if pattern == MozaHidDevice.BASE:
                self._base = device

            thread = Thread(daemon=True, target=self._read_loop, args=[device])
            thread.start()


    def find_devices(self) -> None:
        pass
        # self._base = None
        # devices = [evdev.InputDevice(path) for path in evdev.list_devices()]

        # new_devices = []
        # for hid in devices:
        #     for pattern in self._device_patterns:
        #         if re.search(pattern, hid.name.lower()):
        #             print("HID device found")
        #             new_devices.append(evdev.InputDevice(hid.path))

        #     if re.search(MozaHidDevice.BASE, hid.name.lower()):
        #         self._base = evdev.InputDevice(hid.path)

        # for device in new_devices:
        #     self._devices.append(device)
        #     thread = Thread(daemon=True, target=self._read_loop, args=[device])
        #     thread.start()


    def subscribe_axis(self, axis: AxisData, callback: callable, *args) -> None:
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
        name = ""

        if device == self._base:
            name = MozaAxisBaseCodes[code]
            if name in MozaAxisBaseOffsets:
                value += 32767

        else:
            name = MozaAxisCodes[code]

        # print(f"axis {name} ({code}), value: {value}")

        if name in self._axis_subs:
            for sub in self._axis_subs[name]:
                sub[0](value, *sub[1])


    def _notify_button(self, number: int, state: int) -> None:
        if number <= BTN_DEAD:
            number -= BTN_JOYSTICK - 1
        else:
            number -= KEY_NEXT_FAVORITE - (BTN_DEAD - BTN_JOYSTICK) -2

        # print(f"button {number}, state: {state}")

        # if number in self._button_subs.keys():
        #     for sub in self._button_subs[number]:
        #         sub[0](number, state*sub[1])


    def _read_loop(self, device: evdev.InputDevice) -> None:
        sleep(1)
        try:
            for event in device.read_loop():
                if event.type == EV_KEY:
                    self._notify_button(event.code, event.value)

                elif event.type == EV_ABS:
                    self._notify_axis(device, event.code, event.value)

        except Exception as e:
            pass

        print("Hid loop broken")
        if device == self._base:
            self._base = None
        device = None
