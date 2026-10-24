#!/usr/bin/env python3
"""Render the staged README examples using Omapet's production QML artwork."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent.parent
runner = shutil.which('qmltestrunner') or '/usr/lib/qt6/bin/qmltestrunner'
output = ROOT / 'docs/screenshots'
output.mkdir(parents=True, exist_ok=True)
with tempfile.TemporaryDirectory(prefix='omapet-showcase-') as tmp:
    wrapper = Path(tmp) / 'tst_showcase.qml'
    wrapper.write_text('import QtQuick\nimport ' + json.dumps((ROOT / 'scripts').as_uri()) +
                       ' as Demo\nDemo.Showcase { outputDirectory: ' + json.dumps(str(output)) + ' }\n')
    subprocess.run([runner, '-input', str(wrapper)], check=True, env={**os.environ,
        'QT_QPA_PLATFORM': 'offscreen', 'QT_QUICK_CONTROLS_STYLE': 'Basic', 'QT_QPA_PLATFORMTHEME': ''})
for name in ('desktop-escape', 'desktop-cracks', 'desktop-poop', 'developer-pets', 'group-play'):
    assert (output / (name + '.png')).stat().st_size > 1000, name
print('Rendered five staged screenshots in', output)
