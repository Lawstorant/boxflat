import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Gdk, Adw
from boxflat.panels import *
from boxflat.connection_manager import *
import os

class MainWindow(Adw.ApplicationWindow):
    def __init__(self, data_path: str, dry_run: bool, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._cm = MozaConnectionManager(os.path.join(data_path, "serial.yml"), dry_run)
        self._cm.device_discovery()
        self.connect('close-request', lambda w: self._cm.shutdown())

        with open(os.path.join(data_path, "version"), "r") as version:
            self._version = version.readline().strip()

        self._panels = {}
        self._dry_run = dry_run

        self.set_default_size(0, 800)
        self.set_title("Boxflat")

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

        self.set_content(navigation)
        self.navigation = navigation

        self._prepare_settings()

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

        self._cm.subscribe_no_access(self.show_udev_dialog)


    def switch_panel(self, button) -> None:
        self._cm.reset_subscriptions()
        new_title = button.get_child().get_label()

        self.navigation.set_content(self._panels[new_title].content)
        self._panels[new_title].activate_subs()


    def set_content_title(self, title: str) -> None:
        self.navigation.get_content().set_title(title)


    def show_udev_dialog(self) -> None:
        self._alert.choose()


    def _handle_udev_dialog(self, dialog, response):
        if response == "guide":
            self.open_url("https://github.com/Lawstorant/boxflat?tab=readme-ov-file#udev-rule-installation-for-flatpak")


    def open_url(self, url: str) -> None:
        launcher = Gtk.UriLauncher()
        launcher.set_uri(url)
        launcher.launch()


    def _prepare_settings(self) -> None:
        self._panels["Home"] = HomeSettings(self.switch_panel, self._dry_run, self._version)
        self._panels["Base"] = BaseSettings(self.switch_panel, self._cm)
        self._panels["Wheel"] = WheelSettings(self.switch_panel, self._cm)
        self._panels["Pedals"] = PedalsSettings(self.switch_panel, self._cm)
        self._panels["H-Pattern Shifter"] = HPatternSettings(self.switch_panel, self._cm)
        self._panels["Sequential Shifter"] = SequentialSettings(self.switch_panel, self._cm)
        self._panels["Handbrake"] = HandbrakeSettings(self.switch_panel, self._cm)
        self._panels["Other"] = OtherSettings(self.switch_panel, self._cm)

        self._panels["Other"].subscribe_brake_calibration(
            self._panels["Pedals"].set_brake_calibration_active
        )

        for panel in self._panels.values():
            panel.activate_subs()


        # TODO: Add Dash,Hub and other settings

        if self._dry_run:
            print("Dry run")
            return

        self._cm.set_rw_active(True)
        #self._cm.reset_subscriptions()


    def _activate_default(self) -> SettingsPanel:
        # for panel in self._panels.values():
        #     panel.button.set_active(False)

        self._panels["Home"].button.set_active(True)
        return self._panels["Home"]


    def _panel_buttons(self) -> list:
        buttons = []
        for panel in self._panels.values():
            buttons.append(panel.button)

        return buttons


class MyApp(Adw.Application):
    def __init__(self, data_path: str, dry_run: bool, **kwargs):
        super().__init__(**kwargs)
        self.connect('activate', self.on_activate)
        self._data_path = data_path
        self._dry_run = dry_run
        css_provider = Gtk.CssProvider()
        css_provider.load_from_path(f"{data_path}/style.css")
        Gtk.StyleContext.add_provider_for_display(Gdk.Display.get_default(), css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)


    def on_activate(self, app):
        self.win = MainWindow(self._data_path, self._dry_run, application=app)
        self.win.present()
