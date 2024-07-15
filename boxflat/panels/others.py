from boxflat.connection_manager import MozaConnectionManager
from boxflat.panels import SettingsPanel
from boxflat.widgets import *

class OtherSettings(SettingsPanel):
    def __init__(self, button_callback: callable, cm: MozaConnectionManager):
        self._brake_calibration = None
        super().__init__("Other", button_callback, connection_manager=cm)


    def subscribe_brake_calibration(self, callback: callable):
        self._brake_calibration.subscribe(callback)


    def prepare_ui(self) -> None:
        self.add_preferences_group("Other settings")
        self._add_row(BoxflatSwitchRow("Base Bluetooth", "For the mobile app"))
        self._current_row.reverse_values()
        self._current_row.set_expression("*85")
        self._current_row.set_reverse_expression("/85")
        self._current_row.subscribe(lambda v: self._cm.set_setting("main-set-ble-mode", v))
        self._cm.subscribe("main-get-ble-mode", self._current_row.set_value)


        self.add_preferences_group("Application settings")
        # self._add_row(BoxflatSwitchRow("Monitor Wheel Position"))
        # self._add_row(BoxflatSwitchRow("Monitor Pedals Output"))
        # self._add_row(BoxflatSwitchRow("Monitor Handbrake Output"))
        self._add_row(BoxflatSwitchRow("Monitor Pedals/Handbrake Output", "Still Buggy"))
        self._current_row.subscribe(self._cm.set_cont_active)

        self._brake_calibration = BoxflatSwitchRow("Enable Brake Calibration", "Do it at your own risk")
        self._add_row(self._brake_calibration)

        self._add_row(BoxflatButtonRow("Read settings from devices", "Refresh"))
        self._current_row.subscribe(self._cm.refresh)

        self._add_row(BoxflatSwitchRow("Read settings continuously"))
        self._current_row.subscribe(self._cm.refresh_cont)
        self._current_row.set_value(1, mute=False)

        self._add_row(BoxflatButtonRow("Refresh Devices", "Refresh"))
        self._current_row.subscribe(self._cm.device_discovery)
