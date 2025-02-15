# Copyright (c) 2025, Tomasz Pakuła Using Arch BTW

from boxflat.panels.settings_panel import SettingsPanel
from boxflat.widgets import *
from boxflat.settings_handler import SettingsHandler
from boxflat.hid_handler import is_moza_device
from boxflat.generic import GenericDevice

import evdev
from evdev import ecodes
from binascii import hexlify

class GenericSettings(SettingsPanel):
    def __init__(self, button_callback, settings: SettingsHandler):
        self._settings = settings
        self._device_list: BoxflatPreferencesGroup = None
        self._candidates_list: BoxflatPreferencesGroup = None
        self._back: BoxflatPreferencesGroup = None
        self._listed_devices = {}
        self._fixed_devices = {}
        self._candidates = []
        super().__init__("Generic Devices", button_callback)


    def active(self, value: int):
        pass


    def prepare_ui(self) -> None:
        self.add_preferences_group("Devices with detection fix", suffix=True)
        self._device_list = self._current_group
        self._current_group.subscribe(self.list_candidates)
        self._current_group.set_size_request(620, 0)

        self.add_preferences_group("Connected joysticks")
        self._candidates_list = self._current_group
        self._current_group.set_present(False)
        self._current_group.set_size_request(620, 0)

        self.add_preferences_group("")
        self._back = self._current_group
        self._current_group.set_present(False)
        self._add_row(BoxflatAdvanceRow("Go back"))
        self._current_row.subscribe(self.list_configured_devices)
        self._current_group.set_size_request(620, 0)

        self.list_configured_devices()
        self.fix_devices()


    def list_configured_devices(self, *_) -> None:
        self._back.set_present(False)
        self._candidates_list.set_present(False)

        for entry in self._listed_devices.values():
            self._device_list.remove(entry)

        self._listed_devices = {}
        self._current_group = self._device_list
        devices = self._settings.read_setting("generic-devices") or []

        if len(devices) < 1:
            row = BoxflatLabelRow("No configured devices")
            self._add_row(row)
            self._listed_devices["empty"] = row

        for device in devices:
            row = BoxflatButtonRow(device["name"], "Remove")
            row.subscribe(self.remove_device, device)
            self._add_row(row)
            self._listed_devices[device["name"]] = row

        self._device_list.set_present(True)


    def list_candidates(self, *_) -> None:
        self._device_list.set_present(False)
        self._candidates_list.set_present(True)
        self._current_group = self._candidates_list

        for candidate in self._candidates:
            self._current_group.remove(candidate)

        self._candidates = []
        devices = self._settings.read_setting("generic-devices") or []
        names = [device["name"] for device in devices]

        devices: list[evdev.InputDevice] = [evdev.InputDevice(path) for path in evdev.list_devices()]
        for device in devices:
            if device.name in names:
                continue

            if is_moza_device(device.name):
                continue

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

            row = BoxflatButtonRow(device.name, "Fix Detection")
            row.subscribe(self.add_device, device.path, True)
            self._add_row(row)
            self._candidates.append(row)

        if len(self._candidates) < 1:
            row = BoxflatLabelRow("No promising devices")
            self._add_row(row)
            self._candidates.append(row)

        self._back.set_present(True)


    def add_device(self, something, path: str, refresh=False) -> None:
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

        if refresh:
            self.list_configured_devices()
            self.fix_devices()


    def remove_device(self, state: int, device: dict) -> None:
        devices: list = self._settings.read_setting("generic-devices")
        devices.remove(device)
        self._settings.write_setting(devices, "generic-devices")

        self.list_configured_devices()
        self.fix_devices()


    def fix_devices(self, *_) -> None:
        to_fix = self._settings.read_setting("generic-devices") or []
        names = [device["name"] for device in to_fix]

        fixed_names = list(self._fixed_devices.keys())

        for name in fixed_names:
            self._fixed_devices[name].shutdown()
            self._fixed_devices.pop(name)

        for device in to_fix:
            name = device["name"]
            if name in self._fixed_devices:
                continue

            self._fixed_devices[name] = GenericDevice(device)
            self._fixed_devices[name].subscribe(self._change_device_state)


    def _change_device_state(self, name: str, state: bool) -> None:
        if name not in self._listed_devices.keys():
            return

        text = " (disconnected)"
        label: str = self._listed_devices[name].get_title()

        if state:
            label = label.removesuffix(text)

        elif text not in label:
            label += text

        self._listed_devices[name].set_title(label)
