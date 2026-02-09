#!/usr/bin/env python3
"""
Unit tests for boxflat.process_handler

Tests the ProcessInfo class and pattern matching functionality.
"""

import unittest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from boxflat.process_handler import ProcessInfo


class TestProcessInfo(unittest.TestCase):
    """Test cases for the ProcessInfo class."""

    def test_creation(self):
        """Test creating ProcessInfo objects."""
        p = ProcessInfo("test.exe", "test.exe --arg1 --arg2")
        self.assertEqual(p.name, "test.exe")
        self.assertEqual(p.cmdline, "test.exe --arg1 --arg2")

    def test_equality(self):
        """Test ProcessInfo equality."""
        p1 = ProcessInfo("test.exe", "test.exe --arg1")
        p2 = ProcessInfo("test.exe", "test.exe --arg1")
        p3 = ProcessInfo("test.exe", "test.exe --arg2")
        p4 = ProcessInfo("other.exe", "test.exe --arg1")

        self.assertEqual(p1, p2)
        self.assertNotEqual(p1, p3)
        self.assertNotEqual(p1, p4)

    def test_hash(self):
        """Test ProcessInfo hashing for use in sets/dicts."""
        p1 = ProcessInfo("test.exe", "test.exe --arg1")
        p2 = ProcessInfo("test.exe", "test.exe --arg1")
        p3 = ProcessInfo("test.exe", "test.exe --arg2")

        self.assertEqual(hash(p1), hash(p2))
        self.assertNotEqual(hash(p1), hash(p3))

        # Test in a set
        process_set = {p1, p2, p3}
        self.assertEqual(len(process_set), 2)  # p1 and p2 should be deduplicated

    def test_repr(self):
        """Test ProcessInfo string representation."""
        p = ProcessInfo("test.exe", "test.exe --arg1")
        repr_str = repr(p)
        self.assertIn("test.exe", repr_str)
        self.assertIn("--arg1", repr_str)


class TestPatternMatching(unittest.TestCase):
    """Test cases for process pattern matching."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        # Only import ProcessObserver when running on Linux or in test environment
        try:
            from boxflat.process_handler import ProcessObserver
            cls.observer = ProcessObserver()
        except Exception as e:
            cls.observer = None
            print(f"Warning: Could not create ProcessObserver: {e}")

    def test_exact_name_match(self):
        """Test exact process name matching."""
        if not self.observer:
            self.skipTest("ProcessObserver not available (Windows environment)")

        process = ProcessInfo("ac_client", "ac_client")
        self.assertTrue(self.observer._matches_pattern("ac_client", process))

    def test_name_with_cmdline(self):
        """Test matching process name when cmdline has arguments."""
        if not self.observer:
            self.skipTest("ProcessObserver not available (Windows environment)")

        process = ProcessInfo("ac_client", "/usr/bin/ac_client --mode=race")
        self.assertTrue(self.observer._matches_pattern("ac_client", process))

    def test_cmdline_pattern_match(self):
        """Test matching against command-line patterns."""
        if not self.observer:
            self.skipTest("ProcessObserver not available (Windows environment)")

        # Match specific game launch
        process = ProcessInfo("EADesktop.exe", "EADesktop.exe --game-id=F1")
        self.assertTrue(self.observer._matches_pattern("EADesktop.exe --game-id=F1", process))
        self.assertTrue(self.observer._matches_pattern("--game-id=F1", process))

        # Should not match different game
        self.assertFalse(self.observer._matches_pattern("--game-id=WRC", process))

    def test_case_insensitive_matching(self):
        """Test that pattern matching is case-insensitive."""
        if not self.observer:
            self.skipTest("ProcessObserver not available (Windows environment)")

        process = ProcessInfo("MyGame.exe", "MyGame.exe --Mode=RACE")
        self.assertTrue(self.observer._matches_pattern("mygame.exe", process))
        self.assertTrue(self.observer._matches_pattern("--mode=race", process))

    def test_no_match(self):
        """Test patterns that should not match."""
        if not self.observer:
            self.skipTest("ProcessObserver not available (Windows environment)")

        process = ProcessInfo("python3", "python3 test.py")
        # Note: "python" DOES match "python3" due to substring matching in cmdline
        # This is intentional - use exact process names for strict matching
        self.assertFalse(self.observer._matches_pattern("ruby", process))
        self.assertFalse(self.observer._matches_pattern("java", process))
        self.assertFalse(self.observer._matches_pattern("node", process))

    def test_empty_pattern(self):
        """Test that empty pattern doesn't match."""
        if not self.observer:
            self.skipTest("ProcessObserver not available (Windows environment)")

        process = ProcessInfo("test", "test")
        self.assertFalse(self.observer._matches_pattern("", process))
        self.assertFalse(self.observer._matches_pattern(None, process))

    def test_substring_match_in_cmdline(self):
        """Test substring matching in command line."""
        if not self.observer:
            self.skipTest("ProcessObserver not available (Windows environment)")

        process = ProcessInfo("launcher", "/usr/bin/launcher --game=assetto-corsa --track=spa")

        # Should match substrings
        self.assertTrue(self.observer._matches_pattern("assetto-corsa", process))
        self.assertTrue(self.observer._matches_pattern("--game=assetto", process))
        self.assertTrue(self.observer._matches_pattern("--track=spa", process))

        # Should not match non-existent substrings
        self.assertFalse(self.observer._matches_pattern("iracing", process))


