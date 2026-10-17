import os
import tempfile
import unittest
from unittest.mock import patch
from omapet.core import fresh, store, public
from omapet.desktop import can_roam, configure, position


class DesktopTests(unittest.TestCase):
    def test_view_preferences_and_escapes(self):
        s = fresh()
        configure(s, 'view', 'toggle')
        self.assertEqual(s['desktop_view'], 'detailed')
        configure(s, 'view', 'toggle')
        self.assertEqual(s['desktop_view'], 'simple')
        configure(s, 'escapes', 'off')
        self.assertFalse(s['escapes'])
        configure(s, 'escapes', 'toggle')
        self.assertTrue(s['escapes'])
        with self.assertRaises(ValueError): configure(s, 'view', 'on')

    def test_saved_position_and_invalid_coordinates(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, OMAPET_HOME=tmp):
            with store() as s: position(s, 123.4, 234.8, 'eDP-1')
            with store() as s:
                self.assertEqual(s['desktop_position'], {'x': 123, 'y': 235, 'screen': 'eDP-1'})
                for x, y in [(float('nan'), 0), (0, float('inf')), (-1, 0), (100001, 0)]:
                    with self.assertRaises(ValueError): position(s, x, y)
                self.assertEqual(s['desktop_position']['x'], 123)

    def test_only_fit_pets_go_out(self):
        for key in ('sleeping', 'vacation', 'sick', 'dead'):
            s = fresh(); s[key] = True
            self.assertFalse(can_roam(s))
            with self.assertRaises(ValueError): configure(s, 'roam', 'on')
        for key in ('food', 'energy'):
            s = fresh(); s[key] = 19
            self.assertFalse(can_roam(s))
        s = fresh()
        configure(s, 'roam', 'on')
        self.assertTrue(s['roaming'])
        self.assertGreater(s['escape_at'], 0)
        configure(s, 'roam', 'off')
        self.assertFalse(s['roaming'])

    def test_preferences_survive_and_sleep_brings_pet_home(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, OMAPET_HOME=tmp):
            with store() as s:
                configure(s, 'view', 'detailed')
                configure(s, 'roam', 'on')
            with store() as s:
                self.assertTrue(s['roaming'])
                self.assertEqual(s['desktop_view'], 'detailed')
                s['sleeping'] = True
            with store() as s:
                self.assertFalse(s['roaming'])
                self.assertFalse(public(s)['can_roam'])


if __name__ == '__main__': unittest.main()
