# Copyright (c) 2025, Tomasz Pakuła Using Arch BTW

from boxflat.panels.settings_panel import SettingsPanel
from boxflat.connection_manager import MozaConnectionManager
from boxflat.widgets import *
from boxflat.hid_handler import MozaHidDevice
from boxflat.settings_handler import SettingsHandler

class StalksSettings(SettingsPanel):
    def __init__(self, button_callback, connection_manager: MozaConnectionManager,
                 hid_handler, settings: SettingsHandler):

        self._turn_toggle  = None
        self._turn_hold    = None
        self._headlights   = None
        self._wipers       = None
        self._wpiers_alt   = None
        self._wipers_quick = None
        self._skip         = None
        self._ignition     = None

        self._settings = settings
        super().__init__("Multifunction Stalks", button_callback, connection_manager, hid_handler)

        self._cm.subscribe("hid-device-connected", self._parse_connected, 1)
        self._cm.subscribe("hid-device-disconnected", self._parse_connected, -1)


    def _parse_connected(self, name: str, connected: bool) -> None:
        if name != MozaHidDevice.STALKS:
            return

        self.active(connected)


    def _add_row(self, row: BoxflatRow) -> None:
        super()._add_row(row)
        row.disable_cooldown()


    def prepare_ui(self):
        self.add_preferences_group("Compatibility modes")

        self._add_row(BoxflatSwitchRow("Turn Signals toggle", "Press button again when canceling"))
        self._current_row.subscribe(self._settings.write_setting, "stalks-turnsignal-compat")
        self._current_row.subscribe(self._hid_handler.stalks_turnsignal_compat_active)
        self._current_row.set_value(self._settings.read_setting("stalks-turnsignal-compat") or 0, mute=False)
        self._turn_toggle = self._current_row


        self._add_row(BoxflatSwitchRow("Turn Signals hold", "Hold button as long as signal is active"))
        self._current_row.subscribe(self._settings.write_setting, "stalks-turnsignal-compat-constant")
        self._current_row.subscribe(self._hid_handler.stalks_turnsignal_compat_constant_active)
        self._current_row.set_value(self._settings.read_setting("stalks-turnsignal-compat-constant") or 0, mute=False)
        self._turn_hold = self._current_row

        self.add_preferences_group()
        compat = self._settings.read_setting("stalks-headlights-compat") or 0
        self._add_row(BoxflatSwitchRow("Headlights", "Cycling instead of discrete buttons"))
        self._current_row.subscribe(self._settings.write_setting, "stalks-headlights-compat")
        self._current_row.subscribe(self._hid_handler.stalks_headlights_compat_active)
        self._current_row.set_value(compat, mute=False)
        self._headlights = self._current_row

        positional = self._settings.read_setting("stalks-skip-positional") or 0
        self._add_row(BoxflatSwitchRow("Skip positional", "For games that only have on/off headlights"))
        self._current_row.set_active(compat)
        self._current_row.set_value(positional)
        self._current_row.subscribe(self._settings.write_setting, "stalks-skip-positional")
        self._current_row.subscribe(self._hid_handler.stalks_headlights_skip_pos_active)
        self._skip = self._current_row
        self._headlights.subscribe(self._skip.set_active)
        self._hid_handler.stalks_headlights_skip_pos_active(positional)


        self._wipers1 = BoxflatSwitchRow("Wipers", "Cycling instead of discrete buttons")
        self._wipers2 = BoxflatSwitchRow("Wipers alternative", "Up/Down instead of discrete buttons")

        self.add_preferences_group()
        self._add_row(self._wipers1)
        self._current_row.subscribe(self._settings.write_setting, "stalks-wipers-compat")
        self._current_row.subscribe(self._hid_handler.stalks_wipers_compat_active)
        self._current_row.subscribe(lambda v: self._wipers2.set_value_directly(0) if v == 1 else ...)
        self._current_row.subscribe(self._handle_quick_wipe)
        self._current_row.set_value(self._settings.read_setting("stalks-wipers-compat") or 0, mute=False)
        self._wipers = self._current_row

        self._add_row(self._wipers2)
        self._current_row.subscribe(self._settings.write_setting, "stalks-wipers-compat2")
        self._current_row.subscribe(self._hid_handler.stalks_wipers_compat2_active)
        self._current_row.subscribe(lambda v: self._wipers1.set_value_directly(0) if v == 1 else ...)
        self._current_row.subscribe(self._handle_quick_wipe)
        self._current_row.set_value(self._settings.read_setting("stalks-wipers-compat2") or 0, mute=False)
        self._wpiers_alt = self._current_row

        quick = self._settings.read_setting("stalks-wipers-quick") or 0
        self._quick_wipe = BoxflatSwitchRow("Quick wipe emulation", "One and done")
        self._add_row(self._quick_wipe)
        self._current_row.set_active(0)
        self._current_row.subscribe(self._settings.write_setting, "stalks-wipers-quick")
        self._current_row.subscribe(self._hid_handler.stalks_wipers_quick_active)
        self._current_row.set_value(quick)
        self._wipers_quick = self._current_row
        self._hid_handler.stalks_wipers_quick_active(quick)

        self.add_preferences_group()
        ignition = self._settings.read_setting("stalks-ignition") or 0
        self._add_row(BoxflatSwitchRow("Rear wiper as ignition", "Pretty immersive"))
        self._ignition = self._current_row
        self._current_row.set_value(ignition)
        self._current_row.subscribe(self._settings.write_setting, "stalks-ignition")
        self._current_row.subscribe(self._hid_handler.stalks_ignition_active)
        self._hid_handler.stalks_ignition_active(ignition)


        self.add_preferences_group()
        self._add_row(BoxflatButtonRow("Restore default settings", "Reset"))
        self._current_row.subscribe(self.reset)


    def _handle_quick_wipe(self, *_) -> None:
        row1 = self._wipers1.get_value()
        row2 = self._wipers2.get_value()

        if row1 or row2:
            self._quick_wipe.set_active(1)
            return

        self._quick_wipe.set_active(0)


    def get_settings(self) -> map:
        return {
            "turn-signal-toggle" : self._turn_toggle.get_value(),
            "turn-signal-hold"   : self._turn_hold.get_value(),
            "headlights"         : self._headlights.get_value(),
            "skip-positional"    : self._skip.get_value(),
            "wipers"             : self._wipers.get_value(),
            "wipers-alt"         : self._wpiers_alt.get_value(),
            "wipers-quick"       : self._wipers_quick.get_value(),
            "ignition"           : self._ignition.get_value(),
        }


    def set_settings(self, settings: map) -> None:
        self._turn_toggle.set_value(settings["turn-signal-toggle"], mute=False)
        self._turn_hold.set_value(settings["turn-signal-hold"], mute=False)
        self._headlights.set_value(settings["headlights"], mute=False)
        self._wipers.set_value(settings["wipers"], mute=False)
        self._wpiers_alt.set_value(settings["wipers-alt"], mute=False)
        self._wipers_quick.set_value(settings["wipers-quick"], mute=False)

        if "skip-positional" in settings:
            self._skip.set_value(settings["skip-positional"], mute=False)

        if "ignition" in settings:
            self._ignition.set_value(settings["ignition"], mute=False)


    def reset(self, *_) -> None:
        self._turn_toggle.set_value(0, mute=False)
        self._turn_hold.set_value(0, mute=False)
        self._headlights.set_value(0, mute=False)
        self._wipers.set_value(0, mute=False)
        self._wpiers_alt.set_value(0, mute=False)
        self._wipers_quick.set_value(0, mute=False)
        self._ignition.set_value(0, mute=False)
