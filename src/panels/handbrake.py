import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw
from panels.settings_panel import SettingsPanel

class HandbrakeSettings(SettingsPanel):
    def __init__(self, button_callback) -> None:
        super(HandbrakeSettings, self).__init__("Handbrake", button_callback)

    def _prepare_ui(self) -> None:
        self._add_preferences_page()
        self._add_preferences_group("Handbrake settings")
        self._add_switch_row("Reverse Directiion")
        self._add_toggle_button_row("Handbrake Mode", ["Axis", "Button"])
        self._add_slider_row(
            "Button Treshold",
            0,
            100,
            50,
            marks=[50],
            mark_suffix=" %"
        )

        self._add_preferences_group("Calibration")
        self._add_button_row("Device Calibration", "Calibrate")
