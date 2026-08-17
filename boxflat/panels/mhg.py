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
    Its own command set is not decoded yet, so this panel reports identity
    only. See AB6_STATUS.md.
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

        self._add_row(BoxflatLevelRow("Mini-stick X", max_value=65535))
        self._hid_handler.subscribe(MozaAxis.RIGHT_PADDLE.name, self._current_row.set_value)

        self._add_row(BoxflatLevelRow("Mini-stick Y", max_value=65535))
        self._hid_handler.subscribe(MozaAxis.LEFT_PADDLE.name, self._current_row.set_value)

        self.add_preferences_group("Settings")
        self._add_row(BoxflatLabelRow(
            "Not available yet",
            "The grip's command set is still being mapped"))


    def _set_version(self, value: int, row: BoxflatLabelRow) -> None:
        row.set_label(format_version(value))
