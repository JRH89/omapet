import json
from pathlib import Path
import tempfile
import threading
import unittest
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from omapet.arena import Arena, ArenaHTTPServer, RequestLimits, handler


class HostingTests(unittest.TestCase):
    def test_registration_and_queue_validation_before_mutation(self):
        with tempfile.TemporaryDirectory() as tmp:
            arena = Arena(Path(tmp)/'arena.json', 'test-invitation-secret')
            for name in ['bad\nname', '\x1b[2J', '', 'x'*25, []]:
                with self.assertRaises(ValueError):
                    arena.request('/register', {'name': name, 'invite': arena.invite}, '')
            self.assertFalse(arena.data['players'])
            player = arena.request('/register', {'name': 'Snow', 'invite': arena.invite}, '')
            before = json.dumps(arena.data)
            for traits in [[], {'strength': float('nan')}, {'agility': True}]:
                with self.assertRaises(ValueError): arena.request('/queue', {'traits': traits}, player['token'])
                self.assertEqual(json.dumps(arena.data), before)

    def test_throttles_registration_and_bounds_memory(self):
        limits = RequestLimits()
        for _ in range(3): self.assertTrue(limits.allow('one', True, now=100))
        self.assertFalse(limits.allow('one', True, now=100))
        self.assertTrue(limits.allow('one', True, now=161))
        for i in range(5000): limits.allow(str(i), now=100+i)
        self.assertLessEqual(len(limits.entries), 4096)

    def test_health_malformed_requests_and_request_limits(self):
        with tempfile.TemporaryDirectory() as tmp:
            arena = Arena(Path(tmp)/'arena.json', 'test-invitation-secret')
            server = ArenaHTTPServer(('127.0.0.1', 0), handler(arena, trust_cloudflare=True))
            thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
            base = f'http://127.0.0.1:{server.server_port}'
            try:
                with urlopen(base+'/healthz') as res:
                    self.assertEqual(json.load(res), {'ok': True})
                    self.assertEqual(res.headers['Cache-Control'], 'no-store')
                with urlopen(base+'/') as res:
                    page = res.read().decode()
                    self.assertEqual(res.status, 200)
                    self.assertIn('text/html', res.headers['Content-Type'])
                    self.assertIn('frame-ancestors', res.headers['Content-Security-Policy'])
                    self.assertIn('Join the arena', page)
                    self.assertIn('by Codefront Labs', page)
                    self.assertIn('href="/favicon.svg"', page)
                    self.assertNotIn(arena.invite, page)
                    self.assertFalse(arena.data['players'])
                with urlopen(base+'/favicon.svg') as res:
                    self.assertEqual(res.headers['Content-Type'], 'image/svg+xml')
                    self.assertIn(b'<svg', res.read())
                for body in [b'null', b'[]', b'\xff', b'{']:
                    with self.assertRaises(HTTPError) as err:
                        urlopen(Request(base+'/status', data=body))
                    self.assertEqual(err.exception.code, 400)
                    err.exception.close()
                for i in range(4):
                    try: urlopen(Request(base+'/register', data=b'{"invite":"wrong"}'))
                    except HTTPError as err:
                        code = err.code; err.close()
                self.assertEqual(code, 429)
            finally:
                server.shutdown(); server.server_close(); thread.join()
