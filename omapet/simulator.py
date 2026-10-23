"""Offline sparring, using the real arena rules and disposable identities."""
import curses
import json
from pathlib import Path
import random
import secrets
import tempfile
import time
from .arena import Arena, MOVES
from .characters import CHARACTERS
from .core import data_dir, traits
from .portraits import portrait, terminal_color


def appearance():
    try:
        pet = json.loads((data_dir() / 'pet.json').read_text())
        name, kind = pet['name'], pet['character']
        if not isinstance(name, str) or not name.isprintable() or not name.strip(): raise ValueError()
        if kind not in CHARACTERS: raise ValueError()
        stats = traits(pet)
        return name[:24], kind, stats
    except (OSError, ValueError, KeyError, TypeError):
        return 'Sprout', 'cat', dict.fromkeys(('strength','stamina','agility','defense'), 30)


class Practice:
    def __init__(self, name, character, stats, rng=None):
        self.rng = rng or random.SystemRandom()
        self.tmp = tempfile.TemporaryDirectory(prefix='omapet-practice-')
        self.arena = Arena(Path(self.tmp.name)/'arena.json', secrets.token_urlsafe(24))
        self.character = character
        self.rival_kind = self.rng.choice(tuple(k for k in CHARACTERS if k != character))
        self.players = [self.arena.request('/register', {'name': n, 'invite': self.arena.invite}, '')
                        for n in [name, CHARACTERS[self.rival_kind][0] + ' (CPU)']]
        for p in self.players: self.arena.request('/queue', {'traits': stats}, p['token'])
        self.bot_move = self.rng.choice(MOVES)  # Commit before seeing the user's choice.
        self.result = self.arena.request('/status', {}, self.players[0]['token'])

    def submit(self, move):
        self.result = self.arena.request('/move', {'move': move}, self.players[0]['token'])
        return self.result

    def resolve(self):
        self.arena.request('/move', {'move': self.bot_move}, self.players[1]['token'])
        self.result = self.arena.request('/status', {}, self.players[0]['token'])
        self.bot_move = self.rng.choice(MOVES)
        return self.result

    def close(self):
        self.tmp.cleanup()


def draw(put, box, result, own_kind, rival_kind, colors, left, width, height, practice=False):
    box(4, left, height-9, width, 'PRACTICE · OFFLINE' if practice else 'FRIENDLY ARENA')
    match = result.get('match') if result else None
    if not match:
        put(7,left+3,'[j] Join queue · [d] Practice against a CPU',2)
        put(9,left+3,'Searching for a rival…' if result and result['queued'] else 'Connect with: omapet arena connect URL',3)
        return
    ids = sorted(match['players'], key=lambda p: p != result['id'])
    colwidth=(width-6)//2
    frame=int(time.monotonic()*5)
    for i,p in enumerate(ids):
        kind=own_kind if i==0 else rival_kind
        x=left+3+i*colwidth
        art=portrait(kind,'happy' if match['hp'][p] else 'departed',frame)
        art_width=max(map(len,art))
        for row,line in enumerate(art):put(5+row,x+max(0,(colwidth-art_width)//2),line,colors.get(kind,4),True)
        put(12,x,match['names'][p][:colwidth-7]+(' · YOU' if i==0 else ''),2,True)
        # Battle HP starts at 80 + stamina; display against that exact maximum.
        maximum=result.get('max_hp',{}).get(p) or match.get('max_hp',{}).get(p)
        hp=match['hp'][p];bars=max(5,min(20,colwidth-13))
        if maximum:
            filled=round(bars*hp/maximum)
            put(13,x,'♥ '+'▰'*filled+'▱'*(bars-filled)+f' {hp}',2 if hp>maximum*.3 else 3)
        else:put(13,x,f'♥ Battle HP {hp}',2 if hp>30 else 3)
    if match.get('fighters'):
        for i, p in enumerate(ids):
            team = match['fighters'][p]
            if len(team) > 1:
                put(15, left+3+i*colwidth, ' / '.join(f"{t['name'][:10]} {t['hp']}♥" for t in team)[:colwidth-1], 2)
    winner=match['winner']
    line=('DRAW' if winner=='draw' else 'YOU WIN!' if winner==result['id'] else 'RIVAL WINS') if winner else ('Move locked…' if match['submitted'] else 'Choose your move')
    put(14,left+3,f"ROUND {min(match['round'],30)} · {line}",3 if winner else 4,True)
    put(16,left+3,'[1] Strike > Feint   [2] Guard > Strike   [3] Feint > Guard',2)
    if practice:put(17,left+3,'[n] New rival / rematch   [q / Esc] Back · No XP or care changes',1)
    else:put(17,left+3,'[j] Queue again   [l] Leave / concede   [d] Offline practice',1)
    count=max(0,height-26)
    for i,line in enumerate(match['log'][-count:] if count else []):put(19+i,left+3,line[:width-6])


def play(screen):
    curses.curs_set(0);screen.timeout(60)
    curses.start_color();curses.use_default_colors()
    for i,c in enumerate((curses.COLOR_CYAN,curses.COLOR_GREEN,curses.COLOR_YELLOW,curses.COLOR_MAGENTA),1):curses.init_pair(i,c,-1)
    colors={}
    for i,(kind,(_,color,_)) in enumerate(CHARACTERS.items(),5):
        if i<curses.COLOR_PAIRS:curses.init_pair(i,terminal_color(color,curses.COLORS),-1);colors[kind]=i
    name,kind,stats=appearance()
    game=Practice(name,kind,stats);pending=0;message='A friendly CPU spar. Real battle rules; your pet stays untouched.'
    def put(y,x,text,color=0,bold=False):
        h,w=screen.getmaxyx()
        if 0<=y<h and 0<=x<w-1:
            try:screen.addnstr(y,x,str(text),w-x-1,curses.color_pair(color)|(curses.A_BOLD if bold else 0))
            except curses.error:pass
    def box(y,x,h,w,title):
        put(y,x,'╭'+'─'*(w-2)+'╮',1)
        for row in range(1,h-1):put(y+row,x,'│',1);put(y+row,x+w-1,'│',1)
        put(y+h-1,x,'╰'+'─'*(w-2)+'╯',1);put(y,x+3,' '+title+' ',1,True)
    try:
        while True:
            if pending and time.monotonic()>=pending:
                game.resolve();pending=0
                message=game.result['match']['log'][-1]
            screen.erase();h,w=screen.getmaxyx();width=min(w-4,104);left=max(2,(w-width)//2)
            put(1,left,'O M A P E T   /   BATTLE SIMULATOR',1,True)
            put(2,left,'Offline practice · CPU chooses independently · No server or invitation needed')
            if h>=24 and w>=64:
                result=dict(game.result,max_hp={p['id']:80+max(10,min(60,int(stats['stamina']))) for p in game.players})
                draw(put,box,result,kind,game.rival_kind,colors,left,width,h,True)
            else:put(5,2,'Resize to at least 64 × 24. [q] Exit',3)
            put(h-3,left,message[:max(1,width-1)],3)
            put(h-2,left,'Practice only · No XP, energy cost, injuries, or changes to your real pet.',1)
            screen.refresh();key=screen.getch()
            if key in (ord('q'),27):return
            if key==ord('n'):
                game.close();game=Practice(name,kind,stats);pending=0;message='A new rival approaches!'
            elif key in map(ord,'123') and not pending and not game.result['match']['winner']:
                game.submit(MOVES[key-ord('1')]);pending=time.monotonic()+.7
                message='Your move is locked. Waiting for your rival…'
    finally:
        game.close();screen.timeout(120)


def run():
    curses.wrapper(play)
