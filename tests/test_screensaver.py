import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from omapet.screensaver import snapshot, configure


class ScreensaverTests(unittest.TestCase):
    def test_snapshot_does_not_update_or_create_game_state(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, OMAPET_HOME=tmp):
            self.assertEqual(snapshot()['character'], 'cat')
            self.assertEqual(list(Path(tmp).iterdir()), [])
            p = Path(tmp) / 'pet.json'
            content = json.dumps(dict(name='Snow', character='duck', sleeping=True,
                                      energy=1, updated=1, cracks=[{'id': 'keep'}]))
            p.write_text(content)
            self.assertEqual(snapshot(), {'name': 'Snow', 'character': 'duck'})
            self.assertEqual(p.read_text(), content)
            self.assertEqual(list(Path(tmp).iterdir()), [p])

    def test_invalid_snapshot_uses_safe_appearance(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, OMAPET_HOME=tmp):
            p = Path(tmp) / 'pet.json'; p.write_text('{')
            self.assertEqual(snapshot()['character'], 'cat')
            p.write_text('{"character":"missing"}')
            self.assertEqual(snapshot()['character'], 'cat')

    def test_existing_idle_customization_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, XDG_CONFIG_HOME=tmp, USER='test'):
            target = Path(tmp) / 'omarchy/plugins/test.idle'
            target.mkdir(parents=True)
            with patch('omapet.screensaver.shutil.which', return_value='/bin/omapet'):
                with self.assertRaisesRegex(ValueError, 'existing idle customization'):
                    configure(True)
            self.assertEqual(list(target.iterdir()), [])

    def test_enable_changes_only_launch_command_and_disable_restores_builtin(self):
        from omapet.screensaver import STOCK, MARKER
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, XDG_CONFIG_HOME=tmp, USER='test'):
            target = Path(tmp) / 'omarchy/plugins/test.idle'
            original = 'lockTimeoutSeconds: 300\nlaunch("locked ' + STOCK + '")\n'
            def command(args, **kwargs):
                if args == ['omarchy', 'plugin', 'clone', 'omarchy.idle']:
                    target.mkdir(parents=True); (target / 'Service.qml').write_text(original)
            with patch('omapet.screensaver.shutil.which', return_value='/bin/omapet'), \
                 patch('omapet.screensaver.subprocess.run', side_effect=command) as run, \
                 patch('omapet.screensaver.Path.read_text', autospec=True) as read:
                # Only the packaged compatibility probe is synthetic.
                real_read = Path.open
                def read_file(path, *args, **kwargs):
                    if str(path).startswith('/usr/share/omarchy/'):
                        return STOCK
                    with real_read(path) as f: return f.read()
                read.side_effect = read_file
                configure(True)
                self.assertEqual((target / 'Service.qml').read_text(), original.replace(STOCK, MARKER))
                configure(False)
                run.assert_called_with(['omarchy', 'plugin', 'enable', 'omarchy.idle'], check=True)
