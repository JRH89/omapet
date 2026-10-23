import copy
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from omapet import core, collection, network
from omapet.arena import Arena


class CollectionTests(unittest.TestCase):
    def test_switch_and_reload_preserve_progress_and_household_ledger(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, OMAPET_HOME=tmp):
            with core.store() as s:
                original = s['id']
                core.apply_days(s, 'alice', {'2026-10-23': {'commits': 3}})
                s.update(overlay=True, battle_count=2, battle_day='2026-10-23', arena_team=[original])
                other = collection.hatch(s, 'crab', 'Ferris')
                other['xp'] = 900
                collection.switch(s, other['id'])
                self.assertEqual(s['xp'], 900)
                self.assertEqual(s['battle_count'], 2)
                self.assertTrue(s['overlay'])
                self.assertEqual(core.apply_days(s, 'alice', {'2026-10-23': {'commits': 3}}), 0)
            with core.store() as s:
                self.assertEqual(len(collection.all_pets(s)), 2)
                collection.switch(s, original)
                self.assertEqual(s['xp'], 12)
                self.assertEqual(s['account'], 'alice')

    def test_all_companions_age_and_vacation_is_individual(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, OMAPET_HOME=tmp):
            with core.store() as s:
                other = collection.hatch(s, 'duck')
                other.update(updated=1, vacation=True)
                first = collection.hatch(s, 'android')
                first.update(updated=1, roaming=True)
                frozen = other['food']
            with core.store() as s:
                self.assertEqual(s['companions'][other['id']]['food'], frozen)
                self.assertTrue(s['companions'][first['id']]['sick'])
                self.assertFalse(s['companions'][first['id']]['roaming'])

    def test_useful_care_levels_pets_and_cannot_be_spammed(self):
        s = core.fresh(now=1)
        s.update(food=40, hygiene=40, joy=40)
        core.care(s, 'feed', now=100)
        core.care(s, 'clean', now=100)
        core.care(s, 'play', now=100)
        self.assertEqual(s['xp'], 36)
        s['food'] = 40
        core.care(s, 'feed', now=101)
        self.assertEqual(s['xp'], 36)
        for i in range(20):
            s['food'] = 40
            core.care(s, 'feed', now=2000 + i*1800)
        self.assertEqual(s['xp'], 120)
        self.assertEqual(core.level(s), 2)
        s['food'] = 40
        core.care(s, 'feed', now=86400+2000)
        self.assertEqual(s['xp'], 132)

    def test_rest_reward_requires_real_sleep(self):
        s = core.fresh(now=1)
        core.care(s, 'sleep', now=1)
        core.care(s, 'wake', now=2)
        self.assertEqual(s['xp'], 0)
        core.care(s, 'sleep', now=10)
        core.care(s, 'sleep', now=1000)
        core.care(s, 'wake', now=3610)
        self.assertEqual(s['xp'], 12)
        core.care(s, 'wake', now=10000)
        self.assertEqual(s['xp'], 12)

    def test_loneliness_sadness_and_recovery_are_visible(self):
        s = core.fresh(now=1)
        core.advance(s, 1+15*3600)
        self.assertEqual(core.status(s), 'lonely')
        s.update(joy=10, food=10)
        self.assertEqual(core.public(s)['mood'], 'sad')
        s.update(food=80, energy=80)
        core.care(s, 'play', now=100)
        self.assertEqual(core.status(s), 'lonely')
        core.care(s, 'play', now=2000)
        self.assertEqual(core.status(s), 'happy')
        s.update(sick=True, sleeping=True)
        self.assertEqual(core.status(s), 'sick')

    def test_play_and_spar_require_distinct_fit_pets(self):
        s = core.fresh()
        a = collection.hatch(s, 'crab')
        with self.assertRaises(ValueError): collection.play_together(s, s['id'], s['id'])
        a['sleeping'] = True
        previous = copy.deepcopy(s)
        with self.assertRaises(ValueError): collection.play_together(s, s['id'], a['id'])
        self.assertEqual(s, previous)
        a['sleeping'] = False
        collection.play_together(s, s['id'], a['id'])
        b, c = collection.hatch(s, 'duck'), collection.hatch(s, 'whale')
        result = collection.spar(s, [s['id'], a['id'], b['id'], c['id']])
        self.assertTrue(result['completed'])
        self.assertTrue(all(len(team) == 2 for team in result['fighters'].values()))
        self.assertTrue(all(p['health'] == 100 for p in collection.all_pets(s)))


    def test_household_training_rewards_both_sides_and_levels_up(self):
        s = core.fresh()
        s['xp'] = 80
        peer = collection.hatch(s, 'crab')
        spectator = collection.hatch(s, 'duck')
        old_traits = core.traits(s)
        result = collection.spar(s, [s['id'], peer['id']], now=10000)
        self.assertTrue(result['completed'])
        self.assertEqual([r['xp'] for r in result['training_rewards']], [20, 20])
        self.assertTrue(result['training_rewards'][0]['leveled_up'])
        self.assertEqual(core.level(s), 2)
        self.assertTrue(all(core.traits(s)[k] > v for k, v in old_traits.items()))
        self.assertEqual((s['xp'], peer['xp'], spectator['xp']), (100, 20, 0))
        self.assertEqual((s['health'], peer['health']), (100, 100))
        self.assertEqual((s['energy'], peer['energy']), (75, 75))
        self.assertIn('+20 XP', result['log'][-1])

    def test_training_cap_is_per_pet_survives_switch_and_resets_at_utc_midnight(self):
        s = core.fresh()
        first_id = s['id']
        peer_id = collection.hatch(s, 'crab')['id']
        for _ in range(5): collection.spar(s, [first_id, peer_id], now=86399)
        self.assertEqual((s['xp'], collection.find(s, peer_id)['xp']), (100, 100))
        collection.switch(s, peer_id)
        result = collection.spar(s, [first_id, peer_id], now=86399)
        self.assertEqual([r['xp'] for r in result['training_rewards']], [0, 0])
        self.assertIn('daily training limit', s['message'])
        self.assertEqual((s['training_count'], collection.find(s, first_id)['training_count']), (5, 5))
        for pet in collection.all_pets(s): pet['energy'] = 85
        fresh = collection.hatch(s, 'duck')
        result = collection.spar(s, [peer_id, fresh['id']], now=86399)
        self.assertEqual([r['xp'] for r in result['training_rewards']], [0, 20])
        result = collection.spar(s, [first_id, peer_id], now=86400)
        self.assertEqual([r['xp'] for r in result['training_rewards']], [20, 20])
        self.assertEqual(s['training_count'], 1)

    def test_two_on_two_training_rewards_all_four_and_saves_limits(self):
        with tempfile.TemporaryDirectory() as home, patch.dict(os.environ, OMAPET_HOME=home):
            with core.store() as s:
                ids = [s['id']] + [collection.hatch(s, kind)['id'] for kind in ('crab', 'duck', 'whale')]
                collection.spar(s, ids)
            with core.store() as s:
                for pet_id in ids:
                    pet = collection.find(s, pet_id)
                    self.assertEqual((pet['xp'], pet['training_count']), (20, 1))
                collection.find(s, ids[2])['energy'] = 5
                rejected = copy.deepcopy(s)
                with self.assertRaisesRegex(ValueError, 'rested'): collection.spar(s, ids)
                self.assertEqual(s, rejected)



class ExchangeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.arena = Arena(Path(self.tmp.name)/'arena.json', 'invitation')
        self.a, self.b = [self.arena.request('/register', {'invite': 'invitation', 'name': n}, '') for n in ('Alice', 'Bob')]

    def tearDown(self): self.tmp.cleanup()

    def req(self, who, action, **body):
        return self.arena.request('/exchange/'+action, body, who['token'])

    def test_adoption_is_atomic_persistent_private_and_idempotent(self):
        pet = core.fresh()
        pet.update(xp=2500, account='private-account', days={'secret': 1})
        offer = self.req(self.a, 'offer', operation='offer', mode='adoption', pet=pet)
        self.assertEqual(self.req(self.a, 'offer', operation='offer', mode='adoption', pet=pet), offer)
        self.req(self.b, 'claim', operation='claim', listing=offer['listing'])
        self.req(self.b, 'claim', operation='claim', listing=offer['listing'])
        delivered = self.req(self.b, 'list')['deliveries'][self.b['id'] + ':claim']
        self.assertEqual(delivered['id'], pet['id'])
        self.assertEqual(delivered['xp'], 2500)
        self.assertIsNone(delivered['account'])
        self.assertFalse(self.req(self.a, 'list')['listings'])
        with self.assertRaises(ValueError): self.req(self.a, 'claim', operation='steal', listing=offer['listing'])
        restored = Arena(self.arena.path, 'invitation')
        self.assertEqual(restored.request('/exchange/list', {}, self.b['token'])['deliveries'][self.b['id'] + ':claim']['xp'], 2500)

    def test_trade_swaps_stats_and_cannot_be_claimed_for_free(self):
        high, low = core.fresh('High'), core.fresh('Low')
        high.update(xp=10000, totals=dict.fromkeys(core.KINDS, 100))
        listing = self.req(self.a, 'offer', operation='offer', mode='trade', pet=high)['listing']
        with self.assertRaises(ValueError): self.req(self.b, 'claim', operation='claim', listing=listing)
        self.req(self.b, 'claim', operation='claim', listing=listing, pet=low)
        self.assertEqual(self.req(self.b, 'list')['deliveries'][self.b['id'] + ':claim']['totals'], high['totals'])
        self.assertEqual(self.req(self.a, 'list')['deliveries'][self.b['id'] + ':claim']['id'], low['id'])

    def test_training_history_transfers_and_invalid_limits_are_rejected(self):
        pet = core.fresh()
        pet.update(training_day='2026-10-23', training_count=5)
        listing = self.req(self.a, 'offer', operation='trained', mode='adoption', pet=pet)['listing']
        self.req(self.b, 'claim', operation='trained-claim', listing=listing)
        received = next(iter(self.req(self.b, 'list')['deliveries'].values()))
        self.assertEqual((received['training_day'], received['training_count']), ('2026-10-23', 5))
        for invalid in (-1, 6, True, '5'):
            bad = core.fresh()
            bad.update(training_day='2026-10-23', training_count=invalid)
            with self.assertRaisesRegex(ValueError, 'training history'):
                self.req(self.a, 'offer', operation='invalid'+str(invalid), mode='adoption', pet=bad)

    def test_cancel_requires_owner_and_returns_pet(self):
        pet = core.fresh()
        listing = self.req(self.a, 'offer', operation='offer', mode='adoption', pet=pet)['listing']
        with self.assertRaises(ValueError): self.req(self.b, 'cancel', operation='cancel', listing=listing)
        self.req(self.a, 'cancel', operation='cancel', listing=listing)
        self.assertEqual(self.req(self.a, 'list')['deliveries'][self.a['id'] + ':cancel']['id'], pet['id'])

    def test_network_journal_recovers_lost_response_without_duplicates(self):
        with tempfile.TemporaryDirectory() as home, patch.dict(os.environ, OMAPET_HOME=home):
            core.atomic_json(Path(home)/'arena-client.json', {**self.a, 'url': 'http://arena'})
            with core.store() as s:
                outgoing = collection.hatch(s, 'octocat')
                outgoing['xp'] = 3600
            lost = True
            def call(url, route, body=None, token=''):
                nonlocal lost
                result = self.arena.request(route, body or {}, token)
                if route == '/exchange/offer' and lost:
                    lost = False
                    raise ValueError('Arena unreachable. Check its address and connection.')
                return result
            with patch('omapet.network.call', side_effect=call):
                with self.assertRaises(ValueError): network.exchange('offer', pet_id=outgoing['id'])
                with core.store() as s: self.assertIn('exchange_pending', s)
                result = network.exchange('sync')
                self.assertEqual(len(result['listings']), 1)
                with core.store() as s:
                    self.assertEqual(len(collection.all_pets(s)), 1)
                    self.assertNotIn('exchange_pending', s)
                network.exchange('cancel', listing=result['listings'][0]['id'])
                network.exchange('sync')
                with core.store() as s:
                    self.assertEqual(len(collection.all_pets(s)), 2)
                    self.assertEqual(collection.find(s, outgoing['id'])['xp'], 3600)

    def test_racing_adoptions_have_exactly_one_winner(self):
        from concurrent.futures import ThreadPoolExecutor
        import threading
        third = self.arena.request('/register', {'invite': 'invitation', 'name': 'Third'}, '')
        listing = self.req(self.a, 'offer', operation='offer', mode='adoption', pet=core.fresh())['listing']
        barrier = threading.Barrier(2)
        def claim(player):
            barrier.wait()
            try:
                self.req(player, 'claim', operation='race', listing=listing)
                return True
            except ValueError: return False
        with ThreadPoolExecutor(max_workers=2) as workers:
            self.assertEqual(sorted(workers.map(claim, [self.b, third])), [False, True])
        self.assertEqual(sum(len(self.req(p, 'list')['deliveries']) for p in (self.b, third)), 1)

    def test_full_household_collects_only_arrivals_that_fit(self):
        gifts = [core.fresh('Gift1'), core.fresh('Gift2')]
        for i, pet in enumerate(gifts):
            listing = self.req(self.b, 'offer', operation='offer'+str(i), mode='adoption', pet=pet)['listing']
            self.req(self.a, 'claim', operation='claim'+str(i), listing=listing)
        with tempfile.TemporaryDirectory() as home, patch.dict(os.environ, OMAPET_HOME=home):
            core.atomic_json(Path(home)/'arena-client.json', {**self.a, 'url': 'http://arena'})
            with core.store() as s:
                for _ in range(22): collection.hatch(s, 'duck')
            def call(url, route, body=None, token=''):
                return self.arena.request(route, body or {}, token)
            with patch('omapet.network.call', side_effect=call):
                result = network.exchange('sync')
                self.assertEqual(result['pending_deliveries'], 1)
                self.assertEqual(len(self.req(self.a, 'list')['deliveries']), 1)
                with core.store() as s:
                    self.assertEqual(len(collection.all_pets(s)), 24)
                    collection.remove(s, next(iter(s['companions'])))
                self.assertEqual(network.exchange('sync')['pending_deliveries'], 0)
                self.assertEqual(self.req(self.a, 'list')['deliveries'], {})

    def test_adoption_rejects_an_unnecessary_payment_pet(self):
        pet = core.fresh()
        listing = self.req(self.a, 'offer', operation='offer', mode='adoption', pet=pet)['listing']
        with self.assertRaisesRegex(ValueError, 'Adoption is free'):
            self.req(self.b, 'claim', operation='claim', listing=listing, pet=core.fresh())
        self.assertEqual(len(self.req(self.b, 'list')['listings']), 1)
        self.assertEqual(self.req(self.b, 'list')['deliveries'], {})

    def test_team_sizes_match_and_members_get_knocked_out(self):
        team = [dict(name=n, traits=dict.fromkeys(('strength', 'stamina', 'agility', 'defense'), 30)) for n in ('One', 'Two')]
        req = lambda player, route, body={}: self.arena.request(route, body, player['token'])
        req(self.a, '/queue', {'team': team})
        self.assertIsNone(req(self.b, '/queue')['match'])
        result = req(self.b, '/queue', {'team': team})
        self.assertEqual(len(result['match']['fighters'][self.a['id']]), 2)
        for i in range(30):
            req(self.a, '/move', {'move': 'strike'})
            result = req(self.b, '/move', {'move': 'feint'})
            if result['match']['winner']: break
        self.assertEqual(result['match']['winner'], self.a['id'])
        self.assertEqual(result['match']['hp'][self.b['id']], 0)
        self.assertTrue(all(p['hp'] == 0 for p in result['match']['fighters'][self.b['id']]))

