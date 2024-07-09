import yaml
import os.path
from boxflat.moza_command import MozaCommand

RETRY_COUNT=3

class MozaConnectionManager():
    def __init__(self, serial_data_path: str):
        self._serial_data = None
        with open(serial_data_path) as stream:
            try:
                self._serial_data = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
                quit(1)

        self._recipents = []
        self._message_start= int(self._serial_data["message-start"])
        self._magic_value = int(self._serial_data["magic-value"])

# TODO: add notifications about parameters?
# TODO: add start-stop watching get commands in threads
    def _device_discovery(self) -> None:
        pass

    def subscribe(self, callback: callable) -> None:
        self._recipents.append(callback)

    def notify(self) -> None:
        for recipent in self._recipents:
            pass

    def _calculate_security_byte(self, data: bytes) -> int:
        value = self._magic_value
        for d in data:
            value += int(d)
        return value % 256

    def send_serial_packet(self, message: bytes) -> None:
        msg = ""
        for b in message:
            msg += f"{hex(b)} "
        print(f"Sending: {msg}")

        # TODO: device search
        tty_path = "/dev/ttyACM0"
        if not os.path.isfile(tty_path):
            print(f"{tty_path} -> Device not found\n")
            return

        with open(tty_path, "wb") as tty:
            for i in range(0, RETRY_COUNT):
                tty.write(message)
            tty.close()

    # These probably can be yeeted
    def get_request_group(self, command_name: str, rw: str) -> int:
        return int(_serial_data[name][rw])

    def get_command_id(self, command_name: str) -> int:
        return int(_serial_data[name]["id"])

    def get_device_id(self, device_type: str) -> int:
        return int("0x" + _serial_data["device-ids"][device_type], 0)


    # Set a setting value on a device
    def set_setting(self, command_name: str, device_id: int, value=0, byte_value=None):
        command = MozaCommand(command_name, self._serial_data["commands"])

        if command.length == -1 or command.id == -1:
            print("Command not known yet")
            return

        if command.write_group == -1:
            print("Command doesn't support write access")
            return

        if byte_value != None:
            command.set_payload_bytes(byte_value)
        else:
            command.payload = value

        self.send_serial_packet(
            command.prepare_message(self._message_start, device_id, "w", self._calculate_security_byte))


    # Get a setting value from a device
    def get_setting(self, command_name: str, device_id: int):
        command = MozaCommand(command_name, self._serial_data["commands"])

        if command.length == -1 or command.id == -1:
            print("Command not known yet")
            return

        if command.read_group == -1:
            print("Command doesn't support read access")
            return

        self.send_serial_packet(
            command.prepare_message(self._message_start, device_id, "r", self._calculate_security_byte))


    # helper functions
    def set_base_setting(self, name: str, value=0, byte_value=None) -> None:
        device_id = int(self._serial_data["device-ids"]["base"])
        self.set_setting(name, device_id, value, byte_value)

    def set_wheel_setting(self, name: str, value=0, byte_value=None) -> None:
        device_id = int(self._serial_data["device-ids"]["wheel"])
        self.set_setting(name, device_id, value, byte_value)

    def set_pedals_setting(self, name: str, value=0, byte_value=None) -> None:
        device_id = int(self._serial_data["device-ids"]["pedals"])
        self.set_setting(name, device_id, value, byte_value)

    def set_h_pattern_setting(self, name: str, value=0, byte_value=None) -> None:
        device_id = int(self._serial_data["device-ids"]["hpattern"])
        self.set_setting(name, device_id, value, byte_value)

    def set_sequential_setting(self, name: str, value=0, byte_value=None) -> None:
        device_id = int(self._serial_data["device-ids"]["sequential"])
        self.set_setting(name, device_id, value, byte_value)

    def set_handbrake_setting(self, name: str, value=0, byte_value=None) -> None:
        device_id = int(self._serial_data["device-ids"]["handbrake"])
        self.set_setting(name, device_id, value, byte_value)

    def set_dashboard_setting(self, name: str, value=0, byte_value=None) -> None:
        device_id = int(self._serial_data["device-ids"]["dash"])
        self.set_setting(name, device_id, value, byte_value)

    def set_hub_setting(self, name: str, value=0, byte_value=None) -> None:
        device_id = int(self._serial_data["device-ids"]["hub"])
        self.set_setting(name, device_id, value, byte_value)

    def set_e_stop_setting(self, name: str, value=0, byte_value=None) -> None:
        device_id = int(self._serial_data["device-ids"]["estop"])
        self.set_setting(name, device_id, value, byte_value)
