#!/usr/bin/env python3
"""
Boxflat IPC Client

Example client for controlling boxflat via TCP socket.
Can be used as a standalone command-line tool or imported as a library.

Usage as command-line tool:
    ./boxflat_ipc_client.py set-angle 900
    ./boxflat_ipc_client.py get-angle
    ./boxflat_ipc_client.py load-preset GT3
    ./boxflat_ipc_client.py list-presets

Usage as library:
    from boxflat_ipc_client import BoxflatClient

    client = BoxflatClient()
    client.set_angle(900)
    angle = client.get_angle()
    client.load_preset("GT3")
"""

import socket
import json
import sys
from typing import Dict, Any


class BoxflatClient:
    """Client for communicating with boxflat via TCP socket."""

    def __init__(self, host: str = "127.0.0.1", port: int = 52845):
        """
        Initialize the client.

        Args:
            host: Host to connect to (default: 127.0.0.1)
            port: Port to connect to (default: 52845)
        """
        self.host = host
        self.port = port

    def _send_command(self, command: str, **kwargs) -> Dict[str, Any]:
        """
        Send a command to boxflat and return the response.

        Args:
            command: The command name
            **kwargs: Additional command parameters

        Returns:
            Response dictionary from boxflat

        Raises:
            ConnectionError: If cannot connect to boxflat
            RuntimeError: If command fails
        """
        message = {"command": command, **kwargs}

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5.0)
            sock.connect((self.host, self.port))

            # Send command
            sock.sendall(json.dumps(message).encode('utf-8'))

            # Receive response
            response_data = sock.recv(4096).decode('utf-8')
            response = json.loads(response_data)

            sock.close()

            if response.get('status') == 'error':
                raise RuntimeError(response.get('message', 'Unknown error'))

            return response

        except socket.error as e:
            raise ConnectionError(f"Cannot connect to boxflat at {self.host}:{self.port}: {e}. Is boxflat running?")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Invalid response from boxflat: {e}")

    def set_angle(self, angle: int) -> Dict[str, Any]:
        """
        Set the steering wheel rotation angle (steering lock).

        Args:
            angle: Angle in degrees (90-2700)

        Returns:
            Response dictionary with status

        Example:
            client.set_angle(900)  # Set to 900 degrees
        """
        return self._send_command("set_angle", value=angle)

    def get_angle(self) -> int:
        """
        Get the current steering wheel rotation angle.

        Returns:
            Current angle in degrees

        Example:
            angle = client.get_angle()
            print(f"Current steering lock: {angle}°")
        """
        response = self._send_command("get_angle")
        return response.get('value')

    def get_status(self) -> Dict[str, Any]:
        """
        Get the connection status of devices.

        Returns:
            Status dictionary with device connection info

        Example:
            status = client.get_status()
            if status['base_connected']:
                print("Base is connected")
        """
        return self._send_command("get_status")

    def list_presets(self) -> list:
        """
        List available presets.

        Returns:
            List of preset names

        Example:
            presets = client.list_presets()
            for preset in presets:
                print(f"- {preset}")
        """
        response = self._send_command("list_presets")
        return response.get('presets', [])

    def load_preset(self, name: str) -> Dict[str, Any]:
        """
        Load a preset by name.

        Args:
            name: Preset name (without .yml extension)

        Returns:
            Response dictionary with status

        Example:
            client.load_preset("GT3")
        """
        return self._send_command("load_preset", name=name)

    def ping(self) -> bool:
        """
        Ping boxflat to check if it's responding.

        Returns:
            True if boxflat responds

        Example:
            if client.ping():
                print("Boxflat is running")
        """
        try:
            response = self._send_command("ping")
            return response.get('status') == 'ok'
        except:
            return False


def main():
    """Command-line interface."""
    if len(sys.argv) < 2:
        print("Boxflat IPC Client")
        print()
        print("Usage:")
        print("  boxflat_ipc_client.py <command> [args]")
        print()
        print("Commands:")
        print("  set-angle <degrees> Set steering lock angle (90-2700)")
        print("  get-angle           Get current steering lock angle")
        print("  status              Get device connection status")
        print("  list-presets        List available presets")
        print("  load-preset <name>  Load a preset")
        print("  ping                Check if boxflat is running")
        print()
        print("Examples:")
        print("  boxflat_ipc_client.py set-angle 900")
        print("  boxflat_ipc_client.py load-preset GT3")
        print("  boxflat_ipc_client.py get-angle")
        sys.exit(1)

    command = sys.argv[1]
    client = BoxflatClient()

    try:
        if command == "set-angle":
            if len(sys.argv) < 3:
                print("Error: Missing angle value")
                print("Usage: boxflat_ipc_client.py set-angle <degrees>")
                sys.exit(1)

            angle = int(sys.argv[2])
            response = client.set_angle(angle)
            print(f"✓ {response.get('message', 'Success')}")

        elif command == "get-angle":
            angle = client.get_angle()
            print(f"Current steering lock: {angle}°")

        elif command == "status":
            status = client.get_status()
            print("Device Status:")
            print(f"  Base connected: {status.get('base_connected', False)}")

        elif command == "list-presets":
            presets = client.list_presets()
            if presets:
                print(f"Available presets ({len(presets)}):")
                for preset in presets:
                    print(f"  • {preset}")
            else:
                print("No presets found")

        elif command == "load-preset":
            if len(sys.argv) < 3:
                print("Error: Missing preset name")
                print("Usage: boxflat_ipc_client.py load-preset <name>")
                sys.exit(1)

            preset_name = sys.argv[2]
            response = client.load_preset(preset_name)
            print(f"✓ {response.get('message', 'Success')}")

        elif command == "ping":
            if client.ping():
                print("✓ Boxflat is running")
            else:
                print("✗ Cannot reach boxflat")
                sys.exit(1)

        else:
            print(f"Error: Unknown command '{command}'")
            sys.exit(1)

    except ConnectionError as e:
        print(f"✗ Connection error: {e}")
        sys.exit(1)
    except RuntimeError as e:
        print(f"✗ Command failed: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"✗ Invalid value: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nInterrupted")
        sys.exit(130)


if __name__ == '__main__':
    main()
