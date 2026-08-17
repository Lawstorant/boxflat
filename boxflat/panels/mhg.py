# Copyright (c) 2026, Boxflat contributors

from boxflat.panels.settings_panel import SettingsPanel
from boxflat.panels.ab6 import format_version
from boxflat.connection_manager import MozaConnectionManager
from boxflat.hid_handler import MozaAxis
from boxflat.widgets import *


class MHGSettings(SettingsPanel):
    """MHG flight grip.

    The grip is a separate addressable device that answers through the AB6
    base's serial port, the same way a wheel answers through a wheelbase.
    It has its own command set, addressed on group 50 (read) / 51 (write)
    rather than the AB6 base's 30/31 - confirmed for its two lighting
    zones so far. See AB6_STATUS.md.
    """

    def __init__(self, button_callback, connection_manager: MozaConnectionManager, hid_handler):
        super().__init__("MHG Grip", button_callback, connection_manager, hid_handler)
        self._cm.subscribe_connected("mhg-version", self.active)


    def prepare_ui(self):
        self.add_preferences_group("Device")

        self._add_row(BoxflatLabelRow("Firmware version"))
        self._current_row.set_label("Unknown")
        self._cm.subscribe("mhg-version", self._set_version, self._current_row)

        # The firmware's diagnostic log attributes axis_z, thumb_x and thumb_y
        # to the stick device, so these axes are listed here rather than on the
        # base. Assignments confirmed with tools/ab6_axes.py; the names come
        # from boxflat's shared racing map and are relabelled for what the
        # control actually is.
        self.add_preferences_group("Grip axes")

        self._add_row(BoxflatLevelRow("Yaw (twist)", max_value=65535))
        self._hid_handler.subscribe(MozaAxis.BRAKE.name, self._current_row.set_value)

        self._add_row(BoxflatLevelRow("Mini-stick / hat X", max_value=65535))
        self._hid_handler.subscribe(MozaAxis.RIGHT_PADDLE.name, self._current_row.set_value)

        self._add_row(BoxflatLevelRow("Mini-stick / hat Y", max_value=65535))
        self._hid_handler.subscribe(MozaAxis.LEFT_PADDLE.name, self._current_row.set_value)

        # Confirmed against real hardware from the MHG Basic Settings page
        # capture - see data/serial.yml. Cogging Torque Calibration, the
        # Yaw axis toggle/calibration, the grip Mode 1/Mode 2 mapping
        # dropdowns, Axis Calibration and Mapping Range weren't confidently
        # attributed and are left out.
        self.add_preferences_group("Status Light")

        self._add_row(BoxflatSliderRow("Brightness", range_end=15))
        self._current_row.subscribe(self._cm.set_setting, "mhg-status-light-brightness")
        self._cm.subscribe("mhg-status-light-brightness", self._current_row.set_value)

        self._status_light_row = BoxflatNewColorPickerRow("Color", pickers=1)
        self._add_row(self._status_light_row)
        self._current_row.subscribe("color0", self._set_status_light_color)
        self._cm.subscribe("mhg-status-light-color", self._set_status_light_color_row)

        self.add_preferences_group("Button Light")

        self._add_row(BoxflatSliderRow("Brightness", range_end=15))
        self._current_row.subscribe(self._cm.set_setting, "mhg-button-light-brightness")
        self._cm.subscribe("mhg-button-light-brightness", self._current_row.set_value)

        self._button_light_row = BoxflatNewColorPickerRow("Color", pickers=1)
        self._add_row(self._button_light_row)
        self._current_row.subscribe("color0", self._set_button_light_color)
        self._cm.subscribe("mhg-button-light-color", self._set_button_light_color_row)


    def _set_version(self, value: int, row: BoxflatLabelRow) -> None:
        row.set_label(format_version(value))


    def _set_status_light_color(self, value: list) -> None:
        self._cm.set_setting(value, "mhg-status-light-color")


    def _set_status_light_color_row(self, value: list) -> None:
        if not isinstance(value, list) or len(value) != 3:
            return
        self._status_light_row.set_led_value(value, 0)


    def _set_button_light_color(self, value: list) -> None:
        self._cm.set_setting(value, "mhg-button-light-color")


    def _set_button_light_color_row(self, value: list) -> None:
        if not isinstance(value, list) or len(value) != 3:
            return
        self._button_light_row.set_led_value(value, 0)
