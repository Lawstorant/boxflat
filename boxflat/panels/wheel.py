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
    def __init__(self, button_callback: callable, connection_manager: MozaConnectionManager, hid_handler) -> None:
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
        self._append_sub_connected("wheel-rpm-brightness", self.active)
        self._cm.subscribe_shutdown(self.shutdown)
        self._test_thread = Thread(daemon=True, target=self._wheel_rpm_test)
        self._test_event = Event()
        self._test_thread.start()


    def active(self, value: int) -> None:
        new_id = None
        if value == -1:
            new_id = self._cm.cycle_wheel_id()

        if new_id == 21 and self._stick_row:
            self._stick_row.set_active(0)
        elif self._stick_row:
            self._stick_row.set_active(1)

        super().active(value)

        if value == -1:
            self.set_banner_title(f"Device disconnected. Trying wheel id: {new_id}...")


    def prepare_ui(self) -> None:
        self.add_view_stack()
        self.add_preferences_page("Wheel")

        self.add_preferences_group("Input settings")

        paddle_mode = BoxflatToggleButtonRow("Dual Clutch Paddles Mode")
        self._add_row(paddle_mode)
        self._current_row.add_buttons("Buttons", "Combined", "Split")
        self._current_row.set_expression("+1")
        self._current_row.set_reverse_expression("-1")

        self._current_row.subscribe(self._cm.set_setting_int, "wheel-paddles-mode")
        self._append_sub("wheel-paddles-mode", self._current_row.set_value)
        self._append_sub_connected("wheel-paddles-mode", self._current_row.set_present)
        self._current_row.set_present(False)


        level = BoxflatLevelRow("Combined Paddles", max_value=65534)
        self._add_row(level)
        self._append_sub_hid(MozaAxis.COMBINED_PADDLES, self._current_row.set_value)
        self._append_sub_connected("wheel-paddles-mode", lambda v: level.set_present(v == 2))
        self._append_sub("wheel-clutch-point", self._current_row.set_offset)
        paddle_mode.subscribe(lambda v: level.set_present(v == 2, skip_cooldown=True))
        self._current_row.set_present(0, skip_cooldown=True, trigger_cooldown=False)

        self._add_row(BoxflatLevelRow("Left Paddle", max_value=65534))
        self._append_sub_hid(MozaAxis.LEFT_PADDLE, self._current_row.set_value)
        self._append_sub_connected("wheel-paddles-mode", self._current_row.set_present, -2)
        paddle_mode.subscribe(self._current_row.set_present, -2, True)
        self._current_row.set_present(0, skip_cooldown=True, trigger_cooldown=False)

        self._add_row(BoxflatLevelRow("Right Paddle", max_value=65534))
        self._append_sub_hid(MozaAxis.RIGHT_PADDLE, self._current_row.set_value)
        self._append_sub_connected("wheel-paddles-mode", self._current_row.set_present, -2)
        paddle_mode.subscribe(self._current_row.set_present, -2, True)
        self._current_row.set_present(0, skip_cooldown=True, trigger_cooldown=False)


        slider = BoxflatSliderRow("Clutch Split Point", suffix="%", range_start=5, range_end=95)
        self._add_row(slider)
        self._current_row.set_active(False)
        self._current_row.subtitle = "Left paddle cutoff"
        self._current_row.add_marks(25, 50, 75)
        self._current_row.subscribe(self._cm.set_setting_int, "wheel-clutch-point")
        self._current_row.subscribe(level.set_offset)
        paddle_mode.subscribe(lambda v: slider.set_active(v == 2))
        self._append_sub("wheel-clutch-point", self._current_row.set_value)
        self._append_sub("wheel-paddles-mode", lambda v: slider.set_active(v == 2))
        self._append_sub_connected("wheel-clutch-point", self._current_row.set_present)
        self._current_row.set_present(False)

        self._add_row(BoxflatToggleButtonRow("Rotary Encoder Mode"))
        self._current_row.add_buttons("Buttons", "  Knob ")
        self._current_row.subscribe(self._cm.set_setting_int, "wheel-knob-mode")
        self._append_sub("wheel-knob-mode", self._current_row.set_value)
        self._append_sub_connected("wheel-knob-mode", self._current_row.set_present, +1)

        self._stick_row = BoxflatToggleButtonRow("Left Stick Mode")
        self._add_row(self._stick_row)
        self._current_row.add_buttons("Buttons", "D-Pad")
        self._current_row.set_expression("*256")
        self._current_row.set_reverse_expression("/256")
        self._current_row.subscribe(self._cm.set_setting_int, "wheel-stick-mode")
        self._append_sub("wheel-stick-mode", self._current_row.set_value)


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
        self._current_row.add_switch("Center Wheel", "Press both paddles and Button 1")
        self._current_row.subscribe(self._set_combination_settings)
        self._append_sub("wheel-key-combination", self._get_combination_settings)

        self._add_row(BoxflatButtonRow("Wheel RPM test", "Test"))
        self._current_row.subscribe(self.start_test)

        self._add_row(BoxflatCalibrationRow("Calibrate Paddles", "Follow instructions here", alternative=True))
        self._current_row.subscribe(self._calibrate_paddles)
        self._cm.subscribe_shutdown(self._current_row.shutdown)


        # RPM
        self.add_preferences_page("RPM")
        self.add_preferences_group("Indicator settings")

        self._add_row(BoxflatToggleButtonRow("RPM Indicator Mode"))
        self._current_row.add_buttons("RPM", "Off", "On ")
        self._current_row.set_expression("+1")
        self._current_row.set_reverse_expression("-1")
        self._current_row.subscribe(self._cm.set_setting_int, "wheel-indicator-mode")
        self._append_sub("wheel-indicator-mode", self._current_row.set_value)

        self._add_row(BoxflatToggleButtonRow("RPM Indicator Display Mode"))
        self._current_row.add_buttons("Mode 1", "Mode 2")
        self._current_row.subscribe(self._cm.set_setting_int, "wheel-set-display-mode")
        self._append_sub("wheel-get-display-mode", self._current_row.set_value)

        self._add_row(BoxflatToggleButtonRow("RPM Mode"))
        self._current_row.add_buttons("Percent", "RPM")
        self._current_row.subscribe(self._cm.set_setting_int, "wheel-rpm-mode")
        self._current_row.subscribe(self._reconfigure_timings)
        self._append_sub("wheel-rpm-mode", self._current_row.set_value)

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

        for i in range(MOZA_RPM_LEDS):
            self._timing_row2.add_labels(f"RPM{i+1}", index=i)
            self._timing_row2.subscribe_slider(i, self._cm.set_setting_int, f"wheel-rpm-value{i+1}")
            self._append_sub(f"wheel-rpm-value{i+1}", self._timing_row2.set_slider_value, i)
        self._append_sub(f"wheel-rpm-value10", self._get_rpm_timings2_preset)


        self._append_sub("wheel-rpm-timings", self._get_rpm_timings)
        self._append_sub("wheel-rpm-timings", self._get_rpm_timings_preset)
        self._append_sub("wheel-rpm-mode", self._reconfigure_timings)


        self._add_row(BoxflatSliderRow("Blinking Interval", range_end=1000, subtitle="Miliseconds", increment=50))
        self._current_row.add_marks(125, 250, 375, 500, 625, 750, 875)
        self._current_row.subscribe(self._cm.set_setting_int, "wheel-rpm-interval")
        self._append_sub("wheel-rpm-interval", self._current_row.set_value)


        self.add_preferences_page("Colors")
        self.add_preferences_group("Buttons")
        self._add_row(BoxflatNewColorPickerRow("", blinking=True))
        self._current_row.subscribe(self._cm.set_setting_list, "wheel-button-color")
        self._append_sub_connected("wheel-buttons-brightness", self._current_row.set_active, +1)
        for i in range(MOZA_RPM_LEDS):
            self._append_sub(f"wheel-button-color{i+1}", self._current_row.set_led_value, i)

        self.add_preferences_group("RPM Colors")
        self._add_row(BoxflatNewColorPickerRow(""))
        self._current_row.subscribe(self._cm.set_setting_list, "wheel-rpm-color")
        for i in range(MOZA_RPM_LEDS):
            self._append_sub(f"wheel-rpm-color{i+1}", self._current_row.set_led_value, i)

        self.add_preferences_group("RPM Blinking")
        self._add_row(BoxflatNewColorPickerRow(""))
        self._current_row.subscribe(self._cm.set_setting_list, "wheel-rpm-blink-color")

        self.add_preferences_group("Brightness")
        self._add_row(BoxflatSliderRow("Button Brightness", range_end=15))
        self._current_row.add_marks(5, 10)
        self._current_row.subscribe(self._cm.set_setting_int, "wheel-buttons-brightness")
        self._append_sub("wheel-buttons-brightness", self._current_row.set_value)
        self._append_sub_connected("wheel-buttons-brightness", self._current_row.set_present, +1)

        self._add_row(BoxflatSliderRow("RPM Brightness", range_end=15))
        self._current_row.add_marks(5, 10)
        self._current_row.subscribe(self._cm.set_setting_int, "wheel-rpm-brightness")
        self._append_sub("wheel-rpm-brightness", self._current_row.set_value)

        # self._add_row(BoxflatSliderRow("Flag Brightness", range_end=15))
        # self._current_row.add_marks(5, 10)
        # self._current_row.subscribe(self._cm.set_setting_int, "wheel-flags-brightness")
        # self._append_sub("wheel-flags-brightness", self._current_row.set_value)

        # self.add_preferences_group("Telemetry flag")
        # self._add_row(BoxflatNewColorPickerRow(""))
        # self._current_row.subscribe(self._cm.set_setting_list, "wheel-flag-color")
        # for i in range(MOZA_RPM_LEDS):
        #     self._append_sub(f"wheel-flag-color{i+1}", self._current_row.set_led_value, i)


    def _set_rpm_timings(self, timings: list) -> None:
        self._cm.set_setting_list(timings, "wheel-rpm-timings")


    def _set_rpm_timings_preset(self, value: int) -> None:
        self._cm.set_setting_list(self._timings[value], "wheel-rpm-timings")


    def _get_rpm_timings(self, timings: list) -> None:
        self._timing_row.set_sliders_value(timings)


    def _get_rpm_timings_preset(self, timings: list) -> None:
        index = -1
        if list(timings) in self._timings:
            index = self._timings.index(list(timings))

        self._timing_row.set_button_value(index)


    def _set_rpm_timings2_preset(self, index) -> None:
        for i in range(10):
            self._cm.set_setting_int(self._timings2[index][i], f"wheel-rpm-value{i+1}")


    def _get_rpm_timings2_preset(self, *args) -> None:
        index = -1
        timings = self._timing_row2.get_sliders_value()

        if timings in self._timings2:
            index = self._timings2.index(timings)

        self._timing_row2.set_button_value(index)


    def _reconfigure_timings(self, value: int) -> None:
        self._timing_row.set_present(value < 1)
        self._timing_row2.set_present(value >= 1)


    def _calibrate_paddles(self, value: int) -> None:
        if value == 0:
            self._cm.set_setting_int(5, "wheel-paddles-calibration")

        else:
            self._cm.set_setting_int(1, "wheel-paddles-calibration")
            self._cm.set_setting_int(2, "wheel-paddles-calibration2")


    def _set_combination_settings(self, values) -> None:
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

        self._cm.set_setting_list(output, "wheel-key-combination")


    def _get_combination_settings(self, values) -> None:
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


    def start_test(self, *args) -> None:
        self._test_event.set()


    def _wheel_rpm_test(self, *args) -> None:
        while not self._shutdown:
            if not self._test_event.wait(timeout=1):
                continue

            self._test_event.clear()

            initial_mode = self._cm.get_setting_int("wheel-indicator-mode")
            self._cm.set_setting_int(1, "wheel-indicator-mode")

            t = 0.3
            for i in range(10):
                val = modify_bit(0, i)
                self._cm.set_setting_int(val, "wheel-send-telemetry")
                time.sleep(t)

            for i in reversed(range(9)):
                val = modify_bit(0, i)
                self._cm.set_setting_int(val, "wheel-send-telemetry")
                time.sleep(t)

            val = 0
            self._cm.set_setting_int(val, "wheel-send-telemetry")
            time.sleep(t)
            for i in range(10):
                val = modify_bit(val, i)
                self._cm.set_setting_int(val, "wheel-send-telemetry")
                time.sleep(t)

            time.sleep(0.5)
            val = modify_bit(0,15)
            self._cm.set_setting_int(val, "wheel-send-telemetry")
            time.sleep(1)

            self._cm.set_setting_int(initial_mode, "wheel-indicator-mode")
