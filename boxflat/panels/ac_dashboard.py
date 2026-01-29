# Copyright (c) 2025, Kevin Florczak Also Using Arch BTW

"""
Assetto Corsa Dashboard Panel
Simple panel to launch the AC web dashboard.
"""

import os
import signal
import subprocess
import atexit
from threading import Thread, Event

from boxflat.panels.settings_panel import SettingsPanel
from boxflat.connection_manager import MozaConnectionManager
from boxflat.hid_handler import MozaAxis
from boxflat.settings_handler import SettingsHandler
from boxflat.widgets import BoxflatLabelRow, BoxflatButtonRow, BoxflatSwitchRow, BoxflatComboRow


class ACDashboardSettings(SettingsPanel):
    """AC Dashboard settings panel."""

    def __init__(self, button_callback, connection_manager: MozaConnectionManager, hid_handler, settings: SettingsHandler):
        self._settings = settings
        self._server_process = None
        self._server_running = False
        self._status_row = None
        self._url_row = None
        self._toggle_row = None
        self._toggle_button = None
        self._theme_row = None
        self._themes_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "dashboard", "themes")

        super().__init__("AC Dashboard", button_callback, connection_manager, hid_handler)

    def prepare_ui(self):
        self.add_view_stack()

        # Dashboard Status Group
        self.add_preferences_group("Dashboard Status")

        # Status indicator
        self._status_row = BoxflatLabelRow("Status", "Stopped")
        self._status_row.set_subtitle("Web server is not running")
        self._add_row(self._status_row)

        # URL display
        self._url_row = BoxflatLabelRow("Access URL", "Not available")
        self._url_row.set_subtitle("Open this URL in your browser")
        self._add_row(self._url_row)

        # Controls Group
        self.add_preferences_group("Controls")

        # Start/Stop button
        self._toggle_row = BoxflatButtonRow("Start Dashboard")
        self._toggle_row.set_subtitle("Start the web dashboard server")
        self._add_row(self._toggle_row)
        self._toggle_button = self._toggle_row.add_button("Start")
        self._toggle_row.subscribe(self._toggle_dashboard)

        # Auto-start option (enabled by default if not set)
        autostart_enabled = self._settings.read_setting("ac-dashboard-autostart")
        if autostart_enabled is None:
            autostart_enabled = 1
            self._settings.write_setting(1, "ac-dashboard-autostart")
        self._autostart_row = BoxflatSwitchRow("Auto-start on app launch")
        self._autostart_row.set_subtitle("Automatically start dashboard when Boxflat opens")
        self._add_row(self._autostart_row)
        self._autostart_row.set_value_directly(autostart_enabled)
        self._autostart_row.subscribe(self._settings.write_setting, "ac-dashboard-autostart")

        # Dashboard Theme selector
        self.add_preferences_group("Appearance")
        self._theme_row = BoxflatComboRow("Dashboard Theme", "Select visual theme for the dashboard")
        self._add_row(self._theme_row)
        self._load_themes()
        # Set current theme
        current_theme = self._settings.read_setting("ac-dashboard-theme") or "Default"
        self._theme_row.subscribe(self._on_theme_changed)

        # Requirements Group
        self.add_preferences_group("Requirements")

        # Dependencies check
        self._deps_row = BoxflatLabelRow("Dependencies", "Checking...")
        self._add_row(self._deps_row)
        self._check_dependencies()

        # Info Group
        self.add_preferences_group("Information")

        info_text = """The AC Dashboard displays real-time telemetry from Assetto Corsa in a web browser.

Features:
• Large RPM display with color-coded bar
• Gear indicator (R, N, 1-7)
• Speed display in km/h
• Status indicators (ABS, TC, DRS, Pit Limiter)
• Fuel level bar

Access from any device on your network using the URL shown above.

Requirements:
• Python packages: websockets, aiohttp
• Assetto Corsa running with simshmbridge"""

        self._add_info_text(info_text)

        # Auto-start if enabled
        if autostart_enabled:
            self._start_dashboard()

    def _check_dependencies(self):
        """Check if required dependencies are installed."""
        try:
            import aiohttp
            self._deps_row.set_title("Dependencies installed")
            self._deps_row.set_subtitle("aiohttp available")
            self._deps_available = True
        except ImportError as e:
            self._deps_row.set_title("Dependencies missing")
            self._deps_row.set_subtitle("Install: pip install aiohttp")
            self._deps_available = False

    def _load_themes(self):
        """Load available dashboard themes from themes directory."""
        # Scan themes directory for HTML files
        if os.path.exists(self._themes_dir):
            for filename in sorted(os.listdir(self._themes_dir)):
                if filename.endswith('.html'):
                    # Remove .html extension for display name
                    theme_name = filename[:-5]
                    # Capitalize first letter
                    theme_name = theme_name[0].upper() + theme_name[1:] if theme_name else ""
                    self._theme_row.add_entry(theme_name)

        # Set currently selected theme
        current_theme = self._settings.read_setting("ac-dashboard-theme") or "Default"
        themes_list = [self._theme_row.get_model().get_string(i) for i in range(self._theme_row.get_model().get_n_items())]
        if current_theme in themes_list:
            self._theme_row.set_selected(themes_list.index(current_theme))

    def _on_theme_changed(self, selected):
        """Handle theme selection change."""
        if selected >= 0:
            theme = self._theme_row.get_model().get_string(selected)
            self._settings.write_setting(theme, "ac-dashboard-theme")
            # Restart dashboard if running to apply new theme
            if self._server_running:
                self._stop_dashboard()
                self._start_dashboard()

    def get_selected_theme(self):
        """Get the currently selected theme name."""
        selected = self._theme_row.get_selected()
        if selected >= 0:
            return self._theme_row.get_model().get_string(selected)
        return "Default"

    def _toggle_dashboard(self, *args):
        """Toggle dashboard on/off."""
        if self._server_running:
            self._stop_dashboard()
        else:
            self._start_dashboard()

    def _start_dashboard(self):
        """Start the web dashboard server."""
        if self._server_running or not hasattr(self, '_deps_available') or not self._deps_available:
            return

        # Find the dashboard script (now inside boxflat package)
        script_dir = os.path.dirname(os.path.dirname(__file__))
        dashboard_script = os.path.join(script_dir, "ac_web_dashboard.py")

        if not os.path.exists(dashboard_script):
            self._status_row.set_title("Error")
            self._status_row.set_subtitle("Dashboard script not found")
            return

        # Get selected theme
        selected_theme = self.get_selected_theme()

        # Start the server process
        try:
            # Start in background with new process group for proper cleanup
            env = os.environ.copy()
            env['AC_DASHBOARD_THEME'] = selected_theme

            self._server_process = subprocess.Popen(
                ["python3", dashboard_script],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=script_dir,
                env=env,
                start_new_session=True  # Create new process group
            )
            self._server_running = True

            # Register cleanup on exit (as fallback)
            atexit.register(self._cleanup_process)

            # Update UI
            self._status_row.set_title("Running")
            self._status_row.set_subtitle(f"Web server active (Theme: {selected_theme})")
            self._toggle_row.set_title("Stop Dashboard")
            self._toggle_row.set_subtitle("Stop the web dashboard server")
            self._toggle_button.set_label("Stop")

            # Get local IP for URL (no theme parameter - theme is handled internally)
            import socket
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                local_ip = s.getsockname()[0]
                s.close()
                self._url_row.set_title(f"http://{local_ip}:8765")
                self._url_row.set_subtitle("Open in browser on any device")
            except:
                self._url_row.set_title("http://localhost:8765")
                self._url_row.set_subtitle("Open in browser")

        except Exception as e:
            self._status_row.set_title("Error")
            self._status_row.set_subtitle(f"Failed to start: {e}")

    def _stop_dashboard(self):
        """Stop the web dashboard server."""
        if not self._server_running:
            return

        if self._server_process:
            # Terminate the process group to ensure all child processes are killed
            try:
                os.killpg(os.getpgid(self._server_process.pid), signal.SIGTERM)
            except:
                pass

            self._server_process.terminate()
            try:
                self._server_process.wait(timeout=3)
            except:
                try:
                    os.killpg(os.getpgid(self._server_process.pid), signal.SIGKILL)
                except:
                    self._server_process.kill()
            self._server_process = None

        self._server_running = False

        # Update UI
        self._status_row.set_title("Stopped")
        self._status_row.set_subtitle("Web server is not running")
        self._url_row.set_title("Not available")
        self._url_row.set_subtitle("Start the dashboard first")
        self._toggle_row.set_title("Start Dashboard")
        self._toggle_row.set_subtitle("Start the web dashboard server")
        self._toggle_button.set_label("Start")

    def _cleanup_process(self):
        """Cleanup the dashboard process (called by atexit)."""
        if self._server_process:
            try:
                os.killpg(os.getpgid(self._server_process.pid), signal.SIGKILL)
            except:
                pass

    def _add_info_text(self, text):
        """Add informational text widget."""
        from gi.repository import Gtk

        label = Gtk.Label(label=text)
        label.set_wrap(True)
        label.set_margin_top(10)
        label.set_margin_bottom(10)
        label.set_margin_start(10)
        label.set_margin_end(10)
        label.set_xalign(0)
        label.set_yalign(0)

        # Add some styling
        label.add_css_class("dim-label")

        self._current_group.add(label)

    def shutdown(self):
        """Clean up on shutdown."""
        print("[AC Dashboard] Shutting down...")
        try:
            self._stop_dashboard()
        except Exception as e:
            print(f"[AC Dashboard] Error during shutdown: {e}")
            # Force kill if normal shutdown failed
            if self._server_process:
                try:
                    os.killpg(os.getpgid(self._server_process.pid), signal.SIGKILL)
                except:
                    pass
        super().shutdown()
        print("[AC Dashboard] Shutdown complete")
