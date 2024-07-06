import yaml

MESSAGE_START=""
MAGIC_VALUE=0
RETRY_COUNT=3
SERIAL_VALUES = {}

with open("serial.yml") as stream:
    try:
        SERIAL_VALUES = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)
        quit(1)

    MAGIC_VALUE = int(SERIAL_VALUES["magic-value"])
    MESSAGE_START = int("0x" + SERIAL_VALUES["message-start"], 0)


def calculate_security_sum(data: bytearray) -> int:
    value = MAGIC_VALUE
    for d in data:
        value += int(d)
    return value % 256


def prepare_serial_message(device_id:str, serial_data: bytearray) -> bytes:
    message = bytearray()
    message.append(MESSAGE_START)
    message.append(len(serial_data))
    message.append(int("0x" + device_id[:2], 0))
    message.append(int("0x" + device_id[2:], 0))
    message.extend(serial_data)
    message.append(calculate_security_sum(message))
    return bytes(message)


def send_serial_packet(device_id: str, serial_data: bytearray) -> None:
    message = prepare_serial_message(device_id, serial_data)
    print(f"Sending: {message}")
    for b in message:
        print(hex(b))

    # TODO: device search
    with open("/dev/ttyACM0", "wb") as tty:
        for i in range(0, RETRY_COUNT):
            tty.write(message)
        tty.close()


def set_setting(typ: str, name: str, value: int, device_id: str):
    length = int(SERIAL_VALUES[typ][name]["length"])
    setting_id = int(SERIAL_VALUES[typ][name]["id"])

    data = bytearray()
    data.append(setting_id)
    data.extend(value.to_bytes(length-1))

    send_serial_packet(device_id, data)


# helper functions
def set_base_setting(name: str, value: int) -> None:
    id = SERIAL_VALUES["bases"]["r9v2"]
    set_setting("base", name, value, id)

def set_wheel_setting(name: str, value: int) -> None:
    id = SERIAL_VALUES["wheels"]["rsv2"]
    set_setting("wheel", name, value, id)

def set_pedals_setting(name: str, value: int) -> None:
    set_setting("pedals", name, value)

def set_h_pattern_setting(name: str, value: int) -> None:
    set_setting("pedals", name, value)

def set_sequential_setting(name: str, value: int) -> None:
    id = SERIAL_VALUES["accessories"]["sequential"]
    set_setting("sequential", name, value, id)

def set_handbrake_setting(name: str, value: int) -> None:
    set_setting("handbrake", name, value)

def set_hub_setting(name: str, value: int) -> None:
    set_setting("hub", name, value)
