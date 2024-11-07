# Copyright (c) 2024, Tomasz Pakuła Using Arch BTW

from boxflat.panels.settings_panel import SettingsPanel
from boxflat.widgets import *
from boxflat.hid_handler import MozaAxis, HidHandler
from math import ceil, floor

from gi.repository import Gtk, Adw

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
        estop_row.set_label("Enabled" if value else "Disabled")


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
        self._cm.subscribe("estop-get-status", self._estop_handler, self._current_row)
        self._cm.subscribe("estop-receive-status", self._estop_handler, self._current_row)
        self._cm.subscribe_connected("estop-get-status", self._current_row.set_active, 1)

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
        self._current_group.set_vexpand(True)

        self._add_row(BoxflatMinMaxLevelRow("Input", self._set_limit, "handbrake", max_value=65_534))
        self._hid_handler.subscribe(MozaAxis.HANDBRAKE.name, self._current_row.set_value)
        self._cm.subscribe_connected("handbrake-direction", self._current_group.set_active, 1)

        self.add_preferences_group()

        self._add_row(BoxflatAdvanceRow("About"))
        self._current_row.subscribe(self._show_about_dialog)
        self._current_row.set_width(0)

        self._current_group.set_margin_start(240)
        self._current_group.set_margin_end(240)


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


    def _show_about_dialog(self, *_):
        dialog = Adw.AboutDialog()

        dialog.set_application_name("Boxflat")
        dialog.set_application_icon("io.github.lawstorant.boxflat")

        dialog.set_version(self._version)
        dialog.set_developer_name("Tomasz Pakuła")
        dialog.set_copyright("© 2024 Using Arch BTW\nAll rights reserved")
        dialog.set_license_type(Gtk.License.GPL_3_0)

        dialog.set_issue_url(
            f"https://github.com/Lawstorant/boxflat/issues/new?assignees=lawstorant&labels=bug%2C+triage&projects=&template=bug_report.md&title=[{self._version}]"
        )

        dialog.set_website("https://github.com/Lawstorant/boxflat")
        dialog.add_link("FFB Driver", "https://github.com/JacKeTUs/universal-pidff")
        dialog.add_link(
            "Flatpak udev rule",
            "https://github.com/Lawstorant/boxflat?tab=readme-ov-file#udev-rule-installation-for-flatpak"
        )
        dialog.add_link(
            "Request a feature",
            "https://github.com/Lawstorant/boxflat/issues/new?assignees=lawstorant&labels=feature&projects=&template=feature_request.md"
        )

        dialog.set_comments("Moza Racing software suite")
        # dialog.set_debug_info("")

        dialog.present(self._content)
