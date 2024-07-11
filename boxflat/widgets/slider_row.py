import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw

from boxflat.widgets import BoxflatRow

class BoxflatSliderRow(BoxflatRow):
    def __init__(self, title: str=None, range_start=0,
                 range_end=100, value=0, increment=1,
                 suffix="", draw_value=True):
        super().__init__(title)

        slider = Gtk.Scale()
        self._set_widget(slider)
        self._slider = slider
        self._suffix = suffix
        self._increment = increment

        slider.set_range(range_start, range_end)
        slider.set_increments(increment, 0)
        slider.set_draw_value(draw_value)
        slider.set_round_digits(0)
        slider.set_digits(0)
        slider.set_value(value)
        slider.set_size_request(320, 0)
        self.add_marks(range_start, range_end)

        slider.connect('value-changed', lambda scale: self._slider_increment_handler(int(scale.get_value())))


    def _slider_increment_handler(self, value: int) -> None:
        modulo = value % self._increment

        if modulo != 0:
            self._slider.set_value(value + (self._increment - modulo))
        else:
            self._notify(value)


    def add_marks(self, *marks: int) -> None:
        for mark in marks:
            self._slider.add_mark(mark, Gtk.PositionType.BOTTOM, f"{mark}{self._suffix}")


    def set_width(self, width: int) -> None:
        self._slider.set_size_request(width, 0)


    def _value_handler(self, value=None) -> int:
        if value == None:
            return self._slider.get_value()
        else:
            self._slider.set_value(value)
            return 0
