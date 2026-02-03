# Copyright (c) 2025, Ryan Orth Using CachyOS BTW
# SimAPI integration for reading racing simulator telemetry

import ctypes
import mmap
import os
from threading import Thread, Event
from time import sleep, monotonic

from .subscription import EventDispatcher
from .bitwise import set_bit


# Path to SimAPI shared memory file
SIMAPI_SHM_PATH = "/dev/shm/SIMAPI.DAT"

# SimAPI constants
SIMAPI_STATUS_OFF = 0
SIMAPI_STATUS_MENU = 1
SIMAPI_STATUS_ACTIVE = 2

# Default LED thresholds - spread across full RPM range for better feedback
DEFAULT_THRESHOLDS = [1, 20, 30, 40, 50, 60, 70, 80, 90, 99]

# Max reasonable RPM for validation (F1 engines topped out at ~19000 RPM)
# Set to 20000 to allow margin while rejecting wild values
MAX_REASONABLE_RPM = 20000


class LapTime(ctypes.Structure):
    """Lap time structure from simdata.h"""
    _fields_ = [
        ("hours", ctypes.c_uint32),
        ("minutes", ctypes.c_uint32),
        ("seconds", ctypes.c_uint32),
        ("fraction", ctypes.c_uint32),
    ]


class SimData(ctypes.Structure):
    """
    SimData structure from simapi's simdata.h
    This matches the memory layout of /dev/shm/SIMAPI.DAT

    Note: This is a partial implementation with the fields we need.
    The full structure has many more fields for car data, proximity, etc.
    """
    _pack_ = 4
    _fields_ = [
        ("mtick", ctypes.c_uint64),          # monotonic tick

        ("simstatus", ctypes.c_uint32),      # 0=off, 1=menu, 2=active
        ("velocity", ctypes.c_uint32),       # speed in game units
        ("rpms", ctypes.c_uint32),           # current RPM
        ("gear", ctypes.c_uint32),           # current gear
        ("pulses", ctypes.c_uint32),         # pulse count
        ("maxrpm", ctypes.c_uint32),         # max RPM
        ("idlerpm", ctypes.c_uint32),        # idle RPM
        ("maxgears", ctypes.c_uint32),       # max gears
        ("altitude", ctypes.c_uint32),       # altitude
        ("lap", ctypes.c_uint32),            # current lap
        ("position", ctypes.c_uint32),       # race position
        ("numlaps", ctypes.c_uint32),        # number of laps
        ("playerlaps", ctypes.c_uint32),     # player laps
        ("numcars", ctypes.c_uint32),        # number of cars
        ("gearc", ctypes.c_char * 3),        # gear character

        ("Xvelocity", ctypes.c_double),
        ("Yvelocity", ctypes.c_double),
        ("Zvelocity", ctypes.c_double),

        ("worldXvelocity", ctypes.c_double),
        ("worldYvelocity", ctypes.c_double),
        ("worldZvelocity", ctypes.c_double),

        ("gas", ctypes.c_double),            # throttle
        ("brake", ctypes.c_double),          # brake
        ("fuel", ctypes.c_double),           # fuel level
        ("fuelcapacity", ctypes.c_double),   # fuel capacity
        ("clutch", ctypes.c_double),         # clutch
        ("steer", ctypes.c_double),          # steering
        ("handbrake", ctypes.c_double),      # handbrake

        ("turboboost", ctypes.c_double),
        ("turboboostperct", ctypes.c_double),
        ("maxturbo", ctypes.c_double),

        ("abs", ctypes.c_double),            # ABS
        ("brakebias", ctypes.c_double),
        ("tyreRPS", ctypes.c_double * 4),
        ("tyrediameter", ctypes.c_double * 4),
        ("distance", ctypes.c_double),

        ("heading", ctypes.c_double),
        ("pitch", ctypes.c_double),
        ("roll", ctypes.c_double),
        ("worldposx", ctypes.c_double),
        ("worldposy", ctypes.c_double),
        ("worldposz", ctypes.c_double),

        ("braketemp", ctypes.c_double * 4),
        ("tyrewear", ctypes.c_double * 4),
        ("tyretemp", ctypes.c_double * 4),
        ("tyrepressure", ctypes.c_double * 4),

        ("tyrecontact0", ctypes.c_double * 4),
        ("tyrecontact1", ctypes.c_double * 4),
        ("tyrecontact2", ctypes.c_double * 4),

        ("airdensity", ctypes.c_double),
        ("airtemp", ctypes.c_double),
        ("tracktemp", ctypes.c_double),

        ("suspension", ctypes.c_double * 4),
        ("suspvelocity", ctypes.c_double * 4),

        ("trackdistancearound", ctypes.c_double),
        ("playerspline", ctypes.c_double),
        ("trackspline", ctypes.c_double),
        ("playertrackpos", ctypes.c_uint32),
        ("tracksamples", ctypes.c_uint32),

        ("lastlap", LapTime),
        ("bestlap", LapTime),
        ("currentlap", LapTime),
        ("currentlapinseconds", ctypes.c_uint32),
        ("lastlapinseconds", ctypes.c_uint32),
        ("time", ctypes.c_uint32),
        ("sessiontime", LapTime),
        ("session", ctypes.c_uint8),
        ("sectorindex", ctypes.c_uint8),
        ("sector1time", ctypes.c_double),
        ("sector2time", ctypes.c_double),
        ("lastsectorinms", ctypes.c_uint32),
        ("courseflag", ctypes.c_uint8),      # track flags
        ("playerflag", ctypes.c_uint8),      # player flags

        ("lapisvalid", ctypes.c_bool),

        ("car", ctypes.c_char * 128),
        ("track", ctypes.c_char * 128),
        ("driver", ctypes.c_char * 128),
        ("tyrecompound", ctypes.c_char * 128),

        # Note: We skip cars[MAXCARS] and pd[PROXCARS] arrays as they're large
        # and we don't need them for RPM light control
    ]


