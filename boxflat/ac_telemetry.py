# Copyright (c) 2025, Kevin Florczak Also Using Arch BTW

"""
Assetto Corsa telemetry reader that reads directly from shared memory.
Requires simshmbridge to be running to create the shared memory.
"""
import mmap
import os
import struct
import ctypes
from threading import Thread, Event
import time


class ACTelemetryReader:
    """Reads RPM data from Assetto Corsa shared memory."""

    def __init__(self, callback):
        """
        Initialize AC telemetry reader.

        Args:
            callback: Function to call with RPM value, will be called as callback(rpm)
        """
        self._callback = callback
        self._running = Event()
        self._thread = None
        self._fd = None
        self._mm = None
        self._static_fd = None
        self._static_mm = None
        self._max_rpm = 20000  # default, will be detected or read from static memory
        self._max_rpm_seen = 0  # Track the highest RPM we've actually seen

        # Assetto Corsa shared memory files
        self._AC_PHYSICS_FILE = "/acpmf_physics"
        self._AC_STATIC_FILE = "/acpmf_static"

    def start(self):
        """Start the telemetry reader thread."""
        if self._running.is_set():
            return

        self._running.set()
        self._thread = Thread(target=self._read_loop, daemon=True)
        self._thread.start()
        print("[AC Telemetry] Started reading from Assetto Corsa shared memory")

    def stop(self):
        """Stop the telemetry reader."""
        self._running.clear()
        self._cleanup()
        print("[AC Telemetry] Stopped")

    def _shm_open(self, name, flags):
        """Open shared memory object."""
        libc = ctypes.CDLL("libc.so.6")
        shm_open = libc.shm_open
        shm_open.restype = ctypes.c_int
        return shm_open(name.encode(), flags, 0)

    def _cleanup(self):
        """Clean up resources."""
        try:
            if self._mm:
                self._mm.close()
            if self._fd:
                os.close(self._fd)
            if self._static_mm:
                self._static_mm.close()
            if self._static_fd:
                os.close(self._static_fd)
        except:
            pass

        self._mm = None
        self._fd = None
        self._static_mm = None
        self._static_fd = None

    def _read_max_rpm(self):
        """Read max RPM from static shared memory."""
        try:
            # Open static memory if not already open
            if self._static_fd is None:
                self._static_fd = self._shm_open(self._AC_STATIC_FILE, os.O_RDONLY)
                size = os.fstat(self._static_fd).st_size
                self._static_mm = mmap.mmap(self._static_fd, size, access=mmap.ACCESS_READ)
                print(f"[AC Telemetry] Opened static shared memory, size: {size} bytes")

            size = os.fstat(self._static_fd).st_size

            # Try both offsets: 0x019C (your simshmbridge) and 0x01A8 (official docs)
            # Let's read a range around both to see what's there
            print(f"[AC Telemetry] Scanning for max RPM in static memory...")

            # Scan around 0x0190-0x01B0 to find plausible RPM values
            for offset in range(0x0190, min(0x01C0, size - 4), 4):
                self._static_mm.seek(offset)
                val_bytes = self._static_mm.read(4)
                if len(val_bytes) == 4:
                    # Try reading as int
                    val_i = struct.unpack('<i', val_bytes)[0]
                    # Try reading as float
                    val_f = struct.unpack('<f', val_bytes)[0]

                    if 5000 <= val_i <= 30000:
                        print(f"[AC Telemetry] Offset 0x{offset:04x}: int={val_i} float={val_f:.2f}")
                    elif 5000 <= val_f <= 30000:
                        print(f"[AC Telemetry] Offset 0x{offset:04x}: int={val_i} float={val_f:.2f} **")

            # Now read from 0x019C as you specified
            offset = 0x019C
            if offset + 4 <= size:
                self._static_mm.seek(offset)
                val_bytes = self._static_mm.read(4)
                if len(val_bytes) == 4:
                    val_i = struct.unpack('<i', val_bytes)[0]
                    val_f = struct.unpack('<f', val_bytes)[0]
                    print(f"[AC Telemetry] Offset 0x{offset:04x}: int={val_i} float={val_f:.2f}")

                    # Use float if it looks valid, otherwise try int
                    if 5000 <= val_f <= 30000:
                        old_max = self._max_rpm
                        self._max_rpm = int(val_f)
                        if old_max != self._max_rpm:
                            print(f"[AC Telemetry] Max RPM updated (as float): {old_max} -> {self._max_rpm}")
                        return True
                    elif 5000 <= val_i <= 30000:
                        old_max = self._max_rpm
                        self._max_rpm = val_i
                        if old_max != self._max_rpm:
                            print(f"[AC Telemetry] Max RPM updated (as int): {old_max} -> {self._max_rpm}")
                        return True

            print(f"[AC Telemetry] No valid max RPM found, using default: {self._max_rpm}")
            return False

        except Exception as e:
            print(f"[AC Telemetry] Could not read max RPM: {e}")
            return False

    def _read_loop(self):
        """Main reading loop."""
        self._connected = False
        _max_rpm_check_counter = 0  # Counter for periodic max RPM checks
        _loop_count = 0  # Track loop iterations for periodic logging

        print("[AC Telemetry] Read loop started, waiting for connection...")

        while self._running.is_set():
            try:
                # Try to connect if not connected
                if self._fd is None:
                    try:
                        self._fd = self._shm_open(self._AC_PHYSICS_FILE, os.O_RDONLY)
                        size = os.fstat(self._fd).st_size
                        self._mm = mmap.mmap(self._fd, size, access=mmap.ACCESS_READ)
                        print("[AC Telemetry] Connected to physics shared memory")

                        # Read max RPM on first connection
                        if self._static_fd is None:
                            self._read_max_rpm()

                        self._connected = True
                        _loop_count = 0

                    except Exception as e:
                        # AC not running, wait and retry
                        if _loop_count % 60 == 0:  # Log every ~1 second
                            print(f"[AC Telemetry] Waiting for AC... ({e})")
                        self._connected = False
                        time.sleep(1)
                        _loop_count += 1
                        continue

                # Read RPM from physics data (offset 0x14 = 20)
                self._mm.seek(0x14)
                rpm_bytes = self._mm.read(4)
                rpm = struct.unpack('<i', rpm_bytes)[0]

                # Log what we're reading every ~2 seconds
                _loop_count += 1
                if _loop_count % 120 == 0:
                    print(f"[AC Telemetry] Reading RPM: {rpm}, Max RPM: {self._max_rpm}, Scaled: {int(rpm * 20000 / self._max_rpm) if self._max_rpm > 0 else rpm}")

                # Periodically check if max RPM has changed (every ~2 seconds)
                # This handles car switches in AC
                _max_rpm_check_counter += 1
                if _max_rpm_check_counter >= 120:  # 120 * 0.016s ≈ 2 seconds
                    _max_rpm_check_counter = 0
                    print("[AC Telemetry] Checking for max RPM update...")
                    self._read_max_rpm()

                # Scale to Boxflat's expected max of 20000
                scaled_rpm = int(rpm * 20000 / self._max_rpm) if self._max_rpm > 0 else rpm

                # Always send callback to keep idle effect from taking over
                if self._callback:
                    self._callback(scaled_rpm)

            except Exception as e:
                # Connection lost, cleanup and retry
                print(f"[AC Telemetry] Connection lost: {e}")
                self._cleanup()
                self._connected = False
                time.sleep(0.5)

            time.sleep(0.016)  # ~60 FPS

        print("[AC Telemetry] Read loop stopped")
