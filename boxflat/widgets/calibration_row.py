import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib
from .button_row import BoxflatButtonRow
from threading import Thread
from time import sleep
from boxflat.subscription import EventDispatcher

class BoxflatCalibrationRow(EventDispatcher, BoxflatButtonRow):
    def __init__(self, title: str, subtitle="", alternative=False):
        BoxflatButtonRow.__init__(self, title, button_label="Calibrate", subtitle=subtitle)
        EventDispatcher.__init__(self)

        self._alternative = alternative
        self._register_events("calibration-start", "calibration-stop")


    def _notify(self, *rest):
        Thread(daemon=True, target=self._calibration).start()


    def _calibration(self):
        GLib.idle_add(self.set_active, False)
        tmp = self.get_subtitle()
        text = "Calibration in progress..."
        print("Calibration start")

        if self._alternative:
            GLib.idle_add(self.set_subtitle, "Press all paddles!")
            sleep(4)

        self._dispatch("calibration-start")

        for i in reversed(range(3 if self._alternative else 8)):
            GLib.idle_add(self.set_subtitle, f"{text} {i+1}s")
            sleep(1)

        if self._alternative:
            GLib.idle_add(self.set_subtitle, "Release paddles")
            sleep(3)

        self._dispatch("calibration-stop")
        print("Calibration stop")

        GLib.idle_add(self.set_subtitle, tmp)
        GLib.idle_add(self.set_active, True)
