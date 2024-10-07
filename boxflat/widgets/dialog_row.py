# Copyright (c) 2024, Tomasz Pakuła Using Arch BTW

from gi.repository import Gtk, Adw
from .row import BoxflatRow
from .switch_row import BoxflatSwitchRow

class BoxflatDialogRow(BoxflatRow):
    def __init__(self, title: str, subtitle=""):
        super().__init__(title, subtitle)

        icon = Gtk.Image()
        icon.set_from_icon_name("go-next-symbolic")
        icon.set_valign(Gtk.Align.CENTER)
        # icon.set_pixel_size(32)

        self.set_activatable(True)
        self._title = title
        self._set_widget(icon)
        self._icon = icon
        self._switches = []

        self._group = Adw.PreferencesGroup()
        self._group.add_css_class("wheel-dialog-setting")
        self._page = Adw.PreferencesPage()
        self._page.add(self._group)

        self.connect("activated", self.show_dialog)


    def show_dialog(self, whatever):
        if self._page.get_parent():
            return

        dialog = Adw.Dialog(title=self._title)
        dialog.set_child(Adw.ToolbarView())
        dialog.get_child().add_top_bar(Adw.HeaderBar())
        dialog.get_child().set_content(self._page)
        dialog.present()


    def add_switches(self, *switches):
        for switch in switches:
            self.add_switch(switch)


    def add_switch(self, title: str, subtitle=""):
        row = BoxflatSwitchRow(title, subtitle=subtitle)
        row.set_width(400)
        self._group.add(row)
        self._switches.append(row)
        row.subscribe(self._notify)


    def get_value(self) -> list:
        values = []
        for switch in self._switches:
            values.append(switch.get_value())
        return values


    def get_count(self) -> int:
        return len(self._switches)


    def _set_value(self, values):
        for i in range(self.get_count()):
            self._switches[i].set_value(bool(values[i]))
