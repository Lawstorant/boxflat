import mmap
import os
import struct


class BaseTelemetry:
    GAME_NAME = "DEFAULT"
    DEFAULT_MAX_RPM = 8000

    def __init__(self):
        self.GAME_NAME = type(self).GAME_NAME
        self.source_name = ""


    def connect(self):
        raise NotImplementedError


    def is_connected(self):
        raise NotImplementedError


    def get_rpm(self):
        raise NotImplementedError


    def close(self):
        raise NotImplementedError


class MmapTelemetry(BaseTelemetry):
    PHYSICS_PATH = ""
    PHYSICS_SIZE = 0
    OFFSET_RPM = 0
    OFFSET_CURRENT_MAX_RPM = 0
    RPM_STRUCT = "=i"
    MAX_RPM_STRUCT = "=i"


    def __init__(self):
        super().__init__()
        self.phys = None
        self._file = None
        self.source_name = self.PHYSICS_PATH


    def connect(self):
        if self.phys is not None:
            return self.is_connected()

        if not os.path.exists(self.PHYSICS_PATH):
            return False

        try:
            # No context manager because we close the file in the close function, so that we can continue reading
            file = open(self.PHYSICS_PATH, "rb")
            if os.fstat(file.fileno()).st_size < self.PHYSICS_SIZE:
                file.close()
                return False

            try:
                self.phys = mmap.mmap(
                    file.fileno(),
                    self.PHYSICS_SIZE,
                    access=mmap.ACCESS_READ
                )
            except OSError as e:
                print(f"{self.GAME_NAME} telemetry connect failed: {e}")
                file.close()
                raise e

            self._file = file
        except OSError as e:
            print(f"{self.GAME_NAME} telemetry connect failed: {e}")
            self.close()
            return False

        return True


    def is_connected(self):
        if self.phys is None or not os.path.exists(self.PHYSICS_PATH):
            return False

        return True


    def get_rpm(self):
        if self.phys is None:
            return 0, self.DEFAULT_MAX_RPM

        try:
            self.phys.seek(self.OFFSET_RPM)
            rpm = struct.unpack(self.RPM_STRUCT, self.phys.read(4))[0]

            self.phys.seek(self.OFFSET_CURRENT_MAX_RPM)
            max_rpm = struct.unpack(self.MAX_RPM_STRUCT, self.phys.read(4))[0]
        except (ValueError, BufferError, OSError) as e:
            print(f"{self.GAME_NAME} telemetry read failed: {e}")
            return 0, self.DEFAULT_MAX_RPM

        if max_rpm <= 0:
            max_rpm = self.DEFAULT_MAX_RPM

        return int(rpm), int(max_rpm)


    def close(self):
        if self.phys is not None:
            try:
                self.phys.close()
            except (BufferError, OSError):
                pass
            self.phys = None

        if self._file is not None:
            try:
                self._file.close()
            except OSError:
                pass
            self._file = None
