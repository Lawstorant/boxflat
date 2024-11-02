#!/usr/bin/env python3
# Copyright (c) 2024, Tomasz Pakuła Using Arch BTW

import boxflat.app as app
import argparse
import os

parser = argparse.ArgumentParser("boxflat")
parser.add_argument("--local", help="Run boxflat from repository folder", action="store_true", required=False)
parser.add_argument("--dry-run", help="Don't send any data to the serial devices", action="store_true", required=False)
parser.add_argument("--data-path", help="Use arbitrary data path", type=str, required=False)
parser.add_argument("--flatpak", help="for flatpak usage", action="store_true", required=False)
parser.add_argument("--custom", help="Enable custom commands entry", action="store_true", required=False)
parser.add_argument("--autostart", help="For the autostart handling", action="store_true", required=False)
args = parser.parse_args()

data_path = "/usr/share/boxflat/data"
config_path = "~/.config/boxflat/"
os.environ["BOXFLAT_FLATPAK_EDITION"] = "false"

if args.data_path:
    data_path = args.data_path
    print(f"Data path: {args.data_path}")

if args.local:
    data_path = "data"

if args.flatpak:
    data_path = "/app/share/boxflat/data"
    os.environ["BOXFLAT_FLATPAK_EDITION"] = "true"

app.MyApp(data_path,
    config_path,
    args.dry_run,
    args.custom,
    args.autostart,
    application_id="io.github.lawstorant.boxflat"
).run()
