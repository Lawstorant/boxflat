# Copyright (c) 2026, Boxflat contributors

from boxflat.panels.settings_panel import SettingsPanel
from boxflat.connection_manager import MozaConnectionManager
from boxflat.hid_handler import MozaAxis
from boxflat.widgets import *


def format_version(value: int) -> str:
    """Render a packed version int as a four-part version.

    Group 4 ignores the command id, so the whole payload is version data:
    the base answers 0x01010604 and the grip 0x01010b01, which read as
    1.1.6.4 and 1.1.11.1.
    """
    if value is None or value < 0:
        return "Unknown"

    return ".".join(str(byte) for byte in value.to_bytes(4, "big"))


class AB6Settings(SettingsPanel):
    """Flight base panel.

    Deliberately limited to what the hardware has actually been observed to
    answer. The AB6 does not implement the racing command set, and the
    meaning of its own settings group is not decoded yet, so this panel
    reports identity and live axis state rather than pretending to offer
    settings it cannot write. See AB6_STATUS.md.
    """

    def __init__(self, button_callback, connection_manager: MozaConnectionManager, hid_handler):
        super().__init__("AB6 Base", button_callback, connection_manager, hid_handler)
        self._cm.subscribe_connected("ab6-version", self.active)


    def prepare_ui(self):
        self.add_preferences_group("Device")

        self._add_row(BoxflatLabelRow("Firmware version"))
        self._current_row.set_label("Unknown")
        self._cm.subscribe("ab6-version", self._set_version, self._current_row)

        self._add_row(BoxflatLabelRow("Protocol version"))
        self._current_row.set_label("Unknown")
        self._cm.subscribe("ab6-protocol-version", self._set_version, self._current_row)

        self.add_preferences_group("Stick", alt_level_bar=True)
        self._current_group.set_bar_max(65535)
        self._hid_handler.subscribe(MozaAxis.STEERING.name, self._current_group.set_alt_bar_level)

        self._add_row(BoxflatLabelRow(
            "Settings",
            "Not available yet — the AB6 uses its own command set, which is "
            "still being mapped"))


    def _set_version(self, value: int, row: BoxflatLabelRow) -> None:
        row.set_label(format_version(value))
