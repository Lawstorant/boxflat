# Copyright (c) 2025, Tomasz Pakuła Using Arch BTW

from boxflat.panels.settings_panel import SettingsPanel
from boxflat.connection_manager import MozaConnectionManager
from boxflat.widgets import *
from boxflat.hid_handler import MozaHidDevice

class StalksSettings(SettingsPanel):
    def __init__(self, button_callback, connection_manager: MozaConnectionManager, hid_handler):
        super().__init__("Multifunction Stalks", button_callback, connection_manager, hid_handler)
        self._cm.subscribe("device-connected", self._parse_connected, 1)
        self._cm.subscribe("device-disconnected", self._parse_connected, 0)


    def _parse_connected(self, name: str, connected: bool):
        if name != MozaHidDevice.STALKS:
            return

        self.active(connected)


    def prepare_ui(self):
        self.add_preferences_group("Stalks settings")
        self._add_row(BoxflatToggleButtonRow("Mode"))
        self._current_row.add_buttons("ETS2/ATS", "Direct")

        self._add_row(BoxflatSwitchRow("Legacy Compatibility Mode", "Use your stalks with games that lack cancel binding"))

