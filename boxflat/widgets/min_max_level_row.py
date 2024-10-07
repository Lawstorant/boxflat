# Copyright (c) 2024, Tomasz Pakuła Using Arch BTW

from .button_level_row import *

class BoxflatMinMaxLevelRow(BoxflatButtonLevelRow):
    def __init__(self, title: str, callback: callable,
                 command_prefix: str, subtitle="", max_value=1000):
        super().__init__(title, subtitle, max_value)

        self.set_bar_width(230)
        self._min_button = self.add_button("Min", callback, self.get_fraction, command_prefix, "min")
        self.insert_bar_now()
        self._max_button = self.add_button("Max", callback, self.get_fraction, command_prefix, "max")

        self._bar.connect("notify::value", self._disable_buttons)
        self._min_button.set_sensitive(False)
        self._max_button.set_sensitive(False)


    def _disable_buttons(self, *rest):
        if self.get_percent_floor() == 0:
            GLib.idle_add(self._min_button.set_sensitive, False)
            GLib.idle_add(self._max_button.set_sensitive, False)

        elif self.get_percent_ceil() == 100:
            GLib.idle_add(self._min_button.set_sensitive, False)
            GLib.idle_add(self._max_button.set_sensitive, False)

        else:
            if not self._min_button.get_sensitive():
                GLib.idle_add(self._min_button.set_sensitive, True)

            if not self._max_button.get_sensitive():
                GLib.idle_add(self._max_button.set_sensitive, True)
