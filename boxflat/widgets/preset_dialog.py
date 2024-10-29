# Copyright (c) 2024, Tomasz Pakuła Using Arch BTW

from gi.repository import Gtk, Adw

from .button_row import BoxflatButtonRow
from .switch_row import BoxflatSwitchRow
from .advance_row import BoxflatAdvanceRow
from .label_row import BoxflatLabelRow

from boxflat.subscription import EventDispatcher
from boxflat import process_handler
from boxflat.preset_handler import MozaPresetHandler
from os import environ

class BoxflatPresetDialog(Adw.Dialog, EventDispatcher):
    def __init__(self, presets_path: str, file_name: str):
        Adw.Dialog.__init__(self)
        EventDispatcher.__init__(self)

        self._process_list_group = None
        self._preset_handler = MozaPresetHandler(None)
        self._preset_handler.set_path(presets_path)
        self._preset_handler.set_name(file_name)

        self._register_events("save",  "delete")

        self._initial_name = file_name.removesuffix(".yml")
        preset_name = file_name.removesuffix(".yml")
        self._preset_name = preset_name
        self.set_title("Preset settings")
        self.set_content_width(480)

        # Create UI
        self._name_row = Adw.EntryRow(title="Preset name")
        self._name_row.set_text(preset_name)

        process_name = self._preset_handler.get_linked_process()
        self._auto_apply = BoxflatSwitchRow("Apply automatically")
        self._auto_apply.set_subtitle("Apply when selected process is running")

        self._auto_apply_name = BoxflatLabelRow("Process name")
        self._auto_apply_name.set_label(process_name)
        self._auto_apply_name.set_active(False)
        self._auto_apply.subscribe(self._auto_apply_name.set_active)

        self._auto_apply_select = BoxflatAdvanceRow("Select running process")
        self._auto_apply_select.set_active(False)
        self._auto_apply_select.subscribe(self._open_process_page)
        self._auto_apply.subscribe(self._auto_apply_select.set_active)

        self._auto_apply.set_value(len(process_name) > 0, mute=False)

        # Place rows in logical order
        page = Adw.PreferencesPage()
        group = Adw.PreferencesGroup(margin_start=10, margin_end=10)
        group.add(self._name_row)
        page.add(group)

        group = Adw.PreferencesGroup(margin_start=10, margin_end=10)
        group.add(self._auto_apply)
        group.add(self._auto_apply_name)
        group.add(self._auto_apply_select)
        page.add(group)

        # Finally, add all things together
        nav = Adw.NavigationView()
        self.set_child(nav)
        self._navigation = nav

        toolbar_view = Adw.ToolbarView()
        nav.add(Adw.NavigationPage(title=f"Preset settings", child=toolbar_view))

        toolbar_view.add_top_bar(Adw.HeaderBar())
        toolbar_view.set_content(page)

        self._read_preset_data(presets_path, file_name)

        self._save_row = None
        self._delete_row = None
        # Decide which button style to use
        if Adw.get_minor_version() >= 6:
            self._save_row = Adw.ButtonRow(title="Save")
            self._save_row.add_css_class("suggested-action")
            self._save_row.set_end_icon_name("document-save-symbolic")
            self._save_row.connect("activated", self._notify_save)
            self._name_row.connect("notify::text-length", lambda e, *args: self._save_row.set_sensitive(e.get_text_length()))

            self._delete_row = Adw.ButtonRow(title="Delete")
            self._delete_row.add_css_class("destructive-action")
            self._delete_row.set_end_icon_name("user-trash-symbolic")
            self._delete_row.connect("activated", self._notify_delete)

            group = Adw.PreferencesGroup(margin_start=100, margin_end=100)
            group.add(self._delete_row)
            page.add(group)

            group = Adw.PreferencesGroup(margin_start=100, margin_end=100)
            group.add(self._save_row)
            page.add(group)


        # compatibility with libadwaita older than 1.6
        else:
            self._save_row = Gtk.Button(label="Save", hexpand=True)
            self._save_row.add_css_class("suggested-action")
            self._save_row.add_css_class("square")
            self._save_row.connect("clicked", self._notify_save)
            self._name_row.connect("notify::text-length", lambda e, *args: self._save_row.set_sensitive(e.get_text_length()))

            self._delete_row = Gtk.Button(label="Delete", hexpand=True)
            self._delete_row.add_css_class("destructive-action")
            self._delete_row.add_css_class("square")
            self._delete_row.connect("clicked", self._notify_delete)

            box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
            box.append(self._delete_row)
            box.append(self._save_row)
            box.add_css_class("linked")

            self.get_child().add_bottom_bar(box)


    def _read_preset_data(self, presets_path: str, file_name: str):
        print(f"Reading preset data from \"{file_name}\"")
        # self.set_title(preset_name)


    def _notify_save(self, *rest):
        self.close()

        process_name = ""
        if self._auto_apply.get_value():
            process_name = self._auto_apply_name.get_label()
        self._preset_handler.set_linked_process(process_name)

        current_name = self._name_row.get_text()
        if self._initial_name != current_name:
            self._preset_handler.copy_preset(current_name)
            self._dispatch("delete", self._preset_name)

        self._dispatch("save", self._preset_name)


    def _notify_delete(self, *rest):
        self.close()
        self._dispatch("delete", self._preset_name)


    def _list_processes(self, entry: Adw.EntryRow, page: Adw.PreferencesPage):
        group = Adw.PreferencesGroup()
        name = entry.get_text()

        page.remove(self._process_list_group)
        page.add(group)
        self._process_list_group = group

        if len(name) < 3:
            group.add(BoxflatLabelRow("Enter at least three letters"))
            return

        for name in sorted(process_handler.list_processes(name)):
            row = BoxflatLabelRow(name)
            row.subscribe(self._navigation.pop)
            row.subscribe(self._auto_apply_name.set_label, name)
            row.set_activatable(True)
            group.add(row)


    def _open_process_page(self, *rest):
        entry = Adw.EntryRow()
        entry.set_title("Process name filter")

        group = Adw.PreferencesGroup()
        group.add(entry)
        self._process_list_group = Adw.PreferencesGroup(title="Process list")

        page = Adw.PreferencesPage()
        page.add(group)
        page.add(self._process_list_group)

        entry.connect("notify::text-length", lambda *_: self._list_processes(entry, page))

        toolbar_view = Adw.ToolbarView()
        toolbar_view.add_top_bar(Adw.HeaderBar())
        toolbar_view.set_content(page)

        self._navigation.push(Adw.NavigationPage(title="Find game process", child=toolbar_view))
        self._list_processes(entry, page)
