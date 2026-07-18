"""
Prepare a portrait photo for clean ASCII conversion.
Source photo is assumed to already have background removed (transparent or white).

Steps:
  1. Load image, composite any transparent areas onto white
  2. Convert to grayscale
  3. Boost contrast with autocontrast + ImageEnhance (Pillow-only, no opencv needed)

Output: source-prepped.png (grayscale), consumed by make_ascii_svg.py.
Run once whenever the source photo changes.

    python scripts/prep_photo.py [input.png] [output.png]
"""
import os
import sys

from PIL import Image, ImageEnhance, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
INP = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "source-photo.png")
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "..", "source-prepped.png")

# 1. Load and composite onto white background (handles transparent PNGs)
img = Image.open(INP).convert("RGBA")
white_bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
white_bg.paste(img, mask=img.split()[3])  # use alpha as mask
rgb = white_bg.convert("RGB")

# 2. Convert to grayscale
gray = rgb.convert("L")

# 3. Autocontrast to stretch the histogram (similar effect to CLAHE globally)
gray = ImageOps.autocontrast(gray, cutoff=1)

# 4. A touch of contrast + brightness boost so face lands in the sparse ASCII range
gray = ImageEnhance.Contrast(gray).enhance(1.3)
gray = ImageEnhance.Brightness(gray).enhance(1.1)

gray.save(OUT)
print("wrote", OUT, gray.size)
