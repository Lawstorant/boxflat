import sys
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Gdk, Adw

setting_panels = [
    "Home",
    "Base",
    "Wheel",
    "Pedals",
    "Display",
    "Sequential shifter",
    "H-Pattern shifter"
]

class MainWindow(Adw.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_default_size(800, 500)
        self.set_title("Box Flat")
        
        right_header = Adw.HeaderBar()
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
        navigation.set_max_sidebar_width(10)
        navigation.set_min_sidebar_width(10)
        
        self.navpage = Adw.NavigationPage()
        self.navpage.set_title("Home")
        
        sidebar = Adw.NavigationPage()
        sidebar.set_title("Box Flat")
        
        box2 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box2.append(left_header)
        sidebar.set_child(box2)
        
        self.buttons = []
        for panel in setting_panels:
            button = Gtk.ToggleButton()
            button.set_css_classes(['sidebar-button'])
            button.connect("clicked", self.switch_panel)
            button.set_halign(Gtk.Align.FILL)
            
            label = Gtk.Label(label=f"{panel}")
            label.set_justify(Gtk.Justification.LEFT)
            label.set_xalign(0)
            button.set_child(label)
            
            self.buttons.append(button)
            box2.append(button)
        
        box1 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box1.append(right_header)
        self.navpage.set_child(box1)
        
        self.set_content(navigation)
        navigation.set_content(self.navpage)
        navigation.set_sidebar(sidebar)
        
        slider_label = Gtk.Label(label="Rotation range")
        slider = Gtk.Scale()
        slider.set_digits(0)  # Number of decimal places to use
        slider.set_range(90, 2700)
        slider.add_mark(360, Gtk.PositionType.BOTTOM)
        slider.add_mark(540, Gtk.PositionType.BOTTOM)
        slider.add_mark(900, Gtk.PositionType.BOTTOM)
        slider.add_mark(1800, Gtk.PositionType.BOTTOM)
        # slider.add_mark(360)
        # slider.add_mark(900)
        slider.set_increments(2, 180)
        slider.set_draw_value(True)  # Show a label with current value
        slider.set_value(540)  # Sets the current value/position
        slider.connect('value-changed', self.slider_changed)
        box2 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box2.set_css_classes(['settings-pane'])
        box2.append(slider_label)
        box2.append(slider)
        box1.append(box2)

    def slider_changed(self, slider):
        value = slider.get_value()
        if value % 2:
            slider.set_value(value + 1)
        
    def switch_panel(self, button) -> None:
        for b in self.buttons:
            if b != button:
                b.set_active(False)
                
        self.navpage.set_title(button.get_child().get_label())
        

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