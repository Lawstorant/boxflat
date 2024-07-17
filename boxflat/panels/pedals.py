from boxflat.panels.settings_panel import SettingsPanel
from boxflat.connection_manager import MozaConnectionManager
from boxflat.widgets import *

class PedalsSettings(SettingsPanel):
    def __init__(self, button_callback: callable, connection_manager: MozaConnectionManager) -> None:
        self._brake_calibration_row = None
        super(PedalsSettings, self).__init__("Pedals", button_callback, connection_manager)


    def set_brake_calibration_active(self, active: bool):
        self._brake_calibration_row.set_active(active)


    def prepare_ui(self) -> None:
        self.add_view_stack()

        # Throttle
        self.add_preferences_page("Throttle")
        self.add_preferences_group("Throttle settings", level_bar=1)
        self._current_group.set_bar_max(65535)
        self._cm.subscribe_cont("pedals-throttle-output", self._current_group.set_bar_level)
        self._cm.subscribe("pedals-throttle-min", self._current_group.set_range_start)
        self._cm.subscribe("pedals-throttle-max", self._current_group.set_range_end)

        # self._add_row(BoxflatEqRow("Throttle Curve", 5, suffix="%"))
        # self._current_row.add_marks(20, 40, 60, 80)
        # self._current_row.add_labels("20%", "40%", "60%", "80%", "100%")
        # self._current_row.set_height(260)
        # self._current_row.add_buttons("Linear", "S Curve", "Exponential", "Parabolic")
        # self._current_row.set_button_value(-1)

        self._add_row(BoxflatSliderRow("Range Start", suffix="%"))
        self._current_row.add_marks(20, 40, 60, 80)
        self._current_row.set_width(380)
        self._current_row.subscribe(lambda v: self._cm.set_setting("pedals-throttle-min", v))
        self._cm.subscribe("pedals-throttle-min", self._current_row.set_value)

        self._add_row(BoxflatSliderRow("Range End", suffix="%"))
        self._current_row.add_marks(20, 40, 60, 80)
        self._current_row.set_width(380)
        self._current_row.subscribe(lambda v: self._cm.set_setting("pedals-throttle-max", v))
        self._cm.subscribe("pedals-throttle-max", self._current_row.set_value)

        self.add_preferences_group("Misc")
        self._add_row(BoxflatSwitchRow("Reverse Direction"))
        self._current_row.subscribe(lambda v: self._cm.set_setting("pedals-throttle-dir", v))
        self._cm.subscribe("pedals-throttle-dir", self._current_row.set_value)

        self._add_row(BoxflatCalibrationRow("Calibration", "Set range"))
        self._current_row.subscribe(lambda v: self._cm.set_setting(f"pedals-throttle-{v}-calibration", 1))

        # Brake
        self.add_preferences_page("Brake")
        self.add_preferences_group("Brake settings", level_bar=1)
        self._current_group.set_bar_max(65535)
        self._cm.subscribe_cont("pedals-brake-output", self._current_group.set_bar_level)
        self._cm.subscribe("pedals-brake-min", self._current_group.set_range_start)
        self._cm.subscribe("pedals-brake-max", self._current_group.set_range_end)

        # self._add_row(BoxflatEqRow("Brake Curve", 5, suffix="%"))
        # self._current_row.add_marks(20, 40, 60, 80)
        # self._current_row.add_labels("20%", "40%", "60%", "80%", "100%")
        # self._current_row.set_height(260)
        # self._current_row.add_buttons("Linear", "S Curve", "Exponential", "Parabolic")
        # self._current_row.set_button_value(-1)

        self._add_row(BoxflatSliderRow("Range Start", suffix="%"))
        self._current_row.add_marks(20, 40, 60, 80)
        self._current_row.set_width(380)
        self._current_row.subscribe(lambda v: self._cm.set_setting("pedals-brake-min", v))
        self._cm.subscribe("pedals-brake-min", self._current_row.set_value)

        self._add_row(BoxflatSliderRow("Range End", suffix="%"))
        self._current_row.add_marks(20, 40, 60, 80)
        self._current_row.set_width(380)
        self._current_row.subscribe(lambda v: self._cm.set_setting("pedals-brake-max", v))
        self._cm.subscribe("pedals-brake-max", self._current_row.set_value)

        self._add_row(BoxflatSliderRow("Pressure Point Setting", suffix="%", subtitle="Higher = less range"))
        self._current_row.add_marks(25, 50, 75)
        self._current_row.subscribe(lambda v: self._cm.set_setting_float("pedals-brake-max-force", v))
        self._cm.subscribe("pedals-brake-max-force", self._current_row.set_value)

        self.add_preferences_group("Misc")
        self._add_row(BoxflatSwitchRow("Reverse Direction"))
        self._current_row.subscribe(lambda v: self._cm.set_setting("pedals-brake-dir", v))
        self._cm.subscribe("pedals-brake-dir", self._current_row.set_value)

        self._brake_calibration_row = BoxflatCalibrationRow("Calibration", "Set range")
        self._add_row(self._brake_calibration_row)
        self._current_row.subscribe(lambda v: self._cm.set_setting(f"pedals-brake-{v}-calibration", 1))
        self._current_row.set_active(False)

        # Clutch
        self.add_preferences_page("Clutch")
        self.add_preferences_group("Clutch settings", level_bar=1)
        self._current_group.set_bar_max(65535)
        self._cm.subscribe_cont("pedals-clutch-output", self._current_group.set_bar_level)
        self._cm.subscribe("pedals-clutch-min", self._current_group.set_range_start)
        self._cm.subscribe("pedals-clutch-max", self._current_group.set_range_end)

        # self._add_row(BoxflatEqRow("Clutch Curve", 5, suffix="%"))
        # self._current_row.add_marks(20, 40, 60, 80)
        # self._current_row.add_labels("20%", "40%", "60%", "80%", "100%")
        # self._current_row.set_height(260)
        # self._current_row.add_buttons("Linear", "S Curve", "Exponential", "Parabolic")
        # self._current_row.set_button_value(-1)

        self._add_row(BoxflatSliderRow("Range Start", suffix="%"))
        self._current_row.add_marks(20, 40, 60, 80)
        self._current_row.set_width(380)
        self._current_row.subscribe(lambda v: self._cm.set_setting("pedals-clutch-min", v))
        self._cm.subscribe("pedals-clutch-min", self._current_row.set_value)

        self._add_row(BoxflatSliderRow("Range End", suffix="%"))
        self._current_row.add_marks(20, 40, 60, 80)
        self._current_row.set_width(380)
        self._current_row.subscribe(lambda v: self._cm.set_setting("pedals-clutch-max", v))
        self._cm.subscribe("pedals-clutch-max", self._current_row.set_value)

        self.add_preferences_group("Misc")
        self._add_row(BoxflatSwitchRow("Reverse Direction"))
        self._current_row.subscribe(lambda v: self._cm.set_setting("pedals-clutch-dir", v))
        self._cm.subscribe("pedals-clutch-dir", self._current_row.set_value)

        self._add_row(BoxflatCalibrationRow("Calibration", "Set range"))
        self._current_row.subscribe(lambda v: self._cm.set_setting(f"pedals-clutch-{v}-calibration", 1))
