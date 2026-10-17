#!/usr/bin/env python3
"""Build a reproducible source archive from an explicit set of release files."""
import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile
from check_release import ROOT, check

check()
version = json.loads((ROOT / 'manifest.json').read_text())['version']
root_files = ['manifest.json', 'pyproject.toml', 'README.md', 'LICENSE', 'CHANGELOG.md',
              'PUBLISHING.md', 'preview.png', '.gitignore']
files = [ROOT / f for f in root_files] + list(ROOT.glob('*.qml'))
allowed = {'.py', '.qml', '.md', '.png', '.jsonc', '.css', '.service', '.timer', '.yml'}
for directory in ('omapet', 'scripts', 'integrations', 'docs', 'tests', '.github'):
    files.extend(p for p in (ROOT / directory).rglob('*') if p.is_file() and p.suffix in allowed
                 and '__pycache__' not in p.parts)
files.append(ROOT / 'bin/omapet')
out = ROOT / 'dist'
out.mkdir(exist_ok=True)
archive = out / f'omapet-{version}.tar.gz'
with archive.open('wb') as raw, gzip.GzipFile(filename='', mode='wb', fileobj=raw, mtime=0) as gz:
    with tarfile.open(fileobj=gz, mode='w') as tar:
        for path in sorted(set(files)):
            if path.is_symlink(): raise ValueError(f'Symlink forbidden: {path}')
            content = path.read_bytes()
            info = tarfile.TarInfo(f'omapet-{version}/{path.relative_to(ROOT).as_posix()}')
            info.size = len(content)
            info.mode = 0o755 if path == ROOT / 'bin/omapet' else 0o644
            tar.addfile(info, io.BytesIO(content))
digest = hashlib.sha256(archive.read_bytes()).hexdigest()
archive.with_suffix(archive.suffix + '.sha256').write_text(f'{digest}  {archive.name}\n')
print(archive)
print('SHA256:', digest)
