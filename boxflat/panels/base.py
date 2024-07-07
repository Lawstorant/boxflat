from boxflat.panels.settings_panel import SettingsPanel
import boxflat.connection_manager as connection_manager

class BaseSettings(SettingsPanel):
    def __init__(self, button_callback) -> None:
        super(BaseSettings, self).__init__("Base", button_callback)
        # self._settings = connection_manager.get_base_settings()

    def _rotation_range(self, value) -> None:
        connection_manager.set_base_setting("angle", int(value/2))
        connection_manager.set_base_setting("limit", int(value/2))

    def _prepare_ui(self) -> None:
        self._add_view_stack()
        self._add_preferences_page("Base")
        self._add_preferences_group("Important settings")

        self._add_title_row("Wheel Rotation Angle", "Round and round")
        self._add_slider_row(
            "", 90, 2700, 540,
            size_request=(570,0),
            marks=[360, 540, 720, 900, 1080, 1440, 1800, 2160],
            callback=self._rotation_range,
            increment=2
        )

        # self._add_slider_row(
        #     "FFB Strength", 0, 100, 70,
        #     marks=[50],
        #     mark_suffix="%",
        #     subtitle="Don't loose your grip!"
        # )

        # self._add_preferences_group("Basic settings")
        # self._add_slider_row(
        #     "Road Sensitivity", 0, 10, 8,
        #     marks=[2, 4]
        # )

        # self._add_slider_row(
        #     "Maximum Wheel Speed", 0, 100, 100,
        #     marks=[30, 50],
        #     mark_suffix="%"
        # )

        # self._add_slider_row(
        #     "Wheel Spring", 0, 100, 0,
        #     marks=[50],
        #     mark_suffix="%"
        # )

        # self._add_slider_row(
        #     "Wheel Damper", 0, 100, 10,
        #     marks=[25, 50],
        #     mark_suffix="%"
        # )

        # self._add_preferences_group("Advenced Settings")
        # self._add_switch_row("Force Feedback Reversal")
        # self._add_slider_row(
        #     "Torque output", 0, 100, 70,
        #     marks=[25, 50, 75],
        #     mark_suffix="%"
        # )

        # self._add_switch_row("Hands-Off Protection")
        # self._add_slider_row(
        #     "Steering Wheel Inertia", 100, 4000, 2800,
        #     marks=[1100, 1550, 2800, 3500]
        # )

        # self._add_slider_row(
        #     "Natural Inertia", 100, 500, 150,
        #     marks=[300]
        # )

        # self._add_slider_row(
        #     "Wheel Friction", 0, 100, 30,
        #     marks=[10, 30],
        #     mark_suffix="%"
        # )

        # self._add_slider_row(
        #     "Speed-depended Damping", 0, 100, 0,
        #     marks=[50],
        #     mark_suffix="%"
        # )

        # self._add_slider_row(
        #     "Speed-depended Damping\nStart Point", 0, 400, 120,
        #     marks=[120],
        #     mark_suffix=" kph"
        # )

        # self._add_preferences_page("Equalizer", "network-cellular-signal-excellent-symbolic")
        # self._add_preferences_group("FFB Effect Equalizer")
        # self._add_title_row("FFB Effect Equalizer", "Work In Progress")

        # self._add_preferences_page("Curve", "network-cellular-signal-excellent-symbolic")
        # self._add_preferences_group("Base FFB Curve")
        # self._add_title_row("Base FFB Curve", "Work In Progress")

        # self._add_preferences_page("Misc", "preferences-other-symbolic")
        # self._add_preferences_group("Misc Settings")
        # self._add_switch_row("Base Status Indicator", subtitle="Does nothing if your base doesn't have it")
        # self._add_slider_row(
        #     "Soft Limit Stiffness", 1, 10, 8,
        #     marks=[5]
        # )

        # self._add_toggle_button_row("Soft Limit Strength",["Soft", "Middle", "Hard"])
        # self._add_switch_row("Soft Limit Game Force Strength", subtitle="I have no idea")
        # self._add_toggle_button_row(
        #     "Temperature Control Strategy",
        #     ["Conservative", "Radical"],
        #     subtitle="Conservative = 50°C, Radical = 60°C")
