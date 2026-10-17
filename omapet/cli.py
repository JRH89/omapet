import argparse
import getpass
import json
import sys
from .characters import CHARACTERS, CHARACTER_ICONS, choose, rename
from .core import ACTIONS, store, public, apply_days, care, status, level


def main():
    p = argparse.ArgumentParser(description='Omapet · a GitHub-grown desktop companion')
    sub = p.add_subparsers(dest='command')
    sub.add_parser('tui', help='Open the care dashboard')
    st = sub.add_parser('status'); st.add_argument('--json', action='store_true')
    sub.add_parser('waybar', help='Print a Waybar JSON update')
    act = sub.add_parser('care'); act.add_argument('action', choices=ACTIONS)
    sub.add_parser('sync', help='Sync seven days of contributions using gh authentication')
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
    hit.add_argument('x', type=float); hit.add_argument('y', type=float); hit.add_argument('--screen', default='')
    fix = sub.add_parser('repair', help='Repair one screen crack, or all for keyboard access')
    fix.add_argument('crack_id')
    arena = sub.add_parser('arena'); arena_sub = arena.add_subparsers(dest='action')
    conn = arena_sub.add_parser('connect'); conn.add_argument('url')
    for cmd in ('status', 'queue', 'leave'): arena_sub.add_parser(cmd)
    move = arena_sub.add_parser('move'); move.add_argument('move', choices=['strike', 'guard', 'feint'])
    args = p.parse_args()
    try:
        if args.command in (None, 'tui'):
            from .tui import run
            run(); return
        if args.command == 'sync':
            from .github import collect
            account, days = collect()
            with store() as s: apply_days(s, account, days)
            print(s['message']); return
        if args.command == 'arena':
            from . import network
            if args.action == 'connect':
                network.connect(args.url, getpass.getpass('Arena invitation: '))
                print('Connected. Open omapet and press a to enter the arena.')
            else:
                print(json.dumps(network.request('/' + (args.action or 'status'), getattr(args, 'move', None)), indent=2))
            return
        with store() as s:
            if args.command == 'care': care(s, args.action)
            elif args.command == 'name':
                rename(s, args.name)
            elif args.command == 'character': choose(s, args.character)
            elif args.command == 'hardcore': s['hardcore'] = args.mode == 'on'
            elif args.command == 'position':
                from .desktop import position
                position(s, args.x, args.y, args.screen)
            elif args.command == 'bonk':
                from .desktop import bonk
                bonk(s, args.x, args.y, args.screen)
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
