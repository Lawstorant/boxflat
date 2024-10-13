# Copyright (c) 2024, Tomasz Pakuła Using Arch BTW

from boxflat.panels.settings_panel import SettingsPanel
from boxflat.connection_manager import MozaConnectionManager
from boxflat.widgets import *
from boxflat.settings_handler import PersistentSettingsHandler

class HPatternSettings(SettingsPanel):
    def __init__(self, button_callback, connection_manager: MozaConnectionManager, settings: PersistentSettingsHandler):
        self._slider1 = None
        self._slider2 = None
        self._settings = settings
        super().__init__("H-Pattern Shifter", button_callback, connection_manager)
        self._cm.subscribe_connected("hpattern-paddle-sync", self.active)


    def active(self, value: int):
        value = -1 if value != 0 else value
        super().active(value)


    def prepare_ui(self):
        self.add_preferences_group("Warning")
        self._add_row(BoxflatRow("These options are not operational", "Work in progress"))

        self.add_preferences_group("Shifter Settings")

        row1 = BoxflatSliderRow("Auto Blip Output", 0, 100, increment=10)
        row2 = BoxflatSliderRow("Auto Blip Duration", 0, 1000, subtitle="Miliseconds", increment=50)

        self._add_row(BoxflatSwitchRow("Auto Downshift Throttle Blip", subtitle="Easy rev match"))
        self._current_row.subscribe(row1.set_active)
        self._current_row.subscribe(row2.set_active)

        self._add_row(row1)
        self._add_row(row2)

        row1.add_marks(50)
        row2.add_marks(250, 500, 750)

        row1.set_value(self._settings.read_setting("hpattern-blip-level"), mute=False)
        row2.set_value(self._settings.read_setting("hpattern-blip-duration"), mute=False)

        row1.subscribe(self._settings.write_setting, "hpattern-blip-level")
        row2.subscribe(self._settings.write_setting, "hpattern-blip-duration")

        self.add_preferences_group()
        self._add_row(BoxflatCalibrationRow("Device Calibration", "Shift into R > 7th > R > Neutral"))
        self._current_row.subscribe("calibration-start", self._cm.set_setting, "hpattern-calibration-start")
        self._current_row.subscribe("calibration-stop", self._cm.set_setting, "hpattern-calibration-stop")
