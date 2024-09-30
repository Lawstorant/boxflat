import yaml
import os.path
from binascii import hexlify
from .moza_command import *
from serial import Serial
from threading import Thread, Lock, Event
import time
from .hid_handler import HidHandler, MozaHidDevice
from .subscription import SubscriptionList

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
        self._subscriptions = {}
        self._refresh_thread = Thread(daemon=True, target=self._notify)
        self._refresh_thread.start()

        self._connected_subscriptions = {}
        self._connected_thread = Thread(daemon=True, target=self._notify_connected)
        self._connected_thread.start()

        self._shutown_subs = SubscriptionList()
        self._no_access_subs = SubscriptionList()

        self._sub_lock = Lock()
        self._connected_lock = Lock()

        self._write_command_buffer = {}
        self._read_command_buffer = {}
        self._write_mutex = Lock()
        self._read_mutex = Lock()
        self._rw_thread = Thread(daemon=True, target=self._rw_handler)

        self._message_start= int(self._serial_data["message-start"])
        self._magic_value = int(self._serial_data["magic-value"])
        self._serial_path = "/dev/serial/by-id"


    def shutdown(self) -> None:
        self._shutown_subs.call_without_args()
        self._shutdown = True


    def device_discovery(self, *args) -> None:
        # print("\nDevice discovery...")
        path = self._serial_path

        if not os.path.exists(path):
            # print("No devices found!")
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
        if not command in self._subscriptions:
            self._subscriptions[command] = SubscriptionList()

        self._subscriptions[command].append(callback, *args)


    def subscribe_connected(self, command: str, callback: callable, *args) -> None:
        if not command in self._connected_subscriptions:
            self._connected_subscriptions[command] = SubscriptionList()

        self._connected_subscriptions[command].append(callback, *args)


    def reset_subscriptions(self) -> None:
        # print("\nClearing subscriptions")
        with self._sub_lock:
            self._subscriptions.clear()


    def subscribe_shutdown(self, callback, *args) -> None:
        self._shutown_subs.append(callback, *args)


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
        while not self._shutdown:
            if not self._refresh.wait(2):
                continue

            if not self._refresh_cont.is_set():
                self._refresh.clear()

            with self._sub_lock:
                subs = self._subscriptions.copy()

            for command, subs in subs.items():
                response = self.get_setting_auto(command)

                if response == -1:
                    continue

                subs.call_with_value(response)

            if self._refresh_cont.is_set():
                time.sleep(1)


    def _notify_connected(self) -> None:
        response = 0
        while not self._shutdown:
            if not self._refresh.wait(2):
                continue

            self.device_discovery()

            with self._connected_lock:
                lists = self._connected_subscriptions.copy()

            self._no_access_subs = []
            for command, subs in lists.items():
                subs.call_with_value(self.get_setting_auto(command))

            if self._refresh_cont.is_set():
                time.sleep(1)


    def _notify_no_access(self) -> None:
        if self._no_access_subs:
            self._no_access_subs.call()
            self._no_access_subs = None


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

            for com, val in write_buffer.items():
                self.handle_setting(val, com, True)


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
        # msg = ""
        # for b in message:
        #     msg += f"{hex(b)} "
        # print(f"\nDevice: {serial_path}")
        # print(f"Sending:  {msg}")

        if self._dry_run:
            return bytes(1)

        if serial_path == None:
            # print("No compatible device found!")
            return bytes(1)

        initial_len = message[1]
        rest = bytes()
        length = 0
        cmp = bytes([self._message_start])
        start = bytes()

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
            return bytes(1)

        # message = bytearray()
        # message.extend(cmp)
        # message.append(length)
        # message.extend(rest)

        # msg = ""
        # for b in message:
        #     msg += f"{hex(b)} "
        # print(f"Response: {msg}")

        return rest


    def _handle_command_v2(self, command_data: MozaCommand, rw: int) -> bytes:
        device_id = self._get_device_id(command.device_type)
        message = command_data.prepare_message(self._message_start, device_id, rw)
        device_path = self._get_device_path(command.device_type)

        return self.send_serial_message(device_path, message, (rw == MOZA_COMMAND_READ))


    def handle_setting(self, value, command_name: str, write=True) -> bool:
        if command_name not in self._serial_data["commands"]:
            print("Command not found!")
            return

        command = MozaCommand(command_name, self._serial_data["commands"])

        if write and (command.write_group == -1):
            print("Command doesn't support WRITE operation")
            return

        elif command.read_group == -1:
            print("Command doesn't support READ operation")
            return

        command.set_payload(value)
        response = self._handle_command_v2(command, MOZA_COMMAND_WRITE if write else MOZA_COMMAND_READ)
        command.set_payload_bytes(response)
        return command.get_payload()


    def set_setting(self, value, command_name: str):
        with self._write_mutex:
            # TODO: use Queue here instead of my custom implementation
            self._write_command_buffer[command_name] = value


    def get_setting(self, value, command_name: str):
        response = self.handle_setting(value, command_name, write=False)
        if response == None:
            return -1
        return response


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


# TODO: Rewrite manager so it keeps a read and write connection open constantly.
