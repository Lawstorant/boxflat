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
        self.set_sensitive(True)
        self.set_title(title)
        self.set_subtitle(subtitle)
        self._expression = "*1"
        self._reverse_expression = "*1"
        self.set_size_request(585, 0)


    def get_active(self) -> bool:
        return self.get_sensitive()


    def set_active(self, value: bool) -> None:
        self.set_sensitive(bool(value))


    def mute(self, value: bool=True) -> None:
        self._mute = value


    def unmute(self) -> None:
        self._mute = False


    def get_value(self) -> int:
        return 0


    def set_value(self, value, mute: bool=True) -> None:
        self.mute(mute)
        self._set_value(value)
        self.unmute()

    def _set_value(self, value) -> None:
        pass


    def _set_widget(self, widget: Gtk.Widget) -> None:
        self.add_suffix(widget)


    def subscribe(self, callback: callable) -> None:
        self._subscribers.append(callback)


    def _notify(self) -> None:
        if self._mute:
            return

        for callback in self._subscribers:
            callback(self.get_value())

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

