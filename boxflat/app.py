# Copyright (c) 2024, Tomasz Pakuła Using Arch BTW

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
gi.require_version("Xdp", "1.0")
gi.require_version("XdpGtk4", "1.0")

from gi.repository import Gtk, Gdk, Adw
from boxflat.panels import *
from boxflat.connection_manager import MozaConnectionManager
from boxflat.hid_handler import HidHandler
from boxflat.settings_handler import SettingsHandler
import os
import shutil



class MainWindow(Adw.ApplicationWindow):
    def __init__(self, navigation: Adw.NavigationSplitView):
        super().__init__()
        self.set_default_size(0, 850)
        self.set_title("Boxflat")
        self.set_content(navigation)



class MyApp(Adw.Application):
    def __init__(self, data_path: str, config_path: str, dry_run: bool, custom: bool, autostart: bool,**kwargs):
        super().__init__(**kwargs)
        self.connect('activate', self.on_activate)

        css_provider = Gtk.CssProvider()
        css_provider.load_from_path(f"{data_path}/style.css")
        Gtk.StyleContext.add_provider_for_display(Gdk.Display.get_default(), css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        self._settings = SettingsHandler(config_path)
        self._hid_handler = HidHandler()
        self._config_path = config_path

        self._cm = MozaConnectionManager(os.path.join(data_path, "serial.yml"), dry_run)
        self._cm.subscribe("hid-device-connected", self._hid_handler.add_device)

        if self._settings.read_setting("background"):
            self.hold()

        with open(os.path.join(data_path, "version"), "r") as version:
            self._version = version.readline().strip()

        self._panels: dict[str, SettingsPanel] = {}
        self._dry_run = dry_run
        self._autostart = autostart

        # self.search_btn = Gtk.ToggleButton()  # Search Button
        # self.search_btn.set_icon_name("edit-find-symbolic")
        # self.search_btn.bind_property("active", self.searchbar, "search-mode-enabled",
        #                               GObject.BindingFlags.BIDIRECTIONAL)
        # self.search_btn.set_valign(Gtk.Align.CENTER)
        # self.search_btn.add_css_class("image-button")
        # left_header.pack_start(self.search_btn)

        navigation = Adw.NavigationSplitView()
        navigation.set_max_sidebar_width(178)
        navigation.set_min_sidebar_width(178)

        box2 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        left = Adw.ToolbarView()
        left.add_top_bar(Adw.HeaderBar())
        left.set_content(box2)

        sidebar = Adw.NavigationPage()
        sidebar.set_title("Boxflat")
        sidebar.set_child(left)

        navigation.set_sidebar(sidebar)
        navigation.set_content(Adw.NavigationPage(title="whatever"))

        self.navigation = navigation

        self._prepare_settings()
        if custom:
            self._panels["Other"].enable_custom_commands()

        buttons = self._panel_buttons()
        for button in buttons:
            if button is not buttons[0]:
                button.set_group(buttons[0])
            box2.append(button)

        navigation.set_content(self._activate_default().content)

        udev_alert_body = "alert"

        with open(os.path.join(data_path, "udev-warning.txt"), "r") as file:
            udev_alert_body = "\n" + file.read().strip()

        self._alert = Adw.AlertDialog()
        self._alert.set_body(udev_alert_body)
        self._alert.add_response("guide", "Guide")
        self._alert.add_response("close", "Close")

        self._alert.set_response_appearance("guide", Adw.ResponseAppearance.SUGGESTED)
        self._alert.set_response_appearance("close", Adw.ResponseAppearance.DESTRUCTIVE)
        self._alert.set_close_response("close")
        self._alert.set_heading("No udev rules detected!")
        self._alert.set_body_use_markup(True)
        self._alert.connect("response", self._handle_udev_dialog)

        self._cm.subscribe("no-accesss", self.show_udev_dialog)
        self._cm.subscribe("estop-receive-status", self._cm.set_setting, "base-ffb-disable")


    def on_activate(self, app):
        autostart = self._autostart
        self._autostart = False

        hidden = self._settings.read_setting("autostart-hidden") or 0
        background = self._settings.read_setting("background") or 0

        if autostart and hidden and background:
            return

        win = MainWindow(self.navigation)
        win.set_application(app)
        win.present()


    def switch_panel(self, button):
        new_title = button.get_child().get_label()
        new_content = self._panels[new_title].content

        if self.navigation.get_content() == new_content:
            return

        self.navigation.set_content(new_content)


    def set_content_title(self, title: str):
        self.navigation.get_content().set_title(title)


    def show_udev_dialog(self):
        self._alert.choose()


    def _handle_udev_dialog(self, dialog, response):
        if response == "guide":
            self.open_url("https://github.com/Lawstorant/boxflat?tab=readme-ov-file#udev-rule-installation-for-flatpak")


    def open_url(self, url: str):
        launcher = Gtk.UriLauncher()
        launcher.set_uri(url)
        launcher.launch()


    def _prepare_settings(self):
        self._panels["Home"] = HomeSettings(self.switch_panel, self._dry_run, self._cm, self._hid_handler, self._version)
        self._panels["Base"] = BaseSettings(self.switch_panel, self._cm, self._hid_handler)
        self._panels["Wheel"] = WheelSettings(self.switch_panel, self._cm, self._hid_handler, self._settings)
        self._panels["Pedals"] = PedalsSettings(self.switch_panel, self._cm, self._hid_handler)
        self._panels["H-Pattern Shifter"] = HPatternSettings(self.switch_panel, self._cm, self._settings)
        self._panels["Sequential Shifter"] = SequentialSettings(self.switch_panel, self._cm)
        self._panels["Handbrake"] = HandbrakeSettings(self.switch_panel, self._cm, self._hid_handler)
        self._panels["Other"] = OtherSettings(self.switch_panel, self._cm, self._hid_handler, self._settings, self._version, self)
        self._panels["Presets"] = PresetSettings(self.switch_panel, self._cm, self._settings)
        self._panels["Presets"].set_application(self)

        self._panels["Other"].subscribe("brake-calibration-enabled", self._panels["Pedals"].set_brake_calibration_active)
        self._panels["Pedals"].set_brake_calibration_active(self._panels["Other"].get_brake_valibration_enabled())

        for panel in self._panels.values():
            panel.active(-2)

        self._panels["Home"].active(1)
        self._panels["Other"].active(1)
        self._panels["Presets"].active(1)

        if self._dry_run:
            print("Dry run")
            return

        self._cm.set_write_active()


    def _shutdown(self, *_) -> None:
        for panel in self._panels.values():
            panel.shutdown()

        self._cm.shutdown()


    def _activate_default(self) -> SettingsPanel:
        self._panels["Home"].button.set_active(True)
        return self._panels["Home"]


    def _panel_buttons(self) -> list[Gtk.Button]:
        buttons: list[Gtk.Button] = []
        for panel in self._panels.values():
            buttons.append(panel.button)

        return buttons
