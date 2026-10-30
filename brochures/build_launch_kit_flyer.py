#!/usr/bin/env python3
"""Group Class Launch Kit in the Teacher Training Welcome Flyer style.

The trial class and the parent info session happen in one visit.
"""

import io
import os

from pypdf import PdfReader, PdfWriter
from reportlab.lib import colors
from reportlab.lib.utils import simpleSplit
from reportlab.pdfgen import canvas

from build_payback_flyer import (HERE, TEMPLATE, BLUE, DARK, MUTED, NOTE_FILL, NOTE_LINE,
                                 LEFT, RIGHT, COVER_TOP, COVER_BOTTOM, strip_welcome_text)

LAVENDER, LAVENDER_TXT = colors.HexColor("#E0CBE2"), colors.HexColor("#542E57")
TEAL, TEAL_TXT = colors.HexColor("#4AC3D4"), colors.HexColor("#0F4F58")
ORANGE, ORANGE_TXT = colors.HexColor("#FAD294"), colors.HexColor("#845100")
GREEN, GREEN_TXT = colors.HexColor("#C1D83F"), colors.HexColor("#4F5B0E")

COMMUNITY = ("During your training: community class",
             "Offer a free or paid music class at your local library or a preschool. Use your own "
             "songs and games, since My Music Box songs are for certified teachers. Collect the names "
             "of interested families.")

STEPS = [
    ("Week 1", "Invite families",
     "Invite your community class families, and share your flyer and posts.", LAVENDER, LAVENDER_TXT),
    ("Week 2", "Trial class and info session",
     "30 minutes of My Music Box songs, then a short parent talk.", TEAL, TEAL_TXT),
    ("Week 3", "Enroll and start",
     "Send follow-up emails, enroll families, start your class.", ORANGE, ORANGE_TXT),
]

KIT = [
    ("Trial class and info session plan", "30 minute class, then a short parent talk.", TEAL),
    ("Flyer and social post templates", "Ready to share when you start inviting.", LAVENDER),
    ("Enrollment follow-up emails", "Turn the first visit into enrollment.", ORANGE),
    ("Two live coaching calls", "Bring questions in your first semester.", GREEN),
]


def rounded_top_band(c, x, y_top_pdf, w, band, rad):
    p = c.beginPath()
    p.moveTo(x, y_top_pdf - band)
    p.lineTo(x, y_top_pdf - rad)
    p.arcTo(x, y_top_pdf - 2 * rad, x + 2 * rad, y_top_pdf, startAng=180, extent=-90)
    p.lineTo(x + w - rad, y_top_pdf)
    p.arcTo(x + w - 2 * rad, y_top_pdf - 2 * rad, x + w, y_top_pdf, startAng=90, extent=-90)
    p.lineTo(x + w, y_top_pdf - band)
    p.close()
    c.drawPath(p, stroke=0, fill=1)


def wrapped(c, text, font, size, x, y_top, width, page_h, leading):
    lines = simpleSplit(text, font, size, width)
    c.setFont(font, size)
    for i, line in enumerate(lines):
        c.drawString(x, page_h - (y_top + i * leading), line)
    return y_top + (len(lines) - 1) * leading


