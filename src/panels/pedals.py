import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw
from panels.settings_panel import SettingsPanel

class PedalsSettings(SettingsPanel):
    def __init__(self, button_callback) -> None:
        super(PedalsSettings, self).__init__("Pedals", button_callback)

        label = Gtk.Label(label="Pedals screen")

        self._content.append(label)
