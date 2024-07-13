from boxflat.panels.settings_panel import SettingsPanel
from boxflat.connection_manager import MozaConnectionManager

from boxflat.widgets import *

class WheelSettings(SettingsPanel):
    def __init__(self, button_callback: callable, connection_manager: MozaConnectionManager) -> None:
        self._split = None
        self._timing_row = None
        self._timings = []
        self._timings.append([65, 69, 72, 75, 78, 80, 83, 85, 88, 91])
        self._timings.append([75, 79, 82, 85, 87, 88, 89, 90, 92, 94])
        self._timings.append([80, 83, 86, 89, 91, 92, 93, 94, 96, 97])
        super(WheelSettings, self).__init__("Wheel", button_callback, connection_manager)


    def prepare_ui(self) -> None:
        self.add_preferences_group("Input settings")
        self._add_row(BoxflatToggleButtonRow("Dual Clutch Paddles Mode"))
        self._current_row.add_buttons("Buttons", "Combined", "Split")
        self._current_row.set_expression("+1")
        self._current_row.set_reverse_expression("-1")

        slider = BoxflatSliderRow("Clutch Split Point", suffix="%")
        self._current_row.subscribe(lambda v: slider.set_active(v == 2))
        self._current_row.subscribe(lambda v: self._cm.set_setting("wheel-paddles-mode", v))
        self._cm.subscribe("wheel-paddles-mode", self._current_row.set_value)

        self._add_row(slider)
        self._current_row.set_active(False)
        self._current_row.subtitle = "Left paddle cutoff"
        self._current_row.add_marks(25, 50, 75)
        self._current_row.subscribe(lambda v: self._cm.set_setting("wheel-clutch-point", v))
        self._cm.subscribe("wheel-clutch-point", self._current_row.set_value)
        self._cm.subscribe("wheel-paddles-mode", lambda v: slider.set_active(v == 2))

        self._add_row(BoxflatToggleButtonRow("Left Stick Mode"))
        self._current_row.add_buttons("Buttons", "D-Pad")
        self._current_row.set_expression("*256")
        self._current_row.set_reverse_expression("/256")
        self._current_row.subscribe(lambda v: self._cm.set_setting("wheel-stick-mode", v))
        self._cm.subscribe("wheel-stick-mode", self._current_row.set_value)

        # RPM Lights
        self.add_preferences_group("Indicator settings")
        self._add_row(BoxflatToggleButtonRow("RPM Indicator Mode"))
        self._current_row.add_buttons("RPM", "Off", "On")
        self._current_row.set_expression("+1")
        self._current_row.set_reverse_expression("-1")
        self._current_row.subscribe(lambda v: self._cm.set_setting("wheel-indicator-mode", v))
        self._cm.subscribe("wheel-indicator-mode", self._current_row.set_value)

        self._add_row(BoxflatToggleButtonRow("RPM Indicator Display Mode"))
        self._current_row.set_subtitle("Not read from the wheel")
        self._current_row.add_buttons("Mode 1", "Mode 2")
        self._current_row.set_expression("+1")
        self._current_row.set_reverse_expression("-1")
        self._current_row.subscribe(lambda v: self._cm.set_setting("wheel-display-mode", v))
        # self._cm.subscribe("wheel-display-mode", self._current_row.set_value)

        index = -1
        timings = self._cm.get_setting_list("wheel-indicator-timings")
        if timings in self._timings:
            index = self._timings.index(timings)

        self._timing_row = BoxflatToggleButtonRow("RPM Indicator Timing")
        self._add_row(self._timing_row)
        self._current_row.add_buttons("Early", "Normal", "Late")
        self._current_row.set_value(index)
        self._current_row.subscribe(self._set_indicator_timings)

        self._add_row(BoxflatSliderRow("Brightness", suffix="%"))
        self._current_row.subtitle = "RPM and buttons"
        self._current_row.add_marks(25, 50, 75)
        self._current_row.subscribe(lambda v: self._cm.set_setting("wheel-brightness", v))
        self._cm.subscribe("wheel-brightness", self._current_row.set_value)


    def _set_indicator_timings(self, value: int) -> None:
        self._cm.set_setting("wheel-indicator-timings", byte_value=bytes(self._timings[value]))
