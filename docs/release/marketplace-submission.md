# Marketplace submission draft

Use the official **Submit a plugin** form:
https://github.com/omacom/omarchy-plugin-marketplace/issues/new?template=submit-plugin.yml

**Title:** [Plugin]: Omapet

**Repository URL:** https://github.com/JRH89/omapet

**Category:** Desktop

**Tags:** Games, Bar, Quickshell

**Suggested tag:** Leave blank.

**Maintainer notes:**

Omapet is a virtual pet for Omarchy Quattro with a bar widget, compact/detailed
on-screen habitat, and terminal care dashboard. Twelve characters grow through
capped GitHub contribution XP. Users feed, clean, rest, rename, and care for the
pet manually. The habitat can be dragged with persistent positioning; playtime
allows desktop roaming and optional surprise escapes. A Waybar adapter and casual
private TUI arena are also included.

The plugin uses Quattro's existing Quickshell process. Python 3.11+ and its standard
library are required; there are no third-party Python runtime packages. GitHub CLI
is optional for contribution sync and uses the user's existing authentication.
No GitHub token is stored by the pet or sent to the arena. Sync is manual by default;
a user timer is opt-in. The arena requires an explicitly configured private server
and is intended for trusted groups, not ranked competition.

All pet state and optional arena client credentials stay in the user's data
directory. Installation and removal are documented. The optional installer
refuses to overwrite existing files. No sudo, system-file writes, automatic
package installs, telemetry, or hosted backend are required. Original sprites
are drawn in QML; source, screenshots, and code are distributed under MIT.

The repository includes manifest.json, LICENSE, README, preview.png, three actual
screenshots, a changelog, portable release checks, and a GitHub Actions workflow.
Local validation covers the Omarchy manifest, Python tests, QML drag tests, and
live desktop rendering. Multi-monitor hot-plug behavior is not yet manually tested.

**Form checkboxes:** Review and check the five declarations in the official form
when the repository is public. They cover public install/removal docs, license and
dependencies, ownership/asset rights, configuration consent, and the listing's
security-review limitations. These have not been submitted on your behalf.
