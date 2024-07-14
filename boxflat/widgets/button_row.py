import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk
from .row import BoxflatRow

class BoxflatButtonRow(BoxflatRow):
    def __init__(self, title: str, button_label: str, subtitle=""):
        super().__init__(title, subtitle)

        button = Gtk.Button(label=button_label)
        button.connect('clicked', lambda button: self._notify())
        button.set_valign(Gtk.Align.CENTER)
        self._set_widget(button)
        self._button = button

    def get_value(self) -> int:
        return round(eval("1" + self._expression))
