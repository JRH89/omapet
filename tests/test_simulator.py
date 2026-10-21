import json
import os
from pathlib import Path
import random
import tempfile
import unittest
from unittest.mock import patch
from omapet.core import fresh
from omapet.simulator import Practice, appearance


class SimulatorTests(unittest.TestCase):
    def test_real_rules_hidden_moves_and_completed_match(self):
        game=Practice('Snow','duck',dict.fromkeys(('strength','stamina','agility','defense'),30),random.Random(5))
        try:
            for _ in range(30):
                committed=game.bot_move
                r=game.submit('strike')
                self.assertTrue(r['match']['submitted'])
                self.assertNotIn('moves',r['match'])
                self.assertEqual(committed,game.bot_move)
                r=game.resolve()
                self.assertFalse(r['match']['submitted'])
                self.assertNotIn('moves',r['match'])
                if r['match']['winner'] is not None:break
            self.assertTrue(r['match']['completed'])
            self.assertLessEqual(r['match']['round'],31)
        finally:
            path=Path(game.tmp.name);game.close()
        self.assertFalse(path.exists())

    def test_practice_never_changes_real_pet_or_connection(self):
        with tempfile.TemporaryDirectory() as tmp,patch.dict(os.environ,OMAPET_HOME=tmp):
            root=Path(tmp);pet=fresh();pet.update(name='Snow',character='duck',energy=1,sleeping=True)
            files={'pet.json':json.dumps(pet),'arena-client.json':'{"token":"keep-private"}'}
            for name,value in files.items():(root/name).write_text(value)
            name,kind,stats=appearance();self.assertEqual((name,kind),('Snow','duck'))
            game=Practice(name,kind,stats,random.Random(1))
            try:game.submit('guard');game.resolve()
            finally:game.close()
            self.assertEqual({p.name:p.read_text() for p in root.iterdir()},files)

    def test_preview_does_not_create_a_real_pet(self):
        with tempfile.TemporaryDirectory() as tmp,patch.dict(os.environ,OMAPET_HOME=tmp):
            self.assertEqual(appearance()[1],'cat')
            self.assertEqual(list(Path(tmp).iterdir()),[])
