import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GLib
import time
from boxflat.subscription import SubscribtionList

class BoxflatRow(Adw.ActionRow):
    def __init__(self, title="", subtitle=""):
        super().__init__()
        self._cooldown = 0
        self._subscribers = SubscribtionList()
        self._raw_subscribers = SubscribtionList()
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


    def set_present(self, value, additional=0) -> None:
        GLib.idle_add(self.set_visible, int(value) + additional > 0)


    def mute(self, value: bool=True) -> None:
        self._mute = value


    def unmute(self) -> None:
        self._mute = False


    def get_value(self) -> int:
        return 0


    def get_raw_value(self) -> int:
        return self.get_value()


    def set_value(self, value, mute: bool=True) -> None:
        if self.cooldown():
            # print("Still cooling down")
            # print(self.get_title())
            return

        self.mute(mute)
        self._set_value(value)
        self.unmute()


    def _set_value(self, value) -> None:
        pass


    def _set_widget(self, widget: Gtk.Widget) -> None:
        GLib.idle_add(self.add_suffix, widget)


    def subscribe(self, callback: callable, *args, raw=False) -> None:
        if raw:
            self._raw_subscribers.append(callback, *args)
        else:
            self._subscribers.append(callback, *args)


    def clear_subscribtions(self) -> None:
        self._subscribers.clear()
        self._raw_subscribers.clear()


    def _notify(self, *rest) -> None:
        if self._mute:
            return

        self._cooldown = 1
        self._subscribers.call_with_value(self.get_value())
        self._raw_subscribers.call_with_value(self.get_raw_value())


    def set_expression(self, expr: str) -> None:
        """
        Modify the value when invoking get_value()
        """
        self._expression = expr


    def set_reverse_expression(self, expr: str) -> None:
        """
        Modify the value when invoking set_value()
        """
        self._reverse_expression = expr


    def shutdown(self) -> None:
        self._shutdown = True


    def set_width(self, width: int) -> None:
        self.set_size_request(width, 0)


    def cooldown(self) -> bool:
        ret = (self._cooldown != 0)

        if self._cooldown > 0:
            self._cooldown -= 1

        return ret
