import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw

class BoxflatPreferencesGroup(Adw.PreferencesGroup):
    def __init__(self, title="", level_bar=False):
        super().__init__()
        self._subscribers = []
        self._bar = None
        self.set_title(title)

        self._max_value = 1000

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

        if level_bar:
            self.set_header_suffix(bar)


    def set_bar_level(self, level: int):
        if level > self._bar.get_max_value():
            level = self._bar.get_max_value()

        if level < self._bar.get_min_value():
            level = self._bar.get_min_value()

        self._bar.set_value(level)


    def get_bar_level(self) -> int:
        return int(self._bar.get_level())


    def set_bar_width(self, width: int) -> None:
        self._bar.set_size_request(width, 0)


    def set_bar_max(self, value: int) -> None:
        self._max_value = value
        self._bar.set_max_value(value)


    def set_range_start(self, value: int) -> None:
        self._bar.set_min_value(round(self._max_value * (value/100)))


    def set_range_end(self, value: int) -> None:
        self._bar.set_max_value(round(self._max_value * (value/100)))


