import copy
import os
import tempfile
import unittest
from unittest.mock import patch
from omapet.core import fresh, store
from omapet.collection import hatch, switch, all_pets, roam
from omapet.desktop import team_bonk, repair, MAX_CRACKS


class GroupPlayTests(unittest.TestCase):
    def household(self, count=4):
        s = fresh()
        for _ in range(count-1): hatch(s, 'crab')
        for pet in all_pets(s): pet['roaming'] = True
        s['overlay'] = True
        return s, [p['id'] for p in all_pets(s)]

    def test_team_creates_stronger_bounded_shared_messes(self):
        s, ids = self.household()
        created = team_bonk(s, ids, 200, 300, 'test-screen', now=100)
        self.assertEqual(len(created), 2)
        self.assertTrue(all(c['team_size'] == 4 and c['participants'] == ids for c in created))
        original = s['id']
        switch(s, ids[1])
        self.assertEqual(len(s['cracks']), 2)
        self.assertNotIn('cracks', s['companions'][original])
        with self.assertRaisesRegex(ValueError, 'break'): team_bonk(s, ids, 200, 300, now=189)
        team_bonk(s, ids, 200, 300, now=190)
        self.assertEqual(len(s['cracks']), MAX_CRACKS)
        with self.assertRaisesRegex(ValueError, 'existing cracks'): team_bonk(s, ids, 200, 300, now=280)
        repair(s, s['cracks'][0]['id'])
        with self.assertRaisesRegex(ValueError, 'Repair time'): team_bonk(s, ids, 200, 300, now=280)

    def test_partial_cap_leaves_only_one_slot_and_coordinates_remain_bounded(self):
        s, ids = self.household(2)
        s['cracks'] = [dict(id=str(i)) for i in range(3)]
        created = team_bonk(s, ids, 100000, 100000, now=100)
        self.assertEqual(len(created), 1)
        self.assertEqual(len(s['cracks']), 4)
        self.assertLessEqual(created[0]['x'], 100000)
        self.assertLessEqual(created[0]['y'], 100000)

    def test_unfit_duplicate_hidden_or_invalid_team_cannot_damage(self):
        for condition in ('sleeping', 'sick', 'vacation', 'dead', 'roaming', 'energy'):
            s, ids = self.household()
            p = s['companions'][ids[1]]
            p[condition] = False if condition == 'roaming' else 5 if condition == 'energy' else True
            previous = copy.deepcopy(s)
            with self.assertRaises(ValueError): team_bonk(s, ids, 10, 20, now=100)
            self.assertEqual(s, previous)
        s, ids = self.household()
        for bad in ([ids[0]], [ids[0], ids[0]], ids+['unknown']):
            with self.assertRaises(ValueError): team_bonk(s, bad, 10, 20, now=100)
        s['overlay'] = False
        with self.assertRaisesRegex(ValueError, 'Show'): team_bonk(s, ids, 10, 20, now=100)

    def test_others_can_play_while_active_pet_rests(self):
        s, ids = self.household(3)
        s.update(sleeping=True, roaming=False)
        self.assertEqual(len(team_bonk(s, ids[1:], 100, 100, now=100)), 2)

    def test_companions_cannot_hide_team_messes_and_a_new_outing_resumes_play(self):
        s, ids = self.household(3)
        team_bonk(s, ids, 200, 200, now=100)
        with self.assertRaisesRegex(ValueError, 'Repair all'): roam(s, 'off', ids[1])
        self.assertTrue(s['companions'][ids[1]]['roaming'])
        repair(s, 'all')
        self.assertTrue(s['repairing_cracks'])
        roam(s, 'off')
        s['sleeping'] = True
        roam(s, 'on')
        self.assertFalse(s['repairing_cracks'])
        self.assertFalse(s['roaming'])
        self.assertEqual(len(team_bonk(s, ids[1:], 200, 200, now=190)), 2)

    def test_legacy_companion_messes_migrate_and_survive_reload(self):
        with tempfile.TemporaryDirectory() as home, patch.dict(os.environ, OMAPET_HOME=home):
            with store() as s:
                p = hatch(s, 'crab')
                p['cracks'] = [dict(id='legacy', x=10, y=10, seed=1, kind='crack', screen='')]
                p['repairing_cracks'] = True
            with store() as s:
                self.assertEqual([c['id'] for c in s['cracks']], ['legacy'])
                self.assertTrue(s['repairing_cracks'])
                switch(s, p['id'])
            with store() as s:
                self.assertEqual([c['id'] for c in s['cracks']], ['legacy'])
                repair(s, 'all')
            with store() as s: self.assertEqual(s['cracks'], [])


if __name__ == '__main__': unittest.main()
