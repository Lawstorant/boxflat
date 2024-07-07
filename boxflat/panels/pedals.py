import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw
from boxflat.panels.settings_panel import SettingsPanel

class PedalsSettings(SettingsPanel):
    def __init__(self, button_callback) -> None:
        super(PedalsSettings, self).__init__("Pedals", button_callback)

    def _prepare_ui(self) -> None:
        self._add_preferences_page()

        # Throttle
        self._add_preferences_group("Throttle settings", level_bar=1)
        self._add_switch_row("Reverse Direction")
        self._add_button_row("Pedal Calibration", "Calibrate")

        # Brake
        self._add_preferences_group("Brake settings", level_bar=1)
        self._add_switch_row("Reverse Direction")
        self._add_slider_row(
            "Brake pedal max force",
            0,
            200,
            50,
            marks=[50, 100, 150],
            mark_suffix=" kg",
            subtitle="Not everyone is a Hulk"
        )
        self._add_button_row("Pedal Calibration", "Calibrate")

        # Clutch
        self._add_preferences_group("Clutch settings", level_bar=1)
        self._add_switch_row("Reverse Direction")
        self._add_button_row("Pedal Calibration", "Calibrate")
