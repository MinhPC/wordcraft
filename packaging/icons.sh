#!/usr/bin/env bash
# Regenerate every app icon from the background-free W (assets/app-icon/wordcraft-glyph.png).
#
# Needs: resvg (brew install resvg / cargo install resvg). On macOS, iconutil also writes the
# .icns. The outputs are committed, so builds and packaging never need these tools.
#
#   packaging/icons.sh
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIR="$ROOT/assets/app-icon"
SVG="$DIR/wordcraft.svg"
ID="ai.storyteller.wordcraft"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

command -v resvg >/dev/null || { echo "error: resvg not found (brew install resvg)" >&2; exit 1; }

# packaging/icon_tight.py (Python with Pillow) cleans the artwork and writes two SVGs:
# wordcraft.svg (macOS: the W inside the Dock icon grid's margin) and wordcraft-full.svg
# (Windows and Linux: the W fills the square).
MAC="$SVG"
python3 "$ROOT/packaging/icon_tight.py"
FULL="$DIR/wordcraft-full.svg"

render() { resvg -w "$2" -h "$2" "$1" "$3" </dev/null; }

render "$MAC" 1024 "$DIR/wordcraft-1024.png"
# Runtime window/Dock icon on macOS (embedded by apps/wordcraft); other platforms use hicolor 256.
render "$MAC" 512 "$DIR/wordcraft-macos-512.png"

# Linux hicolor theme.
for s in 16 24 32 48 64 128 256 512; do
  mkdir -p "$DIR/hicolor/${s}x${s}/apps"
  render "$FULL" "$s" "$DIR/hicolor/${s}x${s}/apps/$ID.png"
done
mkdir -p "$DIR/hicolor/scalable/apps"
cp "$FULL" "$DIR/hicolor/scalable/apps/$ID.svg"

# Windows .ico.
ICO_PNGS=()
for s in 16 20 24 32 40 48 64 128 256; do
  render "$FULL" "$s" "$TMP/ico-$s.png"
  ICO_PNGS+=("$TMP/ico-$s.png")
done
(cd "$ROOT" && cargo run -q -p xtask -- ico "$DIR/wordcraft.ico" "${ICO_PNGS[@]}")

# macOS .icns.
if command -v iconutil >/dev/null; then
  SET="$TMP/wordcraft.iconset"
  mkdir -p "$SET"
  for s in 16 32 128 256 512; do
    render "$MAC" "$s" "$SET/icon_${s}x${s}.png"
    render "$MAC" $((s * 2)) "$SET/icon_${s}x${s}@2x.png"
  done
  iconutil -c icns -o "$DIR/wordcraft.icns" "$SET"
else
  echo "warning: iconutil not found (macOS only); wordcraft.icns not regenerated" >&2
fi
echo "icons written to $DIR"
