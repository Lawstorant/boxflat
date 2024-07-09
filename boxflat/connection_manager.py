import yaml
import os.path
import boxflat.moza_command as mc

CM_RETRY_COUNT=3

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


    def _get_device_id(self, command: str) -> int:
        return int(self._serial_data["device-ids"][command.split("-")[0]])


    def send_serial_packet(self, message: bytes) -> None:
        msg = ""
        for b in message:
            msg += f"{hex(b)} "
        print(f"Sending: {msg}")

        # TODO: device search
        # tty_path = "/dev/ttyACM0"
        # if not os.path.isfile(tty_path):
        #     print(f"{tty_path} -> Device not found\n")
        #     return

        with open(tty_path, "wb") as tty:
            for i in range(0, CM_RETRY_COUNT):
                tty.write(message)
            tty.close()

    # Handle command operations
    def _handle_command(self, command_name: str, rw, value: int, byte_value: bytes):
        command = mc.MozaCommand(command_name, self._serial_data["commands"])
        device_id = self._get_device_id(command_name)

        if command.length == -1 or command.id == -1:
            print("Command not known yet")
            return

        if rw == mc.MOZA_COMMAND_READ and command.read_group == -1:
            print("Command doesn't support READ access")
            return

        if rw == mc.MOZA_COMMAND_WRITE and command.write_group == -1:
            print("Command doesn't support WRITE access")
            return

        if rw == mc.MOZA_COMMAND_WRITE:
            if byte_value != None:
                command.set_payload_bytes(byte_value)
            else:
                command.payload = value

        self.send_serial_packet(
            command.prepare_message(self._message_start, device_id, rw, self._calculate_security_byte))


    # Set a setting value on a device
    def set_setting(self, command_name: str, value=0, byte_value=None):
        self._handle_command(command_name, mc.MOZA_COMMAND_WRITE, value, byte_value)


    # Get a setting value from a device
    def get_setting(self, command_name: str):
        self._handle_command(command_name, mc.MOZA_COMMAND_READ, value, byte_value)
