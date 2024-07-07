#!/usr/bin/env python3

import sys
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gdk
from src.main import MyApp

css_provider = Gtk.CssProvider()
css_provider.load_from_path('style.css')
Gtk.StyleContext.add_provider_for_display(Gdk.Display.get_default(), css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

app = MyApp(application_id="com.lawstorant.boxflat")
app.run(sys.argv)
