# Copyright (c) 2024, Tomasz Pakuła Using Arch BTW

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib
from .row import BoxflatRow

class BoxflatLabelRow(BoxflatRow):
    def __init__(self, title: str, subtitle="", value=""):
        super().__init__(title, subtitle)

        label = Gtk.Label()
        label.set_valign(Gtk.Align.CENTER)
        label.set_label(value)
        self._set_widget(label)
        self._label = label
        self._suffix = ""


    def _set_value(self, value: str):
        value = round(eval("value"+self._reverse_expression), 1)
        self._label.set_label(str(value) + self._suffix)


    def set_suffix(self, suffix: str):
        self._suffix = str(suffix)
