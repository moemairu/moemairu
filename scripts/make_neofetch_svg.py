"""
Build a unified neofetch-style SVG containing both the ASCII portrait and the info card.
Colored key/value rows for work experience, tech stack, and highlights --
adapted for Isma'il Faruqy (moemairu): Cyber Security / Systems Programming.

Lines fade/slide in on a short stagger so it feels like the panel is printing
alongside the portrait. STATIC=1 emits the frozen state for previews.
"""
from PIL import Image, ImageEnhance, ImageFilter
import html
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "source-prepped.png")
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "..", "neofetch.svg")
STATIC = bool(os.environ.get("STATIC"))

# ---- Layout Config ----
COLS = 100
ROWS = 48
CELL_W = 8
CELL_H = 15

ART_W = COLS * CELL_W
ART_H = ROWS * CELL_H
PAD = 20
TITLEBAR_H = 30
STATUS_H = 30
INFO_W = 460

CANVAS_W = PAD + ART_W + 40 + INFO_W + PAD
CANVAS_H = TITLEBAR_H + ART_H + STATUS_H + PAD

INFO_X = PAD + ART_W + 40

# ---- ASCII Config ----
RAMP = " .`:-=+*cs#%@"
CONTRAST = 1.05
BRIGHTNESS = 1.0
GAMMA = 1.18
SHARPEN = False
WHITE_FLOOR = 0.80

# ---- Colors ----
FRAME = "#30363d"
TITLE_TEXT = "#7d8590"
INK = "#c9d1d9"
CURSOR = "#c9d1d9"

KEY = "#ffa657"      # orange keys
SECTION = "#58a6ff"  # blue section headers
GREEN = "#3fb950"
ACCENT = "#22d3ee"

# ---- Timing Config ----
ROW_DUR = 0.11
STAGGER = 0.11

# ---- 1. Sample the image ----------------
im_raw = Image.open(SRC)

# Handle transparency: paste onto a white background so transparent parts become spaces
if im_raw.mode in ('RGBA', 'LA') or (im_raw.mode == 'P' and 'transparency' in im_raw.info):
    im_raw = im_raw.convert("RGBA")
    white_bg = Image.new("RGBA", im_raw.size, (255, 255, 255, 255))
    im_raw = Image.alpha_composite(white_bg, im_raw)

im = im_raw.convert("L")
if SHARPEN:
    im = im.filter(ImageFilter.UnsharpMask(radius=2, percent=140, threshold=2))
im = ImageEnhance.Brightness(im).enhance(BRIGHTNESS)
im = ImageEnhance.Contrast(im).enhance(CONTRAST)
im = im.resize((COLS, ROWS), Image.LANCZOS)
px = im.load()

rows_txt = []
for y in range(ROWS):
    chars = []
    for x in range(COLS):
        lum = px[x, y] / 255.0
        lum = pow(lum, GAMMA)
        if lum >= WHITE_FLOOR:
            chars.append(" ")
            continue
        idx = int((1.0 - lum) * (len(RAMP) - 1) + 0.5)
        idx = max(0, min(len(RAMP) - 1, idx))
        chars.append(RAMP[idx])
    rows_txt.append("".join(chars))

art_top = TITLEBAR_H + PAD * 0.35

# ---- Info Card Config (Fastfetch Theme) ----------------
LINE_H = 22.0

# Bullet colors
B_INTRO = "#ffa657"
B_EDU = "#ffbd2e"
B_STACK = "#27c93f"
B_WORK = "#58a6ff"
B_PROJ = "#d2a8ff"

INFO_ROWS = [
    ("title", "moemairu@github"),
    ("gap",),
    ("box_top",),
    ("bullet", B_INTRO, "Intro", "Cyber Security student experienced in"),
    ("bullet", "none", "", "offensive security & cryptography. VP"),
    ("bullet", "none", "", "of a cybersecurity organization."),
    ("box_mid",),
    ("bullet", B_EDU, "Edu", "Informatics, UPN Veteran Jakarta"),
    ("bullet", B_STACK, "Stack", "Burp Suite, ZAP, C, Linux, x86 Asm"),
    ("bullet", "none", "", "(FASM), Java, Python"),
    ("box_mid",),
    ("bullet", B_WORK, "Now", "VP @ Cyber Security Study Club, UPNVJ"),
    ("bullet", B_WORK, "Also", "Lab Assistant @ CS Lab, UPNVJ"),
    ("bullet", B_WORK, "Also", "Penetration Tester @ Reunusa"),
    ("box_mid",),
    ("bullet", B_PROJ, "Proj", "Post-quantum file transfer (ML-KEM-768)"),
    ("bullet", B_PROJ, "Proj", "IDPS: 100% SQL inj. prevention rate"),
    ("bullet", B_PROJ, "Proj", "BadUSB scareware PoC in x86 Assembly"),
    ("box_bot",),
    ("palette",),
]

