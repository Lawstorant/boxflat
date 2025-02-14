# Copyright (c) 2025, Tomasz Pakuła Using Arch BTW

from boxflat.widgets import *
from gi.repository import Gtk, Adw

from boxflat.connection_manager import MozaConnectionManager
from boxflat.hid_handler import HidHandler, MozaAxis
from boxflat.subscription import EventDispatcher

class SettingsPanel(EventDispatcher):
    def __init__(self, title: str, button_callback,
                 connection_manager: MozaConnectionManager=None,
                 hid_handler: HidHandler=None):
        super().__init__()

        self._cm = connection_manager
        self._hid_handler = hid_handler
        self._application = None

        self._current_page: Adw.PreferencesPage = None
        self._current_group: BoxflatPreferencesGroup = None
        self._current_stack: Adw.ViewStack = None
        self._current_row: BoxflatRow = None

        self._groups: list[BoxflatPreferencesGroup] = []

        self._active = True
        self._shutdown = False

        self._banner = self._prepare_banner()
        self._content = Adw.ToastOverlay(vexpand=True)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.append(self._banner)
        box.append(self._content)

        self._toolbar = self._prepare_toolbar()
        self._toolbar.set_content(box)

        self._page = Adw.NavigationPage(title=title, child=self._toolbar)
        self._page.set_size_request(720,0)
        self._button = self._prepare_button(title, button_callback)
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


    def _prepare_toolbar(self) -> Adw.ToolbarView:
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
        banner.connect("button-clicked", lambda *_: self.hide_banner())
        return banner


    def prepare_ui(self):
        return

    def set_setting(self, value):
        pass

    def get_setting(self) -> int:
        return 0

    def set_application(self, application: Adw.Application) -> None:
        self._application = application

    def show_banner(self, value: bool=True):
        GLib.idle_add(self._banner.set_revealed, value)

    def hide_banner(self, *arg):
        GLib.idle_add(self._banner.set_revealed, False)

    def set_banner_title(self, new_title: str):
        self._banner.set_title(new_title)

    def set_banner_label(self, new_label: str):
        self._banner.set_button_label(new_label)

    def show_toast(self, title: str, timeout=0):
        GLib.idle_add(self._content.add_toast, Adw.Toast(title=title, timeout=timeout))

    def apply(self, *arg):
        # self.hide_banner()
        print(f"Applying {self.title} settings...")

    @property
    def content(self) -> Adw.NavigationPage:
        return self._page

    @property
    def button(self) -> Gtk.ToggleButton:
        return self._button

    @property
    def title(self) -> str:
        return self._button.get_child().get_label()


    def deactivate_button(self):
        self._button.set_active(False)


    def active(self, value: int):
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


    def open_url(self, url: str):
        launcher = Gtk.UriLauncher()
        launcher.set_uri(url)
        launcher.launch()


    def add_preferences_page(self, name="", icon="preferences-system-symbolic"):
        page = Adw.PreferencesPage()
        self._current_page = page

        if self._current_stack is None:
            self._content.set_child(page)
        else:
            self._current_stack.add_titled_with_icon(page, name, name, icon)


    def add_preferences_group(self, title="", level_bar=False, alt_level_bar=False, suffix=None):
        if self._current_page is None:
            self.add_preferences_page()

        self._current_group = BoxflatPreferencesGroup(title, level_bar, alt_level_bar, suffix)
        self._current_group.set_bar_width(290)
        self._current_page.add(self._current_group)
        self._groups.append(self._current_group)


    def remove_preferences_group(self, group: Adw.PreferencesGroup):
        if not group:
            return
        self._groups.remove(group)
        GLib.idle_add(self._current_page.remove, group)


    def add_view_stack(self):
        stack = Adw.ViewStack()
        self._content.set_child(stack)
        self._current_stack = stack

        switcher = Adw.ViewSwitcher()
        switcher.set_stack(stack)
        switcher.set_policy(Adw.ViewSwitcherPolicy.WIDE)
        self._header.set_title_widget(switcher)


    def _add_row(self, row: BoxflatRow):
        if self._current_group is None:
            self.add_preferences_group()
        self._current_row = row

        if isinstance(row, BoxflatRow):
            row.set_width(620)

        elif isinstance(row, Adw.PreferencesRow):
            row.set_size_request(620, 0)

        GLib.idle_add(self._current_group.add, row)

    # def deactivate_hid_subs(self):
    #     if not self._hid_handler:
    #         return

    #     self._hid_handler.shutdown()
    #     self._hid_handler = None


    def shutdown(self, *args):
        self._shutdown = True
