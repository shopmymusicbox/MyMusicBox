#!/usr/bin/env python3
"""Kit pages that wrap the flyers and posts:

- basic/Launch_Kit_Overview.pdf: overview for the Basic Studio kit, in the basic style
- basic/Instagram_Captions.pdf: captions in the basic style
- ambassador/Instagram_Captions.pdf: captions in the cloud-and-balloon (Welcome Flyer) style
"""

import io
import os
import re

from pypdf import PdfReader, PdfWriter
from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import simpleSplit
from reportlab.pdfgen import canvas
from reportlab.platypus import Frame, Paragraph

import build_basic_house_style as basic  # registers Nunito as Sans / Sans-Bold / Sans-XBold
from build_launch_kit_flyer import COMMUNITY, KIT, STEPS
from build_payback_flyer import (TEMPLATE, BLUE, DARK as CLOUD_DARK, MUTED as CLOUD_MUTED,
                                 LEFT, RIGHT, COVER_TOP, COVER_BOTTOM, strip_welcome_text)

HERE = os.path.dirname(os.path.abspath(__file__))
CAPTIONS_MD = os.path.join(HERE, "instagram", "captions.md")
LOGO = os.path.join(HERE, "assets", "mymusicbox_logo.png")

BAND, TINT, TXT = (colors.HexColor(h) for h in basic.HUES["indigo"])
NAVY = colors.HexColor(basic.NAVY)
GRAY = colors.HexColor("#5E6577")
RULE = colors.HexColor("#E5E4E2")
PAGE_W, PAGE_H = LETTER
M = 50  # side margin


# ----------------------------------- captions -----------------------------------

def caption_items():
    """(kind, text) pairs from captions.md: 'h' heading, 'li' list item, 'p' paragraph."""
    md = open(CAPTIONS_MD, encoding="utf-8").read().split("\n---\n", 1)[1]
    for k, v in {"📅": "Date:", "🕒": "Time:", "📍": "Place:", "1️⃣": "1.", "2️⃣": "2.", "3️⃣": "3."}.items():
        md = md.replace(k, v)
    md = re.sub(r"[\U0001F300-\U0001FAFF☀-➿️]", "", md)
    for line in md.splitlines():
        line = line.strip()
        if not line or line == "---":
            continue
        line = line.replace("&", "&amp;").replace("<", "&lt;")
        line = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", line)
        line = re.sub(r"`(.+?)`", r"\1", line)
        if line.startswith("## "):
            yield "h", line[3:]
        elif line.startswith("- "):
            yield "li", "&#8226; " + line[2:]
        else:
            yield "p", line


def caption_flowables(title_style, intro_style, head_style, body_style):
    out = [Paragraph("Instagram captions", title_style),
           Paragraph("Replace everything in [square brackets] with your own details before you post. "
                     "Use the separate post images, with one caption for each post.", intro_style)]
    for kind, text in caption_items():
        out.append(Paragraph(text, head_style if kind == "h" else body_style))
    return out


def flow_onto_pages(flowables, page_size, frame_box, decorate):
    """Lay flowables into frame_box on as many pages as needed; decorate(c) draws each page."""
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=page_size)
    pending = list(flowables)
    while pending:
        decorate(c)
        Frame(*frame_box, leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0).addFromList(pending, c)
        c.showPage()
    c.save()
    buf.seek(0)
    return PdfReader(buf)


def ambassador_captions():
    page_w, page_h = (float(v) for v in PdfReader(TEMPLATE).pages[0].mediabox[2:])
    title = ParagraphStyle("t", fontName="Fredoka-SemiBold", fontSize=22, leading=27, textColor=BLUE,
                           alignment=1, spaceAfter=4)
    intro = ParagraphStyle("i", fontName="Inter-Regular", fontSize=9.5, leading=13.5, textColor=CLOUD_MUTED,
                           alignment=1, spaceAfter=8)
    head = ParagraphStyle("h", fontName="Fredoka-SemiBold", fontSize=13, leading=16, textColor=BLUE,
                          spaceBefore=10, spaceAfter=3)
    body = ParagraphStyle("b", fontName="Inter-Regular", fontSize=9.3, leading=13, textColor=CLOUD_DARK,
                          spaceAfter=2.5)

    def white_out(c):
        c.setFillColor(colors.white)
        c.rect(40, page_h - COVER_BOTTOM, page_w - 80, COVER_BOTTOM - COVER_TOP, stroke=0, fill=1)

    overlay = flow_onto_pages(caption_flowables(title, intro, head, body), (page_w, page_h),
                              (LEFT, page_h - COVER_BOTTOM + 4, RIGHT - LEFT, COVER_BOTTOM - COVER_TOP - 10),
                              white_out)
    out = PdfWriter()
    for ov in overlay.pages:
        tpl = PdfWriter(clone_from=TEMPLATE)
        page = tpl.pages[0]
        strip_welcome_text(tpl, page)
        page.merge_page(ov)
        out.add_page(page)
    path = os.path.join(HERE, "ambassador", "Instagram_Captions.pdf")
    with open(path, "wb") as f:
        out.write(f)
    return path, len(out.pages)


