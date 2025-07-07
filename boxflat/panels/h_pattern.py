# Copyright (c) 2025, Tomasz Pakuła Using Arch BTW

from boxflat.panels.settings_panel import SettingsPanel
from boxflat.connection_manager import MozaConnectionManager
from boxflat.widgets import *
from boxflat.settings_handler import SettingsHandler
from boxflat.hid_handler import HidHandler

class HPatternSettings(SettingsPanel):
    def __init__(self, button_callback, connection_manager: MozaConnectionManager, settings: SettingsHandler, hid: HidHandler):
        self._slider1 = None
        self._slider2 = None
        self._enable = None
        self._settings = settings
        self._gear_row = BoxflatLabelRow("Current Gear")

        super().__init__("H-Pattern Shifter", button_callback, connection_manager, hid)
        self._cm.subscribe_connected("hpattern-output-y", self.active)


    def active(self, value: int):
        if value < 10:
            value = -1
        super().active(value)
        self._hid_handler.hpattern_connected(self._active)
        if not self._active:
            self._update_gear(0, 0)


    def prepare_ui(self):
        self.add_preferences_group("Throttle blip")

        row1 = BoxflatSliderRow("Auto Blip Output", 0, 100, suffix="% ", increment=10)
        row2 = BoxflatSliderRow("Auto Blip Duration", 0, 1000, subtitle="Miliseconds", increment=50)
        row1.set_active(0)
        row2.set_active(0)
        self._slider1 = row1
        self._slider2 = row2

        self._add_row(BoxflatSwitchRow("Auto Downshift Throttle Blip", subtitle="Easy rev match"))
        self._current_row.subscribe(row1.set_active)
        self._current_row.subscribe(row2.set_active)
        self._current_row.subscribe(self._hid_handler.update_blip_data)
        self._current_row.set_value(self._settings.read_setting("hpattern-blip-enabled") or 0, mute=False)
        self._current_row.subscribe(self._settings.write_setting, "hpattern-blip-enabled")
        self._enable = self._current_row

        self._add_row(row1)
        self._add_row(row2)

        row1.add_marks(25, 50, 75)
        row2.add_marks(250, 500, 750)

        row1.subscribe(lambda v: self._hid_handler.update_blip_data(level=v))
        row2.subscribe(lambda v: self._hid_handler.update_blip_data(duration=v))

        row1.set_value(self._settings.read_setting("hpattern-blip-level"), mute=False)
        row2.set_value(self._settings.read_setting("hpattern-blip-duration"), mute=False)

        row1.subscribe(self._settings.write_setting, "hpattern-blip-level")
        row2.subscribe(self._settings.write_setting, "hpattern-blip-duration")

        self.add_preferences_group("Misc")
        self._add_row(self._gear_row)
        self._update_gear(0, 0)
        self._hid_handler.subscribe("gear", self._update_gear)

        self._add_row(BoxflatCalibrationRow("Device Calibration", "Shift into R > 7th > R > Neutral"))
        self._current_row.subscribe("calibration-start", self._cm.set_setting, "hpattern-calibration-start")
        self._current_row.subscribe("calibration-stop", self._cm.set_setting, "hpattern-calibration-stop")

        self._slider1.disable_cooldown()
        self._slider2.disable_cooldown()
        self._enable.disable_cooldown()

        # self.add_preferences_group()
        self._add_row(BoxflatButtonRow("Restore default settings", "Reset"))
        self._current_row.subscribe(self.reset)


    def _update_gear(self, gear: int, state: int) -> None:
        label = "R"

        if state != 1:
            label = "N"

        elif gear > 0:
            label = str(gear)

        self._gear_row.set_label(label)


    def get_settings(self) -> map:
        return {
            "blip-enabled": self._enable.get_value(),
            "blip-output" : self._slider1.get_value(),
            "blip-level"  : self._slider2.get_value(),
        }


    def set_settings(self, settings: map) -> None:
        self._enable.set_value(settings["blip-enabled"], mute=False)
        self._slider1.set_value(settings["blip-output"], mute=False)
        self._slider2.set_value(settings["blip-level"], mute=False)


    def reset(self, *_) -> None:
        self.set_settings({
            "blip-enabled": 0,
            "blip-output": 0,
            "blip-level": 0,
        })
