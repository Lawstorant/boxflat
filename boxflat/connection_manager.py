import yaml
import os.path
from binascii import hexlify
from .moza_command import *
from serial import Serial
from threading import Thread
from threading import Lock
from threading import Event
import struct
import time
from .hid_handler import HidHandler, MozaHidDevice

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import GLib

CM_RETRY_COUNT=2

HidDeviceMapping = {
    "base" : MozaHidDevice.BASE,
    "handbrake" : MozaHidDevice.HANDBRAKE,
    "hpattern" : MozaHidDevice.HPATTERN,
    "sequential" : MozaHidDevice.SEQUENTIAL,
    "pedals" : MozaHidDevice.PEDALS,
    "hub" : MozaHidDevice.HUB,
    "estop" : MozaHidDevice.ESTOP,
    "main" : None
}

class MozaConnectionManager():
    def __init__(self, serial_data_path: str, hid_handler: HidHandler, dry_run=False):
        self._serial_data = None
        self._dry_run = dry_run
        self._shutdown = False

        self._hid_handler = hid_handler

        self._serial_devices = {}
        self._devices_lock = Lock()
        self._command_lock = Lock()

        with open(serial_data_path) as stream:
            try:
                self._serial_data = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
                self._shutdown = True
                quit(1)

        self._serial_lock = Lock()

        self._refresh = Event()
        self._refresh_cont = Event()
        self._subscribtions = {}
        self._refresh_thread = Thread(daemon=True, target=self._notify)
        self._refresh_thread.start()

        self._connected_subscribtions = {}
        self._connected_thread = Thread(daemon=True, target=self._notify_connected)
        self._connected_thread.start()

        self._cont_active = Event()
        self._cont_subscribtions = {}
        self._cont_thread = Thread(daemon=True, target=self._notify_cont)
        # self._cont_thread.start()

        self._shutown_subscribtions = []
        self._no_access_subs = []

        self._sub_lock = Lock()
        self._connected_lock = Lock()
        self._cont_lock = Lock()

        self._write_command_buffer = {}
        self._read_command_buffer = {}
        self._write_mutex = Lock()
        self._read_mutex = Lock()
        self._rw_thread = Thread(daemon=True, target=self._rw_handler)

        self._message_start= int(self._serial_data["message-start"])
        self._magic_value = int(self._serial_data["magic-value"])
        self._serial_path = "/dev/serial/by-id"

        self._set_type_method_mapping = {
            "int" : self.set_setting_int,
            "float" : self.set_setting_float,
            "array" : self.set_setting_list,
            "hex" : self.set_setting_hex
        }

        self._get_type_method_mapping = {
            "int" : self.get_setting_int,
            "float" : self.get_setting_float,
            "array" : self.get_setting_list,
            "hex" : self.get_setting_hex
        }


    def shutdown(self) -> None:
        self._shutdown = True
        for sub in self._shutown_subscribtions:
            sub[0](*sub[1])


    def device_discovery(self, *args) -> None:
        # print("\nDevice discovery...")
        path = self._serial_path

        if not os.path.exists(path):
            print("No devices found!")
            self._handle_devices({})
            return

        devices = []
        for device in os.listdir(path):
            if device.find("Gudsen_MOZA"):
                devices.append(os.path.join(path, device))

        serial_devices = {}
        for device in devices:
            if device.lower().find("base") != -1:
                serial_devices["base"] = device
                serial_devices["main"] = device
                # print("Base found")

            elif device.lower().find("hbp") != -1:
                serial_devices["handbrake"] = device
                # print("Handbrake found")

            elif device.lower().find("hgp") != -1:
                serial_devices["hpattern"] = device
                # print("H-Pattern shifter found")

            elif device.lower().find("sgp") != -1:
                serial_devices["sequential"] = device
                # print("Sequential shifter found")

            elif device.lower().find("pedals") != -1:
                serial_devices["pedals"] = device
                # print("Pedals found")

            # TODO: Check this info somehow
            elif device.lower().find("hub") != -1:
                serial_devices["hub"] = device
                # print("Hub found")

            elif device.lower().find("stop") != -1:
                serial_devices["estop"] = device
                # print("E-Stop found")

        self._handle_devices(serial_devices)

        # print("Device discovery end\n")


    def _handle_devices(self, new_devices: dict) -> None:
        old_devices = None

        with self._devices_lock:
            old_devices = self._serial_devices
            self._serial_devices = new_devices

        for device in new_devices:
            if device not in old_devices:
                self._hid_handler.add_device(HidDeviceMapping[device])



    def subscribe(self, command: str, callback: callable, *args) -> None:
        if not command in self._subscribtions:
            self._subscribtions[command] = []

        self._subscribtions[command].append((callback, args))


    def subscribe_connected(self, command: str, callback: callable, *args) -> None:
        if not command in self._connected_subscribtions:
            self._connected_subscribtions[command] = []

        self._connected_subscribtions[command].append((callback, args))


    def reset_subscriptions(self) -> None:
        # print("\nClearing subscriptions")
        with self._sub_lock:
            self._subscribtions.clear()

        with self._cont_lock:
            self._cont_subscribtions.clear()


    def subscribe_cont(self, command: str, callback: callable, *args) -> None:
        if not command in self._cont_subscribtions:
            self._cont_subscribtions[command] = []

        self._cont_subscribtions[command].append((callback, args))


    def subscribe_shutdown(self, callback, *args) -> None:
        self._shutown_subscribtions.append((callback, args))


    def subscribe_no_access(self, callback, *args) -> None:
        self._no_access_subs.append((callback, args))


    def refresh(self, *args) -> None:
        self._refresh.set()


    def refresh_cont(self, active: bool) -> None:
        if active:
            self._refresh_cont.set()
            self._refresh.set()
        else:
            self._refresh_cont.clear()
            self._refresh.clear()


    def _notify(self) -> None:
        response = 0
        while not self._shutdown:
            if not self._refresh.wait(2):
                continue

            if not self._refresh_cont.is_set():
                self._refresh.clear()

            with self._sub_lock:
                subs = dict(self._subscribtions)

            for com in subs.keys():
                com_type = self._serial_data["commands"][com]["type"]
                if com_type == "array":
                    response = self.get_setting_list(com)
                elif com_type == "float":
                    response = self.get_setting_float(com)
                elif com_type == "hex":
                    response = self.get_setting_hex(com)
                else:
                    response = self.get_setting_int(com)

                if response == -1:
                    continue

                for subscriber in subs[com]:
                    subscriber[0](response, *subscriber[1])

            if self._refresh_cont.is_set():
                time.sleep(1)


    def _notify_connected(self) -> None:
        response = 0
        while not self._shutdown:
            if not self._refresh.wait(2):
                continue

            self.device_discovery()

            with self._sub_lock:
                subs = dict(self._connected_subscribtions)

            for com in subs.keys():
                com_type = self._serial_data["commands"][com]["type"]
                if com_type == "array":
                    response = self.get_setting_list(com)
                elif com_type == "float":
                    response = self.get_setting_float(com)
                elif com_type == "hex":
                    response = self.get_setting_hex(com)
                else:
                    response = self.get_setting_int(com)

                self._no_access_subs = []

                for subscriber in subs[com]:
                    subscriber[0](response, *subscriber[1])

            if self._refresh_cont.is_set():
                time.sleep(1)


    def _notify_cont(self) -> None:
        while not self._shutdown:
            if not self._cont_active.wait(2):
                continue

            time.sleep(1/40) # 40 Hz refresh rate
            with self._cont_lock:
                subs = dict(self._cont_subscribtions)

            for com in subs.keys():
                response = self.get_setting_int(com)
                if response == -1:
                    break
                for subscriber in subs[com]:
                    GLib.idle_add(subscriber[0], response, *subscriber[1])


    def _notify_no_access(self) -> None:
        for i in range(len(self._no_access_subs)):
            subscriber = self._no_access_subs[i]
            GLib.idle_add(subscriber[0], *subscriber[1])
            self._no_access_subs.pop(i)


    def set_cont_active(self, active: bool) -> None:
        if active:
            self._cont_active.set()
        else:
            self._cont_active.clear()


    def set_rw_active(self, *args) -> None:
        if not self._rw_thread.is_alive():
            self._rw_thread.start()


    def _rw_handler(self) -> None:
        while not self._shutdown:
            time.sleep(0.1)

            with self._write_mutex:
                write_buffer = self._write_command_buffer
                self._write_command_buffer = {}

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

        with self._devices_lock:
            if device_type in self._serial_devices:
                device_path = self._serial_devices[device_type]

            elif device_type != "hub" and "base" in self._serial_devices:
                device_path = self._serial_devices["base"]

        return device_path


    def send_serial_message(self, serial_path: str, message: bytes, read_response=False) -> bytes:
        msg = ""
        for b in message:
            msg += f"{hex(b)} "
        # print(f"\nDevice: {serial_path}")
        # print(f"Sending:  {msg}")

        if self._dry_run:
            return bytes(1)

        if serial_path == None:
            # print("No compatible device found!")
            return None

        initial_len = message[1]
        rest = bytes()
        length = 0
        cmp = bytes([self._message_start])
        start = bytes(1)

        self._serial_lock.acquire()
        try:
            serial = Serial(serial_path, baudrate=115200, timeout=0.05)
            # time.sleep(1/500)
            serial.reset_output_buffer()
            serial.reset_input_buffer()
            for i in range(CM_RETRY_COUNT):
                serial.write(message)

            time.sleep(1/500)

            # read_response = True # For teesting writes
            start_time = time.time()
            while read_response:
                if time.time() - start_time > 0.04:
                    read_response = False
                    message = None
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
        except Exception as error:
            print("Error opening device!")
            read_response = False
            self._notify_no_access()

        self._serial_lock.release()

        if read_response == False:
            return message

        message = bytearray()
        message.extend(cmp)
        message.append(length)
        message.extend(rest)

        msg = ""
        for b in message:
            msg += f"{hex(b)} "
        # print(f"Response: {msg}")

        return message


    # Handle command operations
    def _handle_command(self, command_name: str, rw, value: int=1, byte_value: bytes=None) -> bytes:
        if not command_name in self._serial_data["commands"]:
            return bytes(1)
        command = MozaCommand(command_name, self._serial_data["commands"])

        if command.length == -1 or command.id == -1:
            print("Command undiscovered")
            return bytes(1)

        if rw == MOZA_COMMAND_READ and command.read_group == -1:
            print("Command doesn't support READ access")
            return bytes(1)

        if rw == MOZA_COMMAND_WRITE and command.write_group == -1:
            print("Command doesn't support WRITE access")
            return None

        if byte_value != None:
            command.set_payload_bytes(byte_value)
        else:
            command.payload = value

        device_id = self._get_device_id(command.device_type)
        if device_id == -1:
            print("Device ID undiscovered yet")
            return bytes(1)

        device_path = self._get_device_path(command.device_type)
        message = command.prepare_message(self._message_start, device_id, rw, self._calculate_checksum)

        # WE get a response without the checksum
        read = (rw == MOZA_COMMAND_READ)
        initial_len = command.payload_length
        response = self.send_serial_message(device_path, message, read)

        if response == None:
            return None

        # if len(response) != len(message):
        #     return None

        # check if length is 2 or lower because we need the
        # device id in the response, not just the value
        # length = response[1]
        # if length <= command.length+1:
        #     return bytes(1)
        length = command.payload_length
        return response[-1-length:-1]


    # Set a setting value on a device
    # If value should be float, provide bytes
    def _set_setting(self, command_name: str, value: int=0, byte_value=None) -> None:
        with self._write_mutex:
            # TODO: use Queue here instead of my custom implementation
            self._write_command_buffer[command_name] = (value, byte_value)


    def set_setting_int(self, value: int, command_name: str) -> None:
        self._set_setting(command_name, value)


    def set_setting_float(self, value: float, command_name: str) -> None:
        self._set_setting(command_name, byte_value=struct.pack(">f", float(value)))


    def set_setting_list(self, values: list, command_name: str) -> None:
        self._set_setting(command_name, byte_value=bytes(values))


    def set_setting_hex(self, value: str, command_name: str) -> None:
        self._set_setting(command_name, byte_value=bytes.fromhex(value))


    def set_setting_auto(self, value, command_name: str) -> bool:
        if command_name not in self._serial_data["commands"]:
            return False

        value_type = self._serial_data["commands"][command_name]["type"]
        self._set_type_method_mapping[value_type](value, command_name)
        return True


    # Get a setting value from a device
    def _get_setting(self, command_name: str) -> bytes:
        return self._handle_command(command_name, MOZA_COMMAND_READ)


    def get_setting_int(self, command_name: str) -> int:
        response = self._get_setting(command_name)
        if response == None:
            return -1
        return int.from_bytes(response)


    def get_setting_list(self, command_name: str) -> list:
        response = self._get_setting(command_name)
        if response == None:
            return -1
        return list(response)


    def get_setting_float(self, command_name: str) -> float:
        response = self._get_setting(command_name)
        if response == None:
            return -1
        return struct.unpack(">f", response)[0]


    def get_setting_hex(self, command_name: str) -> str:
        response = self._get_setting(command_name)
        if response == None:
            return -1
        return hexlify(response).decode("utf-8")


    def get_setting_auto(self, command_name: str):
        if command_name not in self._serial_data["commands"]:
            return

        value_type = self._serial_data["commands"][command_name]["type"]
        return self._get_type_method_mapping[value_type](command_name)


    def cycle_wheel_id(self) -> int:
        with self._devices_lock:
            wid = self._serial_data["device-ids"]["wheel"] - 1

            if wid == self._serial_data["device-ids"]["base"]:
                wid = self._serial_data["device-ids"]["pedals"] - 1

            self._serial_data["device-ids"]["wheel"] = wid

        # print(f"Cycling wheel id. New id: {wid}")
        return wid


    def get_command_data(self) -> dict:
        return self._serial_data["commands"]


# TODO: Move value conversion to MozaCommand
# TODO: Get rid of helper methods for setting/getting settings.
# TODO: Simplify command handler
# TODO: Rewrite manager so it keeps a read and write connection open constantly.
