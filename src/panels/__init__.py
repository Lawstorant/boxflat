from panels.settings_panel import SettingsPanel
from panels.base import BaseSettings
from panels.wheel import WheelSettings
from panels.home import HomeSettings
from panels.dash import DashSettings

_panels = {}

def prepare_panels(button_callback) -> dict:
    _panels["Home"] = HomeSettings(button_callback)
    _panels["Base"] = BaseSettings(button_callback)
    _panels["Wheel"] = WheelSettings(button_callback)
    _panels["Dash"] = DashSettings(button_callback)
        
    return _panels

def activate_default() -> SettingsPanel:
    for panel in _panels.values():
        panel.button.set_active(False)
        
    _panels["Home"].button.set_active(True)
    return _panels["Home"]
    
def panels() -> dict:
    return _panels

def buttons() -> list:
    buttons = []
    for panel in _panels.values():
        buttons.append(panel.button)
        
    return buttons
    