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
        
        slider_ffb = Gtk.Scale()
        slider_ffb.set_digits(0)  # Number of decimal places to use
        slider_ffb.set_range(0, 100)
        slider_ffb.set_increments(1, 10)
        slider_ffb.set_draw_value(True)
        slider_ffb.set_value(50)
        slider_ffb.set_size_request(350,0)
        
        slider_ffb.add_mark(0, Gtk.PositionType.BOTTOM, "0%")
        slider_ffb.add_mark(50, Gtk.PositionType.BOTTOM, "50%")
        slider_ffb.add_mark(100, Gtk.PositionType.BOTTOM, "100%")     
        
        
        dialog = Adw.PreferencesPage()
        group = Adw.PreferencesGroup()
        group.set_title("Generic settings")
        row = Adw.ActionRow()
        row.add_suffix(slider)
        row.set_title("Rotation range")
        row2 = Adw.ActionRow()
        row2.set_title("FFB Strength")
        row2.add_suffix(slider_ffb)
        
        
        group.add(row)
        group.add(row2)
        dialog.add(group)
        
        self._content.append(dialog)
    
    def slider_changed(self, slider):
        value = slider.get_value()
        if value % 2:
            slider.set_value(value + 1)