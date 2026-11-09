#!/usr/bin/env bash
# Rebuilds every Sphere Dark theme from source and puts the installable files in dist/.
# Requirements: python3 with Pillow, pysassc (pip install libsass) or sassc, git, zip.
set -euo pipefail
cd "$(dirname "$0")"
DIST=dist
rm -rf "$DIST"; mkdir -p "$DIST"

# Desktop (GTK 2/3/4, xfwm4, libadwaita) is built on top of Linux Mint's Mint-Y sources.
MINT_THEMES="${MINT_THEMES:-.cache/mint-themes}"
if [[ ! -d "$MINT_THEMES/src/Mint-Y" ]]; then
  echo "Fetching linuxmint/mint-themes into $MINT_THEMES ..."
  git clone --depth 1 https://github.com/linuxmint/mint-themes "$MINT_THEMES"
fi
python3 desktop/build.py "$MINT_THEMES/src/Mint-Y" desktop
tar czf "$DIST/Sphere-Dark.tar.gz" -C desktop Sphere-Dark

# Blender 5.2 extension
python3 blender/build.py blender/source/blender_default_5.2.xml blender/extension/sphere_dark.xml
(cd blender/extension && zip -q -r "../../$DIST/sphere_dark-blender-1.0.0.zip" blender_manifest.toml sphere_dark.xml)

# Krita, Unreal Engine, Ardour
python3 krita/build.py krita/source/KritaDarker.colors "krita/Sphere Dark.colors"
python3 unreal/build.py unreal/SphereDark.json
python3 ardour/build.py ardour/source/dark-ardour.colors ardour/sphere_dark-ardour.colors
cp "krita/Sphere Dark.colors" unreal/SphereDark.json ardour/sphere_dark-ardour.colors "$DIST/"

# Firefox (unsigned; see firefox section of the README to sign it)
(cd firefox && zip -q -r "../$DIST/sphere-dark-firefox.zip" manifest.json images)

# Terminal, YouTube, login screen: plain files
tar czf "$DIST/sphere-dark-terminal.tar.gz" -C terminal sphere-dark.theme install.sh
cp youtube/sphere-dark-youtube.user.css login/install-login-assets.sh "$DIST/"

echo; echo "Done. Installable files:"; ls -1 "$DIST"
