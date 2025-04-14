# Copyright (c) 2025, Tomasz Pakuła Using Arch BTW

from .connection_manager import MozaConnectionManager
from .moza_command import MozaCommand
import yaml
import os
from threading import Thread
from .subscription import SimpleEventDispatcher
from time import sleep

MozaDevicePresetSettings = {
    "main" : [
        "set-interpolation"
    ],
    "base" : [
        "base-limit",
        "base-max-angle",
        "base-ffb-strength",
        "base-road-sensitivity",
        "base-speed",
        "base-spring",
        "base-damper",
        "base-torque",
        "base-inertia",
        "base-friction",
        "base-protection",
        "base-protection-mode",
        "base-natural-inertia",
        "base-speed-damping",
        "base-speed-damping-point",
        "base-soft-limit-stiffness",
        "base-soft-limit-strength",
        "base-soft-limit-retain",
        "base-equalizer1",
        "base-equalizer2",
        "base-equalizer3",
        "base-equalizer4",
        "base-equalizer5",
        "base-equalizer6",
        "base-ffb-curve-y1",
        "base-ffb-curve-y2",
        "base-ffb-curve-y3",
        "base-ffb-curve-y4",
        "base-ffb-curve-y5",
        "base-ffb-reverse"
    ],
    "dash" : [
        "dash-rpm-timings",
        "dash-rpm-indicator-mode",
        "dash-flags-indicator-mode",
        "dash-rpm-display-mode",
        "dash-rpm-interval",
        "dash-rpm-mode",
        "dash-rpm-value1",
        "dash-rpm-value2",
        "dash-rpm-value3",
        "dash-rpm-value4",
        "dash-rpm-value5",
        "dash-rpm-value6",
        "dash-rpm-value7",
        "dash-rpm-value8",
        "dash-rpm-value9",
        "dash-rpm-value10"
    ],
    "dash-colors" : [
        "dash-rpm-color1",
        "dash-rpm-color2",
        "dash-rpm-color3",
        "dash-rpm-color4",
        "dash-rpm-color5",
        "dash-rpm-color6",
        "dash-rpm-color7",
        "dash-rpm-color8",
        "dash-rpm-color9",
        "dash-rpm-color10",
        "dash-flag-color1",
        "dash-flag-color2",
        "dash-flag-color3",
        "dash-flag-color4",
        "dash-flag-color5",
        "dash-flag-color6",
        "dash-rpm-brightness",
        "dash-flags-brightness"
    ],
    "wheel" : [
        "wheel-rpm-timings",
        "wheel-paddles-mode",
        "wheel-rpm-indicator-mode",
        "wheel-stick-mode",
        "wheel-set-rpm-display-mode",
        "wheel-clutch-point",
        "wheel-knob-mode",
        "wheel-rpm-interval",
        "wheel-rpm-mode",
        "wheel-rpm-value1",
        "wheel-rpm-value2",
        "wheel-rpm-value3",
        "wheel-rpm-value4",
        "wheel-rpm-value5",
        "wheel-rpm-value6",
        "wheel-rpm-value7",
        "wheel-rpm-value8",
        "wheel-rpm-value9",
        "wheel-rpm-value10"
    ],
    "wheel-colors" : [
        # "wheel-rpm-blink-color1",
        # "wheel-rpm-blink-color2",
        # "wheel-rpm-blink-color3",
        # "wheel-rpm-blink-color4",
        # "wheel-rpm-blink-color5",
        # "wheel-rpm-blink-color6",
        # "wheel-rpm-blink-color7",
        # "wheel-rpm-blink-color8",
        # "wheel-rpm-blink-color9",
        # "wheel-rpm-blink-color10",
        "wheel-rpm-color1",
        "wheel-rpm-color2",
        "wheel-rpm-color3",
        "wheel-rpm-color4",
        "wheel-rpm-color5",
        "wheel-rpm-color6",
        "wheel-rpm-color7",
        "wheel-rpm-color8",
        "wheel-rpm-color9",
        "wheel-rpm-color10",
        "wheel-button-color1",
        "wheel-button-color2",
        "wheel-button-color3",
        "wheel-button-color4",
        "wheel-button-color5",
        "wheel-button-color6",
        "wheel-button-color7",
        "wheel-button-color8",
        "wheel-button-color9",
        "wheel-button-color10",
        "wheel-button-color11",
        "wheel-button-color12",
        "wheel-button-color13",
        "wheel-button-color14",
        "wheel-rpm-brightness",
        "wheel-buttons-brightness"
    ],
    "pedals" : [
        "pedals-throttle-dir",
        "pedals-throttle-min",
        "pedals-throttle-max",
        "pedals-throttle-y1",
        "pedals-throttle-y2",
        "pedals-throttle-y3",
        "pedals-throttle-y4",
        "pedals-throttle-y5",
        "pedals-brake-dir",
        "pedals-brake-angle-ratio",
        "pedals-brake-min",
        "pedals-brake-max",
        "pedals-brake-y1",
        "pedals-brake-y2",
        "pedals-brake-y3",
        "pedals-brake-y4",
        "pedals-brake-y5",
        "pedals-clutch-dir",
        "pedals-clutch-min",
        "pedals-clutch-max",
        "pedals-clutch-y1",
        "pedals-clutch-y2",
        "pedals-clutch-y3",
        "pedals-clutch-y4",
        "pedals-clutch-y5"
     ],
    "sequential" : [
        "sequential-direction",
        "sequential-paddle-sync",
        "sequential-brightness",
        "sequential-colors"
    ],
    "handbrake" : [
        "handbrake-direction",
        "handbrake-mode",
        "handbrake-button-threshold",
        "handbrake-min",
        "handbrake-max",
        "handbrake-y1",
        "handbrake-y2",
        "handbrake-y3",
        "handbrake-y4",
        "handbrake-y5"
    ]
}

