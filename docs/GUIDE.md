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
Hover over a blocked Let out button to see exactly what your pet needs first.
He runs around the current screen, bouncing away from its edges. Click him to bring
him home once any screen cracks are repaired. Occasionally he bonks the screen,
pauses briefly, and leaves a pretend glass crack. Manual outings and surprise
escapes both include bonks, with an early bonk after release. He may also leave
pixel poop: click its **Clean up** badge before bringing him home. Click each crack's **Repair** badge
to patch it with an animation. Up to four cracks or poop piles can appear; once you start repairing,
he stops making new ones until his next outing. He keeps running between bonks.
Only the small pet and crack windows accept input; there is no full-screen mouse
interception. Playtime doesn't damage your pet or spend XP. Press **x** in the TUI
to repair one crack, or run `omapet repair all` for keyboard access.
Sleep, sickness, low food/energy, or vacation end roaming after all cracks are fixed;
an exhausted pet waits outside while repairs are pending.

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

## Twenty companions, your choice

New pets are randomly assigned a cat, fox, bunny, frog, bear, owl, slime, robot, penguin, snake, gopher, or rubber duck.
Existing pets receive a character once on migration; their name and progress are
preserved. Each has its own desktop silhouette and terminal portrait.
Press **b** in the TUI, choose **1–9**, **s** for snake, **g** for gopher, **d** for duck, or **0** for a surprise. Press **n** to rename.
Changing characters is cosmetic and keeps all stats and progress. Eight more developer-themed
companions are available: octocat, Android robot, Rust crab, Docker whale, PostgreSQL
elephant, Perl camel, Beaver, and a bug. The picker shows every shortcut.

```sh
omapet character fox      # or cat, bunny, frog, bear, owl, slime, robot, penguin, snake, gopher, duck, random
omapet name Fern
```

## Your household, adoption, and trading

Press **k** in the TUI for your collection. Use the arrows to select a pet and
**Enter** to care for it. **h** opens the new-pet picker; **Tab** on Home cycles pets.
Each of up to 24 pets has its own needs, XP and contribution-trained traits. All
pets age while they are at home, including companions you are not viewing. Use
vacation on an individual pet to pause its needs. Existing saves keep their pet.
GitHub identity and contribution high-water marks belong to the household, so
switching pets cannot reward the same contribution twice.

Detailed desktop view has **Next pet**, **Hatch**, and **All out** buttons. All out
releases every eligible pet on the current screen. They automatically form groups
of four for four-square and pairs for catch; a leftover single pet keeps wandering.
Games share a ball, line up around a court, and smoothly regroup as pets come and
go. Balls/courts do not capture clicks over your applications. Group play is visual;
for training XP use the spar controls below.

Occasionally one group gathers, charges, and **team bonks** the desktop. A team
impact makes up to two larger cracks, within the household's shared limit of four
cracks or poop piles. A team can attack at most once every 90 seconds, and cleanup
pauses further damage until a new outing. Ineligible pets leave games automatically.
Hiding/showing pets starts a new game session rather than jumping into an old attack.
Click a companion to send it home after cleanup; right-click it to select it.
Screen messes and cooldowns belong to the household and remain visible after switching
pets. Solo pets retain their normal roaming, bonks and surprise escapes. In the collection, **o** releases pets and **i** brings them home
(after repairing any active-pet messes).

Select a different pet from the active one and press **p** to play together or
**f** to train them in an automatic friendly 1v1 spar. Local training uses the real
combat rules. Every participant earns **20 XP** for each of their first **five
household spars per UTC day**, win or lose. That is up to 100 training XP per pet
per day, separate from care and online battle rewards. Further spars are still
available but give no XP. Each spar spends 10 energy per participant, restores
5 joy, and causes no injuries. Pets must be awake, healthy, out of vacation mode,
and have at least 20 energy. Level-ups improve all four combat traits.

Daily training history stays with the pet when you switch, trade or adopt it.
Other pets do not gain XP just for living in the household. For a local 2v2,
supply four IDs: the first two form one team, and the last two form the other.
All four participants can earn training XP, including knocked-out teammates.

```sh
omapet pets list
omapet pets hatch crab --name Ferris
omapet pets switch PET_ID
omapet care feed --pet PET_ID
omapet pets roam on                  # all eligible pets
omapet pets play FIRST_ID SECOND_ID
omapet pets spar FIRST_ID SECOND_ID
omapet pets spar A_ID B_ID C_ID D_ID
omapet arena queue --team FIRST_ID SECOND_ID
```

Online 2v2 uses **two pets per player**. The collection's **j** key queues the active
and selected pet; select a different pet first. You match against another two-pet
team. One hidden strike/guard/feint command controls your team each round. Each
surviving pet attacks; the front pet absorbs damage before its teammate. Knocked-out
pets stop attacking. Both participating pets receive the usual online XP reward;
the five rewarded matches per UTC day cap applies to the whole household.

