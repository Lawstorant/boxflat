import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk
from .row import BoxflatRow

class BoxflatEqRow(BoxflatRow):
    def __init__(self, title="", subtitle="", draw_values=True):
        super().__init__(title, subtitle)

        label = Gtk.Label()
        label.set_text("XD")
        self.set_child(label)
