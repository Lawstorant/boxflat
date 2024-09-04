import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib
from .row import BoxflatRow

class BoxflatLevelRow(BoxflatRow):
    def __init__(self, title: str, subtitle="", max_value=1000):
        super().__init__(title, subtitle)

        self._max_value = max_value

        bar = Gtk.LevelBar()
        bar.set_mode(Gtk.LevelBarMode.CONTINUOUS)
        bar.set_valign(Gtk.Align.CENTER)
        bar.set_min_value(0)
        bar.set_max_value(max_value)
        bar.set_value(0)
        bar.add_css_class("level-dark")

        self._set_widget(bar)
        self._bar = bar

        self.set_bar_width(270)


    def _set_value(self, value: int) -> None:
        value = round(eval("value"+self._reverse_expression))

        if value > self._max_value:
            value = self._max_value

        if value < 0:
            value = 0

        GLib.idle_add(self._bar.set_value, value)


    def set_bar_max(self, value: int) -> None:
        self._max_value = value
        self._bar.set_max_value(value)


    def set_bar_width(self, width: int) -> None:
        self._bar.set_size_request(width, 0)
