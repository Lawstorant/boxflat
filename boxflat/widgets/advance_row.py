# Copyright (c) 2025, Tomasz Pakuła Using Arch BTW

from gi.repository import Gtk, GLib
from . import BoxflatRow

class BoxflatAdvanceRow(BoxflatRow):
    def __init__(self, title="", subtitle=""):
        super().__init__(title=title, subtitle=subtitle)

        self._icon = Gtk.Image()
        self._icon.set_from_icon_name("go-next-symbolic")
        self._icon.set_valign(Gtk.Align.CENTER)

        self._set_widget(self._icon)
        self.set_activatable(True)

        self.connect("activated", self._notify)


    def set_active(self, value=1, offset=0):
        super().set_active(value=value, offset=offset)
        GLib.idle_add(self._icon.set_opacity, 0.5 + int(self._active))
