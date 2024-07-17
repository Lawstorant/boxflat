from boxflat.panels.settings_panel import SettingsPanel
from boxflat.connection_manager import MozaConnectionManager

from boxflat.widgets import *
import time

class BaseSettings(SettingsPanel):
    def __init__(self, button_callback: callable, connection_manager: MozaConnectionManager) -> None:
        self._curve_row = None
        super(BaseSettings, self).__init__("Base", button_callback, connection_manager)

    def _set_rotation(self, value: int) -> None:
        self._cm.set_setting("base-limit", value)
        self._cm.set_setting("base-maximum-angle", value)

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
        self._cm.subscribe("base-limit", self._current_row.set_value)

        self._add_row(BoxflatSliderRow("FFB Strength", suffix="%"))
        self._current_row.add_marks(25, 50, 75)
        self._current_row.set_expression("*10")
        self._current_row.set_reverse_expression("/10")
        self._current_row.subscribe(lambda v: self._cm.set_setting("base-ffb-strength", v))
        self._cm.subscribe("base-ffb-strength", self._current_row.set_value)

        self._add_row(BoxflatSwitchRow("Force Feedback Enabled"))
        self._current_row.reverse_values()
        self._current_row.subscribe(lambda v: self._cm.set_setting("main-set-ffb-status", v))
        self._cm.subscribe("main-get-ffb-status", self._current_row.set_value)

        self._add_row(BoxflatButtonRow("Adjust center point", "Center"))
        self._current_row.subscribe(lambda v: self._cm.set_setting("base-calibration", 1))

        # Basic settings
        self.add_preferences_group("Basic settings")
        self._add_row(BoxflatSliderRow("Road Sensitivity", range_end=10))
        self._current_row.add_marks(2, 4, 6, 8)
        self._current_row.set_expression("*4 + 10")
        self._current_row.set_reverse_expression("/4 - 2.5")
        self._current_row.subscribe(lambda v: self._cm.set_setting("base-road-sensitivity", v))
        self._cm.subscribe("base-road-sensitivity", self._current_row.set_value)

        self._add_row(BoxflatSliderRow("Maximum Wheel Speed", suffix="%", range_end=200))
        self._current_row.add_marks(50, 100, 150)
        self._current_row.set_expression("*10")
        self._current_row.set_reverse_expression("/10")
        self._current_row.subscribe(lambda v: self._cm.set_setting("base-speed", v))
        self._cm.subscribe("base-speed", self._current_row.set_value)

        self._add_row(BoxflatSliderRow("Wheel Spring", suffix="%"))
        self._current_row.add_marks(50)
        self._current_row.set_expression("*10")
        self._current_row.set_reverse_expression("/10")
        self._current_row.subscribe(lambda v: self._cm.set_setting("base-spring", v))
        self._cm.subscribe("base-spring", self._current_row.set_value)

        self._add_row(BoxflatSliderRow("Wheel Damper", suffix="%"))
        self._current_row.add_marks(10, 25, 50)
        self._current_row.set_expression("*10")
        self._current_row.set_reverse_expression("/10")
        self._current_row.subscribe(lambda v: self._cm.set_setting("base-damper", v))
        self._cm.subscribe("base-damper", self._current_row.set_value)

        # Advenced settings
        self.add_preferences_group("Advenced Settings")
        self._add_row(BoxflatSwitchRow("Force Feedback Reversal"))
        self._current_row.subscribe(lambda v: self._cm.set_setting("base-ffb-reverse", v))
        self._cm.subscribe("base-ffb-reverse", self._current_row.set_value)

        self._add_row(BoxflatSliderRow("Torque output", suffix="%"))
        self._current_row.add_marks(25, 50, 75)
        self._current_row.subscribe(lambda v: self._cm.set_setting("base-torque", v))
        self._cm.subscribe("base-torque", self._current_row.set_value)

        slider = BoxflatSliderRow("Steering Wheel Inertia", range_start=100, range_end=4000)
        self._add_row(BoxflatSwitchRow("Hands-Off Protection"))
        self._current_row.subscribe(lambda v: self._cm.set_setting("base-natural-inertia-enable", v))
        self._current_row.subscribe(slider.set_active)
        self._cm.subscribe("base-natural-inertia-enable", self._current_row.set_value)

        self._add_row(slider)
        self._current_row.add_marks(900, 1550, 2800, 3500)
        self._current_row.subscribe(lambda v: self._cm.set_setting("base-natural-inertia", v))
        self._cm.subscribe("base-natural-inertia", self._current_row.set_value)
        self._cm.subscribe("base-natural-inertia-enable", self._current_row.set_active)

        self._add_row(BoxflatSliderRow("Natural Inertia", range_start=100, range_end=500))
        self._current_row.add_marks(150, 300)
        self._current_row.subscribe(lambda v: self._cm.set_setting("base-inertia", v))
        self._cm.subscribe("base-inertia", self._current_row.set_value)

        self._add_row(BoxflatSliderRow("Wheel Friction", suffix="%"))
        self._current_row.add_marks(10, 30)
        self._current_row.set_expression("*10")
        self._current_row.set_reverse_expression("/10")
        self._current_row.subscribe(lambda v: self._cm.set_setting("base-friction", v))
        self._cm.subscribe("base-friction", self._current_row.set_value)

        self._add_row(BoxflatSliderRow("Speed-depended Damping", suffix="%"))
        self._current_row.add_marks(50)
        self._current_row.subscribe(lambda v: self._cm.set_setting("base-speed-damping", v))
        self._cm.subscribe("base-speed-damping", self._current_row.set_value)

        self._add_row(BoxflatSliderRow("Speed-depended Damping", range_end=400, suffix=" kph"))
        self._current_row.add_marks(120)
        self._current_row.subscribe(lambda v: self._cm.set_setting("base-speed-damping-point", v))
        self._cm.subscribe("base-speed-damping-point", self._current_row.set_value)

        # FFB Equalizer
        self.__prepare_eq()
        # FFB Curve
        self.__prepare_curve()

        # Even less important settings
        self.add_preferences_page("Misc", "preferences-other-symbolic")
        self.add_preferences_group("Misc Settings")

        self._add_row(BoxflatSwitchRow("Base Status Indicator"))
        self._current_row.set_subtitle("Does nothing if your base doesn't have it")
        self._current_row.subscribe(lambda v: self._cm.set_setting("main-set-led-status", v))
        self._cm.subscribe("main-get-led-status", self._current_row.set_value)

        self._add_row(BoxflatSliderRow("Soft Limit Stiffness", range_start=1, range_end=10))
        self._current_row.add_marks(4, 6, 8)
        self._current_row.set_expression("*(400/9)-(400/9)+100")
        self._current_row.set_reverse_expression("/(400/9) - 2.25 + 1")
        self._current_row.subscribe(lambda v: self._cm.set_setting("base-soft-limit-stiffness", v))
        self._cm.subscribe("base-soft-limit-stiffness", self._current_row.set_value)

        self._add_row(BoxflatToggleButtonRow("Soft Limit Strength"))
        self._current_row.add_buttons("Soft", "Middle", "Hard")
        self._current_row.set_expression("*22+56")
        self._current_row.set_reverse_expression("/22 - 2.5454")
        self._current_row.subscribe(lambda v: self._cm.set_setting("base-soft-limit-strength", v))
        self._cm.subscribe("base-soft-limit-strength", self._current_row.set_value)

        self._add_row(BoxflatSwitchRow("Soft Limit Game Force Strength"))
        self._current_row.set_subtitle("I have no idea")
        self._current_row.subscribe(lambda v: self._cm.set_setting("base-soft-limit-retain", v))
        self._cm.subscribe("base-soft-limit-retain", self._current_row.set_value)

        self._add_row(BoxflatToggleButtonRow("Temperature Control Strategy",))
        self._current_row.set_subtitle("Conservative = 50°C, Radical = 60°C")
        self._current_row.add_buttons("Conservative", "Radical")
        self._current_row.subscribe(lambda v: self._cm.set_setting("base-temp-strategy", v))
        self._cm.subscribe("base-temp-strategy", self._current_row.set_value)


    def __prepare_eq(self) -> None:
        self.add_preferences_page("Equalizer", "network-cellular-signal-excellent-symbolic")
        self.add_preferences_group()
        self._add_row(BoxflatRow("Page inactive", "UI Concept"))

        self.add_preferences_group("Equalizer")
        self._add_row(BoxflatEqRow("FFB Equalizer", 6,
            subtitle="Perfectly balanced, as all things should be", range_end=500, suffix="%"))
        self._current_row.add_marks(50, 100, 200, 350)
        self._current_row.add_labels("10Hz", "15Hz", "25Hz", "40Hz", "60Hz", "100Hz")
        self._current_row.set_height(450)


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
            self._current_row.subscribe_slider(i, self._set_curve_point)
        self._cm.subscribe(f"base-ffb-curve-y1", lambda v: self._get_curve(0, v))
        self._cm.subscribe(f"base-ffb-curve-y2", lambda v: self._get_curve(1, v))
        self._cm.subscribe(f"base-ffb-curve-y3", lambda v: self._get_curve(2, v))
        self._cm.subscribe(f"base-ffb-curve-y4", lambda v: self._get_curve(3, v))
        self._cm.subscribe(f"base-ffb-curve-y5", lambda v: self._get_curve(4, v))


    def _set_curve_preset(self, value: int) -> None:
        self._set_curve(self._curve_presets[value])


    def _set_curve_point(self, index: int, value: int) -> None:
        self._cm.set_setting(f"base-ffb-curve-y{index+1}", value)


    def _set_curve(self, values: list) -> None:
        curve = []
        curve.extend(self._curve_x)
        curve.extend(values)

        for i in range(1,5):
            self._cm.set_setting(f"base-ffb-curve-x{i}", curve[i-1])

        for i in range(0,5):
            self._cm.set_setting(f"base-ffb-curve-y{i+1}", curve[i+4])


    def _get_curve(self, sindex: int, value: int) -> None:
        index = -1
        values = self._curve_row.get_sliders_value()
        values[sindex] = value

        if values in self._curve_presets:
            index = self._curve_presets.index(values)

        self._curve_row.set_button_value(index)
        print(f"{sindex} {value}")
        self._curve_row.set_slider_value(sindex, value)

    #          [x1, x2, x3, x4]
    _curve_x = [20, 40, 60, 80]
    _curve_presets = [
    #    y0 skipped as we can't change it's value
    #   [y1, y2, y3, y4, y5]
        [20, 40, 60, 80, 100], # Linear
        [ 8, 24, 76, 92, 100], # S Curve
        [35, 52, 60, 75, 100], # Inverted S
        [ 6, 14, 28, 54, 100], # Exponential
        [46, 72, 86, 94, 100]  # Parabolic
    ]
