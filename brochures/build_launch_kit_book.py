#!/usr/bin/env python3
"""Collect the launch kit into two PDFs: one for Basic Studios, one for Ambassador Studios.

Run the individual builders first; this only collects their output.
"""

import io
import os
import re

from PIL import Image
from pypdf import PdfReader, PdfWriter
from pypdf.generic import ArrayObject, BooleanObject, DictionaryObject, NameObject, TextStringObject
from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer

from build_brochures import DARK, MUTED, PURPLE, PURPLE_TXT, make_on_page

HERE = os.path.dirname(os.path.abspath(__file__))
MARGIN = 0.7 * inch

BASIC = [
    ("basic/Trial_Class_Invite_Flyer.pdf", "basic_invite"),
    ("basic/Trial_Class_Reminder_Flyer.pdf", "basic_reminder"),
    ("basic/instagram/post1_invite.png", None),
    ("basic/instagram/post2_what_happens.png", None),
    ("basic/instagram/post3_last_spots.png", None),
]
AMBASSADOR = [
    ("ambassador/Ambassador_Trial_Class_Invite_Flyer.pdf", "ambassador_invite"),
    ("ambassador/Ambassador_Trial_Class_Reminder_Flyer.pdf", "ambassador_reminder"),
    ("ambassador/instagram/post1_invite.png", None),
    ("ambassador/instagram/post2_what_happens.png", None),
    ("ambassador/instagram/post3_last_spots.png", None),
]

H1 = ParagraphStyle("h1", fontName="Sans-Bold", fontSize=26, leading=31, textColor=DARK, spaceAfter=8)
H2 = ParagraphStyle("h2", fontName="Sans-Bold", fontSize=14, leading=18, textColor=PURPLE_TXT,
                    spaceBefore=14, spaceAfter=6)
BODY = ParagraphStyle("b", fontName="Sans", fontSize=11, leading=16, textColor=DARK, spaceAfter=4)
SUB = ParagraphStyle("s", fontName="Sans", fontSize=12, leading=17, textColor=MUTED, spaceAfter=18)


def text_pages(flowables):
    buf = io.BytesIO()
    doc = BaseDocTemplate(buf, pagesize=LETTER, leftMargin=MARGIN, rightMargin=MARGIN,
                          topMargin=MARGIN + 0.4 * inch, bottomMargin=0.85 * inch)
    frame = Frame(MARGIN, 0.85 * inch, LETTER[0] - 2 * MARGIN, LETTER[1] - MARGIN - 0.4 * inch - 0.85 * inch)
    doc.addPageTemplates([PageTemplate(frames=[frame], onPage=make_on_page(PURPLE))])
    doc.build(flowables)
    buf.seek(0)
    return PdfReader(buf)


def cover(variant):
    if variant == "basic":
        title = "My Music Box Group Piano Launch Kit: Basic Studio"
        who = ("For every licensed My Music Box teacher. These pieces use a neutral look, so your own "
               "studio name comes first. The only brand mention is \"Taught by a Book 1 Certified "
               "My Music Box Teacher\".")
    else:
        title = "My Music Box Group Piano Launch Kit: Ambassador Studio"
        who = ("For Ambassador Studios only. These pieces use the My Music Box color palette, fonts and "
               "artwork, which are part of the Ambassador Studio partnership.")
    items = [
        ("Launch kit overview", "Your path from training to your first full group class."),
        ("Trial class invite", "A flyer to post or email to families."),
        ("Trial class reminder", "A flyer to send to families who signed up."),
        ("Three Instagram posts", "Invite, what happens in a trial class, and last spots."),
        ("Instagram captions", "A ready-to-edit caption for each post."),
    ]
    f = [Spacer(1, 0.6 * inch), Paragraph(title, H1), Paragraph(who, SUB), Paragraph("What's inside", H2)]
    for i, (head, desc) in enumerate(items, 1):
        f.append(Paragraph(f"<b>{i}. {head}.</b> {desc}", BODY))
    f += [Paragraph("How to use the flyers", H2),
          Paragraph("Open this file in any PDF reader (Adobe Reader, Preview, Chrome or Edge). Click a line "
                    "on a flyer and type your studio name, date, time, place and contact. Then print the page, "
                    "or save the file and attach it to an email.", BODY),
          Paragraph("To post on Instagram, use the separate post images, and copy the matching caption from "
                    "the last pages of this kit.", BODY)]
    return text_pages(f)


