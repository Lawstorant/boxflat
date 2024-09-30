import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GLib
import time
from boxflat.subscription import SimpleEventDispatcher

class BoxflatRow(Adw.ActionRow, SimpleEventDispatcher):
    def __init__(self, title="", subtitle=""):
        Adw.ActionRow.__init__(self)
        SimpleEventDispatcher.__init__(self)

        self._cooldown = 0
        self._mute = False
        self._shutdown = False
        self.set_sensitive(True)
        self.set_title(title)
        self.set_subtitle(subtitle)
        self._expression = "*1"
        self._reverse_expression = "*1"
        self._active = True


    def get_active(self) -> bool:
        return self._active


    def set_active(self, value=1, offset=0) -> bool:
        value = bool(int(value) + offset > 0)
        if value != self.get_active():
            self._active = value
            GLib.idle_add(self.set_sensitive, value)
            return True

        return False


    def set_present(self, value, additional=0):
        GLib.idle_add(self.set_visible, int(value) + additional > 0)


    def mute(self, value: bool=True):
        self._mute = value


    def unmute(self):
        self._mute = False


    def get_value(self) -> int:
        return 0


    def get_raw_value(self) -> int:
        return self.get_value()


    def set_value(self, value, mute: bool=True):
        if self.cooldown():
            # print("Still cooling down")
            # print(self.get_title())
            return

        self.mute(mute)
        self._set_value(value)
        self.unmute()


    def _set_value(self, value):
        pass


    def _set_widget(self, widget: Gtk.Widget):
        GLib.idle_add(self.add_suffix, widget)


    def _notify(self, *rest):
        if self._mute:
            return

        self._cooldown = 1
        self._dispatch(self.get_value())


    def set_expression(self, expr: str):
        """
        Modify the value when invoking get_value()
        """
        self._expression = expr


    def set_reverse_expression(self, expr: str):
        """
        Modify the value when invoking set_value()
        """
        self._reverse_expression = expr


    def shutdown(self):
        self._shutdown = True


    def set_width(self, width: int):
        self.set_size_request(width, 0)


    def cooldown(self) -> bool:
        ret = (self._cooldown != 0)

        if self._cooldown > 0:
            self._cooldown -= 1

        return ret
