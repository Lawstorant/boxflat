import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk
from .row import BoxflatRow

class BoxflatEqRow(BoxflatRow):
    def __init__(self, title: str, sliders_number: int,
                 subtitle="", draw_values=True, range_start=0,
                 range_end=100, value=0, increment=1, suffix=""):
        super().__init__(title, subtitle)

        self._suffix = suffix

        child = self.get_child()
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_child(main_box)

        sliders_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        # something_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        main_box.append(child)
        main_box.add_css_class("header")
        main_box.set_valign(Gtk.Align.CENTER)

        self._sliders = []
        self._slider_labels = []
        for i in range(sliders_number):
            slider = Gtk.Scale(orientation=Gtk.Orientation.VERTICAL)
            slider.set_range(range_start, range_end)
            slider.set_inverted(True)

            slider.set_increments(increment, 0)
            slider.set_draw_value(draw_values)
            slider.set_value_pos(Gtk.PositionType.BOTTOM)
            slider.set_round_digits(0)
            slider.set_digits(0)
            slider.set_value(value)
            slider.set_size_request(0, 300)
            slider.set_hexpand(True)
            slider.add_css_class("eq-slider")

            label = Gtk.Label()
            label.add_css_class("eq-label")

            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            box.set_hexpand(True)
            box.append(slider)
            box.append(label)

            sliders_box.append(box)
            self._slider_labels.append(label)
            self._sliders.append(slider)

        main_box.append(sliders_box)
        self.add_marks(range_start, range_end)


    def add_marks(self, *marks: int) -> None:
        for mark in marks:
            for slider in self._sliders:
                slider.add_mark(mark,
                    Gtk.PositionType.RIGHT,f"{mark}{self._suffix}")


    def add_labels(self, *labels: str) -> None:
        for i in range(len(labels)):
            self._slider_labels[i].set_text(labels[i])


    def set_height(self, height: int) -> None:
        for slider in self._sliders:
            slider.set_size_request(0, height)
