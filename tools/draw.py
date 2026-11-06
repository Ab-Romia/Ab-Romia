"""Draw the header card on this profile, in a light and a dark version.

Text is set as outlines from the fonts in tools/fonts, so the card renders the
same everywhere with no web fonts to load. Type and colours match romia.dev.

    python3 tools/draw.py        (needs fontTools and Pillow)
"""

from __future__ import annotations

import base64
import io
from dataclasses import dataclass
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from PIL import Image, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"


@dataclass(frozen=True)
class Theme:
    name: str
    bg: str
    fg: str
    muted: str
    border: str
    accent: str
    photo_ink: str      # what the darkest parts of the photo become
    photo_paper: str    # what the lightest parts become
    photo_strength: float


DARK = Theme("dark", "#0a0b0d", "#eceae4", "#9a978f", "#222327", "#6b8aff",
             photo_ink="#0a0b0d", photo_paper="#aab8f2", photo_strength=0.42)
LIGHT = Theme("light", "#f2f0eb", "#111111", "#5f5c55", "#d9d5cc", "#1f2bff",
              photo_ink="#2a3170", photo_paper="#f2f0eb", photo_strength=0.3)


def num(v: float) -> str:
    s = f"{v:.1f}"
    return s[:-2] if s.endswith(".0") else s


class Face:
    """A static font instance, set as SVG path data with its own kerning."""

    def __init__(self, file: str):
        font = TTFont(TOOLS / "fonts" / file)
        self.glyphs = font.getGlyphSet()
        self.cmap = font.getBestCmap()
        self.upm = font["head"].unitsPerEm
        self.advance = {name: adv for name, (adv, _) in font["hmtx"].metrics.items()}
        self.pairs = []
        gpos = font["GPOS"].table
        kern = {i for r in gpos.FeatureList.FeatureRecord if r.FeatureTag == "kern"
                for i in r.Feature.LookupListIndex}
        for i in sorted(kern):
            lookup = gpos.LookupList.Lookup[i]
            for st in lookup.SubTable:
                if lookup.LookupType == 9 and st.ExtensionLookupType == 2:
                    self.pairs.append(st.ExtSubTable)
                elif lookup.LookupType == 2:
                    self.pairs.append(st)

    def kern(self, a: str, b: str) -> int:
        for st in self.pairs:
            if a not in st.Coverage.glyphs:
                continue
            if st.Format == 1:
                for rec in st.PairSet[st.Coverage.glyphs.index(a)].PairValueRecord:
                    if rec.SecondGlyph == b:
                        return getattr(rec.Value1, "XAdvance", 0) or 0
            else:
                c1 = st.ClassDef1.classDefs.get(a, 0)
                c2 = st.ClassDef2.classDefs.get(b, 0)
                value = st.Class1Record[c1].Class2Record[c2].Value1
                if value is not None and getattr(value, "XAdvance", 0):
                    return value.XAdvance
        return 0

    def layout(self, s: str, size: float, tracking: float):
        """Each glyph's name and pen position, and where the run ends."""
        names = [self.cmap.get(ord(ch), ".notdef") for ch in s]
        scale, x, placed = size / self.upm, 0.0, []
        for i, name in enumerate(names):
            placed.append((name, x))
            x += self.advance[name] * scale
            if i + 1 < len(names):
                x += tracking * size + self.kern(name, names[i + 1]) * scale
        return placed, x

    def width(self, s: str, size: float, tracking: float = 0.0) -> float:
        return self.layout(s, size, tracking)[1]

    def path(self, s: str, size: float, x: float, y: float, tracking: float = 0.0) -> str:
        scale = size / self.upm
        pen = SVGPathPen(self.glyphs, ntos=num)
        for name, dx in self.layout(s, size, tracking)[0]:
            self.glyphs[name].draw(TransformPen(pen, (scale, 0, 0, -scale, x + dx, y)))
        return pen.getCommands()


DISPLAY = Face("archivo-118-800.woff")
SANS = Face("archivo-100-400.woff")
MONO = Face("jetbrains-mono-400.woff")
MONO_MEDIUM = Face("jetbrains-mono-500.woff")


def text(face: Face, parts: list[tuple[str, str]], size: float, x: float, y: float,
         tracking: float = 0.0, anchor: str = "start") -> tuple[str, float]:
    """Coloured runs on one baseline. Returns the markup and where it ends."""
    if anchor == "end":
        x -= sum(face.width(s, size, tracking) for s, _ in parts)
    out = []
    for s, fill in parts:
        out.append(f'<path fill="{fill}" d="{face.path(s, size, x, y, tracking)}"/>')
        x += face.width(s, size, tracking)
    return "".join(out), x


