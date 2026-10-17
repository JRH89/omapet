# Caring for your Omapet

[Back to the README](../README.md)

The command examples below use the optional `omapet` launcher. From a checkout,
use `./bin/omapet` instead. All care and character controls are also available
from the TUI opened by clicking the bar widget.

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

