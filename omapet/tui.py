import curses
import time
from concurrent.futures import ThreadPoolExecutor
from .core import store, public, care, apply_days
from .characters import CHARACTERS, CHARACTER_KEYS, choose, rename


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
    message = 'Welcome home. A little care, a little code.'
    future, arena, result, next_poll = None, False, None, 0
    modal, name_input = None, ''

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
        if future and future.done():
            try:
                value = future.result()
                if isinstance(value, tuple):
                    with store() as state: apply_days(state, *value)
                    message = state['message']
                elif isinstance(value, dict): result = value
            except Exception as e: message = str(e)
            future = None
        if arena and future is None and time.monotonic() > next_poll:
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
        elif arena:
            box(4, left, h - 9, width, 'FRIENDLY ARENA')
            put(6, left + 3, '[j] Join queue   [1] Strike   [2] Guard   [3] Feint', 2)
            put(7, left + 3, '[l] Leave / concede · Strike > Feint > Guard > Strike', 3)
            if result:
                put(9, left + 3, f"{result['online']} online · " + ('Searching for a rival…' if result['queued'] else 'Ready for your next spar'), 1)
                m = result.get('match')
                if m:
                    for i, player in enumerate(m['players']):
                        put(11 + i, left + 3, f"{m['names'][player]} {'(you)' if player == result['id'] else ''}  ♥ {m['hp'][player]}", 2, True)
                    put(14, left + 3, f"ROUND {m['round']} · " + ('Move locked. Waiting…' if m['submitted'] else 'Choose your move.'), 4)
                    if m['winner']:
                        put(14, left + 3, 'Result: ' + m['names'].get(m['winner'], m['winner']) + ' · [j] play again', 3)
                    for i, line in enumerate(m['log'][-max(0, h - 24):]):
                        if 16 + i < h - 6: put(16 + i, left + 3, line[:width - 6])
            else:
                put(10, left + 3, 'Connect with: omapet arena connect URL', 3)
        else:
            split = min(34, width // 2)
            box(4, left, 10, split, 'YOUR COMPANION')
            box(4, left + split + 1, 10, width - split - 1, 'CARE')
            character = s['character']
            art = list(CHARACTERS[character][2])
            frame = int(time.time() * 5)
            action = s.get('last_action') if time.time() - s.get('action_at', 0) < 2.4 else ''
            for i, line in enumerate(art):
                if s['sleeping']: line = line.replace('o', '-').replace('O', '-')
                if s['sick']: line = line.replace('o', 'x')
                put(6 + i, left + split // 2 - 4, line, 4, True)
            if action == 'feed': put(11, left + split // 2 - 6, '· nom nom ·' if frame % 2 else '  (snack)  ', 3)
            elif action == 'clean': put(6 + frame % 4, left + 4, '✧', 1); put(7 + frame % 3, left + split - 5, '✦', 1)
            elif s['sleeping']: put(6, left + split - 7, 'z Z', 1)
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
            put(18, left + 1, '[f] Feed   [c] Clean   [s] Sleep/wake   [p] Play   [m] Medicine', 2)
            put(19, left + 1, '[n] Name   [b] Character   [o] Show/hide pet   [v] Vacation', 2)
            if h >= 27:
                put(21, left + 1, s['message'][:width - 2], 0)
                put(22, left + 1, 'Hardcore · death enabled' if s['hardcore'] else 'Gentle mode · your progress is always safe', 3)
        put(h - 3, left, ('◌ Working… ' if future else '› ') + message[:max(1, width - 13)], 3)
        put(h - 2, left, '[g] Sync GitHub   [a] Arena/home   [r] Revive   [q] Quit', 1)
        if modal:
            # Centered modal overlays without a blocking input loop or network waits.
            mw, mh = min(w - 4, 78), 17 if modal == 'character' else 8
            mx, my = (w - mw) // 2, max(0, (h - mh) // 2)
            for row in range(mh): put(my + row, mx, ' ' * mw)
            box(my, mx, mh, mw, 'CHOOSE YOUR COMPANION' if modal == 'character' else 'A NAME OF THEIR OWN')
            if modal == 'character':
                for i, (kind, (suggested, _, art)) in enumerate(CHARACTERS.items()):
                    col, row = i % 3, i // 3
                    x, y = mx + 3 + col * ((mw - 4) // 3), my + 2 + row * 3
                    put(y, x, f'[{CHARACTER_KEYS[i]}] {kind.title()}' + (' ✓' if kind == s['character'] else ''), 2, True)
                    put(y + 1, x, (art[1] + ' ' + suggested)[:(mw - 4) // 3 - 2], 4)
                put(my + 15, mx + 3, '[0] Surprise me   [Esc] Back', 1)
            else:
                put(my + 2, mx + 3, 'What should we call your companion?', 0)
                put(my + 4, mx + 3, '> ' + name_input + '▏', 2, True)
                put(my + 6, mx + 3, '[Enter] Save   [Esc] Cancel', 1)
        screen.refresh()
        key = screen.getch()
        try:
            if modal:
                if key == 27: modal = None
                elif modal == 'character' and key in map(ord, '0' + CHARACTER_KEYS):
                    kind = 'random' if key == ord('0') else tuple(CHARACTERS)[CHARACTER_KEYS.index(chr(key))]
                    with store() as state: choose(state, kind)
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
            if key == ord('a'): arena = not arena; next_poll = 0
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
                elif key == ord('n'): modal, name_input = 'name', s['name']
                elif key == ord('b'): modal = 'character'
                elif key == ord('o'):
                    with store() as state: state['overlay'] = not state['overlay']
                    message = 'Desktop pet ' + ('shown.' if state['overlay'] else 'hidden. Right-click the bar widget to bring it back.')
                elif key == ord('g') and future is None:
                    from .github import collect
                    future = worker.submit(collect)
        except (ValueError, OSError) as e: message = str(e)
