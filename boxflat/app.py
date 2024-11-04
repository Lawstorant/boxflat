# Copyright (c) 2024, Tomasz Pakuła Using Arch BTW

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')


from gi.repository import Gtk, Gdk, Adw
from boxflat.panels import *
from boxflat.connection_manager import MozaConnectionManager
from boxflat.hid_handler import HidHandler
from boxflat.settings_handler import SettingsHandler

import os
import subprocess


class MainWindow(Adw.ApplicationWindow):
    def __init__(self, navigation: Adw.NavigationSplitView):
        super().__init__()
        self.set_default_size(0, 850)
        self.set_title("Boxflat")
        self.set_content(navigation)


    def check_udev(self, data_path: str) -> None:
        command = ["ls" ,"/etc/udev/rules.d"]
        if os.environ["BOXFLAT_FLATPAK_EDITION"] == "true":
            command = ["flatpak-spawn", "--host", *command]

        rules = subprocess.check_output(command).decode()

        if "99-boxflat.rules" in rules:
            return

        udev_alert_body = "alert"

        with open(os.path.join(data_path, "udev-warning.txt"), "r") as file:
            udev_alert_body = "\n" + file.read().strip()

        alert = Adw.AlertDialog()
        alert.set_body(udev_alert_body)
        alert.add_response("guide", "Guide")
        alert.add_response("close", "Close")
        alert.set_size_request(400, 0)

        alert.set_response_appearance("guide", Adw.ResponseAppearance.SUGGESTED)
        alert.set_response_appearance("close", Adw.ResponseAppearance.DESTRUCTIVE)
        alert.set_close_response("close")

        alert.set_heading("No udev rules detected!")
        alert.set_body_use_markup(True)
        alert.connect("response", self._handle_udev_dialog)

        alert.choose(self)

        subprocess.check_output(command).decode()

        # subprocess.call(["sudo", "ls", "/etc"])


    def _handle_udev_dialog(self, dialog, response):
        if response != "guide":
            return
        url = "https://github.com/Lawstorant/boxflat?tab=readme-ov-file#udev-rule-installation-for-flatpak"
        Gtk.UriLauncher(uri=url).launch()


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
        self._data_path = data_path

        self._cm = MozaConnectionManager(os.path.join(data_path, "serial.yml"), dry_run)
        self._cm.subscribe("hid-device-connected", self._hid_handler.add_device)

        with open(os.path.join(data_path, "version"), "r") as version:
            self._version = version.readline().strip()

        self._panels: dict[str, SettingsPanel] = {}
        self._dry_run = dry_run
        self._autostart = autostart

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

        self._cm.subscribe("estop-receive-status", self._cm.set_setting, "base-ffb-disable")


    def on_activate(self, app):
        autostart = self._autostart
        self._autostart = False

        hidden = self._settings.read_setting("autostart-hidden") or 0
        background = self._settings.read_setting("background") or 0

        if autostart and hidden and background:
            self.hold()
            return

        win = MainWindow(self.navigation)
        win.set_application(app)
        win.present()
        win.check_udev(self._data_path)


    def switch_panel(self, button):
        new_title = button.get_child().get_label()
        new_content = self._panels[new_title].content

        if self.navigation.get_content() == new_content:
            return

        self.navigation.set_content(new_content)


    def set_content_title(self, title: str):
        self.navigation.get_content().set_title(title)


    def _prepare_settings(self):
        self._panels["Home"] = HomeSettings(self.switch_panel, self._dry_run, self._cm, self._hid_handler, self._version)
        self._panels["Base"] = BaseSettings(self.switch_panel, self._cm, self._hid_handler)
        self._panels["Wheel"] = WheelSettings(self.switch_panel, self._cm, self._hid_handler, self._settings)
        self._panels["Pedals"] = PedalsSettings(self.switch_panel, self._cm, self._hid_handler)
        self._panels["H-Pattern Shifter"] = HPatternSettings(self.switch_panel, self._cm, self._settings)
        self._panels["Sequential Shifter"] = SequentialSettings(self.switch_panel, self._cm)
        self._panels["Handbrake"] = HandbrakeSettings(self.switch_panel, self._cm, self._hid_handler)
        self._panels["Other"] = OtherSettings(
            self.switch_panel, self._cm, self._hid_handler, self._settings, self._version, self, self._data_path)

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
