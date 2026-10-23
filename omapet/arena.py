"""Small authoritative, invitation-only, casual arena. No GitHub credentials leave the client."""
from __future__ import annotations
import argparse
import hashlib
import hmac
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import math
import socket
from collections import OrderedDict
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
            if not isinstance(body, dict): raise ValueError('Expected a JSON object')
            if route == '/register':
                name = body.get('name', 'Sprout')
                if not isinstance(name, str) or not name.strip() or len(name) > 24 or not name.isprintable():
                    raise ValueError('Pet name must be 1–24 printable characters')
                if not isinstance(body.get('invite'), str): raise ValueError('Invalid invitation')
            if route == '/queue':
                team = body.get('team')
                if team is not None:
                    if not isinstance(team, list) or len(team) not in (1, 2): raise ValueError('Choose one or two pets')
                    for member in team:
                        if not isinstance(member, dict) or not isinstance(member.get('name'), str) or not member['name'].isprintable() or not 1 <= len(member['name']) <= 24: raise ValueError('Invalid team member')
                        member_stats = member.get('traits')
                        if not isinstance(member_stats, dict): raise ValueError('Invalid team traits')
                        for value in member_stats.values():
                            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value): raise ValueError('Invalid team traits')
                stats = body.get('traits', {})
                if not isinstance(stats, dict): raise ValueError('Invalid traits')
                for key in ('strength', 'stamina', 'agility', 'defense'):
                    value = stats.get(key, 10)
                    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
                        raise ValueError('Traits must be finite numbers')
            players = self.data['players']
            if route == '/register':
                if not hmac.compare_digest(str(body.get('invite', '')), self.invite):
                    raise ValueError('Invalid invitation')
                if len(players) >= 1000:
                    raise ValueError('Arena is full')
                key, secret = secrets.token_hex(12), secrets.token_urlsafe(32)
                players[key] = {'name': name.strip(),
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
            if route.startswith('/exchange/'):
                from .exchange import request
                result = request(self.data, key, route, body)
                self.save()
                return result
            # Reap inactive queue entries; abandoned matches time out and grant no reward.
            for m in self.data['matches'].values():
                if m['winner'] is None and time.time() - m['updated'] > 300:
                    m['winner'] = 'abandoned'
                    m['log'].append('Match expired after five minutes without a completed turn.')
            if route == '/queue':
                # Bound saved history without deleting any active match.
                finished = sorted((m for m in self.data['matches'].values() if m['winner'] is not None),
                                  key=lambda m: m['updated'], reverse=True)
                for old in finished[1000:]: self.data['matches'].pop(old['id'], None)
                existing = self.data['matches'].get(p['match'])
                if existing and existing['winner'] is None:
                    raise ValueError('Finish your current match first')
                stats = body.get('traits', {})
                p['traits'] = {k: max(10, min(60, int(stats.get(k, 10))))
                               for k in ('strength', 'stamina', 'agility', 'defense')}
                team = body.get('team') or [{'name': p['name'], 'traits': p['traits']}]
                p['team'] = [dict(name=t['name'], traits={k: max(10, min(60, int(t['traits'].get(k, 10)))) for k in p['traits']}) for t in team]
                p['queued'], p['match'] = True, None
                other = next((k for k, v in players.items() if k != key and v['queued']
                              and len(v.get('team', [None])) == len(p['team'])
                              and time.time() - v['last'] < 120), None)
                if other:
                    mid = secrets.token_hex(12)
                    ids = [other, key]
                    self.data['matches'][mid] = dict(completed=False, id=mid, players=ids, names={k: players[k]['name'] for k in ids},
                        hp={k: 80 + players[k]['traits']['stamina'] for k in ids},
                        moves={}, round=1, winner=None, log=['A friendly spar begins!'], updated=time.time())
                    match = self.data['matches'][mid]
                    match['fighters'] = {k: [dict(name=t['name'], traits=t['traits'], hp=80+t['traits']['stamina'], max_hp=80+t['traits']['stamina']) for t in players[k].get('team', [{'name': players[k]['name'], 'traits': players[k]['traits']}])] for k in ids}
                    match['hp'] = {k: sum(t['hp'] for t in match['fighters'][k]) for k in ids}
                    match['max_hp'] = dict(match['hp'])
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
                        fighters = m.get('fighters')
                        attackers = [t['traits'] for t in fighters[attacker] if t['hp'] > 0] if fighters else [players[attacker]['traits']]
                        target = next(t['traits'] for t in fighters[defender] if t['hp'] > 0) if fighters else players[defender]['traits']
                        damage[defender] = sum(max(3, 8 + stats['agility' if a == 'feint' else 'strength'] // 5 - target['defense'] // 10) + (8 if BEATS[a] == d else 0) for stats in attackers)
                    for k, amount in damage.items():
                        m['hp'][k] = max(0, m['hp'][k] - amount)
                        if m.get('fighters'):
                            for fighter in m['fighters'][k]:
                                hit = min(fighter['hp'], amount)
                                fighter['hp'] -= hit
                                amount -= hit
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


class RequestLimits:
    """Bounded per-IP throttles; caller must only trust proxy headers on loopback."""
    def __init__(self):
        self.entries = OrderedDict()
        self.lock = threading.Lock()

    def allow(self, peer, registration=False, now=None):
        now = time.monotonic() if now is None else now
        with self.lock:
            for key, capacity, rate in [('global', 120, 60),
                                         ('ip:' + peer, 30, 5)] + (
                    [('registrations', 20, 1/3), ('register:' + peer, 3, 1/60)] if registration else []):
                tokens, updated = self.entries.pop(key, (capacity, now))
                tokens = min(capacity, tokens + max(0, now-updated)*rate)
                allowed = tokens >= 1
                self.entries[key] = (tokens-1 if allowed else tokens, now)
                while len(self.entries) > 4096: self.entries.popitem(last=False)
                if not allowed: return False
            return True


class ArenaHTTPServer(ThreadingHTTPServer):
    daemon_threads = True
    request_queue_size = 32

    def __init__(self, address, request_handler):
        self.slots = threading.BoundedSemaphore(16)
        super().__init__(address, request_handler)

    def process_request(self, request, address):
        if not self.slots.acquire(blocking=False):
            self.shutdown_request(request)
            return
        try: super().process_request(request, address)
        except BaseException:
            self.slots.release()
            raise

    def process_request_thread(self, request, address):
        try: super().process_request_thread(request, address)
        finally: self.slots.release()


def handler(arena, trust_cloudflare=False):
    limits = RequestLimits()
    class Handler(BaseHTTPRequestHandler):
        def setup(self):
            super().setup()
            self.connection.settimeout(5)

        server_version = 'OmapetArena'
        sys_version = ''

        def respond(self, code, result, html=False, content_type=None):
            payload = result.encode() if html else json.dumps(result).encode()
            try:
                self.send_response(code)
                self.send_header('Content-Type', content_type or ('text/html; charset=utf-8' if html else 'application/json'))
                self.send_header('Referrer-Policy', 'no-referrer')
                self.send_header('Content-Security-Policy', "default-src 'none'; img-src 'self'; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'")
                self.send_header('Content-Length', str(len(payload)))
                self.send_header('Cache-Control', 'no-store')
                self.send_header('X-Content-Type-Options', 'nosniff')
                self.send_header('Connection', 'close')
                if code == 429: self.send_header('Retry-After', '60')
                self.end_headers()
                self.wfile.write(payload)
            except (OSError, socket.timeout): pass
            self.close_connection = True

        def peer(self):
            # Only enable this behind a dedicated, loopback-only cloudflared origin.
            if trust_cloudflare and self.client_address[0] in ('127.0.0.1', '::1'):
                import ipaddress
                try: return str(ipaddress.ip_address(self.headers.get('CF-Connecting-IP', '')))
                except ValueError: pass
            return self.client_address[0]

        def do_GET(self):
            if self.path in ('/', '/index.html'):
                from .arena_page import PAGE
                self.respond(200, PAGE, html=True)
            elif self.path == '/favicon.svg':
                from .arena_page import FAVICON
                self.respond(200, FAVICON, html=True, content_type='image/svg+xml')
            elif self.path == '/healthz': self.respond(200, {'ok': True})
            else: self.respond(404, {'error': 'Not found'})

        def do_POST(self):
            if self.path not in ('/register', '/status', '/queue', '/leave', '/move',
                                 '/exchange/list', '/exchange/offer', '/exchange/claim', '/exchange/cancel', '/exchange/ack'):
                self.respond(404, {'error': 'Not found'}); return
            if not limits.allow(self.peer(), self.path == '/register'):
                self.respond(429, {'error': 'Too many requests; try again shortly'}); return
            try:
                if self.headers.get('Transfer-Encoding'): raise ValueError('Chunked requests are not supported')
                length = int(self.headers.get('Content-Length', '0'))
                if length <= 0 or length > 8192: raise ValueError('Invalid request size')
                raw = self.rfile.read(length)
                if len(raw) != length: raise ValueError('Incomplete request')
                body = json.loads(raw)
                if not isinstance(body, dict): raise ValueError('Expected a JSON object')
                token = self.headers.get('Authorization', '').removeprefix('Bearer ')
                result = arena.request(self.path, body, token)
                code = 200
            except (ValueError, KeyError, TypeError, OverflowError, UnicodeError) as exc:
                code, result = 400, {'error': str(exc)}
            except (OSError, socket.timeout):
                self.respond(408, {'error': 'Request timed out'}); return
            self.respond(code, result)

        def log_message(self, *_): pass
    return Handler


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--trust-cloudflare', action='store_true', help='Trust CF-Connecting-IP from a loopback-only tunnel origin')
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=8765)
    parser.add_argument('--state', default='arena.json')
    parser.add_argument('--invite-file', required=True, help='File containing a shared invitation secret')
    args = parser.parse_args()
    invite = Path(args.invite_file).read_text().strip()
    if len(invite) < 16: parser.error('Use an invitation of at least 16 characters')
    if args.trust_cloudflare and args.host not in ('127.0.0.1', '::1'):
        parser.error('--trust-cloudflare requires a loopback listener')
    server = ArenaHTTPServer((args.host, args.port), handler(Arena(args.state, invite), args.trust_cloudflare))
    server.daemon_threads = True
    print(f'Arena listening on {args.host}:{args.port}. Use HTTPS or a trusted private network.')
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally: server.server_close()


if __name__ == '__main__': main()
