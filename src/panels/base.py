import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Gdk, Adw
from panels.settings_panel import SettingsPanel
import connection_manager

class BaseSettings(SettingsPanel):
    def __init__(self, button_callback) -> None:
        super(BaseSettings, self).__init__("Base", button_callback)
        # self._settings = connection_manager.get_base_settings()
        self.prepare_ui()

    def apply(self, *arg) -> None:
        super(BaseSettings, self).apply()
        print("Applying base settings...")
        # connection_manager.set_base_settings()

    def slider_rotation_changed(self, slider) -> None:
        value = slider.get_value()
        if value % 2:
            slider.set_value(value + 1)
            value += 1

    def prepare_ui(self) -> None:
        self._add_preferences_page()
        self._add_preferences_group("Important settings")

        self._add_title_row("Wheel Rotation Angle", "Round and round")
        self._add_slider_row(
            "", 90, 2700, 540,
            size_request=(570,0),
            marks=[360, 540, 720, 900, 1080, 1800],
            callback=self.slider_rotation_changed
        )

        self._add_slider_row(
            "FFB Strength", 0, 100, 70,
            marks=[50],
            mark_suffix="%",
            subtitle="Don't loose your grip!"
        )

        self._add_preferences_group("Basic settings")
        self._add_slider_row(
            "Road Sensitivity", 0, 10, 8,
            marks=[2, 4]
        )

        self._add_slider_row(
            "Maximum Wheel Speed", 0, 100, 100,
            marks=[30, 50],
            mark_suffix="%"
        )

        self._add_slider_row(
            "Wheel Spring", 0, 100, 0,
            marks=[50],
            mark_suffix="%"
        )

        self._add_slider_row(
            "Wheel Damper", 0, 100, 10,
            marks=[25, 50],
            mark_suffix="%"
        )

        self._add_preferences_group("Advenced Settings")
        self._add_switch_row("Force Feedback Reversal")
        self._add_slider_row(
            "Torque output", 0, 100, 70,
            marks=[25, 50, 75],
            mark_suffix="%"
        )

        self._add_switch_row("Hands-Off Protection")
        self._add_slider_row(
            "Steering Wheel Inertia", 100, 4000, 2800,
            marks=[1250, 2800, 3500]
        )

        self._add_slider_row(
            "Natural Inertia", 100, 500, 150,
            marks=[300]
        )

        self._add_slider_row(
            "Wheel Friction", 0, 100, 30,
            marks=[10, 30],
            mark_suffix="%"
        )

        self._add_slider_row(
            "Speed-depended Damping", 0, 100, 0,
            marks=[50],
            mark_suffix="%"
        )

        self._add_slider_row(
            "Speed-depended Damping Start Point", 0, 400, 120,
            marks=[120],
            mark_suffix=" kph"
        )

        self._add_preferences_group("Graphs")
        self._add_title_row("FFB Effect Equalizer", "Work In Progress")
        self._add_title_row("Base FFB Curve", "Work In Progress")

        self._add_preferences_group("Misc Settings")
        self._add_switch_row("Base Status Indicator", subtitle="Does nothing if your base doesn't have it")
        self._add_slider_row(
            "Soft Limit Stiffness", 1, 10, 8,
            marks=[5]
        )

        self._add_combo_row("Soft Limit Strength", {
            100: "Soft",
            78: "Middle",
            56: "Hard"
        })

        self._add_switch_row("Soft Limit Game Force Strength", subtitle="I have no idea")
        self._add_combo_row("Temperature Control Strategy", {
            0: "Conservative",
            1: "Radical"
        }, subtitle="Conservative = 50°C, Radical = 60°C")
