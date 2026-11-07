"""Draw assets/neofetch.svg: a terminal that runs `neofetch`, with a dotted
R where neofetch would print its logo, and the facts beside it.

Text is set as outlines from the fonts in tools/fonts. GitHub serves this
file with a policy that blocks web fonts, and outlines render the same
everywhere. The terminal is the one on romia.dev, dark in either theme.

    python3 tools/draw.py        (needs fontTools)
"""

from __future__ import annotations

from pathlib import Path

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.pointInsidePen import PointInsidePen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent

BG, EDGE, RULE, DOT = "#0d0e11", "#26282d", "#1d1f23", "#2c2e33"
TEXT, DIM, ACCENT = "#e6e3dc", "#6f6c66", "#6b8aff"
# The logo's four tones, darkest to brightest, all from the accent.
TONES = ["#2f3b73", "#4a5cb3", "#6b8aff", "#b4c3ff"]
SWATCHES = ["#2c2e33", "#4a4d55", "#8f8c85", "#e6e3dc", *TONES]

FACTS = [
    ("OS", "Backend and AI systems engineer"),
    ("Host", "Tutanic, Software Engineer"),
    ("Startup", "Zaylon AI, co-founder"),
    ("Kernel", "Python, TypeScript, Java, SQL"),
    ("Packages", "FastAPI, Django, LangGraph, CopilotKit, MCP"),
    ("Streams", "NATS JetStream, Kafka"),
    ("Data", "Postgres, PgBouncer, Dragonfly, Redis, S3"),
    ("Cloud", "AWS, Bedrock, Kubernetes, Helm"),
    ("Locale", "en, ar-EG, de, es"),
    ("Won", "micro1 Best Demonstrated Improvement, advisorydrift"),
    ("Contact", "romia.dev"),
]


def num(v: float) -> str:
    s = f"{v:.1f}"
    return s[:-2] if s.endswith(".0") else s


class Mono:
    """JetBrains Mono, set as SVG path data. Monospaced, so no kerning."""

    def __init__(self, file: str):
        font = TTFont(ROOT / "tools" / "fonts" / file)
        self.glyphs = font.getGlyphSet()
        self.cmap = font.getBestCmap()
        self.upm = font["head"].unitsPerEm
        self.advance = font["hmtx"][self.cmap[ord("0")]][0] / self.upm  # every glyph is this wide, in ems

    def width(self, s: str, size: float) -> float:
        return len(s) * self.advance * size

    def path(self, s: str, size: float, x: float, y: float) -> str:
        scale = size / self.upm
        pen = SVGPathPen(self.glyphs, ntos=num)
        for i, ch in enumerate(s):
            if ch != " ":
                pos = (scale, 0, 0, -scale, x + i * self.advance * size, y)
                self.glyphs[self.cmap.get(ord(ch), ".notdef")].draw(TransformPen(pen, pos))
        return pen.getCommands()


MONO = Mono("jetbrains-mono-400.woff")


def text(parts: list[tuple[str, str]], size: float, x: float, y: float) -> str:
    """Coloured runs on one baseline."""
    out = []
    for s, fill in parts:
        if s.strip():
            out.append(f'<path fill="{fill}" d="{MONO.path(s, size, x, y)}"/>')
        x += MONO.width(s, size)
    return "".join(out)


def logo(x0: float, y0: float, height: float, cell: float) -> tuple[str, float]:
    """An R in the poster face of romia.dev, printed as dots: a dot wherever a
    grid point falls inside the letter, brightest at the top. Returns the
    markup and its width."""
    font = TTFont(ROOT / "tools" / "fonts" / "archivo-125-900.woff")
    glyphs = font.getGlyphSet()
    glyph = glyphs[font.getBestCmap()[ord("R")]]
    bounds = BoundsPen(glyphs)
    glyph.draw(bounds)
    left, bottom, right, top = bounds.bounds
    rows = round(height / cell)
    unit = (top - bottom) / rows  # font units per grid step
    cols = round((right - left) / unit)
    groups: list[list[str]] = [[] for _ in TONES]
    for y in range(rows):
        for x in range(cols):
            probe = PointInsidePen(glyphs, (left + (x + 0.5) * unit, top - (y + 0.5) * unit))
            glyph.draw(probe)
            if not probe.getResult():
                continue
            t = 1 - 0.7 * y / rows
            groups[min(3, int(t * 4))].append(
                f'<circle cx="{num(x0 + (x + 0.5) * cell)}" cy="{num(y0 + (y + 0.5) * cell)}" '
                f'r="{num(cell * 0.5 * (0.35 + 0.6 * t))}"/>')
    markup = "".join(f'<g fill="{tone}">{"".join(dots)}</g>' for tone, dots in zip(TONES, groups))
    return markup, cols * cell


