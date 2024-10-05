import yaml
import os.path
from .moza_command import *
from serial import Serial
from threading import Thread, Lock, Event
import time
from .hid_handler import MozaHidDevice
from .subscription import SubscriptionList, EventDispatcher, BlockingValue
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


class MozaSerialDevice():
    def __init__(self):
        self.name = ""
        self.path = ""
        self.serial_handler = None



class MozaConnectionManager(EventDispatcher):
    def __init__(self, serial_data_path: str, dry_run=False):
        super().__init__()

        self._serial_data = None
        self._dry_run = dry_run
        self._shutdown = Event()

        self._serial_devices = {}
        self._devices_lock = Lock()
        self._exclusive_access = Event()
        self._exclusive_access.set()

        with open(serial_data_path) as stream:
            try:
                self._serial_data = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
                self._shutdown.set()
                quit(1)

        self._device_ids = self._serial_data["device-ids"]

        # register events
        self._command_list = []
        self._polling_list = []
        for device in self._serial_data["commands"]:
            if self._device_ids[device] == -1:
                continue

            for command, data in self._serial_data["commands"][device].items():
                event_name = f"{device}-{command}"
                self._command_list.append(event_name)

                if data["read"] == -1:
                    continue

                self._polling_list.append(event_name)

        self._register_events(*self._polling_list)
        self._register_events("device-connected", "hid-device-connected")
        self._register_events("shutdown", "no-access")

        self._serial_lock = Lock()
        self._refresh_cont = Event()

        self._connected_subscriptions = {}
        self._connected_thread = None
        self._connected_lock = Lock()

        self._message_start= int(self._serial_data["message-start"])
        self._magic_value = int(self._serial_data["magic-value"])
        self._serial_path = "/dev/serial/by-id"
        # self._serial_path = "/dev/pts"


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
                obj = MozaSerialDevice()
                obj.path = device
                obj.name = "base"
                serial_devices["base"] = obj
                # serial_devices["main"] = device
                # print("Base found")

            elif device.lower().find("hbp") != -1:
                obj = MozaSerialDevice()
                obj.path = device
                obj.name = "handbrake"
                serial_devices["handbrake"] = obj
                # print("Handbrake found")

            elif device.lower().find("hgp") != -1:
                obj = MozaSerialDevice()
                obj.path = device
                obj.name = "hpattern"
                serial_devices["hpattern"] = obj
                # print("H-Pattern shifter found")

            elif device.lower().find("sgp") != -1:
                obj = MozaSerialDevice()
                obj.path = device
                obj.name = "sequential"
                serial_devices["sequential"] = obj
                # print("Sequential shifter found")

            elif device.lower().find("pedals") != -1:
                obj = MozaSerialDevice()
                obj.path = device
                obj.name = "pedals"
                serial_devices["pedals"] = obj
                # print("Pedals found")

        self._handle_devices(serial_devices)
        # print("Device discovery end\n")


    def _handle_devices(self, new_devices: dict):
        old_devices = None
        with self._devices_lock:
            old_devices = self._serial_devices

        for device in new_devices:
            if device not in old_devices:
                new_devices[device].serial_handler = SerialHandler(
                    new_devices[device].path,
                    self._message_start, device)

                new_devices[device].serial_handler.subscribe(self._receive_data, device)
                self._dispatch("device-connected", device)
                self._dispatch("hid-device-connected", HidDeviceMapping[device])

            else:
                new_devices[device].serial_handler = old_devices[device].serial_handler

        with self._devices_lock:
            self._serial_devices = new_devices

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
            time.sleep(2)

            for command in self._polling_list:
                if self._event_sub_count(command) == 0:
                    continue
                # print("Polling data: " + command)
                self._get_setting(command)
                time.sleep(0.005)


    def _device_polling(self):
        time.sleep(1)
        while not self._shutdown.is_set():
            self.device_discovery()

            with self._connected_lock:
                lists = self._connected_subscriptions.copy()

            self._clear_event_subscriptions("no-access")
            for command, subs in lists.items():
                value = self.get_setting(command)
                # value = 1
                if value is None:
                    value = -1
                subs.call_with_value(value)

            time.sleep(2)
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
        if not self._connected_thread:
            self._connected_thread = Thread(daemon=True, target=self._device_polling)
            self._connected_thread.start()


    def _get_device_id(self, device_type: str) -> int:
        id = int(self._serial_data["device-ids"][device_type])
        if device_type != "base" and device_type in self._serial_devices:
            id = int(self._serial_data["device-ids"]["main"])
        return id


    def _get_device_handler(self, device_type: str) -> SerialHandler:
        device_handler = None
        with self._devices_lock:
            if device_type in self._serial_devices:
                device_handler = self._serial_devices[device_type].serial_handler

            elif device_type != "hub" and "base" in self._serial_devices:
                device_handler = self._serial_devices["base"].serial_handler

        return device_handler


    def _receive_data(self, data: bytes, device_name: str):
        # print(f"Received: {data.hex(":")}")
        command, value = MozaCommand.value_from_response(
            data, device_name,
            self._serial_data["commands"],
            self._serial_data["ids-to-names"])

        if value is None or command is None:
            return

        self._dispatch(command, value)


    def _handle_command_v2(self, command_data: MozaCommand, rw: int) -> bytes:
        message = command_data.prepare_message(self._message_start, rw, self._magic_value)
        device_handler = self._get_device_handler(command_data.device_type)

        if device_handler is None:
            return

        device_handler.write_bytes(message)


    def _handle_setting(self, value, command_name: str, device_name: str, rw: int, exclusive=False) -> bool:
        command = MozaCommand()
        command.set_data_from_name(command_name, self._serial_data["commands"], device_name)
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

        self._exclusive_access.wait()
        if exclusive:
            self._exclusive_access.clear()
            time.sleep(0.005)

        self._handle_command_v2(command, rw)

        if exclusive:
            time.sleep(0.01)
            self._exclusive_access.set()


    def _split_name(self, command_name: str):
        if command_name not in self._command_list:
            print(f"Command not found: {command_name}")
            return None, None

        device_name = command_name.split("-", maxsplit=1)[0]
        command_name = command_name.split("-", maxsplit=1)[1]
        return command_name, device_name


    def set_setting(self, value, command_name: str, exclusive=False):
        name, device = self._split_name(command_name)
        if name is None:
            return
        self._handle_setting(value, name, device, MOZA_COMMAND_WRITE, exclusive)

        # if self.get_setting(command_name) != value:
        #     self._handle_setting(value, name, device, MOZA_COMMAND_WRITE)


    def get_setting(self, command_name: str, exclusive=False):
        value = BlockingValue()

        sub = self.subscribe_once(command_name, value.set_value)
        self._get_setting(command_name, exclusive)

        return value.get_value_no_clear()


    def _get_setting(self, command_name: str, exclusive=False):
        name, device = self._split_name(command_name)
        if name is None:
            return
        self._handle_setting(1, name, device, MOZA_COMMAND_READ, exclusive)


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
