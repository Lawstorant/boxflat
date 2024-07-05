import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw
from panels.settings_panel import SettingsPanel

class HomeSettings(SettingsPanel):
    def __init__(self, button_callback) -> None:
        super(HomeSettings, self).__init__("Home", button_callback)

        label = Gtk.Label(label="Welcome to Box Flat!")

        self._content.append(label)
        self.hide_banner()
