#!/usr/bin/env python3
"""Training payback flyers in the Teacher Training Welcome Flyer style.

Keeps the welcome flyer's sky background, piano illustration, tagline and footer,
and replaces the welcome text with payback stat cards and charts.
"""

import io
import os

from pypdf import PdfReader, PdfWriter
from pypdf.generic import ContentStream
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "Teacher-Training-Welcome-Flyer.pdf")
FONTS = os.path.join(HERE, "fonts")

for name in ["Fredoka-Medium", "Fredoka-SemiBold", "Inter-Regular", "Inter-Bold"]:
    pdfmetrics.registerFont(TTFont(name, os.path.join(FONTS, f"{name}.ttf")))

BLUE = colors.HexColor("#3E8EC4")
DARK = colors.HexColor("#3A3A3A")
MUTED = colors.HexColor("#6B6B6B")
TRACK = colors.HexColor("#EDEDED")
NOTE_FILL, NOTE_LINE = colors.HexColor("#EEF7FD"), colors.HexColor("#BFE0F4")

# (group size, solid color, light tint, text color)
GROUPS = [
    (4, colors.HexColor("#B683BA"), colors.HexColor("#F1E8F2"), colors.HexColor("#542E57")),
    (6, colors.HexColor("#4AC3D4"), colors.HexColor("#DAF3F6"), colors.HexColor("#15646F")),
    (8, colors.HexColor("#F2B866"), colors.HexColor("#FDEFD8"), colors.HexColor("#845100")),
]
TILE_STYLES = [
    (colors.HexColor("#E0CBE2"), colors.HexColor("#542E57")),
    (colors.HexColor("#4AC3D4"), colors.HexColor("#0F4F58")),
    (colors.HexColor("#FAD294"), colors.HexColor("#845100")),
]

REGIONS = {
    "Region1": dict(founding=2200, lesson=(35, 50)),
    "Region2": dict(founding=1600, lesson=(15, 30)),
}
LESSONS_PER_MONTH = 4

# Content area (points from the top of the page), inside the white card,
# between "Happy Musician" and the "Teach with joy" tagline.
COVER_TOP, COVER_BOTTOM = 196, 718
LEFT, RIGHT = 74, 520