# --------------------------------- basic pages ----------------------------------

def basic_frame(c, footer, notes=True):
    c.setFillColor(BAND)
    c.rect(0, PAGE_H - 13, PAGE_W, 13, stroke=0, fill=1)
    for x, y, s, beamed, dark, angle in ([] if not notes else [(470, 700, 12, False, False, 8), (520, 724, 10, False, True, -8),
                                         (545, 680, 11, True, False, -4)]):
        basic.draw_cute_note_pdf(c, x, y, s, beamed, TXT if dark else BAND, angle)
    c.setStrokeColor(RULE)
    c.setLineWidth(0.75)
    c.line(M, 46, PAGE_W - M, 46)
    # My Music Box logo and name on the left, kit name on the right
    c.drawImage(LOGO, M, 18, width=26, height=26 * 418 / 471, mask="auto")
    c.setFillColor(NAVY)
    c.setFont("Sans-Bold", 10)
    c.drawString(M + 32, 27, "My Music Box Academy")
    c.setFillColor(GRAY)
    c.setFont("Sans", 9)
    c.drawRightString(PAGE_W - M, 27, footer)


def wrapped(c, text, font, size, x, top, width, leading, color):
    c.setFillColor(color)
    c.setFont(font, size)
    lines = simpleSplit(text, font, size, width)
    for i, ln in enumerate(lines):
        c.drawString(x, PAGE_H - (top + i * leading), ln)
    return top + (len(lines) - 1) * leading


