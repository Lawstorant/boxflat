from boxflat.panels.settings_panel import SettingsPanel
from boxflat.connection_manager import MozaConnectionManager

class BaseSettings(SettingsPanel):
    def __init__(self, button_callback: callable, connection_manager: MozaConnectionManager) -> None:
        super(BaseSettings, self).__init__("Base", button_callback, connection_manager)
        # self._settings = self._cm.get_base_settings()

    def _set_rotation_range(self, value) -> None:
        self._cm.set_base_setting("base-maximum-angle", int(value/2))
        self._cm.set_base_setting("base-limit", int(value/2))

    def _set_ffb_strength(self, value) -> None:
        self._cm.set_base_setting("base-ffb-strength", int(value)*10)

    def prepare_ui(self) -> None:
        self.add_view_stack()
        self.add_preferences_page("Base")
        self.add_preferences_group("Important settings")

        self.add_title_row("Wheel Rotation Angle", "Round and round")
        self.add_slider_row(
            "", 90, 2700, 540,
            size_request=(550,0),
            marks=[360, 540, 720, 900, 1080, 1440, 1800, 2160],
            callback=self._set_rotation_range,
            increment=2
        )

        self.add_slider_row(
            "FFB Strength", 0, 100, 70,
            marks=[50],
            mark_suffix="%",
            subtitle="Don't lose your grip!",
            callback=self._set_ffb_strength
        )

        # self.add_preferences_group("Basic settings")
        # self.add_slider_row(
        #     "Road Sensitivity", 0, 10, 8,
        #     marks=[2, 4]
        # )

        # self.add_slider_row(
        #     "Maximum Wheel Speed", 0, 100, 100,
        #     marks=[30, 50],
        #     mark_suffix="%"
        # )

        # self.add_slider_row(
        #     "Wheel Spring", 0, 100, 0,
        #     marks=[50],
        #     mark_suffix="%"
        # )

        # self.add_slider_row(
        #     "Wheel Damper", 0, 100, 10,
        #     marks=[25, 50],
        #     mark_suffix="%"
        # )

        # self.add_preferences_group("Advenced Settings")
        # self.add_switch_row("Force Feedback Reversal")
        # self.add_slider_row(
        #     "Torque output", 0, 100, 70,
        #     marks=[25, 50, 75],
        #     mark_suffix="%"
        # )

        # self.add_switch_row("Hands-Off Protection")
        # self.add_slider_row(
        #     "Steering Wheel Inertia", 100, 4000, 2800,
        #     marks=[1100, 1550, 2800, 3500]
        # )

        # self.add_slider_row(
        #     "Natural Inertia", 100, 500, 150,
        #     marks=[300]
        # )

        # self.add_slider_row(
        #     "Wheel Friction", 0, 100, 30,
        #     marks=[10, 30],
        #     mark_suffix="%"
        # )

        # self.add_slider_row(
        #     "Speed-depended Damping", 0, 100, 0,
        #     marks=[50],
        #     mark_suffix="%"
        # )

        # self.add_slider_row(
        #     "Speed-depended Damping\nStart Point", 0, 400, 120,
        #     marks=[120],
        #     mark_suffix=" kph"
        # )

        # self.add_preferences_page("Equalizer", "network-cellular-signal-excellent-symbolic")
        # self.add_preferences_group("FFB Effect Equalizer")
        # self.add_title_row("FFB Effect Equalizer", "Work In Progress")

        # self.add_preferences_page("Curve", "network-cellular-signal-excellent-symbolic")
        # self.add_preferences_group("Base FFB Curve")
        # self.add_title_row("Base FFB Curve", "Work In Progress")

        # self.add_preferences_page("Misc", "preferences-other-symbolic")
        # self.add_preferences_group("Misc Settings")
        # self.add_switch_row("Base Status Indicator", subtitle="Does nothing if your base doesn't have it")
        # self.add_slider_row(
        #     "Soft Limit Stiffness", 1, 10, 8,
        #     marks=[5]
        # )

        # self.add_toggle_button_row("Soft Limit Strength",["Soft", "Middle", "Hard"])
        # self.add_switch_row("Soft Limit Game Force Strength", subtitle="I have no idea")
        # self.add_toggle_button_row(
        #     "Temperature Control Strategy",
        #     ["Conservative", "Radical"],
        #     subtitle="Conservative = 50°C, Radical = 60°C")
