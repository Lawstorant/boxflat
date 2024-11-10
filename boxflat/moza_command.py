# Copyright (c) 2024, Tomasz Pakuła Using Arch BTW

from sys import byteorder
from binascii import hexlify
from struct import pack, unpack
import boxflat.bitwise as bitwise

MOZA_COMMAND_READ=0
MOZA_COMMAND_WRITE=1
MOZA_COMMAND_DEAD=2

class MozaCommand():
    def __init__(self):
        self.id = 0
        self.read_group = 0
        self.write_group = 0
        self._length = 0
        self._payload = None
        self._name = None
        self._type = None
        self._device_id = None


    def set_data_from_name(self, name: str, commands_data: dict, device_name: str):
        self._device_type = device_name
        commands = commands_data[self._device_type]

        self.id = list(commands[name]["id"])
        self.read_group = int(commands[name]["read"])
        self.write_group = int(commands[name]["write"])

        self._length = int(commands[name]["bytes"])
        self._payload = bytes(self._length)

        self.name = name
        self._type = commands[name]["type"]
        self._device_id = None


    @staticmethod
    def value_from_response(values: bytes, device_name: str, commands_data: dict, device_ids: dict) -> tuple[str]:
        ret = (None, None)
        if values is None:
            return ret

        group = values[0]
        group_byte = bytes([values[0]])
        device_id = values[1]
        payload = values[2:]
        payload_list = list(payload)

        group = bitwise.toggle_bit(group, 7)
        device_id = bitwise.swap_nibbles(device_id)

        if device_id not in device_ids:
            return ret

        if device_name == "base" or device_name == "hub":
            device_name = device_ids[device_id]

        # Some ES wheels report on main/base IDs for some reason.
        # TODO: rewrite the db file and index commands by their rw
        # group first. It's the only stable metric.
        if 63 <= group <= 66:
            device_name = "wheel"

        # Hub reports on main ID
        if group == 228:
            device_name = "hub"
            group = 100

        for name, values in commands_data[device_name].items():
            if group != values["read"]:
                continue

            id_len = len(values["id"])
            if payload_list[:id_len] != values["id"]:
                continue

            value = MozaCommand.value_from_data(payload[id_len:], values["type"])
            if name == "paddle-sync" and value == 0:
                device_name = "hpattern"

            ret = f"{device_name}-{name}", value

            break
        return ret


    @property
    def payload(self) -> bytes:
        return self.get_payload_bytes()

    @payload.setter
    def payload(self, value):
        self.set_payload(value)

    @property
    def id_bytes(self) -> bytes:
        return bytes(self.id)

    @property
    def length(self) -> int:
        return self._length + len(self.id)

    @property
    def payload_length(self) -> int:
        return self._length

    @property
    def read_group_byte(self) -> bytes:
        return self.read_group.to_bytes(1)

    @property
    def write_group_byte(self) -> bytes:
        return self.write_group.to_bytes(1)

    @property
    def length_byte(self) -> bytes:
        return self._length.to_bytes(1)

    @property
    def device_type(self) -> str:
        return self._device_type

    @property
    def type(self) -> str:
        return self._type


    @property
    def device_id(self) -> int:
        return self._device_id


    @device_id.setter
    def device_id(self, new_id: int):
        if isinstance(new_id, int):
            self._device_id = new_id


    def set_payload_bytes(self, value: bytes):
        self._payload = value


    def get_payload_bytes(self) -> bytes:
        return self._payload


    def set_payload(self, value):
        data = None
        try:
            if self._type == "int":
                data = int(value).to_bytes(self._length)

            elif self._type == "float":
                data = pack(">f", float(value))

            elif self._type == "array":
                if isinstance(value, list):
                    data = bytes(value)
                else:
                    data = bytes(self._length)

            elif self._type == "hex":
                data = bytes.fromhex(value)
        except:
            data = bytes(self._length)

        self._payload = data


    def get_payload(self):
        return self.value_from_data(self._payload, self._type)


    @staticmethod
    def value_from_data(data: bytes, value_type: str):
        if  value_type == "int":
            data = int.from_bytes(data)

        elif value_type  == "float":
            data = unpack(">f", data)[0]

        elif value_type  == "array":
            data = list(data)

        elif value_type  == "hex":
            data = hexlify(data).decode("utf-8")

        else:
            data = None

        return data


    def get_payload_length(self) -> int:
        return self._length


    def checksum(self, data: bytes, magic_value: int) -> int:
        value = magic_value
        for d in data:
            value += int(d)
        return value % 256


    def prepare_message(self, start_value: int,
                        rw: int, magic_value: int) -> bytes:

        ret = bytearray()
        ret.append(start_value)
        ret.append(self.length)

        if rw == MOZA_COMMAND_READ:
            ret.extend(self.read_group_byte)
        elif rw == MOZA_COMMAND_WRITE:
            ret.extend(self.write_group_byte)

        ret.append(self._device_id)
        ret.extend(self.id_bytes)
        ret.extend(self._payload)
        ret.append(self.checksum(ret, magic_value))

        return bytes(ret)
