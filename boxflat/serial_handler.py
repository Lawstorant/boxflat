# Copyright (c) 2024, Tomasz Pakuła Using Arch BTW

from threading import Thread
from multiprocessing import Process, Queue, Event
from multiprocessing.queues import Empty
from serial import Serial, SerialException
from boxflat.subscription import SimpleEventDispatcher
from time import sleep

from boxflat.moza_command import MozaCommand


class SerialHandler(SimpleEventDispatcher):
    def __init__(self, serial_path: str, msg_start: str, device_name: str):
        super().__init__()
        self._read_queue = Queue()
        self._text_read_queue = Queue()
        self._write_queue = Queue()
        self._running = Event()

        self._serial_path = serial_path
        self._message_start = msg_start
        self._device_name = device_name

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
            try:
                response = self._read_queue.get(timeout=0.5)
            except:
                continue
            self._dispatch(response)


    def _thread_spawner(self):
        serial = Serial(self._serial_path, baudrate=115200, exclusive=False, timeout=0.5)
        print(f"\"{self._device_name}\" connected")
        serial.reset_output_buffer()
        serial.reset_input_buffer()

        p1 = Thread(target=self._serial_read_handler, args=[serial], daemon=True, name="serial-read")
        p2 = Thread(target=self._serial_write_handler, args=[serial], daemon=True, name="serial-write")

        p1.start()
        p2.start()

        p1.join()
        p2.join()
        serial.close()
        print(f"\"{self._device_name}\" disconnected")


    def _serial_read_handler(self, serial: Serial):
        start = bytes([self._message_start])

        while self._running.is_set():
            try:
                if serial.read(1) != start:
                    continue

                payload_length = int().from_bytes(serial.read(1))
                if not 2 <= payload_length <= 11:
                    continue

                self._read_queue.put(serial.read(payload_length + 2))

            except:
                self.stop()


    def _serial_write_handler(self, serial: Serial):
        data = None
        while self._running.is_set():
            try:
                data = self._write_queue.get(timeout=0.5)
            except Empty:
                continue

            # print(f"Writing: {data.hex(":")}")
            try:
                serial.write(data)
            except SerialException:
                self.stop()
