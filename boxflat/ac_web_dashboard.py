#!/usr/bin/env python3
# Copyright (c) 2025, Kevin Florczak Also Using Arch BTW

"""
Assetto Corsa Web Dashboard
Serves a fullscreen web dashboard displaying AC telemetry in real-time.
Accessible from phone/tablet/PC browser while playing AC.
"""

import mmap
import os
import struct
import ctypes
import asyncio
import json
from threading import Thread, Event
from typing import Set
from pathlib import Path

from aiohttp import web, WSMsgType

# AC shared memory files
AC_PHYSICS_FILE = "/acpmf_physics"
AC_GRAPHICS_FILE = "/acpmf_graphics"


class ACTelemetryReader:
    """Reads telemetry data from AC shared memory using shm_ui_map.json configuration."""

    # Shared memory regions
    SHM_REGIONS = {
        "physics": AC_PHYSICS_FILE,
        "graphics": AC_GRAPHICS_FILE,
    }

    def __init__(self):
        self._running = Event()
        self._shm_regions = {}  # Maps region name -> (fd, mmap)
        self._max_rpm = 20000
        self._connected = False
        self._ui_map = {}
        self._load_ui_map()

    def _load_ui_map(self):
        """Load the UI map configuration."""
        try:
            ui_map_path = Path(__file__).parent / "dashboard" / "shm_ui_map.json"
            with open(ui_map_path, 'r') as f:
                self._ui_map = json.load(f)
            print(f"[AC Dashboard] Loaded UI map from {ui_map_path}")
        except Exception as e:
            print(f"[AC Dashboard] Could not load UI map: {e}")
            self._ui_map = {}

    def _shm_open(self, name, flags):
        """Open shared memory object."""
        libc = ctypes.CDLL("libc.so.6")
        shm_open = libc.shm_open
        shm_open.restype = ctypes.c_int
        return shm_open(name.encode(), flags, 0)

    def _open_region(self, region_name: str, shm_file: str) -> bool:
        """Open a shared memory region."""
        try:
            fd = self._shm_open(shm_file, os.O_RDONLY)
            size = os.fstat(fd).st_size
            mm = mmap.mmap(fd, size, access=mmap.ACCESS_READ)
            self._shm_regions[region_name] = (fd, mm)
            print(f"[AC Dashboard] Connected to {region_name} shared memory, size: {size} bytes")
            return True
        except Exception as e:
            print(f"[AC Dashboard] Could not open {region_name} shared memory: {e}")
            return False

    def _get_region(self, region_name: str):
        """Get the mmap object for a region."""
        if region_name in self._shm_regions:
            fd, mm = self._shm_regions[region_name]
            return mm
        return None

    def _read_max_rpm(self):
        """Read max RPM from physics shared memory."""
        try:
            mm = self._get_region("physics")
            if not mm:
                return False

            fd, _ = self._shm_regions["physics"]
            size = os.fstat(fd).st_size

            # Scan for max RPM around 0x0190-0x01C0
            for offset in range(0x0190, min(0x01C0, size - 4), 4):
                mm.seek(offset)
                val_bytes = mm.read(4)
                if len(val_bytes) == 4:
                    val_i = struct.unpack('<i', val_bytes)[0]
                    val_f = struct.unpack('<f', val_bytes)[0]

                    if 5000 <= val_f <= 30000:
                        self._max_rpm = int(val_f)
                        print(f"[AC Dashboard] Found max RPM: {self._max_rpm} at offset 0x{offset:04x}")
                        return True
                    elif 5000 <= val_i <= 30000:
                        self._max_rpm = val_i
                        print(f"[AC Dashboard] Found max RPM: {self._max_rpm} at offset 0x{offset:04x} (int)")
                        return True

            return False

        except Exception as e:
            print(f"[AC Dashboard] Could not read max RPM: {e}")
            return False

    def read_value(self, key: str, default=None):
        """Read a single value from shared memory using the UI map configuration.

        This is the unified reader - all telemetry reads go through this method.
        """
        if key not in self._ui_map:
            return default

        config = self._ui_map[key]
        shm_type = config.get("shm")
        offset = config.get("offset")
        data_type = config.get("type")

        mm = self._get_region(shm_type)
        if not mm:
            return default

        try:
            mm.seek(offset)
            if data_type == "float":
                return struct.unpack('<f', mm.read(4))[0]
            elif data_type == "int":
                return struct.unpack('<i', mm.read(4))[0]
            elif data_type == "wchar":
                # Read wide string (null-terminated)
                chars = []
                for _ in range(64):  # max 64 chars
                    char = mm.read(4).decode('utf-32', errors='ignore').rstrip('\x00')
                    if not char:
                        break
                    chars.append(char)
                return ''.join(chars)
        except Exception:
            pass

        return default

    def read_array(self, key: str, count: int, default=None):
        """Read an array of values from shared memory."""
        if key not in self._ui_map:
            return default

        config = self._ui_map[key]
        shm_type = config.get("shm")
        offset = config.get("offset")
        data_type = config.get("type")

        mm = self._get_region(shm_type)
        if not mm:
            return default

        try:
            values = []
            for i in range(count):
                mm.seek(offset + (i * 4))
                if data_type == "float":
                    values.append(struct.unpack('<f', mm.read(4))[0])
                elif data_type == "int":
                    values.append(struct.unpack('<i', mm.read(4))[0])
            return values
        except Exception:
            pass

        return default

    def connect(self):
        """Connect to all shared memory regions."""
        success = True
        for region_name, shm_file in self.SHM_REGIONS.items():
            if not self._open_region(region_name, shm_file):
                success = False

        if success:
            self._read_max_rpm()
            self._connected = True

        return success

    def read_telemetry(self):
        """Read all telemetry data and return as dict."""
        if not self._connected:
            return None

        try:
            data = {}

            # Read basic physics values using unified reader
            for key in ["speed", "gear", "rpm", "brake", "drs", "pitLimiter", "fuel"]:
                value = self.read_value(key)
                if value is not None:
                    data[key] = value

            # Read graphics values - convert tc/abs to float for dashboard compatibility
            for key in ["tc", "abs", "lap"]:
                value = self.read_value(key)
                if value is not None:
                    # tc and abs are stored as int but dashboard expects float
                    data[key] = float(value) if key in ["tc", "abs"] else value

            # Read time fields
            for key in ["iCurrentTime", "iBestTime"]:
                value = self.read_value(key)
                if value is not None:
                    data[key] = value

            # Read string fields
            for key in ["currentTimeStr", "bestTimeStr", "tyreCompound"]:
                value = self.read_value(key)
                if value is not None:
                    data[key] = value

            # Read tyre temperature array
            temps = self.read_array("tyreCoreTemperature", 4)
            if temps:
                data["tyreCoreTemperature"] = temps

            # Read tyre pressure array if available
            pressures = self.read_array("tyrePressure", 4)
            if pressures:
                data["tyrePressure"] = pressures

            # Calculate fuel values
            if "fuel" in data:
                data["fuelRem"] = round(data["fuel"] * 60, 1)
                data["fuelCap"] = 60.0
                data["fuelPerLap"] = 0.0

            # Optional fields with defaults
            data["waterTemp"] = self.read_value("waterTemp", default=90.0)
            data["brakeBias"] = self.read_value("brakeBias", default=55)

            # Add max RPM for percentage calculation
            data["maxRpm"] = self._max_rpm
            data["rpmPercent"] = min(100, max(0, int(data.get("rpm", 0) * 100 / self._max_rpm)))

            return data

        except Exception as e:
            print(f"[AC Dashboard] Error reading telemetry: {e}")
            self._connected = False
            return None

    def cleanup(self):
        """Clean up resources."""
        for fd, mm in self._shm_regions.values():
            try:
                mm.close()
                os.close(fd)
            except:
                pass

        self._shm_regions.clear()
        self._connected = False


