# Copyright (c) 2025, Tomasz Pakuła Using Arch BTW

from gi.repository import Gtk, Gdk, GLib
from .row import BoxflatRow
from threading import Thread, Event, Lock
from time import sleep
from boxflat.subscription import EventDispatcher

MOZA_RPM_LEDS    = 10
MOZA_RGB_BUTTONS = 10
MOZA_FLAG_LEDS   = 6

def extract_rgb(rgba: Gdk.RGBA) -> list[int]:
        rgb = rgba.to_string()[4:-1]
        rgb = list(map(int, rgb.split(",")))
        return rgb


class BoxflatNewColorPickerRow(EventDispatcher, BoxflatRow):
    def __init__(self, title="", subtitle="", blinking=False, pickers=10):
        BoxflatRow.__init__(self, title, subtitle)
        EventDispatcher.__init__(self)

        for i in range(pickers):
            self._register_event(f"color{i}")

        child = self.get_child()
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_child(main_box)

        colors_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, hexpand=True, halign=Gtk.Align.FILL)
        colors_box.set_margin_top(6)
        colors_box.set_margin_bottom(12)

        main_box.append(child)
        main_box.add_css_class("header")
        main_box.set_valign(Gtk.Align.CENTER)
        main_box.set_halign(Gtk.Align.FILL)
        main_box.append(colors_box)

        self._dialog = Gtk.ColorDialog(with_alpha=False)
        self._blinking_event: list[Event] = []
        self._value_lock = Lock()

        self._colors: list[Gtk.ColorDialogButton] = []
        red = Gdk.RGBA()
        red.parse("rgb(255,0,0)")
        for i in range(pickers):
            color = Gtk.ColorDialogButton(dialog=self._dialog, hexpand=True)
            color.set_rgba(red)
            color.set_valign(Gtk.Align.CENTER)
            color.set_halign(Gtk.Align.CENTER)
            color.connect('notify::rgba', self._notify)

            self._colors.append(color)
            colors_box.append(color)
            size = color.get_preferred_size()[1]
            color.set_size_request(0, size.width - 1)

            if not blinking:
                continue

            motion_controller = Gtk.EventControllerMotion()
            motion_controller.connect("enter", self._enter_button, i)
            motion_controller.connect("leave", self._leave_button, i)
            color.add_controller(motion_controller)
            self._blinking_event.append(Event())


    def get_value(self, index: int) -> list[int]:
        if not 0 <= index < len(self._colors):
            return
        rgba = self._colors[index].get_rgba()
        return extract_rgb(rgba)


    def get_index(self, button: Gtk.ColorDialogButton) -> int:
        return self._colors.index(button)


    def set_led_value(self, value: list, index: int, mute=True):
        if not isinstance(value, list):
            return

        if self._value_lock.locked():
            return

        if not 0 <= index < len(self._colors):
            return

        if self.cooldown():
            # print("Still cooling down")
            return

        rgba = Gdk.RGBA()
        rgba.parse(f"rgb({value[0]},{value[1]},{value[2]})")
        GLib.idle_add(self._set_led_value, rgba, index, mute)


    def _set_led_value(self, rgba, index, mute):
        if mute:
            self._mute.set()
        self._colors[index].set_rgba(rgba)
        if mute:
            self._mute.clear()


    def _notify(self, button: Gtk.ColorDialogButton, *param, alt_value=None):
        if self._mute.is_set():
            return

        if self._cooldown == 0:
            self._cooldown = 1

        index = self.get_index(button)
        value = alt_value if alt_value else self.get_value(index)

        self._dispatch(f"color{index}", value)


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
                sleep(0.4)

            self._blinking_event[index].clear()
            self._cooldown = 8
