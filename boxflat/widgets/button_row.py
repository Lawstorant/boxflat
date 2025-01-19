# Copyright (c) 2025, Tomasz Pakuła Using Arch BTW

from gi.repository import Gtk
from .row import BoxflatRow

class BoxflatButtonRow(BoxflatRow):
    def __init__(self, title: str, button_label: str=None, subtitle=""):
        super().__init__(title, subtitle)

        self._box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self._box.add_css_class("linked")
        self._set_widget(self._box)

        if button_label:
            self.add_button(button_label)


    def get_value(self) -> int:
        return round(eval("1" + self._expression))


    def add_button(self, button_label: str, callback=None, *args) -> Gtk.Button:
        button = Gtk.Button(label=button_label)
        button.set_valign(Gtk.Align.CENTER)
        self._box.append(button)

        if callback:
            button.connect('clicked', lambda button: callback(*args))
        else:
            button.connect('clicked', self._notify)

        return button
