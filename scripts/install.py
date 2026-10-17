#!/usr/bin/env python3
"""Install this checkout's launcher; optionally install and enable its Quattro widget."""
import argparse
from pathlib import Path
import shutil
import shlex
import subprocess
import json
import time

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--quattro', action='store_true', help='Copy plugin into user config and enable it')
args = parser.parse_args()
source = Path(__file__).resolve().parent.parent
home = Path.home()
launcher = home / '.local/bin/omapet'
launcher.parent.mkdir(parents=True, exist_ok=True)
if launcher.exists() or launcher.is_symlink():
    parser.error(f'{launcher} already exists. Keep it or remove it before reinstalling.')
if args.quattro:
    import os
    config = Path(os.environ.get('XDG_CONFIG_HOME', home / '.config'))
    target = config / 'omarchy/plugins/jrh89.omapet'
    if target.exists(): parser.error(f'{target} already exists; refusing to overwrite it')
    subprocess.run(['omarchy', 'plugin', 'validate', str(source)], check=True)
    shutil.copytree(source, target, ignore=shutil.ignore_patterns('.git', '__pycache__', '.venv', 'build', '*.egg-info'))
    source = target
launcher.write_text('#!/bin/sh\nexec python3 ' + shlex.quote(str(source / 'bin/omapet')) + ' "$@"\n')
launcher.chmod(0o755)
if args.quattro:
    subprocess.run(['omarchy-shell', 'shell', 'rescanPlugins'], check=True)
    # Discovery is asynchronous: wait for the registry before enabling.
    for attempt in range(30):
        result = subprocess.run(['omarchy', 'plugin', 'list', '--json'], capture_output=True, text=True, check=True)
        if any(p['id'] == 'jrh89.omapet' for p in json.loads(result.stdout)):
            break
        time.sleep(0.2)
    else:
        raise SystemExit('Plugin copied, but discovery timed out. Run omarchy plugin enable jrh89.omapet after the shell finishes loading.')
    subprocess.run(['omarchy', 'plugin', 'enable', 'jrh89.omapet'], check=True)
print(f'Installed {launcher}. Ensure ~/.local/bin is on PATH, then run omapet.')
