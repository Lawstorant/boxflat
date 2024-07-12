from boxflat.panels.settings_panel import SettingsPanel
from boxflat.connection_manager import MozaConnectionManager

from boxflat.widgets import *

class WheelSettings(SettingsPanel):
    def __init__(self, button_callback: callable, connection_manager: MozaConnectionManager) -> None:
        self._split = None
        super(WheelSettings, self).__init__("Wheel", button_callback, connection_manager)


    def prepare_ui(self) -> None:
        self.add_preferences_group("Input settings")
        self._add_row(BoxflatToggleButtonRow("Dual Clutch Paddles Mode"))
        self._current_row.add_buttons("Buttons", "Combined", "Split")
        self._current_row.subscribe(lambda v: self._cm.set_setting("wheel-paddles-mode", v+1))
        self._current_row.subscribe(lambda v: slider.set_active(v == 1))
        self._cm.subscribe("wheel-paddles-mode", lambda v: self._current_row.set_value(v-1))

        slider = BoxflatSliderRow("Clutch Split Point", suffix="%")
        self._add_row(slider)
        self._current_row.subtitle = "Left paddle cutoff"
        self._current_row.add_marks(25, 50, 75)
        self._current_row.subscribe(lambda v: self._cm.set_setting("wheel-clutch-point", v))
        self._cm.subscribe("wheel-clutch-point", self._current_row.set_value)
        self._cm.subscribe("wheel-paddles-mode", lambda v: self._current_row.set_active(v == 2))

        self._add_row(BoxflatToggleButtonRow("Left Stick Mode"))
        self._current_row.add_buttons("Buttons", "D-Pad")
        self._current_row.subscribe(lambda v: self._cm.set_setting("wheel-stick-mode", v*256))
        self._cm.subscribe("wheel-stick-mode", lambda v: self._current_row.set_value(round(v/256)))

        # RPM Lights
        self.add_preferences_group("Indicator settings")
        self._add_row(BoxflatToggleButtonRow("RPM Indicator Mode"))
        self._current_row.add_buttons("RPM", "Off", "On")
        self._current_row.subscribe(lambda v: self._cm.set_setting("wheel-indicator-mode", v+1))
        self._cm.subscribe("wheel-indicator-mode", lambda v: self._current_row.set_value(v-1))

        self._add_row(BoxflatToggleButtonRow("RPM Indicator Display Mode"))
        self._current_row.add_buttons("Mode 1", "Mode 2")
        self._current_row.subscribe(lambda v: self._cm.set_setting("wheel-display-mode", v+1))
        self._cm.subscribe("wheel-display-mode", lambda v: self._current_row.set_value(v-1))

        self._add_row(BoxflatToggleButtonRow("RPM Indicator Timing"))
        self._current_row.add_buttons("Early", "Normal", "Late")
        self._current_row.subscribe(self._set_indicator_timings)

        self._add_row(BoxflatSliderRow("Brightness", suffix="%"))
        self._current_row.subtitle = "RPM and buttons"
        self._current_row.add_marks(25, 50, 75)
        self._current_row.subscribe(lambda v: self._cm.set_setting("wheel-brightness", v))
        self._cm.subscribe("wheel-brightness", self._current_row.set_value)


    def _set_indicator_timings(self, value: int) -> None:
        if value == 0:
            value = bytes([65, 69, 72, 75, 78, 80, 83, 85, 88, 91])
            self._cm.set_setting("wheel-indicator-timings", byte_value=value)
        elif value == 1:
            value = bytes([75, 79, 82, 85, 87, 88, 89, 90, 92, 94])
            self._cm.set_setting("wheel-indicator-timings", byte_value=value)
        elif value == 2:
            value = bytes([80, 83, 86, 89, 91, 92, 93, 94, 96, 97])
            self._cm.set_setting("wheel-indicator-timings", byte_value=value)
