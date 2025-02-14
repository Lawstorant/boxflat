# Copyright (c) 2025, Tomasz Pakuła Using Arch BTW

import evdev
from time import sleep
from evdev.device import AbsInfo
from threading import Event

class GenericDevice(EventDispatcher):
    def __init__(self, path: str):
        super().__init__()
        self._path = path
        self._shutdown = Event()


    def shutdown(self):
        self._shutdown.set()


    def _try_open(self, device_path: str) -> evdev.InputDevice:
        try:
            return evdev.InputDevice(device_path)
        except:
            sleep(1)


    def _hid_read_loop(self, device: evdev.InputDevice, shut_event: event):
        sleep(0.3)

        new_device = self.detection_fix(device)
        if new_device is None:
            return

        device_path = device.path
        name = device.name

        while not self._shutdown.is_set():
            if device is None:
                sleep(0.3)
                device = self._try_open(device_path)
                continue

            try:
                for event in device.read_loop():
                    new_device.write_event(event)

            except Exception as e:
                print(e)
                device.close()
                device = None

        if device is not None:
            device.ungrab()


        print(f"HID device disconnected: " + name)


    def detection_fix(self, device: evdev.InputDevice) -> evdev.UInput:
        # Get device capabilities
        cap: dict = device.capabilities()

        # Return if detection fix is unnecessary
        if EV_ABS in cap and EV_KEY in cap:
            print(f"Detection fix not needed for {device.name}")
            return

        # Remove unneeded event types
        cap.pop(EV_SYN)
        cap.pop(EV_MSC)

        # Add necessary event types
        if EV_ABS not in cap:
            cap[EV_ABS] = [(ABS_RZ, AbsInfo(0, 0, 255, 8 ,8, 0))]

        if EV_KEY not in cap:
            cap[EV_KEY] = [BTN_JOYSTICK]

        # Create new device
        new_device = evdev.UInput(cap, vendor=device.info.vendor, product=device.info.product, name=device.name)
        device.grab()
        print(f"Detection fix applied for {device.name}")

        return new_device
