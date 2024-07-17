from boxflat.panels.settings_panel import SettingsPanel
from boxflat.connection_manager import MozaConnectionManager
from boxflat.widgets import *

class HandbrakeSettings(SettingsPanel):
    def __init__(self, button_callback: callable, connection_manager: MozaConnectionManager) -> None:
        self._threshold_active = None
        self._calibration_button = None
        super(HandbrakeSettings, self).__init__("Handbrake", button_callback, connection_manager)


    def prepare_ui(self) -> None:
        self.add_preferences_group("Handbrake settings")
        self._add_row(BoxflatSwitchRow("Reverse Direction"))
        self._current_row.subscribe(lambda v: self._cm.set_setting("handbrake-direction", v))
        self._cm.subscribe("handbrake-direction", self._current_row.set_value)

        row = BoxflatSliderRow("Button threshold", suffix="%")

        self._add_row(BoxflatToggleButtonRow("Handbrake Mode"))
        self._current_row.add_buttons("Axis", "Button")
        self._current_row.subscribe(lambda v: self._cm.set_setting("handbrake-mode", v))
        self._current_row.subscribe(row.set_active)
        self._cm.subscribe("handbrake-mode", self._current_row.set_value)

        self._add_row(row)
        self._current_row.add_marks(25, 50, 75)
        self._current_row.subscribe(lambda v: self._cm.set_setting("handbrake-button-threshold", v))
        self._cm.subscribe("handbrake-mode", self._current_row.set_active)
        self._cm.subscribe("handbrake-button-threshold", self._current_row.set_value)

        self.add_preferences_group("Range settings", level_bar=1)
        self._current_group.set_bar_max(65535)
        self._cm.subscribe_cont("handbrake-output", self._current_group.set_bar_level)
        self._cm.subscribe("handbrake-range-start", self._current_group.set_range_start)
        self._cm.subscribe("handbrake-range-end", self._current_group.set_range_end)

        # self._add_row(BoxflatEqRow("Output Curve", 5, suffix="%"))
        # self._current_row.add_marks(20, 40, 60, 80)
        # self._current_row.add_labels("20%", "40%", "60%", "80%", "100%")
        # self._current_row.set_height(260)
        # self._current_row.add_buttons("Linear", "S Curve", "Exponential", "Parabolic")
        # self._current_row.set_button_value(-1)

        self._add_row(BoxflatSliderRow("Range Start", suffix="%"))
        self._current_row.add_marks(20, 40, 60, 80)
        self._current_row.set_width(380)
        self._current_row.subscribe(lambda v: self._cm.set_setting("handbrake-range-start", v))
        # self._current_row.subscribe(self._current_group.set_range_start)
        self._cm.subscribe("handbrake-range-start", self._current_row.set_value)

        self._add_row(BoxflatSliderRow("Range End", suffix="%", value=100))
        self._current_row.add_marks(20, 40, 60, 80)
        self._current_row.set_width(380)
        self._current_row.subscribe(lambda v: self._cm.set_setting("handbrake-range-end", v))
        # self._current_row.subscribe(self._current_group.set_range_end)
        self._cm.subscribe("handbrake-range-end", self._current_row.set_value)

        self.add_preferences_group("Calibration")
        self._add_row(BoxflatCalibrationRow("Handbrake Calibration", "Fix device range"))
        self._current_row.subscribe(lambda v: self._cm.set_setting(f"handbrake-{v}-calibration", 1))

