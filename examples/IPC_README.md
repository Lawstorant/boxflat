# Boxflat IPC (Inter-Process Communication)

Boxflat supports external program control via TCP socket. This allows other applications (including Windows games running under Wine/Proton) to change settings like steering lock angle and load presets while boxflat is running.

## Connection

**TCP Socket:** `localhost:52845` (127.0.0.1:52845)
- Localhost-only for security
- Works from native Linux apps AND Wine/Proton games
- Standard TCP networking - compatible with any language

## Protocol

JSON messages over TCP socket.

### Request Format
```json
{
  "command": "command_name",
  "parameter": "value"
}
```

### Response Format
```json
{
  "status": "ok",
  "value": "result",
  "message": "optional message"
}
```

Or on error:
```json
{
  "status": "error",
  "message": "error description"
}
```

## Available Commands

### 1. Set Steering Lock Angle

Set the wheel rotation angle (steering lock) in degrees.

**Request:**
```json
{
  "command": "set_angle",
  "value": 900
}
```

**Parameters:**
- `value`: Integer between 90 and 2700 (degrees)

**Response:**
```json
{
  "status": "ok",
  "value": 900,
  "message": "Steering angle set to 900°"
}
```

### 2. Get Steering Lock Angle

Query the current wheel rotation angle.

**Request:**
```json
{
  "command": "get_angle"
}
```

**Response:**
```json
{
  "status": "ok",
  "value": 900,
  "message": "Current angle: 900°"
}
```

### 3. Get Device Status

Check if devices are connected.

**Request:**
```json
{
  "command": "get_status"
}
```

**Response:**
```json
{
  "status": "ok",
  "base_connected": true
}
```

### 4. List Presets

Get a list of available presets.

**Request:**
```json
{
  "command": "list_presets"
}
```

**Response:**
```json
{
  "status": "ok",
  "presets": ["GT3", "F1", "Rally", "Default"],
  "count": 4,
  "message": "Found 4 preset(s)"
}
```

### 5. Load Preset

Load a saved preset by name.

**Request:**
```json
{
  "command": "load_preset",
  "name": "GT3"
}
```

**Response:**
```json
{
  "status": "ok",
  "preset": "GT3",
  "message": "Loaded preset 'GT3'"
}
```

### 6. Ping

Check if boxflat is running and responding.

**Request:**
```json
{
  "command": "ping"
}
```

**Response:**
```json
{
  "status": "ok",
  "message": "pong"
}
```

## Using the Python Client

### Command Line

The provided `boxflat_ipc_client.py` script can be used from the command line:

```bash
./boxflat_ipc_client.py set-angle 900
./boxflat_ipc_client.py get-angle
./boxflat_ipc_client.py list-presets
./boxflat_ipc_client.py load-preset GT3
./boxflat_ipc_client.py status
./boxflat_ipc_client.py ping
```

### As a Python Library

Import and use the `BoxflatClient` class in your Python code:

```python
from boxflat_ipc_client import BoxflatClient

# Create client (connects to localhost:52845)
client = BoxflatClient()

# Check if boxflat is running
if not client.ping():
    print("Boxflat is not running!")
    exit(1)

# Set steering lock to 900 degrees
client.set_angle(900)

# Get current angle
angle = client.get_angle()
print(f"Current steering lock: {angle}°")

# List and load presets
presets = client.list_presets()
print(f"Available: {presets}")

client.load_preset("GT3")

# Check device status
status = client.get_status()
if status['base_connected']:
    print("Base is connected")
```

## Wine/Proton Integration

For Windows games running under Wine/Proton, use standard TCP networking:

```python
import socket
import json

def send_boxflat_command(command, **params):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("127.0.0.1", 52845))

    message = {"command": command, **params}
    sock.sendall(json.dumps(message).encode('utf-8'))

    response = sock.recv(4096).decode('utf-8')
    sock.close()
    return json.loads(response)

# Set angle manually
send_boxflat_command("set_angle", value=900)

# Or load a preset
send_boxflat_command("load_preset", name="GT3")

# List available presets
response = send_boxflat_command("list_presets")
print(f"Presets: {response['presets']}")
```

## Using from Other Languages

### Bash
```bash
echo '{"command":"set_angle","value":900}' | nc 127.0.0.1 52845
echo '{"command":"load_preset","name":"GT3"}' | nc 127.0.0.1 52845
echo '{"command":"get_angle"}' | nc 127.0.0.1 52845
```

### C/C++ (Windows - Wine/Proton)

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <winsock2.h>

#pragma comment(lib, "ws2_32.lib")

