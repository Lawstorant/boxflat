import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk
from .row import BoxflatRow

class BoxflatToggleButtonRow(BoxflatRow):
    def __init__(self, title: str, subtitle=""):
        super().__init__(title, subtitle)
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self._set_widget(box)
        self._box = box
        self._group = None
        self._buttons = []


    def add_buttons(self, *labels: str) -> None:
        for label in labels:
            button = Gtk.ToggleButton(label=label)
            button.add_css_class("toggle-button")
            button.set_valign(Gtk.Align.CENTER)
            self._box.append(button)
            self._buttons.append(button)
            button.connect('toggled', lambda button: self._notify(button.get_active()))

            if self._group == None:
                self._group = button
            else:
                button.set_group(self._group)


    def _value_handler(self, value) -> int:
        if value != None:
            if value < len(self._buttons):
                buttons[value].set_active()

        for i in range(len(self._buttons)):
            if self._buttons[i].get_active():
                return i
        return 0


    def _notify(self, active: bool) -> None:
        if active:
            super()._notify()



