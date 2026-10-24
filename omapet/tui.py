import curses
import time
from concurrent.futures import ThreadPoolExecutor
from .core import store, public, care
from .characters import CHARACTERS, CHARACTER_KEYS, choose, rename
from .portraits import portrait, thumbnail, terminal_color


def run():
    with ThreadPoolExecutor(max_workers=1) as worker:
        curses.wrapper(lambda screen: dashboard(screen, worker))


def dashboard(screen, worker):
    curses.curs_set(0)
    screen.timeout(120)
    curses.start_color()
    curses.use_default_colors()
    for idx, color in enumerate((curses.COLOR_CYAN, curses.COLOR_GREEN, curses.COLOR_YELLOW, curses.COLOR_MAGENTA), 1):
        curses.init_pair(idx, color, -1)
    pet_colors = {}
    for idx, (kind, (_, color, _)) in enumerate(CHARACTERS.items(), 5):
        if idx < curses.COLOR_PAIRS:
            curses.init_pair(idx, terminal_color(color, curses.COLORS), -1)
            pet_colors[kind] = idx
    message = 'Welcome home. A little care, a little code.'
    future, arena, result, next_poll = None, False, None, 0
    modal, name_input = None, ''
    collection_open, board_open, selected, board_selected, board = False, False, 0, 0, None
    from .github import start_auto_sync
    startup_sync = start_auto_sync()

    def put(y, x, text, color=0, bold=False):
        h, w = screen.getmaxyx()
        if 0 <= y < h and 0 <= x < w - 1:
            try:
                screen.addnstr(y, x, str(text), max(0, w - x - 1), curses.color_pair(color) | (curses.A_BOLD if bold else 0))
            except curses.error: pass

    def box(y, x, height, width, title):
        put(y, x, '╭' + '─' * (width - 2) + '╮', 1)
        for row in range(1, height - 1):
            put(y + row, x, '│', 1); put(y + row, x + width - 1, '│', 1)
        put(y + height - 1, x, '╰' + '─' * (width - 2) + '╯', 1)
        put(y, x + 3, ' ' + title + ' ', 1, True)

    while True:
        with store() as state: s = public(state)
        if startup_sync is not None and startup_sync.poll() is not None:
            startup_sync = None
            message = s['message']
        if future and future.done():
            try:
                value = future.result()
                if isinstance(value, str):
                    message = value
                elif isinstance(value, dict):
                    if 'listings' in value:
                        board = value
                        message = 'Exchange updated. Pets and deliveries are saved.'
                        if value.get('pending_deliveries'): message += f" {value['pending_deliveries']} arrivals waiting for room."
                    else: result = value
            except Exception as e: message = str(e)
            future = None
        if arena and not collection_open and future is None and time.monotonic() > next_poll:
            from .network import request
            future = worker.submit(request)
            next_poll = time.monotonic() + 3
        screen.erase()
        h, w = screen.getmaxyx()
        width = min(w - 4, 104)
        left = max(2, (w - width) // 2)
        put(1, left, 'O M A P E T', 1, True)
        put(1, left + 16, ' HOME ' if not arena else ' ARENA ', 2, True)
        put(2, left, 'Your little corner of the terminal.   [a] switch home / arena', 0)
        if h < 24 or w < 64:
            put(5, 2, 'Give your companion a little room: 64 columns × 24 rows.', 3)
            put(7, 2, f"{s['name']} · {s['status']} · Food {s['food']:.0f} · Energy {s['energy']:.0f}", 2)
        elif collection_open:
            pets = s['pets']
            selected = min(selected, len(pets) - 1)
            box(4, left, h - 9, width, 'PET EXCHANGE' if board_open else f"YOUR COLLECTION · {len(pets)}/24")
            if board_open:
                listings = (board or {}).get('listings', [])
                board_selected = max(0, min(board_selected, len(listings) - 1))
                put(6, left + 3, '[e] Household [g] Refresh/deliveries [Enter] Adopt/trade [x] Cancel offer', 2)
                selected = min(selected, len(pets) - 1)
                put(7, left + 3, f"Trade gives: {pets[selected]['name']} L{pets[selected]['level']} · Select in household first.", 3)
                if not listings: put(9, left + 3, 'No offers loaded. [g] Refresh the exchange.', 0)
                start = max(0, board_selected - max(0, h - 22))
                for row, item in enumerate(listings[start:start + max(1, h - 19)]):
                    put(9 + row, left + 3, ('› ' if start + row == board_selected else '  ') +
                        f"{item['name']} · {item['character']} L{item['level']} · {item['mode']}" + (' · YOUR OFFER' if item.get('mine') else ''), 2)
            else:
                put(6, left + 3, '[↑/↓] Select [Enter] Care for pet [h] Hatch [o] All out [i] All home', 2)
                put(7, left + 3, '[p] Play together [f] Train (+XP) [j] Online 2v2 (active + selected)', 2)
                put(8, left + 3, '[u] Offer for adoption [t] Offer for trade [e] Exchange board', 2)
                start = max(0, selected - max(0, h - 23))
                for row, pet in enumerate(pets[start:start + max(1, h - 20)]):
                    put(10 + row, left + 3, ('› ' if start + row == selected else '  ') +
                        f"{pet['name']} · {pet['character']} L{pet['level']} · {pet['status']}" + (' · ACTIVE' if pet['active'] else ''), 2)
        elif arena:
            from .simulator import draw
            draw(put, box, result, s['character'], 'robot', pet_colors, left, width, h)

        else:
            split = min(34, width // 2)
            frame = int(time.monotonic() * 5)
            action = s.get('last_action') if time.time() - s.get('action_at', 0) < 2.4 else ''
            title = ('NOM NOM' if frame % 2 else 'SNACK TIME') if action == 'feed' else 'YOUR COMPANION'
            box(4, left, 10, split, title)
            box(4, left + split + 1, 10, width - split - 1, 'CARE')
            character = s['character']
            mood = 'eating' if action == 'feed' and not s['sleeping'] else s.get('mood', s['status'])
            art = portrait(character, mood, frame)
            art_width = max(map(len, art))
            art_x = left + (split - art_width) // 2
            for i, line in enumerate(art):
                put(5 + i, art_x, line, pet_colors.get(character, 4), True)
            if action == 'clean':
                put(6 + frame % 4, left + 2, '*', 1)
                put(7 + frame % 3, left + split - 3, '*', 1)
            elif s['sleeping']:
                put(5 + frame % 2, left + split - 5, 'zZ', 1)
            put(12, left + 3, f"{s['name']} · {character}"[:split - 5], 2, True)
            sx = left + split + 4
            bars = max(5, min(20, width - split - 23))
            for i, (key, label) in enumerate((('health','Health'), ('food','Food'), ('energy','Energy'), ('hygiene','Clean'), ('joy','Joy'))):
                value = int(s[key]); filled = int(value * bars / 100)
                put(6 + i, sx, f'{label:<7}', 0)
                put(6 + i, sx + 7, '▰' * filled + '▱' * (bars - filled), 2 if value >= 30 else 3)
                put(6 + i, sx + 8 + bars, f'{value:3}', 2 if value >= 30 else 3)
            put(12, sx, s['status'].upper() + (' · CARE PAUSED' if s['vacation'] else ''), 3)
            xp_floor, xp_end = 100 * (s['level'] - 1) ** 2, 100 * s['level'] ** 2
            put(14, left + 1, f"LEVEL {s['level']}  ·  {s['xp'] - xp_floor}/{xp_end - xp_floor} XP to next level", 1, True)
            trait_labels = ('STR', 'STA', 'AGI', 'DEF')
            put(15, left + 1, '   '.join(f'{label} {v:2}' for label, v in zip(trait_labels, s['traits'].values())), 4)
            put(16, left + 1, f"GitHub: {s['account'] or 'not connected'} · Last active: {s.get('last_active', '—')}", 0)
            if s.get('cracks'):
                put(17, left + 1, f"[x] Clean up a mess · {len(s['cracks'])} left before your pet can go home", 3)
            put(18, left + 1, '[f] Feed   [c] Clean   [s] Sleep/wake   [p] Play   [m] Medicine', 2)
            put(19, left + 1, '[n] Name [b] Look [h] Hatch [Tab] Next pet [o] Desktop [v] Away', 2)
            if h >= 27:
                put(21, left + 1, s['message'][:width - 2], 0)
                put(22, left + 1, 'Hardcore · death enabled' if s['hardcore'] else 'Gentle mode · your progress is always safe', 3)
        put(h - 3, left, ('◌ Working… ' if future else '› ') + message[:max(1, width - 13)], 3)
        put(h - 2, left, '[k] Collection / exchange   [g] GitHub   [a] Arena   [r] Revive   [q] Quit', 1)
        if modal:
            # Centered modal overlays without a blocking input loop or network waits.
            mw, mh = min(w - 4, 78), min(h - 2, 19) if modal in ('character', 'hatch') else 8
            mx, my = (w - mw) // 2, max(0, (h - mh) // 2)
            for row in range(mh): put(my + row, mx, ' ' * mw)
            box(my, mx, mh, mw, f'CHOOSE YOUR COMPANION · {len(CHARACTERS)}' if modal in ('character', 'hatch') else 'A NAME OF THEIR OWN')
            if modal in ('character', 'hatch'):
                for i, (kind, (suggested, _, art)) in enumerate(CHARACTERS.items()):
                    col, row = i % 3, i // 3
                    x, y = mx + 3 + col * ((mw - 4) // 3), my + 2 + row * 2
                    label = 'Rubber duck' if kind == 'duck' else kind.title()
                    put(y, x, f'[{CHARACTER_KEYS[i]}] {label}' + (' ✓' if kind == s['character'] else ''), 2, True)
                    put(y + 1, x, thumbnail(kind)[:(mw - 4) // 3 - 2], pet_colors.get(kind, 4), True)
                put(my + mh - 2, mx + 3, '[0] Surprise me  [Esc] Back' + (' · Hatch a new pet' if modal == 'hatch' else ''), 1)
            else:
                put(my + 2, mx + 3, 'What should we call your companion?', 0)
                put(my + 4, mx + 3, '> ' + name_input + '▏', 2, True)
                put(my + 6, mx + 3, '[Enter] Save   [Esc] Cancel', 1)
        screen.refresh()
        key = screen.getch()
        try:
            if modal:
                if key == 27: modal = None
                elif modal in ('character', 'hatch') and key in map(ord, '0' + CHARACTER_KEYS):
                    kind = 'random' if key == ord('0') else tuple(CHARACTERS)[CHARACTER_KEYS.index(chr(key))]
                    with store() as state:
                        if modal == 'hatch':
                            from .collection import hatch
                            hatch(state, kind)
                        else: choose(state, kind)
                    message, modal = state['message'], None
                elif modal == 'name':
                    if key in (10, 13):
                        with store() as state: rename(state, name_input)
                        message, modal = state['message'], None
                    elif key == 21: name_input = ''
                    elif key in (curses.KEY_BACKSPACE, 127, 8): name_input = name_input[:-1]
                    elif 32 <= key <= 126 and len(name_input) < 24: name_input += chr(key)
                continue
            if key == ord('q'): return
            if key == ord('k'):
                collection_open = not collection_open
                continue
            if collection_open:
                from . import collection
                from .network import exchange
                pets = s['pets']
                selected = min(selected, len(pets) - 1)
                if key == ord('e'): board_open = not board_open
                elif key in (curses.KEY_UP, curses.KEY_DOWN):
                    delta = -1 if key == curses.KEY_UP else 1
                    if board_open: board_selected = max(0, min(board_selected + delta, len((board or {}).get('listings', [])) - 1))
                    else: selected = max(0, min(selected + delta, len(pets) - 1))
                elif board_open:
                    offers = (board or {}).get('listings', [])
                    if key == ord('g') and future is None: future = worker.submit(exchange, 'sync')
                    elif offers and key in (10, 13, ord('x')) and future is None:
                        item = offers[board_selected]
                        if key == ord('x'): future = worker.submit(exchange, 'cancel', listing=item['id'])
                        else:
                            give = pets[selected]['id'] if item['mode'] == 'trade' else None
                            future = worker.submit(exchange, 'claim', pet_id=give, listing=item['id'])
                elif key == ord('h'): modal = 'hatch'
                elif key in (10, 13):
                    with store() as state: collection.switch(state, pets[selected]['id'])
                    selected = 0
                elif key in map(ord, 'oi'):
                    with store() as state: collection.roam(state, 'off' if key == ord('i') else 'on')
                elif key == ord('p'):
                    with store() as state: collection.play_together(state, state['id'], pets[selected]['id'])
                    message = state['message']
                elif key == ord('f'):
                    with store() as state: outcome = collection.spar(state, [state['id'], pets[selected]['id']])
                    message = outcome['log'][-1]
                elif key == ord('j') and future is None:
                    from .network import request
                    future = worker.submit(request, '/queue', team=[s['id'], pets[selected]['id']])
                    collection_open, arena = False, True
                elif key in map(ord, 'ut') and future is None:
                    future = worker.submit(exchange, 'offer', pet_id=pets[selected]['id'], mode='adoption' if key == ord('u') else 'trade')
                continue
            if key == ord('a'): arena = not arena; next_poll = 0
            elif arena and key == ord('d'):
                from .simulator import play
                play(screen)
            elif arena and key in map(ord, 'j123l') and future is None:
                from .network import request
                route = '/queue' if key == ord('j') else '/leave' if key == ord('l') else '/move'
                move = {ord('1'): 'strike', ord('2'): 'guard', ord('3'): 'feint'}.get(key)
                future = worker.submit(request, route, move)
            elif not arena:
                actions = dict(zip(map(ord, 'fcspmvr'), ('feed', 'clean', 'wake' if s['sleeping'] else 'sleep', 'play', 'medicine', 'vacation', 'revive')))
                if key in actions:
                    with store() as state: care(state, actions[key])
                    message = state['message']
                elif key == ord('x'):
                    from .desktop import repair
                    with store() as state:
                        if not state.get('cracks'): raise ValueError('No desktop messes to clean')
                        repair(state, state['cracks'][0]['id'])
                    message = state['message']
                elif key == ord('n'): modal, name_input = 'name', s['name']
                elif key == ord('b'): modal = 'character'
                elif key == ord('h'): modal = 'hatch'
                elif key == 9:
                    from .collection import switch, summaries
                    with store() as state:
                        pets = summaries(state)
                        if len(pets) > 1: switch(state, pets[1]['id'])
                    message = f"Caring for {state['name']} · {len(pets)} pets"
                elif key == ord('o'):
                    with store() as state: state['overlay'] = not state['overlay']
                    message = 'Desktop pet ' + ('shown.' if state['overlay'] else 'hidden. Right-click the bar widget to bring it back.')
                elif key == ord('g') and future is None:
                    from .github import sync
                    future = worker.submit(sync)
        except (ValueError, OSError) as e: message = str(e)
