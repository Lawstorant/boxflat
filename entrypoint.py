#!/usr/bin/env python3

import sys
import boxflat.app as app
import argparse
import os
import shutil

parser = argparse.ArgumentParser("boxflat")
parser.add_argument("--local", help="Run boxflat from repository folder", action="store_true", required=False)
parser.add_argument("--dry-run", help="Don't send any data to the serial devices", action="store_true", required=False)
parser.add_argument("--data-path", help="Use arbitrary data path", type=str, required=False)
parser.add_argument("--flatpak", help="for flatpak usage", action="store_true", required=False)
args = parser.parse_args()

data_path = "/usr/share/boxflat/data"
udev_warn = not os.path.isfile("/etc/udev/rules.d/99-boxflat.rules")

if args.data_path:
    data_path = args.data_path
    print(f"Data path: {args.data_path}")

if args.local:
    data_path = "data"

if args.flatpak:
    data_path = "/app/share/boxflat/data"
    udev_warn = not os.path.isfile("/run/host/etc/udev/rules.d/99-boxflat.rules")

app = app.MyApp(data_path, args.dry_run,  udev_warn, application_id="io.github.lawstorant.boxflat")
app.run()
