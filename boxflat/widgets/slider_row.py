import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk
from .row import BoxflatRow

class BoxflatSliderRow(BoxflatRow):
    def __init__(self, title="", range_start=0,
                 range_end=100, value=0, increment=1,
                 subtitle="", suffix="", draw_value=True, big=False):
        super().__init__(title, subtitle)

        slider = Gtk.Scale()
        self._slider = slider
        self._suffix = suffix
        self._increment = increment
        self._range_start = range_start
        self._range_end = range_end

        slider.set_range(range_start, range_end)
        slider.set_increments(increment, 0)
        slider.set_draw_value(draw_value)
        slider.set_round_digits(0)
        slider.set_digits(0)
        slider.set_value(value)
        slider.set_size_request(320, 0)
        slider.set_valign(Gtk.Align.CENTER)
        self.add_marks(range_start, range_end)

        slider.connect('value-changed', self._notify)

        if big:
            label = Gtk.Label()
            label.set_text(str(range_start))
            label.add_css_class("big-slider-label")
            slider.connect('value-changed', lambda b: label.set_text(str(int(b.get_value()))))
            self.add_suffix(label)
            child = self.get_child()
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            box.set_margin_top(13)
            self.set_child(box)
            box.append(child)
            box.append(slider)
            box.add_css_class("header")
            slider.add_css_class("big-slider")
            box.set_valign(Gtk.Align.CENTER)
        else:
            self.add_suffix(slider)
            slider.add_css_class("slider")


    # def _slider_increment_handler(self, scale) -> None:
    #     modulo = self.get_value() % self._increment

    #     if modulo != 0:
    #         self.set_value(self.get_value() + (self._increment - modulo))
    #     else:
    #         self._notify()


    def _notify(self, *args) -> None:
        super()._notify()


    def add_marks(self, *marks: int) -> None:
        for mark in marks:
            self._slider.add_mark(
                mark, Gtk.PositionType.BOTTOM,f"{mark}{self._suffix}")


    def set_slider_width(self, width: int) -> None:
        self._slider.set_size_request(width, 0)


    def get_value(self) -> int:
        return round(eval("self._slider.get_value()" + self._expression))


    def get_raw_value(self) -> int:
        return int(self._slider.get_value())


    def _set_value(self, value: int) -> None:
        value = round(eval("value"+self._reverse_expression))
        if value < self._range_start:
            value = self._range_start

        self._slider.set_value(value)
