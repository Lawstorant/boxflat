import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw

from boxflat.widgets import BoxflatRow

class BoxflatButtonRow(BoxflatRow):
    def __init__(self, title: str, button_label: str, subtitle=""):
        super().__init__(title, subtitle)

        button = Gtk.Button(label=button_label)
        self._set_widget(button)
        self._button = button

        button.add_css_class("row-button")
        button.connect('clicked', lambda button: self._notify())

    @property
    def button_label(self) -> str:
        return self._button.get_label()

    @button_label.setter
    def button_label(self, label: str) -> str:
        return self._button.set_label(label)