def neofetch() -> str:
    W, X, size, lead = 1080, 36, 15.5, 25
    cw = MONO.width("0", size)
    b: list[str] = []

    # Title bar, as on romia.dev.
    b.append(f'<line x1="0" x2="{W}" y1="40" y2="40" stroke="{RULE}"/>')
    for i in range(3):
        b.append(f'<circle cx="{20 + i * 17}" cy="20" r="5" fill="{DOT}"/>')
    b.append(text([("romia@github: ~", "#8f8c85")], 13, 78, 24.5))

    # The command, typed: a cover slides off it one character at a time,
    # carrying the cursor.
    cmd, cmd_y, t0 = "neofetch", 84, 0.5
    cx = X + 2 * cw
    b.append(text([("$ ", ACCENT), (cmd, TEXT)], size, X, cmd_y))
    b.append(f'<g class="cover type"><rect x="{num(cx)}" y="{cmd_y - 18}" width="{num((len(cmd) + 1) * cw)}" '
             f'height="{lead}" fill="{BG}"/><rect class="caret" x="{num(cx)}" y="{num(cmd_y - 12.5)}" '
             f'width="{num(cw)}" height="16" fill="{TEXT}"/></g>')
    typed = t0 + len(cmd) * 0.075 + 0.2

    # The output: the logo on the left, printed top to bottom, the facts
    # beside it.
    top, block = 116, 360  # the facts run about this tall
    tall, cell = 256, 6.4
    ly = top + (block - tall) / 2 - 12  # the logo, centred on the facts
    dots, wide = logo(X + 16, ly, tall, cell)
    b.append(dots)
    b.append(f'<rect class="cover print" x="{X + 12}" y="{num(ly - 4)}" width="{num(wide + 8)}" '
             f'height="{num(tall + 8)}" fill="{BG}"/>')

    ix = X + 16 + wide + 56
    info = [text([("romia", ACCENT), ("@", TEXT), ("github", ACCENT)], size, ix, top + 16),
            text([("-" * 12, DIM)], size, ix, top + 16 + lead)]
    key_w = max(len(k) for k, _ in FACTS) + 2
    for i, (key, value) in enumerate(FACTS):
        line = f"{key}:".ljust(key_w)
        assert MONO.width(line + value, size) < W - ix - X, value
        info.append(text([(line, ACCENT), (value, TEXT)], size, ix, top + 16 + lead * (i + 2)))
    sy = top + 16 + lead * (len(FACTS) + 2) - 4
    for i, colour in enumerate(SWATCHES):
        info.append(f'<rect x="{num(ix + i * 3 * cw)}" y="{sy}" width="{num(3 * cw)}" height="18" fill="{colour}"/>')
    b.append(f'<g class="out">{"".join(info)}</g>')

    # A fresh prompt, and a cursor that keeps blinking.
    py = top + block + 44
    b.append(f'<g class="out end">{text([("$ ", ACCENT)], size, X, py)}<rect class="blink" x="{num(cx)}" '
             f'y="{num(py - 12.5)}" width="{num(cw)}" height="16" fill="{TEXT}"/></g>')
    H = round(py + 28)

    reveal = 0.6
    style = (
        ".cover{display:none}"
        "@media (prefers-reduced-motion:no-preference){"
        ".cover{display:inline}"
        f".type{{animation:type {len(cmd) * 0.075:.3f}s steps({len(cmd)},end) {t0}s both}}"
        f".caret{{animation:hide 1ms linear {typed:.2f}s both}}"
        f".out{{animation:show 1ms linear {typed:.2f}s both}}"
        f".end{{animation-delay:{typed + reveal + 0.2:.2f}s}}"
        f".print{{animation:print {reveal}s steps(24,end) {typed:.2f}s both,hide 1ms linear {typed + reveal:.2f}s forwards}}"
        ".blink{animation:blink 1.1s linear infinite}}"
        f"@keyframes type{{to{{transform:translateX({num(len(cmd) * cw)}px)}}}}"
        f"@keyframes print{{to{{transform:translateY({num(tall + 8)}px)}}}}"
        "@keyframes show{from{opacity:0}to{opacity:1}}"
        "@keyframes hide{from{opacity:1}to{opacity:0}}"
        "@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}"
    )
    title = ("A terminal runs neofetch for Romia (Abdelrahman Abouroumia): a dotted R as the logo, "
             "and beside it: " + "; ".join(f"{k}: {v}" for k, v in FACTS) + ".")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
            f'role="img" aria-labelledby="title"><title id="title">{title}</title><style>{style}</style>'
            f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="14" fill="{BG}" stroke="{EDGE}"/>'
            + "".join(b) + "</svg>\n")


def main() -> None:
    out = ROOT / "assets" / "neofetch.svg"
    out.parent.mkdir(exist_ok=True)
    out.write_text(neofetch())
    print(f"{out.relative_to(ROOT)}  {out.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
