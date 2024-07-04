import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Gdk, Adw

class SettingsPanel(object):
    def __init__(self, title, button_callback) -> None:
        self._content = self._prepare_content()
        self._button = self._prepare_button(title, button_callback)
        
    def _prepare_button(self, title, button_callback) -> Gtk.ToggleButton:
        button = Gtk.ToggleButton()
        button.set_css_classes(['sidebar-button'])
        button.connect("clicked", button_callback)
        button.set_halign(Gtk.Align.FILL)
        
        label = Gtk.Label(label=f"{title}")
        label.set_justify(Gtk.Justification.LEFT)
        label.set_xalign(0)
        button.set_child(label)
        
        return button
    
    def _prepare_content(self) -> Gtk.Box:
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        content.set_css_classes(['settings-pane'])
        return content
        
    @property 
    def content(self) -> Gtk.Box:
        return self._content
    
    @property 
    def button(self) -> Gtk.ToggleButton:
        return self._button
    
    @property
    def title(self) -> str:
        return self._button.get_child().get_label()
    
    def deactivate_button(self) -> None:
        self._button.set_active(False)