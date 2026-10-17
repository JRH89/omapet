import math
import os
import tempfile
import unittest
from unittest.mock import patch
from omapet.core import fresh, store
from omapet.desktop import bonk, configure, repair, MAX_CRACKS


class CrackTests(unittest.TestCase):
    def pet(self):
        s = fresh(); s.update(roaming=True, overlay=True)
        return s

    def test_all_cracks_must_be_fixed_before_returning(self):
        s = self.pet()
        one = bonk(s, 120, 200, 'eDP-1', now=100)
        two = bonk(s, 500, 300, 'eDP-1', now=116)
        with self.assertRaisesRegex(ValueError, 'Repair all 2'):
            configure(s, 'roam', 'off')
        self.assertTrue(s['roaming'])
        repair(s, one['id'])
        with self.assertRaisesRegex(ValueError, 'Repair all 1'):
            configure(s, 'roam', 'off')
        repair(s, two['id'])
        configure(s, 'roam', 'off')
        self.assertFalse(s['roaming'])

    def test_cooldown_limit_and_no_more_damage_while_repairing(self):
        s = self.pet()
        one = bonk(s, 120, 200, now=100)
        with self.assertRaisesRegex(ValueError, 'recovering'):
            bonk(s, 120, 200, now=101)
        for i in range(1, MAX_CRACKS): bonk(s, 120+i*100, 200, now=100+i*16)
        with self.assertRaisesRegex(ValueError, 'existing cracks'):
            bonk(s, 120, 200, now=200)
        repair(s, one['id'])
        with self.assertRaisesRegex(ValueError, 'Repair time'):
            bonk(s, 120, 200, now=220)
        repair(s, 'all')
        with self.assertRaisesRegex(ValueError, 'Repair time'):
            bonk(s, 120, 200, now=240)
        configure(s, 'roam', 'off'); configure(s, 'roam', 'on')
        bonk(s, 120, 200, now=260)
        self.assertEqual(len(s['cracks']), 1)

    def test_no_health_xp_or_position_penalty(self):
        s = self.pet(); s['desktop_position'] = {'x': 300, 'y': 150, 'screen': 'eDP-1'}
        before = {k: s[k] for k in ['health', 'xp', 'energy', 'name', 'character', 'desktop_position']}
        crack = bonk(s, 800, 300, now=100)
        repair(s, crack['id'])
        self.assertEqual({k: s[k] for k in before}, before)

    def test_invalid_or_hidden_impacts_are_rejected(self):
        s = self.pet()
        for x, y in [(math.nan, 1), (1, math.inf), (-1, 1), (100001, 1)]:
            with self.assertRaises(ValueError): bonk(s, x, y)
        for key in ['sleeping', 'sick', 'dead', 'vacation']:
            bad = self.pet(); bad[key] = True
            with self.assertRaises(ValueError): bonk(bad, 10, 10)
        s['overlay'] = False
        with self.assertRaises(ValueError): bonk(s, 10, 10)
        self.assertEqual(s['cracks'], [])

    def test_persistence_and_sleep_do_not_clear_cracks(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, OMAPET_HOME=tmp):
            with store() as s:
                s.update(roaming=True, overlay=True)
                crack = bonk(s, 120, 200, 'eDP-1')
                s['sleeping'] = True
            with store() as s:
                self.assertEqual(s['cracks'], [crack])
                self.assertTrue(s['roaming'])
                repair(s, crack['id'])
            with store() as s:
                self.assertFalse(s['cracks'])
                self.assertFalse(s['roaming'])

    def test_hiding_preserves_damage_and_cannot_bypass_home_gate(self):
        s = self.pet(); crack = bonk(s, 120, 200)
        s['overlay'] = False
        with self.assertRaises(ValueError): configure(s, 'roam', 'off')
        self.assertEqual(s['cracks'], [crack])
        with self.assertRaisesRegex(ValueError, 'already repaired'): repair(s, 'unknown')
        self.assertEqual(s['cracks'], [crack])

    def test_manual_outing_requires_cleaning_both_kinds(self):
        s = fresh(); s['overlay'] = True
        configure(s, 'roam', 'on')
        crack = bonk(s, 100, 100, now=100)
        poop = bonk(s, 200, 200, now=120, kind='poop')
        self.assertEqual(poop['kind'], 'poop')
        repair(s, crack['id'])
        with self.assertRaises(ValueError): configure(s, 'roam', 'off')
        with self.assertRaises(ValueError): bonk(s, 300, 300, now=140, kind='poop')
        repair(s, poop['id'])
        configure(s, 'roam', 'off')
        self.assertFalse(s['roaming'])

    def test_unknown_mess_kind_is_rejected(self):
        s = self.pet()
        with self.assertRaises(ValueError): bonk(s, 100, 100, kind='unknown')
        self.assertFalse(s['cracks'])
