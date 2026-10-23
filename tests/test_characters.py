import unittest
from unittest.mock import patch
from omapet.characters import CHARACTERS, CHARACTER_KEYS, choose, rename
from omapet.core import fresh, care


class CharacterTests(unittest.TestCase):
    def test_twenty_characters_and_random_assignment(self):
        self.assertEqual(len(CHARACTERS), 20)
        with patch('omapet.core.random_character', return_value='frog'):
            self.assertEqual(fresh()['character'], 'frog')
        with patch('omapet.characters.random_character', return_value='robot'):
            s = fresh(); choose(s, 'random')
            self.assertEqual(s['character'], 'robot')

    def test_selection_preserves_progress_and_name(self):
        s = fresh(); s.update(name='Bramble', xp=450)
        for kind in CHARACTERS:
            choose(s, kind)
            self.assertEqual((s['character'], s['name'], s['xp']), (kind, 'Bramble', 450))
        with self.assertRaises(ValueError): choose(s, 'invalid')
        self.assertEqual(s['character'], tuple(CHARACTERS)[-1])
        self.assertEqual(len(CHARACTER_KEYS), len(CHARACTERS))
        self.assertEqual(len(set(CHARACTER_KEYS)), len(CHARACTER_KEYS))

    def test_rename_validation(self):
        s = fresh()
        rename(s, '  Fern  ')
        self.assertEqual(s['name'], 'Fern')
        with self.assertRaises(ValueError): rename(s, '\n')
        self.assertEqual(s['name'], 'Fern')

    def test_successful_actions_emit_animation_events(self):
        s = fresh(); s['food'] = 40
        for action in ('feed', 'clean', 'sleep', 'wake'):
            care(s, action)
            self.assertEqual(s['last_action'], action)
            self.assertGreater(s['action_at'], 0)
        s['food'] = 100
        previous = s['action_at']
        with self.assertRaisesRegex(ValueError, 'Already full'): care(s, 'feed')
        self.assertEqual(s['action_at'], previous)


if __name__ == '__main__': unittest.main()
