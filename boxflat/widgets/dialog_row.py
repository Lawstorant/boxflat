import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Adw
from .row import BoxflatRow
from .switch_row import BoxflatSwitchRow

class BoxflatDialogRow(BoxflatRow):
    def __init__(self, title: str, subtitle=""):
        super().__init__(title, subtitle)

        icon = Gtk.Image()
        icon.set_from_icon_name("go-next-symbolic")
        icon.set_valign(Gtk.Align.CENTER)
        # icon.set_pixel_size(32)

        self.set_activatable(True)
        self._set_widget(icon)
        self._icon = icon


        self._group = Adw.PreferencesGroup()
        self._group.add_css_class("wheel-dialog-setting")
        page = Adw.PreferencesPage()
        page.add(self._group)

        self._dialog = Adw.Dialog(title=title)
        self._dialog.set_child(Adw.ToolbarView())
        self._dialog.get_child().add_top_bar(Adw.HeaderBar())
        self._dialog.get_child().set_content(page)


        self.connect("activated", lambda w: self._dialog.present())


    def add_switches(self, *switches) -> None:
        for switch in switches:
            row = BoxflatSwitchRow(switch)
            row.set_width(400)
            self._group.add(row)
