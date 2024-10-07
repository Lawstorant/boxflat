from gi.repository import Gtk, GLib
from .row import BoxflatRow
from .toggle_button_row import BoxflatToggleButtonRow
from boxflat.subscription import SubscriptionList

class BoxflatEqRow(BoxflatToggleButtonRow):
    def __init__(self, title: str, sliders_number: int,
                 subtitle="", draw_values=True, range_start=0,
                 range_end=100, value=0, increment=1, suffix="",
                 button_row=True, draw_marks=True, ignore_index=-1):
        super().__init__(title, subtitle)

        self._suffix = suffix
        self._slider_subs_list = []
        self._sliders_subs = SubscriptionList()
        self._button_row = button_row
        self._draw_marks = draw_marks

        child = self.get_child()
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        main_box.set_margin_top(13)
        self.set_child(main_box)

        sliders_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        sliders_box.set_hexpand(True)
        sliders_box.set_halign(Gtk.Align.FILL)
        # something_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        main_box.append(child)
        main_box.add_css_class("header")
        main_box.set_valign(Gtk.Align.CENTER)

        self._sliders = []
        self._slider_labels = []
        for i in range(sliders_number):
            slider = Gtk.Scale(orientation=Gtk.Orientation.VERTICAL)
            self._sliders.append(slider)
            self._slider_subs_list.append(SubscriptionList())
            slider.set_range(range_start, range_end)
            slider.set_inverted(True)
            slider.set_halign(Gtk.Align.FILL)

            slider.set_increments(increment, 0)
            slider.set_draw_value(draw_values)
            slider.set_value_pos(Gtk.PositionType.TOP)
            slider.set_round_digits(0)
            slider.set_digits(0)
            slider.set_value(value)
            slider.set_size_request(0, 300)
            slider.add_css_class("eq-slider")

            slider.connect('value-changed', self._notify_slider)

            if i != ignore_index:
                slider.connect('value-changed', self._notify_sliders)

            label = Gtk.Label()
            label.add_css_class("eq-label")

            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            box.set_hexpand(True)
            box.append(slider)
            box.append(label)

            sliders_box.append(box)
            self._slider_labels.append(label)

        if button_row:
            self._box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
            self._box.add_css_class("eq-buttons")
            self._box.add_css_class("linked")
            main_box.append(self._box)

        main_box.append(sliders_box)
        self.add_marks(range_start, range_end)


    def add_marks(self, *marks: int):
        if not self._draw_marks:
            return

        for mark in marks:
            for slider in self._sliders:
                slider.add_mark(mark, Gtk.PositionType.RIGHT,f"{mark}{self._suffix}")


    def add_labels(self, *labels: str, index=None):
        if index is not None:
            self._slider_labels[index].set_text(labels[0])
            return

        if len(labels) != len(self._slider_labels):
            return

        for slider, label in zip(self._slider_labels, labels):
            slider.set_text(label)


    def add_buttons(self, *buttons):
        super().add_buttons(*buttons)
        for button in self._buttons:
            button.set_hexpand(self._button_row)


    def set_height(self, height: int):
        for slider in self._sliders:
            slider.set_size_request(0, height)


    def get_sliders_value(self) -> list:
        values = []
        for slider in self._sliders:
            values.append(round(slider.get_value()))

        return values


    def get_slider_value(self, index: int) -> int:
        return round(self._sliders[index].get_value())


    def set_sliders_value(self, values: list, mute=True):
        if len(values) > len(self._sliders):
            return

        for i, value in enumerate(values):
            self.set_slider_value(value, i, mute)


    def set_slider_value(self, value: int, index: int, mute=True):
        GLib.idle_add(self._set_slider_value, value, index, mute)


    def _set_slider_value(self, value: int, index: int, mute=True):
        self.mute(mute)
        self._sliders[index].set_value(value)
        self.unmute()


    def get_button_value(self) -> int:
        return super().get_value()


    def set_button_value(self, value: int, mute: bool=True):
        super().set_value(value, mute)


    def subscribe_slider(self, index: int, callback: callable, *args):
        self._slider_subs_list[index].append(callback, *args)


    def subscribe_sliders(self, callback: callable, *args):
        self._sliders_subs.append(callback, *args)


    def set_slider_active(self, active: bool, index: int):
        self._sliders[index].set_sensitive(active)


    def _notify_slider(self, scale: Gtk.Scale):
        if self._mute.is_set():
            return

        self._cooldown = 2
        index = self._sliders.index(scale)

        self.set_button_value(-1)
        self._slider_subs_list[index].call_with_value(self.get_slider_value(index))


    def _notify_sliders(self, scale):
        if self._mute.is_set():
            return

        self._cooldown = 2
        self.set_button_value(-1)
        self._sliders_subs.call_with_value(self.get_sliders_value())


    def reconfigure(self, range_start=0, range_end=100, clear_marks=True):
        for slider in self._sliders:
            slider.set_range(range_start, range_end)
            if clear_marks:
                slider.clear_marks()
