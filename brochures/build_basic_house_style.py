#!/usr/bin/env python3
"""Basic-license trial class materials in the My Music Box one-page house style.

One palette color per page. The teacher's own studio name goes where the house style
has the wordmark, and the footer carries the allowed line
"Taught by a Book 1 Certified My Music Box Teacher".
"""

import os

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (BaseDocTemplate, Frame, HRFlowable, PageTemplate, Paragraph,
                                Spacer, Table, TableStyle)

from build_brochures import (DARK, MUTED, BORDER, PANEL, bullet_line, plain_bullet_column)

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "basic")
LIB = "/usr/share/fonts/truetype/liberation"
CERT_LINE = "Taught by a Book 1 Certified My Music Box Teacher"

# one hue per page: (band color, light tint for the card header, text pairing)
HUES = {
    "purple": ("#B683BA", "#E0CBE2", "#542E57"),
    "teal": ("#4AC3D4", "#D5F1F5", "#15646F"),
    "green": ("#C1D83F", "#EEF5CB", "#647312"),
    "orange": ("#FAD294", "#FDEFD8", "#845100"),
}

PAGE_W, PAGE_H = LETTER
MARGIN = 0.7 * inch
BAND_H = 0.18 * inch

INVITE = dict(
    filename="Trial_Class_Invite_Flyer.pdf", hue="purple",
    title="Come try a group piano class!",
    subtitle="A free 30 minute trial class for children ages 4 to 7.",
    left_head="What to expect",
    left_items=["Sing and move to music", "Play first notes on the piano",
                "Make music with new friends", "Parents watch, then stay for a short talk",
                "Up to 8 children, about 45 minutes in all"],
    left_footer="Free, with no commitment. Come see if group piano is right for your child.",
    card_head="Trial class details",
    fields=["Date", "Time", "Place", "Teacher", "Save a spot"],
    card_sentence="Spots are limited, so save yours today.",
)

REMINDER = dict(
    filename="Trial_Class_Reminder_Flyer.pdf", hue="teal",
    title="See you at the trial class!",
    subtitle="We can't wait to make music with your child.",
    left_head="Your visit",
    left_items=["Welcome, 5 minutes", "Trial class, 30 minutes", "Parent talk, 10 minutes",
                "Please arrive 5 minutes early", "One parent stays for the whole visit"],
    left_footer="Comfortable clothes are best. Bring your questions for the parent talk.",
    card_head="Your trial class",
    fields=["Date", "Time", "Place", "Contact"],
    card_sentence="If your plans change, please let your teacher know.",
)


# ------------------------------------ flyers ------------------------------------

def on_page_for(band):
    def on_page(c, doc):
        c.saveState()
        c.setFillColor(band)
        c.rect(0, PAGE_H - BAND_H, PAGE_W, BAND_H, stroke=0, fill=1)
        # teacher's studio name where the house style has the wordmark
        y = PAGE_H - BAND_H - 0.36 * inch
        c.setStrokeColor(BORDER)
        c.setLineWidth(0.8)
        c.line(PAGE_W - MARGIN - 2.4 * inch, y, PAGE_W - MARGIN, y)
        c.setFont('Sans', 8.5)
        c.setFillColor(MUTED)
        c.drawRightString(PAGE_W - MARGIN, y - 11, "Your studio name")
        c.setStrokeColor(BORDER)
        c.setLineWidth(0.75)
        c.line(MARGIN, 0.55 * inch, PAGE_W - MARGIN, 0.55 * inch)
        c.setFont('Sans', 9)
        c.drawString(MARGIN, 0.38 * inch, CERT_LINE)
        c.restoreState()
    return on_page


