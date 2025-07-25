# Copyright (c) 2025, Tomasz Pakuła Using Arch BTW

from boxflat.panels.settings_panel import SettingsPanel
from boxflat.connection_manager import MozaConnectionManager
from boxflat.widgets import *
from boxflat.hid_handler import MozaAxis

class HandbrakeSettings(SettingsPanel):
    def __init__(self, button_callback, connection_manager: MozaConnectionManager, hid_handler):
        self._threshold_active = None
        self._calibration_button = None
        self._curve_row = None

        self._presets = [
            [20, 40, 60, 80, 100], # Linear
            [ 8, 24, 76, 92, 100], # S Curve
            [ 6, 14, 28, 54, 100], # Exponential
            [46, 72, 86, 94, 100]  # Parabolic
        ]

        super().__init__("Handbrake", button_callback, connection_manager, hid_handler)
        self._cm.subscribe_connected("handbrake-direction", self.active)


    def prepare_ui(self):
        self.add_preferences_group("Handbrake settings")
        self._add_row(BoxflatSwitchRow("Reverse Direction"))
        self._current_row.subscribe(self._cm.set_setting, "handbrake-direction")
        self._cm.subscribe("handbrake-direction", self._current_row.set_value)

        row = BoxflatSliderRow("Button threshold", suffix="%")

        self._add_row(BoxflatToggleButtonRow("Handbrake Mode"))
        self._current_row.add_buttons("Axis", "Button")
        self._current_row.subscribe(self._cm.set_setting, "handbrake-mode")
        self._current_row.subscribe(row.set_active)
        self._cm.subscribe("handbrake-mode", self._current_row.set_value)

        self._add_row(row)
        self._current_row.add_marks(25, 50, 75)
        self._current_row.subscribe(self._cm.set_setting, "handbrake-button-threshold")
        self._cm.subscribe("handbrake-mode", self._current_row.set_active)
        self._cm.subscribe("handbrake-button-threshold", self._current_row.set_value)
        self._current_row.set_active(False)

        self.add_preferences_group("Handbrake Curve", level_bar=1)
        self._current_group.set_bar_max(65535)
        self._hid_handler.subscribe(MozaAxis.HANDBRAKE.name, self._current_group.set_bar_level)

        self._curve_row = BoxflatEqRow("", 5, suffix="%")
        self._add_row(self._curve_row)
        self._current_row.add_marks(20, 40, 60, 80)
        self._current_row.add_labels("20%", "40%", "60%", "80%", "100%")
        self._current_row.set_height(260)
        self._current_row.add_buttons("Linear", "S Curve", "Exponential", "Parabolic")
        self._current_row.set_button_value(-1)
        self._current_row.set_height(280)
        self._current_row.subscribe(self._set_curve_preset)
        for i in range(5):
            self._curve_row.subscribe_slider(i, self._set_curve_point, i)
            self._cm.subscribe(f"handbrake-y{i+1}", self._get_curve, i)

        self.add_preferences_group("Handbrake Range")
        self._add_row(BoxflatSliderRow("Range Start", suffix="%"))
        self._current_row.add_marks(20, 40, 60, 80)
        self._current_row.set_slider_width(380)
        self._current_row.subscribe(self._cm.set_setting, "handbrake-min")
        self._cm.subscribe("handbrake-min", self._current_row.set_value)

        self._add_row(BoxflatSliderRow("Range End", suffix="%", value=100))
        self._current_row.add_marks(20, 40, 60, 80)
        self._current_row.set_slider_width(380)
        self._current_row.subscribe(self._cm.set_setting, "handbrake-max")
        self._cm.subscribe("handbrake-max", self._current_row.set_value)

        self.add_preferences_group()
        self._add_row(BoxflatCalibrationRow("Handbrake Calibration", "Pull handbrake fully once"))
        self._current_row.subscribe("calibration-start", self._cm.set_setting, "handbrake-calibration-start")
        self._current_row.subscribe("calibration-stop", self._cm.set_setting, "handbrake-calibration-stop")

        self._add_row(BoxflatButtonRow("Restore default settings", "Reset"))
        self._current_row.subscribe(self.reset)


    def _set_curve_preset(self, value: int):
        self._set_curve(self._presets[value])


    def _set_curve_point(self, value: int, index: int):
        self._cm.set_setting(float(value), f"handbrake-y{index+1}")


    def _set_curve(self, values: list):
        self._curve_row.set_sliders_value(values, mute=False)


    def _get_curve(self, value: int, sindex: int):
        index = -1
        values = self._curve_row.get_sliders_value()
        values[sindex] = value

        if values in self._presets:
            index = self._presets.index(values)

        self._curve_row.set_button_value(index)
        self._curve_row.set_slider_value(value, sindex)


    def reset(self, *_) -> None:
        self._cm.set_setting(0, "handbrake-direction")
        self._cm.set_setting(0, "handbrake-mode")
        self._cm.set_setting(50, "handbrake-button-threshold")
        self._cm.set_setting(0, "handbrake-min")
        self._cm.set_setting(100, "handbrake-max")

        for i in range(len(self._presets[0])):
            self._set_curve_point(self._presets[0][i], i)
