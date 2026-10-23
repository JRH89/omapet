"""Arena-side escrow. One lock and one save cover both sides of every exchange."""
from copy import deepcopy
import math
import time
import uuid
from .characters import CHARACTERS
from .core import KINDS, level, traits


def validate_pet(raw):
    if not isinstance(raw, dict): raise ValueError('Invalid pet')
    try:
        uuid.UUID(raw['id'])
        if raw['character'] not in CHARACTERS: raise ValueError()
        if not isinstance(raw['name'], str) or not raw['name'].strip() or len(raw['name']) > 24 or not raw['name'].isprintable(): raise ValueError()
        numeric = ('xp', 'born', 'updated', 'health', 'food', 'energy', 'hygiene', 'joy', 'neglect')
        for k in numeric:
            n = raw[k]
            if isinstance(n, bool) or not isinstance(n, (int, float)) or not math.isfinite(n) or not 0 <= n <= 1e12: raise ValueError()
        for k in ('health', 'food', 'energy', 'hygiene', 'joy'):
            if raw[k] > 100: raise ValueError()
        if not isinstance(raw['totals'], dict): raise ValueError()
        for k in KINDS:
            n = raw['totals'][k]
            if type(n) is not int or not 0 <= n <= 10**9: raise ValueError()
    except (KeyError, TypeError, AttributeError, ValueError):
        raise ValueError('Invalid pet profile') from None
    training = {}
    if 'training_day' in raw or 'training_count' in raw:
        from datetime import date
        try:
            training_day = raw['training_day']
            count = raw['training_count']
            if not isinstance(training_day, str) or date.fromisoformat(training_day).isoformat() != training_day:
                raise ValueError()
            if type(count) is not int or not 0 <= count <= 5: raise ValueError()
        except (KeyError, TypeError, ValueError): raise ValueError('Invalid training history') from None
        training = dict(training_day=training_day, training_count=count)
    # Keep progression and needs; never publish account history, desktop settings or credentials.
    pet = {k: deepcopy(raw[k]) for k in (*numeric, 'id', 'character', 'name', 'totals')}
    pet.update(training)
    pet.update(version=1, sleeping=False, vacation=False, hardcore=False, dead=False,
               sick=bool(raw.get('sick')), battle_rewards=[], cracks=[], repairing_cracks=False,
               account=None, days={}, synced=None, overlay=False, roaming=False,
               message='Welcome to your new home!')
    if raw.get('dead'): raise ValueError('Revive your pet before offering it')
    return pet


def request(data, owner, route, body):
    market = data.setdefault('exchange', {'listings': {}, 'operations': {}, 'deliveries': {}})
    listings, operations, deliveries = (market[k] for k in ('listings', 'operations', 'deliveries'))
    if route == '/exchange/list':
        return {'listings': [dict(id=k, owner=v['owner'], mode=v['mode'], name=v['pet']['name'], character=v['pet']['character'], level=level(v['pet']), xp=v['pet']['xp'], traits=traits(v['pet'])) for k, v in listings.items()],
                'deliveries': deepcopy(deliveries.get(owner, {}))}
    if route == '/exchange/ack':
        ids = body.get('deliveries')
        if not isinstance(ids, list) or len(ids) > 24 or any(not isinstance(i, str) for i in ids): raise ValueError('Invalid delivery acknowledgements')
        for delivery in ids: deliveries.get(owner, {}).pop(delivery, None)
        return {'ok': True}
    operation = body.get('operation')
    if not isinstance(operation, str) or len(operation) > 64 or not operation:
        raise ValueError('An operation ID is required')
    opkey = owner + ':' + operation
    if opkey in operations: return operations[opkey]
    if route == '/exchange/offer':
        if len(listings) >= 1000: raise ValueError('The exchange is full; try again later')
        mode = body.get('mode')
        if mode not in ('adoption', 'trade'): raise ValueError('Choose adoption or trade')
        if sum(v['owner'] == owner for v in listings.values()) >= 24: raise ValueError('Too many open offers')
        pet = validate_pet(body.get('pet'))
        if any(v['pet']['id'] == pet['id'] for v in listings.values()): raise ValueError('Pet already listed')
        listing = str(uuid.uuid4())
        listings[listing] = dict(owner=owner, mode=mode, pet=pet, created=time.time())
        result = {'listing': listing}
    elif route in ('/exchange/claim', '/exchange/cancel'):
        listing = body.get('listing')
        if not isinstance(listing, str) or listing not in listings: raise ValueError('Offer is no longer available')
        offer = listings[listing]
        if len(deliveries.get(owner, {})) >= 24 or len(deliveries.get(offer['owner'], {})) >= 24:
            raise ValueError('Collect pending deliveries before making this exchange')
        if route.endswith('/cancel'):
            if offer['owner'] != owner: raise ValueError('Only the owner can cancel')
            deliveries.setdefault(owner, {})[opkey] = offer['pet']
        else:
            if offer['owner'] == owner: raise ValueError('Cancel your own offer instead')
            if offer['mode'] == 'adoption' and body.get('pet') is not None:
                raise ValueError('Adoption is free; do not send a pet in return')
            if offer['mode'] == 'trade':
                pet = validate_pet(body.get('pet'))
                if pet['id'] == offer['pet']['id'] or any(v['pet']['id'] == pet['id'] for v in listings.values()):
                    raise ValueError('Pet is already in escrow')
                deliveries.setdefault(offer['owner'], {})[opkey] = pet
            deliveries.setdefault(owner, {})[opkey] = offer['pet']
        del listings[listing]
        result = {'ok': True}
    else: raise ValueError('Unknown exchange endpoint')
    operations[opkey] = result
    return result
