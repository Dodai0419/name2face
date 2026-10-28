"""Write the README images: docs/gallery.svg (24 names) and docs/palettes.svg (one name, 6 palettes)."""
import re
from pathlib import Path

import name2face as nf

DOCS = Path(__file__).parent / "docs"
NAMES = ["ada lovelace", "alan turing", "grace hopper", "linus", "margaret hamilton", "dennis ritchie",
         "katherine johnson", "guido", "barbara liskov", "ken thompson", "radia perlman", "tim berners-lee",
         "frances allen", "john carmack", "hedy lamarr", "donald knuth", "annie easley", "edsger dijkstra",
         "sophie wilson", "claude shannon", "karen sparck jones", "steve wozniak", "joan clarke", "you@example.com"]
PALETTES = [("#f2f1f4", "#7c6cf2"), ("#0b1830", "#18a6d3"), ("#fff4e0", "#ff7a59"),
            ("#e9f7ef", "#2e9e5b"), ("#fdf0f6", "#e0569b"), ("#1d1d22", "#f5c542")]


def grid(svgs, cols, cell=96, gap=12, labels=None):
    """Nest each 80x80 avatar SVG in one SVG sheet, with an optional caption under each."""
    rows = -(-len(svgs) // cols)
    lab = 18 if labels else 0
    w, h = cols * (cell + gap) + gap, rows * (cell + lab + gap) + gap
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">',
             f'<rect width="{w}" height="{h}" rx="16" fill="#fafafa"/>']
    for i, svg in enumerate(svgs):
        x, y = gap + i % cols * (cell + gap), gap + i // cols * (cell + lab + gap)
        parts.append(re.sub(r'<svg xmlns="[^"]+" viewBox="0 0 80 80" width="80" height="80"',
                            f'<svg x="{x}" y="{y}" viewBox="0 0 80 80" width="{cell}" height="{cell}"', svg, count=1))
        if labels:
            parts.append(f'<text x="{x + cell / 2}" y="{y + cell + 14}" font-family="system-ui,sans-serif" '
                         f'font-size="11" text-anchor="middle" fill="#444">{nf.escape_xml(labels[i])}</text>')
    return "".join(parts) + "</svg>"


def main():
    DOCS.mkdir(exist_ok=True)
    (DOCS / "gallery.svg").write_text(grid([nf.avatar(n) for n in NAMES], 6, labels=NAMES), encoding="utf-8")
    faces = [nf.avatar("ada lovelace", p, f) for p in PALETTES for f in ("circle",)]
    (DOCS / "palettes.svg").write_text(grid(faces, 6), encoding="utf-8")
    frames = [nf.avatar("grace hopper", PALETTES[1], f) for f in ("circle", "rounded", "square")]
    (DOCS / "frames.svg").write_text(grid(frames, 3, labels=["circle", "rounded", "square"]), encoding="utf-8")
    print(f"wrote docs/gallery.svg ({len(NAMES)} faces), docs/palettes.svg, docs/frames.svg")


if __name__ == "__main__":
    main()
