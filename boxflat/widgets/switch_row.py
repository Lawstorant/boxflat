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


    def get_value(self) -> int:
        return int(self._switch.get_active())


    def set_value(self, value: int) -> None:
        self._switch.set_active(bool(value))
