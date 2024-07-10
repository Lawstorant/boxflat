import yaml
import os.path
from os import listdir
import boxflat.moza_command as mc
from serial import Serial

CM_RETRY_COUNT=2

class MozaConnectionManager():
    def __init__(self, serial_data_path: str, dry_run=False):
        self._serial_data = None
        self._dry_run = dry_run
        self._serial_devices = {}

        with open(serial_data_path) as stream:
            try:
                self._serial_data = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
                quit(1)

        self._recipents = []
        self._message_start= int(self._serial_data["message-start"])
        self._magic_value = int(self._serial_data["magic-value"])
        self._serial_path = "/dev/serial/by-id"

# TODO: add notifications about parameters?
# TODO: add start-stop watching get commands in threads
    def _device_discovery(self, path: str) -> None:
        if not os.path.exists(path):
            return

        devices = []
        self._serial_devices = {}
        for device in os.listdir(path):
            if device.find("Gudsen_MOZA"):
                devices.append(os.path.join(path, device))

        for device in devices:
            if device.lower().find("base") != -1:
                self._serial_devices["base"] = device

            elif device.lower().find("hbp") != -1:
                self._serial_devices["handbrake"] = device

            elif device.lower().find("hgp") != -1:
                self._serial_devices["hpattern"] = device

            elif device.lower().find("sgp") != -1:
                self._serial_devices["sequential"] = device

            elif device.lower().find("pedals") != -1:
                self._serial_devices["pedals"] = device

            # TODO: Check this info somehow
            elif device.lower().find("stop") != -1:
                self._serial_devices["estop"] = device


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


    def _get_device_id(self, device_type: str) -> int:
        id = int(self._serial_data["device-ids"][device_type])
        if device_type in self._serial_devices:
            id = int(self._serial_data["device-ids"]["main"])
        return id


    def _get_device_path(self, device_type: str) -> str:
        device_path = None
        if device_type in self._serial_devices:
            device_path = self._serial_devices[device_type]

        elif "base" in self._serial_devices and device_type != "hub":
            device_path = self._serial_devices["base"]

        return device_path


    def send_serial_message(self, serial_path: str, message: bytes) -> None:
        msg = ""
        for b in message:
            msg += f"{hex(b)} "
        print(f"\nSending: {msg}")
        print(f"Device: {serial_path}")

        if self._dry_run:
            return

        if serial_path == None:
            print("No compatible device found!")
            return

        with Serial(serial_path) as serial:
            for i in range(0, CM_RETRY_COUNT):
                serial.write(message)
            serial.close()


    # Handle command operations
    def _handle_command(self, command_name: str, rw, value: int=0, byte_value: bytes=None):
        command = mc.MozaCommand(command_name, self._serial_data["commands"])

        if command.length == -1 or command.id == -1:
            print("Command undiscovered")
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

        self._device_discovery(self._serial_path)

        device_id = self._get_device_id(command.device_type)
        device_path = self._get_device_path(command.device_type)

        self.send_serial_message(device_path,
            command.prepare_message(self._message_start, device_id, rw, self._calculate_security_byte))


    # Set a setting value on a device
    # If value should be float, provide bytes
    def set_setting(self, command_name: str, value=0, byte_value=None) -> None:
        if value == None:
            return
        self._handle_command(command_name, mc.MOZA_COMMAND_WRITE, value, byte_value)


    # Get a setting value from a device
    def get_setting(self, command_name: str):
        self._handle_command(command_name, mc.MOZA_COMMAND_READ)
        return 0
