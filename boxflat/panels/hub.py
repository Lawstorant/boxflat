# Copyright (c) 2024, Tomasz Pakuła Using Arch BTW

from boxflat.panels.settings_panel import SettingsPanel
from boxflat.connection_manager import MozaConnectionManager
from boxflat.widgets import *

class HubSettings(SettingsPanel):
    def __init__(self, button_callback, connection_manager: MozaConnectionManager):
        self._S1 = None
        self._S2 = None
        super().__init__("Universal Hub", button_callback, connection_manager)
        self._cm.subscribe_connected("hub-base", self.active)


    def prepare_ui(self):
        self.add_preferences_group("Base")
        self._add_row(BoxflatLabelRow("Base Port", "Unsupported in firmware"))
        self._current_row.set_label("Disconnected")

        self.add_preferences_group("Pedals")
        self._add_row(BoxflatLabelRow("Pedals Port"))
        self._current_row.set_label("Disconnected")
        self._cm.subscribe("hub-pedals1", self._handle_connected, self._current_row, True)

        self.add_preferences_group("Accessories")

        self._add_row(BoxflatLabelRow("Port 1"))
        self._current_row.set_label("Disconnected")
        self._cm.subscribe("hub-port1", self._handle_connected, self._current_row)

        self._add_row(BoxflatLabelRow("Port 2"))
        self._current_row.set_label("Disconnected")
        self._cm.subscribe("hub-port2", self._handle_connected, self._current_row)

        self._add_row(BoxflatLabelRow("Port 3"))
        self._current_row.set_label("Disconnected")
        self._cm.subscribe("hub-port3", self._handle_connected, self._current_row)


    def _handle_connected(self, value: int, row: BoxflatLabelRow, pedals=False) -> None:
        new_label = "Connected"
        if (value >> 8 < 1 if pedals else value > 1):
            new_label = "Disconnected"

        row.set_label(new_label)
