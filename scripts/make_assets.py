#!/usr/bin/env python3
"""Generate the profile README art: assets/header.svg (pixel avatar banner) and assets/rover.gif.

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


# ----------------------------------------------------------------- rover.gif
ROVER = """
.......##.......
......####......
.......##.......
.......##.......
..############..
..#..........#..
..#.##.##.##.#..
..#..........#..
..############..
.####......####.
#....#....#....#
#.##.#....#.##.#
#....#....#....#
.####......####.
"""
TAG = """
##########
#........#
#.##..##.#
#.#..#...#
#...##.#.#
#.#.#..#.#
#..#.##..#
#.##...#.#
#........#
##########
"""


def rover_gif():
    S, N = 260, 36
    hexrgb = lambda h: tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))
    bg, fg, acc, dim, ok = hexrgb(BG), hexrgb(FG), hexrgb(ACCENT), (48, 54, 61), hexrgb(OPEN)
    rover = [r for r in ROVER.strip("\n").split("\n")]
    tag = [r for r in TAG.strip("\n").split("\n")]
    RP, TP = 4, 5                                   # pixel sizes
    ground = 196
    tag_x, tag_y = S - 26 - len(tag[0]) * TP, ground - 18 - len(tag) * TP
    rw, rh = len(rover[0]) * RP, len(rover) * RP
    dock_x = tag_x - rw - 14
    frames = []
    for f in range(N):
        im = Image.new("RGB", (S, S), bg)
        d = ImageDraw.Draw(im)
        for y in range(0, S, 7):                    # faint dot grid
            for x in range(0, S, 7):
                if (x * 3 + y) % 21 == 0:
                    d.point((x, y), fill=(28, 36, 52))
        for x in range(10, S - 10, 8):              # dashed ground
            d.line([(x, ground), (x + 4, ground)], fill=dim, width=2)
        # dock post + AprilTag
        d.rectangle([tag_x + len(tag[0]) * TP // 2 - 2, tag_y + len(tag) * TP, tag_x + len(tag[0]) * TP // 2 + 2, ground], fill=dim)
        for y, row in enumerate(tag):
            for x, c in enumerate(row):
                d.rectangle([tag_x + x * TP, tag_y + y * TP, tag_x + x * TP + TP - 1, tag_y + y * TP + TP - 1],
                            fill=fg if c == "#" else (22, 27, 34))
        # rover position: drive in over 22 frames (ease-out), then sit docked
        drive = min(f / 22, 1.0)
        ease = 1 - (1 - drive) ** 3
        rx = int(14 + (dock_x - 14) * ease)
        ry = ground - rh - 2 + (1 if (f % 4 < 2 and drive < 1) else 0)   # little bounce while moving
        docked = drive >= 1
        # camera beam from mast to tag while approaching
        cam = (rx + rw // 2 + 4, ry + 4)
        tcx, tcy = tag_x + len(tag[0]) * TP // 2, tag_y + len(tag) * TP // 2
        if not docked and f % 3 != 2:
            for k in range(0, 100, 7):
                t = k / 100
                px_, py_ = cam[0] + (tcx - cam[0]) * t, cam[1] + (tcy - cam[1]) * t
                d.point((px_, py_), fill=acc)
        # detection box: appears once close enough, turns green when docked
        if ease > 0.45:
            col = ok if docked else acc
            pad = 4 + (0 if docked else (f % 2) * 2)
            x0, y0 = tag_x - pad, tag_y - pad
            x1, y1 = tag_x + len(tag[0]) * TP + pad - 1, tag_y + len(tag) * TP + pad - 1
            L = 10
            for (cx, cy, dx, dy) in [(x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)]:
                d.line([(cx, cy), (cx + dx * L, cy)], fill=col, width=2)
                d.line([(cx, cy), (cx, cy + dy * L)], fill=col, width=2)
        # rover
        for y, row in enumerate(rover):
            for x, c in enumerate(row):
                if c == "#":
                    d.rectangle([rx + x * RP, ry + y * RP, rx + x * RP + RP - 1, ry + y * RP + RP - 1], fill=fg)
        d.rectangle([rx + 7 * RP, ry, rx + 9 * RP - 1, ry + RP - 1], fill=acc)   # camera lens
        # status text
        msg = "docked" if docked else ("tag 0 locked" if ease > 0.45 else "searching...")
        d.text((14, 22), "$ rover --dock", fill=acc)
        d.text((14, 40), msg, fill=ok if docked else hexrgb(DIM))
        frames.append(im.convert("P", palette=Image.ADAPTIVE, colors=16))
    frames[0].save(OUT / "rover.gif", save_all=True, append_images=frames[1:],
                   duration=[90] * 22 + [140] * (N - 22), loop=0, optimize=True, disposal=2)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    (OUT / "header.svg").write_text(header_svg())
    rover_gif()
    print("assets/header.svg, assets/rover.gif written")
