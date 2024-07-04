import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw
from panels.settings_panel import SettingsPanel

class HPatternSettings(SettingsPanel):
    def __init__(self, button_callback) -> None:
        super(HPatternSettings, self).__init__("H-Pattern Shifter", button_callback)
        
        label = Gtk.Label(label="H-pattern screen")
        
        self._content.append(label)