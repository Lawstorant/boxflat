from boxflat.panels.settings_panel import SettingsPanel
from boxflat.connection_manager import MozaConnectionManager

from boxflat.widgets import *
import time

class BaseSettings(SettingsPanel):
    def __init__(self, button_callback: callable, connection_manager: MozaConnectionManager) -> None:
        self._curve_row = None
        self._eq_row = None

        #          [x1, x2, x3, x4]
        self._curve_x = [20, 40, 60, 80]
        self._curve_presets = [
        #    y0 skipped as we can't change it's value
        #   [y1, y2, y3, y4, y5]
            [20, 40, 60, 80, 100], # Linear
            [ 8, 24, 76, 92, 100], # S Curve
            [35, 52, 60, 75, 100], # Inverted S
            [ 6, 14, 28, 54, 100], # Exponential
            [46, 72, 86, 94, 100]  # Parabolic
        ]

        # presets based on Road Sensitivity EQ settings
        self._eq_presets = [
            [100,  30,  10,   0,   0,   0],
            [100,  60,  20,   0,   0,   0],
            [100,  70,  40,  10,   0,   0],
            [100,  80,  50,  20,  10,   0],
            [100,  90,  60,  30,  20,   0],
            [100, 100,  70,  40,  30,   0],
            [100, 100,  90,  50,  40,   0],
            [100, 100, 100,  60,  60,   0],
            [100, 100, 100,  80,  80,   0],
            [100, 100, 100, 100, 100,   0],
            [100, 100, 100, 100, 100, 100]
        ]

        super().__init__("Base", button_callback, connection_manager)
        self._append_sub_connected("base-limit", self.active)

    def _set_rotation(self, value: int) -> None:
        self._cm.set_setting_int(value, "base-limit")
        self._cm.set_setting_int(value, "base-maximum-angle")

    def prepare_ui(self) -> None:
        self.add_view_stack()
        self.add_preferences_page("Base")
        self.add_preferences_group("Important settings")

        self._add_row(BoxflatSliderRow(
            "Wheel Rotation Angle",subtitle="Round and round", range_start=90, range_end=2700, big=True, draw_value=False))
        self._current_row.add_marks(360, 540, 720, 900, 1080, 1440, 1800, 2160)
        self._current_row.set_expression("/2")
        self._current_row.set_reverse_expression("*2")
        self._current_row.subscribe(self._set_rotation)
        self._append_sub("base-limit", self._current_row.set_value)

        self._add_row(BoxflatSliderRow("FFB Strength", suffix="%"))
        self._current_row.add_marks(25, 50, 75)
        self._current_row.set_expression("*10")
        self._current_row.set_reverse_expression("/10")
        self._current_row.subscribe(self._cm.set_setting_int, "base-ffb-strength")
        self._append_sub("base-ffb-strength", self._current_row.set_value)

        self._add_row(BoxflatSwitchRow("Force Feedback Enabled"))
        self._current_row.reverse_values()
        self._current_row.subscribe(self._cm.set_setting_int, "main-set-ffb-status")
        self._append_sub("main-get-ffb-status", self._current_row.set_value)

        self._add_row(BoxflatButtonRow("Adjust center point", "Center"))
        self._current_row.subscribe(self._cm.set_setting_int, "base-calibration")

        # Basic settings
        self.add_preferences_group("Basic settings")
        self._add_row(BoxflatSliderRow("Road Sensitivity", range_end=10))
        self._current_row.add_marks(2, 4, 6, 8)
        self._current_row.set_expression("*4 + 10")
        self._current_row.set_reverse_expression("/4 - 2.5")
        self._current_row.subscribe(self._cm.set_setting_int, "base-road-sensitivity")
        self._current_row.subscribe(self._set_eq_preset, raw=True)
        self._append_sub("base-road-sensitivity", self._current_row.set_value)

        self._add_row(BoxflatSliderRow("Maximum Wheel Speed", suffix="%", range_end=200))
        self._current_row.add_marks(50, 100, 150)
        self._current_row.set_expression("*10")
        self._current_row.set_reverse_expression("/10")
        self._current_row.subscribe(self._cm.set_setting_int, "base-speed")
        self._append_sub("base-speed", self._current_row.set_value)

        self._add_row(BoxflatSliderRow("Wheel Spring", suffix="%"))
        self._current_row.add_marks(50)
        self._current_row.set_expression("*10")
        self._current_row.set_reverse_expression("/10")
        self._current_row.subscribe(self._cm.set_setting_int, "base-spring")
        self._append_sub("base-spring", self._current_row.set_value)

        self._add_row(BoxflatSliderRow("Wheel Damper", suffix="%"))
        self._current_row.add_marks(10, 25, 50)
        self._current_row.set_expression("*10")
        self._current_row.set_reverse_expression("/10")
        self._current_row.subscribe(self._cm.set_setting_int, "base-damper")
        self._append_sub("base-damper", self._current_row.set_value)

        # Advenced settings
        self.add_preferences_group("Advenced Settings")
        self._add_row(BoxflatSwitchRow("Force Feedback Reversal"))
        self._current_row.subscribe(self._cm.set_setting_int, "base-ffb-reverse")
        self._append_sub("base-ffb-reverse", self._current_row.set_value)

        self._add_row(BoxflatSliderRow("Torque output", suffix="%"))
        self._current_row.add_marks(25, 50, 75)
        self._current_row.subscribe(self._cm.set_setting_int, "base-torque")
        self._append_sub("base-torque", self._current_row.set_value)

        slider = BoxflatSliderRow("Steering Wheel Inertia", range_start=100, range_end=4000)
        self._add_row(BoxflatSwitchRow("Hands-Off Protection"))
        self._current_row.subscribe(self._cm.set_setting_int, "base-natural-inertia-enable")
        self._current_row.subscribe(slider.set_active)
        self._append_sub("base-natural-inertia-enable", self._current_row.set_value)

        self._add_row(slider)
        self._current_row.add_marks(900, 1550, 2800, 3500)
        self._current_row.subscribe(self._cm.set_setting_int, "base-natural-inertia")
        self._append_sub("base-natural-inertia", self._current_row.set_value)
        self._append_sub("base-natural-inertia-enable", self._current_row.set_active)

        self._add_row(BoxflatSliderRow("Natural Inertia", range_start=100, range_end=500))
        self._current_row.add_marks(150, 300)
        self._current_row.subscribe(self._cm.set_setting_int, "base-inertia")
        self._append_sub("base-inertia", self._current_row.set_value)

        self._add_row(BoxflatSliderRow("Wheel Friction", suffix="%"))
        self._current_row.add_marks(10, 30)
        self._current_row.set_expression("*10")
        self._current_row.set_reverse_expression("/10")
        self._current_row.subscribe(self._cm.set_setting_int, "base-friction")
        self._append_sub("base-friction", self._current_row.set_value)

        self._add_row(BoxflatSliderRow("Speed-depended Damping", suffix="%"))
        self._current_row.add_marks(50)
        self._current_row.subscribe(self._cm.set_setting_int, "base-speed-damping")
        self._append_sub("base-speed-damping", self._current_row.set_value)

        self._add_row(BoxflatSliderRow("Speed-depended Damping", range_end=400, suffix=" kph"))
        self._current_row.add_marks(120)
        self._current_row.subscribe(self._cm.set_setting_int, "base-speed-damping-point")
        self._append_sub("base-speed-damping-point", self._current_row.set_value)

        # FFB Equalizer
        self.__prepare_eq()
        # FFB Curve
        self.__prepare_curve()

        # Even less important settings
        self.add_preferences_page("Misc", "preferences-other-symbolic")
        self.add_preferences_group("Misc Settings")

        self._add_row(BoxflatSwitchRow("Base Status Indicator"))
        self._current_row.set_subtitle("Does nothing if your base doesn't have it")
        self._current_row.subscribe(self._cm.set_setting_int, "main-set-led-status")
        self._append_sub("main-get-led-status", self._current_row.set_value)

        self._add_row(BoxflatSliderRow("Soft Limit Stiffness", range_start=1, range_end=10))
        self._current_row.add_marks(4, 6, 8)
        self._current_row.set_expression("*(400/9)-(400/9)+100")
        self._current_row.set_reverse_expression("/(400/9) - 2.25 + 1")
        self._current_row.subscribe(self._cm.set_setting_int, "base-soft-limit-stiffness")
        self._append_sub("base-soft-limit-stiffness", self._current_row.set_value)

        self._add_row(BoxflatToggleButtonRow("Soft Limit Strength"))
        self._current_row.add_buttons("Soft", "Middle", "Hard")
        self._current_row.set_expression("*22+56")
        self._current_row.set_reverse_expression("/22 - 2.5454")
        self._current_row.subscribe(self._cm.set_setting_int, "base-soft-limit-strength")
        self._append_sub("base-soft-limit-strength", self._current_row.set_value)

        self._add_row(BoxflatSwitchRow("Soft Limit Game Force Strength"))
        self._current_row.set_subtitle("I have no idea")
        self._current_row.subscribe(self._cm.set_setting_int, "base-soft-limit-retain")
        self._append_sub("base-soft-limit-retain", self._current_row.set_value)

        self._add_row(BoxflatToggleButtonRow("Temperature Control Strategy",))
        self._current_row.set_subtitle("Conservative = 50°C, Radical = 60°C")
        self._current_row.add_buttons("Conservative", "Radical")
        self._current_row.subscribe(self._cm.set_setting_int, "base-temp-strategy")
        self._append_sub("base-temp-strategy", self._current_row.set_value)


    def __prepare_eq(self) -> None:
        self.add_preferences_page("Equalizer", "network-cellular-signal-excellent-symbolic")

        self.add_preferences_group("Equalizer")
        self._eq_row = BoxflatEqRow("FFB Equalizer", 6,
            subtitle="Perfectly balanced, as all things should be", range_end=400, suffix="%", button_row=False)
        self._add_row(self._eq_row)
        self._current_row.add_marks(50, 100, 200, 300)
        self._current_row.add_labels("10Hz", "15Hz", "25Hz", "40Hz", "60Hz", "100Hz")
        self._current_row.set_height(450)
        for i in range(6):
            self._eq_row.subscribe_slider(i, self._cm.set_setting_int, f"base-equalizer{i+1}")
            self._append_sub(f"base-equalizer{i+1}", self._eq_row.set_slider_value, i)


    def __prepare_curve(self) -> None:
        self.add_preferences_page("Curve", "network-cellular-signal-excellent-symbolic")

        self.add_preferences_group("Base FFB Curve")
        self._curve_row = BoxflatEqRow("FFB Curve", 5, subtitle="Game FFB to Output FFB ratio", suffix="%")
        self._add_row(self._curve_row)
        self._current_row.add_marks(20, 40, 60, 80)
        self._current_row.add_labels("20%", "40%", "60%", "80%", "100%")

        self._current_row.add_buttons("Linear", "S Curve", "Inverted S", "Exponential", "Parabolic")
        self._current_row.set_button_value(-1)
        self._current_row.subscribe(self._set_curve_preset)
        for i in range(5):
            self._current_row.subscribe_slider(i, self._set_curve_point, i)
            self._append_sub(f"base-ffb-curve-y{i+1}", self._get_curve, i)


    def _set_curve_preset(self, value: int) -> None:
        self._set_curve(self._curve_presets[value])


    def _set_curve_point(self, value: int, index: int) -> None:
        self._cm.set_setting_int(value, f"base-ffb-curve-y{index+1}")


    def _set_curve(self, values: list) -> None:
        curve = []
        curve.extend(self._curve_x)
        curve.extend(values)

        for i in range(1,5):
            self._cm.set_setting_int(curve[i-1], f"base-ffb-curve-x{i}")

        for i in range(0,5):
            self._cm.set_setting_int(curve[i+4], f"base-ffb-curve-y{i+1}")


    def _get_curve(self, value: int, sindex: int) -> None:
        index = -1
        values = self._curve_row.get_sliders_value()
        values[sindex] = value

        if values in self._curve_presets:
            index = self._curve_presets.index(values)

        self._curve_row.set_button_value(index)
        self._curve_row.set_slider_value(value, sindex)


    def _set_eq_preset(self, index: int) -> None:
        print(index)
        for i in range(6):
            self._cm.set_setting_int(self._eq_presets[index][i], f"base-equalizer{i+1}")
