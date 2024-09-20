from .button_level_row import *

class BoxflatMinMaxLevelRow(BoxflatButtonLevelRow):
    def __init__(self, title: str, callback: callable,
                 command_prefix: str, subtitle="", max_value=1000):
        super().__init__(title, subtitle, max_value)

        self.set_bar_width(230)
        self.add_button("Min", callback, self.get_percent, f"{command_prefix}-min")
        self.insert_bar_now()
        self.add_button("Max", callback, self.get_percent, f"{command_prefix}-max")