def details_card(head, fields, sentence, tint, txt, width):
    header = Table([[Paragraph(head, ParagraphStyle(
        "h", fontName="Sans-Bold", fontSize=13.5, leading=16, textColor=txt))]], colWidths=[width])
    header.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), tint),
        ("LEFTPADDING", (0, 0), (-1, -1), 14), ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
    ]))
    label = ParagraphStyle("l", fontName="Sans-Bold", fontSize=10.8, leading=14, textColor=DARK)
    rows = [[Paragraph(f, label), ""] for f in fields]
    lines = Table(rows, colWidths=[1.0 * inch, width - 1.0 * inch - 24], rowHeights=34)
    lines.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
        ("LINEBELOW", (1, 0), (1, -1), 0.8, colors.HexColor("#C9C7C4")),
        ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    note = Paragraph(sentence, ParagraphStyle("n", fontName="Sans", fontSize=10.8, leading=15.3,
                                              textColor=DARK))
    body = Table([[lines], [Spacer(1, 14)], [note], [Spacer(1, 6)]], colWidths=[width - 24])
    body.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PANEL),
        ("LEFTPADDING", (0, 0), (-1, -1), 12), ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    outer = Table([[header], [body]], colWidths=[width])
    outer.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1, BORDER),
        ("BACKGROUND", (0, 1), (-1, -1), PANEL),
        ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    return outer


def flyer(spec):
    band, tint, txt = (colors.HexColor(h) for h in HUES[spec["hue"]])
    story = [
        Spacer(1, 0.3 * inch),
        Paragraph(spec["title"], ParagraphStyle("t", fontName="Sans-Bold", fontSize=23, leading=27,
                                                textColor=DARK, spaceAfter=6)),
        Paragraph(spec["subtitle"], ParagraphStyle("s", fontName="Sans", fontSize=11.5, leading=16,
                                                   textColor=MUTED, spaceAfter=22)),
    ]
    LEFT_W, RIGHT_W, GAP = 2.5 * inch, 4.1 * inch, 20
    left = plain_bullet_column(spec["left_head"], spec["left_items"], spec["left_footer"], txt, LEFT_W)
    right = details_card(spec["card_head"], spec["fields"], spec["card_sentence"], tint, txt, RIGHT_W)
    grid = Table([[left, right]], colWidths=[LEFT_W + GAP, RIGHT_W])
    grid.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LINEAFTER", (0, 0), (0, 0), 1, BORDER),
        ("LEFTPADDING", (0, 0), (0, 0), 0), ("RIGHTPADDING", (0, 0), (0, 0), GAP),
        ("LEFTPADDING", (1, 0), (1, 0), GAP), ("RIGHTPADDING", (1, 0), (1, 0), 0),
    ]))
    story += [grid]

    path = os.path.join(OUT, spec["filename"])
    doc = BaseDocTemplate(path, pagesize=LETTER, leftMargin=MARGIN, rightMargin=MARGIN,
                          topMargin=MARGIN + BAND_H, bottomMargin=0.75 * inch, title=spec["title"])
    frame = Frame(MARGIN, 0.75 * inch, PAGE_W - 2 * MARGIN, PAGE_H - MARGIN - BAND_H - 0.75 * inch, id="c")
    doc.addPageTemplates([PageTemplate(id="c", frames=[frame], onPage=on_page_for(band))])
    doc.build(story)
    return path


# ---------------------------------- Instagram -----------------------------------

W, H = 1080, 1350
INK, GRAY, RULE, PANEL_HEX = "#3A3A3A", "#6B6B6B", "#E5E4E2", "#F6F5F4"
SIDE = 84


def pf(bold, size):
    return ImageFont.truetype(f"{LIB}/LiberationSans-{'Bold' if bold else 'Regular'}.ttf", size)


def tw(d, s, f):
    return d.textbbox((0, 0), s, font=f)[2]


def page(hue):
    band, tint, txt = HUES[hue]
    im = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, W, 34), fill=band)
    d.line((SIDE, H - 118, W - SIDE, H - 118), fill=RULE, width=2)
    d.text((SIDE, H - 88), CERT_LINE, font=pf(False, 28), fill=GRAY)
    return im, d, (band, tint, txt)


def headline(d, y, lines, size=76):
    f = pf(True, size)
    for ln in lines:
        d.text((SIDE, y), ln, font=f, fill=INK)
        y += int(size * 1.18)
    return y


