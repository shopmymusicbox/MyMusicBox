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
from reportlab.platypus import (BaseDocTemplate, Flowable, Frame, HRFlowable, PageTemplate, Paragraph,
                                Spacer, Table, TableStyle)

from build_brochures import (DARK, MUTED, BORDER, PANEL, bullet_line, plain_bullet_column)

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "fonts")
# Nunito: rounded and friendly, and not the My Music Box brand font (Fredoka)
pdfmetrics.registerFont(TTFont("Sans", os.path.join(FONTS, "Nunito-Regular.ttf")))
pdfmetrics.registerFont(TTFont("Sans-Bold", os.path.join(FONTS, "Nunito-Bold.ttf")))
pdfmetrics.registerFont(TTFont("Sans-XBold", os.path.join(FONTS, "Nunito-ExtraBold.ttf")))
NOTE_FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
pdfmetrics.registerFont(TTFont("Notes", NOTE_FONT))
NOTES = ["\u266A", "\u266B", "\u2669", "\u266C"]
OUT = os.path.join(HERE, "basic")
LIB = "/usr/share/fonts/truetype/liberation"
CERT_LINE = "Taught by a Book 1 Certified My Music Box Teacher"

# one hue per page: (band color, light tint for the card header, text pairing)
# Basic-level palette: colorful, but none of the My Music Box brand colors, which are
# reserved for Ambassador Studios. One hue per page: (band, light tint, text pairing).
HUES = {
    "indigo": ("#4C5FD5", "#E7EAFB", "#2B3A9E"),
    "rose": ("#E0617F", "#FBE5EB", "#9B2C48"),
    "tangerine": ("#EE8A3C", "#FDEBDC", "#9A4A0B"),
}
NAVY = "#1F2A44"  # headlines on every page, so the accent color stays a highlight

PAGE_W, PAGE_H = LETTER
MARGIN = 0.7 * inch
BAND_H = 0.18 * inch

