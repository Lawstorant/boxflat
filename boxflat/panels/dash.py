# Copyright (c) 2025, Tomasz Pakuła Using Arch BTW

from boxflat.panels.settings_panel import SettingsPanel
from boxflat.connection_manager import MozaConnectionManager
from boxflat.bitwise import *
from boxflat.widgets import *

from boxflat.hid_handler import MozaAxis
from boxflat.settings_handler import SettingsHandler

from zlib import crc32
from boxflat.bitwise import le32, le16

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

class DashSettings(SettingsPanel):
    def __init__(self, button_callback, connection_manager: MozaConnectionManager, hid_handler, settings: SettingsHandler):
        self._settings = settings
        self._blinking_row = None

        self._split = None
        self._timing_row = None
        self._timing_preset_row = None

        self._sequence = 0

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

        super().__init__("Dash", button_callback, connection_manager, hid_handler)
        self._cm.subscribe_connected("dash-rpm-indicator-mode", self.active)


    def active(self, value: int):
        initial = self._active
        super().active(value)

        # only set blink colors if dash freshly connected
        if not self._active or initial:
            return

        # for i in range(MOZA_RPM_LEDS):
        #     self._cm.set_setting(self._blinking_row.get_value(i), f"dash-rpm-blink-color{i+1}")
        #     self._cm.set_setting(self._blinking_row.get_value(i), f"dash-rpm-blink-color{i+1}")


    def prepare_ui(self):
        self.add_view_stack()
        self.add_preferences_page("Display")
        self.add_preferences_group("Display settings")

        self._add_row(BoxflatSliderRow("Brightness", increment=10))
        self._current_row.add_marks(25, 50, 75)
        self._current_row.subscribe(self.brightness)

        self.add_preferences_page("Dash")
        self.add_preferences_group("Indicator modes")

        self._add_row(BoxflatToggleButtonRow("RPM Indicator Mode"))
        self._current_row.add_buttons("Off", " RPM ", "On ")
        self._current_row.subscribe(self._cm.set_setting, "dash-rpm-indicator-mode")
        self._cm.subscribe("dash-rpm-indicator-mode", self._current_row.set_value)

        self._add_row(BoxflatToggleButtonRow("Flags Indicator"))
        self._current_row.add_buttons("Off", "Flags", "On ")
        self._current_row.subscribe(self._cm.set_setting, "dash-flags-indicator-mode")
        self._cm.subscribe("dash-flags-indicator-mode", self._current_row.set_value)


        self.add_preferences_group("RPM settings")
        self._add_row(BoxflatToggleButtonRow("RPM Indicator Display Mode"))
        self._current_row.add_buttons("Mode 1", "Mode 2")
        self._current_row.subscribe(self._cm.set_setting, "dash-rpm-display-mode")
        self._cm.subscribe("dash-rpm-display-mode", self._current_row.set_value)

        self._add_row(BoxflatToggleButtonRow("RPM Mode"))
        self._current_row.add_buttons("Percent", "RPM")
        self._current_row.subscribe(self._cm.set_setting, "dash-rpm-mode")
        self._current_row.subscribe(self._reconfigure_timings)
        self._cm.subscribe("dash-rpm-mode", self._current_row.set_value)

        self.add_preferences_group("Timings")
        self._timing_row = BoxflatEqRow("RPM Indicator Timing", 10, "Is it my turn now?",
            button_row=False, draw_marks=False)

        self._add_row(self._timing_row)
        self._timing_row.add_buttons("Early", "Normal", "Late")
        # self._timing_row.add_buttons("Center")
        self._timing_row.subscribe(self._set_rpm_timings_preset)
        self._timing_row.subscribe_sliders(self._set_rpm_timings)
        for i in range(MOZA_RPM_LEDS):
            self._timing_row.add_labels(f"RPM{i+1}", index=i)


        self._timing_row2 = BoxflatEqRow("RPM Indicator Timing", 10, "Is it my turn now?",
            range_start=2000, range_end=18_000, button_row=False, draw_marks=False, increment=100)

        self._add_row(self._timing_row2)
        self._timing_row2.add_buttons("Early", "Normal", "Late")
        self._timing_row2.subscribe(self._set_rpm_timings2_preset)
        self._timing_row2.set_present(0)

        for i in range(MOZA_RPM_LEDS):
            self._timing_row2.add_labels(f"RPM{i+1}", index=i)
            self._timing_row2.subscribe_slider(i, self._cm.set_setting, f"dash-rpm-value{i+1}")
            self._cm.subscribe(f"dash-rpm-value{i+1}", self._timing_row2.set_slider_value, i)
        self._cm.subscribe(f"dash-rpm-value10", self._get_rpm_timings2_preset)


        self._cm.subscribe("dash-rpm-timings", self._get_rpm_timings)
        self._cm.subscribe("dash-rpm-timings", self._get_rpm_timings_preset)
        self._cm.subscribe("dash-rpm-mode", self._reconfigure_timings)


        self._add_row(BoxflatSliderRow("Blinking Interval", range_end=1000, subtitle="Miliseconds", increment=50))
        self._current_row.add_marks(125, 250, 375, 500, 625, 750, 875)
        self._current_row.subscribe(self._cm.set_setting, "dash-rpm-interval")
        self._cm.subscribe("dash-rpm-interval", self._current_row.set_value)

        # self.add_preferences_group()
        # self._add_row(BoxflatButtonRow("Sync settings with wheel", "Sync"))
        # self._current_row.subscribe(lambda v: Thread(target=self._sync_from_wheel, daemon=True).start())
        # self._cm.subscribe_connected("wheel-telemetry-mode", self._current_group.set_present, 1)

        self._add_row(BoxflatButtonRow("Restore default settings", "Reset"))
        self._current_row.subscribe(self.reset)
        self._current_row.subscribe(self.reset)


        self.add_preferences_page("Colors")
        self.add_preferences_group("RPM Colors")
        self._add_row(BoxflatNewColorPickerRow())
        for i in range(MOZA_RPM_LEDS):
            self._current_row.subscribe(f"color{i}", self._cm.set_setting, f"dash-rpm-color{i+1}")
            self._cm.subscribe(f"dash-rpm-color{i+1}", self._current_row.set_led_value, i)

        self.add_preferences_group("RPM Blinking")
        self._current_group.set_description("These colors are not saved to the dash")
        self._blinking_row = BoxflatNewColorPickerRow()
        self._add_row(self._blinking_row)
        for i in range(MOZA_RPM_LEDS):
            name = f"dash-rpm-blink-color{i+1}"
            self._current_row.set_led_value(self._settings.read_setting(name), i)
            self._current_row.subscribe(f"color{i}", self._cm.set_setting, name)
            self._current_row.subscribe(f"color{i}", self._settings.write_setting, name)

        self.add_preferences_group("Flag Default Colors")
        self._current_group.set_description("More to come...")
        self._add_row(BoxflatNewColorPickerRow(pickers=6))
        for i in range(MOZA_FLAG_LEDS):
            self._current_row.subscribe(f"color{i}", self._cm.set_setting, f"dash-flag-color{i+1}")
            self._cm.subscribe(f"dash-flag-color{i+1}", self._current_row.set_led_value, i)

        self.add_preferences_group("Brightness")
        self._add_row(BoxflatSliderRow("RPM Brightness", range_end=15))
        self._current_row.add_marks(5, 10)
        self._current_row.subscribe(self._cm.set_setting, "dash-rpm-brightness")
        self._cm.subscribe("dash-rpm-brightness", self._current_row.set_value)

        self._add_row(BoxflatSliderRow("Flag Brightness", range_end=15))
        self._current_row.add_marks(5, 10)
        self._current_row.subscribe(self._cm.set_setting, "dash-flags-brightness")
        self._cm.subscribe("dash-flags-brightness", self._current_row.set_value)

        self.add_preferences_group()
        self._add_row(BoxflatButtonRow("Dash indicator test", "Test"))
        self._current_row.subscribe(self.start_test)

        # self.add_preferences_group("Telemetry flag")
        # self._add_row(BoxflatNewColorPickerRow(""))
        # for i in range(MOZA_RPM_LEDS):
        #     self._cm.subscribe(f"dash-flag-color{i+1}", self._current_row.set_led_value, i)


    def _set_rpm_timings(self, timings: list):
        self._cm.set_setting(timings, "dash-rpm-timings")


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
            self._cm.set_setting(value, f"dash-rpm-value{i+1}", exclusive=True)
            time.sleep(0.005)
            self._cm.set_setting(value, f"dash-rpm-value{i+1}")
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


    def start_test(self, *args):
        self._test_thread = Thread(daemon=True, target=self._dash_rpm_test).start()


    def _dash_rpm_test(self, *args):
        self._cm.set_setting(0, "dash-send-telemetry")
        time.sleep(0.2)
        initial_mode = self._cm.get_setting("dash-rpm-indicator-mode", exclusive=True)
        initial_flag_mode = self._cm.get_setting("dash-flags-indicator-mode", exclusive=True)

        self._cm.set_setting(1, "dash-rpm-indicator-mode", exclusive=True)
        self._cm.set_setting(1, "dash-flags-indicator-mode", exclusive=True)

        t = 0.08
        for i in range(10):
            val = bit(i)
            self._cm.set_setting(val, "dash-send-telemetry")
            time.sleep(t)

        for i in reversed(range(1,9)):
            val = bit(i)
            self._cm.set_setting(val, "dash-send-telemetry")
            time.sleep(t)

        val = 0
        self._cm.set_setting(val, "dash-send-telemetry")
        time.sleep(t)
        for i in range(10):
            val = set_bit(val, i)
            self._cm.set_setting(val, "dash-send-telemetry")
            time.sleep(t)

        for i in range(9):
            val = unset_bit(val, i)
            self._cm.set_setting(val, "dash-send-telemetry")
            time.sleep(t)

        for i in reversed(range(10)):
            val = set_bit(val, i)
            self._cm.set_setting(val, "dash-send-telemetry")
            time.sleep(t)

        time.sleep(0.2)
        val = modify_bit(0,15)
        self._cm.set_setting(val, "dash-send-telemetry")
        time.sleep(.8)

        self._cm.set_setting(val, "dash-send-telemetry")
        time.sleep(.8)

        self._cm.set_setting(0, "dash-send-telemetry")
        self._cm.set_setting([255,0,0] * 6, "dash-flag-colors")
        time.sleep(.9)

        self._cm.set_setting(0, "dash-send-telemetry")
        self._cm.set_setting([255,0,0] * 6, "dash-flag-colors")
        time.sleep(.9)

        self._cm.set_setting(0, "dash-send-telemetry")
        self._cm.set_setting([0,255,0] * 6, "dash-flag-colors")
        time.sleep(.9)

        self._cm.set_setting(0, "dash-send-telemetry")
        self._cm.set_setting([0,255,0] * 6, "dash-flag-colors")
        time.sleep(.9)

        self._cm.set_setting(0, "dash-send-telemetry")
        self._cm.set_setting([0,0,255] * 6, "dash-flag-colors")
        time.sleep(.9)

        self._cm.set_setting(0, "dash-send-telemetry")
        self._cm.set_setting([0,0,255] * 6, "dash-flag-colors")
        time.sleep(.9)

        self._cm.set_setting(initial_mode, "dash-rpm-indicator-mode", exclusive=True)
        self._cm.set_setting(initial_mode, "dash-flags-indicator-mode", exclusive=True)


    def reset(self, *_) -> None:
        self._set_rpm_timings_preset(0)
        self._set_rpm_timings2_preset(0)

        self._cm.set_setting(1, "dash-rpm-indicator-mode")
        self._cm.set_setting(1, "dash-flags-indicator-mode")
        self._cm.set_setting(0, "dash-rpm-display-mode")
        self._cm.set_setting(0, "dash-rpm-mode")

        self._set_rpm_timings_preset(0)
        self._set_rpm_timings2_preset(0)

        self._cm.set_setting(250, "dash-rpm-interval")

        self._cm.set_setting([0, 255, 0], f"dash-rpm-color1")
        self._cm.set_setting([0, 255, 0], f"dash-rpm-color2")
        self._cm.set_setting([0, 255, 0], f"dash-rpm-color3")

        self._cm.set_setting([255, 0, 0], f"dash-rpm-color4")
        self._cm.set_setting([255, 0, 0], f"dash-rpm-color5")
        self._cm.set_setting([255, 0, 0], f"dash-rpm-color6")
        self._cm.set_setting([255, 0, 0], f"dash-rpm-color7")

        self._cm.set_setting([255, 0, 255], f"dash-rpm-color8")
        self._cm.set_setting([255, 0, 255], f"dash-rpm-color9")
        self._cm.set_setting([255, 0, 255], f"dash-rpm-color10")

        for i in range(MOZA_RPM_LEDS):
            self._blinking_row.set_led_value([0, 255, 255], i, mute=False)

        for i in range(MOZA_FLAG_LEDS):
            self._cm.set_setting([255, 0, 255], f"dash-flag-color{i+1}")

        self._cm.set_setting(15, "dash-rpm-brightness")
        self._cm.set_setting(15, "dash-flags-brightness")


    def get_seqeunce(self) -> bytes:
        self._sequence += 1
        return le16(self._sequence)


    def prepare_display_data(self, command_id, value, padding=0, sequence=None) -> bytes:
        length = (2 + padding) * 4

        data = bytearray()
        data.extend(le32(command_id))
        data.extend(le32(value))
        if padding > 0:
            data.extend(bytes(padding * 4))

        data2 = bytearray()

        data2.append(0xff)
        data2.extend(le32(length))
        data2.extend(le32(crc32(data)))
        data2.extend(data)
        data2.extend(le32(crc32(data2)))

        if not sequence:
            sequence = self.get_seqeunce()

        data2.insert(0, sequence[0])
        data2.insert(1, sequence[1])

        return bytes(data2)


    def brightness(self, value: int) -> None:
        # command = 1
        # self._cm.set_setting(self.prepare_display_data(0x0e, 100, 0), "dash-display-data")
        # sleep(0.1)
        # self._cm.set_setting(self.prepare_display_data(command, value, 0), "dash-display-data")
        # sleep(0.1)
        # sequence = self.get_seqeunce()
        # self._cm.set_setting(sequence, "dash-sequence-data2")
        self._cm.set_setting(self.prepare_display_data(1, value, 0), "dash-display-data")
        self._cm.set_setting(self.prepare_display_data(1, value, 0), "dash-display-data2")