# Connected WebSocket clients
connected_clients: Set[web.WebSocketResponse] = set()

# Telemetry reader instance
telemetry_reader = ACTelemetryReader()


async def broadcast_telemetry():
    """Read telemetry and broadcast to all connected clients."""
    data_count = 0
    while True:
        # Ensure connection
        if not telemetry_reader._connected:
            if not telemetry_reader.connect():
                await asyncio.sleep(1)
                continue

        # Read telemetry
        data = telemetry_reader.read_telemetry()

        if data and connected_clients:
            # Debug: log data every 5 seconds
            data_count += 1
            if data_count % 300 == 0:
                print(f"[AC Dashboard] Broadcasting: RPM={data.get('rpm')}, Gear={data.get('gear')}, Speed={data.get('speed')}")

            # Broadcast to all connected clients
            message = json.dumps(data)
            disconnected = set()

            for client in list(connected_clients):
                try:
                    await client.send_str(message)
                except:
                    disconnected.add(client)

            # Remove disconnected clients
            connected_clients.difference_update(disconnected)

        await asyncio.sleep(0.016)  # ~60 FPS


async def websocket_handler(request):
    """Handle WebSocket connections."""
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    print(f"[AC Dashboard] Client connected: {request.remote}")
    connected_clients.add(ws)

    try:
        # Keep connection alive and handle incoming messages
        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                # Could handle commands here if needed
                pass
            elif msg.type == WSMsgType.ERROR:
                print(f"[AC Dashboard] WebSocket error: {ws.exception()}")
    except Exception as e:
        print(f"[AC Dashboard] Connection error: {e}")
    finally:
        connected_clients.remove(ws)
        print(f"[AC Dashboard] Client disconnected: {request.remote}")

    return ws


def get_dashboard_html():
    """Return the HTML dashboard page (fallback - should not be used)."""
    return "<html><body><h1>Error: Dashboard theme not found. Please ensure default.html exists in dashboard_themes directory.</h1></body></html>"


