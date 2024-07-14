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
        self.connect('close-request', lambda w: self._cm.shutdown())

        self._panels = {}
        self._dry_run = dry_run

        self.set_default_size(850, 800)
        self.set_title("Boxflat")

        left_header = Adw.HeaderBar()
        left_header.set_show_end_title_buttons(False)

        # self.search_btn = Gtk.ToggleButton()  # Search Button
        # self.search_btn.set_icon_name("edit-find-symbolic")
        # self.search_btn.bind_property("active", self.searchbar, "search-mode-enabled",
        #                               GObject.BindingFlags.BIDIRECTIONAL)
        # self.search_btn.set_valign(Gtk.Align.CENTER)
        # self.search_btn.add_css_class("image-button")
        # left_header.pack_start(self.search_btn)

        navigation = Adw.NavigationSplitView()
        navigation.set_max_sidebar_width(150)
        navigation.set_min_sidebar_width(150)

        sidebar = Adw.NavigationPage()
        sidebar.set_title("Boxflat")
        box2 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box2.append(left_header)
        sidebar.set_child(box2)

        content = Adw.NavigationPage()
        content.set_title("Whatever")
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        content_box2 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        content_box.append(content_box2)
        content.set_child(content_box)

        navigation.set_sidebar(sidebar)
        navigation.set_content(content)

        self.set_content(navigation)
        self.navigation = navigation
        self.settings_box = content_box2

        self._prepare_settings()

        for button in self._panel_buttons():
            box2.append(button)

        self.settings_box.append(self._activate_default().content)
        content.set_title("Home")


    def switch_panel(self, button) -> None:
        new_title = button.get_child().get_label()
        old_title = self.navigation.get_content().get_title()
        box = self.settings_box

        self._panels[old_title].deactivate_button()
        self.set_content_title(new_title)

        box.remove(Gtk.Widget.get_first_child(box))
        box.append(self._panels[new_title].content)


    def set_content_title(self, title: str) -> None:
        self.navigation.get_content().set_title(title)


    def _prepare_settings(self) -> None:
        self._panels["Home"] = HomeSettings(self.switch_panel, self._dry_run)
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

        # TODO: Add Dash,Hub and other settings pcm._device_discovery()

        if self._dry_run:
            print("Dry run")
            return

        self._cm.refresh()
        self._cm.set_rw_active(True)

    def _activate_default(self) -> SettingsPanel:
        for panel in self._panels.values():
            panel.button.set_active(False)

        self._panels["Home"].button.set_active(True)
        return self._panels["Home"]

    def _panel_buttons(self) -> list:
        buttons = []
        for panel in self._panels.values():
            buttons.append(panel.button)

        return buttons


class MyApp(Adw.Application):
    def __init__(self, data_path: str, dry_run: bool, resizable: bool, **kwargs):
        super().__init__(**kwargs)
        self.connect('activate', self.on_activate)
        self._data_path = data_path
        self._dry_run = dry_run
        self._resizable = resizable
        css_provider = Gtk.CssProvider()
        css_provider.load_from_path(f"{data_path}/style.css")
        Gtk.StyleContext.add_provider_for_display(Gdk.Display.get_default(), css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)


    def on_activate(self, app):
        self.win = MainWindow(self._data_path, self._dry_run, application=app)
        self.win.set_resizable(self._resizable)
        self.win.present()
