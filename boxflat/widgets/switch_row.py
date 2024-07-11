import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk
from .row import BoxflatRow

class BoxflatSwitchRow(BoxflatRow):
    def __init__(self, title: str, subtitle=""):
        super().__init__(title, subtitle)

        switch = Gtk.Switch()
        switch.add_css_class("switch")
        switch.connect('notify::active', lambda switch, whatever: self._notify())
        switch.set_valign(Gtk.Align.CENTER)
        self._switch = switch
        self._set_widget(switch)
        self.set_activatable_widget(switch)


    def _value_handler(self, value: bool) -> int:
        if value != None:
            self._switch.set_active(value)
        return int(self._switch.get_active())

