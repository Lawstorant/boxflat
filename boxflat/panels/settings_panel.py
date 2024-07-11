import time
from threading import Thread
from boxflat.widgets import *

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Gio, Adw

from boxflat.connection_manager import MozaConnectionManager

class SettingsPanel(object):
    _current_page = None
    _current_group = None
    _current_stack = None
    _current_row = None
    _header = None
    _rows = []

    def __init__(self, title: str, button_callback: callable, connection_manager: MozaConnectionManager=None) -> None:
        self._cm = connection_manager
        self._content = self._prepare_content()
        self._button = self._prepare_button(title, button_callback)
        self._banner = self._prepare_banner()
        self.prepare_ui()


    def _prepare_button(self, title, button_callback) -> Gtk.ToggleButton:
        button = Gtk.ToggleButton()
        button.set_css_classes(['sidebar-button'])
        button.connect("clicked", button_callback)
        button.set_halign(Gtk.Align.FILL)

        label = Gtk.Label(label=f"{title}")
        label.set_justify(Gtk.Justification.LEFT)
        label.set_xalign(0)
        button.set_child(label)
        return button


    def _prepare_content(self) -> Gtk.Box:
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        content.set_css_classes(['settings-pane'])
        self._header = Adw.HeaderBar()
        content.append(self._header)
        return content


    def _prepare_banner(self, title="Title", label="Hide") -> Adw.Banner:
        banner = Adw.Banner()
        banner.set_title(title)
        banner.set_button_label(label)
        banner.set_revealed(False)
        banner.connect("button-clicked", lambda b: self.hide_banner())
        self._content.append(banner)
        return banner

    def prepare_ui(self) -> None:
            return

    def set_setting(self, value) -> None:
        pass

    def get_setting(self) -> int:
        return 0

    def show_banner(self, value: bool=True) -> None:
        self._banner.set_revealed(value)

    def hide_banner(self, *arg) -> None:
        self._banner.set_revealed(False)

    def set_banner_title(self, new_title: str) -> None:
        self._banner.set_title(new_title)

    def apply(self, *arg) -> None:
        # self.hide_banner()
        print(f"Applying {self.title} settings...")

    @property
    def content(self) -> Gtk.Box:
        return self._content

    @property
    def button(self) -> Gtk.ToggleButton:
        return self._button

    @property
    def title(self) -> str:
        return self._button.get_child().get_label()


    def deactivate_button(self) -> None:
        self._button.set_active(False)


    def active(self, value: bool) -> None:
        for row in self._rows:
            row.set_active(value)

        self.set_banner_title("Device not detected")
        self.show_banner(not value)


    def open_url(self, url: str) -> None:
        launcher = Gtk.UriLauncher()
        launcher.set_uri(url)
        launcher.launch()


    def add_preferences_page(self, name="", icon="preferences-system-symbolic") -> None:
        page = Adw.PreferencesPage()
        self._current_page = page

        if self._current_stack == None:
            self._content.append(page)
        else:
            self._current_stack.add_titled_with_icon(page, name, name, icon)


    def add_preferences_group(self, title="", level_bar=False):
        if self._current_page == None:
            self.add_preferences_page()

        self._current_group = Adw.PreferencesGroup()
        self._current_group.set_title(title)
        self._current_page.add(self._current_group)

        if level_bar:
            bar = Gtk.LevelBar()
            bar.set_mode(Gtk.LevelBarMode.CONTINUOUS)
            bar.set_min_value(0)
            bar.set_max_value(1000)
            bar.set_value(250)
            bar.set_size_request(270,0)
            self._current_group.set_header_suffix(bar)


    def add_view_stack(self) -> None:
        stack = Adw.ViewStack()
        self._content.append(stack)
        self._current_stack = stack

        switcher = Adw.ViewSwitcher()
        switcher.set_stack(stack)
        switcher.set_policy(Adw.ViewSwitcherPolicy.WIDE)
        self._header.set_title_widget(switcher)


    def _add_row(self, row: BoxflatRow) -> None:
        if self._current_group == None:
            self.add_preferences_group()
        self._current_row = row
        self._current_group.add(row)
        self._rows.append(row)
