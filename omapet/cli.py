import argparse
import getpass
import json
import sys
from .characters import CHARACTERS, CHARACTER_ICONS, choose, rename
from .core import ACTIONS, store, public, care, status, level


def main():
    p = argparse.ArgumentParser(description='Omapet · a GitHub-grown desktop companion')
    sub = p.add_subparsers(dest='command')
    sub.add_parser('tui', help='Open the care dashboard')
    saver = sub.add_parser('screensaver', help='Cosmetic pet screensaver')
    saver.add_argument('action', choices=['preview', 'run', 'enable', 'disable', 'snapshot'], default='preview', nargs='?')
    st = sub.add_parser('status'); st.add_argument('--json', action='store_true')
    sub.add_parser('waybar', help='Print a Waybar JSON update')
    act = sub.add_parser('care'); act.add_argument('action', choices=ACTIONS); act.add_argument('--pet')
    sync = sub.add_parser('sync', help='Sync seven days of contributions using gh authentication')
    sync.add_argument('--auto', action='store_true', help='Quiet startup sync; skip overlapping or recent requests')
    name = sub.add_parser('name'); name.add_argument('name')
    character = sub.add_parser('character'); character.add_argument('character', choices=[*CHARACTERS, 'random'])
    hard = sub.add_parser('hardcore'); hard.add_argument('mode', choices=['on', 'off'])
    overlay = sub.add_parser('overlay'); overlay.add_argument('mode', choices=['on', 'off', 'toggle'])
    desktop = sub.add_parser('desktop', help='Desktop view, playtime, and surprise escapes')
    desktop.add_argument('setting', choices=['view', 'roam', 'escapes'])
    desktop.add_argument('value', choices=['simple', 'detailed', 'toggle', 'on', 'off'])
    pos = sub.add_parser('position', help='Save the desktop habitat position')
    pos.add_argument('x', type=float); pos.add_argument('y', type=float); pos.add_argument('--screen', default='')
    hit = sub.add_parser('bonk', help='Record an on-screen roaming impact')
    hit.add_argument('--kind', choices=['crack', 'poop'], default='crack')
    hit.add_argument('x', type=float); hit.add_argument('y', type=float); hit.add_argument('--screen', default='')
    fix = sub.add_parser('repair', help='Repair one screen crack, or all for keyboard access')
    fix.add_argument('crack_id')
    pets = sub.add_parser('pets', help='Collect, adopt, trade and play with pets')
    ps = pets.add_subparsers(dest='action', required=True)
    ps.add_parser('list')
    hatch = ps.add_parser('hatch'); hatch.add_argument('character', choices=[*CHARACTERS, 'random']); hatch.add_argument('--name')
    select = ps.add_parser('switch'); select.add_argument('pet')
    for command in ('play', 'spar'):
        pair = ps.add_parser(command, help='Train household pets and earn XP' if command == 'spar' else 'Play with two pets'); pair.add_argument('ids', nargs='+')
    roam = ps.add_parser('roam'); roam.add_argument('mode', choices=['on', 'off']); roam.add_argument('--pet', default='all')
    offer = ps.add_parser('offer'); offer.add_argument('pet'); offer.add_argument('--mode', choices=['adoption', 'trade'], default='adoption')
    claim = ps.add_parser('claim'); claim.add_argument('listing'); claim.add_argument('--pet', help='Pet to give in return for a trade')
    cancel = ps.add_parser('cancel'); cancel.add_argument('listing')
    ps.add_parser('board'); ps.add_parser('sync')
    arena = sub.add_parser('arena'); arena_sub = arena.add_subparsers(dest='action')
    arena_sub.add_parser('demo', help='Offline practice battle against a CPU; no pet changes')
    conn = arena_sub.add_parser('connect'); conn.add_argument('url')
    for cmd in ('status', 'queue', 'leave'): arena_sub.add_parser(cmd)
    arena_sub.choices['queue'].add_argument('--team', nargs='+', help='One or two pet IDs (2v2 with two)')
    move = arena_sub.add_parser('move'); move.add_argument('move', choices=['strike', 'guard', 'feint'])
    args = p.parse_args()
    try:
        if args.command in (None, 'tui'):
            from .tui import run
            run(); return
        if args.command == 'screensaver':
            from . import screensaver
            if args.action == 'snapshot': print(json.dumps(screensaver.snapshot()))
            elif args.action in ('enable', 'disable'): print(screensaver.configure(args.action == 'enable'))
            else: screensaver.run(preview=args.action == 'preview')
            return
        if args.command == 'sync':
            from .github import sync
            message = sync(auto=args.auto)
            if message: print(message)
            return
        if args.command == 'arena':
            if args.action == 'demo':
                from .simulator import run
                run(); return
            from . import network
            if args.action == 'connect':
                network.connect(args.url, getpass.getpass('Arena invitation: '))
                print('Connected. Open omapet and press a to enter the arena.')
            else:
                print(json.dumps(network.request('/' + (args.action or 'status'), getattr(args, 'move', None), team=getattr(args, 'team', None)), indent=2))
            return
        if args.command == 'pets' and args.action in ('offer', 'claim', 'cancel', 'board', 'sync'):
            from .network import exchange
            print(json.dumps(exchange('list' if args.action == 'board' else args.action,
                  pet_id=getattr(args, 'pet', None), listing=getattr(args, 'listing', None),
                  mode=getattr(args, 'mode', 'adoption')), indent=2))
            return
        with store() as s:
            if args.command == 'pets':
                from . import collection
                if s.get('exchange_pending') and args.action != 'list': raise ValueError('Run omapet pets sync to finish your pending transfer first')
                if args.action == 'list':
                    print(json.dumps(collection.summaries(s), indent=2)); return
                if args.action == 'hatch': collection.hatch(s, args.character, args.name)
                elif args.action == 'switch': collection.switch(s, args.pet)
                elif args.action == 'play':
                    if len(args.ids) != 2: raise ValueError('Choose two pet IDs')
                    collection.play_together(s, *args.ids)
                elif args.action == 'spar': print(json.dumps(collection.spar(s, args.ids), indent=2)); return
                elif args.action == 'roam':
                    from .desktop import configure
                    for pet in collection.all_pets(s) if args.pet == 'all' else [collection.find(s, args.pet)]:
                        if args.mode == 'off' or public(pet)['can_roam']: configure(pet, 'roam', args.mode)
                    s['overlay'] = True
            elif args.command == 'care':
                from .collection import find
                care(find(s, args.pet) if args.pet else s, args.action)
            elif args.command == 'name':
                rename(s, args.name)
            elif args.command == 'character': choose(s, args.character)
            elif args.command == 'hardcore': s['hardcore'] = args.mode == 'on'
            elif args.command == 'position':
                from .desktop import position
                position(s, args.x, args.y, args.screen)
            elif args.command == 'bonk':
                from .desktop import bonk
                bonk(s, args.x, args.y, args.screen, kind=args.kind)
            elif args.command == 'repair':
                from .desktop import repair
                repair(s, args.crack_id)
            elif args.command == 'desktop':
                from .desktop import configure
                configure(s, args.setting, args.value)
            elif args.command == 'overlay': s['overlay'] = not s['overlay'] if args.mode == 'toggle' else args.mode == 'on'
            view = public(s)
        if args.command == 'position': return
        if args.command == 'waybar':
            print(json.dumps({'text': f"{CHARACTER_ICONS.get(s['character'], '🐾')} {s['name']} Lv.{level(s)}", 'class': status(s),
                  'tooltip': f"{status(s).title()} · HP {s['health']:.0f} · Food {s['food']:.0f} · Energy {s['energy']:.0f}\nClick: care · Right click: desktop pet"}))
        elif args.command == 'status' and args.json: print(json.dumps(view))
        else: print(f"{s['name']} · Lv.{level(s)} · {status(s)}\n{s['message']}")
    except (ValueError, OSError, KeyError, json.JSONDecodeError) as e:
        print(f'omapet: {e}', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__': main()
