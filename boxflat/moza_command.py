class MozaCommand():
    def __init__(self, name:str, commands_data: object):
        self.id = int(commands_data[name]["id"])
        self.read_group = int(commands_data[name]["read"])
        self.write_group = int(commands_data[name]["write"])
        self.length = int(commands_data[name]["bytes"])
        self._payload = bytes(self.length)

    @property
    def payload() -> bytes:
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

    def set_payload_bytes(self, value: bytes) -> None:
        self._payload = value

    def prepare_message(self, start_value: int,
                        device_id: int, rw: str,
                        check_function: callable) -> bytes:

        ret = bytearray()
        ret.append(start_value)
        ret.append(self.length + 1)

        if rw == "r":
            ret.extend(self.read_group_byte)
        elif rw == "w":
            ret.extend(self.write_group_byte)

        ret.append(device_id)
        ret.extend(self.id_byte)
        ret.extend(self._payload)
        ret.append(check_function(ret))

        return bytes(ret)
