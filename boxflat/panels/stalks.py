# Copyright (c) 2025, Tomasz Pakuła Using Arch BTW

from boxflat.panels.settings_panel import SettingsPanel
from boxflat.connection_manager import MozaConnectionManager
from boxflat.widgets import *
from boxflat.hid_handler import MozaHidDevice
from boxflat.settings_handler import SettingsHandler

class StalksSettings(SettingsPanel):
    def __init__(self, button_callback, connection_manager: MozaConnectionManager,
                 hid_handler, settings: SettingsHandler):

        self._settings = settings
        super().__init__("Multifunction Stalks", button_callback, connection_manager, hid_handler)

        self._cm.subscribe("hid-device-connected", self._parse_connected, 1)
        self._cm.subscribe("hid-device-disconnected", self._parse_connected, -1)


    def _parse_connected(self, name: str, connected: bool) -> None:
        if name != MozaHidDevice.STALKS:
            return

        self.active(connected)


    def prepare_ui(self):
        self.add_preferences_group("Stalks settings")
        self._add_row(BoxflatSwitchRow("Legacy Compatibility Mode", "Use your stalks with games that lack cancel binding"))
        self._current_row.set_value(self._settings.read_setting("stalks-legacy-mode") or 0, mute=False)
        self._current_row.subscribe(self._settings.write_setting, "stalks-legacy-mode")
