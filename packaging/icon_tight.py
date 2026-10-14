#!/usr/bin/env python3
"""Background-free variant of the app icon for Windows and Linux.

The supplied artwork (assets/app-icon/wordcraft-glyph.png) is the blue paper-ribbon W with a
transparent background. Windows and Linux desktops show icons without a plate (like most apps
there), so this script cleans it and crops it to fill the square. It:

  * writes assets/app-icon/wordcraft-full.svg (Windows/Linux: the W fills the square) and
    assets/app-icon/wordcraft.svg (macOS: the same W inside the Dock's icon-grid margin), each
    with the PNG embedded,
  * with --render: writes the hicolor PNGs, wordcraft.ico, wordcraft-1024.png,
    wordcraft-macos-512.png and wordcraft.icns directly (Pillow), for machines without resvg.

    python3 packaging/icon_tight.py [--render]

"""
import base64
import io
import sys
from pathlib import Path

from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
DIR = ROOT / "assets" / "app-icon"
SRC = DIR / "wordcraft-glyph.png"
APP_ID = "ai.storyteller.wordcraft"
# Fraction of the canvas the mark fills: a hair under 1 so antialiased edges are never clipped.
FILL = 0.985
# macOS icon grid: the artwork sits inside about 80% of the 1024 canvas, the rest is margin.
FILL_MAC = 0.80


def tight(src: Image.Image) -> Image.Image:
    """The supplied background-free W, cleaned and cropped to a square.

    Specks the artwork has around its edges are dropped (only pixels near the solid ribbon
    survive), and the near-opaque interior is made fully opaque."""
    im = src.convert("RGBA")
    r, g, b, a = im.split()
    solid = a.point(lambda v: 255 if v >= 128 else 0)
    box = solid.getbbox()
    if box is None:
        raise SystemExit("no ribbon found in the artwork")
    near = solid.filter(ImageFilter.MaxFilter(7)).filter(ImageFilter.GaussianBlur(1.0)).point(lambda v: 255 if v > 8 else 0)
    # Interior alpha ~253 -> 255; soft antialiased edges keep their values.
    a = a.point(lambda v: 255 if v >= 240 else v)
    a = Image.composite(a, Image.new("L", a.size, 0), near)
    glyph = Image.merge("RGBA", (r, g, b, a))
    pad = 2
    box = (max(box[0] - pad, 0), max(box[1] - pad, 0), min(box[2] + pad, im.width), min(box[3] + pad, im.height))
    crop = glyph.crop(box)
    side = max(crop.size)
    canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    canvas.paste(crop, ((side - crop.width) // 2, (side - crop.height) // 2))
    return canvas


def sized(sq: Image.Image, n: int, fill: float = FILL) -> Image.Image:
    inner = max(round(n * fill), 1)
    out = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    # Premultiplied resampling avoids dark fringes on the transparent corners.
    pm = sq.resize((inner, inner), Image.LANCZOS)
    if n <= 32:
        pm = pm.filter(ImageFilter.UnsharpMask(radius=0.6, percent=60, threshold=0))
    out.paste(pm, ((n - inner) // 2, (n - inner) // 2), pm)
    return out


def main() -> None:
    sq = tight(Image.open(SRC))
    master = sized(sq, 1024)
    png512 = io.BytesIO()
    sized(sq, 512).save(png512, "PNG", optimize=True)
    b64 = base64.b64encode(png512.getvalue()).decode()
    (DIR / "wordcraft-full.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">\n'
        "  <!-- Full-bleed WordCraft paper-ribbon W (packaging/icon_tight.py); embedded raster artwork,"
        " MIT OR Apache-2.0. -->\n"
        f'  <image width="512" height="512" href="data:image/png;base64,{b64}"/>\n'
        "</svg>\n",
        encoding="utf-8",
    )
    mac512 = io.BytesIO()
    sized(sq, 512, FILL_MAC).save(mac512, "PNG", optimize=True)
    mac_b64 = base64.b64encode(mac512.getvalue()).decode()
    (DIR / "wordcraft.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">\n'
        "  <!-- WordCraft paper-ribbon W with the macOS icon-grid margin (packaging/icon_tight.py);"
        " embedded raster artwork, MIT OR Apache-2.0. -->\n"
        f'  <image width="512" height="512" href="data:image/png;base64,{mac_b64}"/>\n'
        "</svg>\n",
        encoding="utf-8",
    )
    print("wrote", DIR / "wordcraft-full.svg", "and", DIR / "wordcraft.svg")
    if "--render" not in sys.argv:
        return
    for s in (16, 24, 32, 48, 64, 128, 256, 512):
        out = DIR / "hicolor" / f"{s}x{s}" / "apps" / f"{APP_ID}.png"
        out.parent.mkdir(parents=True, exist_ok=True)
        sized(sq, s).save(out, "PNG", optimize=True)
    scalable = DIR / "hicolor" / "scalable" / "apps" / f"{APP_ID}.svg"
    scalable.write_bytes((DIR / "wordcraft-full.svg").read_bytes())
    ico_sizes = [16, 20, 24, 32, 40, 48, 64, 128, 256]
    master.save(DIR / "wordcraft.ico", format="ICO", sizes=[(s, s) for s in ico_sizes])
    # Pillow resamples the master for each ICO size; re-embed our own per-size renders instead.
    frames = [sized(sq, s) for s in ico_sizes]
    frames[-1].save(DIR / "wordcraft.ico", format="ICO", sizes=[(s, s) for s in ico_sizes], append_images=frames[:-1])
    sized(sq, 1024, FILL_MAC).save(DIR / "wordcraft-1024.png", "PNG", optimize=True)
    sized(sq, 512, FILL_MAC).save(DIR / "wordcraft-macos-512.png", "PNG", optimize=True)
    icns = [sized(sq, n, FILL_MAC) for n in (16, 32, 64, 128, 256, 512, 1024)]
    icns[-1].save(DIR / "wordcraft.icns", format="ICNS", append_images=icns[:-1])
    print("wrote hicolor PNGs, scalable SVG, wordcraft.ico, macOS PNGs and wordcraft.icns")


if __name__ == "__main__":
    main()
