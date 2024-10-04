from threading import Thread
from multiprocessing import Process, SimpleQueue, Event
from serial import Serial
from boxflat.subscription import EventDispatcher
from time import sleep


class SerialHandler(EventDispatcher):
    def __init__(self, serial_path: str, msg_start: str):
        super().__init__()
        self._read_queue = SimpleQueue()
        self._write_queue = SimpleQueue()
        self._running = Event()

        self._serial_path = serial_path
        self._message_start = msg_start
        self._register_event("incoming-data")

        self._running.set()
        Thread(target=self._notification_handler, daemon=True).start()
        Process(target=self._thread_spawner, daemon=True).start()


    def stop(self):
        self._running.clear()


    def write_bytes(self, message: bytes):
        if message is None:
            return

        self._write_queue.put(message)


    def _notification_handler(self):
        while self._running.is_set():
            data = self._read_queue.get()
            print(f"\"{self._serial_path}\" incoming data: " + data.hex(":"))
            self._dispatch("incoming-data", data)


    def _thread_spawner(self):
        serial = Serial(self._serial_path, baudrate=115200, exclusive=False)
        print(f"\"{self._serial_path}\" Connected")
        serial.reset_output_buffer()
        serial.reset_input_buffer()

        p1 = Thread(target=self._serial_read_handler, args=[serial], daemon=True, name="serial-read")
        p2 = Thread(target=self._serial_write_handler, args=[serial], daemon=True, name="serial-write")

        p1.start()
        p2.start()

        p1.join()
        p2.join()
        serial.close()
        print(f"\"{self._serial_path}\" Disconnected")


    def _serial_read_handler(self, serial: Serial):
        start = bytes([self._message_start])

        try:
            while self._running.is_set():
                if serial.read(1) != start:
                    continue

                payload_length = int().from_bytes(serial.read(1))
                response_group = serial.read(1)
                device_id = serial.read(1)
                payload = serial.read(payload_length)

                response = bytearray()
                response.append(payload_length)
                response.extend(response_group)
                response.extend(device_id)
                response.extend(payload)

                self._read_queue.put(bytes(response))
        except Exception as error:
            pass


    def _serial_write_handler(self, serial: Serial):
        try:
            while self._running.is_set():
                serial.write(self._write_queue.get())
        except Exception as error:
            pass
