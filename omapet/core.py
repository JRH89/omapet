from __future__ import annotations

import contextlib
import fcntl
import json
import math
import os
from pathlib import Path
import tempfile
import time
import uuid
from .characters import random_character
from .desktop import can_roam, roam_block_reason

KINDS = ('commits', 'prs', 'issues', 'reviews')
CAPS = dict(zip(KINDS, (12, 3, 3, 5)))
WEIGHTS = dict(zip(KINDS, (4, 16, 10, 12)))
ACTIONS = ('feed', 'clean', 'sleep', 'wake', 'play', 'medicine', 'vacation', 'revive')


def data_dir():
    return Path(os.environ.get('OMAPET_HOME', Path(os.environ.get('XDG_DATA_HOME', Path.home() / '.local/share')) / 'omapet'))


def fresh(name='Sprout', now=None):
    return dict(character=random_character(), version=1, id=str(uuid.uuid4()), name=name[:24], born=now or time.time(),
                updated=now or time.time(), xp=0, health=100., food=85., energy=85.,
                hygiene=100., joy=80., sleeping=False, vacation=False, hardcore=False,
                dead=False, sick=False, neglect=0., totals={k: 0 for k in KINDS},
                cracks=[], repairing_cracks=False, days={}, account=None, synced=None, battle_rewards=[], overlay=False,
                message='Welcome home. Feed, clean, play, and grow together.')


def clamp(n):
    return max(0., min(100., n))


def level(s):
    return 1 + int(math.sqrt(s['xp'] / 100))


def traits(s):
    lv = level(s)
    return dict(zip(('strength', 'stamina', 'agility', 'defense'),
                    (8 + lv * 2 + min(30, int(math.sqrt(s['totals'][k]) * 2)) for k in KINDS)))


def advance(s, now=None):
    now = time.time() if now is None else now
    hours = min(168, max(0, now - s['updated']) / 3600)
    s['updated'] = max(now, s['updated'])
    if s['vacation'] or s['dead']:
        return
    # Small integration steps make frequent widget polling and one long sleep equivalent.
    while hours > 1e-8:
        dt = min(hours, .25)
        hours -= dt
        s['food'] = clamp(s['food'] - dt * (1.3 if s['sleeping'] else 2.5))
        s['hygiene'] = clamp(s['hygiene'] - dt * 1.6)
        s['joy'] = clamp(s['joy'] - dt * 1.5)
        s['energy'] = clamp(s['energy'] + dt * (20 if s['sleeping'] else -1))
        danger = s['food'] < 10 or s['hygiene'] < 10 or s['energy'] < 5
        s['neglect'] = s['neglect'] + dt if danger else max(0, s['neglect'] - dt)
        s['sick'] = s['sick'] or s['neglect'] >= 6
        s['health'] = clamp(s['health'] + dt * (-2.5 if danger or s['sick'] else 1.5))
        if s['health'] == 0:
            if s['hardcore']:
                s['dead'] = True
                s['message'] = 'Your companion has passed away. Revive to begin caring again.'
                break
            s['health'] = 1.
    if s['sick'] and not s['dead']:
        s['message'] = 'Feeling poorly. Clean up, feed me, and give me medicine.'


