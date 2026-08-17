#!/usr/bin/env python3
# Copyright (c) 2026, Boxflat contributors
"""
Live axis monitor for the Moza AB6 — which physical control drives which axis.

The AB6's evdev axes carry racing names inherited from boxflat's shared map
(ABS_RZ is "brake", ABS_THROTTLE is "clutch", and so on), which say nothing
about what the control actually is on a flight stick. This watches the real
device and reports which axes move, so controls can be labelled from
evidence instead of guesswork.

Optionally also listens to the base's serial diagnostic log, where the
firmware names its own axes (axis_z, thumb_x, thumb_y, hall_button).

Read-only: it opens the input device for reading and never writes anything.

Usage:
    python3 tools/ab6_axes.py                 # watch axes for 20s
    python3 tools/ab6_axes.py --seconds 45
    python3 tools/ab6_axes.py --log           # also stream the firmware log
"""

import argparse
import glob
import os
import sys
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import evdev
except ImportError:
    sys.exit("python-evdev is required: pip install evdev")

# What each evdev axis is on the AB6, as far as the hardware inventory in
# AB6_STATUS.md allows. Confirm with this tool rather than trusting it.
LIKELY = {
    "ABS_X": "stick roll (left/right)",
    "ABS_Y": "stick pitch (fore/aft)",
    "ABS_Z": "?",
    "ABS_RX": "mini-stick X",
    "ABS_RY": "mini-stick Y",
    "ABS_RZ": "stick twist / yaw",
    "ABS_THROTTLE": "slider 1",
    "ABS_RUDDER": "slider 2",
    "ABS_HAT0X": "hat left/right",
    "ABS_HAT0Y": "hat up/down",
}

# The racing names boxflat currently maps these to, for cross-reference.
BOXFLAT_NAME = {
    "ABS_X": "steering",
    "ABS_Y": "combined",
    "ABS_Z": "throttle",
    "ABS_RX": "right_paddle",
    "ABS_RY": "left_paddle",
    "ABS_RZ": "brake",
    "ABS_THROTTLE": "clutch",
    "ABS_RUDDER": "handbrake",
    "ABS_HAT0X": "stick_x",
    "ABS_HAT0Y": "stick_y",
}


def find_device() -> evdev.InputDevice:
    for path in evdev.list_devices():
        device = evdev.InputDevice(path)
        if "ab6" in device.name.lower():
            return device
    sys.exit("No AB6 input device found")


def axis_name(code: int) -> str:
    name = evdev.ecodes.ABS[code]
    return name[0] if isinstance(name, list) else name


def stream_log(stop: threading.Event) -> None:
    """Print the firmware's own axis diagnostics as they arrive."""
    import serial

    matches = glob.glob("/dev/serial/by-id/*Gudsen*AB6*")
    if not matches:
        print("  (no serial node found, skipping firmware log)")
        return

    try:
        port = serial.Serial(matches[0], baudrate=115200, timeout=0.2)
    except Exception as error:
        print(f"  (serial log unavailable: {error})")
        return

    buffer = b""
    while not stop.is_set():
        chunk = port.read(256)
        if not chunk:
            continue
        buffer += chunk
        while b"\n" in buffer:
            line, buffer = buffer.split(b"\n", 1)
            text = "".join(chr(c) for c in line if 32 <= c < 127).strip()
            if text:
                print(f"  [fw] {text}")
    port.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--seconds", type=float, default=20.0,
                        help="how long to watch (default: 20)")
    parser.add_argument("--log", action="store_true",
                        help="also stream the firmware's diagnostic log")
    args = parser.parse_args()

    device = find_device()
    print(f"Watching: {device.name} ({device.path})")
    print(f"Move the controls. Listening for {args.seconds:g}s...\n")

    seen = {}
    stop = threading.Event()

    if args.log:
        threading.Thread(target=stream_log, args=[stop], daemon=True).start()

    deadline = time.monotonic() + args.seconds
    os.set_blocking(device.fileno(), False)

    while time.monotonic() < deadline:
        try:
            event = device.read_one()
        except BlockingIOError:
            event = None
        if event is None:
            time.sleep(0.002)
            continue
        if event.type != evdev.ecodes.EV_ABS:
            continue

        name = axis_name(event.code)
        record = seen.setdefault(name, {"min": event.value, "max": event.value, "count": 0})
        record["min"] = min(record["min"], event.value)
        record["max"] = max(record["max"], event.value)
        record["count"] += 1

    stop.set()
    time.sleep(0.3)

    if not seen:
        print("No axis movement detected.")
        return

    print("\n--- axes that moved ---")
    moved = {n: r for n, r in seen.items() if r["max"] > r["min"]}

    for name, record in sorted(moved.items(), key=lambda kv: -kv[1]["count"]):
        span = record["max"] - record["min"]
        print(f"  {name:14s} {record['min']:6d} … {record['max']:6d}  "
              f"span {span:6d}  events {record['count']:5d}")
        print(f"    {'boxflat name:':16s} {BOXFLAT_NAME.get(name, '-')}")
        print(f"    {'likely control:':16s} {LIKELY.get(name, '?')}")

    idle = sorted(set(seen) - set(moved))
    if idle:
        print(f"\n  reported but did not move: {', '.join(idle)}")


if __name__ == "__main__":
    main()
