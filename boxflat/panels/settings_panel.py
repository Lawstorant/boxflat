import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Gio, Adw
from boxflat.structs import *
from boxflat.connection_manager import MozaConnectionManager
import time
from threading import Thread

class SettingsPanel(object):
    _current_page: Adw.PreferencesPage
    _current_group: Adw.PreferencesGroup
    _current_stack = None
    _header = None

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

    def _prepare_banner(self, title="Title", label="Label") -> Adw.Banner:
        banner = Adw.Banner()
        banner.set_title(title)
        banner.set_button_label(label)
        banner.set_revealed(False)
        banner.connect("button-clicked", self.apply)
        self._content.append(banner)
        return banner

    def prepare_ui(self) -> None:
            return

    def set_setting(self, value) -> None:
        pass

    def get_setting(self) -> int:
        return 0

    def show_banner(self, *arg) -> None:
        self._banner.set_revealed(True)

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

    def add_preferences_group(self, title: str, level_bar=False) -> None:
        if self._current_page != None:
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

    def add_title_row(self, title: str, subtitle="") -> None:
        if self._current_group == None:
            return

        row = Adw.ActionRow()
        row.set_title(title)
        row.set_subtitle(subtitle)

        self._current_group.add(row)

    def _slider_increment_handler(self, scale: Gtk.Scale, increment: int, callback) -> None:
        value = int(scale.get_value())
        modulo = value % increment

        if modulo != 0:
            scale.set_value(value + (increment - modulo))
        else:
            if callback != None:
                callback(value)

    def add_slider_row(self, title: str, range_start: int, range_stop: int,
                        value=0, size_request=(320,0), marks=[], mark_suffix="",
                        callback=None, increment=1, subtitle="", active=True) -> callable:

        if self._current_group == None:
            return

        slider = Gtk.Scale()
        slider.set_range(range_start, range_stop)
        slider.set_increments(increment, 0)
        slider.set_draw_value(True)
        slider.set_round_digits(0)
        slider.set_digits(0)
        slider.set_value(value)
        slider.set_size_request(size_request[0], size_request[1])
        slider.set_sensitive(active)

        marks.append(range_start)
        marks.append(range_stop)
        for mark in marks:
            slider.add_mark(mark, Gtk.PositionType.BOTTOM, f"{mark}{mark_suffix}")

        slider.connect('value-changed', lambda scale: self._slider_increment_handler(scale, increment, callback))

        row = Adw.ActionRow()
        row.add_suffix(slider)
        row.set_title(title)
        row.set_subtitle(subtitle)
        self._current_group.add(row)
        return slider.set_sensitive

    def add_switch_row(self, title: str, value=False, callback=None, subtitle="") -> callable:
        if self._current_group == None:
            return

        switch = Adw.SwitchRow()
        switch.set_title(title)
        switch.set_subtitle(subtitle)
        switch.set_active(value)

        if callback != None:
            switch.connect('notify::active', lambda switch,s: callback(int(switch.get_active())))

        self._current_group.add(switch)
        return switch.get_activatable_widget().set_sensitive

    def add_combo_row(self, title: str, values: dict, callback=None, subtitle="") -> None:
        if self._current_group == None:
            return

        combo = Adw.ComboRow()
        combo.set_title(title)
        combo.set_subtitle(subtitle)

        # Jesus christ, why is this so complicated?
        store = Gio.ListStore(item_type=ComboRow)
        for value in values:
            store.append(ComboRow(value, values[value]))

        factory = Gtk.SignalListItemFactory()
        factory.connect("setup", lambda factory,item : item.set_child(Gtk.Label()))
        factory.connect("bind", lambda factory,item : item.get_child().set_text(item.get_item().row_name))

        combo.set_model(store)
        combo.set_factory(factory)

        # TODO: connect callback function
        if callback != None:
            pass

        self._current_group.add(combo)

    def add_button_row(self, title: str, button_label: str, callback=None, subtitle="") -> callable:
        if self._current_group == None:
            return

        button = Gtk.Button(label=button_label)
        button.add_css_class("row-button")
        if callback != None:
            button.connect('clicked', lambda button: callback())

        row = Adw.ActionRow()
        row.set_title(title)
        row.set_subtitle(subtitle)
        row.add_suffix(button)
        self._current_group.add(row)

        return button.set_sensitive


    def _calibration_function(self, button, row, callback1: callable, callback2: callable):
        button.set_sensitive(False)
        subtitle = row.get_subtitle()
        text = "Calibration in progress..."
        print("Calibration start")
        callback1()
        for i in range(0,10):
            row.set_subtitle(f"{text} {10-i}s")
            time.sleep(1)

        print("Calibration stop")
        callback2()
        row.set_subtitle(subtitle)
        button.set_sensitive(True)

    def _handle_calibration(self, button, row, callback1: callable, callback2: callable) -> None:
        thread = Thread(target=self._calibration_function, args = (button, row, callback1, callback2))
        thread.start()

    def add_calibration_button_row(self, title: str, button_label: str,
                                   callback1=None, callback2=None) -> None:
        if self._current_group == None:
            return

        button = Gtk.Button(label=button_label)
        button.add_css_class("row-button")

        row = Adw.ActionRow()
        row.set_title(title)
        row.set_subtitle("Set device range")
        row.add_suffix(button)

        if callback1 != None and callback2 != None:
            button.connect('clicked', lambda button: self._handle_calibration(button, row, callback1, callback2))

        self._current_group.add(row)

    def add_toggle_button_row(self, title: str, labels: list,
                              callback=None, subtitle="") -> None:
        if self._current_group == None:
            return

        group = None
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        for label in labels:
            button = Gtk.ToggleButton(label=label)
            button.add_css_class("row-button")
            button.add_css_class("toggle-button")
            box.append(button)

            if group is None:
                group = button
                button.set_active(True)
            else:
                button.set_group(group)

            if callback != None:
                button.connect('toggled', lambda button: callback(button.get_label()) if button.get_active() == True else callback(None))

        row = Adw.ActionRow()
        row.set_title(title)
        row.set_subtitle(subtitle)
        row.add_suffix(box)

        self._current_group.add(row)

    def add_color_picker_row(self, title: str, callback=None, subtitle="", init_color=0) -> None:
        if self._current_group == None:
            return

        group = None
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        for i in range(0, PICKER_COLORS):
            button = Gtk.ToggleButton(label=i)
            button.add_css_class("toggle-button")
            button.add_css_class("color-button")
            button.add_css_class(f"c{i}")
            box.append(button)
            button.connect('toggled',
                lambda button: button.add_css_class("color-selected") if button.get_active() == True else button.remove_css_class("color-selected"))

            if group is None:
                group = button
            else:
                button.set_group(group)

            if i == init_color:
                button.set_active(True)

            if callback != None:
                button.connect('toggled',
                    lambda button: callback(int(button.get_label())) if button.get_active() == True else callback(None))

        row = Adw.ActionRow()
        row.set_title(title)
        row.set_subtitle(subtitle)
        row.add_suffix(box)

        self._current_group.add(row)