INVITE = dict(
    filename="Trial_Class_Invite_Flyer.pdf", hue="indigo", eyebrow="Free trial class",
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
    filename="Trial_Class_Reminder_Flyer.pdf", hue="rose", eyebrow="Trial class reminder",
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


# ----------------------------------- keyboard -----------------------------------

BLACK_AFTER = {0, 1, 3, 4, 5}  # black key after C, D, F, G, A
CHORD = set()  # no highlighted keys: a plain keyboard


def keyboard_keys(n_white, x, y_top, width, height):
    """Yield ('white'|'black', index, x, y_top, w, h) for a flat keyboard drawing."""
    kw = width / n_white
    for i in range(n_white):
        yield "white", i, x + i * kw, y_top, kw, height
    for i in range(n_white - 1):
        if i % 7 in BLACK_AFTER:
            bw = kw * 0.58
            yield "black", i, x + (i + 1) * kw - bw / 2, y_top, bw, height * 0.62


# ------------------------------------ flyers ------------------------------------

CLEAR = colors.Color(1, 1, 1, alpha=0)
FIELD_TEXT = colors.HexColor("#3A3A3A")


def text_field(c, name, x, y, width, height, size=11):
    """A typeable PDF field with no box, so the printed page just shows the line."""
    c.acroForm.textfield(name=name, tooltip=name.replace("_", " ").title(), x=x, y=y,
                         width=width, height=height, borderWidth=0, fillColor=CLEAR,
                         textColor=FIELD_TEXT, fontName="Helvetica", fontSize=size, value="")


class WriteIn(Flowable):
    """A write-in line that is also a typeable field."""

    def __init__(self, name, width, height=22):
        super().__init__()
        self.name, self.width, self.height = name, width, height

    def draw(self):
        self.canv.setStrokeColor(colors.HexColor("#C9C7C4"))
        self.canv.setLineWidth(0.8)
        self.canv.line(0, 0, self.width, 0)
        # form fields use page coordinates, not the table cell's local ones
        x, y = self.canv.absolutePosition(0, 2)
        text_field(self.canv, self.name, x, y, self.width, self.height - 2)

def on_page_for(band, tint, txt):
    def on_page(c, doc):
        c.saveState()
        c.setFillColor(band)
        c.rect(0, PAGE_H - BAND_H, PAGE_W, BAND_H, stroke=0, fill=1)
        # teacher's studio name where the house style has the wordmark
        y = PAGE_H - BAND_H - 0.36 * inch
        c.setStrokeColor(BORDER)
        c.setLineWidth(0.8)
        c.line(PAGE_W - MARGIN - 2.4 * inch, y, PAGE_W - MARGIN, y)
        text_field(c, "studio_name", PAGE_W - MARGIN - 2.4 * inch, y + 2, 2.4 * inch, 20, size=12)
        c.setFont('Sans', 8.5)
        c.setFillColor(MUTED)
        c.drawRightString(PAGE_W - MARGIN, y - 11, "Your studio name")
        c.setStrokeColor(BORDER)
        c.setLineWidth(0.75)
        c.line(MARGIN, 0.55 * inch, PAGE_W - MARGIN, 0.55 * inch)
        c.setFont('Sans', 9)
        c.drawString(MARGIN, 0.38 * inch, CERT_LINE)
        draw_pdf_notes(c, band, txt)
        draw_pdf_keyboard(c, MARGIN, 0.75 * inch + 0.45 * inch, PAGE_W - 2 * MARGIN, 1.15 * inch,
                          band, tint, txt)
        c.restoreState()
    return on_page


# (x, y from the bottom, size, glyph, use accent text color, angle)
PDF_NOTES = [
    (226, 190, 22, 0, False, -8), (282, 212, 30, 1, True, 6), (338, 236, 24, 2, False, -6),
    (398, 252, 34, 1, False, 10), (462, 228, 24, 0, True, -10), (520, 256, 30, 3, False, 4),
    (470, 676, 30, 1, False, 8), (528, 640, 22, 0, True, -8),
]


CARD_BOTTOM_MIN = 318  # the details cards end at or above this height (from the bottom)


def draw_pdf_notes(c, band, txt):
    for x, y, size, g, dark, angle in PDF_NOTES:
        assert y + size < CARD_BOTTOM_MIN or y > 600, f"note at {x},{y} would touch the card"
        c.saveState()
        c.translate(x, y)
        c.rotate(angle)
        c.setFillColor(txt if dark else band)
        c.setFont("Notes", size)
        c.drawString(0, 0, NOTES[g])
        c.restoreState()


def draw_pdf_keyboard(c, x, y_bottom, width, height, band, tint, txt):
    navy = colors.HexColor(NAVY)
    top = y_bottom + height
    for kind, i, kx, _, kw, kh in keyboard_keys(21, x, top, width, height):
        if kind == "white":
            c.setFillColor(tint if i in CHORD else colors.white)
            c.setStrokeColor(colors.HexColor("#CBD0DC"))
            c.setLineWidth(0.8)
            c.roundRect(kx, y_bottom, kw, height, 3, stroke=1, fill=1)
            if i in CHORD:
                c.setFillColor(band)
                c.circle(kx + kw / 2, y_bottom + 12, 4.5, stroke=0, fill=1)
        else:
            c.setFillColor(navy)
            c.roundRect(kx, top - kh, kw, kh, 2.5, stroke=0, fill=1)
    c.setFillColor(band)
    c.rect(x, top, width, 4, stroke=0, fill=1)


def details_card(head, fields, sentence, tint, txt, width):
    header = Table([[Paragraph(head, ParagraphStyle(
        "h", fontName="Sans-Bold", fontSize=13.5, leading=16, textColor=txt))]], colWidths=[width])
    header.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), tint),
        ("LEFTPADDING", (0, 0), (-1, -1), 14), ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
    ]))
    label = ParagraphStyle("l", fontName="Sans-Bold", fontSize=10.8, leading=14, textColor=DARK)
    field_w = width - 1.0 * inch - 24
    rows = [[Paragraph(f, label), WriteIn(f.lower().replace(" ", "_"), field_w)] for f in fields]
    lines = Table(rows, colWidths=[1.0 * inch, width - 1.0 * inch - 24], rowHeights=34)
    lines.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
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


class AccentBar(Flowable):
    def __init__(self, color, width=44, height=4):
        super().__init__()
        self.color, self.width, self.height = color, width, height

    def draw(self):
        self.canv.setFillColor(self.color)
        self.canv.roundRect(0, 0, self.width, self.height, 2, stroke=0, fill=1)


