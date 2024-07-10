#!/usr/bin/env python3

import sys
import boxflat.app as app
import argparse

parser = argparse.ArgumentParser("boxflat")
parser.add_argument("--local", help="Run boxflat from repository folder", action="store_true", required=False)
args = parser.parse_args()

data_path = "/usr/share/boxflat/data"
if args.local:
    data_path = "data"

app = app.MyApp(data_path, application_id="com.lawstorant.boxflat")
app.run()
