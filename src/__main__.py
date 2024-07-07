import sys
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Gdk, Adw

import panels

class MainWindow(Adw.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_default_size(900, 700)
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
        panels.prepare_panels(self.switch_panel)

        for button in panels.buttons():
            box2.append(button)

        self.settings_box.append(panels.activate_default().content)
        content.set_title("Home")


    def switch_panel(self, button) -> None:
        new_title = button.get_child().get_label()
        old_title = self.navigation.get_content().get_title()
        box = self.settings_box

        panels.panels()[old_title].deactivate_button()
        self.set_content_title(new_title)

        box.remove(Gtk.Widget.get_first_child(box))
        box.append(panels.panels()[new_title].content)


    def set_content_title(self, title: str) -> None:
        self.navigation.get_content().set_title(title)


class MyApp(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect('activate', self.on_activate)

    def on_activate(self, app):
        self.win = MainWindow(application=app)
        self.win.present()

css_provider = Gtk.CssProvider()
css_provider.load_from_path('style.css')
Gtk.StyleContext.add_provider_for_display(Gdk.Display.get_default(), css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

app = MyApp(application_id="com.lawstorant.boxflat")
app.run(sys.argv)
