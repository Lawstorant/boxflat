import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk
from .row import BoxflatRow

class BoxflatSwitchRow(BoxflatRow):
    def __init__(self, title: str, subtitle=""):
        super().__init__(title, subtitle)

        switch = Gtk.Switch()
        switch.add_css_class("switch")
        switch.connect('notify::active', lambda switch, whatever: self._notify())
        switch.set_valign(Gtk.Align.CENTER)
        self._reverse = False
        self._switch = switch
        self._set_widget(switch)
        self.set_activatable_widget(switch)
        self._value_store = None


    def get_value(self) -> int:
        if not self.get_active():
            return 0

        val = self._switch.get_active()
        if self._reverse:
            val = not val

        return round(eval("int(val)" + self._expression))


    def reverse_values(self) -> None:
        self._reverse = True


    def _set_value(self, value: int) -> None:
        if value < 0:
            return

        val = round(eval("value"+self._reverse_expression))
        if val < 0:
            val = 0
        if self._reverse:
            val = not bool(val)
        self._switch.set_active(bool(val))


    def set_active(self, value=1, offset=0, off_when_inactive=False) -> bool:
        change = super().set_active(value, offset=offset)

        if not change:
            return change

        if off_when_inactive and self._value_store == None:
            self._value_store = self.get_value()
            self.set_value(0)

        elif off_when_inactive and self._value_store != None:
            self.set_value(self._value_store)
            self._value_store = None

        return change
