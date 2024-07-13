from boxflat.panels.settings_panel import SettingsPanel
from boxflat.connection_manager import MozaConnectionManager
from boxflat.widgets import *

class SequentialSettings(SettingsPanel):
    def __init__(self, button_callback: callable, connection_manager: MozaConnectionManager):
        self._S1 = None
        self._S2 = None
        super().__init__("Sequential Shifter", button_callback, connection_manager)

    def prepare_ui(self) -> None:
        self.add_preferences_group("Shifter Settings")
        self._add_row(BoxflatSwitchRow("Reverse Shift Direction", subtitle="Why would you do that?"))
        self._current_row.subscribe(lambda v: self._cm.set_setting("sequential-direction", v))
        self._cm.subscribe("sequential-direction", self._current_row.set_value)

        self._add_row(BoxflatSwitchRow("Paddle Shifter Synchronization", subtitle="Why would you do that?"))
        self._current_row.set_expression("+1")
        self._current_row.set_reverse_expression("-1")
        self._current_row.subscribe(lambda v: self._cm.set_setting("sequential-paddle-sync", v))
        self._cm.subscribe("sequential-paddle-sync", self._current_row.set_value)

        self._add_row(BoxflatSliderRow("Button Brightness", 0, 10))
        self._current_row.add_marks(5);
        self._current_row.subscribe(lambda v: self._cm.set_setting("sequential-brightness", v))
        self._cm.subscribe("sequential-brightness", self._current_row.set_value)

        self._S1 = BoxflatColorPickerRow("S1 Color")
        self._add_row(self._S1)

        self._S2 = BoxflatColorPickerRow("S2 Color")
        self._add_row(self._S2)

        self._S1.set_reverse_expression("/256")
        self._S2.set_reverse_expression("%256")

        self._S1.subscribe(lambda v: self._cm.set_setting("sequential-colors", byte_value=bytes([self._S1.get_value(), self._S2.get_value()])))
        self._S2.subscribe(lambda v: self._cm.set_setting("sequential-colors", byte_value=bytes([self._S1.get_value(), self._S2.get_value()])))

        self._cm.subscribe("sequential-colors", self._S1.set_value)
        self._cm.subscribe("sequential-colors", self._S2.set_value)
