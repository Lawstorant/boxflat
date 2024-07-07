from boxflat.panels.settings_panel import SettingsPanel
import boxflat.connection_manager as connection_manager

class HPatternSettings(SettingsPanel):
    def __init__(self, button_callback) -> None:
        super(HPatternSettings, self).__init__("H-Pattern Shifter", button_callback)


    def _prepare_ui(self) -> None:
        self._add_preferences_page()
        self._add_preferences_group("Shifter Settings")

        self._add_switch_row("Auto Downshift Throttle Blip", True, subtitle="Easy rev match", callback=self._set_throttle_blip)
        self._add_slider_row(
            "Auto Blip Output", 0, 100, 80,
            marks=[50],
            mark_suffix="%",
            subtitle="Throttle level",
            callback=self._set_blip_output
        )
        self._add_slider_row(
            "Auto Blip Duration", 0, 1000, 300,
            marks=[250, 500, 750],
            mark_suffix=" ms",
            callback=self._set_blip_duration
        )

        self._add_preferences_group("Calibration")
        self._add_button_row("Device Calibration", "Calibrate", subtitle="In case of weird behavior", callback=self._set_calibration)


    def _set_throttle_blip(self, value: int) -> None:
        if value != None:
            connection_manager.set_h_pattern_setting("throttle-blip", value)


    def _set_blip_output(self, value: int) -> None:
        if value != None:
            connection_manager.set_h_pattern_setting("blip-output", value)


    def _set_blip_duration(self, value: int) -> None:
        if value != None:
            connection_manager.set_h_pattern_setting("blip-duration", value)


    def _set_calibration(self) -> None:
        connection_manager.set_h_pattern_setting("calibration", 1)

