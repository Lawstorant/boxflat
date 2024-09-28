from gi.repository import Gtk, Adw
from . import BoxflatRow

class BoxflatAdvanceRow(BoxflatRow):
    def __init__(self, title="", subtitle=""):
        super().__init__(title=title, subtitle=subtitle)

        icon = Gtk.Image()
        icon.set_from_icon_name("go-next-symbolic")
        icon.set_valign(Gtk.Align.CENTER)

        self._set_widget(icon)
        self.set_activatable(True)

        self.connect("activated", lambda v: self._notify)
