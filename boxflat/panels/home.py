# Copyright (c) 2024, Tomasz Pakuła Using Arch BTW

from boxflat.panels.settings_panel import SettingsPanel
from boxflat.widgets import *
from boxflat.hid_handler import MozaAxis, HidHandler
from math import ceil, floor

class HomeSettings(SettingsPanel):
    def __init__(self, button_callback, dry_run: bool, connection_manager, hid_handler, version: str=""):
        self._test_text = "inactive"
        if dry_run:
            self._test_text = "active"

        self._version = version
        self._rotation = 180

        super().__init__("Home", button_callback, connection_manager=connection_manager, hid_handler=hid_handler)
        self._cm.subscribe("base-limit", self._get_rotation_limit)


    def _estop_handler(self, value: int, estop_row: BoxflatLabelRow) -> None:
        label = "Disabled"
        if value:
            label = "Enabled"
        estop_row.set_label(label)


    def prepare_ui(self):
        self.add_preferences_group("Wheelbase")
        self._cm.subscribe_connected("base-limit", self._current_group.set_active)

        self._steer_row = BoxflatLabelRow("Steering position")
        self._add_row(self._steer_row)
        self._steer_row.set_suffix("°")
        self._steer_row.set_subtitle(f"Limit = {self._rotation*2}°")
        self._hid_handler.subscribe(MozaAxis.STEERING.name, self._set_steering)
        self._current_row.set_value(0)

        self._add_row(BoxflatLabelRow("E-Stop status"))
        self._current_row.set_label("Disconnected")
        self._current_row.set_present(0)
        self._cm.subscribe("estop-get-status", self._estop_handler, self._current_row)
        self._cm.subscribe("estop-receive-status", self._estop_handler, self._current_row)
        self._cm.subscribe_connected("estop-get-status", self._current_row.set_present, 1)

        self._add_row(BoxflatButtonRow("Adjust center point", "Center"))
        self._current_row.subscribe(self._cm.set_setting, "base-calibration")


        self.add_preferences_group("Pedals")
        self._cm.subscribe_connected("pedals-throttle-dir", self._current_group.set_active, 1)

        self._add_row(BoxflatMinMaxLevelRow("Throttle input", self._set_limit, "pedals-throttle", max_value=65_534))
        self._hid_handler.subscribe(MozaAxis.THROTTLE.name, self._current_row.set_value)
        self._cm.subscribe_connected("pedals-throttle-dir", self._current_row.set_active, 1)

        self._add_row(BoxflatMinMaxLevelRow("Brake input", self._set_limit, "pedals-brake", max_value=65_534))
        self._hid_handler.subscribe(MozaAxis.BRAKE.name, self._current_row.set_value)
        self._cm.subscribe_connected("pedals-throttle-dir", self._current_row.set_active, 1)

        self._add_row(BoxflatMinMaxLevelRow("Clutch input", self._set_limit, "pedals-clutch", max_value=65_534))
        self._hid_handler.subscribe(MozaAxis.CLUTCH.name, self._current_row.set_value)
        self._cm.subscribe_connected("pedals-throttle-dir", self._current_row.set_active, 1)

        self.add_preferences_group("Handbrake")
        self._add_row(BoxflatMinMaxLevelRow("Input", self._set_limit, "handbrake", max_value=65_534))
        self._hid_handler.subscribe(MozaAxis.HANDBRAKE.name, self._current_row.set_value)
        self._cm.subscribe_connected("handbrake-direction", self._current_group.set_present, 1)
        self._current_group.set_present(False)


        self.add_preferences_group("About")
        self._add_row(BoxflatLabelRow("Version:", value=self._version))

        self._add_row(BoxflatButtonRow("Go to the project page", "GitHub", subtitle="Leave a star!"))
        self._current_row.subscribe(lambda value: self.open_url("https://github.com/Lawstorant/boxflat"))

        self._add_row(BoxflatButtonRow("Go to the universal-pidff driver page", "GitHub", subtitle="FFB Driver"))
        self._current_row.subscribe(lambda value: self.open_url("https://github.com/JacKeTUs/universal-pidff"))

        # self.add_preferences_group()
        # self._add_row(BoxflatRow(f"Test mode:  {self._test_text}"))


    def _get_rotation_limit(self, value: int):
        if value == self._rotation:
            return

        self._rotation = value
        self._steer_row.set_subtitle(f"Limit = {value*2}°")


    def _set_steering(self, value: int):
        self._steer_row.set_value(round((value - 32768) / 32768 * self._rotation))


    def _set_limit(self, fraction_method, command: str, min_max: str):
        fraction = fraction_method()

        current_raw_output = int(self._cm.get_setting(command + "-output")) / 65535 * 100
        new_limit = 0

        if min_max == "max":
            new_limit = floor(current_raw_output)
        else:
            new_limit = ceil(current_raw_output)

        # print(f"\nSetting {min_max}-limit for {command}")
        # print(f"Current raw output: {current_raw_output}")
        # print(f"New limit: {new_limit}")

        self._cm.set_setting(new_limit, f"{command}-{min_max}")
