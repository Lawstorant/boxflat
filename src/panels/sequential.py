import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw
from panels.settings_panel import SettingsPanel

class SequentialSettings(SettingsPanel):
    def __init__(self, button_callback) -> None:
        super(SequentialSettings, self).__init__("Sequential Shifter", button_callback)
        
        label = Gtk.Label(label="Sequential screen")
        
        self._content.append(label)