def care(s, action, now=None):
    now = time.time() if now is None else now
    before = {k: s[k] for k in ('food', 'energy', 'hygiene', 'joy', 'health')}
    was_sick = s['sick']
    if action not in ACTIONS:
        raise ValueError('Unknown care action')
    if action == 'vacation':
        s['vacation'] = not s['vacation']
        s['message'] = 'Care paused. Enjoy your break!' if s['vacation'] else 'Welcome back!'
        return
    if action == 'revive':
        if not s['dead']:
            raise ValueError('Your pet is still alive')
        for key in ('health', 'food', 'energy', 'hygiene', 'joy'):
            s[key] = 70.
        s.update(dead=False, sick=False, neglect=0., message='A fresh start. Your progress is safe.')
        return
    if s['dead'] or s['vacation']:
        raise ValueError('Revive your pet or leave vacation mode first')
    if action == 'feed':
        if s['food'] > 90:
            raise ValueError('Already full')
        s['food'] = clamp(s['food'] + 30)
        s['energy'] = clamp(s['energy'] + 8)
        s['hygiene'] = clamp(s['hygiene'] - 8)
        s['message'] = 'Crunch crunch! A little energy boost, and a few crumbs.'
    elif action == 'clean':
        s['hygiene'] = 100.
        s['message'] = 'A sparkling home and a happy companion.'
    elif action == 'sleep':
        s['sleeping'] = True
        s['message'] = 'Zzz… real rest restores energy, no PR required.'
    elif action == 'wake':
        s['sleeping'] = False
        s['message'] = 'Good morning!'
    elif action == 'play':
        if s['sleeping'] or s['energy'] < 15:
            raise ValueError('Rest before playing')
        s['joy'] = clamp(s['joy'] + 25)
        s['energy'] -= 6
        s['food'] = clamp(s['food'] - 5)
        s['message'] = 'A tiny adventure!'
    elif action == 'medicine':
        if s['food'] < 25 or s['hygiene'] < 40:
            raise ValueError('Feed and clean your pet before medicine')
        s.update(sick=False, neglect=0., health=clamp(s['health'] + 25), message='Feeling better!')
    # Reward useful care, with a per-action cooldown and daily cap.
    useful = ((action == 'feed' and before['food'] < 80) or
              (action == 'clean' and before['hygiene'] < 80) or
              (action == 'play' and before['joy'] < 90) or
              (action == 'medicine' and (before['health'] < 80 or was_sick)))
    day = time.strftime('%Y-%m-%d', time.gmtime(now))
    rewards = s.setdefault('care_rewards', {'day': day, 'xp': 0, 'actions': {}})
    if rewards['day'] != day:
        rewards.update(day=day, xp=0)
    previous = rewards['actions'].get(action, -1e20)
    if useful and now - previous >= 1800:
        gain = min(12, 120 - rewards['xp'])
        s['xp'] += gain
        rewards['xp'] += gain
        rewards['actions'][action] = now
        if gain: s['message'] += f' +{gain} care XP!'
    if action == 'sleep' and not s.get('rest_started'):
        s['rest_started'] = now
    if action == 'wake':
        started = s.pop('rest_started', now)
        if now - started >= 3600 and now - rewards['actions'].get('rest', -1e20) >= 3600:
            gain = min(12, 120 - rewards['xp'])
            s['xp'] += gain
            rewards['xp'] += gain
            rewards['actions']['rest'] = now
            if gain: s['message'] += f' +{gain} rest XP!'
    s['last_action'] = action
    s['action_at'] = now


def apply_days(s, account, days, now=None, pet=None):
    pet = s if pet is None else pet
    if s['account'] and s['account'].lower() != account.lower():
        raise ValueError('This pet is bonded to another GitHub account; use a separate OMAPET_HOME')
    gained = 0
    for day, counts in days.items():
        previous = s['days'].setdefault(day, {k: 0 for k in KINDS})
        for k in KINDS:
            count = min(CAPS[k], max(0, int(counts.get(k, 0))))
            delta = max(0, count - previous[k])
            pet['totals'][k] += delta
            gained += delta * WEIGHTS[k]
            previous[k] = max(previous[k], count)
    active = [day for day, counts in days.items() if any(counts.get(k, 0) for k in KINDS)]
    if active:
        s['last_active'] = max(s.get('last_active') or '', max(active))
    s['account'] = account
    pet['xp'] += gained
    s['synced'] = now or time.time()
    s['message'] = f'GitHub synced: +{gained} XP. Every kind of contribution matters.'
    if pet is not s:
        s['message'] = f"GitHub synced for {pet['name']}: +{gained} XP."
        pet['message'] = s['message']
    return gained


def status(s):
    if s['dead']: return 'departed'
    if s['vacation']: return 'vacation'
    if s['sick']: return 'sick'
    if s['sleeping']: return 'sleeping'
    if s['food'] < 25: return 'hungry'
    if s['energy'] < 25: return 'tired'
    if s['hygiene'] < 25: return 'messy'
    if s['joy'] < 25: return 'sad'
    if s['joy'] < 60: return 'lonely'
    return 'happy'


def mood(s):
    condition = status(s)
    if condition in ('departed', 'sick', 'sleeping', 'vacation'): return condition
    return 'sad' if s['joy'] < 25 else 'lonely' if s['joy'] < 60 else 'happy'


def public(s):
    from .collection import summaries
    return {**s, 'pets': summaries(s), 'mood': mood(s), 'level': level(s), 'traits': traits(s), 'status': status(s), 'can_roam': can_roam(s), 'roam_block_reason': roam_block_reason(s)}


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd, tmp = tempfile.mkstemp(dir=path.parent)
    try:
        with os.fdopen(fd, 'w') as f:
            json.dump(value, f, ensure_ascii=True)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)


@contextlib.contextmanager
def store():
    root = data_dir()
    root.mkdir(parents=True, exist_ok=True, mode=0o700)
    with (root / 'state.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        path = root / 'pet.json'
        s = json.loads(path.read_text()) if path.exists() else fresh()
        s.setdefault('character', random_character())
        s.setdefault('desktop_view', 'simple')
        s.setdefault('escapes', True)
        s.setdefault('roaming', False)
        s.setdefault('cracks', [])
        s.setdefault('repairing_cracks', False)
        for companion in s.get('companions', {}).values():
            advance(companion)
            if not can_roam(companion): companion['roaming'] = False
        advance(s)
        if not can_roam(s) and not s['cracks']: s['roaming'] = False
        yield s
        atomic_json(path, s)
