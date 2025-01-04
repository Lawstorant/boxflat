# Copyright (c) 2024, Tomasz Pakuła Using Arch BTW

from threading import Thread
from multiprocessing import Process, Queue, Event
from multiprocessing.queues import Empty
from serial import Serial, SerialException
from .subscription import SimpleEventDispatcher
from time import sleep


class SerialDevice(SimpleEventDispatcher):
    def __init__(self, serial_path: str, device_name: str, baud_rate: int=11520):
        super().__init__()
        self._read_queue = Queue()
        self._text_read_queue = Queue()
        self._write_queue = Queue()

        self._serial_available = Event()
        self._shutdown = Event()

        self._serial_path = serial_path
        self._device_name = device_name
        self._serial = None
        self._baud_rate = 11520

        Thread(target=self._notification_handler, daemon=True).start()
        Process(target=self._thread_spawner, daemon=True).start()


    def stop(self):
        self._serial_available.clear()
        self._shutdown.set()


    def write_bytes(self, message: bytes):
        if message is None:
            return
        self._write_queue.put(message)


    def _notification_handler(self):
        while not self._shutdown.is_set():
            try:
                response = self._read_queue.get(timeout=0.3)
            except:
                continue
            self._dispatch(response)


    def _serial_loader(self) -> None:
        self._serial_available.clear()
        self._serial = None

        while self._serial is None and not self._shutdown.is_set():
            try:
                self._serial = Serial(self._serial_path, baudrate=self._baud_rate, exclusive=False, timeout=0.5)
                # print(f"Serial connection established for {self._device_name}")
            except:
                self._serial = None
                sleep(0.2)

        self._serial_available.set()


    def _thread_spawner(self) -> None:
        self._serial_loader()

        print(f"\"{self._device_name}\" connected")
        self._serial.reset_output_buffer()
        self._serial.reset_input_buffer()

        p1 = Thread(target=self._serial_read_handler, daemon=True, name="serial-read")
        p2 = Thread(target=self._serial_write_handler, daemon=True, name="serial-write")

        p1.start()
        p2.start()

        p1.join()
        p2.join()

        try:
            self._serial.close()
        except:
            pass
        print(f"\"{self._device_name}\" disconnected")


    def _serial_read_handler(self):
        while not self._shutdown.is_set():
            if not self._serial_available.wait(timeout=0.1):
                continue

            try:
                self._read_queue.put(self._serial.read(1))

            except:
                pass


    def _serial_write_handler(self):
        data = None
        while not self._shutdown.is_set():
            try:
                data = self._write_queue.get(timeout=0.3)
            except Empty:
                continue

            # print(f"{self._device_name} writing: {data.hex(":")}")
            try:
                self._serial.write(data)
            except:
                self._serial_loader()
