# Omapet

A tiny companion raised with care and grown through GitHub contributions. Native
Omarchy Quattro bar widget, animated desktop habitat, curses care dashboard,
Waybar adapter, and a shared turn-based TUI arena. Python 3.11+, no Python runtime
dependencies. This is an early implementation for casual play.

## Start here

From this checkout:

```sh
./bin/omapet             # care dashboard; q quits
./bin/omapet name Bramble
gh auth login
./bin/omapet sync
```

Install the launcher and Quattro widget:

```sh
python3 scripts/install.py --quattro
omapet overlay on
```

The installer validates the plugin, copies it into
`~/.config/omarchy/plugins/jrh89.omapet`, creates `~/.local/bin/omapet`, and enables
the plugin. It refuses to overwrite existing installations. Ensure `~/.local/bin`
is on PATH. No sudo, package installs, or background services are performed.
Use `python3 scripts/install.py` for just the launcher (keep this checkout in place).
The Quattro plugin also runs directly from its folder without pip installation.

Click the Quattro bar widget to open the TUI in your configured terminal. The desktop
pet lives in a small transparent layer surface in the bottom-right corner. Click the pet or **Feed** for a snack; use **Clean** and **Rest/Wake** for care.
A snack animation and washing bubbles confirm successful actions, and a short
message explains blocked actions such as being full. Use **×** to hide the pet;
right-click the bar widget to show or hide it again. It appears on the compositor's
default output. The bar widget must be enabled and placed in the active bar for the
desktop pet to run. It shares the existing shell process; it does not launch a second
Quickshell instance. The desktop habitat currently requires Quattro even if you use
the Waybar adapter.

For Waybar, merge `integrations/waybar.jsonc`, add `custom/omapet` to your bar's
modules, and include `integrations/waybar.css`. On other distributions replace
`omarchy-launch-terminal` with your terminal command. The standalone TUI and arena
do not require Omarchy.

## Habitat views and desktop adventures

The habitat has a **Detailed view / Simple view** button; the preference is saved.
Simple is a 218-pixel-wide habitat with symbol stats (♥ health, ◒ food, ϟ energy)
and a single icon toolbar: feed, clean, rest/wake, details, let out, and hide.
Hover over an icon for its label. There is no permanent footer text; care feedback
appears briefly over the portrait. Detailed adds all five care meters,
strength/stamina/agility/defense, total XP and the next level threshold, GitHub
identity and last activity, and Play, Medicine, Vacation controls.

Drag the pet itself, the header, or empty habitat space to move its home. A short
click on the pet still feeds it; a drag never feeds it. Releasing the mouse saves
the position and monitor to the pet's local state. Hide/show and shell restarts
restore that location. Switching views keeps the saved home position, while
clamping the visible window inside the screen if the larger view would overflow.
If the saved monitor is disconnected, the habitat falls back to an available one.
Roaming does not overwrite the habitat's saved position.

**Let out ↗** releases an awake, healthy companion with at least 20 food and energy.
He runs around the current screen, bouncing away from its edges. Click him to bring
him home. Only the small moving pet window accepts input; there is no full-screen
mouse interception. Playtime is cosmetic and doesn't damage your pet or spend XP.
Sleep, sickness, low food/energy, or vacation automatically end roaming.

Surprise escapes are on by default. After a 15-minute grace period, each minute has
an 8% chance to release a visible, eligible pet (roughly 12.5 more minutes on average).
There is a 15-minute cooldown after being released or brought home. Hidden pets
never spontaneously reappear. Turn **Surprise escapes** off in Detailed view if you
prefer manual playtime. Shell restarts begin a new grace period. Roaming resumes
if it was saved, and uses the compositor's default output.

```sh
omapet desktop view detailed     # simple or toggle also work
omapet desktop roam on           # off brings him home
omapet desktop escapes off       # disable surprise escapes
```

## Eleven companions, your choice