def divider(title, lines):
    f = [Spacer(1, 2.4 * inch), Paragraph(title, H1)]
    f += [Paragraph(x, SUB if i == 0 else BODY) for i, x in enumerate(lines)]
    return text_pages(f)


def captions():
    md = open(os.path.join(HERE, "instagram", "captions.md"), encoding="utf-8").read()
    md = md.split("\n---\n", 1)[1]  # skip the intro, the cover already explains it
    swaps = {"📅": "Date:", "🕒": "Time:", "📍": "Place:", "1️⃣": "1.", "2️⃣": "2.", "3️⃣": "3."}
    for k, v in swaps.items():
        md = md.replace(k, v)
    md = re.sub(r"[\U0001F300-\U0001FAFF☀-➿️]", "", md)
    f = [Paragraph("Instagram captions", H1),
         Paragraph("Replace everything in [square brackets] with your own details before you post.", SUB)]
    for line in md.splitlines():
        line = line.strip()
        if not line or line == "---":
            continue
        line = line.replace("&", "&amp;").replace("<", "&lt;")
        line = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", line)
        line = re.sub(r"`(.+?)`", r"\1", line)
        if line.startswith("## "):
            f.append(Paragraph(line[3:], H2))
        elif line.startswith("- "):
            f.append(Paragraph("&#8226; " + line[2:], BODY))
        else:
            f.append(Paragraph(line, BODY))
    return text_pages(f)


def image_page(path):
    buf = io.BytesIO()
    Image.open(path).convert("RGB").save(buf, "PDF", resolution=150)
    buf.seek(0)
    return PdfReader(buf)


def add(writer, reader, prefix=None):
    """Append a PDF; give its form fields a unique prefix so two flyers never share a field."""
    start = len(writer.pages)
    writer.append(reader)
    if not prefix:
        return
    for page in writer.pages[start:]:
        for ref in page.get("/Annots", []):
            annot = ref.get_object()
            if annot.get("/FT") == "/Tx":
                annot[NameObject("/T")] = TextStringObject(f"{prefix}_{annot['/T']}")


def build(variant):
    files = BASIC if variant == "basic" else AMBASSADOR
    name = "Basic Studio" if variant == "basic" else "Ambassador Studio"
    out = os.path.join(HERE, f"My Music Box Group Piano Launch Kit - {name}.pdf")
    w = PdfWriter()
    add(w, cover(variant))
    add(w, PdfReader(os.path.join(HERE, "MyMusicBox_Group_Class_Launch_Kit_Flyer.pdf")))
    for rel, prefix in files:
        path = os.path.join(HERE, rel)
        add(w, image_page(path) if rel.endswith(".png") else PdfReader(path), prefix)
    add(w, captions())

    # one form for the whole file, listing every typeable field
    fields = ArrayObject(ref for page in w.pages for ref in page.get("/Annots", [])
                         if ref.get_object().get("/FT") == "/Tx")
    dr = PdfReader(os.path.join(HERE, "basic/Trial_Class_Invite_Flyer.pdf")).trailer["/Root"]["/AcroForm"]["/DR"]
    w._root_object[NameObject("/AcroForm")] = w._add_object(DictionaryObject({
        NameObject("/Fields"): fields,
        NameObject("/DA"): TextStringObject("/Helv 0 Tf 0 g"),
        NameObject("/DR"): dr.get_object().clone(w),
        NameObject("/NeedAppearances"): BooleanObject(True),
    }))
    w.add_metadata({"/Title": f"My Music Box Group Piano Launch Kit: {name}", "/Author": "MyMusicBox Academy"})
    with open(out, "wb") as f:
        w.write(f)
    return out, len(w.pages), len(fields)


if __name__ == "__main__":
    for variant in ("basic", "ambassador"):
        print(*build(variant))
