# Copyright (c) 2025, Tomasz Pakuła Using Arch BTW

import evdev
from evdev.ecodes import *
from time import sleep
from evdev.device import AbsInfo
from threading import Thread, Event
from boxflat.subscription import SimpleEventDispatcher

GAMEPAD_RANGE = range(BTN_GAMEPAD, BTN_THUMBR+1)

class GenericDevice(SimpleEventDispatcher):
    def __init__(self, entry: dict):
        super().__init__()
        self._entry = entry
        self._name = entry["name"]
        self._shutdown = Event()
        self._device = None
        self._ignore_buttons = False
        self._ignore_axes = False

        if "ignore-buttons" in entry:
            self._ignore_buttons = entry["ignore-buttons"]

        if "ignore-axes" in entry:
            self._ignore_axes = entry["ignore-axes"]

        Thread(daemon=True, target=self._hid_read_loop).start()


    def shutdown(self):
        self._shutdown.set()


    def change_ignore_setting(self, type: str, state: bool):
        if type == "buttons":
            self._ignore_buttons = state

        if type == "axes":
            self._ignore_axes = state


    def _try_open(self) -> evdev.InputDevice:
        devices: list[evdev.InputDevice] = [evdev.InputDevice(path) for path in evdev.list_devices()]
        device = None

        for tmp in devices:
            if tmp.name == self._name:
                device = tmp
                break

        if device is None:
            return

        try:
            device.grab()
        except:
            pass

        return device


    def _hid_read_loop(self):
        sleep(0.3)

        new_device = None
        name = self._name
        sleep_time = 0.5

        while not self._shutdown.is_set():
            if self._device is None:
                self._dispatch(self._name, False)
                self._device = self._try_open()

                if self._device is None:
                    sleep(sleep_time)
                    sleep_time = 5
                    continue

                sleep_time = 0.5
                self._dispatch(self._name, True)
                if new_device is None:
                    new_device = self.detection_fix(self._device)

            try:
                for event in self._device.read_loop():
                    if event.type == EV_KEY and self._ignore_buttons:
                        continue

                    if event.type == EV_ABS and self._ignore_axes:
                        continue

                    if event.type == EV_KEY and event.code in GAMEPAD_RANGE:
                        event.code -= 16

                    new_device.write_event(event)
                    if self._shutdown.is_set():
                        break

            except Exception as e:
                print(e)
                self._device = None
                new_device.close()
                new_device = None

        new_device.close()
        try:
            self._device.ungrab()
        except:
            pass


    def detection_fix(self, device: evdev.InputDevice) -> evdev.UInput:
        # Get device capabilities
        cap: dict = device.capabilities()

        # Return if detection fix is unnecessary
        # if EV_ABS in cap and EV_KEY in cap:
        #     print(f"Detection fix not needed for {device.name}")
        #     return

        # Remove unneeded event types
        if EV_SYN in cap:
            cap.pop(EV_SYN)

        if EV_MSC in cap:
            cap.pop(EV_MSC)

        # Add necessary event types
        if EV_ABS not in cap:
            cap[EV_ABS] = []

        x = False
        y = False

        for axis in cap[EV_ABS]:
            if axis[0] == ABS_X:
                x = True

            if axis[0] == ABS_Y:
                y = True

        if not x:
            cap[EV_ABS].append((ABS_X, AbsInfo(0, 0, 255, 8 ,8, 0)))

        if not y:
            cap[EV_ABS].append((ABS_Y, AbsInfo(0, 0, 255, 8 ,8, 0)))

        if EV_KEY not in cap:
            cap[EV_KEY] = [BTN_JOYSTICK]

        elif BTN_JOYSTICK not in cap[EV_KEY]:
            for btn in GAMEPAD_RANGE:
                if btn not in cap[EV_KEY]:
                    continue

                # translate to joystick range
                cap[EV_KEY].remove(btn)
                cap[EV_KEY].append(btn - 16)

            if BTN_JOYSTICK not in cap[EV_KEY]:
                cap[EV_KEY].append(BTN_JOYSTICK)

        # Create new device
        new_device = evdev.UInput(cap, vendor=device.info.vendor, product=device.info.product, name=device.name)
        print(f"Detection fix applied for {device.name}")
        return new_device
