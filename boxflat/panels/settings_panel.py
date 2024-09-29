from boxflat.widgets import *

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw

from boxflat.connection_manager import MozaConnectionManager
from boxflat.hid_handler import HidHandler, MozaAxis

class SettingsPanel(object):
    def __init__(self, title: str, button_callback: callable,
                 connection_manager: MozaConnectionManager=None,
                 hid_handler: HidHandler=None) -> None:
        self._cm = connection_manager

        self._current_page = None
        self._current_group: BoxflatPreferencesGroup=None
        self._current_stack = None
        self._current_row: BoxflatRow=None
        self._header = None

        self._groups = []
        self._cm_subs = []
        self._cm_subs_connected = []

        self._hid_subs = []
        self._hid_handler = hid_handler

        self._active = True
        self._shutdown = False

        self._content = self._prepare_content()
        self._toast_overlay = Adw.ToastOverlay()
        self._toast_overlay.set_child(self._content)
        self._page = Adw.NavigationPage(title=title, child=self._toast_overlay)
        self._page.set_size_request(720,0)
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
        # button.set_visible(False)
        return button


    def _prepare_content(self) -> Adw.ToolbarView:
        content = Adw.ToolbarView()
        self._header = Adw.HeaderBar()
        content.add_top_bar(self._header)
        content.set_css_classes(['settings-pane'])

        return content


    def _prepare_banner(self, title="Banner title", label="") -> Adw.Banner:
        banner = Adw.Banner()
        banner.set_title(title)
        banner.set_button_label(label)
        banner.set_revealed(False)
        banner.add_css_class("banner-disconnected")
        banner.connect("button-clicked", lambda b: self.hide_banner())
        self._content.add_top_bar(banner)
        return banner


    def prepare_ui(self) -> None:
        return

    def set_setting(self, value) -> None:
        pass

    def get_setting(self) -> int:
        return 0

    def show_banner(self, value: bool=True) -> None:
        GLib.idle_add(self._banner.set_revealed, value)

    def hide_banner(self, *arg) -> None:
        GLib.idle_add(self._banner.set_revealed, False)

    def set_banner_title(self, new_title: str) -> None:
        self._banner.set_title(new_title)

    def set_banner_label(self, new_label: str) -> None:
        self._banner.set_button_label(new_label)

    def show_toast(self, title: str, timeout=0):
        GLib.idle_add(self._toast_overlay.add_toast, Adw.Toast(title=title, timeout=timeout))

    def apply(self, *arg) -> None:
        # self.hide_banner()
        print(f"Applying {self.title} settings...")

    @property
    def content(self) -> Adw.ToolbarView:
        return self._page

    @property
    def button(self) -> Gtk.ToggleButton:
        return self._button

    @property
    def title(self) -> str:
        return self._button.get_child().get_label()


    def deactivate_button(self) -> None:
        self._button.set_active(False)


    def active(self, value: int) -> None:
        value = (value > -1)
        if value == self._active:
            return

        self._active = value
        self.set_banner_title("Device disconnected")
        self.set_banner_label("")
        self.show_banner(not value)

        for group in self._groups:
            group.set_sensitive(value)

        # self._button.set_visible(value)


    def open_url(self, url: str) -> None:
        launcher = Gtk.UriLauncher()
        launcher.set_uri(url)
        launcher.launch()


    def add_preferences_page(self, name="", icon="preferences-system-symbolic") -> None:
        page = Adw.PreferencesPage()
        self._current_page = page

        if self._current_stack == None:
            GLib.idle_add(self._content.set_content, page)
        else:
            self._current_stack.add_titled_with_icon(page, name, name, icon)


    def add_preferences_group(self, title="", level_bar=False, alt_level_bar=False):
        if self._current_page == None:
            self.add_preferences_page()

        self._current_group = BoxflatPreferencesGroup(title, level_bar, alt_level_bar)
        self._current_group.set_bar_width(290)
        self._current_page.add(self._current_group)
        self._groups.append(self._current_group)


    def remove_preferences_group(self, group: Adw.PreferencesGroup):
        if not group:
            return
        GLib.idle_add(self._remove_helper, group)


    def _remove_helper(self, group: Adw.PreferencesGroup):
        self._current_page.remove(group)
        self._groups.remove(group)


    def add_view_stack(self) -> None:
        stack = Adw.ViewStack()
        self._content.set_content(stack)
        self._current_stack = stack

        switcher = Adw.ViewSwitcher()
        switcher.set_stack(stack)
        switcher.set_policy(Adw.ViewSwitcherPolicy.WIDE)
        self._header.set_title_widget(switcher)


    def _add_row(self, row: BoxflatRow) -> None:
        if self._current_group == None:
            self.add_preferences_group()
        self._current_row = row

        if isinstance(row, BoxflatRow):
            row.set_width(620)

        GLib.idle_add(self._current_group.add, row)


    def _append_sub(self, *args):
        self._cm_subs.append(args)


    def _append_sub_connected(self, *args):
        self._cm_subs_connected.append(args)


    def _append_sub_hid(self, *args):
        self._hid_subs.append(args)


    def activate_subs(self) -> None:
        for sub in self._cm_subs:
            self._cm.subscribe(*sub)


    def activate_subs_connected(self) -> None:
        for sub in self._cm_subs_connected:
            self._cm.subscribe_connected(*sub)


    def activate_hid_subs(self) -> None:
        for sub in self._hid_subs:
            self._hid_handler.subscribe(*sub)


    # def deactivate_hid_subs(self) -> None:
    #     if not self._hid_handler:
    #         return

    #     self._hid_handler.shutdown()
    #     self._hid_handler = None


    def shutdown(self, *args) -> None:
        self._shutdown = True