def build_overlay(page_w, page_h, r):
    lo, hi = r["lesson"]
    fee = r["founding"]
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(page_w, page_h))

    def Y(top):  # convert distance-from-top to PDF y
        return page_h - top

    # clear the welcome text and the three cards
    c.setFillColor(colors.white)
    c.rect(40, Y(COVER_BOTTOM), page_w - 80, COVER_BOTTOM - COVER_TOP, stroke=0, fill=1)

    cx = page_w / 2
    c.setFillColor(BLUE)
    c.setFont("Fredoka-SemiBold", 22)
    c.drawCentredString(cx, Y(218), "What does this look like")
    c.drawCentredString(cx, Y(247), "in your studio?")
    c.setFillColor(MUTED)
    c.setFont("Inter-Regular", 10.5)
    c.drawCentredString(cx, Y(268), f"Book 1 training: ${fee:,} founding price. Payment plan available at checkout.")

    # stat cards, styled like the flyer's three cards
    width = RIGHT - LEFT
    gap = 14
    tw, top, th, band = (width - 2 * gap) / 3, 284, 84, 24
    fastest = fee / (8 * hi * LESSONS_PER_MONTH)
    slowest = fee / (4 * lo * LESSONS_PER_MONTH)
    tiles = [
        ("Students per group", "4 to 8"),
        ("Per student per month", f"${lo * LESSONS_PER_MONTH}-${hi * LESSONS_PER_MONTH}"),
        ("To earn it back", f"{max(1, round(fastest))}-{round(slowest + 0.49)} months"),
    ]
    for i, ((label, value), (accent, accent_txt)) in enumerate(zip(tiles, TILE_STYLES)):
        x = LEFT + i * (tw + gap)
        c.setLineWidth(2)
        c.setStrokeColor(accent)
        c.setFillColor(colors.white)
        c.roundRect(x, Y(top + th), tw, th, 10, stroke=1, fill=1)
        p = c.beginPath()  # header band with rounded top corners
        rad = 10
        p.moveTo(x, Y(top + band))
        p.lineTo(x, Y(top + rad))
        p.arcTo(x, Y(top + 2 * rad), x + 2 * rad, Y(top), startAng=180, extent=-90)
        p.lineTo(x + tw - rad, Y(top))
        p.arcTo(x + tw - 2 * rad, Y(top + 2 * rad), x + tw, Y(top), startAng=90, extent=-90)
        p.lineTo(x + tw, Y(top + band))
        p.close()
        c.setFillColor(accent)
        c.drawPath(p, stroke=0, fill=1)
        c.setFillColor(accent_txt)
        c.setFont("Fredoka-Medium", 11)
        c.drawCentredString(x + tw / 2, Y(top + 16), label)
        c.setFont("Fredoka-SemiBold", 22)
        c.drawCentredString(x + tw / 2, Y(top + band + 37), value)

    label_w, value_w = 78, 62
    bar_x = LEFT + label_w
    bar_w = width - label_w - value_w
    bar_h = 14

    def row_label(y_top, n, solid):
        c.setFillColor(solid)
        c.circle(LEFT + 5, Y(y_top + bar_h / 2), 5, stroke=0, fill=1)
        c.setFillColor(DARK)
        c.setFont("Inter-Bold", 10)
        c.drawString(LEFT + 15, Y(y_top + 11), f"{n} students")

    # monthly income range chart
    c.setFillColor(BLUE)
    c.setFont("Fredoka-SemiBold", 14)
    c.drawString(LEFT, Y(400), "Monthly income by group size")
    c.setFillColor(MUTED)
    c.setFont("Inter-Regular", 9.5)
    c.drawString(LEFT, Y(414), f"One weekly class, 4 lessons a month, ${lo} to ${hi} per student per lesson")

    max_val = 8 * hi * LESSONS_PER_MONTH
    y_top = 436
    for n, solid, tint, txt in GROUPS:
        low, high = n * lo * LESSONS_PER_MONTH, n * hi * LESSONS_PER_MONTH
        row_label(y_top, n, solid)
        c.setFillColor(TRACK)
        c.rect(bar_x, Y(y_top + bar_h), bar_w, bar_h, stroke=0, fill=1)
        lx, hx = bar_x + bar_w * low / max_val, bar_x + bar_w * high / max_val
        c.setFillColor(tint)
        c.rect(bar_x, Y(y_top + bar_h), lx - bar_x, bar_h, stroke=0, fill=1)
        c.setFillColor(solid)
        c.rect(lx, Y(y_top + bar_h), hx - lx, bar_h, stroke=0, fill=1)
        c.setFillColor(MUTED)
        c.setFont("Inter-Regular", 8.5)
        c.drawCentredString(lx, Y(y_top - 3), f"${low:,}")
        c.setFillColor(txt)
        c.setFont("Fredoka-SemiBold", 12)
        c.drawString(bar_x + bar_w + 8, Y(y_top + 11), f"${high:,}/mo")
        y_top += 34

    # legend
    ly = y_top - 6
    c.setFillColor(TRACK)
    c.rect(bar_x, Y(ly + 8), 12, 8, stroke=0, fill=1)
    c.setFillColor(MUTED)
    c.setFont("Inter-Regular", 8.5)
    c.drawString(bar_x + 17, Y(ly + 7), f"light part: ${lo} per student")
    c.setFillColor(colors.HexColor("#9A9A9A"))
    c.rect(bar_x + 150, Y(ly + 8), 12, 8, stroke=0, fill=1)
    c.setFillColor(MUTED)
    c.drawString(bar_x + 167, Y(ly + 7), f"full bar: ${hi} per student")

    # months to earn the training back
    c.setFillColor(BLUE)
    c.setFont("Fredoka-SemiBold", 14)
    c.drawString(LEFT, Y(566), f"Months to earn your ${fee:,} training back")
    c.setFillColor(MUTED)
    c.setFont("Inter-Regular", 9.5)
    c.drawString(LEFT, Y(580), f"At the average price: ${(lo + hi) / 2:.2f} per student per lesson "
                              f"(${lo} + ${hi}, divided by 2)")

    mid = (lo + hi) / 2
    longest = fee / (4 * mid * LESSONS_PER_MONTH)
    y_top = 592
    for n, solid, tint, txt in GROUPS:
        months = fee / (n * mid * LESSONS_PER_MONTH)
        bw = bar_w * months / longest
        row_label(y_top, n, solid)
        c.setFillColor(solid)
        c.rect(bar_x, Y(y_top + bar_h), bw, bar_h, stroke=0, fill=1)
        c.setFillColor(txt)
        c.setFont("Fredoka-SemiBold", 12)
        c.drawString(bar_x + bw + 8, Y(y_top + 11), f"{months:.1f} months")
        y_top += 23

    # note
    nt, nh = 670, 28
    c.setFillColor(NOTE_FILL)
    c.setStrokeColor(NOTE_LINE)
    c.setLineWidth(1)
    c.roundRect(LEFT, Y(nt + nh), width, nh, 8, stroke=1, fill=1)
    c.setFillColor(DARK)
    c.setFont("Inter-Bold", 9)
    c.drawString(LEFT + 10, Y(nt + 17.5), "Examples only.")
    c.setFont("Inter-Regular", 9)
    c.drawString(LEFT + 80, Y(nt + 17.5), "You set your own tuition. First year of your annual license is free, "
                                          "then $499 a year.")

    c.showPage()
    c.save()
    buf.seek(0)
    return PdfReader(buf).pages[0]