class MozaPresetHandler(SimpleEventDispatcher):
    def __init__(self, connection_manager: MozaConnectionManager):
        super().__init__()
        self._settings = {}
        self._cm = connection_manager
        self._path = None
        self._name = None


    def set_path(self, preset_path: str):
        self._path = os.path.expanduser(preset_path)


    def set_name(self, name: str):
        if not name.endswith(".yml"):
            name += ".yml"

        self._name = name


    def append_setting(self, setting_name: str):
        device, name = setting_name.split("-", maxsplit=1)
        if device not in self._settings:
            self._settings[device] = []

        self._settings[device].append(name)


    def add_device_settings(self, device: str):
        if device not in MozaDevicePresetSettings:
            return

        for setting in MozaDevicePresetSettings[device]:
            self.append_setting(setting)


    # def remove_setting(self, setting_name: str):
    #     self._settings.remove(setting_name)


    def reset_settings(self):
        self._settings.clear()


    def save_preset(self):
        Thread(target=self._save_preset, daemon=True).start()


    def load_preset(self):
        Thread(target=self._load_preset, daemon=True).start()


    def _get_preset_data(self) -> dict:
        if not os.path.exists(self._path):
            return

        path = os.path.join(self._path, self._name)
        if not os.path.isfile(path):
            return

        with open(path, "r") as file:
            return yaml.safe_load(file.read())


    def _set_preset_data(self, preset_data: dict) -> None:
        if not os.path.exists(self._path):
            os.makedirs(self._path)

        with open(os.path.join(self._path, self._name), "w") as file:
            file.write(yaml.safe_dump(preset_data))


    def get_linked_process(self) -> str:
        data = self._get_preset_data()

        if data is None:
            return ""

        if not "linked-process" in data:
            return ""

        return data["linked-process"]


    def set_linked_process(self, process_name: str):
        data = self._get_preset_data()
        data["linked-process"] = process_name
        self._set_preset_data(data)


    def _save_preset(self):
        if not self._path:
            return

        preset_data = self._get_preset_data() or {}
        preset_data["BoxflatPresetVersion"] = "1"

        for device, settings in self._settings.items():
            if device not in preset_data.keys():
                preset_data[device] = {}

            for setting in settings:
                tries = 0
                while tries < 3:
                    tries += 1
                    replace = setting.replace("set-", "get-")
                    value = self._cm.get_setting(f"{device}-{replace}", exclusive=True)

                    if value == -1:
                        continue
                    preset_data[device][setting] = value
                    tries = 3

        process_name = self.get_linked_process()
        self._set_preset_data(preset_data)

        if process_name is not None:
            self.set_linked_process(process_name)

        self._dispatch()


    def _load_preset(self):
        if not self._path or not self._name:
            return

        preset_data = self._get_preset_data()
        if preset_data is None:
            return

        for key, settings in preset_data.items():
            if key not in MozaDevicePresetSettings.keys():
                continue

            for setting, value in settings.items():
                if setting == "indicator-mode":
                    setting = "rpm-indicator-mode"

                if key == "wheel" and setting.endswith("display-mode"):
                    setting = "set-rpm-display-mode"

                setting = setting.replace("get-", "set-").replace("-end", "-max").replace("-start", "-min")
                # print(f"{key}-{setting}: {value}")
                self._cm.set_setting(value, f"{key}-{setting}", exclusive=True)

        self._dispatch()


    def copy_preset(self, new_name: str) -> None:
        data = self._get_preset_data()

        tmp = self._name
        self.set_name(new_name)

        self._set_preset_data(data)
        self.set_name(tmp)
