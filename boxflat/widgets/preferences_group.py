# Copyright (c) 2025, Tomasz Pakuła Using Arch BTW

from gi.repository import Gtk, Adw, GLib
from threading import Lock

class BoxflatPreferencesGroup(Adw.PreferencesGroup):
    def __init__(self, title="", level_bar=False, alt_level_bar=False):
        super().__init__()
        self._bar = None
        self._bar1 = None
        self._bar2 = None
        self._box  = None
        self.set_title(title)

        self._max_value = 1000
        self._offset = 0

        if level_bar:
            bar = Gtk.LevelBar()
            bar.set_mode(Gtk.LevelBarMode.CONTINUOUS)
            bar.set_valign(Gtk.Align.CENTER)
            bar.set_min_value(0)
            bar.set_max_value(1000)
            bar.set_value(0)

            bar.remove_offset_value(Gtk.LEVEL_BAR_OFFSET_LOW)
            bar.remove_offset_value(Gtk.LEVEL_BAR_OFFSET_HIGH)
            bar.remove_offset_value(Gtk.LEVEL_BAR_OFFSET_FULL)
            self._bar = bar
            self.set_header_suffix(bar)

        if alt_level_bar:
            bar1 = Gtk.LevelBar()
            bar1.set_mode(Gtk.LevelBarMode.CONTINUOUS)
            bar1.set_hexpand(True)
            bar1.set_valign(Gtk.Align.CENTER)
            bar1.set_min_value(0)
            bar1.set_max_value(1000)
            bar1.set_value(0)
            bar1.set_inverted(True)
            bar1.add_css_class("altbar1")
            self._bar1 = bar1

            bar2 = Gtk.LevelBar()
            bar2.set_mode(Gtk.LevelBarMode.CONTINUOUS)
            bar2.set_hexpand(True)
            bar2.set_valign(Gtk.Align.CENTER)
            bar2.set_min_value(0)
            bar2.set_max_value(1000)
            bar2.set_value(0)
            bar2.add_css_class("altbar2")
            self._bar2 = bar2

            box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, hexpand=True)
            box.append(bar1)
            box.append(bar2)

            self._box = box
            self.set_header_suffix(box)


    def set_bar_level(self, level: int):
        level += self._offset

        if level > self._bar.get_max_value():
            level = self._bar.get_max_value()

        if level < self._bar.get_min_value():
            level = self._bar.get_min_value()

        GLib.idle_add(self._bar.set_value, level)


    def set_alt_bar_level(self, level: int):
        level += self._offset
        if abs(level) > self._max_value:
            return

        GLib.idle_add(self._bar1.set_value, 0 if level > 0 else abs(level))
        GLib.idle_add(self._bar2.set_value, 0 if level < 0 else level)


    def get_bar_level(self) -> int:
        return int(self._bar.get_level())


    def set_bar_width(self, width: int):
        if self._box:
            self._box.set_size_request(width/2, 0)
        elif self._bar:
            self._bar.set_size_request(width, 0)


    def set_bar_max(self, value: int):
        self._max_value = value

        if self._box:
            self._bar1.set_max_value(value)
            self._bar2.set_max_value(value)
        else:
            self._bar.set_max_value(value)


    def set_offset(self, value: int):
        self._offset = value


    def set_active(self, value, offset=0):
        test = int(value + offset) > 0
        GLib.idle_add(self.set_sensitive, test)


    def set_present(self, value, offset=0):
        test = int(value) + offset > 0
        GLib.idle_add(self.set_visible, test)
