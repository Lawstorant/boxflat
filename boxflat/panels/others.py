# Copyright (c) 2024, Tomasz Pakuła Using Arch BTW

from boxflat.connection_manager import MozaConnectionManager
from boxflat.panels import SettingsPanel
from boxflat.widgets import *
from boxflat.bitwise import *
from threading import Thread, Event
from gi.repository import Gtk

class OtherSettings(SettingsPanel):
    def __init__(self, button_callback, cm: MozaConnectionManager, hid_handler, version: str):
        super().__init__("Other", button_callback, connection_manager=cm, hid_handler=hid_handler)
        self._version = version
        self._register_event("brake-calibration-active")


    def prepare_ui(self):
        self.add_preferences_group("Other settings")
        self._add_row(BoxflatSwitchRow("Base Bluetooth", "For the mobile app"))
        self._current_row.reverse_values()
        self._current_row.set_expression("*85")
        self._current_row.set_reverse_expression("/85")
        self._current_row.subscribe(self._cm.set_setting, "main-set-ble-mode")
        self._cm.subscribe("main-get-ble-mode", self._current_row.set_value)
        self._cm.subscribe_connected("base-limit", self._current_row.set_active)

        self._add_row(BoxflatSwitchRow("Base FH5 compatibility mode", "Changes USB product ID"))
        self._current_row.subscribe(self._cm.set_setting, "main-set-compat-mode")
        self._cm.subscribe("main-get-compat-mode", self._current_row.set_value)
        self._cm.subscribe_connected("main-get-compat-mode", self._current_row.set_present, +1)

        self._add_row(BoxflatSwitchRow("Pedals FH5 compatibility mode", "Changes USB product ID"))
        self._current_row.subscribe(self._cm.set_setting, "pedals-compat-mode")
        self._cm.subscribe("pedals-compat-mode", self._current_row.set_value)
        self._cm.subscribe_connected("pedals-compat-mode", self._current_row.set_present, +1)


        self.add_preferences_group("Application settings")
        self._add_row(BoxflatSwitchRow("Enable Brake Calibration", "Do it at your own risk"))
        self._current_row.subscribe(self._dispatch, "brake-calibration-active")

        # self._add_row(BoxflatSwitchRow("Read settings continuously"))
        # self._current_row.subscribe(self._cm.refresh_cont)
        # self._current_row.set_value(1, mute=False)

        self._add_row(BoxflatButtonRow("Refresh Devices", "Refresh", subtitle="Not necessary normally"))
        self._current_row.subscribe(self._cm.device_discovery)

        self._add_row(BoxflatSliderRow("HID Update Rate", suffix=" Hz  ", range_start=20, range_end=240, increment=10))
        self._current_row.add_marks(120)
        self._current_row.subscribe(self._hid_handler.set_update_rate)
        self._current_row.set_value(self._hid_handler.get_update_rate())


    def enable_custom_commands(self):
        self.add_preferences_group("Custom command")
        self._command = Adw.EntryRow()
        self._command.set_title("Command name")

        self._value = Adw.EntryRow()
        self._value.set_title("Value")

        commands_url = self._version.removesuffix("-flatpak")
        #commands_url = "https://raw.githubusercontent.com/Lawstorant/boxflat/refs/heads/main/data/serial.yml"
        commands_url = f"https://raw.githubusercontent.com/Lawstorant/boxflat/refs/tags/{commands_url}/data/serial.yml"
        #commands_url = f"https://github.com/Lawstorant/boxflat/blob/{commands_url}/data/serial.yml"

        read = BoxflatButtonRow("Execute command")
        read.add_button("Read", self._read_custom)
        read.add_button("Write", self._write_custom)
        read.add_button("Database", self.open_url, commands_url)

        self._add_row(self._command)
        self._add_row(self._value)
        self._add_row(read)


    def _read_custom(self, *args):
        out = self._cm.get_setting(self._command.get_text())
        if out == -1:
            out = "Error/Command not found"
        self._value.set_text(str(out))


    def _write_custom(self, *args):
        com = self._command.get_text()
        val = eval(self._value.get_text())
        self._cm.set_setting(val, com)
