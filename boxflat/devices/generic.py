from .types import DeviceType
from boxflat.components.serial import SerialDevice
from boxflat.components.hid.device import HidDevice

class BoxflatDevice():
    def __init__(self):
        self._hid: HidDevice = None
        self._serial: SerialDevice = None
        self._type = [DeviceType.GENERIC]
        self._name = "Generic Device"


    def get_type(self) -> list[int]:
        return self._type


    def _serial_write(self, data: bytes) -> None:
        if not self._serial:
            return

        self._serial.write_bytes(data)
