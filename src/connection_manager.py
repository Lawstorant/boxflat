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

    MAGIC_VALUE = SERIAL_VALUES["magic-value"]
    MESSAGE_START = SERIAL_VALUES["message-start"]


def byte_len(data: str) -> int:
    return int(len(data)/4)


def calculate_security_sum(byte_str: str) -> str:
    value = MAGIC_VALUE
    for i in range (0, byte_len(byte_str)):
        start = 4*i+2
        end = 4*i+4
        value += int("0x" + byte_str[start:end], 0)

    return tohex(value % 256)


def prepare_serial_message(device_id:str, serial_data: str) -> str:
    message = MESSAGE_START
    message += tohex(byte_len(serial_data))
    message += device_id
    message += serial_data
    message += calculate_security_sum(message)
    return message


def send_serial_packet(device_id: str, serial_data: str) -> None:
    message = prepare_serial_message(device_id, serial_data)
    print(f"Sending: {message}")

    # TODO: device search
    # with open("/dev/ttyACM0") as tty:
    #     for i in range(0, RETRY_COUNT):
    #         tty.write(message)
    #     tty.close()

def tohex(value: int, length=1) -> str:
    string = hex(value)[2:]
    ret = ""

    while len(string) < length*2:
        string = "0" + string

    for i in range(0, length):
        ret += f"\\x{string[i*2:i*2+2]}"

    return ret

def set_setting(typ: str, name: str, value: int, device_id: str):
    length = SERIAL_VALUES[typ][name]["length"]
    id = tohex(SERIAL_VALUES[typ][name]["id"])

    data = tohex(value, length-1)
    data = id + data
    send_serial_packet(device_id, data)

# helper functions
def set_base_setting(name: str, value: int) -> None:
    set_setting("base", name, value)

def set_wheel_setting(name: str, value: int) -> None:
    id = SERIAL_VALUES["wheels"]["rsv2"]
    set_setting("wheel", name, value, id)

def set_pedals_setting(name: str, value: int) -> None:
    set_setting("pedals", name, value)

def set_h_pattern_setting(name: str, value: int) -> None:
    set_setting("pedals", name, value)

def set_sequential_setting(name: str, value: int) -> None:
    set_setting("sequential", name, value)

def set_handbrake_setting(name: str, value: int) -> None:
    set_setting("handbrake", name, value)

def set_hub_setting(name: str, value: int) -> None:
    set_setting("hub", name, value)
