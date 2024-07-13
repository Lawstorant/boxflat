from boxflat.connection_manager import MozaConnectionManager
from boxflat.panels import SettingsPanel
from boxflat.widgets import *

class OtherSettings(SettingsPanel):
    def __init__(self, button_callback: callable, cm: MozaConnectionManager):
        super().__init__("Other", button_callback, connection_manager=cm)


    def prepare_ui(self) -> None:
        self.add_preferences_group("Other settings")
        # self._add_row(BoxflatSwitchRow("Monitor Wheel Position"))
        # self._add_row(BoxflatSwitchRow("Monitor Pedals Output"))
        # self._add_row(BoxflatSwitchRow("Monitor Handbrake Output"))
        self._add_row(BoxflatSwitchRow("Monitor Pedals/Handbrake Output"))
        self._current_row.subscribe(self._cm.set_cont_active)

        self._add_row(BoxflatButtonRow("Load settings from devices", "Refresh"))
        self._current_row.subscribe(self._cm.refresh)

        self._add_row(BoxflatButtonRow("Refresh Devices", "Refresh"))
        self._current_row.subscribe(self._cm.device_discovery)
