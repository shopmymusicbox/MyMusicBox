#!/usr/bin/env python3
"""Ambassador Studio trial class flyers (invite and reminder) in the Welcome Flyer style.

These use the My Music Box palette, fonts, artwork and logo, which are reserved for
Ambassador Studios. Basic licensed teachers get build_basic_trial_materials.py instead.

Teachers print them and write their own date, time, place and contact on the lines.
"""

import io
import os

from pypdf import PdfReader, PdfWriter
from reportlab.lib import colors
from reportlab.lib.utils import simpleSplit
from reportlab.pdfgen import canvas

from build_payback_flyer import (HERE, TEMPLATE, BLUE, DARK, MUTED, NOTE_FILL, NOTE_LINE,
                                 LEFT, RIGHT, COVER_TOP, COVER_BOTTOM, strip_welcome_text)
from build_launch_kit_flyer import (LAVENDER, LAVENDER_TXT, TEAL, TEAL_TXT, ORANGE, ORANGE_TXT,
                                    rounded_top_band)

PLUM = colors.HexColor("#542E57")
LINE = colors.HexColor("#B9C9D6")

INVITE = dict(
    filename="ambassador/Ambassador_Trial_Class_Invite_Flyer.pdf",
    title="Come try a group piano class!",
    subtitle="A free 30 minute trial class for children ages 4 to 7",
    cards=[
        ("Your child will", ["Sing and move to music", "Play first notes on the piano",
                             "Make music with new friends"], LAVENDER, LAVENDER_TXT),
        ("Parents will", ["Watch the whole class", "Stay for a short talk after class",
                          "Get your questions answered"], TEAL, TEAL_TXT),
        ("Good to know", ["Up to 8 children", "Parents stay and watch",
                          "Free, no commitment"], ORANGE, ORANGE_TXT),
    ],
    details_title="Trial class details",
    fields=["Studio", "Date", "Time", "Place", "Teacher", "Save a spot"],
    closing="Spots are limited. Save yours today!",
    cards_first=True,
)

REMINDER = dict(
    filename="ambassador/Ambassador_Trial_Class_Reminder_Flyer.pdf",
    title="See you at the trial class!",
    subtitle="We can't wait to make music with your child.",
    cards=[
        ("Before you come", ["Arrive 5 minutes early", "Bathroom break before class",
                             "Comfortable clothes"], LAVENDER, LAVENDER_TXT),
        ("What happens", ["Trial class, 30 minutes", "A short parent talk after class",
                          "Time for your questions"], TEAL, TEAL_TXT),
        ("Please remember", ["One parent stays for the whole visit", "Bring your questions",
                             "Tell us if your plans change"], ORANGE, ORANGE_TXT),
    ],
    details_title="Your trial class",
    fields=["Studio", "Date", "Time", "Place", "Contact"],
    closing="Questions? Contact your teacher anytime.",
    cards_first=False,
)

CARD_LEADING = 13


def card_height(items, inner_w):
    lines = sum(len(simpleSplit(it, "Inter-Regular", 9.5, inner_w)) for it in items)
    return 26 + 14 + lines * CARD_LEADING + (len(items) - 1) * 6 + 12


def draw_cards(c, page_h, top, cards):
    width = RIGHT - LEFT
    gap = 14
    tw = (width - 2 * gap) / 3
    inner_w = tw - 34
    th = max(card_height(items, inner_w) for _, items, _, _ in cards)
    for i, (head, items, accent, accent_txt) in enumerate(cards):
        x = LEFT + i * (tw + gap)
        c.setLineWidth(2)
        c.setStrokeColor(accent)
        c.setFillColor(colors.white)
        c.roundRect(x, page_h - (top + th), tw, th, 10, stroke=1, fill=1)
        c.setFillColor(accent)
        rounded_top_band(c, x, page_h - top, tw, 26, 10)
        c.setFillColor(accent_txt)
        c.setFont("Fredoka-SemiBold", 12)
        c.drawCentredString(x + tw / 2, page_h - (top + 17), head)
        y = top + 26 + 18
        for it in items:
            c.setFillColor(accent_txt if accent_txt != LAVENDER_TXT else PLUM)
            c.circle(x + 15, page_h - (y - 3.5), 2.2, stroke=0, fill=1)
            c.setFillColor(DARK)
            c.setFont("Inter-Regular", 9.5)
            for line in simpleSplit(it, "Inter-Regular", 9.5, inner_w):
                c.drawString(x + 22, page_h - y, line)
                y += CARD_LEADING
            y += 6
        assert y - 6 + 4 <= top + th, f"{head} runs past its card"
    return top + th


