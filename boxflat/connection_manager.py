import yaml
import os.path
from binascii import hexlify
from .moza_command import *
from serial import Serial
from threading import Thread, Lock, Event
import time
from .hid_handler import MozaHidDevice
from .subscription import SubscriptionList, EventDispatcher
from queue import SimpleQueue

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import GLib

CM_RETRY_COUNT=2

HidDeviceMapping = {
    "base"       : MozaHidDevice.BASE,
    "handbrake"  : MozaHidDevice.HANDBRAKE,
    "hpattern"   : MozaHidDevice.HPATTERN,
    "sequential" : MozaHidDevice.SEQUENTIAL,
    "pedals"     : MozaHidDevice.PEDALS,
    "hub"        : MozaHidDevice.HUB,
    "estop"      : MozaHidDevice.ESTOP,
    "main"       : None
}



class MozaQueueElement():
    def __init__(self, value=None, command=None):
        self.value = value
        self.command = command



class MozaConnectionManager(EventDispatcher):
    def __init__(self, serial_data_path: str, dry_run=False):
        super().__init__()
        self._register_event("device-connected")
        self._register_event("hid-device-connected")

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

        self._command_list = list(self._serial_data["commands"].keys())
        self._register_events(*self._command_list)

        self._serial_lock = Lock()

        self._refresh_cont = Event()
        self._subscriptions = []

        self._connected_subscriptions = {}
        self._connected_thread = Thread(daemon=True, target=self._notify_connected)
        self._connected_thread.start()

        self._shutown_subs = SubscriptionList()
        self._no_access_subs = SubscriptionList()

        self._sub_lock = Lock()
        self._connected_lock = Lock()

        self._write_queue = SimpleQueue()
        self._write_thread = None

        self._message_start= int(self._serial_data["message-start"])
        self._magic_value = int(self._serial_data["magic-value"])
        self._serial_path = "/dev/serial/by-id"


    def shutdown(self, *rest):
        self._shutown_subs.call_without_args()
        self._shutdown = True


    def device_discovery(self, *args):
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


    def _handle_devices(self, new_devices: dict):
        old_devices = None
        with self._devices_lock:
            old_devices = self._serial_devices
            self._serial_devices = new_devices

        for device in new_devices:
            if device not in old_devices:
                self._dispatch("device-connected", device)
                self._dispatch("hid-device-connected", HidDeviceMapping[device])

        if len(new_devices) == 0 and self._refresh_cont.is_set():
            self.refresh_cont(False)

        elif len(new_devices) > 0 and not self._refresh_cont.is_set():
            self.refresh_cont(True)


    def subscribe(self, event_name: str, callback: callable, *args):
        super().subscribe(event_name, callback, *args)
        if event_name in self._command_list:
            self._subscriptions.append(event_name)


    def subscribe_connected(self, command: str, callback: callable, *args):
        if not command in self._connected_subscriptions:
            self._connected_subscriptions[command] = SubscriptionList()

        self._connected_subscriptions[command].append(callback, *args)


    def reset_subscriptions(self):
        # print("\nClearing subscriptions")
        self._clear_subscriptions(self._command_list)
        with self._sub_lock:
            self._subscriptions.clear()


    def subscribe_shutdown(self, callback, *args):
        self._shutown_subs.append(callback, *args)


    def subscribe_no_access(self, callback: callable, *args):
        self._no_access_subs.append(callback, *args)


    def refresh_cont(self, active: bool):
        if active:
            self._refresh_cont.set()
            Thread(daemon=True, target=self._notify).start()
        else:
            self._refresh_cont.clear()


    def _notify(self):
        while self._refresh_cont.is_set():
            with self._sub_lock:
                subs = self._subscriptions.copy()

            for command in subs:
                response = self.get_setting(command)

                if response == -1:
                    continue

                self._dispatch(command, response)
            time.sleep(1)


    def _notify_connected(self):
        response = 0
        while not self._shutdown:
            time.sleep(1)
            self.device_discovery()

            with self._connected_lock:
                lists = self._connected_subscriptions.copy()

            self._no_access_subs.clear()
            for command, subs in lists.items():
                subs.call_with_value(self.get_setting(command))


    def _notify_no_access(self):
        if self._no_access_subs:
            self._no_access_subs.call()
            self._no_access_subs.clear()


    def set_cont_active(self, active: bool):
        if active:
            self._cont_active.set()
        else:
            self._cont_active.clear()


    def set_write_active(self, *args):
        if not self._write_thread:
            self._write_thread = Thread(daemon=True, target=self._write_handler)
            self._write_thread.start()


    def _write_handler(self):
        while not self._shutdown:
            element = self._write_queue.get()
            self.handle_setting(element.value, element.command, True)
        self._write_thread = None


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
            return

        if serial_path == None:
            # print("No compatible device found!")
            return

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

            #time.sleep(1/500)

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
            # print("Error opening device!")
            read_response = False
            self._notify_no_access()

        self._serial_lock.release()

        if read_response == False:
            return

        message = bytearray()
        message.extend(cmp)
        message.append(length)
        message.extend(rest)

        # msg = ""
        # for b in message:
        #     msg += f"{hex(b)} "
        # print(f"Response: {msg}")

        return bytes(message)


    def _handle_command_v2(self, command_data: MozaCommand, rw: int) -> bytes:
        message = command_data.prepare_message(self._message_start, rw, self._magic_value)
        device_path = self._get_device_path(command_data.device_type)

        response = self.send_serial_message(device_path, message, (rw == MOZA_COMMAND_READ))
        if not response is None:
            response = response[-1-command_data.payload_length:-1]

        # only return payload
        return response


    def handle_setting(self, value, command_name: str, rw: int) -> bool:
        if command_name not in self._command_list:
            print("Command not found!")
            return

        command = MozaCommand(command_name, self._serial_data["commands"])
        command.device_id = self._get_device_id(command.device_type)

        if command.device_id == -1:
            print("Invalid Device ID")
            return

        if rw == MOZA_COMMAND_WRITE and command.write_group == -1:
            print("Command doesn't support WRITE operation")
            return

        elif rw == MOZA_COMMAND_READ and command.read_group == -1:
            print("Command doesn't support READ operation")
            return

        command.set_payload(value)
        response = self._handle_command_v2(command, rw)
        if response == None:
            return

        command.set_payload_bytes(response)
        return command.get_payload()


    def set_setting(self, value, command_name: str):
        self._write_queue.put(MozaQueueElement(value, command_name))


    def get_setting(self, command_name: str):
        response = self.handle_setting(1, command_name, MOZA_COMMAND_READ)
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
