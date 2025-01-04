from boxflat.components.serial import SerialDevice

class MozaSerialDevice(SerialDevice):
    def __init__(self, serial_path: str, device_name: str):
        super().__init__()


    def _serial_read_handler(self):
        start = bytes([self._message_start])

        while not self._shutdown.is_set():
            if not self._serial_available.wait(timeout=0.1):
                continue

            try:
                if self._serial.read(1) != start:
                    continue

                payload_length = int().from_bytes(self._serial.read(1))
                if not 2 <= payload_length <= 11:
                    continue

                self._read_queue.put(self._serial.read(payload_length + 2))

            except:
                pass
