# Copyright (c) 2024, Tomasz Pakuła Using Arch BTW

from .level_row import *
from .button_row import *

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk

class BoxflatButtonLevelRow(BoxflatLevelRow):
    def __init__(self, title: str, subtitle="", max_value=1000):
        super().__init__(title, subtitle, max_value, append_widget=False)

        self._box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        # self._box.set_hexpand(True)
        self._set_widget(self._box)
        self._bar.set_margin_start(10)
        self._bar.set_margin_end(0)


    def add_button(self, button_label: str, callback: callable, *args) -> Gtk.Button:
        button = Gtk.Button(label=button_label)
        button.set_valign(Gtk.Align.CENTER)
        button.set_margin_start(10)
        button.add_css_class("level-button")
        button.connect('clicked', lambda button: callback(*args))

        self._box.append(button)
        return button


    def insert_bar_now(self):
        if not self._bar.get_parent():
            self._box.append(self._bar)
