#!/usr/bin/env python3

import boxflat.app as app
import argparse

parser = argparse.ArgumentParser("boxflat")
parser.add_argument("--local", help="Run boxflat from repository folder", action="store_true", required=False)
parser.add_argument("--dry-run", help="Don't send any data to the serial devices", action="store_true", required=False)
parser.add_argument("--data-path", help="Use arbitrary data path", type=str, required=False)
parser.add_argument("--flatpak", help="for flatpak usage", action="store_true", required=False)
args = parser.parse_args()

data_path = "/usr/share/boxflat/data"
config_path = "~/.boxflat/"

if args.data_path:
    data_path = args.data_path
    print(f"Data path: {args.data_path}")

if args.local:
    data_path = "data"

if args.flatpak:
    data_path = "/app/share/boxflat/data"
    config_path = "~/.var/app/io.github.lawstorant.boxflat/.boxflat/"

app = app.MyApp(data_path, config_path, args.dry_run, application_id="io.github.lawstorant.boxflat")
app.run()
