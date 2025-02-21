# Copyright (c) 2025, Tomasz Pakuła Using Arch BTW

import evdev
from evdev.ecodes import *
from time import sleep
from evdev.device import AbsInfo
from threading import Thread, Event
from boxflat.subscription import SimpleEventDispatcher

class GenericDevice(SimpleEventDispatcher):
    def __init__(self, entry: dict):
        super().__init__()
        self._entry = entry
        self._name = entry["name"]
        self._shutdown = Event()
        self._device = None

        Thread(daemon=True, target=self._hid_read_loop).start()


    def shutdown(self):
        self._shutdown.set()


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
        cap.pop(EV_SYN)
        cap.pop(EV_MSC)

        # Add necessary event types
        if EV_ABS not in cap:
            cap[EV_ABS] = [(ABS_RZ, AbsInfo(0, 0, 255, 8 ,8, 0))]

        if EV_KEY not in cap:
            cap[EV_KEY] = [BTN_JOYSTICK]

        elif BTN_JOYSTICK not in cap[EV_KEY]:
            cap[EV_KEY].append(BTN_JOYSTICK)

        # Create new device
        new_device = evdev.UInput(cap, vendor=device.info.vendor, product=device.info.product, name=device.name)
        print(f"Detection fix applied for {device.name}")
        return new_device
