import math
import socket
import struct

from boxflat.telemetry.base_telemetry import BaseTelemetry


class DirtRally2(BaseTelemetry):
    GAME_NAME = "DiRT Rally 2.0"

    PACKET_FLOATS = 66
    PACKET_SIZE = PACKET_FLOATS * 4
    UDP_PORT = 20777 # can be set in the DR2.0 config file

    # Codemasters/EGO telemetry packet floats: engineRate is rad/s, maxRPM is RPM.
    # We have to convert engineRate back to rpm
    OFFSET_RPM = 37 * 4
    OFFSET_CURRENT_MAX_RPM = 61 * 4
    IDLE_RPM = 63 * 4
    MAX_GEARS = 65 * 4


    def __init__(self):
        super().__init__()
        self._udp_socket = None
        self._last_rpm = 0
        self._last_max_rpm = self.DEFAULT_MAX_RPM


    def connect(self):
        if self.is_connected():
            return True

        if self._ensure_udp_socket():
            self.source_name = f"udp://0.0.0.0:{self.UDP_PORT}"
            return True

        return False


    def is_connected(self):
        return self._udp_socket is not None


    def get_rpm(self):
        if self._udp_socket is not None:
            return self._get_udp_rpm()

        return 0, self.DEFAULT_MAX_RPM


    def close(self):
        if self._udp_socket is not None:
            try:
                self._udp_socket.close()
            except OSError:
                pass
            self._udp_socket = None


    def _ensure_udp_socket(self):
        if self._udp_socket is not None:
            return True

        try:
            port = self.UDP_PORT
            udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            udp_socket.setblocking(False)
            udp_socket.bind(("", port))
        except (OSError, ValueError) as e:
            print(f"{self.GAME_NAME} UDP telemetry bind failed: {e}")
            return False

        self._udp_socket = udp_socket
        return True


    def _get_udp_rpm(self):
        while True:
            try:
                packet = self._udp_socket.recv(4096)
            except BlockingIOError:
                break
            except OSError as e:
                print(f"{self.GAME_NAME} UDP telemetry read failed: {e}")
                return 0, self.DEFAULT_MAX_RPM

            if len(packet) < self.PACKET_SIZE:
                continue

            rpm_data = self._extract_rpm(packet)

            if rpm_data is None:
                continue

            rpm, max_rpm = rpm_data
            self._last_rpm = int(self._engine_rate_to_rpm(rpm))
            self._last_max_rpm = int(max_rpm) if max_rpm > 0 else self.DEFAULT_MAX_RPM

        return self._last_rpm, self._last_max_rpm


    def _engine_rate_to_rpm(self, engine_rate):
        # convert Radians back to RPM
        return engine_rate * 60 / (2 * math.pi)


    def _extract_rpm(self, packet):
        for offset in range(0, len(packet) - self.PACKET_SIZE + 1, 4):
            try:
                rpm = struct.unpack_from("=f", packet, offset + self.OFFSET_RPM)[0]
                max_rpm = struct.unpack_from("=f", packet, offset + self.OFFSET_CURRENT_MAX_RPM)[0]
                idle_rpm = struct.unpack_from("=f", packet, offset + self.IDLE_RPM)[0]
                max_gears = struct.unpack_from("=f", packet, offset + self.MAX_GEARS)[0]
            except struct.error:
                continue

            # If any of the following 4 checks fail, we are not reading the data at the correct spot in the file, so we
            # try at the next spot
            # So we can use these 4 checks (with values we dont need further on) to validate that we are reading the
            # rpm data at the correct spot and not read anything that looks rpm-y but isnt
            if not 0 <= rpm <= 20000:
                continue

            if not 1000 <= max_rpm <= 25000:
                continue

            if not 0 <= idle_rpm <= 5000:
                continue

            if not 1 <= max_gears <= 12:
                continue

            return rpm, max_rpm

        return None
