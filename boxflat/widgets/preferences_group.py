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

        bar = Gtk.LevelBar()
        bar.set_mode(Gtk.LevelBarMode.CONTINUOUS)
        bar.set_valign(Gtk.Align.CENTER)
        bar.set_min_value(0)
        bar.set_max_value(66000)
        bar.set_value(0)
        self._bar = bar

        if level_bar:
            self.set_header_suffix(bar)


    def set_bar_level(self, level: int):
        print(level)
        if level > self._bar.get_max_value():
            self._bar.set_max_value(level)

        if level < self._bar.get_min_value():
            level = self._bar.get_min_value()

        self._bar.set_value(level)


    def get_bar_level(self) -> int:
        return int(self._bar.get_level())

    def set_bar_width(self, width: int) -> None:
        self._bar.set_size_request(width, 0)
