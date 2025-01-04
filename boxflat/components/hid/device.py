# Copyright (c) 2024, Tomasz Pakuła Using Arch BTW

import evdev
import re
from time import sleep

from evdev.ecodes import *
from evdev.device import AbsInfo
from evdev import InputDevice, UInput
from boxflat.components.subscription import EventDispatcher, Observable
from boxflat.devices.types import DeviceType
from threading import Thread, Lock, Event
from enum import StrEnum, auto


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



class HidDevice(EventDispatcher):
    def __init__(self, device_name: str):
        super().__init__()

        self._device_name = device_name
        self._device_type = DeviceType.GENERIC

        self._running = Event()
        self._shutdown = Event()
        self._update_rate = 10

        self._axis_values: dict[AxisValue] = {}

        self._device: InputDevice = self._open_device()
        self._virtual_device: UInput = self._detection_fix()

        cap = self._device.capabilities()
        if EV_ABS in cap:
            for axis in cap[EV_ABS]:
                name = evdev.ecodes.EV_ABS[axis]
                self._axis_values[axis] = AxisValue(name)
                self._register_event(name)

        i = 1;
        self._button_map = {}
        self._reverse_button_list = []
        if EV_KEY in cap:
            for key in cap[EV_KEY]:
                self._button_map[key] = i
                self._reverse_button_list.append(key)
                self._register_event(f"button-{i}")
                i += 1;

        Thread(daemon=True, target=self._hid_read_loop).start()


    def stop(self):
        self._shutdown.clear()


    def get_type(self) -> int:
        return self._device_type


    def get_update_rate(self) -> int:
        return self._update_rate


    def set_update_rate(self, rate: int) -> bool:
        if not 0 <= rate <= 1000:
            return False

        self._update_rate = rate
        return True


    def _open_device(self) -> evdev.ecodes.EV_ABS[axis]:
        devices: list[InputDevice] = [InputDevice(path) for path in evdev.list_devices()]

        for hid in devices:
            if not hid.name.lower() == self.device_name.lower():
                continue

            print(f"HID device found: {hid.name}")
            self._configure_device(hid)
            return hid


    def _configure_device(self, device: InputDevice):
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
            # detect current fuzz. Needed for ABS_HAT axes
            if device.absinfo(ecode).fuzz > fuzz:
                device.set_absinfo(ecode, fuzz=fuzz)


    def reconfigure_fuzz(self, axis: str, new_fuzz: int) -> None:
        code = ecodes[axis]
        if code not in self._axis_values:
            return

        self._device.set_absinfo(code, fuzz=new_fuzz)


    def _axis_data_polling(self):
        if len(self._axis_values) == 0:
            return

        while not self._shutdown.is_set():
            sleep(1/self._update_rate)
            for axis in self._axis_values.values():
                self._dispatch(*axis.data)


    def _update_axis(self, code: int, value: int):
        self._axis_values[code].value = value


    def _notify_button(self, code: int, state: int):
        number = self._button_map[code]
        self._dispatch(f"button-{number}", state)


    def _try_open(self, device_path: str) -> InputDevice:
        try:
            return InputDevice(device_path)
        except:
            pass


    def _hid_read_loop(self):
        sleep(0.3)
        shutdown = Event()

        device_path = self._device.path
        name = self._device.name

        while not shutdown.is_set():
            if self._device is None:
                sleep(0.3)
                self._device = self._try_open(device_path)
                continue

            try:
                for event in self._device.read_loop():
                    if self._virtual_device is not None:
                        self._virtual_devices[pattern].write_event(event)

                    if event.type == EV_ABS:
                        offset = -self._device.absinfo(event.code).min
                        self._update_axis(event.code, int(event.value) + offset)

                    elif event.type == EV_KEY:
                        self._notify_button(event.code, event.value)

            except:
                self._device.close()
                self._device = None


        print(f"HID device disconnected: " + name)


    def _detection_fix(self) -> UInput:
        # Get device capabilities
        device = self._device
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
        virtual_device = UInput(cap, vendor=device.info.vendor, product=device.info.product, name=device.name)
        device.grab()
        return virtual_device


    def _insert_event(ev_type: int, code: int, value: int) -> None:
        self._device_write(ev_type, code, value)
        self._device_write(EV_SYN, SYN_REPORT, 0)


    def insert_button_event(self, button_number: int, state: int) -> None:
        if button_number not in self._reverse_button_list:
            return

        self._insert_event(EV_KEY, self._reverse_button_list[button_number], state)


    def insert_axis_event(self, axis: int, value: int) -> None:
        if axis not in self._axis_values:
            return

        self._insert_event(EV_ABS, axis, value)


    def insert_event(self, event: str, value: int) -> None:
        pass