class LiveCollectionTests(unittest.TestCase):
    def test_http_adoption_then_two_pet_battle_rewards_follow_participants(self):
        from http.server import ThreadingHTTPServer
        import threading
        from omapet.arena import handler
        with tempfile.TemporaryDirectory() as tmp:
            arena = Arena(Path(tmp)/'server.json', 'invitation')
            server = ThreadingHTTPServer(('127.0.0.1', 0), handler(arena))
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                url = f'http://127.0.0.1:{server.server_port}'
                homes = [str(Path(tmp)/n) for n in ('alice', 'bob')]
                teams = []
                for home in homes:
                    with patch.dict(os.environ, OMAPET_HOME=home):
                        network.connect(url, 'invitation')
                        with core.store() as s:
                            companion = collection.hatch(s, 'crab')
                            teams.append([s['id'], companion['id']])
                with patch.dict(os.environ, OMAPET_HOME=homes[0]):
                    with core.store() as s:
                        gift = collection.hatch(s, 'octocat')
                        gift.update(xp=2500, totals=dict.fromkeys(core.KINDS, 50))
                    listing = network.exchange('offer', pet_id=gift['id'])['listing']
                with patch.dict(os.environ, OMAPET_HOME=homes[1]):
                    network.exchange('claim', listing=listing)
                    network.exchange('sync')
                    with core.store() as s:
                        received = collection.find(s, gift['id'])
                        self.assertEqual(received['xp'], 2500)
                        self.assertEqual(received['totals'], gift['totals'])
                        core.apply_days(s, 'bob', {'2026-10-23': {'commits': 1}})
                        collection.switch(s, received['id'])
                        self.assertEqual(core.apply_days(s, 'bob', {'2026-10-23': {'commits': 1}}), 0)
                for home, team in zip(homes, teams):
                    with patch.dict(os.environ, OMAPET_HOME=home): network.request('/queue', team=team)
                for _ in range(30):
                    for home, move in zip(homes, ('strike', 'feint')):
                        with patch.dict(os.environ, OMAPET_HOME=home): result = network.request('/move', move)
                    if result['match']['winner']: break
                for i, home in enumerate(homes):
                    with patch.dict(os.environ, OMAPET_HOME=home):
                        network.request(); network.request()
                        with core.store() as s:
                            self.assertEqual(s['battle_count'], 1)
                            # Bob's non-participating adopted pet remains at exactly its gift XP.
                            if i: self.assertEqual(s['xp'], 2500)
                            rewards = [collection.find(s, p)['xp'] for p in teams[i]]
                            if i: self.assertEqual(rewards, [14, 10])  # Four earlier GitHub XP on first pet.
                            else: self.assertEqual(rewards, [30, 30])
            finally:
                server.shutdown(); server.server_close(); thread.join()


if __name__ == '__main__': unittest.main()
