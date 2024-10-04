from boxflat.panels.settings_panel import SettingsPanel
from boxflat.connection_manager import MozaConnectionManager
from boxflat.bitwise import *
from boxflat.widgets import *

from boxflat.hid_handler import MozaAxis

MOZA_TELEMETRY_FLAGS = [
    "Wheel Spin",
    "Pitlane",
    "Pit Limiter",
    "ABS",
    "Traction Control",
    "DRS ON",
    "Red Flag",
    "Yellow Flag",
    "Blue Flag",
    "Green Flag",
    "White Flag"
]

class WheelSettings(SettingsPanel):
    def __init__(self, button_callback: callable, connection_manager: MozaConnectionManager, hid_handler):
        self._split = None
        self._timing_row = None
        self._timing_preset_row = None
        self._stick_row = None
        self._timings = []
        self._timings.append([65, 69, 72, 75, 78, 80, 83, 85, 88, 91]) # Early
        self._timings.append([75, 79, 82, 85, 87, 88, 89, 90, 92, 94]) # Normal
        self._timings.append([80, 83, 86, 89, 91, 92, 93, 94, 96, 97]) # Late
        # self._timings.append([80, 83, 86, 89, 91, 92, 93, 94, 96, 97]) # Central
        self._wheel_combination_data = []

        self._timings2 = [
            [5400, 5700, 6000, 6300, 6500, 6700, 6900, 7100, 7300, 7600],
            [6300, 6600, 6800, 7100, 7300, 7300, 7400, 7500, 7700, 7800],
            [6700, 6900, 7200, 7400, 7600, 7700, 7800, 7800, 8000, 8100]
        ]

        super().__init__("Wheel", button_callback, connection_manager, hid_handler)
        self._cm.subscribe_connected("wheel-indicator-mode", self.active)


    def active(self, value: int):
        new_id = None
        if value == -1:
            new_id = self._cm.cycle_wheel_id()

        if new_id == 21 and self._stick_row:
            self._stick_row.set_active(0)
            self._combination_row.set_present(0)
        elif self._stick_row:
            self._stick_row.set_active(1)
            self._combination_row.set_present(1)

        super().active(value)

        if value == -1:
            self.set_banner_title(f"Device disconnected. Trying wheel id: {new_id}...")


    def prepare_ui(self):
        self.add_view_stack()
        self.add_preferences_page("Wheel")

        self.add_preferences_group("Input settings")

        paddle_mode = BoxflatToggleButtonRow("Dual Clutch Paddles Mode")
        self._add_row(paddle_mode)
        self._current_row.add_buttons("Buttons", "Combined", "Split")
        self._current_row.set_expression("+1")
        self._current_row.set_reverse_expression("-1")

        self._current_row.subscribe(self._cm.set_setting, "wheel-paddles-mode")
        self._cm.subscribe("wheel-paddles-mode", self._current_row.set_value)
        self._cm.subscribe_connected("wheel-paddles-mode", self._current_row.set_present)
        self._current_row.set_present(False)


        level = BoxflatLevelRow("Combined Paddles", max_value=65534)
        self._add_row(level)
        self._hid_handler.subscribe(MozaAxis.COMBINED_PADDLES.name, self._current_row.set_value)
        self._cm.subscribe_connected("wheel-paddles-mode", lambda v: level.set_present(v == 2))
        self._cm.subscribe("wheel-clutch-point", self._current_row.set_offset)
        paddle_mode.subscribe(lambda v: level.set_present(v == 2, skip_cooldown=True))
        self._current_row.set_present(0, skip_cooldown=True, trigger_cooldown=False)

        self._add_row(BoxflatLevelRow("Left Paddle", max_value=65534))
        self._hid_handler.subscribe(MozaAxis.LEFT_PADDLE.name, self._current_row.set_value)
        self._cm.subscribe_connected("wheel-paddles-mode", self._current_row.set_present, -2)
        paddle_mode.subscribe(self._current_row.set_present, -2, True)
        self._current_row.set_present(0, skip_cooldown=True, trigger_cooldown=False)

        self._add_row(BoxflatLevelRow("Right Paddle", max_value=65534))
        self._hid_handler.subscribe(MozaAxis.RIGHT_PADDLE.name, self._current_row.set_value)
        self._cm.subscribe_connected("wheel-paddles-mode", self._current_row.set_present, -2)
        paddle_mode.subscribe(self._current_row.set_present, -2, True)
        self._current_row.set_present(0, skip_cooldown=True, trigger_cooldown=False)


        slider = BoxflatSliderRow("Clutch Split Point", suffix="%", range_start=5, range_end=95)
        self._add_row(slider)
        self._current_row.set_active(False)
        self._current_row.subtitle = "Left paddle cutoff"
        self._current_row.add_marks(25, 50, 75)
        self._current_row.subscribe(self._cm.set_setting, "wheel-clutch-point")
        self._current_row.subscribe(level.set_offset)
        paddle_mode.subscribe(lambda v: slider.set_active(v == 2))
        self._cm.subscribe("wheel-clutch-point", self._current_row.set_value)
        self._cm.subscribe("wheel-paddles-mode", lambda v: slider.set_active(v == 2))
        self._cm.subscribe_connected("wheel-clutch-point", self._current_row.set_present)
        self._current_row.set_present(False)

        self._add_row(BoxflatToggleButtonRow("Rotary Encoder Mode"))
        self._current_row.add_buttons("Buttons", "  Knob ")
        self._current_row.subscribe(self._cm.set_setting, "wheel-knob-mode")
        self._cm.subscribe("wheel-knob-mode", self._current_row.set_value)
        self._cm.subscribe_connected("wheel-knob-mode", self._current_row.set_present, +1)

        self._stick_row = BoxflatToggleButtonRow("Left Stick Mode")
        self._add_row(self._stick_row)
        self._current_row.add_buttons("Buttons", "D-Pad")
        self._current_row.set_expression("*256")
        self._current_row.set_reverse_expression("/256")
        self._current_row.subscribe(self._cm.set_setting, "wheel-stick-mode")
        self._cm.subscribe("wheel-stick-mode", self._current_row.set_value)


        self.add_preferences_group("Misc")
        self._combination_row = BoxflatDialogRow("Key Combination Settings")
        self._add_row(self._combination_row)
        self._current_row.add_switch("Left Stick Mode", "Press and hold both sticks")
        self._current_row.add_switch("Wheelbase Setting", "Button 34 + Up/Down/Left/Right")
        self._current_row.add_switch("Set angle to 360°", "Button 33 + Up")
        self._current_row.add_switch("Set angle to 540°", "Button 33 + Right")
        self._current_row.add_switch("Set angle to 720°", "Button 33 + Down")
        self._current_row.add_switch("Set angle to 900°", "Button 33 + Left")
        self._current_row.add_switch("Switch Dash Display", "Button 32 + Left/Right")
        self._current_row.add_switch("Set Wheel Center Point", "Press both paddles and Button 1")
        self._current_row.subscribe(self._set_combination_settings)
        self._cm.subscribe("wheel-key-combination", self._get_combination_settings)

        self._add_row(BoxflatButtonRow("Wheel RPM test", "Test"))
        self._current_row.subscribe(self.start_test)

        calibration = BoxflatCalibrationRow("Calibrate Paddles", "Follow instructions here", alternative=True)
        self._add_row(calibration)
        calibration.subscribe("calibration-start", self._calibrate_paddles, 0)
        calibration.subscribe("calibration-stop", self._calibrate_paddles, 1)


        # RPM
        self.add_preferences_page("RPM")
        self.add_preferences_group("Indicator settings")

        self._add_row(BoxflatToggleButtonRow("RPM Indicator Mode"))
        self._current_row.add_buttons("RPM", "Off", "On ")
        self._current_row.set_expression("+1")
        self._current_row.set_reverse_expression("-1")
        self._current_row.subscribe(self._cm.set_setting, "wheel-indicator-mode")
        self._cm.subscribe("wheel-indicator-mode", self._current_row.set_value)

        self._add_row(BoxflatToggleButtonRow("RPM Indicator Display Mode"))
        self._current_row.add_buttons("Mode 1", "Mode 2")
        self._current_row.subscribe(self._cm.set_setting, "wheel-set-display-mode")
        self._cm.subscribe("wheel-get-display-mode", self._current_row.set_value)

        self._add_row(BoxflatToggleButtonRow("RPM Mode"))
        self._current_row.add_buttons("Percent", "RPM")
        self._current_row.subscribe(self._cm.set_setting, "wheel-rpm-mode")
        self._current_row.subscribe(self._reconfigure_timings)
        self._cm.subscribe("wheel-rpm-mode", self._current_row.set_value)

        self.add_preferences_group("Timings")
        self._timing_row = BoxflatEqRow("RPM Indicator Timing", 10, "Is it my turn now?",
            button_row=False, draw_marks=False)

        self._add_row(self._timing_row)
        self._timing_row.add_buttons("Early", "Normal", "Late")
        self._timing_row.subscribe(self._set_rpm_timings_preset)
        self._timing_row.subscribe_sliders(self._set_rpm_timings)
        for i in range(MOZA_RPM_LEDS):
            self._timing_row.add_labels(f"RPM{i+1}", index=i)


        self._timing_row2 = BoxflatEqRow("RPM Indicator Timing", 10, "Is it my turn now?",
            range_start=2000, range_end=18000, button_row=False, draw_marks=False, increment=100)

        self._add_row(self._timing_row2)
        self._timing_row2.add_buttons("Early", "Normal", "Late")
        self._timing_row2.subscribe(self._set_rpm_timings2_preset)
        self._timing_row2.set_present(0)

        for i in range(MOZA_RPM_LEDS):
            self._timing_row2.add_labels(f"RPM{i+1}", index=i)
            self._timing_row2.subscribe_slider(i, self._cm.set_setting, f"wheel-rpm-value{i+1}")
            self._cm.subscribe(f"wheel-rpm-value{i+1}", self._timing_row2.set_slider_value, i)
        self._cm.subscribe(f"wheel-rpm-value10", self._get_rpm_timings2_preset)


        self._cm.subscribe("wheel-rpm-timings", self._get_rpm_timings)
        self._cm.subscribe("wheel-rpm-timings", self._get_rpm_timings_preset)
        self._cm.subscribe("wheel-rpm-mode", self._reconfigure_timings)


        self._add_row(BoxflatSliderRow("Blinking Interval", range_end=1000, subtitle="Miliseconds", increment=50))
        self._current_row.add_marks(125, 250, 375, 500, 625, 750, 875)
        self._current_row.subscribe(self._cm.set_setting, "wheel-rpm-interval")
        self._cm.subscribe("wheel-rpm-interval", self._current_row.set_value)


        self.add_preferences_page("Colors")
        self.add_preferences_group("Buttons")
        self._add_row(BoxflatNewColorPickerRow(blinking=True))
        self._cm.subscribe_connected("wheel-buttons-brightness", self._current_row.set_active, +1)
        for i in range(MOZA_RGB_BUTTONS):
            self._current_row.subscribe(f"color{i}", self._cm.set_setting, f"wheel-button-color{i+1}")
            self._cm.subscribe(f"wheel-button-color{i+1}", self._current_row.set_led_value, i)

        self.add_preferences_group("RPM Colors")
        self._add_row(BoxflatNewColorPickerRow())
        for i in range(MOZA_RPM_LEDS):
            self._current_row.subscribe(f"color{i}", self._cm.set_setting, f"wheel-rpm-color{i+1}")
            self._cm.subscribe(f"wheel-rpm-color{i+1}", self._current_row.set_led_value, i)

        self.add_preferences_group("RPM Blinking")
        self._add_row(BoxflatNewColorPickerRow())
        for i in range(MOZA_RPM_LEDS):
            self._current_row.subscribe(f"color{i}", self._cm.set_setting, f"wheel-rpm-blink-color{i+1}")

        self.add_preferences_group("Brightness")
        self._add_row(BoxflatSliderRow("Button Brightness", range_end=15))
        self._current_row.add_marks(5, 10)
        self._current_row.subscribe(self._cm.set_setting, "wheel-buttons-brightness")
        self._cm.subscribe("wheel-buttons-brightness", self._current_row.set_value)
        self._cm.subscribe_connected("wheel-buttons-brightness", self._current_row.set_present, +1)

        self._add_row(BoxflatSliderRow("RPM Brightness", range_end=15))
        self._current_row.add_marks(5, 10)
        self._current_row.subscribe(self._cm.set_setting, "wheel-rpm-brightness")
        self._cm.subscribe("wheel-rpm-brightness", self._current_row.set_value)

        # self._add_row(BoxflatSliderRow("Flag Brightness", range_end=15))
        # self._current_row.add_marks(5, 10)
        # self._current_row.subscribe(self._cm.set_setting, "wheel-flags-brightness")
        # self._cm.subscribe("wheel-flags-brightness", self._current_row.set_value)

        # self.add_preferences_group("Telemetry flag")
        # self._add_row(BoxflatNewColorPickerRow(""))
        # for i in range(MOZA_RPM_LEDS):
        #     self._cm.subscribe(f"wheel-flag-color{i+1}", self._current_row.set_led_value, i)


    def _set_rpm_timings(self, timings: list):
        self._cm.set_setting(timings, "wheel-rpm-timings")


    def _set_rpm_timings_preset(self, value: int):
        self._timing_row.set_sliders_value(self._timings[value], mute=False)


    def _get_rpm_timings(self, timings: list):
        self._timing_row.set_sliders_value(timings)


    def _get_rpm_timings_preset(self, timings: list):
        index = -1
        if list(timings) in self._timings:
            index = self._timings.index(list(timings))

        self._timing_row.set_button_value(index)


    def _set_rpm_timings2_preset(self, index):
        self._timing_row2.set_sliders_value(self._timings2[index], mute=False)


    def _get_rpm_timings2_preset(self, *args):
        index = -1
        timings = self._timing_row2.get_sliders_value()

        if timings in self._timings2:
            index = self._timings2.index(timings)

        self._timing_row2.set_button_value(index)


    def _reconfigure_timings(self, value: int):
        self._timing_row.set_present(value < 1)
        self._timing_row2.set_present(value >= 1)


    def _calibrate_paddles(self, value: int):
        if value == 0:
            self._cm.set_setting(5, "wheel-paddles-calibration")

        else:
            self._cm.set_setting(1, "wheel-paddles-calibration")
            self._cm.set_setting(2, "wheel-paddles-calibration2")


    def _set_combination_settings(self, values):
        output = self._wheel_combination_data.copy()

        if len(output) != 4:
            return

        output[3] = modify_bit(output[3], 0, values[0])
        output[3] = modify_bit(output[3], 3, values[1])
        output[1] = modify_bit(output[1], 0, values[2])
        output[1] = modify_bit(output[1], 1, values[3])
        output[1] = modify_bit(output[1], 2, values[4])
        output[1] = modify_bit(output[1], 3, values[5])
        output[3] = modify_bit(output[3], 1, values[6])
        output[3] = modify_bit(output[3], 5, values[7])

        self._cm.set_setting(output, "wheel-key-combination")


    def _get_combination_settings(self, values):
        self._wheel_combination_data = values
        byte1 = values[1]
        byte2 = values[3]

        switch_values = []

        switch_values.append(test_bit(byte2, 0))
        switch_values.append(test_bit(byte2, 3))

        # angle settings
        switch_values.append(test_bit(byte1, 0))
        switch_values.append(test_bit(byte1, 1))
        switch_values.append(test_bit(byte1, 2))
        switch_values.append(test_bit(byte1, 3))

        switch_values.append(test_bit(byte2, 1))
        switch_values.append(test_bit(byte2, 5))

        self._combination_row.set_value(switch_values)


    def start_test(self, *args):
        self._test_thread = Thread(daemon=True, target=self._wheel_rpm_test).start()


    def _wheel_rpm_test(self, *args):
        self._cm.set_setting(0, "wheel-send-telemetry")
        time.sleep(0.2)
        initial_mode = self._cm.get_setting("wheel-indicator-mode")
        self._cm.set_setting(1, "wheel-indicator-mode")

        t = 0.07
        for j in range(2):
            for i in range(10):
                val = bit(i)
                self._cm.set_setting(val, "wheel-send-telemetry")
                time.sleep(t)

            for i in reversed(range(1,9)):
                val = bit(i)
                self._cm.set_setting(val, "wheel-send-telemetry")
                time.sleep(t)

        val = 0
        self._cm.set_setting(val, "wheel-send-telemetry")
        time.sleep(t)
        for i in range(10):
            val = set_bit(val, i)
            self._cm.set_setting(val, "wheel-send-telemetry")
            time.sleep(t)

        for i in range(9):
            val = unset_bit(val, i)
            self._cm.set_setting(val, "wheel-send-telemetry")
            time.sleep(t)

        for i in reversed(range(10)):
            val = set_bit(val, i)
            self._cm.set_setting(val, "wheel-send-telemetry")
            time.sleep(t)

        for i in reversed(range(1,10)):
            val = unset_bit(val, i)
            self._cm.set_setting(val, "wheel-send-telemetry")
            time.sleep(t)

        for i in range(1,10):
            val = set_bit(val, i)
            self._cm.set_setting(val, "wheel-send-telemetry")
            time.sleep(t)

        time.sleep(0.2)
        val = modify_bit(0,15)
        self._cm.set_setting(val, "wheel-send-telemetry")
        time.sleep(0.8)

        self._cm.set_setting(initial_mode, "wheel-indicator-mode")
