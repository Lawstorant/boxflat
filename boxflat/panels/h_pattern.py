from boxflat.panels.settings_panel import SettingsPanel
from boxflat.connection_manager import MozaConnectionManager

class HPatternSettings(SettingsPanel):
    def __init__(self, button_callback: callable, connection_manager: MozaConnectionManager) -> None:
        self._slider1 = None
        self._slider2 = None
        super(HPatternSettings, self).__init__("H-Pattern Shifter", button_callback, connection_manager)


    def prepare_ui(self) -> None:
        self.add_preferences_page()
        self.add_preferences_group("Shifter Settings")

        self.add_switch_row("Auto Downshift Throttle Blip", True, subtitle="Easy rev match", callback=self._set_throttle_blip)
        self._slider1 = self.add_slider_row(
            "Auto Blip Output", 0, 100, 80,
            marks=[50],
            mark_suffix="%",
            subtitle="Throttle level",
            callback=self._set_blip_output
        )
        self._slider2 = self.add_slider_row(
            "Auto Blip Duration", 0, 1000, 300,
            marks=[250, 500, 750],
            subtitle="Miliseconds",
            callback=self._set_blip_duration
        )

        self.add_preferences_group("Calibration")
        self.add_calibration_button_row("Device Calibration", "Calibrate",
            callback1=self._set_calibration_start, callback2=self._set_calibration_stop)


    def _set_throttle_blip(self, value: int) -> None:
        if value == None:
            return

        self._slider1(bool(value))
        self._slider2(bool(value))
        self._cm.set_setting("hpattern-throttle-blip", value)


    def _set_blip_output(self, value: int) -> None:
        if value != None:
            self._cm.set_setting("hpattern-blip-output", value)


    def _set_blip_duration(self, value: int) -> None:
        if value != None:
            self._cm.set_setting("hpattern-blip-duration", value)


    def _set_calibration_start(self) -> None:
        self._cm.set_setting(f"hpattern-start-calibration")

    def _set_calibration_stop(self) -> None:
        self._cm.set_setting(f"hpattern-stop-calibration")
