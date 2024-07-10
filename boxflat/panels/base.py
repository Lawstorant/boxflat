from boxflat.panels.settings_panel import SettingsPanel
from boxflat.connection_manager import MozaConnectionManager

class BaseSettings(SettingsPanel):
    def __init__(self, button_callback: callable, connection_manager: MozaConnectionManager) -> None:
        self._protection_slider = None
        super(BaseSettings, self).__init__("Base", button_callback, connection_manager)
        # self._settings = self._cm.get_base_settings()

    def _set_center(self) -> None:
        self._cm.set_setting("base-calibration", 1)

    def _set_rotation_range(self, value) -> None:
        self._cm.set_setting("base-maximum-angle", int(value/2))
        self._cm.set_setting("base-limit", int(value/2))

    def _set_ffb_strength(self, value) -> None:
        self._cm.set_setting("base-ffb-strength", int(value)*10)

    def _set_road_sensitivity(self, value) -> None:
        self._cm.set_setting("base-road-sensitivity", int(value)*4 + 10)

    def _set_wheel_speed(self, value) -> None:
        self._cm.set_setting("base-speed", int(value)*10)

    def _set_spring(self, value) -> None:
        self._cm.set_setting("base-spring", int(value)*10)

    def _set_damper(self, value) -> None:
        self._cm.set_setting("base-damper", int(value)*10)

    def _set_reverse(self, value) -> None:
        self._cm.set_setting("base-ffb-reverse", value)

    def _set_torque(self, value) -> None:
        self._cm.set_setting("base-torque", value)

    def _set_protection(self, value) -> None:
        self._protection_slider(value)
        self._cm.set_setting("base-natural-inertia-enable", value)

    def _set_protection_value(self, value) -> None:
        self._cm.set_setting("base-natural-inertia", value)

    def _set_inertia(self, value) -> None:
        self._cm.set_setting("base-inertia", value*10)

    def _set_friction(self, value) -> None:
        self._cm.set_setting("base-friction", value*10)

    def _set_speed_damping(self, value) -> None:
        self._cm.set_setting("base-speed-damping", value)

    def _set_speed_damping_point(self, value) -> None:
        self._cm.set_setting("base-speed-damping-point", value)

    def _set_led_status(self, value) -> None:
        self._cm.set_setting("main-set-led-status", value)

    def _set_soft_limit_stiffness(self, value) -> None:
        self._cm.set_setting("base-soft-limit-stiffness", round((400/9)*(value-1) + 100))

    def _set_soft_limit_strength(self, value) -> None:
        if value == "Soft":
            self._cm.set_setting("base-soft-limit-strength", 56)
        elif value == "Middle":
            self._cm.set_setting("base-soft-limit-strength", 78)
        elif value == "Hard":
            self._cm.set_setting("base-soft-limit-strength", 100)

    def _set_soft_limit_retain(self, value) -> None:
        self._cm.set_setting("base-soft-limit-retain", value)

    def _set_temperature_strategy(self, value) -> None:
        if value == "Conservative":
            self._cm.set_setting("base-temp-strategy", 0)
        elif value == "Radical":
            self._cm.set_setting("base-temp-strategy", 1)


    def prepare_ui(self) -> None:
        self.add_view_stack()
        self.add_preferences_page("Base")
        self.add_preferences_group("Important settings")

        self.add_title_row("Wheel Rotation Angle", "Round and round")
        self.add_slider_row("", 90, 2700, 540,
            size_request=(550,0),
            marks=[360, 540, 720, 900, 1080, 1440, 1800, 2160],
            callback=self._set_rotation_range,
            increment=2)

        self.add_slider_row("FFB Strength", 0, 100, 70,
            marks=[50],
            mark_suffix="%",
            subtitle="Don't lose your grip!",
            callback=self._set_ffb_strength)

        self.add_button_row("Set Center", "Calibrate", callback=self._set_center)

        self.add_preferences_group("Basic settings")
        self.add_slider_row("Road Sensitivity", 0, 10, 8,
            marks=[2, 4, 6, 8],
            callback=self._set_road_sensitivity)

        self.add_slider_row("Maximum Wheel Speed", 0, 200, 100,
            marks=[50, 100, 150],
            mark_suffix="%",
            callback=self._set_wheel_speed)

        self.add_slider_row("Wheel Spring", 0, 100, 0,
            marks=[50],
            mark_suffix="%",
            callback=self._set_spring)

        self.add_slider_row("Wheel Damper", 0, 100, 10,
            marks=[10, 25, 50],
            mark_suffix="%",
            callback=self._set_damper)

        # Advenced settings
        self.add_preferences_group("Advenced Settings")
        self.add_switch_row("Force Feedback Reversal", callback=self._set_reverse)
        self.add_slider_row("Torque output", 0, 100, 70,
            marks=[25, 50, 75],
            mark_suffix="%",
            callback=self._set_torque)

        self.add_switch_row("Hands-Off Protection", callback=self._set_protection)
        self._protection_slider = self.add_slider_row("Steering Wheel Inertia", 100, 4000, 2800,
            marks=[1100, 1550, 2800, 3500],
            active=False,
            callback=self._set_protection_value)

        self.add_slider_row("Natural Inertia", 100, 500, 150,
            marks=[150, 300],
            callback=self._set_inertia)

        self.add_slider_row("Wheel Friction", 0, 100, 30,
            marks=[10, 30],
            mark_suffix="%",
            callback=self._set_friction)

        self.add_slider_row("Speed-depended Damping", 0, 100, 0,
            marks=[50],
            mark_suffix="%",
            callback=self._set_speed_damping)

        self.add_slider_row("Speed-depended Damping", 0, 400, 120,
            marks=[120],
            mark_suffix=" kph",
            subtitle="Start Point",
            callback=self._set_speed_damping_point)

        # self.add_preferences_page("Equalizer", "network-cellular-signal-excellent-symbolic")
        # self.add_preferences_group("FFB Effect Equalizer")
        # self.add_title_row("FFB Effect Equalizer", "Work In Progress")

        # self.add_preferences_page("Curve", "network-cellular-signal-excellent-symbolic")
        # self.add_preferences_group("Base FFB Curve")
        # self.add_title_row("Base FFB Curve", "Work In Progress")

        self.add_preferences_page("Misc", "preferences-other-symbolic")
        self.add_preferences_group("Misc Settings")
        self.add_switch_row("Base Status Indicator",
                            subtitle="Does nothing if your base doesn't have it",
                            callback=self._set_led_status)
        self.add_slider_row("Soft Limit Stiffness", 1, 10, 8,
            marks=[4, 6, 8],
            callback=self._set_soft_limit_stiffness)

        self.add_toggle_button_row("Soft Limit Strength",["Soft", "Middle", "Hard"],
            callback=self._set_soft_limit_strength)
        self.add_switch_row("Soft Limit Game Force Strength", subtitle="I have no idea",
            callback=self._set_soft_limit_retain)

        self.add_toggle_button_row(
            "Temperature Control Strategy",
            ["Conservative", "Radical"],
            subtitle="Conservative = 50°C, Radical = 60°C",
            callback=self._set_temperature_strategy
        )
