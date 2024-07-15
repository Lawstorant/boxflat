import yaml
import os.path
from .moza_command import *
from serial import Serial
from threading import Thread
from threading import Lock
import struct
import time

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import GLib

CM_RETRY_COUNT=1

class MozaConnectionManager():
    def __init__(self, serial_data_path: str, dry_run=False):
        self._serial_data = None
        self._dry_run = dry_run
        self._shutdown = False

        self._serial_devices = {}
        self._devices_lock = Lock()

        with open(serial_data_path) as stream:
            try:
                self._serial_data = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
                self._shutdown = True
                quit(1)

        self._serial_lock = Lock()

        self._refresh = False
        self._refresh_cont = False
        self._subscribtions = {}
        self._refresh_thread = Thread(target=self._notify)
        self._refresh_thread.start()

        self._cont_active = False
        self._cont_subscribtions = {}
        self._cont_thread = Thread(target=self._notify_cont)
        self._cont_thread.start()

        self._write_command_buffer = {}
        self._read_command_buffer = {}
        self._write_mutex = Lock()
        self._read_mutex = Lock()
        self._rw_thread = Thread(target=self._rw_handler)

        self._message_start= int(self._serial_data["message-start"])
        self._magic_value = int(self._serial_data["magic-value"])
        self._serial_path = "/dev/serial/by-id"
        self.device_discovery()


    def shutdown(self) -> None:
        self._shutdown = True


    def device_discovery(self, *args) -> None:
        print("\nDevice discovery...")
        path = self._serial_path

        self._devices_lock.acquire()
        self._serial_devices = {}

        if not os.path.exists(path):
            print("No devices found!")
            self._devices_lock.release()
            return


        devices = []
        for device in os.listdir(path):
            if device.find("Gudsen_MOZA"):
                devices.append(os.path.join(path, device))

        for device in devices:
            if device.lower().find("base") != -1:
                self._serial_devices["base"] = device
                self._serial_devices["main"] = device
                print("Base found")

            elif device.lower().find("hbp") != -1:
                self._serial_devices["handbrake"] = device
                print("Handbrake found")

            elif device.lower().find("hgp") != -1:
                self._serial_devices["hpattern"] = device
                print("H-Pattern shifter found")

            elif device.lower().find("sgp") != -1:
                self._serial_devices["sequential"] = device
                print("Sequential shifter found")

            elif device.lower().find("pedals") != -1:
                self._serial_devices["pedals"] = device
                print("Pedals found")

            # TODO: Check this info somehow
            elif device.lower().find("hub") != -1:
                self._serial_devices["hub"] = device
                print("Hub found")

            elif device.lower().find("stop") != -1:
                self._serial_devices["estop"] = device
                print("E-Stop found")

        self._devices_lock.release()
        print("Device discovery end\n")


    def subscribe(self, command: str, callback: callable) -> None:
        if not command in self._subscribtions:
            self._subscribtions[command] = []
        self._subscribtions[command].append(callback)


    def subscribe_cont(self, command: str, callback: callable) -> None:
        if not command in self._cont_subscribtions:
            self._cont_subscribtions[command] = []
        self._cont_subscribtions[command].append(callback)


    def refresh(self, *args) -> None:
        self._refresh = True


    def refresh_cont(self, active: bool) -> None:
        self._refresh_cont = active
        self._refresh = active


    def _notify(self) -> None:
        response = 0
        while not self._shutdown:
            if not self._refresh:
                time.sleep(1)
                continue

            if not self._refresh_cont:
                self._refresh = False

            for com in self._subscribtions.keys():
                if self._serial_data["commands"][com]["type"] == "array":
                    response = self.get_setting_list(com)
                else:
                    response = self.get_setting_int(com)

                for subscriber in self._subscribtions[com]:
                    subscriber(response)

            if self._refresh_cont:
                time.sleep(5)


    def _notify_cont(self) -> None:
        while not self._shutdown:
            if not self._cont_active:
                time.sleep(1)
                continue

            time.sleep(1/30) # 30 Hz refresh rate
            for com in self._cont_subscribtions.keys():
                response = self.get_setting_int(com)
                for subscriber in self._cont_subscribtions[com]:
                    GLib.idle_add(subscriber, response)


    def set_cont_active(self, active: bool) -> None:
        self._cont_active = active


    def set_rw_active(self, active: bool) -> None:
        if active and not self._rw_thread.is_alive():
            self._rw_thread.start()
        elif not active and self._rw_thread.is_alive():
            self._rw_thread.stop()


    def _rw_handler(self) -> None:
        while not self._shutdown:
            time.sleep(0.5)

            self._write_mutex.acquire()
            write_buffer = self._write_command_buffer
            self._write_command_buffer = {}
            self._write_mutex.release()

            for com in write_buffer.keys():
                self._handle_command(com, MOZA_COMMAND_WRITE, write_buffer[com][0], write_buffer[com][1])


    def _calculate_checksum(self, data: bytes) -> int:
        value = self._magic_value
        for d in data:
            value += int(d)
        return value % 256


    def _get_device_id(self, device_type: str) -> int:
        id = int(self._serial_data["device-ids"][device_type])
        if device_type != "base" and device_type in self._serial_devices:
            id = int(self._serial_data["device-ids"]["main"])
        return id


    def _get_device_path(self, device_type: str) -> str:
        device_path = None

        self._devices_lock.acquire()

        if device_type in self._serial_devices:
            device_path = self._serial_devices[device_type]

        elif "base" in self._serial_devices and device_type != "hub":
            device_path = self._serial_devices["base"]

        self._devices_lock.release()

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

        rest = bytes()
        length = 0
        cmp = bytes([self._message_start])
        start = bytes(1)

        self._serial_lock.acquire()
        try:
            serial = Serial(serial_path, baudrate=115200, timeout=0.3)
            time.sleep(1/200)
            serial.reset_output_buffer()
            serial.reset_input_buffer()
            for i in range(CM_RETRY_COUNT):
                serial.write(message)

            # read_response = True # For teesting writes
            start_time = time.time()
            while read_response:
                if time.time() - start_time > 0.5:
                    read_response = False
                    break

                start = serial.read(1)
                if start != cmp:
                    continue

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
        except TypeError as error:
            print("Error opening device!")
            read_response = False

        self._serial_lock.release()

        if read_response == False:
            return bytes(1)

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
        command = MozaCommand(command_name, self._serial_data["commands"])

        if command.length == -1 or command.id == -1:
            print("Command undiscovered")
            return bytes(1)

        if rw == MOZA_COMMAND_READ and command.read_group == -1:
            print("Command doesn't support READ access")
            return bytes(1)

        if rw == MOZA_COMMAND_WRITE and command.write_group == -1:
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
        read = rw == MOZA_COMMAND_READ
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
        self._write_mutex.acquire()
        self._write_command_buffer[command_name] = (value, byte_value)
        self._write_mutex.release()

    def set_setting_float(self, command_name: str, value: float) -> None:
        self.set_setting(command_name, byte_value=bytearray(struct.pack("f", value)))

    def set_setting_list(self, command_name: str, values: list) -> None:
        self.set_setting(command_name, byte_value=bytes(values))

    # Get a setting value from a device
    def get_setting(self, command_name: str) -> bytes:
        return self._handle_command(command_name, MOZA_COMMAND_READ)

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
