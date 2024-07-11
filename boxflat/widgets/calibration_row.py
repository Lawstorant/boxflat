import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk
from .button_row import BoxflatButtonRow
from threading import Thread
from time import sleep

class BoxflatCalibrationRow(BoxflatButtonRow):
    def __init__(self, title: str, subtitle=""):
        super().__init__(title, "Calibration", subtitle)
        self._in_progress = False
        self._thread = Thread(target=self._calibration)


    def __del__(self):
        self._thread.stop()


    def _notify(self) -> None:
        self._thread.start()


    def _value_handler(self, value) -> str:
        if self._in_progress:
            return "stop"
        return "start"


    def _calibration(self) -> None:
        self.active = False
        self._in_progress = True
        tmp = self.subtitle
        text = "Calibration in progress..."
        print("Calibration start")
        super()._notify()

        for i in reversed(range(10)):
            self.subtitle = f"{text} {i+1}s"
            sleep(1)

        self._in_progress = False
        print("Calibration stop")
        super()._notify()
        self.subtitle = tmp
        self.active = True
