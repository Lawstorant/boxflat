#!/usr/bin/env python3
# Copyright (c) 2026, Boxflat contributors
"""
Decode a USBPcap capture of MOZA Cockpit talking to the AB6 on Windows.

Requires `tshark` (part of Wireshark) on PATH. Locates the AB6 automatically
by its USB VID:PID (346e:1002) - no manual endpoint/device-address filtering
needed.

Frame format (see moza-protocol.md, AB6_STATUS.md):

    0x7e | length | group | device-id | [cmd-id + payload] (length bytes) | checksum

Two different framing conventions appear on the wire:

- Synchronous command replies set bit 7 on the group byte, and the
  device-id nibbles are swapped (see boxflat/bitwise.py). Both are undone
  here to recover the plain group/device-id used in requests.
- The AB6's asynchronous diagnostic log (group 14, cmd id 5) is a *push*,
  not a reply to a specific read: its group byte is NOT bit7-toggled. Code
  that assumes uniform toggling misreads this stream as "group 142" - see
  the note in AB6_STATUS.md for how this was found.

Usage:

    python3 tools/ab6_pcap_decode.py capture.pcapng
    python3 tools/ab6_pcap_decode.py capture.pcapng --out-dir captures/my-session
"""

import argparse
import os
import re
import subprocess
import sys
from collections import defaultdict

AB6_VID_PID = "346e:1002"


def run_tshark(pcap_path: str) -> list[tuple[int, float, str, bytes]]:
    """Extract (frame_no, time, src, bytes) for the AB6's CDC data frames."""
    vid, pid = AB6_VID_PID.split(":")

    find_addr = subprocess.run(
        ["tshark", "-r", pcap_path, "-Y", f"usb.idVendor==0x{vid} && usb.idProduct==0x{pid}",
         "-T", "fields", "-e", "usb.device_address"],
        capture_output=True, text=True, check=True,
    )
    addresses = sorted(set(a for a in find_addr.stdout.split() if a))
    if not addresses:
        sys.exit(f"No USB device {AB6_VID_PID} found in {pcap_path}")
    if len(addresses) > 1:
        print(f"Warning: device {AB6_VID_PID} seen at multiple addresses "
              f"{addresses}; using {addresses[0]} (it may have re-enumerated)")
    address = addresses[0]

    result = subprocess.run(
        ["tshark", "-r", pcap_path, "-Y", f"usb.device_address=={address} && usb.capdata",
         "-T", "fields", "-e", "frame.number", "-e", "frame.time_relative",
         "-e", "usb.src", "-e", "usb.capdata"],
        capture_output=True, text=True, check=True,
    )

    entries = []
    for line in result.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) != 4 or not parts[3]:
            continue
        frame_no, t, src, hexstr = parts
        entries.append((int(frame_no), float(t), src, bytes.fromhex(hexstr)))
    return entries


def swap_nibbles(value: int) -> int:
    return ((value & 0x0F) << 4) | ((value & 0xF0) >> 4)


def toggle_bit(value: int, bit: int) -> int:
    return value ^ (1 << bit)


def split_directions(entries):
    host_to_dev, dev_to_host = [], []
    for frame_no, t, src, data in entries:
        (host_to_dev if src == "host" else dev_to_host).append((frame_no, t, data))
    return host_to_dev, dev_to_host


def parse_frames(entries):
    """Greedy stream parser: concatenate one direction's bytes and split on
    the 0x7e | length framing. Each frame keeps the (frame_no, time) of the
    USB transfer it started in, for chronological attribution."""
    blob = bytearray()
    marks = []
    for frame_no, t, data in entries:
        marks.append((len(blob), frame_no, t))
        blob.extend(data)

    frames = []
    i, n, mark_idx = 0, len(blob), 0
    while i < n:
        if blob[i] != 0x7E:
            i += 1
            continue
        if i + 1 >= n:
            break
        length = blob[i + 1]
        frame_len = 5 + length
        if i + frame_len > n:
            break
        raw = bytes(blob[i:i + frame_len])

        while mark_idx + 1 < len(marks) and marks[mark_idx + 1][0] <= i:
            mark_idx += 1
        frame_no, t = marks[mark_idx][1], marks[mark_idx][2]

        frames.append({
            "frame_no": frame_no, "time": t, "raw": raw, "length": length,
            "group_raw": raw[2], "device_raw": raw[3],
            "id_payload": raw[4:4 + length], "checksum": raw[4 + length],
        })
        i += frame_len
    return frames