New pets are randomly assigned a cat, fox, bunny, frog, bear, owl, slime, robot, penguin, snake, or gopher.
Existing pets receive a character once on migration; their name and progress are
preserved. Each has its own desktop silhouette and terminal portrait.
Press **b** in the TUI, choose **1–9**, **s** for snake, **g** for gopher, or **0** for a surprise. Press **n** to rename.
Changing characters is cosmetic and keeps all stats and progress.

```sh
omapet character fox      # or cat, bunny, frog, bear, owl, slime, robot, penguin, snake, gopher, random
omapet name Fern
```

## Progress that makes sense

GitHub activity builds training experience; it does not replace food or sleep.

| Contribution | Trait | XP each | Reward cap / UTC day | Reason |
| --- | --- | ---: | ---: | --- |
| Commit | Strength | 4 | 12 | Repeated practice |
| Pull request opened | Stamina | 16 | 3 | Carrying work through a larger task |
| Issue opened | Agility | 10 | 3 | Spotting problems and opportunities |
| Pull request review | Defense | 12 | 5 | Protecting teammates and catching mistakes |

Each sync reads seven UTC days, including today, from GitHub's GraphQL
`viewer.contributionsCollection`. First sync grants the same capped seven-day
welcome training. Historical daily high-water marks prevent double rewards when
resyncing, deleting contributions, or crossing a date boundary. Each pet bonds to
one GitHub login; switching accounts requires a separate `OMAPET_HOME`.

Level is `1 + floor(sqrt(XP / 100))`. Each trait starts at `8 + 2 × level`, plus
`min(30, floor(2 × sqrt(rewarded contributions of that type)))`. This makes your
contribution mix visible without making commit volume overwhelmingly powerful.
Caps also reduce incentives to split work or open low-value issues. These are game
signals, not measurements of engineering quality.

GitHub contribution eligibility applies: commits must count toward the GitHub
contribution graph, activity may appear with a delay, and private activity depends
on your authentication and access. We count review contributions as GitHub defines
them, rather than every review comment. No repository contents are fetched.
The GitHub CLI supplies authentication; Omapet never stores or forwards its token.
Only the signed-in user's metrics are read. Failed syncs do not change progression.
Days outside the rolling seven-day window cannot be recovered by later syncs.

## Care and rest

TUI keys: **f** feed, **c** clean, **s** sleep/wake, **p** play, **m** medicine,
**g** GitHub sync, **v** vacation, **o** desktop visibility, **a** arena,
**n** rename (Ctrl+U clears the input), **b** character picker,
**r** revive, **q** quit. `omapet care ACTION` exposes the same actions to scripts.

Food, cleanliness, energy, and joy decay with elapsed real time. Feeding makes
crumbs; playing costs food and energy. Sleep restores 10 energy/hour and slows
hunger. Danger means food <10, cleanliness <10, or energy <5. Six continuous hours
of danger cause sickness; danger or sickness costs 2.5 health/hour. Safe, healthy
conditions restore 1.5 health/hour. Feed and clean before administering medicine.
Care has no GitHub requirement and never costs contribution XP.

Gentle mode is the default: neglect can make your pet sick but health stops at 1.
`omapet hardcore on` enables death at zero health. `omapet care revive` brings your
companion back without erasing its level. Arena damage never harms your home pet.
Vacation freezes all care needs. Taking time off GitHub never directly harms the
pet. Offline care catches up when any interface reads state, with at most seven
days of decay applied per read after a long absence. Closing the TUI does not pause
care; use vacation for that.

State lives in `$XDG_DATA_HOME/omapet/pet.json` (normally
`~/.local/share/omapet/pet.json`), protected by a file lock and atomic replacement.
Use `OMAPET_HOME=/another/folder` for a separate pet or demo. Arena client credentials
are stored separately with mode 0600. Pet data is retained when the plugin is removed.

GitHub sync is explicit by default. To opt into hourly updates after authenticating:

