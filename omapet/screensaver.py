"""Cosmetic, read-only pet preview and optional Omarchy idle-service integration."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import time
from .characters import CHARACTERS
from .core import data_dir

STOCK = '|| omarchy-launch-screensaver'
MARKER = '|| omapet screensaver run'


def snapshot():
    """Read appearance only; never advance or save the game state."""
    try:
        pet = json.loads((data_dir() / 'pet.json').read_text())
    except (OSError, ValueError):
        pet = {}
    character = pet.get('character', 'cat')
    return {'name': str(pet.get('name', 'Omapet'))[:24],
            'character': character if character in CHARACTERS else 'cat'}


def config_root():
    return Path(os.environ.get('XDG_CONFIG_HOME', Path.home() / '.config')) / 'omarchy'


def configure(enabled):
    """Use Omarchy's supported idle clone; never modify packaged service files."""
    config = config_root()
    record = config / 'omapet-screensaver.json'
    if not enabled:
        if not record.exists():
            return 'Omapet screensaver is not enabled.'
        saved = json.loads(record.read_text())
        subprocess.run(['omarchy', 'plugin', 'enable', 'omarchy.idle'], check=True)
        return 'Default Omarchy screensaver restored.'
    if not shutil.which('omapet'):
        raise ValueError('Install the omapet launcher before enabling the screensaver.')
    if record.exists():
        saved = json.loads(record.read_text())
        target = config / 'plugins' / saved['clone']
    else:
        clone = os.environ.get('USER') or __import__('getpass').getuser()
        clone += '.idle'
        target = config / 'plugins' / clone
        if target.exists():
            raise ValueError('An existing idle customization is present. See docs/GUIDE.md for manual integration.')
        # Validate the supported integration before switching the active service.
        stock = Path('/usr/share/omarchy/shell/plugins/services/idle/Service.qml')
        if stock.read_text().count(STOCK) != 1:
            raise ValueError('Unsupported Omarchy idle service; no settings changed.')
        subprocess.run(['omarchy', 'plugin', 'clone', 'omarchy.idle'], check=True)
        record.write_text(json.dumps({'clone': clone}) + '\n')
    service = target / 'Service.qml'
    text = service.read_text()
    if MARKER not in text:
        if text.count(STOCK) != 1:
            raise ValueError('Idle launch command was customized; no code changed.')
        shutil.copy2(service, service.with_suffix('.qml.bak-' + time.strftime('%Y%m%d-%H%M%S')))
        service.write_text(text.replace(STOCK, MARKER))
    subprocess.run(['omarchy-shell', 'shell', 'rescanPlugins'], check=True)
    subprocess.run(['omarchy', 'plugin', 'enable', target.name], check=True)
    return 'Omapet screensaver enabled. Idle timeout and screen locking are unchanged.'


def run(preview=False):
    if not shutil.which('quickshell'):
        raise ValueError('The pet screensaver requires Quickshell.')
    if subprocess.run(['omarchy-shell', 'lock', 'isLocked'], capture_output=True, text=True).stdout.strip() == 'true':
        return
    if not preview and subprocess.run(['omarchy-toggle-enabled', 'screensaver-off']).returncode == 0:
        return
    qml = Path(__file__).resolve().parent.parent / 'PetScreensaver.qml'
    # Omarchy's lock command closes screensavers by this process argument.
    subprocess.run(['org.omarchy.screensaver', '--no-duplicate', '--path', str(qml)],
                   executable=shutil.which('quickshell'), check=True)
