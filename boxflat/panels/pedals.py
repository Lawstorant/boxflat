# Copyright (c) 2025, Tomasz Pakuła Using Arch BTW

from boxflat.panels.settings_panel import SettingsPanel
from boxflat.connection_manager import MozaConnectionManager
from boxflat.widgets import *
from boxflat.hid_handler import MozaAxis, AxisData

class PedalsSettings(SettingsPanel):
    def __init__(self, button_callback, connection_manager: MozaConnectionManager, hid_handler):
        self._brake_calibration_row = None
        self._curve_rows: dict[str, BoxflatEqRow] = {}

        self._presets = [
            [20, 40, 60, 80, 100], # Linear
            [ 8, 24, 76, 92, 100], # S Curve
            [ 6, 14, 28, 54, 100], # Exponential
            [46, 72, 86, 94, 100]  # Parabolic
        ]

        super().__init__("Pedals", button_callback, connection_manager, hid_handler)
        self._cm.subscribe_connected("pedals-throttle-dir", self.active)


    def set_brake_calibration_active(self, active: int):
        self._brake_calibration_row.set_active(active)


    def prepare_ui(self):
        self.add_view_stack()
        for pedal in [MozaAxis.THROTTLE, MozaAxis.BRAKE, MozaAxis.CLUTCH]:
            self._prepare_pedal(pedal)


    def _prepare_pedal(self, pedal: AxisData):
        self.add_preferences_page(pedal.name.title())
        self.add_preferences_group(f"{pedal.name.title()} Curve", level_bar=1)
        self._current_group.set_bar_max(65_534)
        self._hid_handler.subscribe(pedal.name, self._current_group.set_bar_level)

        self._curve_rows[pedal.name] = BoxflatEqRow("", 5, suffix="%")
        self._add_row(self._curve_rows[pedal.name])
        self._current_row.add_marks(20, 40, 60, 80)
        self._current_row.add_labels("20%", "40%", "60%", "80%", "100%")
        self._current_row.set_height(280)
        self._current_row.add_buttons("Linear", "S Curve", "Exponential", "Parabolic")
        # self._current_row.set_button_value(-1)
        self._curve_rows[pedal.name].set_height(290)
        self._current_row.subscribe(self._set_curve_preset, pedal.name)
        for i in range(5):
            self._curve_rows[pedal.name].subscribe_slider(i, self._set_curve_point, i, pedal.name)
            self._cm.subscribe(f"pedals-{pedal.name}-y{i+1}", self._get_curve, i, pedal.name)

        self.add_preferences_group(f"{pedal.name.title()} Range")
        self._add_row(BoxflatSliderRow("Range Start", suffix="%"))
        self._current_row.add_marks(20, 40, 60, 80)
        self._current_row.set_slider_width(380)
        self._current_row.subscribe(self._cm.set_setting, f"pedals-{pedal.name}-min")
        self._cm.subscribe(f"pedals-{pedal.name}-min", self._current_row.set_value)

        self._add_row(BoxflatSliderRow("Range End", suffix="%"))
        self._current_row.add_marks(20, 40, 60, 80)
        self._current_row.set_slider_width(380)
        self._current_row.subscribe(self._cm.set_setting, f"pedals-{pedal.name}-max")
        self._cm.subscribe(f"pedals-{pedal.name}-max", self._current_row.set_value)

        if pedal == MozaAxis.BRAKE:
            self._add_row(BoxflatSliderRow("Sensor ratio", suffix="%", subtitle="0% = Only Angle Sensor\n100% = Only Load Cell"))
            self._current_row.add_marks(25, 50, 75)
            self._current_row.subscribe(self._cm.set_setting, "pedals-brake-angle-ratio")
            self._cm.subscribe("pedals-brake-angle-ratio", self._current_row.set_value)

        self.add_preferences_group("Misc")
        self._add_row(BoxflatSwitchRow("Reverse Direction"))
        self._current_row.subscribe(self._cm.set_setting, f"pedals-{pedal.name}-dir")
        self._cm.subscribe(f"pedals-{pedal.name}-dir", self._current_row.set_value)

        self._add_row(BoxflatCalibrationRow("Calibration", f"Fully depress {pedal.name} once"))
        self._current_row.subscribe("calibration-start", self._cm.set_setting, f"pedals-{pedal.name}-calibration-start", True)
        self._current_row.subscribe("calibration-stop", self._cm.set_setting, f"pedals-{pedal.name}-calibration-stop", True)
        if pedal == MozaAxis.BRAKE:
            self._brake_calibration_row = self._current_row


    def _set_curve_preset(self, value: int, pedal: str):
        self._set_curve(self._presets[value], pedal)


    def _set_curve_point(self, value: int, index: int, pedal: str):
        self._cm.set_setting(value, f"pedals-{pedal}-y{index+1}")


    def _set_curve(self, values: list, pedal: str):
        self._curve_rows[pedal].set_sliders_value(values, mute=False)


    def _get_curve(self, value: int, sindex: int, pedal: str):
        index = -1
        row = self._curve_rows[pedal]

        values = row.get_sliders_value()
        values[sindex] = value

        if values in self._presets:
            index = self._presets.index(values)

        row.set_button_value(index)
        row.set_slider_value(value, sindex)
