# Copyright (c) 2025, Tomasz Pakuła Using Arch BTW

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
import re

CM_RETRY_COUNT=1

HidDeviceMapping = {
    "base"       : MozaHidDevice.BASE,
    "handbrake"  : MozaHidDevice.HANDBRAKE,
    "hpattern"   : MozaHidDevice.HPATTERN,
    "sequential" : MozaHidDevice.SEQUENTIAL,
    "pedals"     : MozaHidDevice.PEDALS,
    "hub"        : MozaHidDevice.HUB,
    "stalks"     : MozaHidDevice.STALKS,
}

SerialDeviceMapping = {
    MozaHidDevice.BASE       : "base",
    MozaHidDevice.HANDBRAKE  : "handbrake",
    MozaHidDevice.HPATTERN   : "hpattern",
    MozaHidDevice.SEQUENTIAL : "sequential",
    MozaHidDevice.PEDALS     : "pedals",
    MozaHidDevice.HUB        : "hub",
    "gudsen_e-stop"          : "estop",
    MozaHidDevice.STALKS     : "stalks",
    "moza_.*_digital_dash"   : "dash",
}


class MozaSerialDevice():
    name: str
    path: str
    serial_handler: SerialHandler

    def __init__(self, name="", path="", handler=None):
        self.name = name
        self.path = path
        self.serial_handler = handler



