import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib
from .button_row import BoxflatButtonRow
from threading import Thread
from threading import Event
from time import sleep

class BoxflatCalibrationRow(BoxflatButtonRow):
    def __init__(self, title: str, subtitle="", alternative=False):
        super().__init__(title, "Calibrate", subtitle)
        self._alternative = alternative
        self._calibration_event = Event()
        self._thread = Thread(target=self._calibration)
        self._thread.start()


    def _notify(self) -> None:
        self._calibration_event.set()


    def _notify_calibration(self) -> None:
        self._cooldown = 1

        if self._mute:
            return

        for sub in self._subscribers:
            if not self._alternative:
                sub[0](1, f"{sub[1][0]}-{self.get_value()}-calibration")

            else:
                sub[0](self.get_value(), *sub[2])


    def get_value(self) -> str:
        if self._calibration_event.is_set():
            return 1 if self._alternative else "start"
        return 0 if self._alternative else "stop"


    def _calibration(self) -> None:
        while not self._shutdown:
            if not self._calibration_event.wait(timeout=1):
                continue

            GLib.idle_add(self.set_active, False)
            tmp = self.get_subtitle()
            text = "Calibration in progress..."
            print("Calibration start")

            if self._alternative:
                GLib.idle_add(self.set_subtitle, "Press all paddles!")
                sleep(4)

            self._notify_calibration()

            for i in reversed(range(3 if self._alternative else 8)):
                GLib.idle_add(self.set_subtitle, f"{text} {i+1}s")
                sleep(1)

            if self._alternative:
                GLib.idle_add(self.set_subtitle, "Release paddles")
                sleep(3)

            self._calibration_event.clear()
            self._notify_calibration()
            print("Calibration stop")

            GLib.idle_add(self.set_subtitle, tmp)
            GLib.idle_add(self.set_active, True)
