from panels.settings_panel import SettingsPanel
import connection_manager

class HandbrakeSettings(SettingsPanel):
    def __init__(self, button_callback) -> None:
        super(HandbrakeSettings, self).__init__("Handbrake", button_callback)


    def _prepare_ui(self) -> None:
        self._add_preferences_page()
        self._add_preferences_group("Handbrake settings")
        self._add_switch_row("Reverse Direction", callback=self._set_direction)
        self._add_toggle_button_row("Handbrake Mode", ["Axis", "Button"], callback=self._set_mode)
        self._add_slider_row(
            "Button threshold",
            0,
            100,
            50,
            marks=[50],
            mark_suffix=" %",
            callback=self._set_button_threshold
        )

        self._add_preferences_group("Calibration")
        self._add_button_row("Device Calibration", "Calibrate", subtitle="Set device range", callback=self._calibrate)


    def _set_direction(self, value: int) -> None:
        if value != None:
            connection_manager.set_handbrake_setting("direction", value)


    def _set_mode(self, label: str) -> None:
        if label == "Axis":
            connection_manager.set_handbrake_setting("mode", 0)
        elif label == "Button":
            connection_manager.set_handbrake_setting("mode", 1)


    def _set_button_threshold(self, value: int) -> None:
        if value != None:
            connection_manager.set_handbrake_setting("button-threshold", value)

    def _calibrate(self) -> None:
        connection_manager.set_handbrake_setting("calibrate", 1)
