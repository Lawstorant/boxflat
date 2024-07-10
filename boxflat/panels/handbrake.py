from boxflat.panels.settings_panel import SettingsPanel
from boxflat.connection_manager import MozaConnectionManager
import time

class HandbrakeSettings(SettingsPanel):
    def __init__(self, button_callback: callable, connection_manager: MozaConnectionManager) -> None:
        self._threshold_active = None
        self._calibration_button = None
        super(HandbrakeSettings, self).__init__("Handbrake", button_callback, connection_manager)

    def prepare_ui(self) -> None:
        self.add_preferences_page()
        self.add_preferences_group("Handbrake settings")
        self.add_switch_row("Reverse Direction", callback=self._set_direction)
        self.add_toggle_button_row("Handbrake Mode", ["Axis", "Button"], callback=self._set_mode)
        self._threshold_active = self.add_slider_row(
            "Button threshold",
            0,
            100,
            50,
            marks=[25, 50, 75],
            mark_suffix=" %",
            callback=self._set_button_threshold,
            subtitle="Doesn't work for some reason"
        )
        self.add_slider_row(
            "Handbrake Range Start",
            0,
            100,
            0,
            marks=[25, 50, 75],
            mark_suffix=" %",
            callback=lambda value: self._set_range("start", value)
        )
        self.add_slider_row(
            "Handbrake Range End",
            0,
            100,
            100,
            marks=[25, 50, 75],
            mark_suffix=" %",
            callback=lambda value: self._set_range("end", value)
        )

        self.add_preferences_group("Calibration")
        self.add_calibration_button_row("Device Calibration", "Calibrate",
            callback1=self._set_calibration_start, callback2=self._set_calibration_stop)


    def _set_direction(self, value: int) -> None:
        if value != None:
            self._cm.set_setting("handbrake-direction", value)


    def _set_mode(self, label: str) -> None:
        if label == "Axis":
            self._cm.set_setting("handbrake-mode", 0)
            self._threshold_active(False)
        elif label == "Button":
            self._cm.set_setting("handbrake-mode", 1)
            self._threshold_active(True)


    def _set_button_threshold(self, value: int) -> None:
        if value != None:
            self._cm.set_setting("handbrake-button-threshold", value)


    def _set_range(self, position: str, value: int) -> None:
        self._cm.set_setting(f"handbrake-range-{position}", value)


    def _set_calibration_start(self) -> None:
        self._cm.set_setting(f"handbrake-start-calibration")

    def _set_calibration_stop(self) -> None:
        self._cm.set_setting(f"handbrake-stop-calibration")