def draw_details(c, page_h, top, title, fields):
    width = RIGHT - LEFT
    row = 31
    h = 34 + len(fields) * row + 4
    c.setFillColor(NOTE_FILL)
    c.setStrokeColor(NOTE_LINE)
    c.setLineWidth(1)
    c.roundRect(LEFT, page_h - (top + h), width, h, 10, stroke=1, fill=1)
    c.setFillColor(BLUE)
    c.setFont("Fredoka-SemiBold", 14)
    c.drawString(LEFT + 16, page_h - (top + 24), title)
    c.setStrokeColor(LINE)
    for i, f in enumerate(fields):
        y = top + 34 + (i + 1) * row - 8
        c.setFillColor(DARK)
        c.setFont("Inter-Bold", 10.5)
        c.drawString(LEFT + 16, page_h - y, f)
        c.setLineWidth(0.8)
        c.line(LEFT + 100, page_h - (y + 3), RIGHT - 16, page_h - (y + 3))
        c.acroForm.textfield(name=f.lower().replace(" ", "_"), tooltip=f, x=LEFT + 100,
                             y=page_h - (y + 3) + 2, width=RIGHT - 16 - (LEFT + 100), height=18,
                             borderWidth=0, fillColor=colors.Color(1, 1, 1, alpha=0),
                             textColor=DARK, fontName="Helvetica", fontSize=11, value="")
    return top + h


def build_overlay(page_w, page_h, spec):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(page_w, page_h))
    c.setFillColor(colors.white)
    c.rect(40, page_h - COVER_BOTTOM, page_w - 80, COVER_BOTTOM - COVER_TOP, stroke=0, fill=1)

    cx = page_w / 2
    c.setFillColor(BLUE)
    c.setFont("Fredoka-SemiBold", 25)
    c.drawCentredString(cx, page_h - 226, spec["title"])
    c.setFillColor(MUTED)
    c.setFont("Inter-Regular", 11)
    c.drawCentredString(cx, page_h - 249, spec["subtitle"])

    y = 272
    if spec["cards_first"]:
        y = draw_cards(c, page_h, y, spec["cards"]) + 28
        y = draw_details(c, page_h, y, spec["details_title"], spec["fields"]) + 40
    else:
        y = draw_details(c, page_h, y, spec["details_title"], spec["fields"]) + 28
        y = draw_cards(c, page_h, y, spec["cards"]) + 40

    assert y <= COVER_BOTTOM - 6, f"{spec['filename']}: content runs to {y}"
    c.setFillColor(PLUM)
    c.setFont("Fredoka-SemiBold", 15)
    c.drawCentredString(cx, page_h - y, spec["closing"])
    c.showPage()
    c.save()
    buf.seek(0)
    return PdfReader(buf).pages[0]


def keep_form_fields(out, page, overlay):
    """merge_page copies the typeable fields onto the page; register them as the form."""
    from pypdf.generic import ArrayObject, BooleanObject, NameObject
    from pypdf.generic import DictionaryObject
    src = overlay.pdf.trailer["/Root"]["/AcroForm"].get_object()
    fields = ArrayObject(x for x in page["/Annots"] if x.get_object().get("/FT") == "/Tx")
    form = DictionaryObject({
        NameObject("/Fields"): fields,
        NameObject("/DA"): src["/DA"],
        NameObject("/DR"): src["/DR"].get_object().clone(out),
        NameObject("/NeedAppearances"): BooleanObject(True),
    })
    out._root_object[NameObject("/AcroForm")] = out._add_object(form)


def build(spec):
    out = PdfWriter(clone_from=TEMPLATE)
    page = out.pages[0]
    strip_welcome_text(out, page)
    overlay = build_overlay(float(page.mediabox.width), float(page.mediabox.height), spec)
    page.merge_page(overlay)
    keep_form_fields(out, page, overlay)
    out.add_metadata({"/Title": spec["title"], "/Author": "MyMusicBox Academy"})
    path = os.path.join(HERE, spec["filename"])
    with open(path, "wb") as f:
        out.write(f)
    return path


if __name__ == "__main__":
    for spec in (INVITE, REMINDER):
        print(build(spec))
