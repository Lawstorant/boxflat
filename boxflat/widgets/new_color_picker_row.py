import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gdk
from .row import BoxflatRow

MOZA_RPM_LEDS=10

def extract_rgb(rgba: Gdk.RGBA) -> list:
        rgb = rgba.to_string()[4:-1]
        rgb = list(map(int, rgb.split(",")))
        return rgb


class BoxflatNewColorPickerRow(BoxflatRow):
    def __init__(self, title: str, subtitle=""):
        super().__init__(title, subtitle)

        child = self.get_child()
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_child(main_box)

        colors_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, hexpand=True, halign=Gtk.Align.CENTER)
        colors_box.set_size_request(0, 61)

        main_box.append(child)
        main_box.add_css_class("header")
        main_box.set_valign(Gtk.Align.CENTER)

        self._dialog = Gtk.ColorDialog(with_alpha=False)

        self._colors = []
        for i in range(MOZA_RPM_LEDS):
            color = Gtk.ColorDialogButton(dialog=self._dialog, hexpand=True, halign=Gtk.Align.CENTER)
            color.connect('notify::rgba', self._notify)

            self._colors.append(color)
            colors_box.append(color)

        main_box.append(colors_box)


    def get_value(self, index: int) -> list:
        if index in range(len(self._colors)):
            rgba = self._colors[index].get_rgba()
            return extract_rgb(rgba)
        return []


    def set_led_value(self, value: list, index: int) -> None:
        if index not in range(len(self._colors)):
            return

        if self.cooldown():
            print("Still cooling down")
            return

        self._mute = True
        rgba = Gdk.RGBA()
        rgba.parse(f"rgb({value[0]},{value[1]},{value[2]})")

        self._colors[index].set_rgba(rgba)
        self._mute = False


    def _notify(self, button: Gtk.ColorDialogButton, param) -> None:
        if self._mute:
            return

        self._cooldown = 1
        index = self._colors.index(button)
        for sub in self._subscribers:
            sub[0](self.get_value(index), sub[2][0] + str(index+1))




