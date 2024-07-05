import sys
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


def prepare_serial_message(serial_data: str) -> str:
    message = MESSAGE_START
    message += tohex(byte_len(serial_data))
    message += SERIAL_VALUES["devices"]["r9"]
    message += serial_data
    message += calculate_security_sum(message)
    return message


def send_serial_packet(serial_data: str) -> None:
    message = prepare_serial_message(serial_data)
    print(f"Sending: {message}")

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


def set_rotation_limit(angle: int) -> None:
    length = SERIAL_VALUES["base"]["limit"]["length"]
    id = tohex(SERIAL_VALUES["base"]["limit"]["id"])

    data = tohex(int(angle/2), length-1)
    data = id + data

    send_serial_packet(data)


def set_rotatoion_angle(angle: int) -> None:
    length = SERIAL_VALUES["base"]["angle"]["length"]
    id = tohex(SERIAL_VALUES["base"]["angle"]["id"])

    data = tohex(int(angle/2), length-1)
    data = id + data

    send_serial_packet(data)
