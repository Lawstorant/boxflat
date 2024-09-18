from .connection_manager import MozaConnectionManager
from .moza_command import MozaCommand
import yaml
import os
from threading import Thread

MozaDevicePresetSettings = {
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
    "wheel" : [
        "wheel-rpm-timings",
        "wheel-paddles-mode",
        "wheel-indicator-mode",
        "wheel-stick-mode",
        "wheel-set-display-mode",
        "wheel-clutch-point",
        "wheel-knob-mode",
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
        "wheel-rpm-brightness",
        "wheel-buttons-brightness",
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
    "handbrake" : [
        "handbrake-direction",
        "handbrake-mode",
        "handbrake-button-threshold",
        "handbrake-range-start",
        "handbrake-range-end",
        "handbrake-y1",
        "handbrake-y2",
        "handbrake-y3",
        "handbrake-y4",
        "handbrake-y5"
    ]
}

class MozaPresetHandler():
    def __init__(self, connection_manager: MozaConnectionManager):
        self._settings = {}
        self._cm = connection_manager
        self._path = None
        self._name = None
        self._callbacks = []


    def set_path(self, preset_path: str):
        self._path = preset_path


    def set_name(self, name: str):
        self._name = name


    def add_callback(self, callback: callable):
        self._callbacks.append(callback)


    def append_setting(self, setting_name: str):
        command = MozaCommand(setting_name, self._cm.get_command_data())
        if command.device_type not in self._settings:
            self._settings[command.device_type] = []

        self._settings[command.device_type].append(command.name)


    def add_device_settings(self, device: str):
        if device in MozaDevicePresetSettings:
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


    def _save_preset(self):
        if not self._path:
            return

        preset_data = {}
        preset_data["BoxflatPresetVersion"] = "1"

        for device, settings in self._settings.items():
            preset_data[device] = {}
            for setting in settings:
                if "-set-" in setting:
                    setting = setting.replace("-set-", "-get-")


                tries = 0
                while tries < 3:
                    tries += 1
                    value = self._cm.get_setting_auto(f"{device}-{setting}")
                    if value != -1:
                        preset_data[device][setting] = value
                        tries = 3

        path = os.path.expanduser(self._path)

        if not os.path.exists(path):
            os.makedirs(path)

        with open(os.path.join(path, self._name + ".yml"), "w") as file:
            file.write(yaml.safe_dump(preset_data))

        for callback in self._callbacks:
            callback()


    def _load_preset(self):
        if not self._path or not self._name:
            return

        preset_data = None

        with open(os.path.join(self._path, self._name), "r") as file:
            preset_data = yaml.safe_load(file.read())

        for key, settings in preset_data.items():
            if key in MozaDevicePresetSettings.keys():
                for setting, value in settings.items():
                    # print(f"{key}-{setting}: {value}")
                    self._cm.set_setting_auto(value, f"{key}-{setting}")

        for callback in self._callbacks:
            callback()