```sh
mkdir -p ~/.config/systemd/user
cp integrations/omapet-sync.{service,timer} ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now omapet-sync.timer
```

## Meet in the arena

One person hosts; friends connect to the same server over a trusted LAN/VPN or an
HTTPS reverse proxy. There is no hosted matchmaking service to sign up for.

```sh
# Host: generate and privately share an invitation. Keep these files out of git.
python3 -c 'import secrets; print(secrets.token_urlsafe(24))' > arena-invite.txt
chmod 600 arena-invite.txt
python3 -m omapet.arena --invite-file arena-invite.txt --host 127.0.0.1

# Every player: use the address exposed by your VPN or HTTPS proxy.
omapet arena connect http://127.0.0.1:8765
# The invitation is prompted without echo, rather than put in shell history.
omapet
```

For a trusted LAN/VPN, bind `--host` to that interface's address. Internet-facing
servers should sit behind HTTPS, request-rate limits, and connection limits.
The stdlib HTTP server is intended for small private groups. An invitation grants
registration access; treat it as a shared secret. HTTP sends arena tokens in cleartext,
so use HTTPS outside a trusted network. No GitHub credentials, logins, repository
names, contribution records, or home-care state are sent to the arena. A pet name
and four bounded traits are shared. The server stores hashed client tokens.

Press **a**, then **j** to queue. Two queued players automatically match. Each round,
choose **1** strike, **2** guard, or **3** feint; choices stay secret until both submit.
Strike beats feint, feint beats guard, guard beats strike. Strength powers strikes
and guards, agility powers feints, defense reduces damage, stamina adds battle HP.
Turns resolve simultaneously. A battle ends at zero HP or after 30 rounds. No
completed turn for five minutes expires a match; **l** leaves or concedes.

Completed matches grant 30 XP for a win, 10 for a loss or draw, for the first five
matches per UTC day. Each rewarded match costs 10 home energy. Concessions and
expired matches grant no XP. Repeated polling does not re-award XP. Players must
be healthy, awake, outside vacation, and have at least 20 energy to join through
the standard client.

The server owns turn order, hidden moves, HP, results, and match persistence.
Client-provided traits are clamped to 10–60, but they are **not cryptographically
verified**. Local saves and arena rewards can be edited. This is a friendly arena,
not an anti-cheat or ranked service. Server restarts retain players and matches;
change the invitation to prevent new registrations, and remove a player's record
from the stopped server's state to revoke its token.

## Development and removal

```sh
python3 -m unittest discover -s tests -v
QT_QPA_PLATFORM=offscreen /usr/lib/qt6/bin/qmltestrunner -input tests/qml
omarchy plugin validate .
# qmllint is commonly at /usr/lib/qt6/bin/qmllint on Arch.
qmllint -I "$OMARCHY_PATH/shell" BarWidget.qml PetModel.qml PetSprite.qml DesktopPet.qml
```

The installed Quickshell uses dynamic platform types; qmllint may report
`PanelWindow` as uncreatable and lack `QProcess::ExitStatus` metadata even for
valid runtime usage. Shell imports also need to resolve `qs.Ui` to the installed
shell's `Ui` directory. Actual desktop rendering should be checked in a running
Quattro session.

Disable/remove with `omarchy plugin remove jrh89.omapet`, remove the launcher
`~/.local/bin/omapet`, and remove the Waybar module if configured. If you opted into
sync, run `systemctl --user disable --now omapet-sync.timer` and remove the two unit
files, then `systemctl --user daemon-reload`. Remove the data directory separately
only if you want to erase your pet. A launcher-only install is removed by deleting
the launcher. No system-owned Omarchy files are modified.

Implementation references: [Quattro plugin development](https://plugins.omarchy.org/develop.html),
[Omarchy shell contract](https://github.com/omacom/omarchy/blob/quattro/shell/README.md),
[GitHub GraphQL API](https://docs.github.com/en/graphql/reference).