async def serve_dashboard(request):
    """Serve the dashboard HTML page."""
    import os

    # Get theme from environment variable (set by panel) or query parameter for override
    theme = os.environ.get('AC_DASHBOARD_THEME', 'Default')
    # Allow query parameter to override for testing/bookmarking
    theme = request.query.get('theme', theme)

    # Map theme names to filenames (all loaded from files now)
    theme_files = {}

    # Load available themes from dashboard/themes directory
    themes_dir = os.path.join(os.path.dirname(__file__), 'dashboard', 'themes')
    if os.path.exists(themes_dir):
        for filename in os.listdir(themes_dir):
            if filename.endswith('.html'):
                # Convert filename to theme name (e.g., "default.html" -> "Default")
                theme_name = filename[:-5]  # Remove .html
                theme_name = theme_name[0].upper() + theme_name[1:] if theme_name else ""
                theme_files[theme_name] = os.path.join(themes_dir, filename)

    # Get the HTML content
    if theme in theme_files:
        # Load from file
        try:
            with open(theme_files[theme], 'r') as f:
                html_content = f.read()
            print(f"[AC Dashboard] Loading theme: {theme} from file")
            return web.Response(text=html_content, content_type='text/html')
        except Exception as e:
            print(f"[AC Dashboard] Error loading theme file: {e}")
            # Fall back to error message
            return web.Response(text=get_dashboard_html(), content_type='text/html')
    else:
        # Theme not found
        print(f"[AC Dashboard] Theme not found: {theme}. Available themes: {list(theme_files.keys())}")
        return web.Response(text=get_dashboard_html(), content_type='text/html')


async def serve_static(request):
    """Serve static files (JS, CSS, etc.) from dashboard/scripts directory."""
    import os
    filename = request.match_info.get('filename')
    if not filename:
        return web.Response(status=404, text="Not found")

    # Security: only allow serving from dashboard/scripts directory
    scripts_dir = os.path.join(os.path.dirname(__file__), 'dashboard', 'scripts')
    file_path = os.path.join(scripts_dir, filename)

    # Ensure the path is within scripts_dir
    if not os.path.abspath(file_path).startswith(os.path.abspath(scripts_dir)):
        return web.Response(status=403, text="Access denied")

    if os.path.exists(file_path) and os.path.isfile(file_path):
        # Determine content type
        if filename.endswith('.js'):
            content_type = 'application/javascript'
        elif filename.endswith('.css'):
            content_type = 'text/css'
        elif filename.endswith('.svg'):
            content_type = 'image/svg+xml'
        elif filename.endswith('.png'):
            content_type = 'image/png'
        elif filename.endswith('.jpg') or filename.endswith('.jpeg'):
            content_type = 'image/jpeg'
        else:
            content_type = 'text/plain'

        try:
            with open(file_path, 'r') as f:
                content = f.read()
            return web.Response(text=content, content_type=content_type)
        except Exception as e:
            print(f"[AC Dashboard] Error serving static file: {e}")
            return web.Response(status=500, text="Internal server error")
    else:
        return web.Response(status=404, text="File not found")


async def serve_icons(request):
    """Serve icon files from dashboard/icons directory."""
    import os
    filename = request.match_info.get('filename')
    if not filename:
        return web.Response(status=404, text="Not found")

    icons_dir = os.path.join(os.path.dirname(__file__), 'dashboard', 'icons')
    file_path = os.path.join(icons_dir, filename)

    # Security: only allow serving from icons_dir
    if not os.path.abspath(file_path).startswith(os.path.abspath(icons_dir)):
        return web.Response(status=403, text="Access denied")

    if os.path.exists(file_path) and os.path.isfile(file_path):
        # Determine content type based on extension
        if filename.endswith('.svg'):
            content_type = 'image/svg+xml'
        elif filename.endswith('.png'):
            content_type = 'image/png'
        elif filename.endswith('.jpg') or filename.endswith('.jpeg'):
            content_type = 'image/jpeg'
        else:
            content_type = 'application/octet-stream'

        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            return web.Response(body=content, content_type=content_type)
        except Exception as e:
            print(f"[AC Dashboard] Error serving icon file: {e}")
            return web.Response(status=500, text="Internal server error")
    else:
        return web.Response(status=404, text="Icon not found")


async def start_web_server():
    """Start the web server with WebSocket support on port 8765."""
    app = web.Application()
    app.router.add_get('/', serve_dashboard)
    app.router.add_get('/ws', websocket_handler)
    app.router.add_get('/dashboard/scripts/{filename}', serve_static)
    app.router.add_get('/dashboard/icons/{filename}', serve_icons)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8765)
    await site.start()

    print("[AC Dashboard] Web server started on http://localhost:8765")
    print("[AC Dashboard] WebSocket endpoint: ws://localhost:8765/ws")
    print("[AC Dashboard] Access from your phone/tablet using your PC's IP address")


async def main():
    """Main entry point."""
    print("[AC Dashboard] Starting AC Web Dashboard...")

    # Start web server (includes WebSocket support)
    await start_web_server()

    # Start telemetry broadcast
    await broadcast_telemetry()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[AC Dashboard] Shutting down...")
        telemetry_reader.cleanup()
