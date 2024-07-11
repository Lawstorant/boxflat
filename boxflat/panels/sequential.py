from boxflat.panels.settings_panel import SettingsPanel
from boxflat.connection_manager import MozaConnectionManager
from boxflat.widgets import *

class SequentialSettings(SettingsPanel):
    colorS1 = 0
    colorS2 = 0

    def __init__(self, button_callback: callable, connection_manager: MozaConnectionManager) -> None:
        super(SequentialSettings, self).__init__("Sequential Shifter", button_callback, connection_manager)

    def prepare_ui(self) -> None:
        self.add_preferences_group("Shifter Settings")
        self._add_row(BoxflatSwitchRow("Reverse Shift Direction", subtitle="Why would you do that?"))
        self._current_row.subscribe(lambda v: self._cm.set_setting("sequential-direction", v))
        self._cm.subscribe("sequential-direction", self._current_row.set_value)

        self._add_row(BoxflatSwitchRow("Paddle Shifter Synchronization", subtitle="Why would you do that?"))
        self._current_row.subscribe(lambda v: self._cm.set_setting("sequential-paddle-sync", v+1))
        self._cm.subscribe("sequential-paddle-sync", self._current_row.set_value)

        self._add_row(BoxflatSliderRow("Button Brightness", 0, 10))
        self._current_row.add_marks(5)
        self._current_row.subscribe(lambda v: self._cm.set_setting("sequential-brightness", v))
        self._cm.subscribe("sequential-brightness", self._current_row.set_value)


        self._add_row(BoxflatColorPickerRow("S1 Color"))
        self._current_row.subscribe(lambda v: self._set_colors(1, v))
        self._cm.subscribe("sequential-colors", lambda v: self._current_row.set_value(v % 256))

        self._add_row(BoxflatColorPickerRow("S2 Color"))
        self._current_row.subscribe(lambda v: self._set_colors(2, v))
        self._cm.subscribe("sequential-colors", lambda v: self._current_row.set_value(round(v / 256)))


    def _set_colors(self, button: int, color: int) -> None:
        if color == None:
            return
        if button == 1:
            self.colorS1 = color
        if button == 2:
            self.colorS2 = color

        self._cm.set_setting("sequential-colors", self.colorS1*256 + self.colorS2)
