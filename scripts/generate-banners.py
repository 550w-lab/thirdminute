#!/usr/bin/env python3
"""Generate the README banners using Noto Sans CJK outlines.

Requires Python 3 and fontTools. Supply a directory containing the unmodified
NotoSansCJKsc-Regular.otf and NotoSansCJKjp-Regular.otf font files:

    python scripts/generate-banners.py --font-dir /path/to/noto-fonts

The font files are not bundled. Their licence is preserved in assets/OFL-Noto.txt.
Banner text below matches the four approved README language versions.
"""

from argparse import ArgumentParser
from html import escape
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont


COPY = {
    "en": {
        "projectLabel": "Project",
        "projectName": "Thirdminute",
        "descriptor": "Associative graph memory for AI.",
        "developmentLabel": "In development",
    },
    "zh-CN": {
        "projectLabel": "Project Thirdminute",
        "projectName": "第三分钟",
        "descriptor": "基于图的 AI 联想记忆。",
        "developmentLabel": "开发中",
    },
    "de": {
        "projectLabel": "Project Thirdminute",
        "projectName": "Die dritte Minute",
        "descriptor": "Assoziatives, graphbasiertes Gedächtnis für KI.",
        "developmentLabel": "In Entwicklung",
    },
    "ja": {
        "projectLabel": "Project Thirdminute",
        "projectName": "3分目",
        "descriptor": "AIのためのグラフ型連想メモリ。",
        "developmentLabel": "開発中",
    },
}

PALETTES = {
    "dark": {
        "start": "#0f141b",
        "end": "#131d29",
        "border": "#263342",
        "fg": "#edf2f7",
        "muted": "#a3afbd",
        "graph": "#8aa3bd",
        "gold": "#d4b58c",
    },
    "light": {
        "start": "#fbfcfe",
        "end": "#edf3f8",
        "border": "#dce5ed",
        "fg": "#202b38",
        "muted": "#596878",
        "graph": "#67859f",
        "gold": "#986a34",
    },
}


def text_width(text, size, font, tracking=0):
    cmap = font.getBestCmap()
    widths = font["hmtx"].metrics
    units = font["head"].unitsPerEm
    return sum(widths[cmap[ord(char)]][0] for char in text) * size / units + max(0, len(text) - 1) * tracking


def outlined_text(text, x, baseline, size, font, color, tracking=0, title=False):
    cmap = font.getBestCmap()
    glyphs = font.getGlyphSet()
    scale = size / font["head"].unitsPerEm
    parts = []
    for char in text:
        name = cmap[ord(char)]
        pen = SVGPathPen(glyphs)
        glyphs[name].draw(pen)
        path = pen.getCommands()
        if path:
            weight = f' stroke="{color}" stroke-width="5" stroke-linejoin="round" paint-order="stroke fill"' if title else ""
            parts.append(
                f'<path fill="{color}"{weight} transform="translate({x:.3f} {baseline:.3f}) '
                f'scale({scale:.6f} {-scale:.6f})" d="{path}"/>'
            )
        x += font["hmtx"].metrics[name][0] * scale + tracking
    return "".join(parts)


def wrap_text(text, size, font, max_width):
    tokens = text.split(" ") if " " in text else list(text)
    separator = " " if " " in text else ""
    lines, current = [], ""
    for token in tokens:
        trial = current + separator + token if current else token
        if current and text_width(trial, size, font) > max_width:
            lines.append(current)
            current = token
        else:
            current = trial
    if current:
        lines.append(current)
    return lines


def constellation(palette, mobile):
    points = [
        (0, 122), (33, 66), (75, 141), (92, 26), (138, 91),
        (179, 159), (210, 15), (232, 107), (281, 64), (327, 0),
    ]
    edges = [(0, 1), (0, 2), (1, 3), (1, 4), (2, 4), (2, 5),
             (3, 6), (4, 7), (5, 7), (6, 8), (7, 8), (8, 9)]
    graph = palette["graph"]
    gold = palette["gold"]
    transform = "translate(246 169) scale(.4)" if mobile else "translate(623 53)"
    opacity = ".58" if mobile else "1"
    parts = [f'<g transform="{transform}" opacity="{opacity}">']
    for index, (a, b) in enumerate(edges):
        ax, ay = points[a]
        bx, by = points[b]
        color = gold if index == len(edges) - 1 else graph
        parts.append(f'<line x1="{ax}" y1="{ay}" x2="{bx}" y2="{by}" stroke="{color}" stroke-width="1" opacity=".34"/>')
    for x, y, radius in [(20, 8, 1.05), (124, 182, .9), (289, 163, 1.2)]:
        parts.append(f'<circle cx="{x}" cy="{y}" r="{radius}" fill="{graph}" opacity=".24"/>')
    radii = [2.0, 2.9, 2.0, 2.3, 3.4, 2.1, 2.5, 2.6, 3.0, 4.1]
    for index, ((x, y), radius) in enumerate(zip(points, radii)):
        if index == len(points) - 1:
            parts.append(f'<circle cx="{x}" cy="{y}" r="19" fill="url(#future-glow)"/>')
            parts.append(f'<circle cx="{x}" cy="{y}" r="{radius}" fill="{gold}"/>')
        else:
            parts.append(f'<circle cx="{x}" cy="{y}" r="{radius}" fill="{graph}" opacity=".76"/>')
    parts.append("</g>")
    return "".join(parts)