def dot_list(d, y, items, txt, size=36, gap=22):
    f = pf(True, size)
    for it in items:
        r = 8
        d.ellipse((SIDE + 4, y + size / 2 - r, SIDE + 4 + 2 * r, y + size / 2 + r), fill=txt)
        d.text((SIDE + 40, y), it, font=f, fill=INK)
        assert SIDE + 40 + tw(d, it, f) < W - SIDE, it
        y += size + gap
    return y


def card(d, y, head, body_lines, colors_, size=34):
    band, tint, txt = colors_
    x1, x2 = SIDE, W - SIDE
    hh = 84
    body_h = 36 + len(body_lines) * (size + 18) + 18
    d.rectangle((x1, y, x2, y + hh + body_h), fill=PANEL_HEX, outline=RULE, width=2)
    d.rectangle((x1 + 1, y + 1, x2 - 1, y + hh), fill=tint)
    d.text((x1 + 30, y + (hh - 40) / 2), head, font=pf(True, 40), fill=txt)
    ty = y + hh + 36
    for bold, s in body_lines:
        d.text((x1 + 30, ty), s, font=pf(bold, size), fill=INK)
        assert x1 + 30 + tw(d, s, pf(bold, size)) < x2 - 24, s
        ty += size + 18
    return y + hh + body_h


def centered_post(fn):
    """Measure the post, then redraw it centered between the top band and the footer."""
    _, end = fn()
    bottom = H - 160
    assert end <= bottom, f"{fn.__name__} runs into the footer"
    im, _ = fn(140 + (bottom - end) / 2)
    return im


def ig_invite(y0=140):
    im, d, c = page("purple")
    y = y0
    d.text((SIDE, y), "Free trial class", font=pf(True, 34), fill=c[2])
    y = headline(d, y + 60, ["Come try a", "group piano class!"])
    d.text((SIDE, y + 10), "For children ages 4 to 7. 30 minutes.", font=pf(False, 36), fill=GRAY)
    y = dot_list(d, y + 100, ["Sing and move to music", "Play first notes on the piano",
                              "Make music with new friends"], c[2])
    y = card(d, y + 34, "Save a spot", [(True, "Send us a message today."),
                                         (False, "Up to 8 children per class.")], c)
    return im, y


def ig_what_happens(y0=140):
    im, d, c = page("green")
    y = y0
    d.text((SIDE, y), "Free trial class", font=pf(True, 34), fill=c[2])
    y = headline(d, y + 60, ["What happens in", "a trial class?"])
    y = card(d, y + 40, "In 30 minutes, your child will", [
        (True, "1.  Sing first"), (False, "      Sing the song before playing it."),
        (True, "2.  Move to the music"), (False, "      Feel the rhythm in the body."),
        (True, "3.  Play the piano"), (False, "      First notes, with new friends.")], c, size=32)
    d.text((SIDE, y + 36), "Parents watch, then stay for a short talk.", font=pf(False, 34), fill=GRAY)
    d.text((SIDE, y + 96), "Message us to save a spot.", font=pf(True, 36), fill=c[2])
    return im, y + 140


def ig_last_spots(y0=140):
    im, d, c = page("orange")
    y = y0
    d.text((SIDE, y), "Free trial class", font=pf(True, 34), fill=c[2])
    y = headline(d, y + 60, ["Only a few", "spots left!"], size=96)
    d.text((SIDE, y + 10), "Group piano for children ages 4 to 7.", font=pf(False, 36), fill=GRAY)
    y = dot_list(d, y + 100, ["30 minute trial class", "Up to 8 children", "Parents stay and watch"], c[2])
    y = card(d, y + 34, "Message us today", [(True, "Spots go to the first families"),
                                              (True, "who reach out.")], c)
    return im, y


if __name__ == "__main__":
    os.makedirs(os.path.join(OUT, "instagram"), exist_ok=True)
    for spec in (INVITE, REMINDER):
        print(flyer(spec))
    for name, fn in [("post1_invite", ig_invite), ("post2_what_happens", ig_what_happens),
                     ("post3_last_spots", ig_last_spots)]:
        p = os.path.join(OUT, "instagram", f"{name}.png")
        centered_post(fn).save(p, optimize=True)
        print(p)
