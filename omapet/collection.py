"""A household keeps one active pet and any number of companions in one atomic save."""
from copy import deepcopy
from .core import fresh, level, status, mood, care
from .characters import CHARACTERS, choose, rename

# Preferences and contribution high-water marks belong to the household, not traded pets.
HOUSEHOLD = ('companions', 'overlay', 'desktop_view', 'escapes', 'desktop_position',
             'battle_rewards', 'battle_day', 'battle_count', 'arena_team',
             'account', 'days', 'synced', 'last_active', 'exchange_pending', 'exchange_received')


def snapshot(s):
    return deepcopy({k: v for k, v in s.items() if k not in HOUSEHOLD})


def all_pets(s):
    return [s, *s.get('companions', {}).values()]


def find(s, pet_id):
    if pet_id == s['id']: return s
    try: return s.get('companions', {})[pet_id]
    except KeyError: raise ValueError('Unknown pet ID; use omapet pets list') from None


def summaries(s):
    return [dict(id=p['id'], name=p['name'], character=p['character'], level=level(p),
                 status=status(p), mood=mood(p), active=p['id'] == s['id'],
                 roaming=p.get('roaming', False))
            for p in all_pets(s)]


def hatch(s, character, name=None):
    if len(all_pets(s)) >= 24: raise ValueError('Your household is full (24 pets)')
    p = fresh(name or CHARACTERS.get(character, ('Sprout',))[0])
    choose(p, character)
    if name: rename(p, name)
    s.setdefault('companions', {})[p['id']] = p
    s['message'] = f"{p['name']} joined your household!"
    return p


def switch(s, pet_id):
    if pet_id == s['id']: return
    target = deepcopy(find(s, pet_id))
    shared = {k: s[k] for k in HOUSEHOLD if k in s}
    companions = shared.setdefault('companions', {})
    companions[s['id']] = snapshot(s)
    del companions[pet_id]
    s.clear()
    s.update(target)
    # Transferred pets never replace the recipient's GitHub identity or ledger.
    for k in HOUSEHOLD: s.pop(k, None)
    s.update(shared)
    s.setdefault('account', None)
    s.setdefault('days', {})
    s.setdefault('synced', None)
    s.setdefault('battle_rewards', [])


def remove(s, pet_id):
    if pet_id == s['id']:
        others = list(s.get('companions', {}))
        if not others: raise ValueError('Keep at least one pet in your household')
        switch(s, others[0])
    s['companions'].pop(pet_id, None)


def receive(s, pet):
    if any(p['id'] == pet['id'] for p in all_pets(s)): return
    if len(all_pets(s)) >= 24: raise ValueError('Make room in your household before collecting deliveries')
    incoming = deepcopy(pet)
    import time
    incoming['updated'] = time.time()  # Escrow is a safe shelter; needs are paused there.
    s.setdefault('companions', {})[pet['id']] = incoming


def play_together(s, first, second):
    a, b = find(s, first), find(s, second)
    if a is b: raise ValueError('Choose two different pets')
    for p in (a, b):
        if p['sleeping'] or p['dead'] or p['sick'] or p['vacation'] or p['energy'] < 15:
            raise ValueError('Both pets need to be awake, healthy and rested')
    for p in (a, b): care(p, 'play')
    s['message'] = f"{a['name']} and {b['name']} played together!"


def spar(s, ids):
    """Auto-resolve a friendly household spar with the same arena combat rules."""
    import secrets
    import tempfile
    from pathlib import Path
    from .arena import Arena, MOVES
    from .core import traits
    if len(ids) not in (2, 4) or len(set(ids)) != len(ids):
        raise ValueError('Choose two pets for 1v1, or four pets for 2v2')
    pets = [find(s, i) for i in ids]
    for p in pets:
        if p['sleeping'] or p['dead'] or p['sick'] or p['vacation'] or p['energy'] < 20:
            raise ValueError('Every pet needs to be awake, healthy and rested')
    size = len(pets) // 2
    with tempfile.TemporaryDirectory(prefix='omapet-spar-') as tmp:
        arena = Arena(Path(tmp) / 'arena.json', 'local-practice')
        players = [arena.request('/register', {'invite': 'local-practice', 'name': pets[i*size]['name']}, '') for i in range(2)]
        for i, player in enumerate(players):
            arena.request('/queue', {'team': [dict(name=p['name'], traits=traits(p)) for p in pets[i*size:(i+1)*size]]}, player['token'])
        for _ in range(30):
            moves = [secrets.choice(MOVES) for _ in players]
            for player, move in zip(players, moves):
                result = arena.request('/move', {'move': move}, player['token'])
            if result['match']['winner']: break
    for p in pets:
        p['energy'] -= 10
        p['joy'] = min(100, p['joy'] + 5)
    s['message'] = 'Friendly spar complete. No injuries; each pet used 10 energy.'
    return result['match']
