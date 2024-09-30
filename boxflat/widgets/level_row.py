import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib
from .row import BoxflatRow
from math import ceil, floor

class BoxflatLevelRow(BoxflatRow):
    def __init__(self, title: str, subtitle="", max_value=1000, append_widget=True):
        super().__init__(title, subtitle)

        self._max_value = max_value

        bar = Gtk.LevelBar()
        bar.set_mode(Gtk.LevelBarMode.CONTINUOUS)
        bar.set_valign(Gtk.Align.CENTER)
        bar.set_min_value(0)
        bar.set_max_value(max_value)
        bar.set_value(0)
        bar.set_margin_end(2)

        bar.remove_offset_value(Gtk.LEVEL_BAR_OFFSET_LOW)
        bar.remove_offset_value(Gtk.LEVEL_BAR_OFFSET_HIGH)
        bar.remove_offset_value(Gtk.LEVEL_BAR_OFFSET_FULL)

        self._bar = bar
        if append_widget:
            self._set_widget(bar)

        self.set_bar_width(310)
        self._present_cooldown = True


    def _set_value(self, value: int):
        if not self.get_active():
            return

        if value > self._max_value:
            value = self._max_value

        if value < 0:
            value = 0

        GLib.idle_add(self._bar.set_value, value)


    def set_bar_max(self, value: int):
        self._max_value = value
        self._bar.set_max_value(value)


    def set_bar_width(self, width: int):
        self._bar.set_size_request(width, 0)


    def set_offset(self, value: int):
        value = ceil((value / 100) * self._max_value)
        self._bar.add_offset_value("level-offset", value)


    def set_present(self, value, additional=0,
                    skip_cooldown=False, trigger_cooldown=True):
        if self._present_cooldown and not skip_cooldown:
            self._present_cooldown = False

        else:
            self._present_cooldown = trigger_cooldown
            super().set_present(value, additional)


    def set_active(self, value, offset=0):
        if super().set_active(value, offset):
            self.set_value(0)


    def get_value(self) -> int:
        return int(self._bar.get_value())


    def get_fraction(self) -> float:
        return self._bar.get_value()  / self._bar.get_max_value()


    def get_percent(self) -> int:
        return round(self.get_fraction() * 100)


    def get_percent_floor(self) -> int:
        return floor(self.get_fraction() * 100)

    def get_percent_ceil(self) -> int:
        return ceil(self.get_fraction() * 100)
