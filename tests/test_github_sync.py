import json
import os
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch
from omapet import core, github, collection


class StartupSyncTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.env = patch.dict(os.environ, OMAPET_HOME=self.tmp.name)
        self.env.start()
        self.addCleanup(self.tmp.cleanup)
        self.addCleanup(self.env.stop)
        self.days = {'2026-10-23': {'commits': 3}}

    def test_startup_is_coalesced_and_manual_sync_can_bypass_cooldown(self):
        with patch('omapet.github.collect', return_value=('alice', self.days)) as collect:
            self.assertIn('+12 XP', github.sync(auto=True, now=100))
            self.assertIsNone(github.sync(auto=True, now=159))
            self.assertEqual(collect.call_count, 1)
            self.assertIn('+0 XP', github.sync(now=159))
            self.assertEqual(collect.call_count, 2)
            self.assertIsNone(github.sync(auto=True, now=160))
            github.sync(auto=True, now=219)
            self.assertEqual(collect.call_count, 3)
        with core.store() as s: self.assertEqual(s['xp'], 12)

    def test_offline_startup_is_quiet_and_does_not_erase_progress(self):
        with core.store() as s: s['xp'] = 100
        with patch('omapet.github.collect', side_effect=ValueError('Not authenticated')) as collect:
            self.assertIsNone(github.sync(auto=True, now=100))
            self.assertIsNone(github.sync(auto=True, now=101))
            self.assertEqual(collect.call_count, 1)
            with self.assertRaisesRegex(ValueError, 'Not authenticated'): github.sync(now=102)
        with core.store() as s: self.assertEqual(s['xp'], 100)
        with patch('omapet.github.collect', return_value=('alice', self.days)):
            self.assertIn('+12 XP', github.sync(now=103))

    def test_care_is_not_locked_during_http_and_switch_does_not_redirect_xp(self):
        with core.store() as s:
            original = s['id']
            peer = collection.hatch(s, 'crab')['id']
        def collect():
            with core.store() as s:
                collection.switch(s, peer)
                s['food'] = 40
                core.care(s, 'feed')
            return 'alice', self.days
        with patch('omapet.github.collect', side_effect=collect):
            github.sync(auto=True)
        with core.store() as s:
            self.assertEqual(s['id'], peer)
            self.assertEqual(s['xp'], 12)  # Only the care reward on this pet.
            self.assertEqual(collection.find(s, original)['xp'], 12)
            self.assertEqual(s['account'], 'alice')
            self.assertEqual(core.apply_days(s, 'alice', self.days), 0)

    def test_overlapping_ui_requests_do_not_repeat_the_network_call(self):
        entered, finish = threading.Event(), threading.Event()
        failures = []
        def collect():
            entered.set()
            if not finish.wait(5): raise RuntimeError('test timed out')
            return 'alice', self.days
        def sync():
            try: github.sync(auto=True, now=100)
            except Exception as exc: failures.append(exc)
        with patch('omapet.github.collect', side_effect=collect) as collect_mock:
            thread = threading.Thread(target=sync)
            thread.start()
            try:
                self.assertTrue(entered.wait(5))
                self.assertIsNone(github.sync(auto=True, now=100))
                with self.assertRaisesRegex(ValueError, 'already running'): github.sync(now=100)
                with core.store() as s: self.assertEqual(s['xp'], 0)
            finally:
                finish.set()
                thread.join(5)
            self.assertFalse(thread.is_alive())
            self.assertEqual(failures, [])
            self.assertEqual(collect_mock.call_count, 1)

    def test_departed_target_does_not_consume_the_household_ledger(self):
        with core.store() as s:
            original = s['id']
            collection.hatch(s, 'duck')
        def collect():
            with core.store() as s: collection.remove(s, original)
            return 'alice', self.days
        with patch('omapet.github.collect', side_effect=collect): self.assertIsNone(github.sync(auto=True))
        with core.store() as s:
            self.assertEqual(s['xp'], 0)
            self.assertEqual(s['days'], {})

    def test_background_child_uses_cli_and_does_not_need_tui_to_stay_open(self):
        root = Path(self.tmp.name)
        fake_bin = root / 'bin'
        fake_bin.mkdir()
        payload = {'data': {'viewer': {'login': 'alice', **{
            'd'+str(i): dict.fromkeys(github.FIELDS, 1) for i in range(7)}}}}
        fake_gh = fake_bin / 'gh'
        import shlex
        fake_gh.write_text('#!/bin/sh\nprintf %s ' + shlex.quote(json.dumps(payload)) + '\n')
        fake_gh.chmod(0o755)
        with patch.dict(os.environ, PATH=str(fake_bin) + ':' + os.environ['PATH']):
            process = github.start_auto_sync()
            self.assertEqual(process.wait(timeout=10), 0)
        with core.store() as s:
            self.assertEqual(s['account'], 'alice')
            self.assertEqual(s['xp'], 7 * sum(core.WEIGHTS.values()))
        self.assertTrue((root / 'github-sync.json').exists())


if __name__ == '__main__': unittest.main()