def ascii_preview(data: bytes) -> str:
    return "".join(chr(c) if 32 <= c < 127 else "." for c in data)


def reassemble_diagnostic_log(resp_frames) -> dict[int, str]:
    """The diagnostic log (group 14, cmd id 5) is an async push: its group
    byte is the plain value 14, not toggled like a reply. One physical log
    line is usually split across several frames."""
    fragments = defaultdict(list)
    for f in resp_frames:
        if f["group_raw"] != 14:
            continue
        device = swap_nibbles(f["device_raw"])
        payload = f["id_payload"]
        if not payload or payload[0] != 5:
            continue
        fragments[device].append(payload[1:].decode("latin1", errors="replace"))
    return {device: "".join(parts) for device, parts in fragments.items()}


PARAM_WRITE_RE = re.compile(r"Table (\d+), Param (\d+) Written: (-?\d+) (-?[\d.]+)")


def extract_param_writes(logs: dict[int, str]) -> list[tuple[int, int, int, int, str]]:
    rows = []
    for device, text in logs.items():
        for m in PARAM_WRITE_RE.finditer(text):
            table, param, raw, fval = m.groups()
            rows.append((device, int(table), int(param), int(raw), fval))
    return rows


def summarize_binary_traffic(req_frames, resp_frames, out) -> None:
    def describe_request(f):
        # Requests carry group/device-id raw - no nibble swap. Only replies
        # (see describe_reply below) get that transform.
        group, device = f["group_raw"], f["device_raw"]
        p = f["id_payload"]
        return group, device, (p[0] if p else None)

    def describe_reply(f):
        # Only meaningful for frames with bit 7 actually set (true replies).
        group = toggle_bit(f["group_raw"], 7)
        device = swap_nibbles(f["device_raw"])
        p = f["id_payload"]
        return group, device, (p[0] if p else None)

    print("=== Requests (host -> AB6), grouped ===\n", file=out)
    groups = defaultdict(list)
    for f in req_frames:
        g, d, cmd_id = describe_request(f)
        groups[(g, d)].append(cmd_id)
    for (g, d), ids in sorted(groups.items()):
        distinct = sorted({i for i in ids if i is not None})
        print(f"  group={g:3d} (0x{g:02x})  device={d:3d}  n={len(ids):4d}  ids={distinct}",
              file=out)

    print("\n=== Replies with the reply-marker bit set (device -> host) ===\n", file=out)
    groups = defaultdict(list)
    for f in resp_frames:
        if not (f["group_raw"] & 0x80):
            continue
        g, d, cmd_id = describe_reply(f)
        groups[(g, d)].append(cmd_id)
    for (g, d), ids in sorted(groups.items()):
        distinct = sorted({i for i in ids if i is not None})
        print(f"  group={g:3d} (0x{g:02x})  device={d:3d}  n={len(ids):4d}  ids={distinct}",
              file=out)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                      formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("pcap", help="path to the .pcapng capture")
    parser.add_argument("--out-dir", default=".",
                         help="directory to write diag_log_*.txt and param_writes.csv into")
    args = parser.parse_args()

    entries = run_tshark(args.pcap)
    print(f"Extracted {len(entries)} CDC data frames from {args.pcap}")

    host_to_dev, dev_to_host = split_directions(entries)
    req_frames = parse_frames(host_to_dev)
    resp_frames = parse_frames(dev_to_host)
    print(f"Parsed {len(req_frames)} request frames, {len(resp_frames)} reply frames")

    os.makedirs(args.out_dir, exist_ok=True)

    logs = reassemble_diagnostic_log(resp_frames)
    for device, text in logs.items():
        path = os.path.join(args.out_dir, f"diag_log_device{device}.txt")
        with open(path, "w") as f:
            f.write(text)
        print(f"Wrote {path} ({len(text)} chars)")

    rows = extract_param_writes(logs)
    csv_path = os.path.join(args.out_dir, "param_writes.csv")
    with open(csv_path, "w") as f:
        f.write("device,table,param,raw_int32,float_value\n")
        for device, table, param, raw, fval in rows:
            f.write(f"{device},{table},{param},{raw},{fval}\n")
    print(f"Wrote {csv_path} ({len(rows)} param writes)")

    summary_path = os.path.join(args.out_dir, "binary_traffic_summary.txt")
    with open(summary_path, "w") as f:
        summarize_binary_traffic(req_frames, resp_frames, f)
    print(f"Wrote {summary_path}")


if __name__ == "__main__":
    main()
