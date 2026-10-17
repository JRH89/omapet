#!/usr/bin/env python3
"""Check the portable release contract, without reading the user's pet data."""
import json
from pathlib import Path
import subprocess
import sys
import tomllib

ROOT = Path(__file__).resolve().parent.parent


def check():
    manifest = json.loads((ROOT / 'manifest.json').read_text())
    project = tomllib.loads((ROOT / 'pyproject.toml').read_text())['project']
    assert manifest['version'] == project['version'], 'Manifest and Python versions differ'
    assert manifest['schemaVersion'] == 1
    assert manifest['id'] == 'jrh89.omapet'
    assert manifest['license'] == 'MIT'
    for entry in manifest['entryPoints'].values():
        path = Path(entry)
        assert not path.is_absolute() and '..' not in path.parts
        assert (ROOT / path).is_file(), f'Missing entry point: {entry}'
    for name in ['README.md', 'LICENSE', 'CHANGELOG.md', 'PUBLISHING.md', 'preview.png',
                 'docs/screenshots/widget-compact.png', 'docs/screenshots/widget-detailed.png',
                 'docs/screenshots/tui.png', 'docs/release/marketplace-submission.md']:
        assert (ROOT / name).is_file(), f'Missing release file: {name}'
    for directory in ('omapet', 'bin', 'integrations', 'scripts', 'tests', 'docs'):
        for path in (ROOT / directory).rglob('*'):
            assert not path.is_symlink(), f'Symlink forbidden in release: {path}'
    subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-v'], cwd=ROOT, check=True)
    print(f"Release {manifest['version']}: portable checks passed")


if __name__ == '__main__': check()
