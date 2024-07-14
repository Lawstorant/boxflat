MOZA_COMMAND_READ=0
MOZA_COMMAND_WRITE=1

class MozaCommand():
    def __init__(self, name:str, commands_data: object):
        self.id = int(commands_data[name]["id"])
        self.read_group = int(commands_data[name]["read"])
        self.write_group = int(commands_data[name]["write"])
        self.length = int(commands_data[name]["bytes"])
        self._payload = bytes(self.length)
        self._device_type = name.split("-")[0]
        self._type = commands_data[name]["type"]

    @property
    def payload(self) -> bytes:
        return self._payload

    @payload.setter
    def payload(self, value: int) -> None:
        self._payload = value.to_bytes(self.length)

    @property
    def id_byte(self) -> bytes:
        return self.id.to_bytes(1)

    @property
    def read_group_byte(self) -> bytes:
        return self.read_group.to_bytes(1)

    @property
    def write_group_byte(self) -> bytes:
        return self.write_group.to_bytes(1)

    @property
    def length_byte(self) -> bytes:
        return self.length.to_bytes(1)

    @property
    def device_type(self) -> str:
        return self._device_type

    def set_payload_bytes(self, value: bytes) -> None:
        self._payload = value

    def prepare_message(self, start_value: int,
                        device_id: int, rw: int,
                        check_function: callable=None) -> bytes:

        ret = bytearray()
        ret.append(start_value)
        ret.append(self.length + 1)

        if rw == MOZA_COMMAND_READ:
            ret.extend(self.read_group_byte)
        elif rw == MOZA_COMMAND_WRITE:
            ret.extend(self.write_group_byte)

        ret.append(device_id)
        ret.extend(self.id_byte)
        ret.extend(self._payload)

        if check_function != None:
            ret.append(check_function(ret))

        return bytes(ret)
