from boxflat.panels.settings_panel import SettingsPanel
from boxflat.connection_manager import MozaConnectionManager
from boxflat.widgets import *

class SequentialSettings(SettingsPanel):
    def __init__(self, button_callback: callable, connection_manager: MozaConnectionManager):
        self._S1 = None
        self._S2 = None
        super().__init__("Sequential Shifter", button_callback, connection_manager)
        self._append_sub_connected("sequential-paddle-sync", self.active)


    def active(self, value: int) -> None:
        value = -1 if value < 1 else value
        super().active(value)


    def prepare_ui(self) -> None:
        self.add_preferences_group("Shifter Settings")
        self._add_row(BoxflatSwitchRow("Reverse Shift Direction"))
        self._current_row.subscribe(self._cm.set_setting_auto, "sequential-direction")
        self._append_sub("sequential-direction", self._current_row.set_value)

        self._add_row(BoxflatSwitchRow("Paddle Shifter Synchronization", subtitle="Use the same buttons as paddle shifters"))
        self._current_row.set_expression("+1")
        self._current_row.set_reverse_expression("-1")
        self._current_row.subscribe(self._cm.set_setting_auto, "sequential-paddle-sync")
        self._append_sub("sequential-paddle-sync", self._current_row.set_value)

        self.add_preferences_group("Buttons")
        self._add_row(BoxflatSliderRow("Button Brightness", 0, 10))
        self._current_row.add_marks(5)
        self._current_row.set_slider_width(290)
        self._current_row.subscribe(self._cm.set_setting_auto, "sequential-brightness")
        self._append_sub("sequential-brightness", self._current_row.set_value)

        self._S1 = BoxflatColorPickerRow("S1 Color")
        self._add_row(self._S1)

        self._S2 = BoxflatColorPickerRow("S2 Color")
        self._add_row(self._S2)

        self._S1.subscribe(self._set_colors)
        self._S2.subscribe(self._set_colors)
        self._append_sub("sequential-colors", self._get_colors)


    def _set_colors(self, *args) -> None:
        self._cm.set_setting_auto([self._S1.get_value(), self._S2.get_value()], "sequential-colors")


    def _get_colors(self, value: list) -> None:
        self._S1.set_value(int(value[0]))
        self._S2.set_value(int(value[1]))
