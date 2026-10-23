import json
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from .core import data_dir, atomic_json, store, traits


def call(url, route, body=None, token=''):
    parsed = urlparse(url)
    if parsed.scheme not in ('http', 'https') or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError('Arena URL must be http(s) without embedded credentials')
    req = Request(url.rstrip('/') + route, data=json.dumps(body or {}).encode(),
                  headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token,
                           'User-Agent': 'Omapet/0.1.0 (+https://github.com/JRH89/omapet)'})
    try:
        with urlopen(req, timeout=8) as res:
            return json.loads(res.read(1048576))
    except HTTPError as e:
        try: message = json.loads(e.read(8192)).get('error', 'Arena request failed')
        except (ValueError, AttributeError): message = f'Arena request blocked or failed (HTTP {e.code})'
        e.close()
        error = ValueError(message)
        error.definitive = e.code in (400, 401, 403, 404, 413, 429)
        raise error from None
    except (URLError, TimeoutError):
        raise ValueError('Arena unreachable. Check its address and connection.') from None


def connect(url, invite):
    with store() as s:
        if s.get('exchange_pending'): raise ValueError('Finish your pending transfer before reconnecting')
        name = s['name']
    result = call(url, '/register', {'name': name, 'invite': invite})
    atomic_json(data_dir() / 'arena-client.json', {**result, 'url': url})


def request(route='/status', move=None, team=None):
    path = data_dir() / 'arena-client.json'
    if not path.exists(): raise ValueError('Connect first: omapet arena connect URL')
    cfg = json.loads(path.read_text())
    body = {'move': move} if move else {}
    if route == '/queue':
        with store() as s:
            from .collection import find
            pets = [find(s, i) for i in team] if team else [s]
            if len(pets) not in (1, 2) or len({p['id'] for p in pets}) != len(pets): raise ValueError('Choose one or two different pets')
            for p in pets:
                if p['dead'] or p['sick'] or p['vacation'] or p['sleeping'] or p['energy'] < 20:
                    raise ValueError('Every teammate must be awake, healthy and rested')
            body['traits'] = traits(s)
            body['team'] = [dict(name=p['name'], traits=traits(p)) for p in pets]
            queued_ids = [p['id'] for p in pets]
    result = call(cfg['url'], route, body, cfg['token'])
    if route == '/queue':
        with store() as s: s['arena_team'] = queued_ids
    m = result.get('match')
    if m and m.get('completed') and m['winner'] is not None:
        with store() as s:
            if m['id'] not in s['battle_rewards']:
                # At most five reward-bearing matches a UTC day; practice is always available.
                import datetime
                today = str(datetime.datetime.now(datetime.timezone.utc).date())
                if s.get('battle_day') != today:
                    s['battle_day'], s['battle_count'] = today, 0
                if s['battle_count'] < 5:
                    from .collection import all_pets
                    for pet in all_pets(s):
                        if pet['id'] in s.get('arena_team', [s['id']]):
                            pet['xp'] += 30 if m['winner'] == result['id'] else 10
                            pet['energy'] = max(0, pet['energy'] - 10)
                    s['battle_count'] += 1
                s['battle_rewards'].append(m['id'])
    return result


def exchange(action, pet_id=None, listing=None, mode='adoption'):
    """Journal outgoing pets before HTTP so retries cannot clone or lose a pet."""
    import uuid
    from .collection import find, snapshot, remove, receive, all_pets
    path = data_dir() / 'arena-client.json'
    if not path.exists(): raise ValueError('Connect first: omapet arena connect URL')
    cfg = json.loads(path.read_text())
    if pet_id and action not in ('offer', 'claim'):
        raise ValueError('Only offers and trades can send a pet')
    with store() as s:
        pending = s.get('exchange_pending')
        if pending and action not in ('sync', 'list'):
            raise ValueError('Finish the pending transfer with omapet pets sync first')
        if not pending and action not in ('sync', 'list'):
            body = {'operation': str(uuid.uuid4()), 'listing': listing, 'mode': mode}
            if pet_id:
                if pet_id in s.get('arena_team', []):
                    arena_status = call(cfg['url'], '/status', {}, cfg['token'])
                    match = arena_status.get('match')
                    if arena_status.get('queued') or (match and match.get('winner') is None):
                        raise ValueError('Finish or leave the arena before offering a teammate')
                if len(all_pets(s)) < 2: raise ValueError('Keep at least one pet at home')
                body['pet'] = snapshot(find(s, pet_id))
            elif action == 'offer': raise ValueError('Choose a pet to offer')
            if action in ('claim', 'cancel') and len(all_pets(s)) >= 24 and not pet_id:
                raise ValueError('Make room for another pet first')
            s['exchange_pending'] = {'route': '/exchange/' + action, 'body': body, 'pet_id': pet_id}
    with store() as s:
        pending = s.get('exchange_pending')
        result = {}
        if pending:
            try:
                result = call(cfg['url'], pending['route'], pending['body'], cfg['token'])
            except ValueError as exc:
                # A transport failure is ambiguous: retain the journal for idempotent retry.
                if getattr(exc, 'definitive', False):
                    s.pop('exchange_pending', None)
                    atomic_json(data_dir() / 'pet.json', s)
                raise
            if pending['pet_id']: remove(s, pending['pet_id'])
            s.pop('exchange_pending', None)
        # Commit outgoing removal BEFORE fetching incoming deliveries, even if HTTP fails.
        atomic_json(data_dir() / 'pet.json', s)
        board = call(cfg['url'], '/exchange/list', {}, cfg['token'])
        seen = s.setdefault('exchange_received', [])
        for delivery, pet in board['deliveries'].items():
            if delivery not in seen:
                if len(all_pets(s)) >= 24 and not any(p['id'] == pet['id'] for p in all_pets(s)):
                    continue  # Keep surplus arrivals safely in escrow until there is room.
                receive(s, pet)
                seen.append(delivery)
        atomic_json(data_dir() / 'pet.json', s)
        acknowledged = [d for d in board['deliveries'] if d in seen]
        if acknowledged:
            call(cfg['url'], '/exchange/ack', {'deliveries': acknowledged}, cfg['token'])
        return {**result, 'pending_deliveries': len(board['deliveries']) - len(acknowledged), 'listings': [dict(v, mine=v['owner'] == cfg['id']) for v in board['listings']]}
