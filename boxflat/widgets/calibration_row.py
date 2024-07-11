import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw

from boxflat.widgets import BoxflatButtonRow

class BoxflatCalibrationRow(BoxflatButtonRow):
    def __init__(self, title: str, button_label: str, subtitle=""):
        super().__init__(title, button_label, subtitle)

    def _value_handler(self, *args):
        return 2
