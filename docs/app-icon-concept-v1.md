# WordCraft app icon — concept v1

Created 2026-10-14 using the built-in OpenAI image generation tool. Original generation without reference images. Approved artwork under the repository's MIT OR Apache-2.0 terms.

Asset: [wordcraft-concept-v1.png](../assets/app-icon/wordcraft-concept-v1.png). Approved and installed on 2026-10-14: Windows executable/installer and web favicon use `wordcraft.ico`; macOS uses `wordcraft.icns` and `wordcraft-macos-512.png`; Linux/runtime use the hicolor PNGs. The SVG wrappers embed the approved PNG, preserving its exact artwork rather than claiming to be vector masters. `packaging/icons.sh` regenerates derived assets using resvg and, on macOS, iconutil. Update (2026-10-14, later): the app icon no longer has a tile. `assets/app-icon/wordcraft-glyph.png` is the same W on a transparent background; `packaging/icon_tight.py` cleans it and writes the Windows/Linux icons with the W filling the square, and the macOS icons with the W inside the Dock's icon-grid margin (about 80% of the canvas). The concept PNG with its tile stays as the design record.

Direction: a white paper ribbon forming W, a folded corner suggesting a document, and the project's indigo palette. The broad silhouette is intended to remain recognizable at small sizes; platform size variants have been exported; visual and decode validation are recorded below.

## Generation prompt

Use case: logo-brand. Create one original production-quality app icon concept for WordCraft, an independent open-source word processor. Square composition, a single large rounded-square indigo tile floating on genuinely transparent background with generous clear edge margin. Brand palette indigo #3B5BDB, deeper indigo #2B47B5, white, subtle periwinkle. Inside tile, a unique bold white folded-paper ribbon forming a readable abstract W with two valleys; integrate a restrained small paper corner fold into the top right of the mark. Design should suggest writing, a document and precise craftsmanship using one coherent geometric silhouette. Premium desktop app feel, mostly flat vector-like geometry, very restrained smooth lighting and depth, crisp edges, generous negative space, balanced optical centering, recognizable at 32px. No small text, no wordmark, no decoration, no pen, no multi-icon presentation, no mockup, no watermark. Must be wholly original: do not copy, trace, recreate or imitate Microsoft Word/Office icons or other proprietary product assets; specifically no overlapping blue document panels or W badge attached to a document. Produce the actual standalone icon, not a presentation board.

Tool option: `transparent_background: true`.

## Integration validation (2026-10-14)

- `cargo build --offline -p wordcraft` succeeded on Windows; the icon extracted from `target/debug/wordcraft.exe` was visually inspected and shows the approved W.
- Decoded all nine ICO representations (16, 20, 24, 32, 40, 48, 64, 128, 256 px), all ICNS representations and all eight hicolor PNGs; inspected the 256 px export.
- `cargo xtask assets` passed; `cargo test --offline -p xtask ico::tests` passed all three tests; `git diff --check` passed.
- Native macOS/Linux installer appearance and the browser's favicon cache need platform validation; file references remain the same, so those builds consume the regenerated assets.
