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
            button.connect('toggled', self._notify)

            if self._group == None:
                self._group = button
                button.set_active(True)
            else:
                button.set_group(self._group)


    def get_value(self) -> int:
        val = 0
        for i in range(len(self._buttons)):
            if self._buttons[i].get_active():
                val = i

        return round(eval("val" + self._expression))


    def _set_value(self, value: int) -> None:
        if value == -1:
            for button in self._buttons:
                button.set_active(False)
            return

        value = round(eval("value"+self._reverse_expression))

        if value < 0:
            value = 0
        elif value >= len(self._buttons):
            value = len(self._buttons)-1

        self._buttons[value].set_active(True)


    def _notify(self, button: Gtk.ToggleButton) -> None:
        if button.get_active():
            super()._notify()



