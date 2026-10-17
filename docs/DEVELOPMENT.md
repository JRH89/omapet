# Development

[Back to the README](../README.md)

## Run from a checkout

```sh
git clone https://github.com/JRH89/omapet.git
cd omapet
./bin/omapet
```

Python 3.11+ is sufficient for the terminal dashboard. Desktop development also
requires a running Omarchy Quattro session. There are no Python runtime packages
to install.

For a copied local development installation:

```sh
python3 scripts/install.py --quattro
```

The helper validates the manifest, copies the checkout into the user plugin
directory, creates an optional launcher, and enables the plugin. It refuses to
overwrite existing plugin folders or launchers. Use a normal Git-managed install
for `omarchy plugin update`; a copied development folder cannot be updated that way.
User-owned plugin files can be edited under `~/.config/omarchy/plugins/jrh89.omapet/`.
Never edit system-owned Omarchy files. Quickshell may retain QML types in its cache;
use `omarchy restart shell` if hot reload does not display a code change.

## Verify changes

```sh
python3 scripts/check_release.py
omarchy plugin validate .
QT_QPA_PLATFORM=offscreen /usr/lib/qt6/bin/qmltestrunner -input tests/qml
```

The portable checks include the manifest/version contract, required release
assets, and Python tests. The QML tests distinguish clicks from drags and verify
that a drag saves on release. GitHub responses are mocked; arena tests exercise
a real local HTTP server.

On Arch, QML tools are commonly under `/usr/lib/qt6/bin`. To resolve Quattro's
`qs.Ui` imports for linting, create temporary import aliases outside the plugin:

```sh
IMPORT_DIR=$(mktemp -d)
mkdir -p "$IMPORT_DIR/qs"
ln -s /usr/share/omarchy/shell/Ui "$IMPORT_DIR/qs/Ui"
ln -s /usr/share/omarchy/shell/Commons "$IMPORT_DIR/qs/Commons"
/usr/lib/qt6/bin/qmllint -I "$IMPORT_DIR" ./*.qml
rm -r "$IMPORT_DIR"
```

Quickshell provides some platform types dynamically. Its installed metadata may
report `PanelWindow` as uncreatable, unresolved margin types, or missing
`QProcess::ExitStatus` even for working runtime usage. Always check actual rendering
in Quattro as well. Single-monitor rendering, roaming, hide/show, and position
restoration have been checked locally. Multi-monitor hot-plug remains unverified.

## Build the source archive

```sh
python3 scripts/package_release.py
```

This runs the portable checks and writes a reproducible archive plus SHA256
checksum under `dist/`. It uses an explicit set of source and documentation
paths and excludes Git history, bytecode, local pet saves, arena state, and tokens.
See [PUBLISHING.md](../PUBLISHING.md) for marketplace submission.
