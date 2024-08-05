from boxflat.panels.settings_panel import SettingsPanel
from boxflat.connection_manager import MozaConnectionManager

from boxflat.widgets import *

MOZA_TELEMETRY_FLAGS = [
    "Wheel Spin",
    "Pitlane",
    "Pit Limiter",
    "ABS",
    "Traction Control",
    "DRS ON",
    "Red Flag",
    "Yellow Flag",
    "Blue Flag",
    "Green Flag",
    "White Flag"
]

class WheelSettings(SettingsPanel):
    def __init__(self, button_callback: callable, connection_manager: MozaConnectionManager) -> None:
        self._split = None
        self._timing_row = None
        self._timing_preset_row = None
        self._timings = []
        self._timings.append([65, 69, 72, 75, 78, 80, 83, 85, 88, 91]) # Early
        self._timings.append([75, 79, 82, 85, 87, 88, 89, 90, 92, 94]) # Normal
        self._timings.append([80, 83, 86, 89, 91, 92, 93, 94, 96, 97]) # Late
        # self._timings.append([80, 83, 86, 89, 91, 92, 93, 94, 96, 97]) # Central

        super().__init__("Wheel", button_callback, connection_manager)
        self._append_sub_connected("wheel-clutch-point", self.active)


    def prepare_ui(self) -> None:
        self.add_view_stack()
        self.add_preferences_page("Wheel")

        self.add_preferences_group("Input settings")
        self._add_row(BoxflatToggleButtonRow("Dual Clutch Paddles Mode"))
        self._current_row.add_buttons("Buttons", "Combined", "Split")
        self._current_row.set_expression("+1")
        self._current_row.set_reverse_expression("-1")

        slider = BoxflatSliderRow("Clutch Split Point", suffix="%", range_start=5, range_end=95)
        self._current_row.subscribe(lambda v: slider.set_active(v == 2))
        self._current_row.subscribe(self._cm.set_setting_int, "wheel-paddles-mode")
        self._append_sub("wheel-paddles-mode", self._current_row.set_value)

        self._add_row(slider)
        self._current_row.set_active(False)
        self._current_row.subtitle = "Left paddle cutoff"
        self._current_row.add_marks(25, 50, 75)
        self._current_row.subscribe(self._cm.set_setting_int, "wheel-clutch-point")
        self._append_sub("wheel-clutch-point", self._current_row.set_value)
        self._append_sub("wheel-paddles-mode", lambda v: slider.set_active(v == 2))

        self._add_row(BoxflatToggleButtonRow("Rotary Encoder Mode"))
        self._current_row.add_buttons("Buttons", "  Knob ")
        self._current_row.subscribe(self._cm.set_setting_int, "wheel-knob-mode")
        self._append_sub("wheel-knob-mode", self._current_row.set_value)
        self._append_sub_connected("wheel-knob-mode", self._current_row.set_present)

        self._add_row(BoxflatToggleButtonRow("Left Stick Mode"))
        self._current_row.add_buttons("Buttons", "D-Pad")
        self._current_row.set_expression("*256")
        self._current_row.set_reverse_expression("/256")
        self._current_row.subscribe(self._cm.set_setting_int, "wheel-stick-mode")
        self._append_sub("wheel-stick-mode", self._current_row.set_value)

        self.add_preferences_group("Brightness")
        self._add_row(BoxflatSliderRow("Button Brightness", range_end=15))
        self._current_row.add_marks(5, 10)
        self._current_row.subscribe(self._cm.set_setting_int, "wheel-buttons-brightness")
        self._append_sub("wheel-buttons-brightness", self._current_row.set_value)

        self._add_row(BoxflatSliderRow("RPM Brightness", range_end=15))
        self._current_row.add_marks(5, 10)
        self._current_row.subscribe(self._cm.set_setting_int, "wheel-rpm-brightness")
        self._append_sub("wheel-rpm-brightness", self._current_row.set_value)

        self._add_row(BoxflatSliderRow("Flag Brightness", range_end=15))
        self._current_row.add_marks(5, 10)
        self._current_row.subscribe(self._cm.set_setting_int, "wheel-flags-brightness")
        self._append_sub("wheel-flags-brightness", self._current_row.set_value)

        self.add_preferences_group("Misc")
        self._add_row(BoxflatButtonRow("Reset Parameters", "WIP"))
        self._add_row(BoxflatButtonRow("Calibrate Paddles", "WIP"))

        self.add_preferences_page("RPM")
        self.add_preferences_group("Indicator settings")

        self._add_row(BoxflatToggleButtonRow("RPM Indicator Mode"))
        self._current_row.add_buttons("RPM", "Off", "On ")
        self._current_row.set_expression("+1")
        self._current_row.set_reverse_expression("-1")
        self._current_row.subscribe(self._cm.set_setting_int, "wheel-indicator-mode")
        self._append_sub("wheel-indicator-mode", self._current_row.set_value)

        self._add_row(BoxflatToggleButtonRow("RPM Indicator Display Mode"))
        self._current_row.add_buttons("Mode 1", "Mode 2")
        self._current_row.subscribe(self._cm.set_setting_int, "wheel-set-display-mode")
        self._append_sub("wheel-get-display-mode", self._current_row.set_value)

        self._add_row(BoxflatToggleButtonRow("RPM Mode"))
        self._current_row.add_buttons("Percent", "RPM")
        self._current_row.subscribe(self._cm.set_setting_int, "wheel-rpm-mode")
        self._append_sub("wheel-rpm-mode", self._current_row.set_value)

        self.add_preferences_group("Timings")
        self._timing_row = BoxflatEqRow("RPM Indicator Timing", 10, "Is it my turn now?",
            button_row=False, draw_marks=False)

        self._add_row(self._timing_row)
        self._timing_row.add_marks(50, 80)
        self._timing_row.add_buttons("Early", "Normal", "Late")
        self._timing_row.set_button_value(-1)
        self._timing_row.subscribe(self._set_rpm_timings_preset)
        self._timing_row.subscribe_sliders(self._set_rpm_timings)
        for i in range(MOZA_RPM_LEDS):
            self._timing_row.add_labels(f"RPM{i+1}", index=i)

        self._append_sub("wheel-rpm-timings", self._get_rpm_timings)
        self._append_sub("wheel-rpm-timings", self._get_rpm_timings_preset)


        self._add_row(BoxflatSliderRow("Blinking Interval", range_end=1000, subtitle="Miliseconds"))
        self._current_row.add_marks(200, 400, 600, 800)
        self._current_row.subscribe(self._cm.set_setting_int, "wheel-rpm-interval")
        self._append_sub("wheel-rpm-interval", self._current_row.set_value)


        self.add_preferences_page("Colors")
        self.add_preferences_group("Buttons")
        self._add_row(BoxflatNewColorPickerRow(""))
        self._current_row.subscribe(self._cm.set_setting_list, "wheel-button-color")
        for i in range(MOZA_RPM_LEDS):
            self._append_sub(f"wheel-button-color{i+1}", self._current_row.set_led_value, i)

        self.add_preferences_group("RPM Colors")
        self._add_row(BoxflatNewColorPickerRow(""))
        self._current_row.subscribe(self._cm.set_setting_list, "wheel-rpm-color")
        for i in range(MOZA_RPM_LEDS):
            self._append_sub(f"wheel-rpm-color{i+1}", self._current_row.set_led_value, i)

        # self._add_row(BoxflatNewColorPickerRow("RPM Blinking"))
        # self._current_row.subscribe(self._cm.set_setting_list, "wheel-rpm-blink-color")
        # for i in range(MOZA_RPM_LEDS):
        #     self._append_sub(f"wheel-rpm-blink-color{i+1}", self._current_row.set_led_value, i)

        self.add_preferences_group("Telemetry flag")
        self._add_row(BoxflatNewColorPickerRow(""))
        self._current_row.subscribe(self._cm.set_setting_list, "wheel-flag-color")
        for i in range(MOZA_RPM_LEDS):
            self._append_sub(f"wheel-flag-color{i+1}", self._current_row.set_led_value, i)


    def _set_rpm_timings(self, timings: list) -> None:
        self._cm.set_setting_list(timings[:-1], "wheel-rpm-timings")


    def _set_rpm_timings_preset(self, value: int) -> None:
        self._cm.set_setting_list(self._timings[value], "wheel-rpm-timings")


    def _get_rpm_timings(self, timings: list) -> None:
        self._timing_row.set_sliders_value(timings)


    def _get_rpm_timings_preset(self, timings: list) -> None:
        index = -1
        if list(timings) in self._timings:
            index = self._timings.index(list(timings))

        self._timing_row.set_button_value(index)
