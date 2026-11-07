"""Draw assets/neofetch.svg: a terminal that runs `neofetch --off`, which
prints the facts without a logo.

Text is set as outlines from the fonts in tools/fonts. GitHub serves this
file with a policy that blocks web fonts, and outlines render the same
everywhere. The terminal is the one on romia.dev, dark in either theme.

    python3 tools/draw.py        (needs fontTools)
"""

from __future__ import annotations

from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent

BG, EDGE, RULE, DOT = "#0d0e11", "#26282d", "#1d1f23", "#2c2e33"
TEXT, DIM, ACCENT = "#e6e3dc", "#6f6c66", "#6b8aff"
# neofetch's colour blocks, in the palette of romia.dev.
SWATCHES = ["#2c2e33", "#4a4d55", "#8f8c85", "#e6e3dc", "#2f3b73", "#4a5cb3", "#6b8aff", "#b4c3ff"]

FACTS = [
    ("OS", "Backend and AI systems engineer"),
    ("Host", "Tutanic, Software Engineer"),
    ("Startup", "Zaylon AI, co-founder"),
    ("Kernel", "Python, TypeScript, Java, SQL"),
    ("Packages", "FastAPI, Django, LangGraph, CopilotKit, MCP"),
    ("Streams", "NATS JetStream, Kafka"),
    ("Data", "Postgres, PgBouncer, Dragonfly, Redis, S3"),
    ("Cloud", "AWS, Bedrock, Kubernetes, Helm"),
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


def neofetch() -> str:
    W, X, size, lead = 760, 36, 15.5, 25
    cw = MONO.width("0", size)
    b: list[str] = []

    # Title bar, as on romia.dev.
    b.append(f'<line x1="0" x2="{W}" y1="40" y2="40" stroke="{RULE}"/>')
    for i in range(3):
        b.append(f'<circle cx="{20 + i * 17}" cy="20" r="5" fill="{DOT}"/>')
    b.append(text([("romia@github: ~", "#8f8c85")], 13, 78, 24.5))

    # The command, typed: a cover slides off it one character at a time,
    # carrying the cursor.
    cmd, cmd_y, t0 = "neofetch --off", 84, 0.5
    cx = X + 2 * cw
    b.append(text([("$ ", ACCENT), (cmd, TEXT)], size, X, cmd_y))
    b.append(f'<g class="cover type"><rect x="{num(cx)}" y="{cmd_y - 18}" width="{num((len(cmd) + 1) * cw)}" '
             f'height="{lead}" fill="{BG}"/><rect class="caret" x="{num(cx)}" y="{num(cmd_y - 12.5)}" '
             f'width="{num(cw)}" height="16" fill="{TEXT}"/></g>')
    typed = t0 + len(cmd) * 0.075 + 0.2

    # The output: who, then the facts, then the colour blocks.
    y = cmd_y + 44
    info = [text([("romia", ACCENT), ("@", TEXT), ("github", ACCENT)], size, X, y),
            text([("-" * 12, DIM)], size, X, y + lead)]
    key_w = max(len(k) for k, _ in FACTS) + 2
    for i, (key, value) in enumerate(FACTS):
        line = f"{key}:".ljust(key_w)
        assert MONO.width(line + value, size) < W - 2 * X, value
        info.append(text([(line, ACCENT), (value, TEXT)], size, X, y + lead * (i + 2)))
    sy = y + lead * (len(FACTS) + 2) - 4
    for i, colour in enumerate(SWATCHES):
        info.append(f'<rect x="{num(X + i * 3 * cw)}" y="{sy}" width="{num(3 * cw)}" height="18" fill="{colour}"/>')
    b.append(f'<g class="out">{"".join(info)}</g>')

    # A fresh prompt, and a cursor that keeps blinking.
    py = sy + 18 + 44
    b.append(f'<g class="out end">{text([("$ ", ACCENT)], size, X, py)}<rect class="blink" x="{num(cx)}" '
             f'y="{num(py - 12.5)}" width="{num(cw)}" height="16" fill="{TEXT}"/></g>')
    H = round(py + 28)

    style = (
        ".cover{display:none}"
        "@media (prefers-reduced-motion:no-preference){"
        ".cover{display:inline}"
        f".type{{animation:type {len(cmd) * 0.075:.3f}s steps({len(cmd)},end) {t0}s both}}"
        f".caret{{animation:hide 1ms linear {typed:.2f}s both}}"
        f".out{{animation:show 1ms linear {typed:.2f}s both}}"
        f".end{{animation-delay:{typed + 0.4:.2f}s}}"
        ".blink{animation:blink 1.1s linear infinite}}"
        f"@keyframes type{{to{{transform:translateX({num(len(cmd) * cw)}px)}}}}"
        "@keyframes show{from{opacity:0}to{opacity:1}}"
        "@keyframes hide{from{opacity:1}to{opacity:0}}"
        "@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}"
    )
    title = ("A terminal runs neofetch --off for Romia (Abdelrahman Abouroumia): "
             + "; ".join(f"{k}: {v}" for k, v in FACTS) + ".")
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
