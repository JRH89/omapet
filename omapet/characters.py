"""Shared character catalogue for the terminal and desktop."""
import secrets

CHARACTERS = {
    'cat': ('Mochi', '#e8c9ad', (r' /\_/\ ', '( o.o )', ' > ^ < ', '/|   |\\', '(_|_|_)')),
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
    'duck': ('Quackers', '#f5d461', ('   __  ', ' <(o ) ', r'  (  \___', '   (_____)', '    ~~~~ ')),
    'octocat': ('Merge', '#ab9dd9', (' /\\_/\\ ', '( o.o )', ' /~~~\\ ', '(~~~~~)', ' ~ ~ ~ ')),
    'android': ('Droid', '#a4c639', (' \\   / ', ' (o o) ', ' [===] ', ' |   | ', ' d   b ')),
    'crab': ('Ferris', '#f18a61', (' \\   / ', ' (o o) ', '<[===]>', ' /|||\\ ', '       ')),
    'whale': ('Docker', '#6bb9e8', ('  []   ', ' [][]  ', ' /o  \\_', '(     _/', ' \\___/ ')),
    'elephant': ('Posty', '#8ba4ce', (' /---\\ ', '( o o )', ' /| U| ', '( |  |)', '(_|__|)')),
    'camel': ('Perl', '#d5b17d', ('   /o> ', ' /\\| | ', '(  | | ', ' |   | ', ' d   b ')),
    'beaver': ('Gradle', '#8bbcb2', (' (o o) ', ' / TT\\ ', '(    )=', ' |   | ', '(_|_|_)')),
    'bug': ('Glitch', '#df87b2', (' \\   / ', ' (o o) ', '/[===]\\', '\\[===]/', ' /   \\ ')),

}


CHARACTER_KEYS = '123456789sgdoacrwebu'

# Text-only Waybar fallback; Quattro renders the actual pixel sprite.
CHARACTER_ICONS = {
    'cat': '🐈', 'fox': '🦊', 'bunny': '🐇', 'frog': '🐸',
    'bear': '🐻', 'owl': '🦉', 'slime': '🫧', 'robot': '🤖',
    'penguin': '🐧', 'snake': '🐍', 'gopher': '🐿', 'duck': '🦆', 'octocat': '🐙', 'android': '🤖',
    'crab': '🦀', 'whale': '🐳', 'elephant': '🐘', 'camel': '🐪', 'beaver': '🦫', 'bug': '🐛',
}

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
