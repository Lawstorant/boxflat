#!/usr/bin/env python3
# Copyright (c) 2026, Boxflat contributors
"""
AB6 command-group sweep — read-only protocol discovery for the Moza AB6.

The AB6 shares the Moza wire framing but not the racing command set. It
answers an unsupported request with a *framed* error that names the command
group it rejected:

    Stick Error Cmd: [main_cmd: 40]

That makes the firmware its own discovery oracle: sweep the group byte and
watch for the groups that stop producing that error. See AB6_STATUS.md.

Hand-built frames are silently ignored by the device, so every message here
is built through boxflat's own MozaCommand encoder.

SAFETY: this tool only ever sends READ requests. It never writes a setting.

Usage (from the repository root):

    python3 tools/ab6_sweep.py                  # sweep groups 0-255
    python3 tools/ab6_sweep.py --groups 32-96   # sweep a narrower range
    python3 tools/ab6_sweep.py --devices        # sweep device ids instead
    python3 tools/ab6_sweep.py --known 40       # try racing command ids in a group
"""

import argparse
import glob
import os
import sys
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import serial
except ImportError:
    sys.exit("pyserial is required: pip install pyserial")

import yaml

from boxflat.moza_command import MozaCommand, MOZA_COMMAND_READ

MESSAGE_START = 0x7E
MAGIC_VALUE = 13
DEFAULT_DEVICE_ID = 19

# Classification of a reply
REJECTED = "rejected"   # device answered "Stick Error" — group not supported
DATA = "data"           # framed reply carrying an actual payload
EMPTY = "empty"         # framed reply, zero-length payload: group exists, nothing returned
SILENT = "silent"       # no reply at all


def find_port() -> str:
    """Locate the AB6's by-id serial node."""
    matches = glob.glob("/dev/serial/by-id/*Gudsen*AB6*")
    if not matches:
        matches = glob.glob("/dev/serial/by-id/*Gudsen*")
    if not matches:
        sys.exit("No Gudsen serial device found under /dev/serial/by-id")
    return matches[0]


class Probe:
    def __init__(self, port: str, timeout: float, settle: float = 0.1):
        # The device can answer slower than a fixed sleep would allow. Waiting
        # for the reply instead of guessing prevents it being attributed to the
        # *next* request, which silently shifts every result by one.
        self._timeout = timeout
        self._settle = settle
        self._serial = serial.Serial(port, baudrate=115200, timeout=0.05)
        self._rx = []
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._reader, daemon=True)
        time.sleep(0.3)
        self._serial.reset_input_buffer()
        self._thread.start()

    def _reader(self):
        while not self._stop.is_set():
            try:
                chunk = self._serial.read(512)
            except (OSError, serial.SerialException):
                break
            if chunk:
                self._rx.append(chunk)

    def close(self):
        self._stop.set()
        time.sleep(0.3)
        self._serial.close()

    @staticmethod
    def build(group: int, device_id: int, cmd_id: int, payload_bytes: int = 2) -> bytes:
        """Build a correctly framed READ request via boxflat's own encoder."""
        spec = {
            "probe": {
                "id": [cmd_id],
                "read": group,
                # Never sent — a write group is required by the encoder.
                "write": group,
                "bytes": payload_bytes,
                "type": "int",
            }
        }
        command = MozaCommand()
        command.set_data_from_name("probe", {"ab6": spec}, "ab6")
        command.device_id = device_id
        command.set_payload(1)
        return command.prepare_message(MESSAGE_START, MOZA_COMMAND_READ, MAGIC_VALUE)

    def _drain(self) -> None:
        """Discard late replies from earlier requests, so attribution is clean."""
        while True:
            self._rx.clear()
            time.sleep(self._settle)
            if not self._rx:
                break
        self._serial.reset_input_buffer()
        self._rx.clear()

    def exchange(self, message: bytes) -> bytes:
        """Send one request and wait for its reply."""
        self._drain()
        self._serial.write(message)
        self._serial.flush()

        deadline = time.monotonic() + self._timeout
        while not self._rx and time.monotonic() < deadline:
            time.sleep(0.01)

        if not self._rx:
            return b""

        # Something arrived — give the rest of the frame time to land.
        time.sleep(self._settle)
        return b"".join(self._rx)


def classify(reply: bytes) -> tuple:
    """Return (kind, detail) for a reply blob.

    A reply frame is: 0x7e | length | group | device-id | payload | checksum,
    where the group has bit 7 set to mark it as a response. Distinguishing a
    zero-length acknowledgment from a real payload matters: an empty reply
    means the group exists but returned nothing, which is a very different
    signal from the device rejecting the group outright.
    """
    if not reply:
        return SILENT, ""

    if b"Error" in reply:
        text = "".join(chr(c) if 32 <= c < 127 else "." for c in reply)
        start = text.find("Stick")
        return REJECTED, text[start:].strip(".") if start != -1 else text.strip(".")

    if len(reply) >= 4 and reply[0] == MESSAGE_START:
        length = reply[1]
        group = reply[2] & 0x7F
        device_id = reply[3]
        if length == 0:
            return EMPTY, f"group {group}, device {device_id}"
        payload = reply[4:4 + length]
        return DATA, f"group {group}, device {device_id}, payload {payload.hex(':')}"

    return DATA, reply.hex(":")


