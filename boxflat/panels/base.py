from boxflat.panels.settings_panel import SettingsPanel
from boxflat.connection_manager import MozaConnectionManager

from boxflat.widgets import *

class BaseSettings(SettingsPanel):
    def __init__(self, button_callback: callable, connection_manager: MozaConnectionManager) -> None:
        self._protection_slider = None
        super(BaseSettings, self).__init__("Base", button_callback, connection_manager)
        # self._settings = self._cm.get_base_settings()

    def _set_soft_limit_strength(self, value) -> None:
        if value == "Soft":
            self._cm.set_setting("base-soft-limit-strength", 56)
        elif value == "Middle":
            self._cm.set_setting("base-soft-limit-strength", 78)
        elif value == "Hard":
            self._cm.set_setting("base-soft-limit-strength", 100)


    def prepare_ui(self) -> None:
        self.add_view_stack()
        self.add_preferences_page("Base")
        self.add_preferences_group("Important settings")

        self._add_row(BoxflatRow("Wheel Rotation Angle", "Round and round"))

        self._add_row(BoxflatSliderRow("", range_start=90, range_end=2700, increment=2))
        self._current_row.width = 550
        self._current_row.add_marks(360, 540, 720, 900, 1080, 1440, 1800, 2160)
        self._current_row.subscribe(lambda v: self._cm.set_setting("base-maximum-angle", round(v/2)))
        self._current_row.subscribe(lambda v: self._cm.set_setting("base-limit", round(v/2)))
        self._cm.subscribe("base-maximum-angle", self._current_row.set_value)

        self._add_row(BoxflatSliderRow("FFB Strength", suffix="%"))
        self._current_row.add_marks(25, 50, 75)
        self._current_row.subscribe(lambda v: self._cm.set_setting("base-ffb-strength", v*10))
        self._cm.subscribe("base-ffb-strength", lambda v: self._current_row.set_value(round(v/10)))

        self._add_row(BoxflatCalibrationRow("Set Center"))
        self._current_row.subscribe(lambda v: self._cm.set_setting("base-calibration", 1))

        # Basic settings
        self.add_preferences_group("Basic settings")
        self._add_row(BoxflatSliderRow("Road Sensitivity", range_end=10))
        self._current_row.add_marks(2, 4, 6, 8)
        self._current_row.subscribe(lambda v: self._cm.set_setting("base-road-sensitivity", v*4 + 10))
        self._cm.subscribe("base-road-sensitivity",
                           lambda v: self._current_row.set_value(round((v-10)/4)))

        self._add_row(BoxflatSliderRow("Maximum Wheel Speed", suffix="%", range_end=200))
        self._current_row.add_marks(50, 100, 150)
        self._current_row.subscribe(lambda v: self._cm.set_setting("base-speed", int(v)*10))
        self._cm.subscribe("base-speed", lambda v: self._current_row.set_value(round(v/10)))

        self._add_row(BoxflatSliderRow("Wheel Spring", suffix="%"))
        self._current_row.add_marks(50)
        self._current_row.subscribe(lambda v: self._cm.set_setting("base-spring", int(v)*10))
        self._cm.subscribe("base-spring", lambda v: self._current_row.set_value(round(v/10)))

        self._add_row(BoxflatSliderRow("Wheel Spring", suffix="%"))
        self._current_row.add_marks(10, 25, 50)
        self._current_row.subscribe(lambda v: self._cm.set_setting("base-damper", int(v)*10))
        self._cm.subscribe("base-damper", lambda v: self._current_row.set_value(round(v/10)))

        # Advenced settings
        self.add_preferences_group("Advenced Settings")
        self._add_row(BoxflatSwitchRow("Force Feedback Reversal"))
        self._current_row.subscribe(lambda v: self._cm.set_setting("base-ffb-reverse", v))
        self._cm.subscribe("base-ffb-reverse", self._current_row.set_value)

        self._add_row(BoxflatSliderRow("Torque output", suffix="%"))
        self._current_row.add_marks(25, 50, 75)
        self._current_row.subscribe(lambda v: self._cm.set_setting("base-torque", v))
        self._cm.subscribe("base-torque", self._current_row.set_value)

        self._add_row(BoxflatSwitchRow("Hands-Off Protection"))
        self._current_row.subscribe(lambda v: self._cm.set_setting("base-natural-inertia-enable", v))
        self._cm.subscribe("base-natural-inertia-enable", self._current_row.set_value)

        self._add_row(BoxflatSliderRow("Steering Wheel Inertia", range_start=100, range_end=4000))
        self._current_row.add_marks(1100, 1550, 2800, 3500)
        self._current_row.subscribe(lambda v: self._cm.set_setting("base-natural-inertia", v))
        self._cm.subscribe("base-natural-inertia", self._current_row.set_value)

        self._add_row(BoxflatSliderRow("Natural Inertia", range_start=100, range_end=500))
        self._current_row.add_marks(150, 300)
        self._current_row.subscribe(lambda v: self._cm.set_setting("base-inertia", v*10))
        self._cm.subscribe("base-inertia", self._current_row.set_value)

        self._add_row(BoxflatSliderRow("Wheel Friction", suffix="%"))
        self._current_row.add_marks(10, 30)
        self._current_row.subscribe(lambda v: self._cm.set_setting("base-friction", v*10))
        self._cm.subscribe("base-friction", lambda v: self._current_row.set_value(round(v/10)))

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
        self._current_row.subtitle = "Does nothing if your base doesn't have it"
        self._current_row.subscribe(lambda v: self._cm.set_setting("main-set-led-status", v))
        self._cm.subscribe("main-get-led-status", self._current_row.set_value)

        self._add_row(BoxflatSliderRow("Soft Limit Stiffness", range_start=1, range_end=10))
        self._current_row.add_marks(4, 6, 8)
        self._current_row.subscribe(
            lambda v: self._cm.set_setting("base-soft-limit-stiffness", round((400/9) * (v-1) + 100)))
        self._cm.subscribe("base-soft-limit-stiffness",
            lambda v: self._current_row.set_value(round((v-100) / (400/9) + 1)))

        self._add_row(BoxflatToggleButtonRow("Soft Limit Strength"))
        self._current_row.add_buttons("Soft", "Middle", "Hard")
        self._current_row.subscribe(
            lambda v: self._cm.set_setting("base-soft-limit-strength", v*22 + 56))
        self._cm.subscribe("base-soft-limit-strength",
            lambda v: self._current_row.set_value(round((v-56) / 22)))

        self._add_row(BoxflatSwitchRow("Soft Limit Game Force Strength"))
        self._current_row.subtitle = "I have no idea"
        self._current_row.subscribe(lambda v: self._cm.set_setting("base-soft-limit-retain", v))
        self._cm.subscribe("base-soft-limit-retain", self._current_row.set_value)

        self._add_row(BoxflatToggleButtonRow("Temperature Control Strategy",))
        self._current_row.subtitle = "Conservative = 50°C, Radical = 60°C"
        self._current_row.add_buttons("Conservative", "Radical")
        self._current_row.subscribe(lambda v: self._cm.set_setting("base-temp-strategy", v))
        self._cm.subscribe("base-temp-strategy", self._current_row.set_value)


    def __prepare_eq(self) -> None:
        self.add_preferences_page("Equalizer", "network-cellular-signal-excellent-symbolic")
        self.add_preferences_group("Equalizer")
        self._add_row(BoxflatRow("FFB Effect Equalizer", "Work In Progress"))


    def __prepare_curve(self) -> None:
        self.add_preferences_page("Curve", "network-cellular-signal-excellent-symbolic")
        self.add_preferences_group("Curve")
        self._add_row(BoxflatRow("Base FFB Curve", "Work In Progress"))
