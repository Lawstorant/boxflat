# Copyright (c) 2025, Tomasz Pakuła Using Arch BTW

from boxflat.panels.settings_panel import SettingsPanel
from boxflat.widgets import *
from boxflat.settings_handler import SettingsHandler

import evdev
from evdev import ecodes
from binascii import hexlify

class GenericSettings(SettingsPanel):
    def __init__(self, button_callback, settings: SettingsHandler):
        self._settings = settings
        self._device_list = None
        self._listed_devices = []
        super().__init__("Generic Devices", button_callback)


    def active(self, value: int):
        pass


    def prepare_ui(self) -> None:
        self.add_preferences_group("Devices with detection fix", suffix=True)
        self._device_list = self._current_group
        self._current_group.subscribe(lambda *_: self.add_device("test"))

        self.list_candidates()

        self.list_configured_devices()


    def list_configured_devices(self) -> None:
        for entry in self._listed_devices:
            self._device_list.remove(entry)

        self._listed_devices = []
        devices = self._settings.read_setting("generic-devices")
        if devices is None or len(devices) < 1:
            row = BoxflatLabelRow("No configured devices")
            self._add_row(row)
            self._listed_devices.append(row)
            return

        for device in devices:
            row = BoxflatButtonRow(device["name"], "Remove")
            self._add_row(row)
            self._current_row.subscribe(self.remove_device, device)
            self._listed_devices.append(row)


    def list_candidates(self) -> None:
        devices: list[evdev.InputDevice] = [evdev.InputDevice(path) for path in evdev.list_devices()]
        for device in devices:
            capabilities = device.capabilities(absinfo=False, verbose=False)
            axes = ecodes.EV_ABS in capabilities[0]
            keys = ecodes.EV_KEY in capabilities[0]

            # device filtering
            if not axes and not keys:
                continue

            if keys and ecodes.BTN_JOYSTICK not in capabilities[ecodes.EV_KEY]:
                continue

            if axes:
                axes = False
                for i in range(ecodes.ABS_BRAKE):
                    if i in capabilities[ecodes.EV_ABS]:
                        axes = True
                        break

                if not axes:
                    continue

            self.add_device(device.path)


    def add_device(self, path: str) -> None:
        if path == "test":
            print("XDD")
            return

        device = evdev.InputDevice(path)
        entry = {
            "name": device.name,
            "vid": "0x{:04x}".format(device.info.vendor),
            "pid": "0x{:04x}".format(device.info.product),
        }

        devices = self._settings.read_setting("generic-devices") or []
        if entry in devices:
            return

        devices.append(entry)
        self._settings.write_setting(devices, "generic-devices")


    def remove_device(self, state: int, device: dict) -> None:
        devices: list = self._settings.read_setting("generic-devices")
        devices.remove(device)
        self._settings.write_setting(devices, "generic-devices")

        self.list_configured_devices()
