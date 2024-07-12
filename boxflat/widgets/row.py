import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw

class BoxflatRow(Adw.ActionRow):
    def __init__(self, title="", subtitle=""):
        super().__init__()
        self._subscribers = []
        self._mute = False
        self.set_sensitive(True)
        self.set_title(title)
        self.set_subtitle(subtitle)

    def get_active(self) -> bool:
        return self.get_sensitive()

    def set_active(self, value: bool) -> None:
        self.set_sensitive(bool(value))

    def mute(self) -> None:
        self._mute = True

    def unmute(self) -> None:
        self._mute = False

    def get_value(self) -> int:
        return 0

    def set_value(self, value) -> None:
        pass

    def set_value_discreet(self, value) -> None:
        self.mute()
        self.set_value(value)
        self.unmute()

    def _set_widget(self, widget: Gtk.Widget) -> None:
        self.add_suffix(widget)

    def subscribe(self, callback: callable) -> None:
        self._subscribers.append(callback)

    def _notify(self) -> None:
        if self._mute:
            return

        for callback in self._subscribers:
            callback(self.get_value())
