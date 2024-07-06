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
            "Button Brightness", 0, 10, 8,
            marks=[5]
        )

        self._add_color_picker_row("S1 Color", callback=lambda color: self._color_handler(1, color))
        self._add_color_picker_row("S2 Color", callback=lambda color: self._color_handler(2, color))


    def _color_handler(self, button: int, color: int) -> None:
        if color == None:
            return

        print(f"Button: {button}\nColor: {color}\n")


