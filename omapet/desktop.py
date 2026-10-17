"""Persistent desktop preferences and safe playtime transitions."""
import time
import math


def can_roam(s):
    return not any(s.get(k, False) for k in ('sleeping', 'vacation', 'dead', 'sick')) and s['energy'] >= 20 and s['food'] >= 20


def configure(s, setting, value):
    if setting == 'view':
        if value not in ('simple', 'detailed', 'toggle'): raise ValueError('Choose simple or detailed')
        s['desktop_view'] = ('simple' if s.get('desktop_view', 'simple') == 'detailed' else 'detailed') if value == 'toggle' else value
    elif setting in ('roam', 'escapes'):
        if value not in ('on', 'off', 'toggle'): raise ValueError('Choose on or off')
        key = 'roaming' if setting == 'roam' else 'escapes'
        enabled = not s.get(key, key == 'escapes') if value == 'toggle' else value == 'on'
        if key == 'roaming' and enabled and not can_roam(s):
            raise ValueError('Your companion needs to be awake, healthy, fed, and rested to roam')
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