def strip_welcome_text(reader, page):
    """Remove the welcome flyer's text blocks inside the content area, so the old
    words are gone from the file, not just covered."""
    ops = ContentStream(page.get_contents(), reader).operations
    height = float(page.mediabox.height)
    ctm, stack, kept, block, drop = [1, 0, 0, 1, 0, 0], [], [], None, False

    def concat(m, n):  # m then n, both as [a b c d e f]
        return [m[0] * n[0] + m[1] * n[2], m[0] * n[1] + m[1] * n[3],
                m[2] * n[0] + m[3] * n[2], m[2] * n[1] + m[3] * n[3],
                m[4] * n[0] + m[5] * n[2] + n[4], m[4] * n[1] + m[5] * n[3] + n[5]]

    for operands, op in ops:
        if op == b"q":
            stack.append(ctm)
        elif op == b"Q":
            ctm = stack.pop()
        elif op == b"cm":
            ctm = concat([float(v) for v in operands], ctm)
        if op == b"BT":
            block, drop = [], False
        if block is not None:
            block.append((operands, op))
            if op == b"Tm":
                top = height - concat([float(v) for v in operands], ctm)[5]
                drop = COVER_TOP <= top <= COVER_BOTTOM
            if op == b"ET":
                if not drop:
                    kept.extend(block)
                block = None
            continue
        kept.append((operands, op))

    cs = ContentStream(None, reader)
    cs.operations = kept
    page.replace_contents(cs)


def build(region, r):
    out = PdfWriter(clone_from=TEMPLATE)
    template = out.pages[0]
    strip_welcome_text(out, template)
    w, h = float(template.mediabox.width), float(template.mediabox.height)
    template.merge_page(build_overlay(w, h, r))
    out.add_metadata({"/Title": "My Music Box Training Payback", "/Author": "MyMusicBox Academy"})
    path = os.path.join(HERE, f"MyMusicBox_Training_Payback_{region}_Flyer.pdf")
    with open(path, "wb") as f:
        out.write(f)
    return path


if __name__ == "__main__":
    for region, r in REGIONS.items():
        print(build(region, r))