class SimApiHandler(EventDispatcher):
    """
    Handles reading telemetry data from SimAPI shared memory.
    Follows the pattern established by HidHandler.

    Events dispatched:
    - "rpm-percent": RPM as percentage (0-100)
    - "rpm-bitmask": 16-bit LED bitmask
    - "gear": Current gear number
    - "sim-status": Simulation status (0=off, 1=menu, 2=active)
    - "connected": SimAPI availability (bool)
    """

    def __init__(self):
        super().__init__()

        # Threading
        self._running = Event()
        self._poll_rate = 60  # Hz

        # Shared memory
        self._shm_fd = None
        self._mm = None

        # Configuration
        self._led_count = 10
        self._thresholds = DEFAULT_THRESHOLDS.copy()
        self._blink_threshold = 95  # Percentage for blinking

        # State
        self._last_rpm_percent = -1
        self._last_bitmask = -1
        self._last_gear = -1
        self._last_status = -1
        self._connected = False
        self._last_telemetry_time = 0  # Track last telemetry send for keepalive

        # Watchdog for detecting stale connections (simd restart)
        self._last_mtick = 0
        self._stale_count = 0
        self._stale_threshold = 30  # Reconnect after this many stale reads (~0.5s at 60Hz)

        # Auto-calibration state
        self._calibrated_maxrpm = 0  # Highest RPM seen
        self._last_car = b""  # Track car changes for recalibration
        self._last_track = b""  # Track track changes
        self._calibration_buffer = 1.05  # Add 5% buffer above highest seen
        self._maxrpm_before_change = 0  # Track maxrpm before car change to detect stale data

        # Connection manager reference (set externally)
        self._connection_manager = None
        self._dash_enabled = False
        self._wheel_enabled = False
        self._wheel_old_protocol = False  # True for ES wheel (old protocol)
        self._wheel_colors_sent = False  # Track if we've sent color config
        self._auto_enable = True
        self._debug = True  # Enable debug output
        self._debug_ui_enabled = False  # UI debug view toggle

        # Register events
        self._register_events(
            "rpm-percent",
            "rpm-bitmask",
            "rpm-raw",  # (rpm, maxrpm, idlerpm, effective_max) tuple for debugging
            "gear",
            "sim-status",
            "connected",
            "car-changed",  # Emitted when car/session changes
            "car-name",  # Current car name as string
            "debug-data"  # Full SimData dict for debug UI
        )

    def set_connection_manager(self, cm):
        """Set the connection manager for sending telemetry commands."""
        self._connection_manager = cm

    def start(self) -> bool:
        """Start the telemetry polling thread."""
        if self._running.is_set():
            return True

        self._running.set()
        Thread(target=self._poll_loop, daemon=True).start()
        return True

    def stop(self) -> None:
        """Stop the telemetry polling thread."""
        self._running.clear()
        self._close_shm()

    def is_available(self) -> bool:
        """Check if simd process is running by scanning /proc."""
        try:
            for pid in os.listdir("/proc"):
                if pid.isdigit():
                    try:
                        with open(f"/proc/{pid}/comm", "r") as f:
                            if f.read().strip() == "simd":
                                return True
                    except (FileNotFoundError, PermissionError):
                        continue
        except OSError:
            pass
        return False

    def is_connected(self) -> bool:
        """Check if currently connected to SimAPI."""
        return self._connected

    def set_thresholds(self, thresholds: list) -> None:
        """Set the RPM percentage thresholds for each LED."""
        if len(thresholds) == self._led_count:
            self._thresholds = list(thresholds)

    def get_thresholds(self) -> list:
        """Get current RPM thresholds."""
        return self._thresholds.copy()

    def set_poll_rate(self, hz: int) -> None:
        """Set polling frequency in Hz (1-120)."""
        self._poll_rate = max(1, min(hz, 120))

    def get_poll_rate(self) -> int:
        """Get current polling rate."""
        return self._poll_rate

    def set_dash_enabled(self, enabled: bool) -> None:
        """Enable/disable sending telemetry to dashboard."""
        self._dash_enabled = enabled
        if not enabled and self._connection_manager:
            # Clear LEDs when disabling
            self._connection_manager.set_setting(0, "dash-send-telemetry")

    def set_wheel_enabled(self, enabled: bool) -> None:
        """Enable/disable sending telemetry to wheel."""
        self._wheel_enabled = enabled
        self._wheel_colors_sent = False  # Reset so colors get sent on first telemetry
        if self._connection_manager and not enabled:
            # Clear LEDs when disabling
            if self._wheel_old_protocol:
                self._connection_manager.set_setting(0, "wheel-old-send-telemetry")
            else:
                self._connection_manager.set_setting([0, 0], "wheel-send-rpm-telemetry")

    def set_wheel_old_protocol(self, old_protocol: bool) -> None:
        """Set whether to use old wheel protocol (ES wheel) or new protocol."""
        self._wheel_old_protocol = old_protocol
        self._wheel_colors_sent = False  # Reset colors flag when switching protocols

    def set_auto_enable(self, enabled: bool) -> None:
        """Enable/disable auto-start when sim is detected."""
        self._auto_enable = enabled

    def set_debug_ui_enabled(self, enabled: bool) -> None:
        """Enable/disable debug UI data dispatching."""
        self._debug_ui_enabled = enabled

    def is_debug_ui_enabled(self) -> bool:
        """Check if debug UI data dispatching is enabled."""
        return self._debug_ui_enabled

    def reset_calibration(self) -> None:
        """Reset the auto-calibrated max RPM."""
        self._calibrated_maxrpm = 0
        self._maxrpm_before_change = 0
        if self._debug:
            print("[SimAPI] Max RPM calibration reset")

    def get_calibrated_maxrpm(self) -> int:
        """Get the current auto-calibrated max RPM."""
        return self._calibrated_maxrpm

    def _open_shm(self) -> bool:
        """Open and memory-map the SimAPI shared memory file."""
        if self._mm is not None:
            return True

        if not self.is_available():
            if self._connected:
                self._connected = False
                self._dispatch("connected", False)
            return False

        try:
            self._shm_fd = os.open(SIMAPI_SHM_PATH, os.O_RDONLY)
            file_size = os.fstat(self._shm_fd).st_size

            # Map only what we need (or the full file if smaller)
            map_size = min(file_size, ctypes.sizeof(SimData))
            self._mm = mmap.mmap(self._shm_fd, map_size, access=mmap.ACCESS_READ)

            self._last_mtick = 0  # Reset watchdog
            self._stale_count = 0
            if not self._connected:
                self._connected = True
                self._dispatch("connected", True)
            return True

        except (FileNotFoundError, OSError, ValueError) as e:
            self._close_shm()
            return False

    def _close_shm(self) -> None:
        """Close shared memory mapping."""
        if self._mm:
            try:
                self._mm.close()
            except:
                pass
            self._mm = None

        if self._shm_fd is not None:
            try:
                os.close(self._shm_fd)
            except:
                pass
            self._shm_fd = None

        # Only dispatch disconnection if simd is actually not running
        # (shared memory file doesn't exist). This prevents UI flapping
        # during internal reconnections due to stale data.
        if self._connected and not self.is_available():
            self._connected = False
            self._dispatch("connected", False)

    def _read_simdata(self) -> SimData:
        """Read current SimData from shared memory."""
        if not self._mm:
            return None

        try:
            self._mm.seek(0)
            data = self._mm.read(ctypes.sizeof(SimData))
            return SimData.from_buffer_copy(data)
        except (ValueError, OSError):
            self._close_shm()
            return None

    def _poll_loop(self) -> None:
        """Main polling loop - runs in daemon thread."""
        reconnect_interval = 1.0  # Seconds between reconnect attempts
        availability_check_counter = 0
        availability_check_interval = 60  # Check every ~1 second at 60Hz

        while self._running.is_set():
            interval = 1.0 / self._poll_rate

            # Periodically check if simd is still running
            availability_check_counter += 1
            if availability_check_counter >= availability_check_interval:
                availability_check_counter = 0
                if not self.is_available() and self._connected:
                    self._connected = False
                    self._dispatch("connected", False)
                    self._close_shm()

            # Try to open shared memory if not mapped
            if self._mm is None:
                if not self._open_shm():
                    sleep(reconnect_interval)
                    continue

            data = self._read_simdata()
            if data is None:
                sleep(reconnect_interval)
                continue

            # Watchdog: check if mtick is updating (detect simd restart)
            if data.mtick == self._last_mtick:
                self._stale_count += 1
                if self._stale_count >= self._stale_threshold:
                    # if self._debug:
                    #     print("[SimAPI] Connection stale, reconnecting...")
                    self._close_shm()
                    self._stale_count = 0
                    sleep(reconnect_interval)
                    continue
            else:
                self._last_mtick = data.mtick
                self._stale_count = 0

            self._process_telemetry(data)
            sleep(interval)

        # Cleanup on exit
        self._clear_leds()

    def _process_telemetry(self, data: SimData) -> None:
        """Process telemetry data and dispatch events."""
        # Dispatch status changes
        if data.simstatus != self._last_status:
            self._last_status = data.simstatus
            self._dispatch("sim-status", data.simstatus)

            # Clear LEDs when sim becomes inactive
            if data.simstatus != SIMAPI_STATUS_ACTIVE:
                self._clear_leds()
                # Clear car name
                self._dispatch("car-name", "None")
                return
            else:
                # Sim just became active - wake up the wheel with a brief flash
                self._wake_up_leds()
                # Dispatch current car name
                try:
                    car_name = data.car.decode('utf-8', errors='ignore').rstrip('\x00')
                    self._dispatch("car-name", car_name if car_name else "Unknown")
                except:
                    self._dispatch("car-name", "Unknown")

        # Only process RPM when sim is active
        if data.simstatus != SIMAPI_STATUS_ACTIVE:
            return

        # Detect car/track changes for recalibration
        current_car = data.car
        current_track = data.track
        if current_car != self._last_car or current_track != self._last_track:
            if self._last_car != b"" or self._last_track != b"":
                # Car or track changed - reset calibration and save old maxrpm
                # to detect stale data from SimAPI
                self._maxrpm_before_change = data.maxrpm
                self._calibrated_maxrpm = 0
                if self._debug:
                    try:
                        car_name = current_car.decode('utf-8', errors='ignore').rstrip('\x00')
                        print(f"[SimAPI] Car/track changed, resetting calibration. Car: {car_name}")
                    except:
                        pass
                self._dispatch("car-changed", current_car)
            self._last_car = current_car
            self._last_track = current_track

            # Dispatch car name as readable string
            try:
                car_name = current_car.decode('utf-8', errors='ignore').rstrip('\x00')
                self._dispatch("car-name", car_name if car_name else "Unknown")
            except:
                self._dispatch("car-name", "Unknown")

        # Determine effective max RPM (use game value or auto-calibrate)
        if self._maxrpm_before_change > 0 and data.maxrpm != self._maxrpm_before_change:
            if self._debug:
                print(f"[SimAPI] MaxRPM updated to {data.maxrpm}, clearing stale marker")
            self._maxrpm_before_change = 0

        # Use auto-calibration if game value is missing, stale, or unreasonable
        use_auto_calibration = (
            data.maxrpm == 0 or
            data.maxrpm > MAX_REASONABLE_RPM or
            data.maxrpm <= data.idlerpm or
            self._maxrpm_before_change > 0  # stale after car change
        )

        if use_auto_calibration:
            # Update calibration if we see a valid higher RPM
            if self._calibrated_maxrpm < data.rpms <= MAX_REASONABLE_RPM:
                self._calibrated_maxrpm = data.rpms
                if self._debug:
                    print(f"[SimAPI] Auto-calibrated maxRPM: {self._calibrated_maxrpm}")
            effective_maxrpm = int(self._calibrated_maxrpm * self._calibration_buffer)
        else:
            effective_maxrpm = data.maxrpm

        # Debug: print raw values periodically (after effective_maxrpm is calculated)
        if self._debug and data.simstatus == SIMAPI_STATUS_ACTIVE:
            if not hasattr(self, '_debug_counter'):
                self._debug_counter = 0
            self._debug_counter += 1
            if self._debug_counter % 300 == 0:  # Every ~10 second at 60Hz
                print(f"[SimAPI] RPM: {data.rpms}, MaxRPM: {data.maxrpm} (eff: {effective_maxrpm}), IdleRPM: {data.idlerpm}, Gear: {data.gear}")

        # Calculate RPM percentage using effective max
        rpm_percent = self._calculate_rpm_percent(data.rpms, effective_maxrpm, data.idlerpm)

        # Dispatch raw RPM data periodically for display (every 10 polls = ~6Hz at 60Hz poll rate)
        if not hasattr(self, '_raw_counter'):
            self._raw_counter = 0
        self._raw_counter += 1
        if self._raw_counter % 10 == 0:
            self._dispatch("rpm-raw", (data.rpms, data.maxrpm, data.idlerpm, effective_maxrpm))

            # Dispatch full debug data if debug UI is enabled
            if self._debug_ui_enabled:
                self._dispatch("debug-data", self._simdata_to_dict(data))

        # Dispatch RPM changes
        if rpm_percent != self._last_rpm_percent:
            self._last_rpm_percent = rpm_percent
            self._dispatch("rpm-percent", rpm_percent)

        # Calculate bitmask and send telemetry
        bitmask = self._calculate_bitmask(rpm_percent)
        current_time = monotonic()
        time_since_last = current_time - self._last_telemetry_time

        # Send telemetry if bitmask changed or keepalive needed (at least once per second)
        if bitmask != self._last_bitmask or time_since_last >= 1.0:
            if bitmask != self._last_bitmask:
                self._last_bitmask = bitmask
                self._dispatch("rpm-bitmask", bitmask)
            self._send_telemetry(bitmask)
            self._last_telemetry_time = current_time

        # Dispatch gear changes
        if data.gear != self._last_gear:
            self._last_gear = data.gear
            self._dispatch("gear", data.gear)

    def _calculate_rpm_percent(self, rpm: int, max_rpm: int, idle_rpm: int) -> int:
        """Calculate RPM as percentage of usable range."""
        if max_rpm <= idle_rpm:
            return 0

        rpm_range = max_rpm - idle_rpm
        rpm_percent = int(((rpm - idle_rpm) / rpm_range) * 100)
        return max(0, min(100, rpm_percent))

    def _calculate_bitmask(self, rpm_percent: int) -> int:
        """Convert RPM percentage to LED bitmask."""
        bitmask = 0
        for i, threshold in enumerate(self._thresholds):
            if rpm_percent >= threshold:
                bitmask = set_bit(bitmask, i)
        return bitmask

    def _simdata_to_dict(self, data: SimData) -> dict:
        """Convert SimData structure to a dictionary for debug display."""
        def decode_str(b):
            try:
                return b.decode('utf-8', errors='ignore').rstrip('\x00')
            except:
                return ""

        def laptime_to_str(lt: LapTime) -> str:
            return f"{lt.hours:02d}:{lt.minutes:02d}:{lt.seconds:02d}.{lt.fraction:03d}"

        return {
            # Basic telemetry
            "mtick": data.mtick,
            "simstatus": data.simstatus,
            "velocity": data.velocity,
            "rpms": data.rpms,
            "gear": data.gear,
            "maxrpm": data.maxrpm,
            "idlerpm": data.idlerpm,
            "maxgears": data.maxgears,
            "gearc": decode_str(data.gearc),

            # Position/Lap info
            "lap": data.lap,
            "position": data.position,
            "numlaps": data.numlaps,
            "playerlaps": data.playerlaps,
            "numcars": data.numcars,
            "altitude": data.altitude,

            # Velocity vectors
            "Xvelocity": data.Xvelocity,
            "Yvelocity": data.Yvelocity,
            "Zvelocity": data.Zvelocity,
            "worldXvelocity": data.worldXvelocity,
            "worldYvelocity": data.worldYvelocity,
            "worldZvelocity": data.worldZvelocity,

            # Controls
            "gas": data.gas,
            "brake": data.brake,
            "clutch": data.clutch,
            "steer": data.steer,
            "handbrake": data.handbrake,

            # Fuel
            "fuel": data.fuel,
            "fuelcapacity": data.fuelcapacity,

            # Turbo
            "turboboost": data.turboboost,
            "turboboostperct": data.turboboostperct,
            "maxturbo": data.maxturbo,

            # ABS/Brakes
            "abs": data.abs,
            "brakebias": data.brakebias,
            "braketemp": list(data.braketemp),

            # Tyres
            "tyreRPS": list(data.tyreRPS),
            "tyrediameter": list(data.tyrediameter),
            "tyrewear": list(data.tyrewear),
            "tyretemp": list(data.tyretemp),
            "tyrepressure": list(data.tyrepressure),

            # Orientation
            "heading": data.heading,
            "pitch": data.pitch,
            "roll": data.roll,

            # World position
            "worldposx": data.worldposx,
            "worldposy": data.worldposy,
            "worldposz": data.worldposz,
            "distance": data.distance,

            # Suspension
            "suspension": list(data.suspension),
            "suspvelocity": list(data.suspvelocity),

            # Track
            "trackdistancearound": data.trackdistancearound,
            "playerspline": data.playerspline,
            "trackspline": data.trackspline,
            "playertrackpos": data.playertrackpos,
            "tracksamples": data.tracksamples,

            # Weather
            "airdensity": data.airdensity,
            "airtemp": data.airtemp,
            "tracktemp": data.tracktemp,

            # Timing
            "lastlap": laptime_to_str(data.lastlap),
            "bestlap": laptime_to_str(data.bestlap),
            "currentlap": laptime_to_str(data.currentlap),
            "currentlapinseconds": data.currentlapinseconds,
            "lastlapinseconds": data.lastlapinseconds,
            "time": data.time,
            "sessiontime": laptime_to_str(data.sessiontime),
            "session": data.session,
            "sectorindex": data.sectorindex,
            "sector1time": data.sector1time,
            "sector2time": data.sector2time,
            "lastsectorinms": data.lastsectorinms,

            # Flags
            "courseflag": data.courseflag,
            "playerflag": data.playerflag,
            "lapisvalid": data.lapisvalid,

            # Session info
            "car": decode_str(data.car),
            "track": decode_str(data.track),
            "driver": decode_str(data.driver),
            "tyrecompound": decode_str(data.tyrecompound),
        }

    def _send_telemetry(self, bitmask: int) -> None:
        """Send telemetry to enabled devices."""
        if not self._connection_manager:
            return

        if self._dash_enabled:
            self._connection_manager.set_setting(bitmask, "dash-send-telemetry")

        if self._wheel_enabled:
            if self._wheel_old_protocol:
                # Old protocol (ES wheel): simple 4-byte integer, same as dashboard
                self._connection_manager.set_setting(bitmask, "wheel-old-send-telemetry")
            else:
                # New protocol: send colors on first telemetry, then [low_byte, high_byte]
                if not self._wheel_colors_sent:
                    self._setup_wheel_telemetry_colors()
                    self._wheel_colors_sent = True

                self._connection_manager.set_setting(
                    [bitmask & 255, bitmask >> 8],
                    "wheel-send-rpm-telemetry"
                )

    def _clear_leds(self) -> None:
        """Clear all LEDs."""
        self._last_bitmask = 0
        self._last_rpm_percent = -1

        if not self._connection_manager:
            return

        if self._dash_enabled:
            self._connection_manager.set_setting(0, "dash-send-telemetry")

        if self._wheel_enabled:
            if self._wheel_old_protocol:
                self._connection_manager.set_setting(0, "wheel-old-send-telemetry")
            else:
                self._connection_manager.set_setting([0, 0], "wheel-send-rpm-telemetry")

    def _wake_up_leds(self) -> None:
        """Send a brief flash to wake up the wheel's telemetry mode.

        Some wheels don't respond to telemetry until they receive a non-zero
        bitmask. This sends all LEDs on then off to initialize the wheel.
        """
        if not self._connection_manager:
            return

        full_bitmask = 0x3FF  # All 10 LEDs on

        if self._dash_enabled:
            self._connection_manager.set_setting(full_bitmask, "dash-send-telemetry")
            self._connection_manager.set_setting(0, "dash-send-telemetry")

        if self._wheel_enabled:
            if self._wheel_old_protocol:
                self._connection_manager.set_setting(full_bitmask, "wheel-old-send-telemetry")
                self._connection_manager.set_setting(0, "wheel-old-send-telemetry")
            else:
                # For new wheels, ensure colors are sent first
                if not self._wheel_colors_sent:
                    self._setup_wheel_telemetry_colors()
                    self._wheel_colors_sent = True
                self._connection_manager.set_setting(
                    [full_bitmask & 255, full_bitmask >> 8],
                    "wheel-send-rpm-telemetry"
                )
                self._connection_manager.set_setting([0, 0], "wheel-send-rpm-telemetry")

        # Reset last bitmask so the next telemetry update will be sent,
        # even if RPM is below 10% (bitmask=0)
        self._last_bitmask = -1

    def _setup_wheel_telemetry_colors(self) -> None:
        """Configure wheel telemetry LED colors (required before telemetry works).

        The wheel needs color data sent via wheel-telemetry-rpm-colors before
        it will display RPM telemetry. Format is [index, R, G, B, ...] in
        two 20-byte chunks.
        """
        if not self._connection_manager:
            return

        # Default colors: green (1-3), red (4-7), blue (8-10)
        colors = [
            [0, 255, 0],    # LED 1 - green
            [0, 255, 0],    # LED 2 - green
            [0, 255, 0],    # LED 3 - green
            [255, 0, 0],    # LED 4 - red
            [255, 0, 0],    # LED 5 - red
            [255, 0, 0],    # LED 6 - red
            [255, 0, 0],    # LED 7 - red
            [0, 0, 255],    # LED 8 - blue
            [0, 0, 255],    # LED 9 - blue
            [0, 0, 255],    # LED 10 - blue
        ]

        # Build the color data array: [index, R, G, B, index, R, G, B, ...]
        color_data = []
        for i, color in enumerate(colors):
            color_data.append(i)
            color_data.extend(color)

        # Send in two chunks of 20 bytes each (5 LEDs per chunk)
        self._connection_manager.set_setting(color_data[:20], "wheel-telemetry-rpm-colors")
        self._connection_manager.set_setting(color_data[20:], "wheel-telemetry-rpm-colors")
