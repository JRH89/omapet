# Publish Omapet on the Omarchy plugin website

The website lists a plugin hosted in a **public GitHub repository**. It does not
accept a local folder or a ZIP upload as the plugin source. A release archive is
optional; the marketplace reads `manifest.json` from the public repository.

Official instructions: https://plugins.omarchy.org/publish.html
Official submission form: https://github.com/omacom/omarchy-plugin-marketplace/issues/new?template=submit-plugin.yml

## Prepared locally

- Plugin ID: `jrh89.omapet`; initial version: `0.1.0`.
- Root `manifest.json`, MIT license, dependency/install/removal documentation.
- `preview.png` and actual compact, detailed, and TUI screenshots in `docs/screenshots/`.
- `CHANGELOG.md`, release checks, source archive builder, and CI configuration.
- Form-ready category, tags, and maintainer notes in
  [the marketplace submission draft](docs/release/marketplace-submission.md).

## 1. Validate the candidate

```sh
python3 scripts/check_release.py
omarchy plugin validate .
QT_QPA_PLATFORM=offscreen /usr/lib/qt6/bin/qmltestrunner -input tests/qml
python3 scripts/package_release.py
```

The archive and SHA256 checksum appear in `dist/`. It includes the plugin source,
docs, screenshots, and tests, using an explicit file list; it excludes `.git`,
bytecode, local pet data, server state, and invitation files. The archive has
normalized timestamps and ownership. CI runs portable checks on Python 3.11 and
3.14 on GitHub; consult the repository’s Actions tab for the latest results.

QML lint can also be run with installed Quattro imports. Quickshell's dynamic
platform types produce known `PanelWindow` / process exit-status metadata warnings.
See [the development guide](docs/DEVELOPMENT.md) for import-path details. Actual widget rendering, movement, and
position restoration have been checked locally; multi-monitor hot-plug remains
an unverified edge case.

## 2. Source repository and listing status

The public source repository is [JRH89/omapet](https://github.com/JRH89/omapet).
The plugin's permanent ID is `jrh89.omapet`; keep it stable across releases so
existing installations and user preferences continue to work.

The marketplace submission has not been sent. Publishing the source repository
does not automatically create a marketplace listing. Use the prepared submission
draft after checking the installation from this public source.

## 3. Verify a clean install from the public repository

On a test Quattro session:

```sh
omarchy plugin add https://github.com/JRH89/omapet.git --enable
```

The plugin runs its Python helper directly from its installed folder, so pip is
not required. Right-click its bar widget to show the pet; left-click opens the TUI.
For a standalone `omapet` command, the optional launcher-only installer is:

```sh
python3 ~/.config/omarchy/plugins/jrh89.omapet/scripts/install.py
```

The separate `scripts/install.py --quattro` helper is only for local development;
it is not part of the marketplace installation flow.

Confirm care feedback, both views, character selection, naming, dragging,
hide/show, and remembered position after shell restart. Remove the plugin with
`omarchy plugin remove jrh89.omapet`; pet data should remain. GitHub sync and arena
networking are optional and should also be checked when credentials/peers are
available. Local tests mock GitHub responses and exercise real local HTTP battles;
there has been no hosted public-server test.

## 4. Submit to the marketplace

Open the official submission form and use `docs/release/marketplace-submission.md`:

- Repository URL: **https://github.com/JRH89/omapet**.
- Category: **Desktop**.
- Tags: **Games**, **Bar**, **Quickshell** (three tags).
- Maintainer notes: copy the prepared text after reviewing it.

Review and check the form's declarations, then submit. The registry validates the
current repository commit before a maintainer approves the listing. Creating the
repository alone does not publish a marketplace listing, and submission does not
guarantee approval. No marketplace issue is created by the preparation scripts. The release archive
is local; creating a GitHub Release is optional and separate from listing approval.
