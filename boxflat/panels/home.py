from boxflat.panels.settings_panel import SettingsPanel
from boxflat.widgets import *

from boxflat.hid_handler import MozaAxis, MozaHidDevice

class HomeSettings(SettingsPanel):
    def __init__(self, button_callback, dry_run: bool, version: str="", connection_manager=None) -> None:
        self._test_text = "inactive"
        if dry_run:
            self._test_text = "active"

        self._version = version

        super().__init__("Home", button_callback, connection_manager=connection_manager)
        self._device_pattern = MozaHidDevice.BASE
        self._rotation = 180
        self._append_sub("base-limit", self._get_rotation_limit)


    def prepare_ui(self) -> None:
        self.add_preferences_group("Wheelbase")
        self._append_sub_connected("base-limit", self._current_group.set_active)

        self._steer_row = BoxflatLabelRow("Steering position")
        self._add_row(self._steer_row)
        self._steer_row.set_suffix("°")
        self._append_sub_hid(MozaAxis.STEERING, self._set_steering)
        self._steer_row.set_value(0)

        self._add_row(BoxflatButtonRow("Adjust center point", "Center"))
        self._current_row.subscribe(self._cm.set_setting_int, "base-calibration")


        self.add_preferences_group("Pedals")
        self._append_sub_connected("pedals-throttle-dir", self._current_group.set_active, 1)

        self._add_row(BoxflatLevelRow("Throttle input", max_value=65535))
        self._current_row.set_reverse_expression("+32768")
        self._append_sub_hid(MozaAxis.THROTTLE, self._current_row.set_value)

        self._add_row(BoxflatLevelRow("Brake input", max_value=65535))
        self._current_row.set_reverse_expression("+32768")
        self._append_sub_hid(MozaAxis.BRAKE, self._current_row.set_value)

        self._add_row(BoxflatLevelRow("Clutch input", max_value=65535))
        self._current_row.set_reverse_expression("+32768")
        self._append_sub_hid(MozaAxis.CLUTCH, self._current_row.set_value)

        self.add_preferences_group("About")
        self._add_row(BoxflatLabelRow("Version:", value=self._version))


        # old stuff
        # self.add_preferences_group()
        # self._add_row(BoxflatRow("Welcome to Boxflat", subtitle=f"Version: {self._version}"))

        # self.add_preferences_group()
        # self._add_row(BoxflatButtonRow("Go to the project page", "GitHub", subtitle="Leave a star!"))
        # self._current_row.subscribe(lambda value: self.open_url("https://github.com/Lawstorant/boxflat"))

        # self._add_row(BoxflatButtonRow("Go to the universal-pidff driver page", "GitHub", subtitle="FFB Driver"))
        # self._current_row.subscribe(lambda value: self.open_url("https://github.com/JacKeTUs/universal-pidff"))

        # self.add_preferences_group()
        # self._add_row(BoxflatRow(f"Test mode:  {self._test_text}"))


    def _get_rotation_limit(self, value: int) -> None:
        self._rotation = value


    def _set_steering(self, value: int) -> None:
        self._steer_row.set_value(round((value - 32768) / 32768 * self._rotation))


