#!/usr/bin/env python3

import sys
import boxflat.app as app
import argparse

parser = argparse.ArgumentParser("boxflat")
parser.add_argument("--local", help="Run boxflat from repository folder", action="store_true", required=False)
parser.add_argument("--dry-run", help="Don't send any data to the serial devices", action="store_true", required=False)
args = parser.parse_args()

data_path = "/usr/share/boxflat/data"
if args.local:
    data_path = "data"

app = app.MyApp(data_path, args.dry_run, application_id="com.lawstorant.boxflat")
app.run()