def flyer(spec):
    band, tint, txt = (colors.HexColor(h) for h in HUES[spec["hue"]])
    story = [
        Spacer(1, 0.3 * inch),
        Paragraph(spec["eyebrow"], ParagraphStyle("e", fontName="Sans-Bold", fontSize=11, leading=14,
                                                  textColor=txt, spaceAfter=6)),
        Paragraph(spec["title"], ParagraphStyle("t", fontName="Sans-XBold", fontSize=26, leading=29,
                                                textColor=colors.HexColor(NAVY), spaceAfter=8)),
        AccentBar(band),
        Spacer(1, 10),
        Paragraph(spec["subtitle"], ParagraphStyle("s", fontName="Sans", fontSize=11.5, leading=16,
                                                   textColor=MUTED, spaceAfter=24)),
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
    doc.addPageTemplates([PageTemplate(id="c", frames=[frame], onPage=on_page_for(band, tint, txt))])
    doc.build(story)
    return path


# ---------------------------------- Instagram -----------------------------------

W, H = 1080, 1350
INK, GRAY, RULE, PANEL_HEX = "#3A3A3A", "#6B6B6B", "#E5E4E2", "#F6F5F4"
SIDE = 84


def pf(bold, size, xbold=False):
    name = "Nunito-ExtraBold" if xbold else ("Nunito-Bold" if bold else "Nunito-Regular")
    return ImageFont.truetype(os.path.join(FONTS, f"{name}.ttf"), size)


def note(im, x, y, size, glyph, color, angle):
    f = ImageFont.truetype(NOTE_FONT, size)
    layer = Image.new("L", (size * 2, size * 2), 0)
    ImageDraw.Draw(layer).text((size // 2, size // 4), NOTES[glyph], font=f, fill=255)
    layer = layer.rotate(angle, resample=Image.BICUBIC, expand=False)
    im.paste(Image.new("RGB", layer.size, color), (int(x), int(y)), layer)


# (x, y, size, glyph, use accent text color, angle): around the corner shape and the footer
PNG_NOTES = [(930, H - 120, 48, 1, False, -6)]  # small glyph note beside the footer

# cute notes in the top corner: (center x, center y, size, beamed pair?, use accent text color, angle)
CUTE_NOTES = [(690, 128, 32, False, False, -10), (790, 168, 40, False, False, 8),
              (905, 205, 44, True, True, -6)]


def cute_note(im, cx, cy, s, beamed, color, angle):
    """A chunky note with a round head and thick rounded stem; drawn 4x and scaled down."""
    k = 4
    S = s * k
    size = int(S * 7)
    layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    ox, oy = size * 0.32, size * 0.7  # first head center

    def head(hx, hy):
        d.ellipse((hx - 0.75 * S, hy - 0.6 * S, hx + 0.75 * S, hy + 0.6 * S), fill=color)
    def stem(x, y_top, y_bot):
        w = 0.28 * S
        d.rounded_rectangle((x - w / 2, y_top, x + w / 2, y_bot), radius=w / 2, fill=color)

    sx1 = ox + 0.62 * S
    top1 = oy - 2.2 * S
    stem(sx1, top1, oy - 0.1 * S)
    if beamed:
        ox2, oy2 = ox + 2.0 * S, oy - 0.35 * S
        sx2, top2 = ox2 + 0.62 * S, top1 - 0.35 * S
        stem(sx2, top2, oy2 - 0.1 * S)
        bw = 0.42 * S
        d.polygon([(sx1 - 0.11 * S, top1), (sx2 + 0.11 * S, top2), (sx2 + 0.11 * S, top2 + bw),
                   (sx1 - 0.11 * S, top1 + bw)], fill=color)
        head(ox2, oy2)
    else:  # rounded flag
        # flag hangs from the stem top: the arc's top point sits exactly on the stem
        d.arc((sx1 - 0.85 * S, top1, sx1 + 0.85 * S, top1 + 1.7 * S), 270, 40,
              fill=color, width=int(0.3 * S))
        d.ellipse((sx1 - 0.14 * S, top1 - 0.02 * S, sx1 + 0.16 * S, top1 + 0.28 * S), fill=color)
    head(ox, oy)
    layer = layer.rotate(angle, resample=Image.BICUBIC)
    layer = layer.resize((size // k, size // k), Image.LANCZOS)
    im.paste(layer, (int(cx - size / k * 0.45), int(cy - size / k * 0.55)), layer)


def tw(d, s, f):
    return d.textbbox((0, 0), s, font=f)[2]


def page(hue):
    band, tint, txt = HUES[hue]
    im = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(im)
    d.ellipse((W - 300, -260, W + 260, 300), fill=tint)  # soft corner shape
    d.rectangle((0, 0, W, 18), fill=band)
    d.line((SIDE, H - 118, W - SIDE, H - 118), fill=RULE, width=2)
    d.text((SIDE, H - 88), CERT_LINE, font=pf(False, 28), fill=GRAY)
    for x, y, size, g, dark, angle in PNG_NOTES:
        note(im, x, y, size, g, txt if dark else band, angle)
    for x, y, size, beamed, dark, angle in CUTE_NOTES:
        cute_note(im, x, y, size, beamed, txt if dark else band, angle)
    draw_png_keyboard(d, SIDE, KEYS_TOP, W - 2 * SIDE, KEYS_H, band, tint)
    return im, d, (band, tint, txt)


KEYS_H = 120
KEYS_TOP = H - 118 - 34 - KEYS_H


def draw_png_keyboard(d, x, top, width, height, band, tint):
    d.rectangle((x, top - 8, x + width, top), fill=band)
    for kind, i, kx, ky, kw, kh in keyboard_keys(14, x, top, width, height):
        if kind == "white":
            d.rounded_rectangle((kx, ky, kx + kw, ky + kh), radius=8,
                                fill=tint if i in CHORD else "white", outline="#CBD0DC", width=2)
            if i in CHORD:
                cx, cy = kx + kw / 2, ky + kh - 26
                d.ellipse((cx - 10, cy - 10, cx + 10, cy + 10), fill=band)
        else:
            d.rounded_rectangle((kx, ky, kx + kw, ky + kh), radius=6, fill=NAVY)


def headline(d, y, lines, accent, size=76):
    f = pf(True, size, xbold=True)
    for ln in lines:
        d.text((SIDE, y), ln, font=f, fill=NAVY)
        y += int(size * 1.18)
    d.rounded_rectangle((SIDE, y + 22, SIDE + 88, y + 32), radius=5, fill=accent)
    return y + 36


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
    body_h = 14 + len(body_lines) * (size + 18) + 22
    d.rounded_rectangle((x1, y, x2, y + hh + body_h), radius=28, fill=tint)
    d.rounded_rectangle((x1, y, x1 + 12, y + hh + body_h), radius=6, fill=band)
    d.text((x1 + 40, y + (hh - 40) / 2 + 6), head, font=pf(True, 40), fill=txt)
    ty = y + hh + 14
    for bold, s in body_lines:
        d.text((x1 + 40, ty), s, font=pf(bold, size), fill=NAVY if bold else INK)
        assert x1 + 40 + tw(d, s, pf(bold, size)) < x2 - 24, s
        ty += size + 18
    return y + hh + body_h


def centered_post(fn):
    """Measure the post, then redraw it centered between the top band and the footer."""
    _, end = fn()
    bottom = KEYS_TOP - 36
    assert end <= bottom, f"{fn.__name__} runs into the footer"
    im, _ = fn(140 + (bottom - end) / 2)
    return im


def ig_invite(y0=140):
    im, d, c = page("indigo")
    y = y0
    d.text((SIDE, y), "Free trial class", font=pf(True, 34), fill=c[2])
    y = headline(d, y + 60, ["Come try a", "group piano class!"], c[0])
    d.text((SIDE, y + 10), "For children ages 4 to 7. 30 minutes.", font=pf(False, 36), fill=GRAY)
    y = dot_list(d, y + 100, ["Sing and move to music", "Play first notes on the piano",
                              "Make music with new friends"], c[2])
    y = card(d, y + 34, "Save a spot", [(True, "Send us a message today."),
                                         (False, "Up to 8 children per class.")], c)
    return im, y


def ig_what_happens(y0=140):
    im, d, c = page("tangerine")
    y = y0
    d.text((SIDE, y), "Free trial class", font=pf(True, 34), fill=c[2])
    y = headline(d, y + 60, ["What happens in", "a trial class?"], c[0])
    y = card(d, y + 40, "In 30 minutes, your child will", [
        (True, "1.  Sing first"), (False, "      Sing the song before playing it."),
        (True, "2.  Move to the music"), (False, "      Feel the rhythm in the body."),
        (True, "3.  Play the piano"), (False, "      First notes, with new friends.")], c, size=32)
    d.text((SIDE, y + 36), "Parents watch, then stay for a short talk.", font=pf(False, 34), fill=GRAY)
    d.text((SIDE, y + 96), "Message us to save a spot.", font=pf(True, 36), fill=c[2])
    return im, y + 140


def ig_last_spots(y0=140):
    im, d, c = page("rose")
    y = y0
    d.text((SIDE, y), "Free trial class", font=pf(True, 34), fill=c[2])
    y = headline(d, y + 60, ["Only a few", "spots left!"], c[0], size=96)
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
