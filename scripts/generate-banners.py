#!/usr/bin/env python3
"""Generate the README banners with GitHub's system font stack.

Run: python3 scripts/generate-banners.py
The banner text stays as SVG text so it uses the same system fonts as GitHub's
README on each platform. Copy matches the four approved README versions.
"""

from argparse import ArgumentParser
from html import escape
from pathlib import Path


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


# GitHub Primer's system-font stack. SVG images do not inherit the page's CSS,
# so declare the same stack explicitly inside the image.
FONT_STACK = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji'"


def svg_text(text, x, baseline, size, color):
    return (f'<text x="{x}" y="{baseline}" font-size="{size}" '
            f'fill="{color}">{escape(text)}</text>')


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


def banner(lang, theme, mobile):
    data, colors = COPY[lang], PALETTES[theme]
    width, height = (400, 250) if mobile else (1000, 270)
    left = 24 if mobile else 42
    label = "Project Thirdminute" if lang == "en" else f'{data["projectName"]} (Thirdminute)'
    title = escape(f'{label} — {data["descriptor"]}')
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{title}" xml:lang="{lang}">',
        f'<title>{title}</title>',
        '<desc>A constellation of connected memories extends toward a warm golden point.</desc>',
        '<defs>',
        f'<linearGradient id="surface" x1="0" y1="0" x2="1" y2=".4"><stop offset="0" stop-color="{colors["start"]}"/><stop offset="1" stop-color="{colors["end"]}"/></linearGradient>',
        f'<radialGradient id="future-glow"><stop offset="0" stop-color="{colors["gold"]}" stop-opacity=".15"/><stop offset="1" stop-color="{colors["gold"]}" stop-opacity="0"/></radialGradient>',
        '</defs>',
        f'<rect x=".5" y=".5" width="{width-1}" height="{height-1}" rx="7" fill="url(#surface)" stroke="{colors["border"]}" stroke-opacity=".65"/>',
        constellation(colors, mobile),
    ]
    # Font selection follows the host just as the surrounding README does.
    # Fixed line breaks and conservative type sizes leave room for font metrics
    # to vary between macOS, Windows, Linux and mobile devices.
    parts.append(f'<g font-family="{FONT_STACK}" font-weight="400">')
    eyebrow = f'550W Lab  /  {data["projectLabel"]}'
    parts.append(svg_text(eyebrow, left, 40 if mobile else 51, 12 if mobile else 13, colors["muted"]))

    title_size = ({"en": 42, "de": 33, "zh-CN": 45, "ja": 45}[lang] if mobile
                  else {"en": 62, "de": 55, "zh-CN": 65, "ja": 65}[lang])
    parts.append(svg_text(data["projectName"], left, 105 if mobile else 131, title_size, colors["fg"]))

    descriptor_lines = (["Assoziatives, graphbasiertes", "Gedächtnis für KI."]
                        if mobile and lang == "de" else [data["descriptor"]])
    for index, line in enumerate(descriptor_lines):
        parts.append(svg_text(line, left, (143 if mobile else 174) + index * (20 if mobile else 23),
                              16 if mobile else 17, colors["fg"]))

    status_baseline = 217 if mobile else 229
    dot_y = status_baseline - 4.4
    parts.append(f'<circle cx="{left+2.7}" cy="{dot_y}" r="2.7" fill="{colors["gold"]}"/>')
    parts.append(svg_text(f'02:38 · {data["developmentLabel"]}', left+14, status_baseline, 13.5 if mobile else 13, colors["muted"]))
    parts.append("</g>")
    parts.append("</svg>")
    return "".join(parts)


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parents[1] / "assets")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for lang in COPY:
        for theme in PALETTES:
            for mobile in [False, True]:
                suffix = f'mobile-{theme}' if mobile else theme
                path = args.output_dir / f'hero-{lang}-{suffix}.svg'
                path.write_text(banner(lang, theme, mobile), encoding="utf-8")
                print(path.name)


if __name__ == "__main__":
    main()
