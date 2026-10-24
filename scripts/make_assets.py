#!/usr/bin/env python3
"""Generate the profile README art: assets/header.svg (pixel avatar banner).

Run:  python3 scripts/make_assets.py      
Everything is drawn from code, so nothing depends on third-party card services.
"""
from html import escape
from pathlib import Path


OUT = Path(__file__).resolve().parent.parent / "assets"

# palette (GitHub dark)
BG, PANEL, FG, DIM, FAINT = "#0d1117", "#161b22", "#e6edf3", "#8b949e", "#21262d"
ACCENT, MERGED, OPEN = "#7aa2f7", "#a371f7", "#3fb950"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"

# Same pixel boy as the website avatar: left half, mirrored.  '#' ink, ':' 50% dither.
AVATAR_LEFT = """
................
................
...........#####
.........#######
........########
.......#########
......##########
......###.#.##.#
.....###........
.....##.........
....####........
...###..........
..####..........
..#::#.#########
..#::#.#..######
..#::#.#.#######
..#::#..#######.
..####..........
...##...........
.....#..........
......#.........
......#.........
.......#.....###
........##......
..........###...
............####
..........####::
......#####::::#
....##::::::::::
...#::::::::::::
..#:::::::::::::
..##############
"""


def avatar_grid():
    left = [r.ljust(16, ".")[:16] for r in AVATAR_LEFT.strip("\n").split("\n")]
    g = [r + r[::-1] for r in left]
    g[19] = g[19][:15] + "##" + g[19][17:]  # nose
    return [[c == "#" or (c == ":" and (x + y) % 2 == 0) for x, c in enumerate(row)] for y, row in enumerate(g)]


VISOR_ROWS = range(13, 17)  # rows of the shades, used for the glint


# ---------------------------------------------------------------- header.svg
def header_svg():
    W, H, PX = 1000, 330, 7
    ax, ay = 52, 52
    grid = avatar_grid()
    px = "".join(f'<rect x="{ax + x * PX}" y="{ay + y * PX}" width="{PX}" height="{PX}"/>'
                 for y, row in enumerate(grid) for x, on in enumerate(row) if on)
    visor = "".join(f'<rect x="{ax + x * PX}" y="{ay + y * PX}" width="{PX}" height="{PX}"/>'
                    for y in VISOR_ROWS for x, on in enumerate(grid[y]) if on)

    # terminal lines: (text, colour, size, bold)
    lines = [
        ("$ whoami", ACCENT, 18, False),
        ("nithin jambula", FG, 34, True),
        ("$ cat role.txt", ACCENT, 18, False),
        ("robotics software engineer / VIT-AP / India", FG, 20, False),
        ("$ ls ~/explores", ACCENT, 18, False),
        ("robots/  system-architecture/  ai-agents/  open-source/", DIM, 18, False),
    ]
    tx, ty = 330, 64
    out, clips, t = [], [], 0.4
    y = ty
    for i, (text, col, size, bold) in enumerate(lines):
        y += size + (14 if i else 0)
        cw = size * 0.6
        width = int(len(text) * cw * 1.08) + 12
        dur = max(0.4, len(text) * 0.045)
        # step the clip width one character at a time (SMIL, works inside <img> on GitHub)
        steps = len(text)
        vals = ";".join(str(int(width * k / steps)) for k in range(steps + 1))
        keys = ";".join(f"{k / steps:.4f}" for k in range(steps + 1))
        clips.append(f'<clipPath id="c{i}"><rect x="{tx}" y="{y - size}" height="{size + 8}" width="0">'
                     f'<animate attributeName="width" values="{vals}" keyTimes="{keys}" calcMode="discrete" '
                     f'begin="{t:.2f}s" dur="{dur:.2f}s" fill="freeze"/></rect></clipPath>')
        weight = ' font-weight="700"' if bold else ""
        out.append(f'<text x="{tx}" y="{y}" fill="{col}" font-size="{size}"{weight} clip-path="url(#c{i})">'
                   f"{escape(text)}</text>")
        t += dur + (0.35 if text.startswith("$") else 0.6)
    y += 36
    cursor = (f'<text x="{tx}" y="{y}" fill="{ACCENT}" font-size="18" opacity="0">$ '
              f'<animate attributeName="opacity" values="0;1" begin="{t:.2f}s" dur="0.01s" fill="freeze"/></text>'
              f'<rect x="{tx + 24}" y="{y - 15}" width="11" height="19" fill="{FG}" opacity="0">'
              f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" dur="1s" begin="{t:.2f}s" '
              f'repeatCount="indefinite"/></rect>')

    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{MONO}">
  <title>Nithin Jambula: robotics software engineer</title>
  <defs>
    <pattern id="dots" width="6" height="6" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r="1" fill="{ACCENT}" opacity="0.18"/></pattern>
    <linearGradient id="fade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff"/><stop offset="0.45" stop-color="#fff" stop-opacity="0"/></linearGradient>
    <mask id="fadeMask"><rect width="{W}" height="{H}" fill="url(#fade)"/></mask>
    <linearGradient id="glint" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{ACCENT}" stop-opacity="0"/><stop offset="0.5" stop-color="#ffffff" stop-opacity="0.9"/><stop offset="1" stop-color="{ACCENT}" stop-opacity="0"/></linearGradient>
    <clipPath id="visor">{visor}</clipPath>
    {"".join(clips)}
  </defs>
  <rect width="{W}" height="{H}" rx="14" fill="{BG}"/>
  <rect width="{W}" height="{H}" rx="14" fill="url(#dots)" mask="url(#fadeMask)"/>
  <rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="14" fill="none" stroke="{FAINT}"/>
  <g fill="{FG}">{px}</g>
  <g clip-path="url(#visor)"><rect x="{ax - 80}" y="{ay}" width="60" height="{32 * PX}" fill="url(#glint)" transform="skewX(-20)">
    <animate attributeName="x" values="{ax - 80};{ax + 32 * PX + 80};{ax + 32 * PX + 80}" keyTimes="0;0.35;1" dur="4s" repeatCount="indefinite"/></rect></g>
  <rect x="{ax - 6}" y="{ay + 32 * PX + 6}" width="{32 * PX + 12}" height="3" fill="{ACCENT}" opacity="0.5"/>
  <line x1="300" y1="40" x2="300" y2="{H - 40}" stroke="{FAINT}"/>
  {"".join(out)}
  {cursor}
  <rect x="0" y="0" width="{W}" height="2" fill="{ACCENT}" opacity="0.06">
    <animate attributeName="y" values="0;{H}" dur="6s" repeatCount="indefinite"/></rect>
</svg>
'''


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    (OUT / "header.svg").write_text(header_svg())
    print("assets/header.svg written")
