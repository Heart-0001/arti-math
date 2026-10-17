"""Locate, preview and crop regions of a PDF for the arti-math notebook page.

Usage:
  pdfcrop.py find   <pdf> <text>                      # pages + boxes (as page fractions) where text occurs
  pdfcrop.py render <pdf> <page> <out.png> [--dpi 80]  # whole page, low dpi, to look at before cropping
  pdfcrop.py crop   <pdf> <page> <out_base> --box x0,y0,x1,y1 [--dpi 220] [--color]

Pages are 1-based. Boxes are fractions of the page (0..1, origin top-left).
`crop` writes <out_base>.png and <out_base>_dark.png, tinted to the template's
paper/ink colors so the image blends into the entry card in both themes.
With --color the light version keeps the original colors and the dark one is
a plain inversion.
"""
import argparse
import sys

import fitz  # PyMuPDF

# Keep in sync with --paper / --ink in assets/template.html
LIGHT_PAPER, LIGHT_INK = (0xFB, 0xFC, 0xFA), (0x1C, 0x26, 0x22)
DARK_PAPER, DARK_INK = (0x16, 0x1E, 0x1A), (0xDD, 0xE6, 0xE0)


def cmd_find(a):
    doc = fitz.open(a.pdf)
    hits = 0
    for pno, page in enumerate(doc, 1):
        w, h = page.rect.width, page.rect.height
        for r in page.search_for(a.text):
            hits += 1
            print(f"page {pno}: box {r.x0 / w:.3f},{r.y0 / h:.3f},{r.x1 / w:.3f},{r.y1 / h:.3f}")
    if not hits:
        print("no match")


def cmd_render(a):
    page = fitz.open(a.pdf)[a.page - 1]
    page.get_pixmap(dpi=a.dpi).save(a.out)
    print(a.out)


def tint(pix, paper, ink):
    """Map grayscale value v (0 = black, 255 = white) linearly onto ink..paper."""
    gray = fitz.Pixmap(fitz.csGRAY, pix) if pix.n != 1 else pix
    lut = [bytes(round(i + (p - i) * v / 255) for i, p in zip(ink, paper)) for v in range(256)]
    data = b"".join(lut[v] for v in gray.samples)
    return fitz.Pixmap(fitz.csRGB, gray.width, gray.height, data, False)


def cmd_crop(a):
    page = fitz.open(a.pdf)[a.page - 1]
    x0, y0, x1, y1 = (float(v) for v in a.box.split(","))
    w, h = page.rect.width, page.rect.height
    clip = fitz.Rect(x0 * w, y0 * h, x1 * w, y1 * h)
    pix = page.get_pixmap(dpi=a.dpi, clip=clip, alpha=False)
    if pix.n == 4:
        pix = fitz.Pixmap(fitz.csRGB, pix)
    if a.color:
        light = pix
        dark = fitz.Pixmap(pix)
        dark.invert_irect(dark.irect)
    else:
        light = tint(pix, LIGHT_PAPER, LIGHT_INK)
        dark = tint(pix, DARK_PAPER, DARK_INK)
    light.save(a.out_base + ".png")
    dark.save(a.out_base + "_dark.png")
    print(f"{a.out_base}.png  {a.out_base}_dark.png  ({pix.width}x{pix.height}px)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("find")
    f.add_argument("pdf")
    f.add_argument("text")
    r = sub.add_parser("render")
    r.add_argument("pdf")
    r.add_argument("page", type=int)
    r.add_argument("out")
    r.add_argument("--dpi", type=int, default=80)
    c = sub.add_parser("crop")
    c.add_argument("pdf")
    c.add_argument("page", type=int)
    c.add_argument("out_base")
    c.add_argument("--box", required=True)
    c.add_argument("--dpi", type=int, default=220)
    c.add_argument("--color", action="store_true")
    a = ap.parse_args()
    {"find": cmd_find, "render": cmd_render, "crop": cmd_crop}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
