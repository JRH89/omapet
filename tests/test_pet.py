import json
import os
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch
from http.server import ThreadingHTTPServer
from omapet import core, network
from omapet.arena import Arena, handler
from omapet.github import collect


class PetTests(unittest.TestCase):
    def test_sync_is_capped_and_idempotent(self):
        s = core.fresh(now=1)
        days = {'2026-10-16': dict.fromkeys(core.KINDS, 1000)}
        self.assertEqual(core.apply_days(s, 'me', days, now=2), 186)
        self.assertEqual(core.apply_days(s, 'me', days, now=3), 0)
        self.assertEqual(s['totals'], core.CAPS)

    def test_high_water_survives_deleted_contributions(self):
        s = core.fresh()
        for count in (5, 2, 5, 7):
            core.apply_days(s, 'me', {'2026-10-16': {'commits': count}})
        self.assertEqual(s['xp'], 28)

    def test_account_cannot_change(self):
        s = core.fresh()
        core.apply_days(s, 'alice', {})
        with self.assertRaises(ValueError): core.apply_days(s, 'bob', {})
        core.apply_days(s, 'ALICE', {})

    def test_vacation_freezes_care(self):
        s = core.fresh(now=1); s['vacation'] = True
        core.advance(s, 1000000)
        self.assertEqual(s['food'], 85)
        self.assertEqual(s['health'], 100)

    def test_neglect_sickness_gentle_and_hardcore(self):
        s = core.fresh(now=1)
        core.advance(s, 1 + 7 * 86400)
        self.assertTrue(s['sick'])
        self.assertFalse(s['dead'])
        self.assertEqual(s['health'], 1)
        s = core.fresh(now=1); s['hardcore'] = True
        core.advance(s, 1 + 7 * 86400)
        self.assertTrue(s['dead'])
        core.care(s, 'revive')
        self.assertFalse(s['dead'])

    def test_sleep_and_medicine(self):
        s = core.fresh(now=1); s['energy'] = 20
        core.care(s, 'sleep'); core.advance(s, 3601)
        self.assertAlmostEqual(s['energy'], 30)
        s.update(sick=True, food=5, hygiene=0)
        with self.assertRaises(ValueError): core.care(s, 'medicine')
        core.care(s, 'feed'); core.care(s, 'clean'); core.care(s, 'medicine')
        self.assertFalse(s['sick'])

    def test_polling_does_not_change_decay(self):
        a, b = core.fresh(now=1), core.fresh(now=1)
        core.advance(a, 3601)
        for i in range(1, 61): core.advance(b, 1 + i * 60)
        for k in ('food', 'energy', 'health', 'hygiene'):
            self.assertAlmostEqual(a[k], b[k])

    def test_atomic_store_rolls_back_failed_action(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, OMAPET_HOME=tmp):
            with core.store() as s: s['name'] = 'Bramble'
            with self.assertRaises(ValueError):
                with core.store() as s:
                    s['name'] = 'Lost'; raise ValueError()
            with core.store() as s: self.assertEqual(s['name'], 'Bramble')
            self.assertEqual((Path(tmp) / 'pet.json').stat().st_mode & 0o777, 0o600)

    @patch('omapet.github.subprocess.run')
    def test_graphql_all_four_metrics(self, run):
        fields = ('totalCommitContributions', 'totalPullRequestContributions', 'totalIssueContributions', 'totalPullRequestReviewContributions')
        run.return_value.stdout = json.dumps({'data': {'viewer': {'login': 'alice', **{f'd{i}': dict.fromkeys(fields, 1) for i in range(7)}}}})
        account, days = collect()
        self.assertEqual(account, 'alice')
        self.assertEqual(len(days), 7)
        self.assertTrue(all(set(d) == set(core.KINDS) for d in days.values()))
        self.assertIn('viewer', run.call_args.args[0][-1])

    @patch('omapet.github.subprocess.run')
    def test_partial_graphql_result_rejected(self, run):
        run.return_value.stdout = '{"errors": [{"message": "rate limit"}]}'
        with self.assertRaises(ValueError): collect()


class ArenaTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.arena = Arena(Path(self.tmp.name) / 'server.json', 'test-invitation-secret')
        self.alice = self.arena.request('/register', {'invite': 'test-invitation-secret', 'name': 'Alice'}, '')
        self.bob = self.arena.request('/register', {'invite': 'test-invitation-secret', 'name': 'Bob'}, '')

    def tearDown(self): self.tmp.cleanup()

    def req(self, player, route, body=None):
        return self.arena.request(route, body or {}, player['token'])

    def match(self):
        self.req(self.alice, '/queue', {'traits': dict.fromkeys(('strength','stamina','agility','defense'), 30)})
        return self.req(self.bob, '/queue')['match']

    def test_authentication(self):
        with self.assertRaises(ValueError): self.arena.request('/status', {}, 'wrong-token')
        with self.assertRaises(ValueError): self.arena.request('/register', {'invite': 'wrong'}, '')
        self.assertNotIn(self.alice['token'], self.arena.path.read_text())

    def test_hidden_moves_and_full_battle(self):
        self.match()
        for _ in range(30):
            result = self.req(self.alice, '/move', {'move': 'strike'})
            self.assertNotIn('moves', result['match'])
            self.assertTrue(result['match']['submitted'])
            with self.assertRaises(ValueError): self.req(self.alice, '/move', {'move': 'guard'})
            result = self.req(self.bob, '/move', {'move': 'feint'})
            if result['match']['winner'] is not None: break
        self.assertEqual(result['match']['winner'], self.alice['id'])
        self.assertTrue(result['match']['completed'])
        restored = Arena(self.arena.path, 'test-invitation-secret')
        self.assertEqual(restored.request('/status', {}, self.alice['token'])['match']['winner'], self.alice['id'])

    def test_concede_is_not_rewarded(self):
        self.match()
        result = self.req(self.alice, '/leave')
        self.assertEqual(result['match']['winner'], self.bob['id'])
        self.assertFalse(result['match']['completed'])

    def test_match_expiry(self):
        m = self.match()
        self.arena.data['matches'][m['id']]['updated'] = 1
        result = self.req(self.alice, '/status')
        self.assertEqual(result['match']['winner'], 'abandoned')

    def test_http_clients_and_reward_replay(self):
        server = ThreadingHTTPServer(('127.0.0.1', 0), handler(self.arena))
        thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
        try:
            url = f'http://127.0.0.1:{server.server_port}'
            with patch.dict(os.environ, OMAPET_HOME=self.tmp.name):
                network.connect(url, 'test-invitation-secret')
                client = json.loads((Path(self.tmp.name) / 'arena-client.json').read_text())
                network.request('/queue')
                self.req(self.bob, '/queue')
                for _ in range(30):
                    network.request('/move', 'strike')
                    result = self.req(self.bob, '/move', {'move': 'feint'})
                    if result['match']['winner'] is not None: break
                network.request(); network.request()
                with core.store() as s:
                    self.assertEqual(s['xp'], 30)
                    self.assertEqual(s['battle_count'], 1)
                self.assertEqual(client['url'], url)
        finally:
            server.shutdown(); server.server_close(); thread.join()


if __name__ == '__main__': unittest.main()
