from boxflat.panels.settings_panel import SettingsPanel
from boxflat.connection_manager import MozaConnectionManager
import time
from boxflat.widgets import *

class HandbrakeSettings(SettingsPanel):
    def __init__(self, button_callback: callable, connection_manager: MozaConnectionManager) -> None:
        self._threshold_active = None
        self._calibration_button = None
        super(HandbrakeSettings, self).__init__("Handbrake", button_callback, connection_manager)

    def prepare_ui(self) -> None:
        self.add_preferences_group("Handbrake settings")
        self.add_switch_row("Reverse Direction", callback=self._set_direction)
        self.add_toggle_button_row("Handbrake Mode", ["Axis", "Button"], callback=self._set_mode)

        row = BoxflatSliderRow("Button threshold", suffix="%")
        row.subtitle = "Doesn't work for some reason"
        row.add_marks(25, 50, 75)
        row.active = False
        row.subscribe(lambda value: self._cm.set_setting("handbrake-button-threshold", value))
        self._cm.subscribe("handbrake-mode", row.value)
        self._add_row(row)

        row = BoxflatSliderRow("Handbrake Range Start", suffix="%")
        row.subtitle = "Doesn't work for some reason"
        row.add_marks(25, 50, 75)
        row.active = False
        row.subscribe(lambda value: self._cm.set_setting("handbrake-range-start", value))
        self._add_row(row)

        row = BoxflatSliderRow("Handbrake Range End", suffix="%")
        row.subtitle = "Doesn't work for some reason"
        row.add_marks(25, 50, 75)
        row.active = False
        row.subscribe(lambda value: self._cm.set_setting("handbrake-range-end", value))
        self._add_row(row)

        self.add_preferences_group("Calibration")
        self.add_calibration_button_row("Device Calibration", "Calibrate",
            callback1=self._set_calibration_start, callback2=self._set_calibration_stop)


    def _set_direction(self, value: int) -> None:
        if value != None:
            self._cm.set_setting("handbrake-direction", value)


    def _set_mode(self, label: str) -> None:
        if label == "Axis":
            self._cm.set_setting("handbrake-mode", 0)
            # self._threshold_active(False)
        elif label == "Button":
            self._cm.set_setting("handbrake-mode", 1)
            # self._threshold_active(True)

    def _set_calibration_start(self) -> None:
        self._cm.set_setting(f"handbrake-start-calibration")

    def _set_calibration_stop(self) -> None:
        self._cm.set_setting(f"handbrake-stop-calibration")
