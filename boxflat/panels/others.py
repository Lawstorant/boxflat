from boxflat.connection_manager import MozaConnectionManager
from boxflat.panels import SettingsPanel
from boxflat.widgets import *
from boxflat.bitwise import *
from threading import Thread, Event

class OtherSettings(SettingsPanel):
    def __init__(self, button_callback: callable, cm: MozaConnectionManager, hid_handler):
        self._brake_calibration = None
        super().__init__("Other", button_callback, connection_manager=cm, hid_handler=hid_handler)


    def subscribe_brake_calibration(self, callback: callable):
        self._brake_calibration.subscribe(callback)


    def prepare_ui(self) -> None:
        self.add_preferences_group("Other settings")
        self._add_row(BoxflatSwitchRow("Base Bluetooth", "For the mobile app"))
        self._current_row.reverse_values()
        self._current_row.set_expression("*85")
        self._current_row.set_reverse_expression("/85")
        self._current_row.subscribe(self._cm.set_setting_int, "main-set-ble-mode")
        self._append_sub("main-get-ble-mode", self._current_row.set_value)
        self._append_sub_connected("base-limit", self._current_row.set_active)

        self._add_row(BoxflatSwitchRow("Base FH5 compatibility mode", "Changes USB product ID"))
        self._current_row.subscribe(self._cm.set_setting_int, "main-set-compat-mode")
        self._append_sub("main-get-compat-mode", self._current_row.set_value)
        self._append_sub_connected("main-get-compat-mode", self._current_row.set_present, +1)

        self._add_row(BoxflatSwitchRow("Pedals FH5 compatibility mode", "Changes USB product ID"))
        self._current_row.subscribe(self._cm.set_setting_int, "pedals-compat-mode")
        self._append_sub("pedals-compat-mode", self._current_row.set_value)
        self._append_sub_connected("pedals-compat-mode", self._current_row.set_present, +1)


        self.add_preferences_group("Application settings")

        self._brake_calibration = BoxflatSwitchRow("Enable Brake Calibration", "Do it at your own risk")
        self._add_row(self._brake_calibration)

        self._add_row(BoxflatSwitchRow("Read settings continuously"))
        self._current_row.subscribe(self._cm.refresh_cont)
        self._current_row.set_value(1, mute=False)

        self._add_row(BoxflatButtonRow("Refresh Devices", "Refresh", subtitle="Not necessary normally"))
        self._current_row.subscribe(self._cm.device_discovery)

        self._add_row(BoxflatSliderRow("HID Update Rate", suffix="Hz", range_start=20, range_end=240, increment=10))
        self._current_row.add_marks(120)
        self._current_row.subscribe(self._hid_handler.set_update_rate)
        self._current_row.set_value(self._hid_handler.get_update_rate())

        # self.add_preferences_group("Custom command")
        # self._command = Adw.EntryRow()
        # self._command.set_title("Command name")

        # self._value = Adw.EntryRow()
        # self._value.set_title("Value")

        # read = BoxflatButtonRow("Execute command", "Read")
        # write = BoxflatButtonRow("Execute command", "Write")

        # read.subscribe(self._read_custom)
        # write.subscribe(self._write_custom)

        # self._add_row(self._command)
        # self._add_row(self._value)
        # self._add_row(read)
        # self._add_row(write)


    def _read_custom(self, *args) -> None:
        out = self._cm.get_setting_int(self._command.get_text())
        self._value.set_text(str(out))


    def _write_custom(self, *args) -> None:
        com = self._command.get_text()
        val = int(self._value.get_text())
        self._cm.set_setting_int(val, com)
