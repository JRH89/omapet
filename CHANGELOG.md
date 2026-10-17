# Changelog

## Unreleased

- Make energy easier to maintain: meals restore 8 energy, sleep restores 20/hour,
  awake drain is 1/hour, and playing costs 6 energy.

- Add an optional fullscreen pixel-pet screensaver with direction changes, multi-monitor
  support, a habitat preview button, and reversible Omarchy idle integration.
  The screensaver only reads appearance and never modifies the pet.

- Add occasional pixel poop during outings, with click-to-clean animations and a home gate.
- Include an early screen bonk on manual outings as well as random escapes.
- Simplify the bar to pet icon and status; move name, level, and care stats to hover.

- Roaming pets occasionally bonk the screen and leave animated, repairable cracks.
  Repair every crack before bringing them home; keyboard repair is also available.

- Larger ASCII portraits for all twelve pets, character-matched terminal colors, blinking,
  sleep expressions, and clearer picker thumbnails.
- Add a rubber duck character, available with the picker’s **d** key or `omapet character duck`.
- Redraw all twelve companions with expressive faces and distinct silhouettes.
- Render sprites on a small pixel grid with unfiltered scaling, including care animations.

- Show a miniature version of the selected pet beside its name and level in the bar.
- Explain blocked playtime actions on hover, including low energy, hunger, and sickness.

## 0.1.0 — Initial preview

- Native Omarchy Quattro bar widget and draggable desktop habitat with saved position.
- Compact icon toolbar and detailed care, combat, XP, and GitHub statistics.
- Eleven selectable characters with animated care and roaming; optional random escapes.
- Terminal dashboard with naming and character selection, plus a Waybar JSON adapter.
- Capped, replay-safe GitHub contribution XP through existing GitHub CLI authentication.
- Manual care, vacation, gentle mode, optional death, and revival without lost progress.
- Private, invitation-based TUI sparring arena with simultaneous secret moves.

This is an early release. The arena is intended for trusted groups and accepts
client-provided traits; it is not a ranked or cheat-resistant service. Desktop
rendering and drag behavior have been checked on a single-monitor Hyprland setup.
Multi-monitor hot-plug behavior has not been manually verified.