def esc(s):
    return html.escape(s)

def rise(inner, i):
    if STATIC:
        return f"<g>{inner}</g>"
    delay = 1.0 + i * 0.06  # slightly faster stagger for fastfetch theme
    return (f'<g opacity="0" transform="translate(0,5)">{inner}'
            f'<animate attributeName="opacity" from="0" to="1" begin="{delay:.2f}s" dur="0.4s" fill="freeze"/>'
            f'<animateTransform attributeName="transform" type="translate" from="0 5" to="0 0" '
            f'begin="{delay:.2f}s" dur="0.4s" fill="freeze" calcMode="spline" keySplines="0.2 0.8 0.2 1"/></g>')

# ---- 2. Assemble SVG ------------------------------------------------------
parts = []
parts.append(
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{CANVAS_W}" height="{CANVAS_H}" '
    f'viewBox="0 0 {CANVAS_W} {CANVAS_H}" font-family="ui-monospace, SFMono-Regular, '
    f'Menlo, Consolas, monospace">'
)

parts.append(f'<rect width="{CANVAS_W}" height="{CANVAS_H}" rx="12" fill="transparent"/>')
parts.append(f'<rect x="0.5" y="0.5" width="{CANVAS_W-1}" height="{CANVAS_H-1}" rx="12" '
             f'fill="none" stroke="{FRAME}" stroke-width="1" stroke-opacity="0.6"/>')

parts.append(f'<line x1="0" y1="{TITLEBAR_H}" x2="{CANVAS_W}" y2="{TITLEBAR_H}" stroke="{FRAME}" stroke-opacity="0.4"/>')
for i, dotcol in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
    parts.append(f'<circle cx="{PAD + i*16}" cy="{TITLEBAR_H/2}" r="5" fill="{dotcol}"/>')
parts.append(f'<text x="{CANVAS_W/2}" y="{TITLEBAR_H/2 + 4}" fill="{TITLE_TEXT}" font-size="12" '
             f'text-anchor="middle">moemairu@github: ~$ fastfetch</text>')

# ---- Draw ASCII Art ----
font_size = CELL_H * 0.86
for ry, line in enumerate(rows_txt):
    y = art_top + ry * CELL_H + CELL_H * 0.74
    row_y = art_top + ry * CELL_H
    delay = ry * STAGGER
    safe = esc(line)
    text = (f'<text xml:space="preserve" x="{PAD}" y="{y:.1f}" fill="{INK}" '
            f'font-size="{font_size:.1f}" textLength="{ART_W}" lengthAdjust="spacing">{safe}</text>')

    if STATIC:
        parts.append(text)
        continue

    parts.append(
        f'<clipPath id="r{ry}"><rect x="{PAD}" y="{row_y:.1f}" height="{CELL_H}" width="0">'
        f'<animate attributeName="width" from="0" to="{ART_W}" begin="{delay:.3f}s" '
        f'dur="{ROW_DUR:.2f}s" fill="freeze"/></rect></clipPath>'
    )
    parts.append(f'<g clip-path="url(#r{ry})">{text}</g>')
    parts.append(
        f'<rect y="{row_y+1:.1f}" width="{CELL_W}" height="{CELL_H-2}" fill="{CURSOR}" opacity="0">'
        f'<animate attributeName="x" from="{PAD}" to="{PAD+ART_W}" begin="{delay:.3f}s" '
        f'dur="{ROW_DUR:.2f}s" fill="freeze"/>'
        f'<set attributeName="opacity" to="0.85" begin="{delay:.3f}s"/>'
        f'<set attributeName="opacity" to="0" begin="{delay+ROW_DUR:.3f}s"/></rect>'
    )

# ---- Draw Info Card (Fastfetch Theme) ----
# Center the 429px tall info card vertically alongside the 720px tall ASCII art
info_y = TITLEBAR_H + 145
VAL_X = INFO_X + 90
FRAME_COL = "#595959"  # Dark gray for unicode box drawing lines

