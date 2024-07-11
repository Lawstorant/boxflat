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
        return self._row.get_suffix().get_sensitive()

    @active.setter
    def active(self, value: bool) -> None:
        self.set_sensitive(value)

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

    @property
    def value(self):
        return self._value_handler()

    @value.setter
    def value(self, value) -> None:
        self._mute = True
        self._value_handler(value)
        self._mute = False

    def _set_widget(self, widget: Gtk.Widget) -> None:
        self.add_suffix(widget)

    def subscribe(self, callback: callable) -> None:
        self._subscribers.append(callback)

    def _notify(self) -> None:
        if self._mute:
            return

        for callback in self._subscribers:
            callback(self.value)

    def _value_handler(self, *args):
        return 1
