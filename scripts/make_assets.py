#!/usr/bin/env python3
"""Generate the profile README art: assets/header.svg, assets/avatar.gif, assets/open-source.svg.

Run:  python3 scripts/make_assets.py      (needs Pillow for the GIF: pip install pillow)
Everything is drawn from code, so nothing depends on third-party card services.
"""
from html import escape
from pathlib import Path

from PIL import Image, ImageDraw

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


# ----------------------------------------------------------- open-source.svg
def open_source_svg():
    rows = [("microsoft/markitdown", "190K+"), ("learning-unlimited/ESP-Website", "220+")]
    W, top, rh = 1000, 30, 64
    H = top + rh * len(rows) + 14
    body = []
    for i, (repo, stars) in enumerate(rows):
        y = top + i * rh
        body.append(f'''
  <rect x="24" y="{y}" width="{W - 48}" height="{rh - 14}" rx="8" fill="{PANEL}" stroke="{FAINT}"/>
  <circle cx="50" cy="{y + 25}" r="5" fill="{MERGED}"/><circle cx="50" cy="{y + 25}" r="5" fill="{MERGED}" opacity="0.6">
    <animate attributeName="r" values="5;9;5" dur="2.4s" begin="{i * 1.2}s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="0.6;0;0.6" dur="2.4s" begin="{i * 1.2}s" repeatCount="indefinite"/></circle>
  <text x="72" y="{y + 31}" fill="{FG}" font-size="18" font-weight="700">{escape(repo)}</text>
  <text x="{W - 50}" y="{y + 31}" fill="{ACCENT}" font-size="17" text-anchor="end">&#9733; {stars}</text>''')
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{MONO}">
  <title>Open source: contributor to microsoft/markitdown and learning-unlimited/ESP-Website</title>
  <rect width="{W}" height="{H}" rx="14" fill="{BG}"/>
  <rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="14" fill="none" stroke="{FAINT}"/>{"".join(body)}
</svg>
'''


# ---------------------------------------------------------------- avatar.gif
def avatar_gif():
    S, PX, N = 240, 6, 24          # canvas, pixel size, frames
    grid = avatar_grid()
    ox, oy = (S - 32 * PX) // 2, 20
    hexrgb = lambda h: tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))
    bg, fg, acc = hexrgb(BG), hexrgb(FG), hexrgb(ACCENT)
    bits = [(ox + 2 * PX, 0.0), (ox + 30 * PX, 0.35), (ox + 1 * PX, 0.6), (ox + 31 * PX, 0.85)]
    frames = []
    for f in range(N):
        im = Image.new("RGB", (S, S), bg)
        d = ImageDraw.Draw(im)
        for y in range(0, S, 6):                          # faint dot grid
            for x in range(0, S, 6):
                if (x + y) % 12 == 0:
                    d.point((x, y), fill=(28, 36, 52))
        glint = int((f / N) * 60) - 10                    # column of the visor glint
        for y, row in enumerate(grid):
            for x, on in enumerate(row):
                if not on:
                    continue
                col = fg
                if y in VISOR_ROWS and abs(x - glint) <= 1:
                    col = acc if abs(x - glint) == 1 else (255, 255, 255)
                d.rectangle([ox + x * PX, oy + y * PX, ox + x * PX + PX - 1, oy + y * PX + PX - 1], fill=col)
        for bx, phase in bits:                            # data bits rising from the headphones
            p = (f / N + phase) % 1
            by = oy + 15 * PX - int(p * 110)
            if p < 0.85:
                shade = tuple(int(c * (1 - p)) + int(b * p) for c, b in zip(acc, bg))
                d.rectangle([bx, by, bx + PX - 2, by + PX - 2], fill=shade)
        d.rectangle([ox, oy + 32 * PX + 6, ox + 32 * PX, oy + 32 * PX + 8], fill=acc)   # underline
        frames.append(im.convert("P", palette=Image.ADAPTIVE, colors=16))
    frames[0].save(OUT / "avatar.gif", save_all=True, append_images=frames[1:], duration=90, loop=0,
                   optimize=True, disposal=2)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    (OUT / "header.svg").write_text(header_svg())
    (OUT / "open-source.svg").write_text(open_source_svg())
    avatar_gif()
    print("assets/header.svg, assets/open-source.svg, assets/avatar.gif written")
