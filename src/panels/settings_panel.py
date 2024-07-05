import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Gio, Adw
from structs import *

class SettingsPanel(object):
    _current_page: Adw.PreferencesPage
    _current_group: Adw.PreferencesGroup

    def __init__(self, title, button_callback) -> None:
        self._content = self._prepare_content()
        self._button = self._prepare_button(title, button_callback)
        self._banner = self._prepare_banner()

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
        return content

    def _prepare_banner(self) -> Adw.Banner:
        banner = Adw.Banner()
        banner.set_title("Remember to apply settings")
        banner.set_button_label("Apply")
        banner.set_revealed(True)
        banner.connect("button-clicked", self.apply)
        self._content.append(banner)
        return banner

    def show_banner(self, *arg) -> None:
        self._banner.set_revealed(True)

    def hide_banner(self, *arg) -> None:
        self._banner.set_revealed(False)

    def set_banner_title(self, new_title: str) -> None:
        self._banner.set_title(new_title)

    def apply(self) -> None:
        # self.hide_banner()
        pass

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

    def _add_preferences_page(self) -> None:
        self._current_page = Adw.PreferencesPage()
        self._content.append(self._current_page)

    def _add_preferences_group(self, title: str) -> None:
        if self._current_page != None:
            self._current_group = Adw.PreferencesGroup()
            self._current_group.set_title(title)
            self._current_page.add(self._current_group)

    def _add_title_row(self, title: str, subtitle="") -> None:
        if self._current_group == None:
            return

        row = Adw.ActionRow()
        row.set_title(title)
        row.set_subtitle(subtitle)

        self._current_group.add(row)

    def _add_slider_row(self, title: str, range_start: int, range_stop: int,
                        value=0, size_request=(350,0), marks=[], mark_suffix="",
                        callback=None, subtitle="") -> None:

        if self._current_group == None:
            return

        slider = Gtk.Scale()
        slider.set_digits(0)
        slider.set_range(range_start, range_stop)
        slider.set_increments(1, 0)
        slider.set_draw_value(True)
        slider.set_value(value)
        slider.set_size_request(size_request[0], size_request[1])

        marks.append(range_start)
        marks.append(range_stop)
        for mark in marks:
            slider.add_mark(mark, Gtk.PositionType.BOTTOM, f"{mark}{mark_suffix}")

        if callback != None:
            slider.connect('value-changed', callback)

        row = Adw.ActionRow()
        row.add_suffix(slider)
        row.set_title(title)
        row.set_subtitle(subtitle)

        self._current_group.add(row)

    def _add_switch_row(self, title: str, value=False, callback=None, subtitle="") -> None:
        switch = Adw.SwitchRow()
        switch.set_title(title)
        switch.set_subtitle(subtitle)
        switch.set_active(value)

        if callback != None:
            switch.get_activatable_widget().connect('state-set', callback)

        self._current_group.add(switch)

    def _add_combo_row(self, title: str, values: dict, callback=None, subtitle="") -> None:
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

        if callback != None:
            pass

        self._current_group.add(combo)
