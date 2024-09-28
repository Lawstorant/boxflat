from boxflat.panels.settings_panel import SettingsPanel
from boxflat.connection_manager import MozaConnectionManager
from boxflat.widgets import *
from boxflat.hid_handler import MozaAxis

class HandbrakeSettings(SettingsPanel):
    def __init__(self, button_callback: callable, connection_manager: MozaConnectionManager, hid_handler) -> None:
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
        self._append_sub_connected("handbrake-direction", self.active)

    def prepare_ui(self) -> None:
        self.add_preferences_group("Handbrake settings")
        self._add_row(BoxflatSwitchRow("Reverse Direction"))
        self._current_row.subscribe(self._cm.set_setting_int, "handbrake-direction")
        self._append_sub("handbrake-direction", self._current_row.set_value)

        row = BoxflatSliderRow("Button threshold", suffix="%")

        self._add_row(BoxflatToggleButtonRow("Handbrake Mode"))
        self._current_row.add_buttons("Axis", "Button")
        self._current_row.subscribe(self._cm.set_setting_int, "handbrake-mode")
        self._current_row.subscribe(row.set_active)
        self._append_sub("handbrake-mode", self._current_row.set_value)

        self._add_row(row)
        self._current_row.add_marks(25, 50, 75)
        self._current_row.subscribe(self._cm.set_setting_int, "handbrake-button-threshold")
        self._append_sub("handbrake-mode", self._current_row.set_active)
        self._append_sub("handbrake-button-threshold", self._current_row.set_value)
        self._current_row.set_active(False)

        self.add_preferences_group("Range settings", level_bar=1)
        self._current_group.set_bar_max(65535)
        self._append_sub_hid(MozaAxis.HANDBRAKE, self._current_group.set_bar_level)

        self._curve_row = BoxflatEqRow("Output Curve", 5, suffix="%")
        self._add_row(self._curve_row)
        self._current_row.add_marks(20, 40, 60, 80)
        self._current_row.add_labels("20%", "40%", "60%", "80%", "100%")
        self._current_row.set_height(260)
        self._current_row.add_buttons("Linear", "S Curve", "Exponential", "Parabolic")
        self._current_row.set_button_value(-1)
        self._current_row.subscribe(self._set_curve_preset)
        for i in range(5):
            self._curve_row.subscribe_slider(i, self._set_curve_point, i)
            self._append_sub(f"handbrake-y{i+1}", self._get_curve, i)


        self._add_row(BoxflatSliderRow("Range Start", suffix="%"))
        self._current_row.add_marks(20, 40, 60, 80)
        self._current_row.set_slider_width(380)
        self._current_row.subscribe(self._cm.set_setting_int, "handbrake-min")
        # self._current_row.subscribe(self._current_group.set_range_start)
        self._append_sub("handbrake-min", self._current_row.set_value)

        self._add_row(BoxflatSliderRow("Range End", suffix="%", value=100))
        self._current_row.add_marks(20, 40, 60, 80)
        self._current_row.set_slider_width(380)
        self._current_row.subscribe(self._cm.set_setting_int, "handbrake-max")
        # self._current_row.subscribe(self._current_group.set_range_end)
        self._append_sub("handbrake-max", self._current_row.set_value)

        self.add_preferences_group("Calibration")
        self._add_row(BoxflatCalibrationRow("Handbrake Calibration", "Pull handbrake fully once"))
        self._current_row.subscribe(self._cm.set_setting_int, "handbrake")
        self._cm.subscribe_shutdown(self._current_row.shutdown)


    def _set_curve_preset(self, value: int) -> None:
        self._set_curve(self._presets[value])


    def _set_curve_point(self, value: int, index: int) -> None:
        self._cm.set_setting_float(float(value), f"handbrake-y{index+1}")


    def _set_curve(self, values: list) -> None:
        curve = []
        curve.extend(values)

        for i in range(0,5):
            self._cm.set_setting_float(curve[i], f"handbrake-y{i+1}")


    def _get_curve(self, value: int, sindex: int) -> None:
        index = -1
        values = self._curve_row.get_sliders_value()
        values[sindex] = value

        if values in self._presets:
            index = self._presets.index(values)

        self._curve_row.set_button_value(index)
        self._curve_row.set_slider_value(value, sindex)
