import gi
from gi.repository import Gtk, Adw, GLib

from . import BoxflatButtonRow, BoxflatSwitchRow

class BoxflatPresetDialog(Adw.Dialog):
    def __init__(self, presets_path: str, file_name: str):
        super().__init__()

        preset_name = file_name.removesuffix(".yml")
        self._delete_subs = []
        self.set_title(preset_name)

        # Create UI
        self._name_row = Adw.EntryRow(title="Preset name")
        # self._name_row.set_text(preset_name)

        self._auto_apply = BoxflatSwitchRow("Apply automatically")
        self._auto_apply.set_subtitle("Apply when selected process is running")
        self._auto_apply.set_width(400)

        self._auto_apply_name = Adw.EntryRow(title="Process name")
        self._auto_apply_name.set_sensitive(False)
        self._auto_apply.subscribe(self._auto_apply_name.set_sensitive)

        self._save_row = None
        self._delete_row = None

        # Decide which button style to use
        if Adw.get_minor_version() >= 6:
            self._save_row = Adw.ButtonRow(title="Save")
            self._save_row.add_css_class("suggested-action")
            self._save_row.set_end_icon_name("document-save-symbolic")
            self._save_row.connect("activated", lambda v: print("Save preset"))
            self._name_row.connect("notify::text-length", lambda e, *args: self._save_row.set_sensitive(e.get_text_length()))

            self._delete_row = Adw.ButtonRow(title="Delete")
            self._delete_row.add_css_class("destructive-action")
            self._delete_row.set_end_icon_name("user-trash-symbolic")
            self._delete_row.connect("activated", lambda v: print("Delete preset"))


        # compatibility with libadwaita older than 1.6
        else:
            self._save_row = BoxflatButtonRow("Preset destiny")
            # self._save_row.subscribe(self._save_preset)
            self._save_row.add_button("Save", print, "Save preset")
            self._save_row.add_button("Delete", print, "Delete preset").add_css_class("destructive-action")
            self._name_row.connect("notify::text-length", lambda e, *args: self._save_row.set_active(e.get_text_length()))

        # Place rows in logical order
        page = Adw.PreferencesPage()

        group = Adw.PreferencesGroup()
        group.add(self._name_row)
        page.add(group)

        group = Adw.PreferencesGroup()
        group.add(self._auto_apply)
        group.add(self._auto_apply_name)
        page.add(group)

        group = Adw.PreferencesGroup()
        group.add(self._save_row)
        page.add(group)

        if self._delete_row:
            group = Adw.PreferencesGroup()
            group.add(self._delete_row)
            page.add(group)


        # Finally, add all things together
        self.set_child(Adw.ToolbarView())
        self.get_child().add_top_bar(Adw.HeaderBar())
        self.get_child().set_content(page)
        self.present()


    def _read_preset_data(self):
        # self.set_title(preset_name)
        pass


    def _notify_delete(self):
        for sub in self._delete_subs:
            sub[0](*sub[1])


    def _subscribe_delete(self, callback: callable, *args) -> bool:
        if not callback:
            return False

        self._delete_subs.append((callback, args))
        return True
