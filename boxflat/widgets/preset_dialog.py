from gi.repository import Gtk, Adw, GLib

from .button_row import BoxflatButtonRow
from .switch_row import BoxflatSwitchRow
from .advance_row import BoxflatAdvanceRow

from boxflat.subscription import EventDispatcher

class BoxflatPresetDialog(Adw.Dialog, EventDispatcher):
    def __init__(self, presets_path: str, file_name: str):
        Adw.Dialog.__init__(self)
        EventDispatcher.__init__(self)

        self._register_events("save",  "delete")
        preset_name = file_name.removesuffix(".yml")
        self._preset_name = preset_name
        self.set_title("Preset settings")
        self.set_content_width(480)

        # Create UI
        self._name_row = Adw.EntryRow(title="Preset name")
        self._name_row.set_text(preset_name)

        self._auto_apply = BoxflatSwitchRow("Apply automatically")
        self._auto_apply.set_subtitle("Apply when selected process is running")

        self._auto_apply_name = Adw.EntryRow(title="Process name")
        self._auto_apply_name.set_sensitive(False)
        self._auto_apply.subscribe(self._auto_apply_name.set_sensitive)

        self._auto_apply_select = BoxflatAdvanceRow("Select running process")
        self._auto_apply_select.set_active(False)
        self._auto_apply_select.subscribe(self._open_process_page)
        self._auto_apply.subscribe(self._auto_apply_select.set_active)

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
        nav.add(Adw.NavigationPage(title=f"\"{preset_name}\" preset settings", child=toolbar_view))

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
        self._dispatch("save", self._preset_name)
        self.close()


    def _notify_delete(self, *rest):
        self._dispatch("delete", self._preset_name)
        self.close()


    def _open_process_page(self, *rest):
        page = Adw.PreferencesPage()

        toolbar_view = Adw.ToolbarView()
        toolbar_view.add_top_bar(Adw.HeaderBar())
        toolbar_view.set_content(page)

        self._navigation.push(Adw.NavigationPage(title="Find game process", child=toolbar_view))