def build_overlay(page_w, page_h):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(page_w, page_h))

    def Y(top):
        return page_h - top

    c.setFillColor(colors.white)
    c.rect(40, Y(COVER_BOTTOM), page_w - 80, COVER_BOTTOM - COVER_TOP, stroke=0, fill=1)

    cx = page_w / 2
    c.setFillColor(BLUE)
    c.setFont("Fredoka-SemiBold", 24)
    c.drawCentredString(cx, Y(224), "Group Class Launch Kit")
    c.setFillColor(MUTED)
    c.setFont("Inter-Regular", 10.5)
    c.drawCentredString(cx, Y(246), "From your training to your first full group class. Included with your Book 1 training.")

    width = RIGHT - LEFT
    c.setFillColor(BLUE)
    c.setFont("Fredoka-SemiBold", 14)
    c.drawString(LEFT, Y(274), "Your path, step by step")

    # during training: full-width community class card
    top, band = 284, 24
    title, body = COMMUNITY
    body_lines = simpleSplit(body, "Inter-Regular", 9.5, width - 24)
    ch = band + 12 + len(body_lines) * 13.5
    c.setLineWidth(2)
    c.setStrokeColor(GREEN)
    c.setFillColor(colors.white)
    c.roundRect(LEFT, Y(top + ch), width, ch, 10, stroke=1, fill=1)
    c.setFillColor(GREEN)
    rounded_top_band(c, LEFT, Y(top), width, band, 10)
    c.setFillColor(GREEN_TXT)
    c.setFont("Fredoka-SemiBold", 12)
    c.drawString(LEFT + 12, Y(top + 16), title)
    c.setFillColor(MUTED)
    wrapped(c, body, "Inter-Regular", 9.5, LEFT + 12, top + band + 15, width - 24, page_h, 13.5)

    # after certification: three week cards
    after = top + ch + 20
    c.setFillColor(BLUE)
    c.setFont("Fredoka-Medium", 11)
    c.drawString(LEFT, Y(after), "After your Book 1 certification")
    gap, top, th = 14, after + 10, 114
    tw = (width - 2 * gap) / 3
    for i, (week, title, body, accent, accent_txt) in enumerate(STEPS):
        x = LEFT + i * (tw + gap)
        c.setLineWidth(2)
        c.setStrokeColor(accent)
        c.setFillColor(colors.white)
        c.roundRect(x, Y(top + th), tw, th, 10, stroke=1, fill=1)
        c.setFillColor(accent)
        rounded_top_band(c, x, Y(top), tw, 26, 10)
        c.setFillColor(accent_txt)
        c.setFont("Fredoka-SemiBold", 12)
        c.drawCentredString(x + tw / 2, Y(top + 17), week)
        c.setFillColor(DARK)
        end = wrapped(c, title, "Inter-Bold", 10.5, x + 12, top + 46, tw - 24, page_h, 13.5)
        c.setFillColor(MUTED)
        last = wrapped(c, body, "Inter-Regular", 9.5, x + 12, end + 18, tw - 24, page_h, 13.5)
        assert last + 8 < top + th, f"{week} text runs past its card"

    # what's in the kit, 2 x 2 panels
    kit_top = top + th + 26
    c.setFillColor(BLUE)
    c.setFont("Fredoka-SemiBold", 14)
    c.drawString(LEFT, Y(kit_top), "What's in your launch kit")
    pw, ph, pg = (width - 14) / 2, 44, 10
    for i, (title, desc, accent) in enumerate(KIT):
        x = LEFT + (i % 2) * (pw + 14)
        t = kit_top + 12 + (i // 2) * (ph + pg)
        assert len(simpleSplit(desc, "Inter-Regular", 9, pw - 26)) == 1, desc
        c.setLineWidth(1)
        c.setStrokeColor(colors.HexColor("#E5E4E2"))
        c.setFillColor(colors.HexColor("#FAFAF9"))
        c.roundRect(x, Y(t + ph), pw, ph, 8, stroke=1, fill=1)
        c.setFillColor(accent)
        c.roundRect(x, Y(t + ph), 6, ph, 3, stroke=0, fill=1)
        c.setFillColor(DARK)
        c.setFont("Inter-Bold", 10)
        c.drawString(x + 16, Y(t + 18), title)
        c.setFillColor(MUTED)
        c.setFont("Inter-Regular", 9)
        c.drawString(x + 16, Y(t + 32), desc)

    # trial class video
    nt, nh = kit_top + 12 + 2 * ph + pg + 12, 40
    c.setFillColor(NOTE_FILL)
    c.setStrokeColor(NOTE_LINE)
    c.roundRect(LEFT, Y(nt + nh), width, nh, 8, stroke=1, fill=1)
    c.setFillColor(DARK)
    c.setFont("Inter-Bold", 9.5)
    c.drawString(LEFT + 12, Y(nt + 16), "Trial class video:")
    c.setFont("Inter-Regular", 9.5)
    label_w = c.stringWidth("Trial class video: ", "Inter-Bold", 9.5)
    c.drawString(LEFT + 12 + label_w, Y(nt + 16), "watch a full 30 minute trial class taught with")
    c.drawString(LEFT + 12, Y(nt + 30), "My Music Box songs, then teach your own the same way.")

    closing = nt + nh + 16
    assert closing <= COVER_BOTTOM - 2, f"content runs to {closing}"
    c.setFillColor(MUTED)
    c.setFont("Inter-Regular", 9.5)
    c.drawCentredString(cx, Y(closing), "How to use: type your details on the flyers, then print or email. "
                                        "Captions are on the last pages.")
    c.showPage()
    c.save()
    buf.seek(0)
    return PdfReader(buf).pages[0]


def build():
    out = PdfWriter(clone_from=TEMPLATE)
    page = out.pages[0]
    strip_welcome_text(out, page)
    page.merge_page(build_overlay(float(page.mediabox.width), float(page.mediabox.height)))
    out.add_metadata({"/Title": "My Music Box Group Class Launch Kit", "/Author": "MyMusicBox Academy"})
    path = os.path.join(HERE, "MyMusicBox_Group_Class_Launch_Kit_Flyer.pdf")
    with open(path, "wb") as f:
        out.write(f)
    return path


if __name__ == "__main__":
    print(build())
