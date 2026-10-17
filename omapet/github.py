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
