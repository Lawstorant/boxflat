from boxflat.panels.settings_panel import SettingsPanel
from boxflat.widgets import *

from boxflat.hid_handler import MozaAxis, HidHandler

class HomeSettings(SettingsPanel):
    def __init__(self, button_callback, dry_run: bool, connection_manager, hid_handler, version: str="") -> None:
        self._test_text = "inactive"
        if dry_run:
            self._test_text = "active"

        self._version = version
        self._rotation = 180

        super().__init__("Home", button_callback, connection_manager=connection_manager, hid_handler=hid_handler)
        self._append_sub("base-limit", self._get_rotation_limit)


    def prepare_ui(self) -> None:
        self.add_preferences_group("Wheelbase")
        self._append_sub_connected("base-limit", self._current_group.set_active)

        self._steer_row = BoxflatLabelRow("Steering position")
        self._add_row(self._steer_row)
        self._steer_row.set_suffix("°")
        self._steer_row.set_subtitle(f"Limit = {self._rotation*2}°")
        self._append_sub_hid(MozaAxis.STEERING, self._set_steering)

        self._add_row(BoxflatButtonRow("Adjust center point", "Center"))
        self._current_row.subscribe(self._cm.set_setting_int, "base-calibration")


        self.add_preferences_group("Pedals")
        self._append_sub_connected("pedals-throttle-dir", self._current_group.set_active, 1)

        self._add_row(BoxflatMinMaxLevelRow("Throttle input", self._set_limit, "pedals-throttle", max_value=65534))
        self._append_sub_hid(MozaAxis.THROTTLE, self._current_row.set_value)
        self._append_sub_connected("pedals-throttle-dir", self._current_row.set_active, 1)

        self._add_row(BoxflatMinMaxLevelRow("Brake input", self._set_limit, "pedals-brake", max_value=65534))
        self._append_sub_hid(MozaAxis.BRAKE, self._current_row.set_value)
        self._append_sub_connected("pedals-throttle-dir", self._current_row.set_active, 1)

        self._add_row(BoxflatMinMaxLevelRow("Clutch input", self._set_limit, "pedals-clutch", max_value=65534))
        self._append_sub_hid(MozaAxis.CLUTCH, self._current_row.set_value)
        self._append_sub_connected("pedals-throttle-dir", self._current_row.set_active, 1)

        self.add_preferences_group("Handbrake")
        self._add_row(BoxflatMinMaxLevelRow("Input", self._set_limit, "handbrake", max_value=65534))
        self._append_sub_hid(MozaAxis.HANDBRAKE, self._current_row.set_value)
        self._append_sub_connected("handbrake-direction", self._current_group.set_present, 1)


        self.add_preferences_group("About")
        self._add_row(BoxflatLabelRow("Version:", value=self._version))

        self._add_row(BoxflatButtonRow("Go to the project page", "GitHub", subtitle="Leave a star!"))
        self._current_row.subscribe(lambda value: self.open_url("https://github.com/Lawstorant/boxflat"))

        self._add_row(BoxflatButtonRow("Go to the universal-pidff driver page", "GitHub", subtitle="FFB Driver"))
        self._current_row.subscribe(lambda value: self.open_url("https://github.com/JacKeTUs/universal-pidff"))

        # self.add_preferences_group()
        # self._add_row(BoxflatRow(f"Test mode:  {self._test_text}"))


    def _get_rotation_limit(self, value: int) -> None:
        if value == self._rotation:
            return

        self._rotation = value
        self._steer_row.set_subtitle(f"Limit = {value*2}°")


    def _set_steering(self, value: int) -> None:
        self._steer_row.set_value(round((value - 32768) / 32768 * self._rotation))


    def _set_limit(self, percent_func: callable, command: str):
        # print(f"{command}: {percent_func()}")
        self._cm.set_setting_int(percent_func(), command)
