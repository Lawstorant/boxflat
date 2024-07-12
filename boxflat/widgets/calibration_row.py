import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk
from .button_row import BoxflatButtonRow
from threading import Thread
from time import sleep

class BoxflatCalibrationRow(BoxflatButtonRow):
    def __init__(self, title: str, subtitle=""):
        super().__init__(title, "Calibrate", subtitle)
        self._in_progress = False
        self._thread = Thread(target=self._calibration)


    def __del__(self):
        self._thread.stop()


    def _notify(self) -> None:
        self._thread.start()
        super()._notify()


    def get_value(self) -> str:
        if self._in_progress:
            return "stop"
        return "start"


    def _calibration(self) -> None:
        self.set_active(False)
        self._in_progress = True
        tmp = self.get_subtitle()
        text = "Calibration in progress..."
        print("Calibration start")
        super()._notify()

        for i in reversed(range(10)):
            self.set_subtitle(f"{text} {i+1}s")
            sleep(1)

        self._in_progress = False
        print("Calibration stop")
        super()._notify()
        self.set_subtitle(tmp)
        self.set_active(True)
