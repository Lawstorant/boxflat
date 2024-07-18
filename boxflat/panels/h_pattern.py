from boxflat.panels.settings_panel import SettingsPanel
from boxflat.connection_manager import MozaConnectionManager
from boxflat.widgets import *

class HPatternSettings(SettingsPanel):
    def __init__(self, button_callback: callable, connection_manager: MozaConnectionManager) -> None:
        self._slider1 = None
        self._slider2 = None
        super(HPatternSettings, self).__init__("H-Pattern Shifter", button_callback, connection_manager)


    def prepare_ui(self) -> None:
        self.add_preferences_group("Shifter Settings")

        row1 = BoxflatSliderRow("Auto Blip Output", 0, 100)
        row2 = BoxflatSliderRow("Auto Blip Duration", 0, 1000, subtitle="Miliseconds")

        self._add_row(BoxflatSwitchRow("Auto Downshift Throttle Blip", subtitle="Easy rev match"))
        self._current_row.subscribe(self._cm.set_setting_int, "hpattern-throttle-blip")
        self._current_row.subscribe(row1.set_active)
        self._current_row.subscribe(row2.set_active)
        self._append_sub("hpattern-throttle-blip", self._current_row.set_value)

        self._add_row(row1)
        self._current_row.add_marks(50)
        self._current_row.subscribe(self._cm.set_setting_int, "hpattern-blip-output")
        self._append_sub("hpattern-blip-output", self._current_row.set_value)
        self._append_sub("hpattern-throttle-blip", self._current_row.set_active)
        self._current_row.set_active(False)

        self._add_row(row2)
        self._current_row.add_marks(250, 500, 750)
        self._current_row.subscribe(self._cm.set_setting_int, "hpattern-blip-duration")
        self._append_sub("hpattern-blip-duration", self._current_row.set_value)
        self._append_sub("hpattern-throttle-blip", self._current_row.set_active)
        self._current_row.set_active(False)

        self.add_preferences_group("Calibration")
        self._add_row(BoxflatCalibrationRow("Device Calibration", "Fix device range"))
        self._current_row.subscribe(self._cm.set_setting_int, "hpattern")
