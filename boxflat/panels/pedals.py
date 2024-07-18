from boxflat.panels.settings_panel import SettingsPanel
from boxflat.connection_manager import MozaConnectionManager
from boxflat.widgets import *

class PedalsSettings(SettingsPanel):
    def __init__(self, button_callback: callable, connection_manager: MozaConnectionManager) -> None:
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

        super(PedalsSettings, self).__init__("Pedals", button_callback, connection_manager)


    def set_brake_calibration_active(self, active: bool):
        self._brake_calibration_row.set_active(active)


    def prepare_ui(self) -> None:
        self.add_view_stack()

        # Throttle
        self.add_preferences_page("Throttle")
        self.add_preferences_group("Throttle settings", level_bar=1)
        self._current_group.set_bar_max(65535)
        self._cm.subscribe_cont("pedals-throttle-output", self._current_group.set_bar_level)
        self._cm.subscribe("pedals-throttle-min", self._current_group.set_range_start)
        self._cm.subscribe("pedals-throttle-max", self._current_group.set_range_end)

        self._curve_rows.append(BoxflatEqRow("Throttle Curve", 5, suffix="%"))
        self._add_row(self._curve_rows[0])
        self._current_row.add_marks(20, 40, 60, 80)
        self._current_row.add_labels("20%", "40%", "60%", "80%", "100%")
        self._current_row.set_height(260)
        self._current_row.add_buttons("Linear", "S Curve", "Exponential", "Parabolic")
        self._current_row.set_button_value(-1)
        self._current_row.subscribe(self._set_curve_preset, "throttle")
        for i in range(5):
            self._curve_rows[0].subscribe_slider(i, self._set_curve_point, i, "throttle")
        self._cm.subscribe(f"pedals-throttle-y1", self._get_curve, 0, "throttle")
        self._cm.subscribe(f"pedals-throttle-y2", self._get_curve, 1, "throttle")
        self._cm.subscribe(f"pedals-throttle-y3", self._get_curve, 2, "throttle")
        self._cm.subscribe(f"pedals-throttle-y4", self._get_curve, 3, "throttle")
        self._cm.subscribe(f"pedals-throttle-y5", self._get_curve, 4, "throttle")

        self._add_row(BoxflatSliderRow("Range Start", suffix="%"))
        self._current_row.add_marks(20, 40, 60, 80)
        self._current_row.set_width(380)
        self._current_row.subscribe(self._cm.set_setting_int, "pedals-throttle-min")
        self._cm.subscribe("pedals-throttle-min", self._current_row.set_value)

        self._add_row(BoxflatSliderRow("Range End", suffix="%"))
        self._current_row.add_marks(20, 40, 60, 80)
        self._current_row.set_width(380)
        self._current_row.subscribe(self._cm.set_setting_int, "pedals-throttle-max")
        self._cm.subscribe("pedals-throttle-max", self._current_row.set_value)

        self.add_preferences_group("Misc")
        self._add_row(BoxflatSwitchRow("Reverse Direction"))
        self._current_row.subscribe(self._cm.set_setting_int, "pedals-throttle-dir")
        self._cm.subscribe("pedals-throttle-dir", self._current_row.set_value)

        self._add_row(BoxflatCalibrationRow("Calibration", "Set range"))
        self._current_row.subscribe(self._cm.set_setting_int, "pedals-throttle")

        # Brake
        self.add_preferences_page("Brake")
        self.add_preferences_group("Brake settings", level_bar=1)
        self._current_group.set_bar_max(65535)
        self._cm.subscribe_cont("pedals-brake-output", self._current_group.set_bar_level)
        self._cm.subscribe("pedals-brake-min", self._current_group.set_range_start)
        self._cm.subscribe("pedals-brake-max", self._current_group.set_range_end)

        self._curve_rows.append(BoxflatEqRow("Brake Curve", 5, suffix="%"))
        self._add_row(self._curve_rows[1])
        self._current_row.add_marks(20, 40, 60, 80)
        self._current_row.add_labels("20%", "40%", "60%", "80%", "100%")
        self._current_row.set_height(260)
        self._current_row.add_buttons("Linear", "S Curve", "Exponential", "Parabolic")
        self._current_row.set_button_value(-1)
        self._current_row.subscribe(self._set_curve_preset, "brake")
        for i in range(5):
            self._curve_rows[1].subscribe_slider(i, self._set_curve_point, i, "brake")
        self._cm.subscribe(f"pedals-brake-y1", self._get_curve, 0, "brake")
        self._cm.subscribe(f"pedals-brake-y2", self._get_curve, 1, "brake")
        self._cm.subscribe(f"pedals-brake-y3", self._get_curve, 2, "brake")
        self._cm.subscribe(f"pedals-brake-y4", self._get_curve, 3, "brake")
        self._cm.subscribe(f"pedals-brake-y5", self._get_curve, 4, "brake")

        self._add_row(BoxflatSliderRow("Range Start", suffix="%"))
        self._current_row.add_marks(20, 40, 60, 80)
        self._current_row.set_width(380)
        self._current_row.subscribe(self._cm.set_setting_int, "pedals-brake-min")
        self._cm.subscribe("pedals-brake-min", self._current_row.set_value)

        self._add_row(BoxflatSliderRow("Range End", suffix="%"))
        self._current_row.add_marks(20, 40, 60, 80)
        self._current_row.set_width(380)
        self._current_row.subscribe(self._cm.set_setting_int, "pedals-brake-max")
        self._cm.subscribe("pedals-brake-max", self._current_row.set_value)

        self._add_row(BoxflatSliderRow("Pressure Point Setting", suffix="%", subtitle="Higher = less range"))
        self._current_row.add_marks(25, 50, 75)
        self._current_row.subscribe(self._cm.set_setting_float, "pedals-brake-max-force")
        self._cm.subscribe("pedals-brake-max-force", self._current_row.set_value)

        self.add_preferences_group("Misc")
        self._add_row(BoxflatSwitchRow("Reverse Direction"))
        self._current_row.subscribe(self._cm.set_setting_int, "pedals-brake-dir")
        self._cm.subscribe("pedals-brake-dir", self._current_row.set_value)

        self._brake_calibration_row = BoxflatCalibrationRow("Calibration", "Set range")
        self._add_row(self._brake_calibration_row)
        self._current_row.subscribe(self._cm.set_setting_int, "pedals-brake")
        self._current_row.set_active(False)

        # Clutch
        self.add_preferences_page("Clutch")
        self.add_preferences_group("Clutch settings", level_bar=1)
        self._current_group.set_bar_max(65535)
        self._cm.subscribe_cont("pedals-clutch-output", self._current_group.set_bar_level)
        self._cm.subscribe("pedals-clutch-min", self._current_group.set_range_start)
        self._cm.subscribe("pedals-clutch-max", self._current_group.set_range_end)

        self._curve_rows.append(BoxflatEqRow("Clutch Curve", 5, suffix="%"))
        self._add_row(self._curve_rows[2])
        self._current_row.add_marks(20, 40, 60, 80)
        self._current_row.add_labels("20%", "40%", "60%", "80%", "100%")
        self._current_row.set_height(260)
        self._current_row.add_buttons("Linear", "S Curve", "Exponential", "Parabolic")
        self._current_row.set_button_value(-1)
        self._current_row.subscribe(self._set_curve_preset, "clutch")
        for i in range(5):
            self._curve_rows[2].subscribe_slider(i, self._set_curve_point, i, "clutch")
        self._cm.subscribe(f"pedals-clutch-y1", self._get_curve, 0, "clutch")
        self._cm.subscribe(f"pedals-clutch-y2", self._get_curve, 1, "clutch")
        self._cm.subscribe(f"pedals-clutch-y3", self._get_curve, 2, "clutch")
        self._cm.subscribe(f"pedals-clutch-y4", self._get_curve, 3, "clutch")
        self._cm.subscribe(f"pedals-clutch-y5", self._get_curve, 4, "clutch")

        self._add_row(BoxflatSliderRow("Range Start", suffix="%"))
        self._current_row.add_marks(20, 40, 60, 80)
        self._current_row.set_width(380)
        self._current_row.subscribe(self._cm.set_setting_int, "pedals-clutch-min")
        self._cm.subscribe("pedals-clutch-min", self._current_row.set_value)

        self._add_row(BoxflatSliderRow("Range End", suffix="%"))
        self._current_row.add_marks(20, 40, 60, 80)
        self._current_row.set_width(380)
        self._current_row.subscribe(self._cm.set_setting_int, "pedals-clutch-max")
        self._cm.subscribe("pedals-clutch-max", self._current_row.set_value)

        self.add_preferences_group("Misc")
        self._add_row(BoxflatSwitchRow("Reverse Direction"))
        self._current_row.subscribe(self._cm.set_setting_int, "pedals-clutch-dir")
        self._cm.subscribe("pedals-clutch-dir", self._current_row.set_value)

        self._add_row(BoxflatCalibrationRow("Calibration", "Set range"))
        self._current_row.subscribe(self._cm.set_setting_int, "pedals-clutch")


    def _set_curve_preset(self, value: int, pedal: str) -> None:
        self._set_curve(self._presets[value], pedal)


    def _set_curve_point(self, value: int, index: int, pedal: str) -> None:
        self._cm.set_setting_float(value, f"pedals-{pedal}-y{index+1}")


    def _set_curve(self, values: list, pedal: str) -> None:
        curve = []
        curve.extend(values)

        for i in range(0,5):
            self._cm.set_setting_float(curve[i], f"pedals-{pedal}-y{i+1}")


    def _get_curve(self, value: int, sindex: int, pedal: str) -> None:
        index = -1
        pi = self._pedals.index(pedal)
        values = self._curve_rows[pi].get_sliders_value()
        values[sindex] = value

        if values in self._presets:
            index = self._presets.index(values)

        self._curve_rows[pi].set_button_value(index)
        self._curve_rows[pi].set_slider_value(sindex, value)
