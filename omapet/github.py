"""Read contribution totals through the user's existing gh authentication."""
import datetime as dt
import json
import subprocess
from .core import KINDS

FIELDS = ('totalCommitContributions', 'totalPullRequestContributions',
          'totalIssueContributions', 'totalPullRequestReviewContributions')


def collect():
    # Seven UTC days, including today. Per-day high water marks prevent repeat rewards.
    today = dt.datetime.now(dt.timezone.utc).date()
    parts = []
    dates = []
    for i in range(7):
        day = today - dt.timedelta(days=i)
        start = f'{day}T00:00:00Z'
        end = f'{day}T23:59:59Z'
        parts.append(f'd{i}: contributionsCollection(from: "{start}", to: "{end}") {{ {" ".join(FIELDS)} }}')
        dates.append(str(day))
    query = '{ viewer { login ' + ' '.join(parts) + ' } }'
    try:
        result = subprocess.run(['gh', 'api', 'graphql', '-f', 'query=' + query],
                                capture_output=True, text=True, timeout=30, check=True)
    except FileNotFoundError:
        raise ValueError('Install GitHub CLI (gh), then run gh auth login') from None
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        raise ValueError('GitHub sync failed. Check gh auth status and network; your pet data is safe.') from None
    payload = json.loads(result.stdout)
    if payload.get('errors') or not payload.get('data', {}).get('viewer'):
        raise ValueError('GitHub returned incomplete contribution data; no XP changed')
    viewer = payload['data']['viewer']
    return viewer['login'], {day: dict(zip(KINDS, (viewer[f'd{i}'][f] for f in FIELDS)))
                             for i, day in enumerate(dates)}


AUTO_SYNC_INTERVAL = 60


def sync(auto=False, now=None):
    """Share one sync across UI processes without holding the pet lock during HTTP."""
    import fcntl
    import time
    from .core import data_dir, atomic_json, store, apply_days
    from .collection import find
    now = time.time() if now is None else now
    root = data_dir()
    root.mkdir(parents=True, exist_ok=True, mode=0o700)
    with (root / 'github-sync.lock').open('a') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            if auto: return None
            raise ValueError('GitHub sync is already running. Try again shortly.') from None
        meta_path = root / 'github-sync.json'
        try:
            meta = json.loads(meta_path.read_text())
            attempted = float(meta['attempted'])
        except (OSError, ValueError, KeyError, TypeError):
            attempted = None
        if auto and attempted is not None and 0 <= now - attempted < AUTO_SYNC_INTERVAL:
            return None
        with store() as s: pet_id = s['id']
        atomic_json(meta_path, {'attempted': now})
        try:
            account, days = collect()
            with store() as s:
                # Switching companions while gh runs must not redirect the XP.
                pet = find(s, pet_id)
                apply_days(s, account, days, now=now, pet=pet)
                message = s['message']
        except (ValueError, OSError, KeyError) as exc:
            atomic_json(meta_path, {'attempted': now, 'error': str(exc)})
            if auto: return None  # Offline care never needs an auth dialog or startup error.
            raise
        return message


def start_auto_sync():
    """A short-lived child keeps startup and quitting independent of network latency."""
    import sys
    from pathlib import Path
    return subprocess.Popen([sys.executable, str(Path(__file__).resolve().parent.parent / 'bin/omapet'),
                             'sync', '--auto'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                            start_new_session=True)
