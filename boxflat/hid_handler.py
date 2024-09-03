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


class MozaAxis():
    STEERING =         ("X", "X")
    THROTTLE =         ("RX", "Z")
    BRAKE    =         ("RZ", "RZ")
    CLUTCH   =         ("RY", "THROTTLE")
    COMBINED_PADDLES = ("Y", "Y")
    LEFT_PADDLE  =     ("RY", "RY")
    RIGHT_PADDLE =     ("RX", "RX")
    LEFT_STICK_X =     ("HAT_0X", "HAT_0X")
    LEFT_STICK_Y =     ("HAT_0Y", "HAT_0Y")
    HANDBRAKE    =     ("RUDDER", "RUDDER")


class HidHandler():
    def __init__(self, device_pattern: str):
        self._axis_subs = {}
        self._button_subs = {}
        self._shutdown = False
        self._device = None
        self._base = None

        devices = [evdev.InputDevice(path) for path in evdev.list_devices()]

        for hid in devices:
            if re.search(device_pattern, hid.name.lower()):
                self._device = evdev.InputDevice(hid.path)

            if re.search(MozaHidDevice.BASE, hid.name.lower()):
                self._base = evdev.InputDevice(hid.path)

        if self._device == None:
            self._device = self._base

        self._read_thread = Thread(target=self._read_loop)
        self._read_thread.start()


    def __del__(self):
        self.shutdown()


    def shutdown(self):
        self._shutdown = True


    def subscribe_axis(self, axis: tuple, callback: callable, *args) -> None:
        if self._device == self._base:
            axis = axis[1]
        else:
            axis = axis[0]

        axis = "ABS_" + axis

        if not axis in self._axis_subs:
            self._axis_subs[axis] = []

        self._axis_subs[axis].append((callback, args))


    def subscribe_button(self, number, callback: callable, *args) -> None:
        if not button in self._button_subs:
            self._button_subs[number] = []

        self._button_subs[number].append((callback, args))


    def _notify_axis(self, code: int, value: int) -> None:
        name = evdev.ecodes.ABS[code]
        print(f"axis {name}, value: {value}")

        if name in self._axis_subs.keys():
            for sub in self._axis_subs[name]:
                sub[0](value, *sub[1])


    def _notify_button(self, number: int, state: int) -> None:
        if number <= BTN_DEAD:
            number -= BTN_JOYSTICK - 1
        else:
            number -= KEY_NEXT_FAVORITE + (BTN_DEAD - BTN_JOYSTICK)

        # print(f"button {number}, state: {state}")

        if number in self._button_subs.keys():
            for sub in self._button_subs[number]:
                sub[0](number, state*sub[1])


    def _read_loop(self) -> None:
        if not self._device:
            print("HID device not found!")
            return

        while not self._shutdown:
            sleep(1/200)
            try:
                event = self._device.read_one()
            except Exception as error:
                self.shutdown()
                continue

            if not event:
                continue

            if event.type == evdev.ecodes.EV_KEY:
                self._notify_button(event.code, event.value)

            elif event.type == evdev.ecodes.EV_ABS:
                self._notify_axis(event.code, event.value)




