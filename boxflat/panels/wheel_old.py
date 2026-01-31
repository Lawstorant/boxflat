# Copyright (c) 2025, Tomasz Pakuła Using Arch BTW

from boxflat.panels.settings_panel import SettingsPanel
from boxflat.connection_manager import MozaConnectionManager
from boxflat.bitwise import *
from boxflat.widgets import *

from boxflat.hid_handler import MozaAxis
from boxflat.settings_handler import SettingsHandler
from boxflat.ac_telemetry import ACTelemetryReader

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

SHARED_SETTINGS = [
    "rpm-display-mode",
    "rpm-timings",
    "rpm-indicator-mode",
    "rpm-interval",
    "rpm-mode",
    "rpm-value1",
    "rpm-value2",
    "rpm-value3",
    "rpm-value4",
    "rpm-value5",
    "rpm-value6",
    "rpm-value7",
    "rpm-value8",
    "rpm-value9",
    "rpm-value10",
    "rpm-color1",
    "rpm-color2",
    "rpm-color3",
    "rpm-color4",
    "rpm-color5",
    "rpm-color6",
    "rpm-color7",
    "rpm-color8",
    "rpm-color9",
    "rpm-color10",
    "rpm-brightness",
]

indicator_mode_map = [2,1,3]

class OldWheelSettings(SettingsPanel):
    def __init__(self, button_callback, connection_manager: MozaConnectionManager, hid_handler, settings: SettingsHandler):
        self._settings = settings
        self._blinking_row = None

        self._split = None
        self._timing_row = None
        self._timing_preset_row = None
        self._stick_row = None
        self._wheel_combination_data: list[int] = []

        self._timings: list[list[int]] = [
            [65, 69, 72, 75, 78, 80, 83, 85, 88, 91], # Early
            [75, 79, 82, 85, 87, 88, 89, 90, 92, 94], # Normal
            [80, 83, 86, 89, 91, 92, 93, 94, 96, 97], # Late
        ]
        #self._timings.append([80, 83, 86, 89, 91, 92, 93, 94, 96, 97]) # Outside-in

        self._timings2: list[list[int]] = [
            [5400, 5700, 6000, 6300, 6500, 6700, 6900, 7100, 7300, 7600],
            [6300, 6600, 6800, 7100, 7300, 7300, 7400, 7500, 7700, 7800],
            [6700, 6900, 7200, 7400, 7600, 7700, 7800, 7800, 8000, 8100]
        ]

        # Initialize AC telemetry reader (direct shared memory, reads from AC like Monocoque)
        def _rpm_callback(rpm_value):
            """Callback when AC telemetry updates RPM."""
            # Send RPM to wheel using bitfield method (for old wheels)
            # Calculate percentage (0-100) and convert to LED bitfield
            percent = min(100, max(0, int(rpm_value * 100 / 20000)))
            num_leds = int(percent / 10)

            value = 0
            for i in range(num_leds):
                value = bit(i) | value

            self._cm.set_setting(value, "wheel-old-send-telemetry")

        self._ac_telemetry = ACTelemetryReader(_rpm_callback)

        super().__init__("Wheel Old", button_callback, connection_manager, hid_handler)
        self._cm.subscribe_connected("wheel-rpm-value1", self.active)
        self.set_banner_title(f"Device disconnected...")


    def active(self, value: int):
        initial = self._active

        super().active(value)
        if value == -1:
            new_id = self._cm.cycle_wheel_id(old=True)
            self.set_banner_title(f"Device disconnected. Trying wheel id: {new_id}...")
            return

        # Ensure AC telemetry switch stays sensitive even when device disconnected
        if hasattr(self, '_ac_telemetry_switch_row') and self._ac_telemetry_switch_row:
            self._ac_telemetry_switch_row.set_sensitive(True)

        wheel_id = self._cm.get_device_id("wheel")
        if self._stick_row is not None:
            self._stick_row.set_active(wheel_id == 23)

        if self._combination_row is not None:
            self._combination_row.set_active(wheel_id == 23)

        # only set blink colors if wheel freshly connected
        if not self._active or initial:
            return

        for i in range(MOZA_RPM_LEDS):
            self._cm.set_setting(self._blinking_row.get_value(i), f"wheel-rpm-blink-color{i+1}")
            self._cm.set_setting(self._blinking_row.get_value(i), f"wheel-rpm-blink-color{i+1}")


    def prepare_ui(self):
        self.add_view_stack()
        self.add_preferences_page("Wheel")

        self.add_preferences_group("Info")
        self._current_group.set_description("If you don't have ES wheel, please update it to the newest firmware")

        self.add_preferences_group("Clutch Paddles")
        self._cm.subscribe_connected("wheel-paddles-mode", self._current_group.set_present)
        self._current_group.set_present(0)

        paddle_mode = BoxflatToggleButtonRow("Dual Clutch Paddles Mode")
        self._add_row(paddle_mode)
        self._current_row.add_buttons("Buttons", "Combined", "Split")
        self._current_row.set_expression("+1")
        self._current_row.set_reverse_expression("-1")

        self._current_row.subscribe(self._cm.set_setting, "wheel-paddles-mode")
        self._cm.subscribe("wheel-paddles-mode", self._current_row.set_value)


        level = BoxflatLevelRow("Combined Paddles", max_value=65535)
        self._add_row(level)
        self._hid_handler.subscribe(MozaAxis.COMBINED_PADDLES.name, self._current_row.set_value)
        self._cm.subscribe_connected("wheel-paddles-mode", lambda v: level.set_present(v == 2))
        self._cm.subscribe("wheel-clutch-point", self._current_row.set_offset)
        paddle_mode.subscribe(lambda v: level.set_present(v == 2, skip_cooldown=True))
        self._current_row.set_present(0, skip_cooldown=True, trigger_cooldown=False)

        self._add_row(BoxflatLevelRow("Left Paddle", max_value=65535))
        self._hid_handler.subscribe(MozaAxis.LEFT_PADDLE.name, self._current_row.set_value)
        self._cm.subscribe_connected("wheel-paddles-mode", self._current_row.set_present, -2)
        paddle_mode.subscribe(self._current_row.set_present, -2, True)
        self._current_row.set_present(0, skip_cooldown=True, trigger_cooldown=False)

        self._add_row(BoxflatLevelRow("Right Paddle", max_value=65535))
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

        self.add_preferences_group("Input")
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
        self._current_row.add_switch("Switch Dash Display", "Button 32 + Left/Right\nCM2: Button 20 + Right stick")
        self._current_row.add_switch("Set Wheel Center Point", "Press both paddles and Button 1")
        self._current_row.subscribe(self._set_combination_settings)
        self._cm.subscribe("wheel-key-combination", self._get_combination_settings)

        calibration = BoxflatCalibrationRow("Calibrate Paddles", "Follow instructions here", alternative=True)
        self._add_row(calibration)
        calibration.subscribe("calibration-start", self._calibrate_paddles, 0)
        calibration.subscribe("calibration-stop", self._calibrate_paddles, 1)

        self.add_preferences_group()
        self._add_row(BoxflatButtonRow("Restore default settings", "Reset"))
        self._current_row.subscribe(self.reset)
        self._current_row.subscribe(self.reset)


        # RPM
        self.add_preferences_page("RPM")
        self.add_preferences_group("Indicator settings")

        self._add_row(BoxflatToggleButtonRow("RPM Indicator Mode"))
        self._current_row.add_buttons("RPM", "Off", "On ")
        self._current_row.set_expression("+1")
        self._current_row.set_reverse_expression("-1")
        self._current_row.subscribe(self._cm.set_setting, "wheel-rpm-indicator-mode")
        self._cm.subscribe("wheel-rpm-indicator-mode", self._current_row.set_value)

        self._add_row(BoxflatToggleButtonRow("RPM Indicator Display Mode"))
        self._current_row.add_buttons("Mode 1", "Mode 2")
        self._current_row.subscribe(self._cm.set_setting, "wheel-set-rpm-display-mode")
        self._cm.subscribe("wheel-get-rpm-display-mode", self._current_row.set_value)

        self._add_row(BoxflatToggleButtonRow("RPM Mode"))
        self._current_row.add_buttons("Percent", "RPM")
        self._current_row.subscribe(self._cm.set_setting, "wheel-rpm-mode")
        self._current_row.subscribe(self._reconfigure_timings)
        self._cm.subscribe("wheel-rpm-mode", self._current_row.set_value)

        self.add_preferences_group("Telemetry")
        self._current_group.set_description("Read RPM data directly from Assetto Corsa shared memory")
        # Make this group always accessible, even when device is disconnected
        self._groups.remove(self._current_group)  # Remove from auto-sensitivity list

        # Load saved state
        telemetry_enabled = self._settings.read_setting("ac-telemetry-enabled") or False

        # Enable/Disable telemetry
        self._add_row(BoxflatSwitchRow("Enable AC Telemetry"))
        self._ac_telemetry_switch_row = self._current_row
        # Directly connect to the switch signal
        self._ac_telemetry_switch_row._switch.connect('notify::active', self._on_ac_telemetry_switch_changed)

        # Set initial state
        self._ac_telemetry_switch_row._switch.set_active(telemetry_enabled)

        self.add_preferences_group("Timings")
        self._timing_row = BoxflatEqRow("RPM Indicator Timing", 10, "Is it my turn now?",
            button_row=False, draw_marks=False)

        self._add_row(self._timing_row)
        self._timing_row.add_buttons("Early", "Normal", "Late")
        # self._timing_row.add_buttons("Center")
        self._timing_row.subscribe(self._set_rpm_timings_preset)
        self._timing_row.subscribe_sliders(self._set_rpm_timings)
        for i in range(MOZA_RPM_LEDS):
            self._timing_row.add_label(f"RPM{i+1}", index=i)


        self._timing_row2 = BoxflatEqRow("RPM Indicator Timing", 10, "Is it my turn now?",
            range_start=2000, range_end=18_000, button_row=False, draw_marks=False, increment=100)

        self._add_row(self._timing_row2)
        self._timing_row2.add_buttons("Early", "Normal", "Late")
        self._timing_row2.subscribe(self._set_rpm_timings2_preset)
        self._timing_row2.set_present(0)

        for i in range(MOZA_RPM_LEDS):
            self._timing_row2.add_label(f"RPM{i+1}", index=i)
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

        self.add_preferences_group("RPM Colors")
        self._add_row(BoxflatNewColorPickerRow())
        for i in range(MOZA_RPM_LEDS):
            self._current_row.subscribe(f"color{i}", self._cm.set_setting, f"wheel-old-rpm-color{i+1}")
            self._cm.subscribe(f"wheel-old-rpm-color{i+1}", self._current_row.set_led_value, i)

        self.add_preferences_group("RPM Blinking")
        self._current_group.set_description("These colors are not saved to the wheel")
        self._blinking_row = BoxflatNewColorPickerRow()
        self._add_row(self._blinking_row)
        for i in range(MOZA_RPM_LEDS):
            name = f"wheel-rpm-blink-color{i+1}"
            self._current_row.set_led_value(self._settings.read_setting(name), i)
            self._current_row.subscribe(f"color{i}", self._cm.set_setting, name)
            self._current_row.subscribe(f"color{i}", self._settings.write_setting, name)

        self._add_row(BoxflatSliderRow("RPM Brightness", range_end=15))
        self._current_row.add_marks(5, 10)
        self._current_row.subscribe(self._cm.set_setting, "wheel-old-rpm-brightness")
        self._cm.subscribe("wheel-old-rpm-brightness", self._current_row.set_value)

        self.add_preferences_group()
        self._add_row(BoxflatButtonRow("Wheel indicator test", "Test"))
        self._current_row.subscribe(self.start_test)


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
        # self._timing_row2.set_sliders_value(self._timings2[index], mute=False)
        for i, value in enumerate(self._timings2[index]):
            self._cm.set_setting(value, f"wheel-rpm-value{i+1}", exclusive=True)
            time.sleep(0.005)
            self._cm.set_setting(value, f"wheel-rpm-value{i+1}")
            time.sleep(0.005)


    def _get_rpm_timings2_preset(self, *args):
        index = -1
        timings = self._timing_row2.get_sliders_value()

        if timings in self._timings2:
            index = self._timings2.index(timings)

        self._timing_row2.set_button_value(index)


    def _reconfigure_timings(self, value: int):
        self._timing_row.set_present(value < 1)
        self._timing_row2.set_present(value >= 1)


    def _on_ac_telemetry_switch_changed(self, switch, gparam):
        """Handle AC telemetry switch change."""
        enabled = switch.get_active()
        print(f"[Wheel Old] AC telemetry toggle: {enabled}")

        if enabled:
            print("[Wheel Old] Starting direct AC telemetry (shared memory)")
            self._ac_telemetry.start()
        else:
            print("[Wheel Old] Stopping AC telemetry")
            self._ac_telemetry.stop()

        self._settings.write_setting(int(enabled), "ac-telemetry-enabled")


    def _calibrate_paddles(self, value: int, *_):
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

        switch_values: list[int] = []

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


    def _sync_from_dash(self, *args):
        for setting in SHARED_SETTINGS:
            value = self._cm.get_setting(f"dash-{setting}", exclusive=True)
            if value is None:
                value = self._cm.get_setting(f"dash-{setting}", exclusive=True)

            if setting == "rpm-display-mode":
                setting = f"set-{setting}"

            if setting == "rpm-indicator-mode":
                value = indicator_mode_map[value]

            self._cm.set_setting(value, f"wheel-{setting}")

        for i in range(MOZA_RPM_LEDS):
            color = self._settings.read_setting(f"dash-rpm-blink-color{i+1}")
            self._blinking_row.set_led_value(color, i, mute=False)
            self._blinking_row.set_led_value(color, i, mute=False)


    def _wheel_rpm_test(self, *args):
        self._cm.set_setting(0, "wheel-old-send-telemetry")
        time.sleep(0.2)
        initial_mode = self._cm.get_setting("wheel-rpm-indicator-mode", exclusive=True)
        self._cm.set_setting(1, "wheel-rpm-indicator-mode", exclusive=True)

        t = 0.1
        for j in range(2):
            for i in range(10):
                val = bit(i)
                self._cm.set_setting(val, "wheel-old-send-telemetry")
                time.sleep(t)

            for i in reversed(range(1,9)):
                val = bit(i)
                self._cm.set_setting(val, "wheel-old-send-telemetry")
                time.sleep(t)

        val = 0
        self._cm.set_setting(val, "wheel-old-send-telemetry")
        time.sleep(t)
        for i in range(10):
            val = set_bit(val, i)
            self._cm.set_setting(val, "wheel-old-send-telemetry")
            time.sleep(t)

        for i in range(9):
            val = unset_bit(val, i)
            self._cm.set_setting(val, "wheel-old-send-telemetry")
            time.sleep(t)

        for i in reversed(range(10)):
            val = set_bit(val, i)
            self._cm.set_setting(val, "wheel-old-send-telemetry")
            time.sleep(t)

        for i in reversed(range(1,10)):
            val = unset_bit(val, i)
            self._cm.set_setting(val, "wheel-old-send-telemetry")
            time.sleep(t)

        for i in range(1,10):
            val = set_bit(val, i)
            self._cm.set_setting(val, "wheel-old-send-telemetry")
            time.sleep(t)

        time.sleep(0.2)
        val = modify_bit(0,15)
        self._cm.set_setting(val, "wheel-old-send-telemetry")
        time.sleep(0.9)

        self._cm.set_setting(val, "wheel-old-send-telemetry")
        time.sleep(0.9)

        self._cm.set_setting(0, "wheel-old-send-telemetry")
        self._cm.set_setting([255, 0, 0] * 7, "wheel-flag-colors1")
        self._cm.set_setting([255, 0, 0] * 3, "wheel-flag-colors2")
        time.sleep(0.9)

        self._cm.set_setting(0, "wheel-old-send-telemetry")
        self._cm.set_setting([255, 0, 0] * 7, "wheel-flag-colors1")
        self._cm.set_setting([255, 0, 0] * 3, "wheel-flag-colors2")
        time.sleep(0.9)

        self._cm.set_setting(0, "wheel-old-send-telemetry")
        self._cm.set_setting([0, 255, 0] * 7, "wheel-flag-colors1")
        self._cm.set_setting([0, 255, 0] * 3, "wheel-flag-colors2")
        time.sleep(0.9)

        self._cm.set_setting(0, "wheel-old-send-telemetry")
        self._cm.set_setting([0, 255, 0] * 7, "wheel-flag-colors1")
        self._cm.set_setting([0, 255, 0] * 3, "wheel-flag-colors2")
        time.sleep(0.9)

        self._cm.set_setting(0, "wheel-old-send-telemetry")
        self._cm.set_setting([0, 0, 255] * 7, "wheel-flag-colors1")
        self._cm.set_setting([0, 0, 255] * 3, "wheel-flag-colors2")
        time.sleep(0.9)

        self._cm.set_setting(0, "wheel-old-send-telemetry")
        self._cm.set_setting([0, 0, 255] * 7, "wheel-flag-colors1")
        self._cm.set_setting([0, 0, 255] * 3, "wheel-flag-colors2")
        time.sleep(0.9)

        self._cm.set_setting(initial_mode, "wheel-rpm-indicator-mode", exclusive=True)


    def reset(self, *_) -> None:
        self._set_rpm_timings_preset(0)
        self._set_rpm_timings2_preset(0)

        self._cm.set_setting(0, "wheel-rpm-indicator-mode")
        # self._cm.set_setting(1, "wheel-flags-indicator-mode")
        self._cm.set_setting(0, "wheel-set-rpm-display-mode")
        self._cm.set_setting(0, "wheel-rpm-mode")
        self._cm.set_setting(2, "wheel-paddles-mode")
        self._cm.set_setting(50, "wheel-clutch-point")
        self._cm.set_setting(0, "wheel-knob-mode")
        self._cm.set_setting(256, "wheel-stick-mode")

        self._set_rpm_timings_preset(0)
        self._set_rpm_timings2_preset(0)

        self._cm.set_setting(250, "wheel-rpm-interval")

        self._cm.set_setting([0, 255, 0], f"wheel-old-rpm-color1")
        self._cm.set_setting([0, 255, 0], f"wheel-old-rpm-color2")
        self._cm.set_setting([0, 255, 0], f"wheel-old-rpm-color3")

        self._cm.set_setting([255, 0, 0], f"wheel-old-rpm-color4")
        self._cm.set_setting([255, 0, 0], f"wheel-old-rpm-color5")
        self._cm.set_setting([255, 0, 0], f"wheel-old-rpm-color6")
        self._cm.set_setting([255, 0, 0], f"wheel-old-rpm-color7")

        self._cm.set_setting([255, 0, 255], f"wheel-old-rpm-color8")
        self._cm.set_setting([255, 0, 255], f"wheel-old-rpm-color9")
        self._cm.set_setting([255, 0, 255], f"wheel-old-rpm-color10")

        for i in range(MOZA_RPM_LEDS):
            self._blinking_row.set_led_value([0, 255, 255], i, mute=False)

        # for i in range(MOZA_FLAG_LEDS):
        #     self._cm.set_setting([255, 0, 0], f"wheel-flag-color{i+1}")

        self._cm.set_setting(15, "wheel-old-rpm-brightness")
        self._set_combination_settings([0] * 8)


    def shutdown(self):
        """Cleanup when panel is being destroyed."""
        if hasattr(self, '_ac_telemetry') and self._ac_telemetry:
            self._ac_telemetry.stop()
