import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw
import time

class BoxflatRow(Adw.ActionRow):
    def __init__(self, title="", subtitle=""):
        super().__init__()
        self._subscribers = []
        self._mute = False
        self._shutdown = False
        self.set_sensitive(True)
        self.set_title(title)
        self.set_subtitle(subtitle)
        self._expression = "*1"
        self._reverse_expression = "*1"
        self.set_size_request(620, 0)


    def get_active(self) -> bool:
        return self.get_sensitive()


    def set_active(self, value) -> None:
        self.set_sensitive(int(value) == 1)


    def set_present(self, value) -> None:
        print(value)
        self.set_visible(int(value) != -1)


    def mute(self, value: bool=True) -> None:
        self._mute = value


    def unmute(self) -> None:
        self._mute = False


    def get_value(self) -> int:
        return 0


    def get_raw_value(self) -> int:
        return self.get_value()


    def set_value(self, value, mute: bool=True) -> None:
        self.mute(mute)
        self._set_value(value)
        self.unmute()


    def _set_value(self, value) -> None:
        pass


    def _set_widget(self, widget: Gtk.Widget) -> None:
        self.add_suffix(widget)


    def subscribe(self, callback: callable, *args, raw=False) -> None:
        self._subscribers.append((callback, raw, args))


    def clear_subscribtions(self) -> None:
        self._subscribers = []


    def _notify(self) -> None:
        if self._mute:
            return

        for sub in self._subscribers:
            value = self.get_raw_value() if sub[1] else self.get_value()
            sub[0](value, *sub[2])


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
