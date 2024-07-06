from panels.settings_panel import SettingsPanel

class HPatternSettings(SettingsPanel):
    def __init__(self, button_callback) -> None:
        super(HPatternSettings, self).__init__("H-Pattern Shifter", button_callback)

    def _prepare_ui(self) -> None:
        self._add_preferences_page()
        self._add_preferences_group("Shifter Settings")

        self._add_switch_row("Auto Downshift Throttle Blip", True, subtitle="Easy rev match")
        self._add_slider_row(
            "Auto Blip Output", 0, 100, 80,
            marks=[50],
            mark_suffix="%",
            subtitle="Throttle level"
        )
        self._add_slider_row(
            "Auto Blip Duration", 0, 1000, 300,
            marks=[250, 500, 750],
            mark_suffix=" ms"
        )

        self._add_preferences_group("Calibration")
        self._add_button_row("Device Calibration", "Calibrate", subtitle="In case of weird behavior")
