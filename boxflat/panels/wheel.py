from boxflat.panels.settings_panel import SettingsPanel
from boxflat.connection_manager import MozaConnectionManager

from boxflat.widgets import *

class WheelSettings(SettingsPanel):
    def __init__(self, button_callback: callable, connection_manager: MozaConnectionManager) -> None:
        self._split = None
        self._timing_row = None
        self._timings = []
        self._timings.append([65, 69, 72, 75, 78, 80, 83, 85, 88, 91]) # Early
        self._timings.append([75, 79, 82, 85, 87, 88, 89, 90, 92, 94]) # Normal
        self._timings.append([80, 83, 86, 89, 91, 92, 93, 94, 96, 97]) # Late
        super().__init__("Wheel", button_callback, connection_manager)
        self._append_sub_connected("wheel-paddles-mode", self.active)


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

        self._add_row(BoxflatToggleButtonRow("Left Stick Mode"))
        self._current_row.add_buttons("Buttons", "D-Pad")
        self._current_row.set_expression("*256")
        self._current_row.set_reverse_expression("/256")
        self._current_row.subscribe(self._cm.set_setting_int, "wheel-stick-mode")
        self._append_sub("wheel-stick-mode", self._current_row.set_value)

        # RPM Lights
        self.add_preferences_group("Indicator settings")
        self._add_row(BoxflatToggleButtonRow("RPM Indicator Mode"))
        self._current_row.add_buttons("RPM", "Off", "On")
        self._current_row.set_expression("+1")
        self._current_row.set_reverse_expression("-1")
        self._current_row.subscribe(self._cm.set_setting_int, "wheel-indicator-mode")
        self._append_sub("wheel-indicator-mode", self._current_row.set_value)

        self._add_row(BoxflatToggleButtonRow("RPM Indicator Display Mode"))
        self._current_row.add_buttons("Mode 1", "Mode 2")
        self._current_row.subscribe(self._cm.set_setting_int, "wheel-set-display-mode")
        self._append_sub("wheel-get-display-mode", self._current_row.set_value)

        self._timing_row = BoxflatToggleButtonRow("RPM Indicator Timing")
        self._timing_row.set_subtitle("Custom if not active")
        self._timing_row.add_buttons("Early", "Normal", "Late")
        self._timing_row.set_value(-1)
        self._timing_row.subscribe(self._set_indicator_timings)
        self._append_sub("wheel-indicator-timings", self._get_indicator_timings)
        self._add_row(self._timing_row)

        self._add_row(BoxflatSliderRow("Brightness", suffix="%"))
        self._current_row.subtitle = "RPM and buttons"
        self._current_row.add_marks(25, 50, 75)
        self._current_row.subscribe(self._cm.set_setting_int, "wheel-brightness")
        self._append_sub("wheel-brightness", self._current_row.set_value)


        self.add_preferences_page("RPM")
        self.add_preferences_group("RPM colors")

        for i in range(10):
            self._add_row(BoxflatColorPickerRow(f"Indicator {i+1} Color", alt_colors=True))


    def _set_indicator_timings(self, value: int) -> None:
        self._cm.set_setting_list(self._timings[value], "wheel-indicator-timings")


    def _get_indicator_timings(self, timings: list) -> None:
        index = -1
        if list(timings) in self._timings:
            index = self._timings.index(timings)

        self._timing_row.set_value(index)
