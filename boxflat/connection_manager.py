import yaml
import os.path
import boxflat.moza_command as mc
from serial import Serial
from threading import Thread
from threading import Lock
import struct
import time

CM_RETRY_COUNT=1

class MozaConnectionManager():
    def __init__(self, serial_data_path: str, dry_run=False):
        self._serial_data = None
        self._dry_run = dry_run
        self._serial_devices = {}
        self._shutdown = False

        with open(serial_data_path) as stream:
            try:
                self._serial_data = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
                quit(1)

        self._subscribtions = {}
        self._refresh_thread = Thread(target=self._notify)

        self._write_command_buffer = {}
        self._read_command_buffer = {}
        self._write_mutex = Lock()
        self._read_mutex = Lock()
        self._rw_thread = Thread(target=self._rw_handler)

        # self._cont_subscribtions = {}
        # self._cont_thread = Thread(target=self._notify_cont)
        # self._cont_enabled = False

        self._message_start= int(self._serial_data["message-start"])
        self._magic_value = int(self._serial_data["magic-value"])
        self._serial_path = "/dev/serial/by-id"
        self._device_discovery()


    def shutdown(self) -> None:
        self._shutdown = True

# TODO: add start-stop watching get commands in threads
    def _device_discovery(self) -> None:
        path = self._serial_path
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


    def subscribe(self, command: str, callback: callable) -> None:
        if not command in self._subscribtions:
            self._subscribtions[command] = []
        self._subscribtions[command].append(callback)


    def refresh(self) -> None:
        while self._refresh_thread.is_alive():
            pass
        self._refresh_thread.start()


    def _notify(self) -> None:
        for com in self._subscribtions.keys():
            if self._shutdown:
                break
            response = self.get_setting_int(com)
            for subscriber in self._subscribtions[com]:
                subscriber(response)


    def set_rw_active(self, active: bool) -> None:
        if active and not self._rw_thread.is_alive():
            self._rw_thread.start()
        elif not active and self._rw_thread.is_alive():
            self._rw_thread.stop()


    def _rw_handler(self) -> None:
        while not self._shutdown:
            time.sleep(0.5)
            if not self._write_mutex.acquire(True, 0.1):
                continue

            write_buffer = self._write_command_buffer
            self._write_command_buffer = {}
            self._write_mutex.release()

            for com in write_buffer.keys():
                self._handle_command(com, mc.MOZA_COMMAND_WRITE, write_buffer[com][0], write_buffer[com][1])


    def _calculate_checksum(self, data: bytes) -> int:
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


    def send_serial_message(self, serial_path: str, message: bytes, read_response=False) -> bytes:
        msg = ""
        for b in message:
            msg += f"{hex(b)} "
        print(f"\nDevice: {serial_path}")
        print(f"Sending:  {msg}")

        if self._dry_run:
            return bytes(1)

        if serial_path == None:
            print("No compatible device found!")
            return bytes(1)

        with Serial(serial_path, baudrate=115200, timeout=1) as serial:
            time.sleep(0.02)
            serial.reset_output_buffer()
            serial.reset_input_buffer()
            serial.read_all()
            for i in range(CM_RETRY_COUNT):
                serial.write(message)

            if read_response == False:
                return bytes(1)

            rest = bytes()
            length = None
            cmp = bytes([self._message_start])
            start = bytes(1)

            while True:
                while start != cmp:
                    start = serial.read(1)

                length = int.from_bytes(serial.read(1))
                if length != message[1]:
                    continue

                # length + 3 because we need to read
                # device id and checksum at the end
                rest = serial.read(length+3)
                if rest[2] != message[4]:
                    continue
                break

            serial.close()

        message = bytearray()
        message.extend(cmp)
        message.append(length)
        message.extend(rest)

        msg = ""
        for b in message:
            msg += f"{hex(b)} "
        print(f"Response: {msg}")

        return message


    # Handle command operations
    def _handle_command(self, command_name: str, rw, value: int=1, byte_value: bytes=None) -> bytes:
        command = mc.MozaCommand(command_name, self._serial_data["commands"])

        if command.length == -1 or command.id == -1:
            print("Command undiscovered")
            return bytes(1)

        if rw == mc.MOZA_COMMAND_READ and command.read_group == -1:
            print("Command doesn't support READ access")
            return bytes(1)

        if rw == mc.MOZA_COMMAND_WRITE and command.write_group == -1:
            print("Command doesn't support WRITE access")
            return bytes(1)

        if byte_value != None:
            command.set_payload_bytes(byte_value)
        else:
            command.payload = value

        device_id = self._get_device_id(command.device_type)
        device_path = self._get_device_path(command.device_type)
        message = command.prepare_message(self._message_start, device_id, rw, self._calculate_checksum)

        # WE get a response without the checksum
        read = rw == mc.MOZA_COMMAND_READ
        response = self.send_serial_message(device_path, message, read)
        if response == bytes(1):
            return response

        # check if length is 2 or lower because we need the
        # device id in the response, not just the value
        # length = response[1]
        # if length <= command.length+1:
        #     return bytes(1)
        length = command.length
        return response[-1-length:-1]

    # Set a setting value on a device
    # If value should be float, provide bytes
    def set_setting(self, command_name: str, value: int=0, byte_value=None) -> None:
        while not self._write_mutex.acquire(1):
            time.sleep(0.001)
            pass
        self._write_command_buffer[command_name] = (value, byte_value)
        self._write_mutex.release()

    def set_setting_float(self, command_name: str, value: float) -> None:
        self.set_setting(command_name, byte_value=bytearray(struct.pack("f", value)))

    def set_setting_list(self, command_name: str, values: list) -> None:
        self.set_setting(command_name, byte_value=bytes(values))

    # Get a setting value from a device
    def get_setting(self, command_name: str) -> bytes:
        return self._handle_command(command_name, mc.MOZA_COMMAND_READ)

    def get_setting_int(self, command_name: str) -> int:
        return int.from_bytes(self.get_setting(command_name))

    def get_setting_list(self, command_name: str) -> list:
        response = self.get_setting(command_name)
        res = []
        for value in response:
            res.append(value)
        return res

    def get_setting_float(self, command_name: str) -> float:
        return float.from_bytes(self.get_setting(command_name))