int boxflat_command(const char* json_command) {
    WSADATA wsa;
    SOCKET sock;
    struct sockaddr_in server;
    char buffer[4096];

    WSAStartup(MAKEWORD(2,2), &wsa);

    sock = socket(AF_INET, SOCK_STREAM, 0);

    server.sin_family = AF_INET;
    server.sin_addr.s_addr = inet_addr("127.0.0.1");
    server.sin_port = htons(52845);

    if (connect(sock, (struct sockaddr*)&server, sizeof(server)) < 0) {
        return -1;
    }

    send(sock, json_command, strlen(json_command), 0);

    int n = recv(sock, buffer, sizeof(buffer) - 1, 0);
    buffer[n] = '\0';
    printf("%s\n", buffer);

    closesocket(sock);
    WSACleanup();
    return 0;
}

// Usage in your game:
void OnCarSelected(const char* carName) {
    if (strcmp(carName, "F1") == 0) {
        boxflat_command("{\"command\":\"set_angle\",\"value\":360}");
    } else if (strcmp(carName, "GT3") == 0) {
        boxflat_command("{\"command\":\"load_preset\",\"name\":\"GT3\"}");
    } else {
        boxflat_command("{\"command\":\"set_angle\",\"value\":900}");
    }
}
```

### C# (Unity, etc.)

```csharp
using System.Net.Sockets;
using System.Text;

public static void SetBoxflatAngle(int angle) {
    TcpClient client = new TcpClient("127.0.0.1", 52845);
    string message = $"{{\"command\":\"set_angle\",\"value\":{angle}}}";
    byte[] data = Encoding.UTF8.GetBytes(message);
    client.GetStream().Write(data, 0, data.Length);

    byte[] response = new byte[4096];
    int bytes = client.GetStream().Read(response, 0, response.Length);
    string responseText = Encoding.UTF8.GetString(response, 0, bytes);
    client.Close();
}

public static void LoadBoxflatPreset(string presetName) {
    TcpClient client = new TcpClient("127.0.0.1", 52845);
    string message = $"{{\"command\":\"load_preset\",\"name\":\"{presetName}\"}}";
    byte[] data = Encoding.UTF8.GetBytes(message);
    client.GetStream().Write(data, 0, data.Length);
    client.Close();
}
```

### Lua (game mods)

```lua
local socket = require("socket")

function boxflat_command(cmd)
    local tcp = socket.tcp()
    tcp:connect("127.0.0.1", 52845)
    tcp:send(cmd)
    local response = tcp:receive("*a")
    tcp:close()
    return response
end

-- Usage
boxflat_command('{"command":"set_angle","value":900}')
boxflat_command('{"command":"load_preset","name":"GT3"}')
```

## Use Cases

1. **Game Integration**: Games or launchers automatically set steering lock based on car/track
2. **Wine/Proton Games**: Windows games control boxflat via standard TCP networking
3. **Profile Switching**: External profile managers change settings when switching between sims
4. **Automation**: Scripts automate boxflat configuration
5. **Third-party Tools**: Other tools extend boxflat's functionality

## Example: Automatic Preset Switching

### From Python Script
```python
#!/usr/bin/env python3
from boxflat_ipc_client import BoxflatClient

# Game-to-preset mapping
GAME_PRESETS = {
    "assettocorsa": "AC-GT3",
    "beamng": "BeamNG",
    "iracing": "iRacing-Oval",
    "dirt-rally": "Rally"
}

def launch_game_with_preset(game_name, game_command):
    client = BoxflatClient()

    if game_name in GAME_PRESETS:
        preset = GAME_PRESETS[game_name]
        print(f"Loading preset: {preset}")
        client.load_preset(preset)

    # Launch the game
    import subprocess
    subprocess.run(game_command)

# Usage
launch_game_with_preset("assettocorsa", ["steam", "steam://rungameid/244210"])
```

### From Bash Launcher
```bash
#!/bin/bash
# game_launcher.sh

load_preset_for_game() {
    case "$1" in
        "assettocorsa")
            echo '{"command":"load_preset","name":"AC-GT3"}' | nc 127.0.0.1 52845
            ;;
        "beamng")
            echo '{"command":"load_preset","name":"BeamNG"}' | nc 127.0.0.1 52845
            ;;
        "iracing")
            echo '{"command":"load_preset","name":"iRacing"}' | nc 127.0.0.1 52845
            ;;
    esac
}

# Load preset and launch game
load_preset_for_game "$1"
shift
exec "$@"
```

## Security Considerations

- TCP socket is bound to `127.0.0.1` only (localhost)
- Only local processes can connect
- No authentication required (local-only is considered sufficient)
- Consider security implications in multi-user systems

## Error Handling

Always check the response status:

```python
try:
    response = client.set_angle(900)
    if response['status'] == 'ok':
        print("Success!")
except ConnectionError:
    print("Cannot connect to boxflat - is it running?")
except RuntimeError as e:
    print(f"Command failed: {e}")
```

## Extending the IPC

To add new commands, edit `boxflat/ipc_handler.py`:

1. Add a new command handler method `_cmd_your_command()`
2. Add the command to `_process_command()`
3. Update this documentation

Example:
```python
def _cmd_your_command(self, message: dict) -> dict:
    """Handle your custom command."""
    # Your implementation
    return {"status": "ok", "message": "Done"}
```
