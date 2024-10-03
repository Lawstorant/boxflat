import yaml
import os.path
from .moza_command import *
from serial import Serial
from threading import Thread, Lock, Event
import time
from .hid_handler import MozaHidDevice
from .subscription import SubscriptionList, EventDispatcher
from queue import SimpleQueue
from .serial_handler import SerialHandler

CM_RETRY_COUNT=1

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
    def __init__(self, value=None, command_name=None):
        self.value = value
        self.command_name = command_name



class MozaConnectionManager(EventDispatcher):
    def __init__(self, serial_data_path: str, dry_run=False):
        super().__init__()

        self._serial_data = None
        self._dry_run = dry_run
        self._shutdown = Event()

        self._serial_devices = {}
        self._devices_lock = Lock()

        with open(serial_data_path) as stream:
            try:
                self._serial_data = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
                self._shutdown.set()
                quit(1)

        self._device_ids = self._serial_data["device-ids"]

        # register events
        self._command_list = list(self._serial_data["commands"].keys())
        self._polling_list = []
        for command, data in self._serial_data["commands"].items():
            if self._device_ids[command.split("-")[0]] == -1:
                continue

            if data["read"] == -1:
                continue

            self._polling_list.append(command)

        self._register_events(*self._polling_list)
        self._register_events("device-connected", "hid-device-connected")
        self._register_events("shutdown", "no-access")


        self._serial_lock = Lock()
        self._refresh_cont = Event()

        self._connected_subscriptions = {}
        self._connected_thread = None
        self._connected_lock = Lock()

        self._write_queue = SimpleQueue()
        self._write_thread = None

        self._message_start= int(self._serial_data["message-start"])
        self._magic_value = int(self._serial_data["magic-value"])
        self._serial_path = "/dev/serial/by-id"


    def shutdown(self, *rest):
        self._dispatch("shutdown")
        self._shutdown.set()


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
                # serial_devices["main"] = device
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

        self._handle_devices(serial_devices)
        # print("Device discovery end\n")


    def _handle_devices(self, new_devices: dict):
        old_devices = None
        with self._devices_lock:
            old_devices = self._serial_devices
            self._serial_devices = new_devices

        for device, path in new_devices:
            if device not in old_devices:
                SerialHandler(path, self._message_start)
                self._dispatch("device-connected", device)
                self._dispatch("hid-device-connected", HidDeviceMapping[device])

        if len(new_devices) == 0 and self._refresh_cont.is_set():
            self.refresh_cont(False)

        elif len(new_devices) > 0 and not self._refresh_cont.is_set():
            self.refresh_cont(True)


    def subscribe_connected(self, command: str, callback: callable, *args):
        if not command in self._connected_subscriptions:
            self._connected_subscriptions[command] = SubscriptionList()
        self._connected_subscriptions[command].append(callback, *args)


    def refresh_cont(self, active: bool):
        if active:
            self._refresh_cont.set()
            Thread(daemon=True, target=self._polling_thread).start()
        else:
            self._refresh_cont.clear()


    def _polling_thread(self):
        while self._refresh_cont.is_set():
            time.sleep(0.5)

            for command in self._polling_list:
                if self._event_sub_count(command) == 0:
                    continue

                # print("Polling data: " + command)
                response = self.get_setting(command)
                if response is None:
                    continue

                self._dispatch(command, response)


    def _device_polling(self):
        while not self._shutdown.is_set():
            self.device_discovery()

            with self._connected_lock:
                lists = self._connected_subscriptions.copy()

            self._clear_event_subscriptions("no-access")
            for command, subs in lists.items():
                value = self.get_setting(command)
                if value is None:
                    value = -1
                subs.call_with_value(value)

            time.sleep(1)
        self._connected_thread = None


    def _notify_no_access(self):
        self._dispatch("no-access")
        self._clear_event_subscriptions("no-access")


    def set_cont_active(self, active: bool):
        if active:
            self._cont_active.set()
        else:
            self._cont_active.clear()


    def set_write_active(self, *args):
        if not self._write_thread:
            self._write_thread = Thread(daemon=True, target=self._write_handler)
            self._write_thread.start()

        if not self._connected_thread:
            self._connected_thread = Thread(daemon=True, target=self._device_polling)
            self._connected_thread.start()


    def _write_handler(self):
        while not self._shutdown.is_set():
            element = self._write_queue.get()
            self._handle_setting(element.value, element.command_name, True)
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
        # msg = message.hex(':')
        # print(f"Sending: {msg}")

        return

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
            serial = Serial(serial_path, baudrate=115200, timeout=0.01)
            time.sleep(1/500)
            serial.reset_output_buffer()
            serial.reset_input_buffer()
            for i in range(CM_RETRY_COUNT):
                serial.write(message)

            #time.sleep(1/500)

            # read_response = True # For teesting writes
            start_time = time.time()
            while read_response:
                if time.time() - start_time > 0.02:
                    # print("Time's up!")
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

        #print(time.time() - start_time)
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

        # msg = message.hex(':')
        # print(f"Response: {msg}\n")

        return bytes(message)


    def _handle_command_v2(self, command_data: MozaCommand, rw: int) -> bytes:
        message = command_data.prepare_message(self._message_start, rw, self._magic_value)
        device_path = self._get_device_path(command_data.device_type)

        response = self.send_serial_message(device_path, message, (rw == MOZA_COMMAND_READ))
        if response is not None:
            response = response[-1-command_data.payload_length:-1]

        # only return payload
        return response


    def _handle_setting(self, value, command_name: str, rw: int) -> bool:
        if command_name not in self._command_list:
            print("Command not found: " + command_name)
            return

        command = MozaCommand(command_name, self._serial_data["commands"])
        command.device_id = self._get_device_id(command.device_type)

        if command.device_id == -1:
            print("Invalid Device ID")
            return

        if rw == MOZA_COMMAND_WRITE and command.write_group == -1:
            print("Command doesn't support WRITE operation: " + command_name)
            return

        elif rw == MOZA_COMMAND_READ and command.read_group == -1:
            print("Command doesn't support READ operation: " + command_name)
            return

        command.set_payload(value)
        response = self._handle_command_v2(command, rw)
        if response is None:
            return

        return command.get_payload(alt_data=response)


    def set_setting(self, value, command_name: str):
        self._write_queue.put(MozaQueueElement(value, command_name))


    def get_setting(self, command_name: str):
        return self._handle_setting(1, command_name, MOZA_COMMAND_READ)


    def cycle_wheel_id(self) -> int:
        with self._devices_lock:
            wid = self._serial_data["device-ids"]["wheel"] - 1

            if wid == self._serial_data["device-ids"]["base"] + 1:
                wid = self._serial_data["device-ids"]["pedals"] - 2

            self._serial_data["device-ids"]["wheel"] = wid

        # print(f"Cycling wheel id. New id: {wid}")
        return wid


    def get_command_data(self) -> dict:
        return self._serial_data["commands"]


# TODO: Rewrite manager so it keeps a read and write connection open constantly.
