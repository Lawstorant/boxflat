import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw
from panels.settings_panel import SettingsPanel

class WheelSettings(SettingsPanel):
    def __init__(self, button_callback) -> None:
        super(WheelSettings, self).__init__("Wheel", button_callback)

        label = Gtk.Label(label="Wheel screen")

        self._content.append(label)
