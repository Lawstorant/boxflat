from boxflat.panels.settings_panel import SettingsPanel
from boxflat.connection_manager import MozaConnectionManager
from boxflat.widgets import *

class SequentialSettings(SettingsPanel):
    _S1 = None
    _S2 = None

    def __init__(self, button_callback: callable, connection_manager: MozaConnectionManager) -> None:
        super().__init__("Sequential Shifter", button_callback, connection_manager)

    def prepare_ui(self) -> None:
        self.add_preferences_group("Shifter Settings")
        self._add_row(BoxflatSwitchRow("Reverse Shift Direction", subtitle="Why would you do that?"))
        self._current_row.subscribe(lambda v: self._cm.set_setting("sequential-direction", v))
        self._cm.subscribe("sequential-direction", self._current_row.set_value)

        self._add_row(BoxflatSwitchRow("Paddle Shifter Synchronization", subtitle="Why would you do that?"))
        self._current_row.subscribe(lambda v: self._cm.set_setting("sequential-paddle-sync", v+1))
        self._cm.subscribe("sequential-paddle-sync", self._current_row.set_value)

        self._add_row(BoxflatSliderRow("Button Brightness", 0, 10))
        self._current_row.add_marks(5);
        self._current_row.subscribe(lambda v: self._cm.set_setting("sequential-brightness", v))
        self._cm.subscribe("sequential-brightness", self._current_row.set_value)

        self.S1 = BoxflatColorPickerRow("S1 Color")
        self._add_row(self.S1)

        self.S2 = BoxflatColorPickerRow("S2 Color")
        self._add_row(self.S2)

        self.S1.subscribe(lambda v: self._cm.set_setting("sequential-colors", byte_value=bytes([self.S1.value, self.S2.value])))
        self.S2.subscribe(lambda v: self._cm.set_setting("sequential-colors", byte_value=bytes([self.S1.value, self.S2.value])))

        self._cm.subscribe("sequential-colors", lambda v: self.S1.set_value(round(v / 256)))
        self._cm.subscribe("sequential-colors", lambda v: self.S2.set_value(v % 256))
