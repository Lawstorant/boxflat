import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw
from panels.settings_panel import SettingsPanel

class WheelSettings(SettingsPanel):
    def __init__(self, button_callback) -> None:
        super(WheelSettings, self).__init__("Wheel", button_callback)

    def _prepare_ui(self) -> None:
        self._add_preferences_page()
        self._add_preferences_group("Input settings")
        self._add_toggle_button_row("Dual Clutch Paddles Mode", ["Combined", "Split", "Buttons"])
        self._add_slider_row("Clutch Split Point", 0 , 100, 50, marks=[25, 50, 75], mark_suffix=" %")
        self._add_toggle_button_row("Left Stick Mode", ["Buttons", "D-Pad"])


        self._add_preferences_group("Indicator settings")
        self._add_toggle_button_row("RPM Indicator Mode", ["RPM", "On", "Off"])
        self._add_toggle_button_row("RPM Indicator Display Mode", ["Mode 1", "Mode 2"])
        # TODO: Add custom timing with a vertical sliders widget
        self._add_toggle_button_row("RPM Indicator Timing", ["Early", "Normal", "Late"])
        # TODO: Add color picker for every light
        self._add_slider_row("Brightness", 0 , 100, 50, marks=[25, 50, 75], mark_suffix=" %", subtitle="RPM and buttons")

        self._add_preferences_group("Indicator colors")
        for i in range(0, 10):
            self._add_color_picker_row(f"Light {i+1}")
