import mmap
import os
import struct


class BaseTelemetry:
    GAME_NAME = "DEFAULT"

    def __init__(self):
        self.GAME_NAME = type(self).GAME_NAME
        self.source_name = ""


    def connect(self):
        raise NotImplementedError


    def is_connected(self):
        return True


    def get_rpm(self):
        raise NotImplementedError


    def close(self):
        pass


class MmapTelemetry(BaseTelemetry):
    PHYSICS_PATH = ""
    PHYSICS_SIZE = 0
    STATIC_PATH = ""
    STATIC_SIZE = 0
    OFFSET_RPM = 0
    OFFSET_CURRENT_MAX_RPM = 0
    OFFSET_STATIC_MAX_RPM = None
    RPM_STRUCT = "=i"
    MAX_RPM_STRUCT = "=i"
    DEFAULT_MAX_RPM = 8000


    def __init__(self):
        super().__init__()
        self.phys = None
        self.static = None
        self._file = None
        self._static_file = None
        self.source_name = self.PHYSICS_PATH


    def connect(self):
        if self.phys is not None:
            return self.is_connected()

        if not os.path.exists(self.PHYSICS_PATH):
            return False

        try:
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
            except OSError:
                file.close()
                raise

            self._file = file
            if not self._connect_static():
                self.close()
                return False
        except OSError as e:
            print(f"{self.GAME_NAME} telemetry connect failed: {e}")
            self.close()
            return False

        return True


    def is_connected(self):
        if self.phys is None or not os.path.exists(self.PHYSICS_PATH):
            return False

        if self.OFFSET_STATIC_MAX_RPM is not None:
            return self.static is not None and os.path.exists(self.STATIC_PATH)

        return True


    def get_rpm(self):
        if self.phys is None:
            return 0, self.DEFAULT_MAX_RPM

        try:
            self.phys.seek(self.OFFSET_RPM)
            rpm = struct.unpack(self.RPM_STRUCT, self.phys.read(4))[0]

            if self.OFFSET_STATIC_MAX_RPM is not None:
                self.static.seek(self.OFFSET_STATIC_MAX_RPM)
                max_rpm = struct.unpack(self.MAX_RPM_STRUCT, self.static.read(4))[0]
            else:
                self.phys.seek(self.OFFSET_CURRENT_MAX_RPM)
                max_rpm = struct.unpack(self.MAX_RPM_STRUCT, self.phys.read(4))[0]
        except (ValueError, BufferError, OSError) as e:
            print(f"{self.GAME_NAME} telemetry read failed: {e}")
            return 0, self.DEFAULT_MAX_RPM

        if max_rpm <= 0:
            max_rpm = self.DEFAULT_MAX_RPM

        return int(rpm), int(max_rpm)


    def _connect_static(self):
        if self.OFFSET_STATIC_MAX_RPM is None:
            return True

        if self.static is not None:
            return True

        if not os.path.exists(self.STATIC_PATH):
            return False

        try:
            file = open(self.STATIC_PATH, "rb")
            if os.fstat(file.fileno()).st_size < self.STATIC_SIZE:
                file.close()
                return False

            try:
                self.static = mmap.mmap(
                    file.fileno(),
                    self.STATIC_SIZE,
                    access=mmap.ACCESS_READ
                )
            except OSError:
                file.close()
                raise

            self._static_file = file
        except OSError as e:
            print(f"{self.GAME_NAME} static telemetry connect failed: {e}")
            return False

        return True


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

        if self.static is not None:
            try:
                self.static.close()
            except (BufferError, OSError):
                pass
            self.static = None

        if self._static_file is not None:
            try:
                self._static_file.close()
            except OSError:
                pass
            self._static_file = None
