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
        self.add_preferences_group("Compatibility modes")

        self._add_row(BoxflatSwitchRow("Turn Signals toggle", "Press button again when canceling"))
        self._current_row.subscribe(self._settings.write_setting, "stalks-turnsignal-compat")
        self._current_row.subscribe(self._hid_handler.stalks_turnsignal_compat_active)
        self._current_row.set_value(self._settings.read_setting("stalks-turnsignal-compat") or 0, mute=False)

        self._add_row(BoxflatSwitchRow("Turn Signals hold", "Hold button as long as signal is active"))
        self._current_row.subscribe(self._settings.write_setting, "stalks-turnsignal-compat-constant")
        self._current_row.subscribe(self._hid_handler.stalks_turnsignal_compat_constant_active)
        self._current_row.set_value(self._settings.read_setting("stalks-turnsignal-compat-constant") or 0, mute=False)

        self.add_preferences_group()
        self._add_row(BoxflatSwitchRow("Headlights", "Cycling instead of discrete buttons"))
        self._current_row.subscribe(self._settings.write_setting, "stalks-headlights-compat")
        self._current_row.subscribe(self._hid_handler.stalks_headlights_compat_active)
        self._current_row.set_value(self._settings.read_setting("stalks-headlights-compat") or 0, mute=False)

        self._wipers1 = BoxflatSwitchRow("Wipers", "Cycling instead of discrete buttons")
        self._wipers2 = BoxflatSwitchRow("Wipers alternative", "Up/Down instead of discrete buttons")

        self.add_preferences_group()
        self._add_row(self._wipers1)
        self._current_row.subscribe(self._settings.write_setting, "stalks-wipers-compat")
        self._current_row.subscribe(self._hid_handler.stalks_wipers_compat_active)
        self._current_row.subscribe(lambda v: self._wipers2.set_value_directly(0) if v == 1 else ...)
        self._current_row.subscribe(self._handle_quick_wipe)
        self._current_row.set_value(self._settings.read_setting("stalks-wipers-compat") or 0, mute=False)

        self._add_row(self._wipers2)
        self._current_row.subscribe(self._settings.write_setting, "stalks-wipers-compat2")
        self._current_row.subscribe(self._hid_handler.stalks_wipers_compat2_active)
        self._current_row.subscribe(lambda v: self._wipers1.set_value_directly(0) if v == 1 else ...)
        self._current_row.subscribe(self._handle_quick_wipe)
        self._current_row.set_value(self._settings.read_setting("stalks-wipers-compat2") or 0, mute=False)

        self._quick_wipe = BoxflatSwitchRow("Quick wipe emulation", "One and done")
        self._add_row(self._quick_wipe)
        self._current_row.set_active(0)
        self._current_row.subscribe(self._settings.write_setting, "stalks-wipers-quick")
        self._current_row.subscribe(self._hid_handler.stalks_wipers_quick_active)
        self._current_row.set_value(self._settings.read_setting("stalks-wipers-quick") or 0, mute=False)


    def _handle_quick_wipe(self, *_) -> None:
        row1 = self._wipers1.get_value()
        row2 = self._wipers2.get_value()

        if row1 or row2:
            self._quick_wipe.set_active(1)
            return

        self._quick_wipe.set_active(0)
