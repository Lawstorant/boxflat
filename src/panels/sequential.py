import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw
from panels.settings_panel import SettingsPanel

class SequentialSettings(SettingsPanel):
    def __init__(self, button_callback) -> None:
        super(SequentialSettings, self).__init__("Sequential Shifter", button_callback)

    def _prepare_ui(self) -> None:
        self._add_preferences_page()
        self._add_preferences_group("Shifter Settings")

        self._add_switch_row("Reverse Shift Direction", subtitle="Why would you do that?")
        self._add_switch_row("Paddle Shifter Synchronization")

        self._add_slider_row(
            "Auto Blip Duration", 0, 1000, 300,
            marks=[250, 500, 750],
            mark_suffix=" ms"
        )