def sweep_groups(probe: Probe, groups: range, device_id: int) -> dict:
    print(f"Sweeping groups {groups.start}-{groups.stop - 1} at device id {device_id}\n")
    results = {REJECTED: [], DATA: [], EMPTY: [], SILENT: []}

    for group in groups:
        message = probe.build(group, device_id, cmd_id=1)
        kind, detail = classify(probe.exchange(message))
        results[kind].append((group, detail))

        if kind != SILENT:
            print(f"  group {group:3d} (0x{group:02x})  {kind:8s}  {detail}")

    return results


def sweep_devices(probe: Probe, group: int) -> None:
    print(f"Sweeping device ids 0-255 using group {group}\n")
    for device_id in range(256):
        message = probe.build(group, device_id, cmd_id=1)
        kind, detail = classify(probe.exchange(message))
        if kind != SILENT:
            print(f"  device {device_id:3d} (0x{device_id:02x})  {kind:8s}  {detail}")


def try_known_ids(probe: Probe, group: int, device_id: int, serial_yml: str) -> None:
    """Test the hypothesis that MOZA reused racing command ids in a new group."""
    with open(serial_yml) as stream:
        data = yaml.safe_load(stream)

    base = data["commands"]["base"]
    print(f"Trying {len(base)} racing 'base' command ids in group {group} "
          f"at device id {device_id}\n")

    for name, spec in base.items():
        ids = list(spec["id"])
        if len(ids) != 1:
            continue
        message = probe.build(group, device_id, ids[0], int(spec["bytes"]))
        kind, detail = classify(probe.exchange(message))
        if kind == DATA:
            print(f"  {name:28s} id={ids[0]:3d}  DATA  {detail}")
        elif kind == REJECTED:
            print(f"  {name:28s} id={ids[0]:3d}  rejected")


def parse_range(text: str) -> range:
    if "-" in text:
        low, high = text.split("-", 1)
        return range(int(low), int(high) + 1)
    value = int(text)
    return range(value, value + 1)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--port", help="serial port (default: autodetect the AB6)")
    parser.add_argument("--groups", default="0-255",
                        help="group range to sweep, e.g. 32-96 (default: 0-255)")
    parser.add_argument("--device-id", type=int, default=DEFAULT_DEVICE_ID,
                        help=f"device id to address (default: {DEFAULT_DEVICE_ID})")
    parser.add_argument("--devices", action="store_true",
                        help="sweep device ids instead of groups")
    parser.add_argument("--known", type=int, metavar="GROUP",
                        help="try the racing 'base' command ids inside GROUP")
    parser.add_argument("--timeout", type=float, default=0.5,
                        help="how long to wait for a reply (default: 0.5s)")
    parser.add_argument("--data-path", default="data",
                        help="path to the data directory (default: data)")
    args = parser.parse_args()

    port = args.port or find_port()
    print(f"Port: {port}")
    print("Read-only: no setting is ever written.\n")

    probe = Probe(port, args.timeout)
    try:
        if args.devices:
            sweep_devices(probe, parse_range(args.groups).start)
        elif args.known is not None:
            try_known_ids(probe, args.known, args.device_id,
                          os.path.join(args.data_path, "serial.yml"))
        else:
            results = sweep_groups(probe, parse_range(args.groups), args.device_id)

            print("\n--- summary ---")
            print(f"  carried a payload  : {len(results[DATA])}")
            print(f"  empty ack          : {len(results[EMPTY])}")
            print(f"  rejected by device : {len(results[REJECTED])}")
            print(f"  silent             : {len(results[SILENT])}")

            accepted = results[DATA] + results[EMPTY]

            if results[DATA]:
                found = ", ".join(str(g) for g, _ in results[DATA])
                print(f"\nGroups returning real data: {found}")
                print("Next: python3 tools/ab6_sweep.py --known <group>")

            if results[EMPTY]:
                found = ", ".join(str(g) for g, _ in results[EMPTY])
                print(f"\nGroups the device accepts but answered empty: {found}")
                print("These exist — command id 1 is simply not one of theirs.")
                print("Next: python3 tools/ab6_sweep.py --known <group>")

            if not accepted:
                if results[REJECTED]:
                    print("\nEvery answered group was rejected. The device is talking, "
                          "so framing is right — widen the range or try --devices.")
                else:
                    print("\nNothing answered at all. Check that boxflat is not "
                          "running and holding the port.")
    except KeyboardInterrupt:
        print("\nInterrupted.")
    finally:
        probe.close()


if __name__ == "__main__":
    main()
