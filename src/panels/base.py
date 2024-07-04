import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Gdk, Adw
from panels.settings_panel import SettingsPanel

class BaseSettings(SettingsPanel):
    def __init__(self, button_callback) -> None:
        super(BaseSettings, self).__init__("Base", button_callback)
        
        slider = Gtk.Scale()
        slider.set_digits(0)  # Number of decimal places to use
        slider.set_range(90, 2700)
        slider.set_increments(2, 180)
        slider.set_draw_value(True)
        slider.set_value(540)
        slider.set_size_request(460,0)
        
        slider.add_mark(90, Gtk.PositionType.BOTTOM, "90")
        slider.add_mark(360, Gtk.PositionType.BOTTOM, "360")
        slider.add_mark(540, Gtk.PositionType.BOTTOM, "540")
        slider.add_mark(900, Gtk.PositionType.BOTTOM, "900")
        slider.add_mark(1800, Gtk.PositionType.BOTTOM, "1800")
        slider.add_mark(2700, Gtk.PositionType.BOTTOM, "2700")

        slider.connect('value-changed', self.slider_changed)
        
        dialog = Adw.PreferencesPage()
        group = Adw.PreferencesGroup()
        group.set_title("Generic settings")
        row = Adw.ActionRow()
        row.add_suffix(slider)
        row.set_title("Rotation range")
        row.set_title_lines(0)
        row2 = Adw.ActionRow()
        row2.set_title("Rotation")
        
        
        group.add(row)
        group.add(row2)
        dialog.add(group)
        
        self._content.append(dialog)
    
    def slider_changed(self, slider):
        value = slider.get_value()
        if value % 2:
            slider.set_value(value + 1)