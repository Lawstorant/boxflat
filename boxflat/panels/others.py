from boxflat.connection_manager import MozaConnectionManager
from boxflat.panels import SettingsPanel
from boxflat.widgets import *
from boxflat.bitwise import *
from threading import Thread, Event

class OtherSettings(SettingsPanel):
    def __init__(self, button_callback: callable, cm: MozaConnectionManager):
        self._brake_calibration = None
        self._test_thread = Thread(target=self._wheel_rpm_test)
        self._test_event = Event()
        self._shutdown = False
        self._test_thread.start()
        super().__init__("Other", button_callback, connection_manager=cm)
        self._cm.subscribe_shutdown(self.shutdown)


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

        self._add_row(BoxflatSwitchRow("Base FH5 compatibility mode", "Breaks Forza Horizon 5 on linux"))
        self._current_row.subscribe(self._cm.set_setting_int, "main-set-compat-mode")
        self._append_sub("main-get-compat-mode", self._current_row.set_value)

        self._add_row(BoxflatSwitchRow("Pedals FH5 compatibility mode", "Breaks Forza Horizon 5 on linux"))
        self._current_row.subscribe(self._cm.set_setting_int, "pedals-compat-mode")
        self._append_sub("pedals-compat-mode", self._current_row.set_value)


        self.add_preferences_group("Application settings")
        # self._add_row(BoxflatSwitchRow("Monitor Wheel Position"))
        # self._add_row(BoxflatSwitchRow("Monitor Pedals Output"))
        # self._add_row(BoxflatSwitchRow("Monitor Handbrake Output"))
        self._add_row(BoxflatSwitchRow("Monitor Pedals/Handbrake Output"))
        self._current_row.subscribe(self._cm.set_cont_active)
        self._current_row.set_value(1, mute=False)

        self._brake_calibration = BoxflatSwitchRow("Enable Brake Calibration", "Do it at your own risk")
        self._add_row(self._brake_calibration)

        self._add_row(BoxflatButtonRow("Read settings from devices", "Refresh"))
        self._current_row.subscribe(self._cm.refresh)

        self._add_row(BoxflatSwitchRow("Read settings continuously"))
        self._current_row.subscribe(self._cm.refresh_cont)
        self._current_row.set_value(1, mute=False)

        self._add_row(BoxflatButtonRow("Refresh Devices", "Refresh", subtitle="Not necessary normally"))
        self._current_row.subscribe(self._cm.device_discovery)

        self.add_preferences_group("Testing")
        self._add_row(BoxflatButtonRow("Wheel RPM test", "Test"))
        self._current_row.subscribe(self.start_test)

        # self.add_preferences_group("Custom command")
        # self._command = Adw.EntryRow()
        # self._command.set_title("Command name")
        # self._command.set_text("wheel-set-telemetry")

        # self._value = Adw.EntryRow()
        # self._value.set_title("Value")
        # self._value.set_text("ffff83ff")

        # read = BoxflatButtonRow("Execute command", "Read")
        # write = BoxflatButtonRow("Execute command", "Write")

        # read.subscribe(self._read_custom)
        # write.subscribe(self._write_custom)

        # self._add_row(self._command)
        # self._add_row(self._value)
        # self._add_row(read)
        # self._add_row(write)


    def _read_custom(self, *args) -> None:
        out = self._cm.get_setting_list(self._command.get_text())
        self._value.set_text(str(out))


    def _write_custom(self, *args) -> None:
        com = self._command.get_text()
        val = int(self._value.get_text())
        self._cm.set_setting_int(com, val)


    def shutdown(self, *args) -> None:
        self._shutdown = True


    def start_test(self, *args) -> None:
        self._test_event.set()


    def _wheel_rpm_test(self, *args) -> None:
        while not self._shutdown:
            if not self._test_event.wait(timeout=1):
                continue

            self._test_event.clear()

            t = 0.3
            for i in range(10):
                val = modify_bit(0, i)
                self._cm.set_setting_int(val, "wheel-send-telemetry")
                time.sleep(t)

            for i in reversed(range(9)):
                val = modify_bit(0, i)
                self._cm.set_setting_int(val, "wheel-send-telemetry")
                time.sleep(t)

            val = 0
            self._cm.set_setting_int(val, "wheel-send-telemetry")
            time.sleep(t)
            for i in range(10):
                val = modify_bit(val, i)
                self._cm.set_setting_int(val, "wheel-send-telemetry")
                time.sleep(t)

            time.sleep(0.5)
            val = modify_bit(0,15)
            self._cm.set_setting_int(val, "wheel-send-telemetry")