Connect to a private arena with `omapet arena connect URL`. In your collection,
**u** offers the selected pet for free adoption and **t** offers it for an open trade.
An open trade accepts any living pet in return, including a lower-level pet.
**e** opens the exchange board; **g** refreshes offers and collects deliveries.
**Enter** adopts a free pet, or trades your selected household pet for a trade offer.
**x** cancels your own selected offer. Keep at least one pet at home.

```sh
omapet pets offer PET_ID                    # free adoption
omapet pets offer PET_ID --mode trade       # accepts any living pet
omapet pets board
omapet pets claim LISTING_ID                # free adoption
omapet pets claim LISTING_ID --pet MY_ID     # exchange your pet for a trade offer
omapet pets cancel LISTING_ID
omapet pets sync                            # collect arrivals / retry interrupted transfers
```

Offers move pets into server escrow until adopted, traded, or cancelled. Escrow
pauses their needs. Names, characters, XP, trained totals, and care meters transfer;
GitHub identities, contribution histories, desktop settings and arena credentials
stay private. The new owner can train the pet with their own GitHub account.
After a connection interruption, run **pets sync** before making another transfer.
The transfer journal and server operation receipts make retries idempotent.
If your household fills up, deliveries wait on the server until you make room.
Back up both the local pet save and arena identity file; the server's arena save
contains outstanding offers and deliveries. Both client and server must be updated
for exchange and team features. This remains a casual, trusted-group system with
client-supplied progress, rather than a cheat-resistant economy.

## Progress that makes sense

Useful feeding, cleaning, play, medicine and a completed hour of sleep each earn
12 XP, up to 120 care XP per pet per UTC day. Each care action has a 30-minute
reward cooldown; sleep must last at least an hour, with at least an hour between
rest rewards. Medicine for an already healthy pet and cleaning an already-clean pet earn no XP.
Care levels improve every combat trait through the existing level bonus. GitHub
activity adds training experience and specialized traits.

Joy falls by 1.5 per hour. Below 60, your pet feels lonely; below 25, it feels sad.
Play restores joy. The sprite expresses these moods even when hunger is the main
status; sickness is visible even when a sick pet is sleeping.

| Contribution | Trait | XP each | Reward cap / UTC day | Reason |
| --- | --- | ---: | ---: | --- |
| Commit | Strength | 4 | 12 | Repeated practice |
| Pull request opened | Stamina | 16 | 3 | Carrying work through a larger task |
| Issue opened | Agility | 10 | 3 | Spotting problems and opportunities |
| Pull request review | Defense | 12 | 5 | Protecting teammates and catching mistakes |

Each sync reads seven UTC days, including today, from GitHub's GraphQL
`viewer.contributionsCollection`. First sync grants the same capped seven-day
welcome training. Historical daily high-water marks prevent double rewards when
resyncing, deleting contributions, or crossing a date boundary. Each household bonds to
one GitHub login; switching accounts requires a separate `OMAPET_HOME`. Sync rewards
the pet active when the request starts, even if you switch companions while it runs.

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
crumbs and restores 8 energy (up to 100); a full pet cannot eat again. Playing
costs 6 energy and 5 food. Awake pets lose 1 energy/hour. Sleep restores
20 energy/hour and slows
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

GitHub sync runs automatically when the TUI starts, when the bar widget loads,
and whenever you show the desktop pet. It uses your existing `gh` login in the
background, without an authentication prompt. Startup requests from both interfaces
share a lock and a 60-second cooldown, so simultaneous opens or rapid hide/show
cycles do not repeatedly call GitHub. Care stays responsive while syncing and
when offline; failed automatic attempts are quiet. Run `gh auth login` once to
enable contribution XP, and press **g** or run `omapet sync` to retry manually
without waiting for the cooldown. Ordinary status polling never syncs.

To also opt into hourly updates while no interface is open:

```sh
mkdir -p ~/.config/systemd/user
cp integrations/omapet-sync.{service,timer} ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now omapet-sync.timer
```

## Pet screensaver

The optional screensaver shows your selected pixel companion running and turning
around on a dark fullscreen background, on each connected monitor. Move the mouse,
click, or press a key to dismiss it. Use **Preview pet screensaver** in the detailed
habitat, or run:

```sh
omapet screensaver preview       # try it now, without changing idle settings
omapet screensaver enable        # use it when Omarchy starts the screensaver
omapet screensaver disable       # restore Omarchy's default idle service
```

The terminal command must be installed for automatic screensaver integration;
see the README's optional terminal command instructions. Enabling creates a user
clone of Omarchy's idle service and changes only its screensaver launch command.
Existing idle customizations are preserved: automatic setup refuses to overwrite
an existing idle clone. For a custom clone, replace `omarchy-launch-screensaver`
in its screensaver launch command with `omapet screensaver run` yourself.

The preview reads only the saved name and character. It never writes pet state,
spends energy, grants XP, or creates poop or cracks. Ordinary pet care timers keep
passing as usual; this animation does not count as exercise or sleep. Use Vacation
mode separately if you want to pause care while away.

Omarchy's idle timeout, Stay Awake setting, screensaver-off toggle, and lock timer
remain in effect. Preview works even when automatic screensavers are disabled.
Locking closes the animation through Omarchy's normal screensaver cleanup.
