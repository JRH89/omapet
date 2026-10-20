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
            return json.loads(res.read(65536))
    except HTTPError as e:
        try: message = json.loads(e.read(8192)).get('error', 'Arena request failed')
        except (ValueError, AttributeError): message = f'Arena request blocked or failed (HTTP {e.code})'
        e.close()
        raise ValueError(message) from None
    except (URLError, TimeoutError):
        raise ValueError('Arena unreachable. Check its address and connection.') from None


def connect(url, invite):
    with store() as s: name = s['name']
    result = call(url, '/register', {'name': name, 'invite': invite})
    atomic_json(data_dir() / 'arena-client.json', {**result, 'url': url})


def request(route='/status', move=None):
    path = data_dir() / 'arena-client.json'
    if not path.exists(): raise ValueError('Connect first: omapet arena connect URL')
    cfg = json.loads(path.read_text())
    body = {'move': move} if move else {}
    if route == '/queue':
        with store() as s:
            if s['dead'] or s['sick'] or s['vacation'] or s['sleeping'] or s['energy'] < 20:
                raise ValueError('Your pet needs to be awake, healthy, and rested to spar')
            body['traits'] = traits(s)
    result = call(cfg['url'], route, body, cfg['token'])
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
                    s['xp'] += 30 if m['winner'] == result['id'] else 10
                    s['battle_count'] += 1
                    s['energy'] = max(0, s['energy'] - 10)
                s['battle_rewards'].append(m['id'])
    return result