class TestProcessObserverRegistration(unittest.TestCase):
    """Test cases for ProcessObserver registration methods."""

    def setUp(self):
        """Set up test fixtures."""
        try:
            from boxflat.process_handler import ProcessObserver
            self.observer = ProcessObserver()
        except Exception as e:
            self.observer = None
            print(f"Warning: Could not create ProcessObserver: {e}")

    def test_register_process(self):
        """Test registering a process pattern."""
        if not self.observer:
            self.skipTest("ProcessObserver not available")

        self.observer.register_process("test_game.exe")
        events = self.observer.list_events()
        self.assertIn("test_game.exe", events)

    def test_register_empty_process(self):
        """Test that empty process patterns are not registered."""
        if not self.observer:
            self.skipTest("ProcessObserver not available")

        initial_events = set(self.observer.list_events())
        self.observer.register_process("")
        after_events = set(self.observer.list_events())
        self.assertEqual(initial_events, after_events)

    def test_deregister_process(self):
        """Test deregistering a process pattern."""
        if not self.observer:
            self.skipTest("ProcessObserver not available")

        self.observer.register_process("game_to_remove.exe")
        self.assertIn("game_to_remove.exe", self.observer.list_events())

        self.observer.deregister_process("game_to_remove.exe")
        self.assertNotIn("game_to_remove.exe", self.observer.list_events())

    def test_deregister_all_processes(self):
        """Test deregistering all process patterns."""
        if not self.observer:
            self.skipTest("ProcessObserver not available")

        # Register several processes
        self.observer.register_process("game1.exe")
        self.observer.register_process("game2.exe")
        self.observer.register_process("game3.exe")

        self.observer.deregister_all_processes()

        # Only "no-games" should remain
        events = self.observer.list_events()
        self.assertEqual(events, ["no-games"])

    def test_no_games_event_preserved(self):
        """Test that no-games event is always preserved."""
        if not self.observer:
            self.skipTest("ProcessObserver not available")

        self.assertIn("no-games", self.observer.list_events())
        self.observer.deregister_all_processes()
        self.assertIn("no-games", self.observer.list_events())


class TestListProcesses(unittest.TestCase):
    """Test cases for list_processes function."""

    def test_list_processes_returns_list(self):
        """Test that list_processes returns a list of ProcessInfo."""
        try:
            from boxflat.process_handler import list_processes
            result = list_processes()
            self.assertIsInstance(result, list)
            if result:
                self.assertIsInstance(result[0], ProcessInfo)
        except KeyError:
            # BOXFLAT_FLATPAK_EDITION env var not set
            self.skipTest("BOXFLAT_FLATPAK_EDITION not set")

    def test_list_processes_with_filter(self):
        """Test that list_processes filter works."""
        try:
            from boxflat.process_handler import list_processes
            # Filter for python - should find at least the test runner
            result = list_processes("python")
            self.assertIsInstance(result, list)
            for proc in result:
                self.assertTrue(
                    "python" in proc.name.lower() or "python" in proc.cmdline.lower(),
                    f"Filter failed: {proc}"
                )
        except KeyError:
            self.skipTest("BOXFLAT_FLATPAK_EDITION not set")

    def test_list_processes_no_duplicates(self):
        """Test that list_processes doesn't return duplicates."""
        try:
            from boxflat.process_handler import list_processes
            result = list_processes()
            # Convert to set of tuples to check for duplicates
            seen = set()
            for proc in result:
                key = (proc.name, proc.cmdline)
                self.assertNotIn(key, seen, f"Duplicate process found: {proc}")
                seen.add(key)
        except KeyError:
            self.skipTest("BOXFLAT_FLATPAK_EDITION not set")


if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2)
