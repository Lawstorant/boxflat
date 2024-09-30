import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gdk
from .row import BoxflatRow
from threading import Thread, Event, Lock
from time import sleep

MOZA_RPM_LEDS=10

def extract_rgb(rgba: Gdk.RGBA) -> list:
        rgb = rgba.to_string()[4:-1]
        rgb = list(map(int, rgb.split(",")))
        return rgb


class BoxflatNewColorPickerRow(BoxflatRow):
    def __init__(self, title: str, subtitle="", blinking=False):
        super().__init__(title, subtitle)

        child = self.get_child()
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_child(main_box)

        colors_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, hexpand=True, halign=Gtk.Align.CENTER)
        colors_box.set_margin_top(6)
        colors_box.set_margin_bottom(12)

        main_box.append(child)
        main_box.add_css_class("header")
        main_box.set_valign(Gtk.Align.CENTER)
        main_box.append(colors_box)

        self._dialog = Gtk.ColorDialog(with_alpha=False)
        self._blinking_event = []
        self._value_lock = Lock()

        self._colors = []
        red = Gdk.RGBA()
        red.parse("rgb(230,60,60)")
        for i in range(MOZA_RPM_LEDS):
            color = Gtk.ColorDialogButton(dialog=self._dialog, hexpand=True, halign=Gtk.Align.CENTER)
            color.set_rgba(red)
            color.set_size_request(0,48)
            color.connect('notify::rgba', self._notify)

            self._colors.append(color)
            colors_box.append(color)

            if not blinking:
                continue

            motion_controller = Gtk.EventControllerMotion()
            motion_controller.connect("enter", self._enter_button, i)
            motion_controller.connect("leave", self._leave_button, i)
            color.add_controller(motion_controller)
            self._blinking_event.append(Event())


    def get_value(self, index: int) -> list:
        if index >= 0 and index < len(self._colors):
            rgba = self._colors[index].get_rgba()
            return extract_rgb(rgba)
        return []


    def get_index(self, button: Gtk.ColorDialogButton) -> int:
        return self._colors.index(button)


    def set_led_value(self, value: list, index: int):
        if self._value_lock.locked():
            return

        if index < 0 or index >= len(self._colors):
            return

        if self.cooldown():
            # print("Still cooling down")
            return

        # TODO: use Lock instead of boolean value
        self._mute = True
        rgba = Gdk.RGBA()
        rgba.parse(f"rgb({value[0]},{value[1]},{value[2]})")

        self._colors[index].set_rgba(rgba)
        self._mute = False


    def _notify(self, button: Gtk.ColorDialogButton, *param, alt_value=None):
        if self._mute:
            return

        if self._cooldown == 0:
            self._cooldown = 1
        index = self.get_index(button)
        value = alt_value if alt_value else self.get_value(index)

        for sub in self._subscribers:
            sub[0](value, sub[2][0] + str(index+1))


    def _enter_button(self, controller: Gtk.EventControllerMotion, a, b, index: int):
        if not self._blinking_event[index].is_set():
            self._blinking_event[index].set()
            Thread(target=self._button_blinking, args=[index]).start()


    def _leave_button(self, controller: Gtk.EventControllerMotion, index: int):
        self._blinking_event[index].clear()


    def _button_blinking(self, index: int):
        with self._value_lock:
            self._cooldown = -1

            button = self._colors[index]
            value = self.get_value(index)

            iterations = 0
            while self._blinking_event[index].is_set() and iterations < 50:
                iterations += 1
                self._notify(button, alt_value=[0, 0, 0])
                sleep(0.4)
                self._notify(button, alt_value=value)
                sleep(0.8)

            self._blinking_event[index].clear()
            self._cooldown = 10
