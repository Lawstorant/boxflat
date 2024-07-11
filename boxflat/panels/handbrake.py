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
        self._add_row(BoxflatSwitchRow("Reverse Direction"))
        self._current_row.subscribe(lambda value: self._cm.set_setting("handbrake-direction", value))

        self._add_row(BoxflatToggleButtonRow("Handbrake Mode"))
        self._current_row.add_buttons("Axis", "Button")
        self._current_row.subscribe(lambda value: self._cm.set_setting("handbrake-mode", value))

        self._add_row(BoxflatSliderRow("Button threshold", suffix="%"))
        self._current_row.subtitle = "Doesn't work for some reason"
        self._current_row.add_marks(25, 50, 75)
        self._current_row.subscribe(lambda value: self._cm.set_setting("handbrake-button-threshold", value))
        self._cm.subscribe("handbrake-mode", self._current_row.active)

        self._add_row(BoxflatSliderRow("Handbrake Range Start", suffix="%"))
        self._current_row.subtitle = "Doesn't work for some reason"
        self._current_row.add_marks(25, 50, 75)
        self._current_row.subscribe(lambda value: self._cm.set_setting("handbrake-range-start", value))

        self._add_row(BoxflatSliderRow("Handbrake Range End", suffix="%"))
        self._current_row.subtitle = "Doesn't work for some reason"
        self._current_row.add_marks(25, 50, 75)
        self._current_row.subscribe(lambda value: self._cm.set_setting("handbrake-range-end", value))

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
