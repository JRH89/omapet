#!/usr/bin/env python3
"""Back up an atomically-written arena state, retaining fourteen daily snapshots."""
import datetime
import json
import os
from pathlib import Path
import tempfile
import sys

root = Path(sys.argv[1]).resolve()
source = root / 'state/arena.json'
if not source.exists(): raise SystemExit('No arena state yet; backup skipped.')
# One opened inode remains a complete snapshot even if the server replaces its file.
raw = source.read_bytes()
data = json.loads(raw)
if not isinstance(data.get('players'), dict) or not isinstance(data.get('matches'), dict):
    raise SystemExit('Invalid arena state; refusing to replace a backup.')
backups = root / 'backups'
backups.mkdir(mode=0o700, exist_ok=True)
stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d')
target = backups / ('arena-' + stamp + '.json')
fd, tmp = tempfile.mkstemp(dir=backups)
try:
    with os.fdopen(fd, 'wb') as f:
        f.write(raw); f.flush(); os.fsync(f.fileno())
    os.replace(tmp, target)
finally:
    if os.path.exists(tmp): os.unlink(tmp)
for old in sorted(backups.glob('arena-????-??-??.json'), reverse=True)[14:]: old.unlink()
print('Arena backup verified:', target.name)