def banner(lang, theme, mobile, fonts):
    data, colors = COPY[lang], PALETTES[theme]
    font = fonts["ja" if lang == "ja" else "zh-CN"]
    width, height = (400, 250) if mobile else (1000, 270)
    left = 24 if mobile else 42
    label = "Project Thirdminute" if lang == "en" else f'{data["projectName"]} (Thirdminute)'
    title = escape(f'{label} — {data["descriptor"]}')
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{title}">',
        f'<title>{title}</title>',
        '<desc>A constellation of connected memories extends toward a warm golden point.</desc>',
        '<defs>',
        f'<linearGradient id="surface" x1="0" y1="0" x2="1" y2=".4"><stop offset="0" stop-color="{colors["start"]}"/><stop offset="1" stop-color="{colors["end"]}"/></linearGradient>',
        f'<radialGradient id="future-glow"><stop offset="0" stop-color="{colors["gold"]}" stop-opacity=".15"/><stop offset="1" stop-color="{colors["gold"]}" stop-opacity="0"/></radialGradient>',
        '</defs>',
        f'<rect x=".5" y=".5" width="{width-1}" height="{height-1}" rx="7" fill="url(#surface)" stroke="{colors["border"]}" stroke-opacity=".65"/>',
        constellation(colors, mobile),
    ]
    eyebrow = f'550W Lab  /  {data["projectLabel"]}'
    parts.append(outlined_text(eyebrow, left, 40 if mobile else 51, 12 if mobile else 13, font, colors["muted"], tracking=.08))

    title_size = (47 if lang in ("zh-CN", "ja") else 44) if mobile else (65 if lang in ("zh-CN", "ja") else 62)
    title_tracking = -.75 if lang in ("en", "de") else -.4
    max_title_width = 352 if mobile else 555
    while text_width(data["projectName"], title_size, font, title_tracking) > max_title_width:
        title_size -= .25
    parts.append(outlined_text(data["projectName"], left, 105 if mobile else 131, title_size, font, colors["fg"], tracking=title_tracking, title=True))

    descriptor_size = 16 if mobile else 17
    descriptor_lines = wrap_text(data["descriptor"], descriptor_size, font, 352 if mobile else 550)
    for index, line in enumerate(descriptor_lines):
        parts.append(outlined_text(line, left, (143 if mobile else 174) + index * (20 if mobile else 23), descriptor_size, font, colors["fg"]))

    status_baseline = 217 if mobile else 229
    dot_y = status_baseline - 4.4
    parts.append(f'<circle cx="{left+2.7}" cy="{dot_y}" r="2.7" fill="{colors["gold"]}"/>')
    parts.append(outlined_text(f'02:38 · {data["developmentLabel"]}', left+14, status_baseline, 13.5 if mobile else 13, font, colors["muted"]))
    parts.append("</svg>")
    return "".join(parts)


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--font-dir", "--fonts-dir", dest="font_dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parents[1] / "assets")
    args = parser.parse_args()
    fonts = {
        "zh-CN": TTFont(args.font_dir / "NotoSansCJKsc-Regular.otf"),
        "ja": TTFont(args.font_dir / "NotoSansCJKjp-Regular.otf"),
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for lang in COPY:
        for theme in PALETTES:
            for mobile in [False, True]:
                suffix = f'mobile-{theme}' if mobile else theme
                path = args.output_dir / f'hero-{lang}-{suffix}.svg'
                path.write_text(banner(lang, theme, mobile, fonts), encoding="utf-8")
                print(path.name)


if __name__ == "__main__":
    main()