class MozaConnectionManager(EventDispatcher):
    def __init__(self, serial_data_path: str, dry_run=False):
        super().__init__()

        self._serial_data = None
        self._dry_run = dry_run
        self._shutdown = Event()

        self._serial_devices: dict[str, MozaSerialDevice] = {}
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

        self._device_ids: dict[str, int] = self._serial_data["device-ids"]

        # register events
        self._command_list: list[str] = []
        self._polling_list: list[str] = []
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
        self._register_events("device-disconnected", "hid-device-disconnected")

        self._serial_lock = Lock()
        self._refresh_cont = Event()

        self._connected_subscriptions: dict[str, SubscriptionList] = {}
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
        if not os.path.exists(self._serial_path):
            # print("No devices found!")
            self._handle_devices({})
            return

        devices = []
        for device in os.listdir(self._serial_path):
            if device.lower().find("gudsen"):
                devices.append(os.path.join(self._serial_path, device))

        serial_devices: dict[str, MozaSerialDevice] = {}
        for path in devices:
            for part, name in SerialDeviceMapping.items():
                part = part.replace(" ", "_")
                if not re.search(part, path.lower()):
                    continue

                serial_devices[name] = MozaSerialDevice(name, path)
                # print(f"\"{name}\" found".title())

        self._handle_devices(serial_devices)
        # print("Device discovery end\n")


    def _handle_devices(self, new_devices: dict):
        old_devices = None
        with self._devices_lock:
            old_devices = self._serial_devices

        for name in new_devices:
            if name in old_devices:
                new_devices[name].serial_handler = old_devices[name].serial_handler
                continue

            new_devices[name].serial_handler = SerialHandler(
                new_devices[name].path,
                self._message_start, name)

            new_devices[name].serial_handler.subscribe(self._receive_data, name)
            self._dispatch("device-connected", name)
            if name in HidDeviceMapping:
                self._dispatch("hid-device-connected", HidDeviceMapping[name])

        for name, device in old_devices.items():
            if name in new_devices:
                continue

            device.serial_handler.stop()
            self._dispatch("device-disconnected", name)
            if name in HidDeviceMapping:
                self._dispatch("hid-device-disconnected", HidDeviceMapping[name])


        with self._devices_lock:
            self._serial_devices = new_devices

        if len(new_devices) == 0 and self._refresh_cont.is_set():
            self.refresh_cont(False)

        elif len(new_devices) > 0 and not self._refresh_cont.is_set():
            self.refresh_cont(True)


    def subscribe_connected(self, command: str, callback, *args):
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
                if command.startswith("estop-receive"):
                    continue

                if self._event_sub_count(command) == 0:
                    continue
                # print("Polling data: " + command)
                self._get_setting(command)
                time.sleep(0.002)


    def _device_polling(self):
        time.sleep(1)
        while not self._shutdown.is_set():
            self.device_discovery()

            with self._connected_lock:
                lists = self._connected_subscriptions.copy()

            for command, subs in lists.items():
                value = self.get_setting(command)
                # value = 1
                if value is None:
                    value = -1
                subs.call(value)

            time.sleep(2)
        self._connected_thread = None


    def set_cont_active(self, active: bool):
        if active:
            self._cont_active.set()
        else:
            self._cont_active.clear()


    def set_write_active(self, *args):
        if not self._connected_thread:
            self._connected_thread = Thread(daemon=True, target=self._device_polling)
            self._connected_thread.start()


    def get_device_id(self, device_type: str) -> int:
        id = int(self._serial_data["device-ids"][device_type])
        if device_type != "base" and device_type in self._serial_devices:
            id = int(self._serial_data["device-ids"]["main"])
        return id


    def _get_device_handler(self, device_type: str) -> SerialHandler:
        device_handler = None
        with self._devices_lock:
            if device_type in self._serial_devices:
                device_handler = self._serial_devices[device_type].serial_handler

            elif "base" in self._serial_devices:
                # print(f"Redirect {device_type} to base")
                device_handler = self._serial_devices["base"].serial_handler

        return device_handler


    def _get_hub_handler(self) -> SerialHandler:
        if "hub" not in self._serial_devices:
            return
        # print(f"Redirect {device_type} to hub")
        return self._serial_devices["hub"].serial_handler


    def _receive_data(self, data: bytes, device_name: str):
        command, value = MozaCommand.value_from_response(
            data, device_name,
            self._serial_data["commands"],
            self._serial_data["ids-to-names"])

        if value is None or command is None:
            return

        # print(f"{command} received: {data.hex(":")}")
        self._dispatch(command, value)


    def _handle_command_v2(self, command_data: MozaCommand, rw: int) -> bytes:
        message = command_data.prepare_message(self._message_start, rw, self._magic_value)
        device_handler = self._get_device_handler(command_data.device_type)

        if device_handler is not None:
            device_handler.write_bytes(message)

        device_handler = self._get_hub_handler()
        if device_handler is not None:
            device_handler.write_bytes(message)


    def _handle_setting(self, value, command_name: str, device_name: str, rw: int) -> bool:
        command = MozaCommand()
        command.set_data_from_name(command_name, self._serial_data["commands"], device_name)
        command.device_id = self.get_device_id(command.device_type)

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
        self._handle_command_v2(command, rw)


    def _split_name(self, command_name: str):
        if command_name not in self._command_list:
            print(f"Command not found: {command_name}")
            return None, None

        device_name = command_name.split("-", maxsplit=1)[0]
        command_name = command_name.split("-", maxsplit=1)[1]
        return command_name, device_name


    def set_setting(self, value, command_name: str, exclusive=False):
        self._exclusive_access.wait()
        if exclusive:
            self._exclusive_access.clear()
            time.sleep(0.005)

        name, device = self._split_name(command_name)
        if name is None:
            return
        self._handle_setting(value, name, device, MOZA_COMMAND_WRITE)

        if exclusive:
            self._exclusive_access.set()

        # if self.get_setting(command_name) != value:
        #     self._handle_setting(value, name, device, MOZA_COMMAND_WRITE)


    def get_setting(self, command_name: str, exclusive=False):
        self._exclusive_access.wait()
        if exclusive:
            self._exclusive_access.clear()
            time.sleep(0.005)

        value = BlockingValue()

        self.subscribe_once(command_name, value.set_value)
        self._get_setting(command_name, exclusive)
        response = value.get_value_no_clear()

        if exclusive:
            time.sleep(0.01)
            self._exclusive_access.set()

        return response


    def _get_setting(self, command_name: str, exclusive=False):
        name, device = self._split_name(command_name)
        if name is None:
            return
        self._handle_setting(1, name, device, MOZA_COMMAND_READ)


    def cycle_wheel_id(self) -> int:
        with self._devices_lock:
            wid = self._serial_data["device-ids"]["wheel"] - 2

            if wid < self._serial_data["device-ids"]["base"]:
                wid = self._serial_data["device-ids"]["pedals"] - 2

            self._serial_data["device-ids"]["wheel"] = wid

            # print(f"Cycling wheel id. New id: {wid}")
            return wid


    def get_command_data(self) -> dict[str, dict]:
        return self._serial_data["commands"]
