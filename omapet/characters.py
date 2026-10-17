"""Shared character catalogue for the terminal and desktop."""
import secrets

CHARACTERS = {
    'cat': ('Mochi', '#9bd9b7', (r' /\_/\ ', '( o.o )', ' > ^ < ', '/|   |\\', '(_|_|_)')),
    'fox': ('Ember', '#efa76e', (r' /\ /\ ', '( ^.^ )', ' \\ v / ', ' /   \\~', '(_/ \\_)')),
    'bunny': ('Clover', '#d4b5e8', (' (\\ /) ', ' (o.o) ', ' / >o< ', '(     )', '(_/ \\_)')),
    'frog': ('Puddle', '#a6cf72', (' @   @ ', '( o_o )', ' /---\\ ', '(     )', '(_/ \\_)')),
    'bear': ('Maple', '#cda67f', (' ʕ•ᴥ•ʔ ', ' /   \\ ', '|  o  |', '|     |', '(_/ \\_)')),
    'owl': ('Pixel', '#93b9dd', (' /\\_/\\ ', '( O,O )', ' ( v ) ', '/|   |\\', '  ^ ^  ')),
    'slime': ('Boba', '#84d8cf', ('   __  ', ' /    \\ ', '/ o  o\\', '|  __ |', ' \\____/ ')),
    'robot': ('Bolt', '#c1c8d8', ('   |   ', ' [o_o] ', ' /[+]\\ ', ' |   | ', ' d   b ')),
    'penguin': ('Tux', '#526b85', ('  .--. ', ' (o  o)', ' / >  \\', '(  ()  )', r' \_/\_/ ')),
    'snake': ('Noodle', '#97ce79', ('   __  ', '  (o.o)', '  /  / ', ' / ~(_ ', '(_____)')),
    'gopher': ('Goober', '#ba936d', ('  .--. ', ' (o..o)', ' / \"\" \\', '(      )', '(_/ \\_)')),
}


CHARACTER_KEYS = '123456789sg'

def random_character():
    return secrets.choice(tuple(CHARACTERS))


def choose(s, character):
    selected = random_character() if character == 'random' else character
    if selected not in CHARACTERS:
        raise ValueError('Choose: ' + ', '.join(CHARACTERS))
    s['character'] = selected
    s['message'] = f"Say hello to your {s['character']}!"


def rename(s, name):
    name = name.strip()
    if not name or not name.isprintable():
        raise ValueError('Use a printable name, up to 24 characters')
    s['name'] = name[:24]
    s['message'] = f"Hello, {s['name']}!"
