"""Persistent desktop preferences and safe playtime transitions."""
import time
import math
import secrets
import uuid


def roam_block_reason(s):
    if s.get('dead'):
        return 'Revive your pet before letting it out.'
    reasons = []
    if s.get('vacation'):
        reasons.append('Leave vacation mode first.')
    if s.get('sleeping'):
        reasons.append('Your pet is sleeping. Wake it when it is rested.')
    if s.get('sick'):
        reasons.append('Your pet is sick. Feed, clean, and give it medicine.')
    if s['energy'] < 20:
        reasons.append(f"Low energy ({math.floor(s['energy'])}/100). Let your pet sleep until energy reaches 20.")
    if s['food'] < 20:
        reasons.append(f"Hungry ({math.floor(s['food'])}/100). Feed your pet until food reaches 20.")
    return '\n'.join(reasons)


def can_roam(s):
    return not roam_block_reason(s)


def configure(s, setting, value):
    if setting == 'view':
        if value not in ('simple', 'detailed', 'toggle'): raise ValueError('Choose simple or detailed')
        s['desktop_view'] = ('simple' if s.get('desktop_view', 'simple') == 'detailed' else 'detailed') if value == 'toggle' else value
    elif setting in ('roam', 'escapes'):
        if value not in ('on', 'off', 'toggle'): raise ValueError('Choose on or off')
        key = 'roaming' if setting == 'roam' else 'escapes'
        enabled = not s.get(key, key == 'escapes') if value == 'toggle' else value == 'on'
        if key == 'roaming' and enabled and not can_roam(s):
            raise ValueError(roam_block_reason(s))
        if key == 'roaming' and not enabled and s.get('cracks'):
            raise ValueError(f"Repair all {len(s['cracks'])} cracks or messes before bringing your pet home.")
        if key == 'roaming' and enabled and not s.get('roaming'):
            s['repairing_cracks'] = False
        s[key] = enabled
        if key == 'roaming':
            s['escape_at'] = time.time()
            s['message'] = 'Freedom! Click me to bring me home.' if enabled else 'Home sweet home. That was fun!'
    else: raise ValueError('Unknown desktop setting')


def position(s, x, y, screen=''):
    x, y = float(x), float(y)
    if not all(math.isfinite(v) and 0 <= v <= 100000 for v in (x, y)):
        raise ValueError('Desktop coordinates must be finite, positive screen positions')
    if not isinstance(screen, str) or not screen.isprintable() and screen:
        raise ValueError('Invalid screen name')
    s['desktop_position'] = {'x': round(x), 'y': round(y), 'screen': screen[:128]}


MAX_CRACKS = 4
BONK_COOLDOWN = 15


def _record_messes(s, x, y, screen, now, kind, participants=None):
    if kind not in ('crack', 'poop'): raise ValueError('Unknown desktop mess')
    x, y = float(x), float(y)
    if not all(math.isfinite(v) and 0 <= v <= 100000 for v in (x, y)):
        raise ValueError('Invalid impact coordinates')
    if not isinstance(screen, str) or len(screen) > 128 or (screen and not screen.isprintable()):
        raise ValueError('Invalid screen name')
    cracks = s.setdefault('cracks', [])
    if s.get('repairing_cracks'):
        raise ValueError('Repair time: no more bonks until the next outing')
    if len(cracks) >= MAX_CRACKS:
        raise ValueError('Repair the existing cracks first')
    if now - s.get('last_bonk_at', 0) < BONK_COOLDOWN:
        raise ValueError('Your pet is recovering from its last bonk')
    created = []
    for i in range(min(2 if participants else 1, MAX_CRACKS - len(cracks))):
        crack = dict(id=uuid.uuid4().hex, x=round(max(0, min(100000, x + (i * 90)))),
                     y=round(max(0, min(100000, y + (i * 35)))), screen=screen, kind=kind,
                     seed=secrets.randbits(31))
        if participants:
            crack.update(team_size=len(participants), participants=participants)
        cracks.append(crack)
        created.append(crack)
    s['last_bonk_at'] = now
    s['message'] = f"{'Oops! Clean up the poop.' if kind == 'poop' else 'Bonk! Repair the crack.'} {len(cracks)} mess(es) left."
    return created


def bonk(s, x, y, screen='', now=None, kind='crack'):
    now = time.time() if now is None else now
    if not s.get('roaming') or not s.get('overlay') or not can_roam(s):
        raise ValueError('Only a visible, healthy roaming pet can bonk the screen')
    return _record_messes(s, x, y, screen, now, kind)[0]


def team_bonk(s, ids, x, y, screen='', now=None):
    from .collection import find
    now = time.time() if now is None else now
    if len(ids) not in (2, 3, 4) or len(set(ids)) != len(ids):
        raise ValueError('Choose two to four different pets for a team bonk')
    if not s.get('overlay'): raise ValueError('Show your pets before a team bonk')
    pets = [find(s, pet_id) for pet_id in ids]
    if any(not p.get('roaming') or not can_roam(p) for p in pets):
        raise ValueError('Every teammate must be roaming, awake, healthy, and rested')
    if now - s.get('last_team_bonk_at', -1e20) < 90:
        raise ValueError('Your team needs a break before another team bonk')
    created = _record_messes(s, x, y, screen, now, 'crack', ids)
    s['last_team_bonk_at'] = now
    s['message'] = f"Team bonk! {', '.join(p['name'] for p in pets)} teamed up. Repair {len(s['cracks'])} mess(es) before heading home."
    return created


def repair(s, crack_id):
    cracks = s.get('cracks', [])
    remaining = [] if crack_id == 'all' else [c for c in cracks if c['id'] != crack_id]
    if len(remaining) == len(cracks):
        raise ValueError('That crack is already repaired')
    s['cracks'] = remaining
    s['repairing_cracks'] = True
    s['message'] = (f"Fixed! {len(remaining)} mess(es) left." if remaining
                    else 'All patched up! Click your pet to bring it home.')
