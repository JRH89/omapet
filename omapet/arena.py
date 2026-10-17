"""Small authoritative, invitation-only, casual arena. No GitHub credentials leave the client."""
from __future__ import annotations
import argparse
import hashlib
import hmac
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import secrets
import threading
import time
from .core import atomic_json

MOVES = ('strike', 'guard', 'feint')
# Strike beats feint, feint beats guard, guard beats strike.
BEATS = {'strike': 'feint', 'feint': 'guard', 'guard': 'strike'}


class Arena:
    def __init__(self, path, invite):
        self.path = Path(path)
        self.invite = invite
        self.lock = threading.Lock()
        self.data = json.loads(self.path.read_text()) if self.path.exists() else {'players': {}, 'matches': {}}

    def save(self):
        atomic_json(self.path, self.data)

    def request(self, route, body, token):
        with self.lock:
            players = self.data['players']
            if route == '/register':
                if not hmac.compare_digest(str(body.get('invite', '')), self.invite):
                    raise ValueError('Invalid invitation')
                if len(players) >= 1000:
                    raise ValueError('Arena is full')
                key, secret = secrets.token_hex(12), secrets.token_urlsafe(32)
                players[key] = {'name': str(body.get('name', 'Sprout'))[:24],
                                'token': hashlib.sha256(secret.encode()).hexdigest(),
                                'queued': False, 'match': None, 'wins': 0, 'last': time.time()}
                self.save()
                return {'id': key, 'token': secret}
            digest = hashlib.sha256(token.encode()).hexdigest()
            key = next((k for k, p in players.items() if hmac.compare_digest(p['token'], digest)), None)
            if key is None:
                raise ValueError('Unknown arena identity; register first')
            p = players[key]
            p['last'] = time.time()
            # Reap inactive queue entries; abandoned matches time out and grant no reward.
            for m in self.data['matches'].values():
                if m['winner'] is None and time.time() - m['updated'] > 300:
                    m['winner'] = 'abandoned'
                    m['log'].append('Match expired after five minutes without a completed turn.')
            if route == '/queue':
                existing = self.data['matches'].get(p['match'])
                if existing and existing['winner'] is None:
                    raise ValueError('Finish your current match first')
                stats = body.get('traits', {})
                p['traits'] = {k: max(10, min(60, int(stats.get(k, 10))))
                               for k in ('strength', 'stamina', 'agility', 'defense')}
                p['queued'], p['match'] = True, None
                other = next((k for k, v in players.items() if k != key and v['queued']
                              and time.time() - v['last'] < 120), None)
                if other:
                    mid = secrets.token_hex(12)
                    ids = [other, key]
                    self.data['matches'][mid] = dict(completed=False, id=mid, players=ids, names={k: players[k]['name'] for k in ids},
                        hp={k: 80 + players[k]['traits']['stamina'] for k in ids},
                        moves={}, round=1, winner=None, log=['A friendly spar begins!'], updated=time.time())
                    for k in ids:
                        players[k].update(queued=False, match=mid)
            elif route == '/leave':
                p['queued'] = False
                m = self.data['matches'].get(p['match'])
                if m and m['winner'] is None:
                    m['winner'] = next(k for k in m['players'] if k != key)
                    m['log'].append(p['name'] + ' conceded.')
            elif route == '/move':
                m = self.data['matches'].get(p['match'])
                if not m or m['winner'] is not None:
                    raise ValueError('No active match')
                move = body.get('move')
                if move not in MOVES:
                    raise ValueError('Choose strike, guard, or feint')
                if key in m['moves']:
                    raise ValueError('Move locked; waiting for opponent')
                m['moves'][key] = move
                if len(m['moves']) == 2:
                    damage = {}
                    for attacker in m['players']:
                        defender = next(k for k in m['players'] if k != attacker)
                        a, d = m['moves'][attacker], m['moves'][defender]
                        stats, target = players[attacker]['traits'], players[defender]['traits']
                        power = stats['agility'] if a == 'feint' else stats['strength']
                        amount = max(3, 8 + power // 5 - target['defense'] // 10)
                        damage[defender] = amount + (8 if BEATS[a] == d else 0)
                    for k, amount in damage.items(): m['hp'][k] = max(0, m['hp'][k] - amount)
                    a, b = m['players']
                    m['log'].append(f"Round {m['round']}: {players[a]['name']} {m['moves'][a]} / {players[b]['name']} {m['moves'][b]} · HP {m['hp'][a]}:{m['hp'][b]}")
                    m['round'] += 1
                    m['moves'] = {}
                    m['updated'] = time.time()
                    if min(m['hp'].values()) <= 0 or m['round'] > 30:
                        m['completed'] = True
                        m['winner'] = 'draw' if m['hp'][a] == m['hp'][b] else max(m['hp'], key=m['hp'].get)
                        if m['winner'] in players: players[m['winner']]['wins'] += 1
            elif route != '/status':
                raise ValueError('Unknown arena endpoint')
            self.save()
            m = self.data['matches'].get(p['match'])
            # Opponent's choice stays secret until both moves have resolved.
            match = {k: v for k, v in m.items() if k != 'moves'} if m else None
            if match: match['submitted'] = key in m['moves']
            return {'id': key, 'queued': p['queued'], 'match': match,
                    'online': sum(time.time() - v['last'] < 120 for v in players.values())}


def handler(arena):
    class Handler(BaseHTTPRequestHandler):
        def setup(self):
            super().setup()
            self.connection.settimeout(10)

        def do_POST(self):
            try:
                length = int(self.headers.get('Content-Length', '0'))
                if length <= 0 or length > 8192: raise ValueError('Invalid request size')
                body = json.loads(self.rfile.read(length))
                if not isinstance(body, dict): raise ValueError('Expected a JSON object')
                token = self.headers.get('Authorization', '').removeprefix('Bearer ')
                result = arena.request(self.path, body, token)
                code = 200
            except (ValueError, KeyError, TypeError, OverflowError) as exc:
                code, result = 400, {'error': str(exc)}
            payload = json.dumps(result).encode()
            self.send_response(code)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def log_message(self, *_): pass
    return Handler


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=8765)
    parser.add_argument('--state', default='arena.json')
    parser.add_argument('--invite-file', required=True, help='File containing a shared invitation secret')
    args = parser.parse_args()
    invite = Path(args.invite_file).read_text().strip()
    if len(invite) < 16: parser.error('Use an invitation of at least 16 characters')
    server = ThreadingHTTPServer((args.host, args.port), handler(Arena(args.state, invite)))
    server.daemon_threads = True
    print(f'Arena listening on {args.host}:{args.port}. Use HTTPS or a trusted private network.')
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally: server.server_close()


if __name__ == '__main__': main()
