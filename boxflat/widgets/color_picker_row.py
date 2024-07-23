from .toggle_button_row import BoxflatToggleButtonRow

PICKER_COLORS=8

class BoxflatColorPickerRow(BoxflatToggleButtonRow):
    def __init__(self, title: str, subtitle="", alt_colors=False):
        super().__init__(title, subtitle)

        for i in range(0, PICKER_COLORS):
            self.add_buttons(str(i))
            self._buttons[i].add_css_class("color-button")
            self._buttons[i].add_css_class(f"c{i}")
            self._buttons[i].connect('toggled',
                lambda b: b.add_css_class("cs") if b.get_active() == True else b.remove_css_class("cs"))

            if alt_colors:
                self._buttons[i].add_css_class(f"c{i}-alt")

        # self._buttons[0].add_css_class("cs")
