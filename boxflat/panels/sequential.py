# Copyright (c) 2025, Tomasz Pakuła Using Arch BTW

from boxflat.panels.settings_panel import SettingsPanel
from boxflat.connection_manager import MozaConnectionManager
from boxflat.hid_handler import HidHandler
from boxflat.widgets import *

class SequentialSettings(SettingsPanel):
    def __init__(self, button_callback, connection_manager: MozaConnectionManager, hid: HidHandler):
        self._S1 = None
        self._S2 = None
        super().__init__("Sequential Shifter", button_callback, connection_manager, hid)
        self._cm.subscribe_connected("sequential-output-y", self.active)


    def prepare_ui(self):
        self.add_preferences_group("Shift Settings")
        self._add_row(BoxflatSwitchRow("Reverse Shift Direction"))
        self._current_row.subscribe(self._cm.set_setting, "sequential-direction")
        self._cm.subscribe("sequential-direction", self._filter_data, self._current_row)

        self._add_row(BoxflatSwitchRow("Paddle Shifter Synchronization", subtitle="Use the same buttons as paddle shifters. Works with USB now!"))
        self._current_row.set_expression("+1")
        self._current_row.set_reverse_expression("-1")
        self._current_row.subscribe(self._cm.set_setting, "sequential-paddle-sync")
        self._cm.subscribe("sequential-paddle-sync", self._filter_data, self._current_row)
        self._cm.subscribe("sequential-paddle-sync", lambda v: self._hid_handler.paddle_sync_enabled(v-1))

        self.add_preferences_group("Lights")
        self._add_row(BoxflatSliderRow("Buttons Brightness", 0, 10))
        self._current_row.add_marks(5)
        self._current_row.set_slider_width(294)
        self._current_row.subscribe(self._cm.set_setting, "sequential-brightness")
        self._cm.subscribe("sequential-brightness", self._filter_data, self._current_row)

        self._S1 = BoxflatColorPickerRow("S1 Color")
        self._add_row(self._S1)

        self._S2 = BoxflatColorPickerRow("S2 Color")
        self._add_row(self._S2)

        self._S1.subscribe(self._set_colors)
        self._S2.subscribe(self._set_colors)
        self._cm.subscribe("sequential-colors", self._get_colors)


    def _set_colors(self, *args):
        self._cm.set_setting([self._S1.get_value(), self._S2.get_value()], "sequential-colors")


    def _get_colors(self, value: list):
        if not self._active:
            return

        self._S1.set_value(int(value[0]))
        self._S2.set_value(int(value[1]))


    def _filter_data(self, value, row: BoxflatRow):
        if not self._active:
            return
        row.set_value(value)
