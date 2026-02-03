# Copyright (c) 2025, Ryan Orth Using CachyOS BTW
# IPC handler for external program control

import socket
import os
import json
from threading import Thread, Event
from .subscription import EventDispatcher


class IpcHandler(EventDispatcher):
    """
    Handles IPC via TCP socket to allow external programs to control boxflat.

    TCP Socket: localhost:52845 (configurable, localhost-only for security)

    Protocol: JSON messages over TCP socket

    Commands:
    - {"command": "set_angle", "value": 900}       # Set steering lock to 900 degrees
    - {"command": "get_angle"}                     # Query current steering lock
    - {"command": "get_status"}                    # Get connection status
    - {"command": "list_presets"}                  # List available presets
    - {"command": "load_preset", "name": "GT3"}    # Load a preset

    Responses:
    - {"status": "ok", "value": ...}
    - {"status": "error", "message": "..."}
    """

    def __init__(self, connection_manager, settings_handler, tcp_port=52845):
        super().__init__()
        self._cm = connection_manager
        self._settings = settings_handler
        self._running = Event()
        self._tcp_socket = None
        self._tcp_port = tcp_port
        self._tcp_thread = None

        # Register events
        self._register_event("preset-loaded")
        print("[IPC] Event 'preset-loaded' registered")
    def start(self) -> bool:
        """Start the IPC handler thread."""
        if self._running.is_set():
            return True

        self._running.set()
        return self._start_tcp_socket()

    def _start_tcp_socket(self) -> bool:
        """Start the TCP socket listener (localhost only for security)."""
        try:
            self._tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            # Bind to localhost only for security
            self._tcp_socket.bind(('127.0.0.1', self._tcp_port))
            self._tcp_socket.listen(5)

            self._tcp_thread = Thread(target=self._listen_loop, daemon=True, name="IPC-TCP")
            self._tcp_thread.start()

            print(f"[IPC] Listening on localhost:{self._tcp_port}")
            return True

        except OSError as e:
            if e.errno == 98:  # Address already in use
                print(f"[IPC] Port {self._tcp_port} already in use (another boxflat instance running?)")
            else:
                print(f"[IPC] Failed to start: {e}")
            self._cleanup()
            return False

    def stop(self) -> None:
        """Stop the IPC handler."""
        self._running.clear()
        self._cleanup()

    def _cleanup(self) -> None:
        """Clean up socket resources."""
        if self._tcp_socket:
            try:
                self._tcp_socket.close()
            except:
                pass
            self._tcp_socket = None

    def _listen_loop(self) -> None:
        """Main loop that accepts TCP socket connections."""
        self._tcp_socket.settimeout(1.0)  # Check running flag periodically

        while self._running.is_set():
            try:
                conn, addr = self._tcp_socket.accept()
                # Verify connection is from localhost
                if addr[0] != '127.0.0.1':
                    print(f"[IPC] Rejected connection from {addr[0]}")
                    conn.close()
                    continue

                # Handle each connection in the same thread (they should be quick)
                self._handle_connection(conn)
            except socket.timeout:
                continue
            except OSError as e:
                if self._running.is_set():
                    print(f"[IPC] Accept error: {e}")
                break

    def _handle_connection(self, conn: socket.socket) -> None:
        """Handle a single client connection."""
        try:
            conn.settimeout(5.0)

            # Read the message (max 4KB)
            data = conn.recv(4096).decode('utf-8')
            if not data:
                return

            # Parse JSON command
            try:
                message = json.loads(data)
            except json.JSONDecodeError as e:
                response = {"status": "error", "message": f"Invalid JSON: {e}"}
                conn.sendall(json.dumps(response).encode('utf-8'))
                return

            # Process command
            response = self._process_command(message)

            # Send response
            conn.sendall(json.dumps(response).encode('utf-8'))

        except socket.timeout:
            print("[IPC] Client connection timeout")
        except Exception as e:
            print(f"[IPC] Error handling connection: {e}")
        finally:
            try:
                conn.close()
            except:
                pass

    def _process_command(self, message: dict) -> dict:
        """Process a command message and return a response."""
        command = message.get('command')

        if not command:
            return {"status": "error", "message": "Missing 'command' field"}

        if command == "set_angle":
            return self._cmd_set_angle(message)
        elif command == "get_angle":
            return self._cmd_get_angle(message)
        elif command == "get_status":
            return self._cmd_get_status(message)
        elif command == "list_presets":
            return self._cmd_list_presets(message)
        elif command == "load_preset":
            return self._cmd_load_preset(message)
        elif command == "ping":
            return {"status": "ok", "message": "pong"}
        else:
            return {"status": "error", "message": f"Unknown command: {command}"}

    def _cmd_set_angle(self, message: dict) -> dict:
        """Set the steering wheel rotation angle (steering lock)."""
        value = message.get('value')

        if value is None:
            return {"status": "error", "message": "Missing 'value' field"}

        try:
            angle = int(value)
            if angle < 90 or angle > 2700:
                return {"status": "error", "message": "Angle must be between 90 and 2700"}

            # Set both base-limit and base-max-angle (as done in base.py)
            self._cm.set_setting(angle // 2, "base-limit")
            self._cm.set_setting(angle // 2, "base-max-angle")

            return {"status": "ok", "value": angle, "message": f"Steering angle set to {angle}°"}

        except (ValueError, TypeError) as e:
            return {"status": "error", "message": f"Invalid value: {e}"}
        except Exception as e:
            return {"status": "error", "message": f"Failed to set angle: {e}"}

    def _cmd_get_angle(self, message: dict) -> dict:
        """Get the current steering wheel rotation angle."""
        try:
            # Query the current setting
            angle = self._cm.get_setting("base-limit")
            if angle is None:
                return {"status": "error", "message": "Base not connected or angle not available"}

            # The angle is stored as half the actual value
            actual_angle = angle * 2
            return {"status": "ok", "value": actual_angle, "message": f"Current angle: {actual_angle}°"}

        except Exception as e:
            return {"status": "error", "message": f"Failed to get angle: {e}"}

    def _cmd_get_status(self, message: dict) -> dict:
        """Get the connection status of devices."""
        try:
            # Check if base is connected by trying to get a setting
            base_connected = self._cm.get_setting("base-limit") is not None

            status = {
                "status": "ok",
                "base_connected": base_connected,
            }

            return status

        except Exception as e:
            return {"status": "error", "message": f"Failed to get status: {e}"}

    def _cmd_list_presets(self, message: dict) -> dict:
        """List available presets."""
        try:
            presets_path = os.path.join(self._settings.get_path(), "presets")

            if not os.path.exists(presets_path):
                return {"status": "ok", "presets": [], "message": "No presets directory found"}

            # List all .yml files in the presets directory
            preset_files = [f.removesuffix('.yml') for f in os.listdir(presets_path)
                           if f.endswith('.yml') and os.path.isfile(os.path.join(presets_path, f))]

            preset_files.sort()

            return {
                "status": "ok",
                "presets": preset_files,
                "count": len(preset_files),
                "message": f"Found {len(preset_files)} preset(s)"
            }

        except Exception as e:
            return {"status": "error", "message": f"Failed to list presets: {e}"}

    def _cmd_load_preset(self, message: dict) -> dict:
        """Load a preset by name."""
        preset_name = message.get('name')

        if not preset_name:
            return {"status": "error", "message": "Missing 'name' field"}

        try:
            from boxflat.preset_handler import MozaPresetHandler

            preset_name = preset_name.removesuffix('.yml')
            presets_path = os.path.join(self._settings.get_path(), "presets")

            # Check if preset exists
            preset_file = os.path.join(presets_path, f"{preset_name}.yml")
            if not os.path.isfile(preset_file):
                return {"status": "error", "message": f"Preset '{preset_name}' not found"}

            # Load the preset
            pm = MozaPresetHandler(self._cm)
            pm.set_path(presets_path)
            pm.set_name(preset_name)

            # Load preset without h-pattern and stalks settings (pass None)
            # These are UI-specific and not needed for IPC
            pm.load_preset(None, None)

            # Notify subscribers (e.g., UI) that a preset was loaded
            self._dispatch("preset-loaded", preset_name)

            return {
                "status": "ok",
                "preset": preset_name,
                "message": f"Loaded preset '{preset_name}'"
            }

        except Exception as e:
            return {"status": "error", "message": f"Failed to load preset: {e}"}