def photo(theme: Theme, w: int, h: int) -> str:
    """The portrait as on romia.dev: black and white with a hint of the accent,
    blurred, and quiet enough to sit behind type. Returns base64 JPEG."""
    im = Image.open(TOOLS / "portrait.jpg").convert("L")
    src_w, src_h = im.size
    crop_h = round(src_w * h / w)
    top = round((src_h - crop_h) * 0.3)  # hold the face about a third down
    im = im.crop((0, top, src_w, top + crop_h)).resize((w, h), Image.LANCZOS)
    im = ImageOps.autocontrast(im, cutoff=1).filter(ImageFilter.GaussianBlur(12))
    im = ImageOps.colorize(im, black=theme.photo_ink, white=theme.photo_paper)
    im = Image.blend(Image.new("RGB", (w, h), theme.bg), im, theme.photo_strength)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=78, optimize=True, progressive=True)
    return base64.b64encode(buf.getvalue()).decode()


def medal(x: float, y: float, size: float, stroke: str) -> str:
    """Lucide's "award" icon, drawn on a 24-unit grid."""
    return (f'<g transform="translate({num(x)} {num(y)}) scale({size / 24:.3f})" fill="none" '
            f'stroke="{stroke}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
            '<circle cx="12" cy="8" r="6"/><path d="M15.477 12.89 17 22l-5-3-5 3 1.523-9.11"/></g>')


def header(t: Theme) -> str:
    W, H, X = 1200, 420, 60
    px = 500  # where the photo starts; it fades in from here
    b = [
        "<defs>",
        f'<clipPath id="card"><rect width="{W}" height="{H}" rx="16"/></clipPath>',
        # A long, eased fade: a short one lets the bright sky in the photo
        # switch on as a visible edge.
        '<linearGradient id="fade">'
        '<stop offset="0.08" stop-color="#000"/><stop offset="0.25" stop-color="#121212"/>'
        '<stop offset="0.4" stop-color="#404040"/><stop offset="0.55" stop-color="#8c8c8c"/>'
        '<stop offset="0.7" stop-color="#d9d9d9"/><stop offset="0.82" stop-color="#fff"/></linearGradient>',
        f'<mask id="soft"><rect x="{px}" width="{W - px}" height="{H}" fill="url(#fade)"/></mask>',
        "</defs>",
        '<g clip-path="url(#card)">',
        f'<rect width="{W}" height="{H}" fill="{t.bg}"/>',
        f'<image x="{px}" width="{W - px}" height="{H}" mask="url(#soft)" '
        f'href="data:image/jpeg;base64,{photo(t, W - px, H)}"/>',
        "</g>",
    ]

    b.append(text(MONO, [("ABDELRAHMAN ABOUROUMIA (ROMIA)", t.muted)], 17, X, 72, tracking=0.12)[0])
    b.append(text(MONO_MEDIUM, [("romia.dev ↗", t.fg)], 17, W - X, 72, anchor="end")[0])

    size, track = 86, -0.03
    b.append(text(DISPLAY, [("Backend and ", t.fg), ("AI", t.accent)], size, X, 178, track)[0])
    line, end = text(DISPLAY, [("systems", t.accent), (" engineer.", t.fg)], size, X, 264, track)
    b.append(line)
    # The block cursor from the terminal on romia.dev: the card's only motion.
    cw, ch = 0.42 * size, 0.72 * size
    b.append(f'<rect class="cursor" x="{num(end + 0.08 * size)}" y="{num(264 - ch)}" '
             f'width="{num(cw)}" height="{num(ch)}" fill="{t.accent}">'
             '<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" dur="1.1s" '
             'repeatCount="indefinite"/></rect>')

    b.append(text(SANS, [("Software Engineer at Tutanic", t.fg), ("   ·   ", t.muted),
                         ("Co-founder of Zaylon AI", t.fg)], 23, X, 326)[0])
    b.append(medal(X - 1, 344, 20, t.accent))
    b.append(text(MONO_MEDIUM, [("BEST DEMONSTRATED IMPROVEMENT · MICRO1 FRONTIER ENGINEERING CHALLENGE 2026",
                                 t.accent)], 14.5, X + 28, 360, tracking=0.06)[0])

    b.append(f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="15.5" fill="none" stroke="{t.border}"/>')

    title = ("Abdelrahman Abouroumia (Romia). Backend and AI systems engineer. Software Engineer at Tutanic, "
             "co-founder of Zaylon AI. Best Demonstrated Improvement, micro1 Frontier Engineering Challenge 2026.")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
            f'role="img" aria-labelledby="title"><title id="title">{title}</title>'
            "<style>@media (prefers-reduced-motion: reduce){.cursor{display:none}}</style>"
            + "".join(b) + "</svg>\n")


def main() -> None:
    (ROOT / "assets").mkdir(exist_ok=True)
    for theme in (DARK, LIGHT):
        out = ROOT / "assets" / f"header-{theme.name}.svg"
        out.write_text(header(theme))
        print(f"{out.relative_to(ROOT)}  {out.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
