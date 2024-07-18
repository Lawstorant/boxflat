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
        # self._thread.start()


    def _notify(self) -> None:
        self._in_progress = True


    def _notify_calibration(self) -> None:
        if self._mute:
            return

        for sub in self._subscribers:
            sub[0](1, f"{sub[1]}-{self.get_value()}-calibration")


    def get_value(self) -> str:
        if self._in_progress:
            return "stop"
        return "start"


    def _calibration(self) -> None:
        while True:
            if not self._in_progress:
                sleep(0.5)
                continue

            self.set_active(False)
            tmp = self.get_subtitle()
            text = "Calibration in progress..."
            print("Calibration start")
            self._notify_calibration()

            for i in reversed(range(10)):
                self.set_subtitle(f"{text} {i+1}s")
                sleep(1)

            self._in_progress = False
            print("Calibration stop")
            self._notify_calibration()
            self.set_subtitle(tmp)
            self.set_active(True)
