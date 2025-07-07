# Copyright (c) 2025, Tomasz Pakuła Using Arch BTW

from gi.repository import Gtk, Adw, Gio, GObject
from .row import BoxflatRow


class ComboRow(GObject.Object):
    def __init__(self, text="", value=None):
        super().__init__()
        self.text = text
        self.value = value


class BoxflatComboRow(Adw.ComboRow, BoxflatRow):
    def __init__(self, title: str, subtitle=""):
        Adw.ComboRow.__init__(self)
        BoxflatRow.__init__(self, title, subtitle, init_adw=False)

        self.set_model(Gtk.StringList())
        self.connect("notify::selected", self._notify)


    def add_entry(self, text) -> None:
        if not text:
            return
        self.get_model().append(text)


    def get_value(self) -> int:
        return self.get_selected()


    def _set_value(self, value: int) -> None:
        if value < 0:
            return
        self.set_selected(value)
