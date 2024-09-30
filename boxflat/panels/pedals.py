from boxflat.panels.settings_panel import SettingsPanel
from boxflat.connection_manager import MozaConnectionManager
from boxflat.widgets import *
from boxflat.hid_handler import MozaAxis

class PedalsSettings(SettingsPanel):
    def __init__(self, button_callback: callable, connection_manager: MozaConnectionManager, hid_handler) -> None:
        self._brake_calibration_row = None
        self._curve_rows = []

        self._presets = [
            [20, 40, 60, 80, 100], # Linear
            [ 8, 24, 76, 92, 100], # S Curve
            [ 6, 14, 28, 54, 100], # Exponential
            [46, 72, 86, 94, 100]  # Parabolic
        ]

        self._pedals = [
            "throttle",
            "brake",
            "clutch"
        ]

        super().__init__("Pedals", button_callback, connection_manager, hid_handler)
        self._append_sub_connected("pedals-throttle-dir", self.active)


    def set_brake_calibration_active(self, active: bool):
        self._brake_calibration_row.set_active(active)


    def prepare_ui(self) -> None:
        self.add_view_stack()

        # Throttle
        self.add_preferences_page("Throttle")
        self.add_preferences_group("Throttle settings", level_bar=1)
        self._current_group.set_bar_max(65534)
        self._append_sub_hid(MozaAxis.THROTTLE.name, self._current_group.set_bar_level)

        self._curve_rows.append(BoxflatEqRow("Throttle Curve", 5, suffix="%"))
        self._add_row(self._curve_rows[0])
        self._current_row.add_marks(20, 40, 60, 80)
        self._current_row.add_labels("20%", "40%", "60%", "80%", "100%")
        self._current_row.set_height(260)
        self._current_row.add_buttons("Linear", "S Curve", "Exponential", "Parabolic")
        # self._current_row.set_button_value(-1)
        self._current_row.subscribe(self._set_curve_preset, "throttle")
        for i in range(5):
            self._curve_rows[0].subscribe_slider(i, self._set_curve_point, i, "throttle")
            self._append_sub(f"pedals-throttle-y{i+1}", self._get_curve, i, "throttle")

        self._add_row(BoxflatSliderRow("Range Start", suffix="%"))
        self._current_row.add_marks(20, 40, 60, 80)
        self._current_row.set_slider_width(380)
        self._current_row.subscribe(self._cm.set_setting, "pedals-throttle-min")
        self._append_sub("pedals-throttle-min", self._current_row.set_value)

        self._add_row(BoxflatSliderRow("Range End", suffix="%"))
        self._current_row.add_marks(20, 40, 60, 80)
        self._current_row.set_slider_width(380)
        self._current_row.subscribe(self._cm.set_setting, "pedals-throttle-max")
        self._append_sub("pedals-throttle-max", self._current_row.set_value)

        self.add_preferences_group("Misc")
        self._add_row(BoxflatSwitchRow("Reverse Direction"))
        self._current_row.subscribe(self._cm.set_setting, "pedals-throttle-dir")
        self._append_sub("pedals-throttle-dir", self._current_row.set_value)

        self._add_row(BoxflatCalibrationRow("Calibration", "Fully depress throttle once"))
        self._current_row.subscribe("calibration-start", self._cm.set_setting, "pedals-throttle-calibration-start")
        self._current_row.subscribe("calibration-stop", self._cm.set_setting, "pedals-throttle-calibration-stop")

        # Brake
        self.add_preferences_page("Brake")
        self.add_preferences_group("Brake settings", level_bar=1)
        self._current_group.set_bar_max(65534)
        self._append_sub_hid(MozaAxis.BRAKE.name, self._current_group.set_bar_level)

        self._curve_rows.append(BoxflatEqRow("Brake Curve", 5, suffix="%"))
        self._add_row(self._curve_rows[1])
        self._current_row.add_marks(20, 40, 60, 80)
        self._current_row.add_labels("20%", "40%", "60%", "80%", "100%")
        self._current_row.set_height(260)
        self._current_row.add_buttons("Linear", "S Curve", "Exponential", "Parabolic")
        # self._current_row.set_button_value(-1)
        self._current_row.subscribe(self._set_curve_preset, "brake")
        for i in range(5):
            self._curve_rows[1].subscribe_slider(i, self._set_curve_point, i, "brake")
            self._append_sub(f"pedals-brake-y{i+1}", self._get_curve, i, "brake")

        self._add_row(BoxflatSliderRow("Range Start", suffix="%"))
        self._current_row.add_marks(20, 40, 60, 80)
        self._current_row.set_slider_width(380)
        self._current_row.subscribe(self._cm.set_setting, "pedals-brake-min")
        self._append_sub("pedals-brake-min", self._current_row.set_value)

        self._add_row(BoxflatSliderRow("Range End", suffix="%"))
        self._current_row.add_marks(20, 40, 60, 80)
        self._current_row.set_slider_width(380)
        self._current_row.subscribe(self._cm.set_setting, "pedals-brake-max")
        self._append_sub("pedals-brake-max", self._current_row.set_value)

        self._add_row(BoxflatSliderRow("Sensor ratio", suffix="%", subtitle="0% = Only Angle Sensor\n100% = Only Load Cell"))
        self._current_row.add_marks(25, 50, 75)
        self._current_row.subscribe(self._cm.set_setting, "pedals-brake-angle-ratio")
        self._append_sub("pedals-brake-angle-ratio", self._current_row.set_value)

        self.add_preferences_group("Misc")
        self._add_row(BoxflatSwitchRow("Reverse Direction"))
        self._current_row.subscribe(self._cm.set_setting, "pedals-brake-dir")
        self._append_sub("pedals-brake-dir", self._current_row.set_value)

        self._brake_calibration_row = BoxflatCalibrationRow("Calibration", "Fully depress brake once")
        self._add_row(self._brake_calibration_row)
        self._current_row.subscribe("calibration-start", self._cm.set_setting, "pedals-throttle-brake-start")
        self._current_row.subscribe("calibration-stop", self._cm.set_setting, "pedals-throttle-brake-stop")
        self._current_row.set_active(False)

        # Clutch
        self.add_preferences_page("Clutch")
        self.add_preferences_group("Clutch settings", level_bar=1)
        self._current_group.set_bar_max(65534)
        self._append_sub_hid(MozaAxis.CLUTCH.name, self._current_group.set_bar_level)

        self._curve_rows.append(BoxflatEqRow("Clutch Curve", 5, suffix="%"))
        self._add_row(self._curve_rows[2])
        self._current_row.add_marks(20, 40, 60, 80)
        self._current_row.add_labels("20%", "40%", "60%", "80%", "100%")
        self._current_row.set_height(260)
        self._current_row.add_buttons("Linear", "S Curve", "Exponential", "Parabolic")
        # self._current_row.set_button_value(-1)
        self._current_row.subscribe(self._set_curve_preset, "clutch")
        for i in range(5):
            self._curve_rows[2].subscribe_slider(i, self._set_curve_point, i, "clutch")
            self._append_sub(f"pedals-clutch-y{i+1}", self._get_curve, i, "clutch")

        self._add_row(BoxflatSliderRow("Range Start", suffix="%"))
        self._current_row.add_marks(20, 40, 60, 80)
        self._current_row.set_slider_width(380)
        self._current_row.subscribe(self._cm.set_setting, "pedals-clutch-min")
        self._append_sub("pedals-clutch-min", self._current_row.set_value)

        self._add_row(BoxflatSliderRow("Range End", suffix="%"))
        self._current_row.add_marks(20, 40, 60, 80)
        self._current_row.set_slider_width(380)
        self._current_row.subscribe(self._cm.set_setting, "pedals-clutch-max")
        self._append_sub("pedals-clutch-max", self._current_row.set_value)

        self.add_preferences_group("Misc")
        self._add_row(BoxflatSwitchRow("Reverse Direction"))
        self._current_row.subscribe(self._cm.set_setting, "pedals-clutch-dir")
        self._append_sub("pedals-clutch-dir", self._current_row.set_value)

        self._add_row(BoxflatCalibrationRow("Calibration", "Fully depress clutch once"))
        self._current_row.subscribe("calibration-start", self._cm.set_setting, "pedals-clutch-calibration-start")
        self._current_row.subscribe("calibration-stop", self._cm.set_setting, "pedals-clutch-calibration-stop")


    def _set_curve_preset(self, value: int, pedal: str) -> None:
        self._set_curve(self._presets[value], pedal)


    def _set_curve_point(self, value: int, index: int, pedal: str) -> None:
        self._cm.set_setting(value, f"pedals-{pedal}-y{index+1}")


    def _set_curve(self, values: list, pedal: str) -> None:
        curve = []
        curve.extend(values)

        for i in range(0,5):
            self._cm.set_setting(curve[i], f"pedals-{pedal}-y{i+1}")


    def _get_curve(self, value: int, sindex: int, pedal: str) -> None:
        index = -1
        pi = self._pedals.index(pedal)
        values = self._curve_rows[pi].get_sliders_value()
        values[sindex] = value

        if values in self._presets:
            index = self._presets.index(values)

        self._curve_rows[pi].set_button_value(index)
        self._curve_rows[pi].set_slider_value(value, sindex)
