from boxflat.panels.settings_panel import SettingsPanel
from boxflat.connection_manager import MozaConnectionManager

class HandbrakeSettings(SettingsPanel):
    def __init__(self, button_callback: callable, connection_manager: MozaConnectionManager) -> None:
        self._threshold_active = None
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
            marks=[50],
            mark_suffix=" %",
            callback=self._set_button_threshold
        )

        self.add_preferences_group("Calibration")
        self.add_button_row("Device Calibration", "Calibrate", subtitle="Set device range", callback=self._set_calibration)


    def _set_direction(self, value: int) -> None:
        if value != None:
            self._cm.set_handbrake_setting("direction", value)


    def _set_mode(self, label: str) -> None:
        if label == "Axis":
            self._cm.set_handbrake_setting("mode", 0)
            self._threshold_active(False)
        elif label == "Button":
            self._cm.set_handbrake_setting("mode", 1)
            self._threshold_active(True)


    def _set_button_threshold(self, value: int) -> None:
        if value != None:
            self._cm.set_handbrake_setting("button-threshold", value)


    def _set_calibration(self) -> None:
        self._cm.set_handbrake_setting("calibration", 1)
