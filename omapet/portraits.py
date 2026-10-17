"""Seven-line, plain-ASCII portraits for the terminal's companion card.

Only @ marks an eye, so blinking never changes outlines, whiskers, or lettering.
The small catalogue drawings remain useful as character-picker thumbnails.
"""

PORTRAITS = {
    'cat': (
        r'      /\___/\ ',
        r'     (  @ @  )',
        r'     (  =^=  )',
        r'     /       \ ',
        r'    /|       |\__',
        r'   (_|  ___  |_) )',
        r'     (_/   \_)__/',
    ),
    'fox': (
        r'     /\     /\ ',
        r'    /  \___/  \ ',
        r'   (   @   @   )',
        r'    \  \_^_/  /',
        r'     /  \_/  \   /|',
        r'    (|       |)_/ |',
        r'     (_/___\_)___/',
    ),
    'bunny': (
        r'       (\   /)',
        r'        \\_//',
        r'       ( @.@ )',
        r'       (  v  )',
        r'      /|     |\ ',
        r'     (_|  _  |_)',
        r'       (_/ \_)',
    ),
    'frog': (
        r'       _     _',
        r'     _(@)___(@)_',
        r'    /           \ ',
        r'   (   \_____/   )',
        r'    \   _____   /',
        r'    /| /     \ |\ ',
        r'   (_(_/     \_)_)',
    ),
    'bear': (
        r'     .--. .--.',
        r'    (  _ Y _  )',
        r'     / @   @ \ ',
        r'    (  ( Y )  )',
        r"    /|  '-'  |\ ",
        r'   (_|       |_)',
        r'     (_/___\_)',
    ),
    'owl': (
        r'      /\___/\ ',
        r'     / .---. \ ',
        r'    | ( @|@ ) |',
        r'    |  \_V_/  |',
        r'    /|  v v  |\ ',
        r'   (_|_______|_)',
        r'       ^^ ^^',
    ),
    'slime': (
        r'         __',
        r"      .-'  '-.",
        r'     /        \ ',
        r'    /  @    @  \ ',
        r'   /     __     \ ',
        r'  (    \____/    )',
        r"   '---.____.---'",
    ),
    'robot': (
        r'         o',
        r'         |',
        r'    .----------.',
        r'   [| @  __  @ |]',
        r"    '---.++.---'",
        r'     /|____|\ ',
        r'      d    b',
    ),
    'penguin': (
        r'       .-----.',
        r'      /  @ @  \ ',
        r'     (    >    )',
        r'    /|  .---.  |\ ',
        r'   / | (     ) | \ ',
        r"   \_|  '---'  |_/",
        r'     (__/ \__)',
    ),
    'snake': (
        r'      .------.',
        r'     / @    @ \ ',
        r'     \  .__.  /',
        r"      '-. Y.-'",
        r'   .---./  \---.',
        r'  (  ___\__/___  )',
        r"   '------------'",
    ),
    'gopher': (
        r'       _     _',
        r'      ( )___( )',
        r'     /  @   @  \ ',
        r'    (   (___)   )',
        r'     \   TT    /',
        r'     /|       |\ ',
        r'    (_/_______\_)',
    ),
    'duck': (
        '',
        '    ___',
        '  <( @ )____',
        '   (  ._>  /',
        "    `-----'",
        '  ~ ~ ~ ~ ~ ~',
        '',
    ),
}


def portrait(character, mood='happy', frame=0):
    if mood in ('sick', 'departed'):
        eye = 'x'
    elif mood == 'sleeping' or frame % 40 >= 38:
        eye = '-'
    elif mood == 'eating':
        eye = '^'
    else:
        eye = {'owl': 'O', 'robot': '0'}.get(character, 'o')
    lines = tuple(line.replace('@', eye).rstrip() for line in PORTRAITS[character])
    margin = min(len(line) - len(line.lstrip()) for line in lines if line)
    return tuple(line[margin:] if line else '' for line in lines)


def terminal_color(hex_color, colors):
    """Approximate a character's sprite palette without changing the terminal theme."""
    if colors >= 256:
        levels = (0, 95, 135, 175, 215, 255)
        rgb = [int(hex_color[i:i + 2], 16) for i in (1, 3, 5)]
        r, g, b = [min(range(6), key=lambda n: abs(levels[n] - value)) for value in rgb]
        return 16 + 36 * r + 6 * g + b
    return {'#e8c9ad': 3, '#efa76e': 3, '#d4b5e8': 5, '#a6cf72': 2,
            '#cda67f': 3, '#93b9dd': 6, '#84d8cf': 6, '#c1c8d8': 7,
            '#526b85': 6, '#97ce79': 2, '#ba936d': 3, '#f5d461': 3}.get(hex_color, 7)


def thumbnail(character):
    eye_row = next(i for i, line in enumerate(PORTRAITS[character]) if '@' in line)
    return portrait(character)[eye_row].strip()