def basic_overview():
    path = os.path.join(HERE, "basic", "Launch_Kit_Overview.pdf")
    c = canvas.Canvas(path, pagesize=LETTER)
    c.setTitle("Group Class Launch Kit: Basic Studio")
    basic_frame(c, "My Music Box Group Piano Launch Kit: Basic Studio")
    width = PAGE_W - 2 * M

    def Y(top):
        return PAGE_H - top

    c.setFillColor(TXT)
    c.setFont("Sans-Bold", 11)
    c.drawString(M, Y(64), "Basic Studio")
    c.setFillColor(NAVY)
    c.setFont("Sans-XBold", 28)
    c.drawString(M, Y(96), "Group Class Launch Kit")
    c.setFillColor(BAND)
    c.roundRect(M, Y(110), 44, 4, 2, stroke=0, fill=1)
    c.setFillColor(GRAY)
    c.setFont("Sans", 11.5)
    c.drawString(M, Y(132), "From certification to your first full group class. Included with your Book 1 training.")

    def heading(top, text):
        c.setFillColor(NAVY)
        c.setFont("Sans-XBold", 14)
        c.drawString(M, Y(top), text)

    # community class
    heading(166, "After your Book 1 certification")
    title, body = COMMUNITY
    lines = simpleSplit(body, "Sans", 10, width - 36)
    top, h = 178, 34 + len(lines) * 14
    c.setFillColor(TINT)
    c.roundRect(M, Y(top + h), width, h, 10, stroke=0, fill=1)
    c.setFillColor(BAND)
    c.roundRect(M, Y(top + h), 6, h, 3, stroke=0, fill=1)
    c.setFillColor(TXT)
    c.setFont("Sans-Bold", 11.5)
    c.drawString(M + 20, Y(top + 20), title[0].upper() + title[1:])
    wrapped(c, body, "Sans", 10, M + 20, top + 37, width - 36, 14, NAVY)

    # three weeks
    after = top + h + 24
    c.setFillColor(TXT)
    c.setFont("Sans-Bold", 10.5)
    c.drawString(M, Y(after), "Then, over three weeks")
    gap, wt = 14, after + 10
    tw = (width - 2 * gap) / 3
    wh = 112
    for i, (week, head, text, _, _) in enumerate(STEPS):
        x = M + i * (tw + gap)
        c.setStrokeColor(BAND)
        c.setLineWidth(1.5)
        c.setFillColor(colors.white)
        c.roundRect(x, Y(wt + wh), tw, wh, 10, stroke=1, fill=1)
        c.setFillColor(TINT)
        c.roundRect(x + 1, Y(wt + 27), tw - 2, 26, 9, stroke=0, fill=1)
        c.rect(x + 1, Y(wt + 27), tw - 2, 10, stroke=0, fill=1)
        c.setFillColor(TXT)
        c.setFont("Sans-Bold", 11.5)
        c.drawCentredString(x + tw / 2, Y(wt + 18), week)
        end = wrapped(c, head, "Sans-Bold", 10.5, x + 12, wt + 45, tw - 24, 13.5, NAVY)
        last = wrapped(c, text, "Sans", 9.8, x + 12, end + 17, tw - 24, 13, GRAY)
        assert last + 8 < wt + wh, f"{week} text runs past its card"

    # kit list
    kt = wt + wh + 30
    heading(kt, "What's in your launch kit")
    pw, ph = (width - 14) / 2, 44
    for i, (head, desc, _) in enumerate(KIT):
        x = M + (i % 2) * (pw + 14)
        t = kt + 12 + (i // 2) * (ph + 10)
        c.setFillColor(colors.HexColor("#F7F8FC"))
        c.setStrokeColor(colors.HexColor("#E3E6F2"))
        c.setLineWidth(1)
        c.roundRect(x, Y(t + ph), pw, ph, 8, stroke=1, fill=1)
        c.setFillColor(BAND)
        c.roundRect(x, Y(t + ph), 5, ph, 2.5, stroke=0, fill=1)
        c.setFillColor(NAVY)
        c.setFont("Sans-Bold", 10.5)
        c.drawString(x + 16, Y(t + 18), head)
        c.setFillColor(GRAY)
        c.setFont("Sans", 9.5)
        c.drawString(x + 16, Y(t + 33), desc)

    # trial class video
    vt = kt + 12 + 2 * ph + 10 + 16
    vh = 48
    c.setFillColor(TINT)
    c.roundRect(M, Y(vt + vh), width, vh, 10, stroke=0, fill=1)
    c.setFillColor(TXT)
    c.setFont("Sans-Bold", 11)
    c.drawString(M + 16, Y(vt + 20), "Trial class video")
    c.setFillColor(NAVY)
    c.setFont("Sans", 10)
    c.drawString(M + 16, Y(vt + 36), "A demo of a real 30 minute trial class, so you can see exactly how it "
                                     "runs before you teach your own.")

    # how to use
    ht = vt + vh + 28
    heading(ht, "How to use this kit")
    y = ht + 18
    for line in ["Open this file in any PDF reader (Adobe Reader, Preview, Chrome or Edge).",
                 "On a flyer, click a line and type your studio name, date, time, place and contact.",
                 "Print the flyer, or save the file and attach it to an email.",
                 "For Instagram, use the separate post images and copy the captions on the last pages."]:
        c.setFillColor(BAND)
        c.circle(M + 4, Y(y - 3.5), 2.4, stroke=0, fill=1)
        c.setFillColor(NAVY)
        c.setFont("Sans", 10.5)
        c.drawString(M + 14, Y(y), line)
        y += 17
    assert y < PAGE_H - 60, "overview runs into the footer"
    c.showPage()
    c.save()
    return path


def basic_captions():
    title = ParagraphStyle("t", fontName="Sans-XBold", fontSize=26, leading=31, textColor=NAVY, spaceAfter=4)
    intro = ParagraphStyle("i", fontName="Sans", fontSize=11, leading=15, textColor=GRAY, spaceAfter=10)
    head = ParagraphStyle("h", fontName="Sans-Bold", fontSize=13.5, leading=17, textColor=TXT,
                          spaceBefore=9, spaceAfter=3)
    body = ParagraphStyle("b", fontName="Sans", fontSize=10.3, leading=14, textColor=NAVY, spaceAfter=2)
    r = flow_onto_pages(caption_flowables(title, intro, head, body), LETTER,
                        (M, 66, PAGE_W - 2 * M, PAGE_H - 66 - 50),
                        lambda c: basic_frame(c, "My Music Box Group Piano Launch Kit: Basic Studio", notes=False))
    path = os.path.join(HERE, "basic", "Instagram_Captions.pdf")
    out = PdfWriter()
    for p in r.pages:
        out.add_page(p)
    with open(path, "wb") as f:
        out.write(f)
    return path, len(out.pages)


if __name__ == "__main__":
    print(basic_overview())
    print(*basic_captions())
    print(*ambassador_captions())
