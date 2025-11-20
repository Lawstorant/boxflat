# Copyright (c) 2025, Tomasz Pakuła Using Arch BTW

from boxflat.panels.settings_panel import SettingsPanel
from boxflat.connection_manager import MozaConnectionManager

from boxflat.hid_handler import MozaAxis, MozaHidDevice

from boxflat.widgets import *
import time

class BaseSettings(SettingsPanel):
    def __init__(self, button_callback, connection_manager: MozaConnectionManager, hid_handler):
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

        super().__init__("Base", button_callback, connection_manager, hid_handler)
        self._cm.subscribe_connected("base-limit", self.active)


    def _set_rotation(self, value: int):
        self._cm.set_setting(value, "base-limit")
        self._cm.set_setting(value, "base-max-angle")


    def prepare_ui(self):
        self.add_view_stack()
        self.add_preferences_page("Base")
        self.add_preferences_group("Core settings", alt_level_bar=True)
        self._current_group.set_bar_max(32767)
        self._current_group.set_offset(-32767)
        self._hid_handler.subscribe(MozaAxis.STEERING.name, self._current_group.set_alt_bar_level)

        self._add_row(BoxflatSliderRow(
            "Wheel Rotation Angle",subtitle="Round and round", range_start=90, range_end=2700, big=True, draw_value=False))
        self._current_row.add_marks(360, 540, 720, 900, 1080, 1440, 1800, 2160)
        self._current_row.add_mark(2520, "2520  ")
        self._current_row.set_expression("/2")
        self._current_row.set_reverse_expression("*2")
        self._current_row.subscribe(self._set_rotation)
        self._cm.subscribe("base-limit", self._current_row.set_value)

        self._add_row(BoxflatButtonRow("Adjust center point", "Center"))
        self._current_row.subscribe(self._cm.set_setting, "base-calibration")

        self._add_row(BoxflatSwitchRow("Standby mode"))
        # self._current_row.reverse_values()
        self._current_row.subscribe(self._cm.set_setting, "main-set-work-mode")
        self._cm.subscribe("main-get-work-mode", self._current_row.set_value)

        self._add_row(BoxflatSwitchRow("Force Feedback", subtitle="E-Stop override"))
        self._current_row.reverse_values()
        self._current_row.subscribe(self._cm.set_setting, "base-ffb-disable")
        self._cm.subscribe("base-ffb-disable", self._current_row.set_value)
        self._cm.subscribe_connected("estop-get-status", self._current_row.set_present, 1)

        # Basic settings
        self.add_preferences_group("Basic settings")
        self._add_row(BoxflatSliderRow("Base torque output", suffix="%"))
        self._current_row.add_marks(25, 50, 75)
        self._current_row.subscribe(self._cm.set_setting, "base-torque")
        self._cm.subscribe("base-torque", self._current_row.set_value)

        self._add_row(BoxflatSliderRow("Game FFB strength", suffix="%"))
        self._current_row.add_marks(25, 50, 75)
        self._current_row.set_expression("*10")
        self._current_row.set_reverse_expression("/10")
        self._current_row.subscribe(self._cm.set_setting, "base-ffb-strength")
        self._cm.subscribe("base-ffb-strength", self._current_row.set_value)

        self._add_row(BoxflatSliderRow("Maximum Wheel Speed", suffix="%", range_end=200))
        self._current_row.add_marks(50, 100, 150)
        self._current_row.set_expression("*10")
        self._current_row.set_reverse_expression("/10")
        self._current_row.subscribe(self._cm.set_setting, "base-speed")
        self._cm.subscribe("base-speed", self._current_row.set_value)


        self.add_preferences_group("Protection")
        slider = BoxflatSliderRow("Steering Wheel Inertia", range_start=100, range_end=4000, increment=50)
        mode = BoxflatToggleButtonRow("Protection Mode")

        self._add_row(BoxflatSwitchRow("Hands-Off Protection"))
        self._current_row.subscribe(self._cm.set_setting, "base-protection")
        self._current_row.subscribe(slider.set_active)
        self._current_row.subscribe(mode.set_active)
        self._cm.subscribe("base-protection", self._current_row.set_value)

        self._add_row(mode)
        self._current_row.add_buttons("Mode 1", "Mode 2")
        self._current_row.set_expression("+1")
        self._current_row.set_reverse_expression("-1")
        self._current_row.subscribe(self._cm.set_setting, "base-protection-mode")
        self._cm.subscribe("base-protection-mode", self._current_row.set_value)
        self._cm.subscribe("base-protection", self._current_row.set_active)

        self._add_row(slider)
        self._current_row.add_mark(1100, "KS/GS  ")
        self._current_row.add_mark(1550, "ES")
        self._current_row.add_mark(2800, "CS/RS")
        self._current_row.add_mark(3500, "TSW  ")
        self._current_row.subscribe(self._cm.set_setting, "base-natural-inertia")
        self._cm.subscribe("base-natural-inertia", self._current_row.set_value)
        self._cm.subscribe("base-protection", self._current_row.set_active)

        self.add_preferences_group("High Speed Damping")
        self._add_row(BoxflatSliderRow("Damping Level", suffix="%"))
        self._current_row.add_marks(50)
        self._current_row.subscribe(self._cm.set_setting, "base-speed-damping")
        self._cm.subscribe("base-speed-damping", self._current_row.set_value)

        self._add_row(BoxflatSliderRow("Trigger Speed", range_end=400, suffix=" kph   "))
        self._current_row.add_marks(120)
        self._current_row.subscribe(self._cm.set_setting, "base-speed-damping-point")
        self._cm.subscribe("base-speed-damping-point", self._current_row.set_value)

        self.add_preferences_page("Effects")
        self.add_preferences_group("Wheelbase Effects")

        self._add_row(BoxflatSliderRow("Wheel Damper", suffix="%"))
        self._current_row.add_marks(10, 25, 50)
        self._current_row.set_expression("*10")
        self._current_row.set_reverse_expression("/10")
        self._current_row.subscribe(self._cm.set_setting, "base-damper")
        self._cm.subscribe("base-damper", self._current_row.set_value)

        self._add_row(BoxflatSliderRow("Wheel Friction", suffix="%"))
        self._current_row.add_marks(10, 30)
        self._current_row.set_expression("*10")
        self._current_row.set_reverse_expression("/10")
        self._current_row.subscribe(self._cm.set_setting, "base-friction")
        self._cm.subscribe("base-friction", self._current_row.set_value)

        self._add_row(BoxflatSliderRow("Natural Inertia", range_start=100, range_end=500, increment=50))
        self._current_row.add_marks(150, 300)
        self._current_row.set_expression("*10")
        self._current_row.set_reverse_expression("/10")
        self._current_row.subscribe(self._cm.set_setting, "base-inertia")
        self._cm.subscribe("base-inertia", self._current_row.set_value)

        self._add_row(BoxflatSliderRow("Wheel Spring", suffix="%"))
        self._current_row.add_marks(50)
        self._current_row.set_expression("*10")
        self._current_row.set_reverse_expression("/10")
        self._current_row.subscribe(self._cm.set_setting, "base-spring")
        self._cm.subscribe("base-spring", self._current_row.set_value)

        self.add_preferences_group("Game Effects")
        self._add_row(BoxflatSliderRow("Game Damper", subtitle="Default = 50%", increment=5, suffix="%"))
        self._current_row.add_marks(25, 50, 75)
        self._current_row.set_expression("*2.55")
        self._current_row.set_reverse_expression("/2.55")
        self._current_row.subscribe(self._cm.set_setting, "main-set-damper-gain")
        self._cm.subscribe("main-get-damper-gain", self._current_row.set_value)

        self._add_row(BoxflatSliderRow("Game Friction", subtitle="Default = 50%", increment=5, suffix="%"))
        self._current_row.add_marks(25, 50, 75)
        self._current_row.set_expression("*2.55")
        self._current_row.set_reverse_expression("/2.55")
        self._current_row.subscribe(self._cm.set_setting, "main-set-friction-gain")
        self._cm.subscribe("main-get-friction-gain", self._current_row.set_value)

        self._add_row(BoxflatSliderRow("Game Inertia", subtitle="Default = 50%", increment=5, suffix="%"))
        self._current_row.add_marks(25, 50, 75)
        self._current_row.set_expression("*2.55")
        self._current_row.set_reverse_expression("/2.55")
        self._current_row.subscribe(self._cm.set_setting, "main-set-inertia-gain")
        self._cm.subscribe("main-get-inertia-gain", self._current_row.set_value)

        self._add_row(BoxflatSliderRow("Game Spring", subtitle="Default = 100%", increment=5, suffix="%"))
        self._current_row.add_marks(25, 50, 75)
        self._current_row.set_expression("*2.55")
        self._current_row.set_reverse_expression("/2.55")
        self._current_row.subscribe(self._cm.set_setting, "main-set-spring-gain")
        self._cm.subscribe("main-get-spring-gain", self._current_row.set_value)

        # FFB Equalizer
        self.__prepare_eq()
        # FFB Curve
        self.__prepare_curve()

        # Even less important settings
        self.add_preferences_page("Misc", "preferences-other-symbolic")
        self.add_preferences_group("Soft limit")

        self._add_row(BoxflatSliderRow("Soft Limit Stiffness", range_start=1, range_end=10))
        self._current_row.add_marks(4, 6, 8)
        self._current_row.set_expression("*(400/9)-(400/9)+100")
        self._current_row.set_reverse_expression("/(400/9) - 2.25 + 1")
        self._current_row.subscribe(self._cm.set_setting, "base-soft-limit-stiffness")
        self._cm.subscribe("base-soft-limit-stiffness", self._current_row.set_value)

        self._add_row(BoxflatToggleButtonRow("Soft Limit Strength"))
        self._current_row.add_buttons("Soft", "Middle", "Hard")
        self._current_row.set_expression("*22+56")
        self._current_row.set_reverse_expression("/22 - 2.5454")
        self._current_row.subscribe(self._cm.set_setting, "base-soft-limit-strength")
        self._cm.subscribe("base-soft-limit-strength", self._current_row.set_value)

        self._add_row(BoxflatSwitchRow("Soft Limit Retain Game FFB"))
        self._current_row.subscribe(self._cm.set_setting, "base-soft-limit-retain")
        self._cm.subscribe("base-soft-limit-retain", self._current_row.set_value)

        self.add_preferences_group("Misc")
        self._add_row(BoxflatSwitchRow("Base Status Indicator"))
        self._current_row.set_subtitle("Does nothing if your base doesn't have it")
        self._current_row.subscribe(self._cm.set_setting, "main-set-led-status")
        self._cm.subscribe("main-get-led-status", self._current_row.set_value)

        # self._add_row(BoxflatSwitchRow("Default Work Mode State"))
        # self._current_row.reverse_values()
        # self._current_row.subscribe(self._cm.set_setting, "main-set-default-ffb-status")
        # self._cm.subscribe("main-get-default-ffb-status", self._current_row.set_value)

        self._add_row(BoxflatToggleButtonRow("Temperature Control Strategy",))
        self._current_row.set_subtitle("Conservative = 50°C, Radical = 60°C")
        self._current_row.add_buttons("Conservative", "Radical")
        self._current_row.subscribe(self._cm.set_setting, "base-temp-strategy")
        self._cm.subscribe("base-temp-strategy", self._current_row.set_value)

        tmp1 = BoxflatComboRow("Select music")
        tmp1.set_active(0)
        for i in range(10):
            tmp1.add_entry(f"Music {i+1}")
        tmp1.subscribe(lambda v: self._cm.set_setting(v + 1, "base-music-index-set"))
        self._cm.subscribe("base-music-index-get", lambda v: tmp1.set_value(v-1))

        tmp2 = BoxflatButtonRow("Preview", "Play")
        tmp2.set_active(0)
        tmp2.subscribe(lambda v: self._cm.set_setting(tmp1.get_value() + 1, "base-music-preview"))

        tmp3 = BoxflatSliderRow("Volume", subtitle="Very loud over 20")
        tmp3.add_marks(20, 40, 60, 80)
        tmp3.set_active(0)
        tmp3.set_slider_width(250)
        tmp3.set_expression("*2.55")
        tmp3.set_reverse_expression("/2.55")
        tmp3.subscribe(self._cm.set_setting, "base-music-volume-set")
        self._cm.subscribe("base-music-volume-get", tmp3.set_value)

        self.add_preferences_group("Startup music")
        self._add_row(BoxflatSwitchRow("Startup music enabled"))
        self._current_row.subscribe(tmp1.set_active)
        self._current_row.subscribe(tmp2.set_active)
        self._current_row.subscribe(tmp3.set_active)
        self._current_row.subscribe(self._cm.set_setting, "base-music-enabled-set")

        self._cm.subscribe("base-music-enabled-get", self._current_row.set_value)
        self._cm.subscribe("base-music-enabled-get", tmp1.set_active)
        self._cm.subscribe("base-music-enabled-get", tmp2.set_active)
        self._cm.subscribe("base-music-enabled-get", tmp3.set_active)
        self._cm.subscribe_connected("base-music-enabled-get", self._current_group.set_present, 1)

        self._add_row(tmp3)
        self._add_row(tmp1)
        self._add_row(tmp2)

        self.add_preferences_group("Temperatures")
        self._add_row(BoxflatLabelRow("MCU Temperature"))
        self._current_row.set_suffix("°C")
        self._current_row.set_reverse_expression("/100")
        self._cm.subscribe("base-mcu-temp", self._current_row.set_value)

        self._add_row(BoxflatLabelRow("MOSFET Temperature"))
        self._current_row.set_suffix("°C")
        self._current_row.set_reverse_expression("/100")
        self._cm.subscribe("base-mosfet-temp", self._current_row.set_value)

        self._add_row(BoxflatLabelRow("Motor Temperature"))
        self._current_row.set_suffix("°C")
        self._current_row.set_reverse_expression("/100")
        self._cm.subscribe("base-motor-temp", self._current_row.set_value)

        self.add_preferences_group()
        self._add_row(BoxflatButtonRow("Restore default settings", "Reset"))
        self._current_row.subscribe(self.reset)
        self._current_row.subscribe(self.reset)


    def __prepare_eq(self):
        self.add_preferences_page("EQ", "network-cellular-signal-excellent-symbolic")

        self.add_preferences_group()
        self._eq_row = BoxflatEqRow("FFB Equalizer", 6,
            subtitle="Perfectly balanced, as all things should be", range_end=400, suffix="%", button_row=False)
        self._add_row(self._eq_row)
        self._current_row.add_marks(50, 100, 200, 300)
        self._current_row.add_labels("10Hz", "15Hz", "25Hz", "40Hz", "60Hz", "100Hz")
        self._current_row.set_height(450)
        for i in range(6):
            self._eq_row.subscribe_slider(i, self._cm.set_setting, f"base-equalizer{i+1}")
            self._cm.subscribe(f"base-equalizer{i+1}", self._eq_row.set_slider_value, i)

        self.add_preferences_group()
        self._sensitivity_row = BoxflatSliderRow("Road Sensitivity", range_end=10)
        self._add_row(self._sensitivity_row)
        self._sensitivity_row.add_marks(2, 4, 6, 8)
        self._sensitivity_row.set_expression("*4 + 10")
        self._sensitivity_row.set_reverse_expression("/4 - 2.5")
        self._sensitivity_row.set_slider_width(350)
        self._sensitivity_row.subscribe(self._cm.set_setting, "base-road-sensitivity")
        self._sensitivity_row.subscribe(self._set_eq_preset, True)
        self._cm.subscribe("base-road-sensitivity", self._sensitivity_row.set_value)

        self._add_row(BoxflatSliderRow("FFB interpolation", 0, 10, subtitle="Mostly causes issues"))
        self._current_row.add_marks(2,4,6,8)
        self._current_row.set_slider_width(350)
        self._current_row.set_expression("*10")
        self._current_row.set_reverse_expression("/10")
        self._current_row.subscribe(self._cm.set_setting, "main-set-interpolation")
        self._cm.subscribe("main-get-interpolation", self._current_row.set_value)
        self._cm.subscribe_connected("main-get-interpolation", self._current_row.set_present, 1)


    def __prepare_curve(self):
        self.add_preferences_page("Curve", "network-cellular-signal-excellent-symbolic")

        self.add_preferences_group()
        self._curve_row = BoxflatEqRow("FFB Curve", 5, subtitle="Game FFB to Output FFB ratio", suffix="%")
        self._add_row(self._curve_row)
        self._current_row.add_marks(20, 40, 60, 80)
        self._current_row.add_labels("20%", "40%", "60%", "80%", "100%")
        self._current_row.set_height(320)

        self._current_row.add_buttons("Linear", "S Curve", "Inverted S", "Exponential", "Parabolic")
        self._current_row.set_button_value(-1)
        self._current_row.subscribe(self._set_curve_preset)
        for i in range(5):
            self._current_row.subscribe_slider(i, self._set_curve_point, i)
            self._cm.subscribe(f"base-ffb-curve-y{i+1}", self._get_curve, i)

        self.add_preferences_group()
        self._add_row(BoxflatSliderRow("Stronger around center", subtitle="FFB reaches first EQ point earlier", range_end=10))
        self._current_row.add_marks(5)
        self._current_row.set_expression("*-1 +20")
        self._current_row.set_reverse_expression("*-1 +20")
        self._current_row.subscribe(self._cm.set_setting, "base-ffb-curve-x1")
        self._cm.subscribe("base-ffb-curve-x1", self._current_row.set_value)

        self._add_row(BoxflatSwitchRow("Force Feedback Reversal"))
        self._current_row.subscribe(self._cm.set_setting, "base-ffb-reverse")
        self._cm.subscribe("base-ffb-reverse", self._current_row.set_value)


    def _set_curve_preset(self, value: int):
        self._set_curve(self._curve_presets[value])


    def _set_curve_point(self, value: int, index: int):
        self._cm.set_setting(value, f"base-ffb-curve-y{index+1}")


    def _set_curve(self, values: list):
        for i in range(4):
            self._cm.set_setting(self._curve_x[i], f"base-ffb-curve-x{i+1}")

        for i in range(5):
            self._cm.set_setting(values[i], f"base-ffb-curve-y{i+1}")


    def _get_curve(self, value: int, sindex: int):
        index = -1
        values = self._curve_row.get_sliders_value()
        values[sindex] = value

        if values in self._curve_presets:
            index = self._curve_presets.index(values)

        self._curve_row.set_button_value(index)
        self._curve_row.set_slider_value(value, sindex)


    def _set_eq_preset(self, index: int, get_index_from_sensitivity=False):
        if get_index_from_sensitivity:
            index = self._sensitivity_row.get_raw_value()

        for i in range(6):
            self._cm.set_setting(self._eq_presets[index][i], f"base-equalizer{i+1}")


    def reset(self, *_) -> None:
        self._set_rotation(450)
        self._set_curve_preset(0)
        self._set_eq_preset(0)

        self._cm.set_setting(0, "main-set-work-mode")
        self._cm.set_setting(0, "base-ffb-disable")
        self._cm.set_setting(100, "base-torque")
        self._cm.set_setting(800, "base-ffb-strength")
        self._cm.set_setting(1000, "base-speed")
        self._cm.set_setting(0, "base-protection")
        self._cm.set_setting(1, "base-protection-mode")
        self._cm.set_setting(1100, "base-natural-inertia")
        self._cm.set_setting(0, "base-speed-damping")
        self._cm.set_setting(120, "base-speed-damping-point")
        self._cm.set_setting(0, "base-spring")
        self._cm.set_setting(400, "base-damper")
        self._cm.set_setting(2500, "base-inertia")
        self._cm.set_setting(250, "base-friction")
        self._cm.set_setting(255, "main-set-spring-gain")
        self._cm.set_setting(128, "main-set-damper-gain")
        self._cm.set_setting(128, "main-set-inertia-gain")
        self._cm.set_setting(128, "main-set-friction-gain")
        self._cm.set_setting(278, "base-soft-limit-stiffness")
        self._cm.set_setting(78, "base-soft-limit-strength")
        self._cm.set_setting(0, "base-soft-limit-retain")
        self._cm.set_setting(1, "main-set-led-status")
        self._cm.set_setting(1, "base-music-index-set")
        self._cm.set_setting(51, "base-music-volume-set")
        self._cm.set_setting(1, "base-music-enabled-set")
        self._cm.set_setting(0, "main-set-interpolation")
        self._cm.set_setting(0, "base-ffb-reverse")
        self._cm.set_setting(0, "base-temp-strategy")
        self._cm.set_setting(50, "base-road-sensitivity")

        self._set_curve_preset(0)
        self._set_eq_preset(-1)