# Calculate box characters
BOX_W = 430
box_top = f"┌{'─'*22}●{'─'*28}┐"
box_mid = f"├{'─'*22}●{'─'*28}┤"
box_bot = f"└{'─'*22}●{'─'*28}┘"

# The right border is placed to align perfectly with the end of the textLength box.
# Since textLength is 430, the last character '┐' ends at exactly 430.
# The '│' character at size 14 is about 8.4px wide. If we place it at 430 - 8.4 = 421.6, it aligns left.
RIGHT_BORDER_X = INFO_X + 421.6

for i, row in enumerate(INFO_ROWS):
    kind = row[0]
    if kind == "gap":
        info_y += LINE_H * 0.5
        continue
    elif kind == "title":
        title = esc(row[1])
        inner = (f'<text x="{INFO_X}" y="{info_y:.1f}" fill="{INK}" font-size="22" font-weight="800">'
                 f'{title}</text>')
    elif kind == "box_top":
        inner = f'<text x="{INFO_X}" y="{info_y:.1f}" fill="{FRAME_COL}" font-size="14" font-weight="700" textLength="{BOX_W}" lengthAdjust="spacing">{esc(box_top)}</text>'
    elif kind == "box_mid":
        inner = f'<text x="{INFO_X}" y="{info_y:.1f}" fill="{FRAME_COL}" font-size="14" font-weight="700" textLength="{BOX_W}" lengthAdjust="spacing">{esc(box_mid)}</text>'
    elif kind == "box_bot":
        inner = f'<text x="{INFO_X}" y="{info_y:.1f}" fill="{FRAME_COL}" font-size="14" font-weight="700" textLength="{BOX_W}" lengthAdjust="spacing">{esc(box_bot)}</text>'
    elif kind == "bullet":
        color = row[1]
        key = esc(row[2])
        val = esc(row[3])
        bullet_svg = f'<text x="{INFO_X + 16}" y="{info_y:.1f}" fill="{color}" font-size="12">●</text>' if color != "none" else ""
        key_svg = f'<text x="{INFO_X + 32}" y="{info_y:.1f}" fill="{INK}" font-size="13.5" font-weight="700">{key}</text>' if key else ""
        inner = (
            f'<text x="{INFO_X}" y="{info_y:.1f}" fill="{FRAME_COL}" font-size="14" font-weight="700">│</text>'
            f'{bullet_svg}'
            f'{key_svg}'
            f'<text x="{VAL_X}" y="{info_y:.1f}" fill="{INK}" font-size="13.5">{val}</text>'
            f'<text x="{RIGHT_BORDER_X:.1f}" y="{info_y:.1f}" fill="{FRAME_COL}" font-size="14" font-weight="700">│</text>'
        )
    elif kind == "palette":
        # Draw the little color blocks at the bottom like fastfetch does
        swatches = ["#ff5f56", "#ffbd2e", "#27c93f", "#58a6ff", "#d2a8ff", "#22d3ee"]
        blocks = []
        cx = INFO_X + 80
        for s in swatches:
            blocks.append(f'<circle cx="{cx}" cy="{info_y-4:.1f}" r="6" fill="{s}"/>')
            cx += 20
        inner = "".join(blocks)
    else:
        continue
    
    parts.append(rise(inner, i))
    info_y += LINE_H

# status bar with a steady blinking cursor
status_line_y = TITLEBAR_H + ART_H + PAD * 0.35
status_y = status_line_y + 19
parts.append(f'<line x1="0" y1="{status_line_y:.1f}" x2="{CANVAS_W}" y2="{status_line_y:.1f}" stroke="{FRAME}" stroke-opacity="0.4"/>')
parts.append(f'<text x="{PAD}" y="{status_y:.1f}" fill="{TITLE_TEXT}" font-size="13">'
             f'moemairu@github:~$ whoami <tspan fill="{INK}">Isma\'il Faruqy</tspan></text>')
parts.append(f'<rect x="{PAD+224}" y="{status_y-12:.1f}" width="8" height="14" fill="{INK}">'
             f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.51;1" '
             f'dur="1s" repeatCount="indefinite"/></rect>')

parts.append("</svg>")
svg = "".join(parts)
with open(OUT, "w") as f:
    f.write(svg)
print("wrote", OUT, len(svg), "bytes;", CANVAS_W, "x", CANVAS_H)
