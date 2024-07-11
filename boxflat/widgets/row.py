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
        self.title = title
        self.subtitle = subtitle

    @property
    def active(self) -> bool:
        return self.get_sensitive()

    @active.setter
    def active(self, value: bool) -> None:
        self.set_sensitive(bool(value))

    def set_active(self, value: bool) -> None:
        self.active = value

    @property
    def title(self) -> str:
        return self.get_title()

    @title.setter
    def title(self, title: str) -> None:
        self.set_title(title)

    @property
    def subtitle(self) -> str:
        return self.get_subtitle()

    @subtitle.setter
    def subtitle(self, subtitle: str) -> None:
        self.set_subtitle(subtitle)

    def mute(self) -> None:
        self._mute = True

    def unmute(self) -> None:
        self._mute = False

    @property
    def value(self):
        return self.get_value()

    @value.setter
    def value(self, value) -> None:
        self.set_value(value)

    def get_value(self, ) -> int:
        return self._value_handler(None)

    def set_value(self, value) -> None:
        self.mute()
        self._value_handler(value)
        self.unmute()

    def _set_widget(self, widget: Gtk.Widget) -> None:
        self.add_suffix(widget)

    def subscribe(self, callback: callable) -> None:
        self._subscribers.append(callback)

    def _notify(self) -> None:
        if self._mute:
            return

        for callback in self._subscribers:
            callback(self.value)

    def _value_handler(self, *args) -> int:
        return 1
