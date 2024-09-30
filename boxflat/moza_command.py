from sys import byteorder
from binascii import hexlify
from struct import pack, unpack

MOZA_COMMAND_READ=0
MOZA_COMMAND_WRITE=1

class MozaCommand():
    def __init__(self, name:str, commands_data: object):
        self.id = list(commands_data[name]["id"])
        self.read_group = int(commands_data[name]["read"])
        self.write_group = int(commands_data[name]["write"])

        self._length = int(commands_data[name]["bytes"])
        self._payload = bytes(self.length)

        self.name = name.split("-", maxsplit=1)[1]
        self._device_type = name.split("-")[0]
        self._type = commands_data[name]["type"]


    @property
    def payload(self) -> bytes:
        return self.get_payload_bytes()

    @payload.setter
    def payload(self, value) -> None:
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


    def set_payload_bytes(self, value: bytes) -> None:
        self._payload = value


    def get_payload_bytes(self) -> bytes:
        return self._payload


    def set_payload(self, value):
        data = None
        if self._type == "int":
            data = int(value).to_bytes(self._length)

        elif self._type == "float":
            data = pack(">f", float(value))

        elif self._type == "array":
            data = bytes(value)

        elif self._type == "hex":
            data = bytes.fromhex(value)

        self._payload = data


    def get_payload(self):
        data = self._payload
        if self._type == "int":
            data = int.from_bytes(data)

        elif self._type == "float":
            data = unpack(">f", data)[0]

        elif self._type == "array":
            data = list(data)

        elif self._type == "hex":
            data = hexlify(data).decode("utf-8")

        return data


    def get_payload_length(self) -> int:
        return self._length


    def _calculate_checksum(self, data: bytes, magic_value: int) -> int:
        value = magic_value
        for d in data:
            value += int(d)
        return value % 256


    def prepare_message(self, start_value: int,
                        device_id: int, rw: int, magic_value: int) -> bytes:

        ret = bytearray()
        ret.append(start_value)
        ret.append(self.length)

        if rw == MOZA_COMMAND_READ:
            ret.extend(self.read_group_byte)
        elif rw == MOZA_COMMAND_WRITE:
            ret.extend(self.write_group_byte)

        ret.append(device_id)
        ret.extend(self.id_bytes)
        ret.extend(self._payload)
        ret.append(self._calculate_checksum(ret, magic_value))

        return bytes(ret)
