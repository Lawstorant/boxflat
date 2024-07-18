import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk
from .row import BoxflatRow
from .toggle_button_row import BoxflatToggleButtonRow

class BoxflatEqRow(BoxflatToggleButtonRow):
    def __init__(self, title: str, sliders_number: int,
                 subtitle="", draw_values=True, range_start=0,
                 range_end=100, value=0, increment=1, suffix=""):
        super().__init__(title, subtitle)

        self._suffix = suffix
        self._slider_subs = []

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
            self._sliders.append(slider)
            self._slider_subs.append([])
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

            slider.connect('value-changed', self._notify_slider)

            label = Gtk.Label()
            label.add_css_class("eq-label")

            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            box.set_hexpand(True)
            box.append(slider)
            box.append(label)

            sliders_box.append(box)
            self._slider_labels.append(label)

        self._box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self._box.add_css_class("eq-buttons")
        main_box.append(self._box)

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


    def add_buttons(self, *buttons) -> None:
        super().add_buttons(*buttons)
        for button in self._buttons:
            button.set_hexpand(True)


    def set_height(self, height: int) -> None:
        for slider in self._sliders:
            slider.set_size_request(0, height)


    def get_sliders_value(self) -> list:
        values = []
        for slider in self._sliders:
            values.append(round(slider.get_value()))

        return values


    def get_slider_value(self, index: int) -> int:
        return round(self._sliders[index].get_value())


    def set_sliders_value(self, values: list) -> None:
        self.mute(True)
        if len(self._sliders) != len(values):
            return

        for i in range(len(self._sliders)):
            self._sliders[i].set_value(values[i])
        self.unmute()


    def set_slider_value(self, index: int, value: int, mute=True) -> None:
        self.mute(mute)
        self._sliders[index].set_value(value)
        self.unmute()


    def get_button_value(self) -> int:
        return super().get_value()


    def set_button_value(self, value: int, mute: bool=True) -> None:
        super().set_value(value, mute)


    def subscribe_slider(self, index: int, callback: callable, *args) -> None:
        self._slider_subs[index].append((callback, args))


    def set_slider_active(self, index: int, active=True) -> None:
        self._sliders[index].set_sensitive(active)


    def _notify_slider(self, scale) -> None:
        if self._mute:
            return

        index = self._sliders.index(scale)

        self.set_button_value(-1)
        for sub in self._slider_subs[index]:
            sub[0](self.get_slider_value(index), *sub[1])
