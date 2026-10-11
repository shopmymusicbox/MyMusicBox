#!/usr/bin/env python3
"""My Music Box one-page brochures: training payback (Region 1, Region 2) and group class launch kit."""

import os

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle, HRFlowable

FONT_DIR = '/usr/share/fonts/truetype/liberation'
pdfmetrics.registerFont(TTFont('Sans', f'{FONT_DIR}/LiberationSans-Regular.ttf'))
pdfmetrics.registerFont(TTFont('Sans-Bold', f'{FONT_DIR}/LiberationSans-Bold.ttf'))

DARK = colors.HexColor('#3A3A3A')
MUTED = colors.HexColor('#6B6B6B')
BORDER = colors.HexColor('#E5E4E2')
PANEL = colors.HexColor('#F6F5F4')
PURPLE1, PURPLE1_TXT = colors.HexColor('#E0CBE2'), colors.HexColor('#5F3762')
PURPLE, PURPLE_TXT = colors.HexColor('#B683BA'), colors.HexColor('#542E57')
GREEN, GREEN_TXT = colors.HexColor('#C1D83F'), colors.HexColor('#647312')
ORANGE, ORANGE_TXT = colors.HexColor('#FAD294'), colors.HexColor('#845100')
TEAL, TEAL_TXT = colors.HexColor('#4AC3D4'), colors.HexColor('#15646F')

PAGE_W, PAGE_H = LETTER
MARGIN = 0.7 * inch
BAND_H = 0.18 * inch
OUT_DIR = os.path.dirname(os.path.abspath(__file__))


def make_on_page(band_color):
    def on_page(c, doc):
        c.saveState()
        c.setFillColor(band_color)
        c.rect(0, PAGE_H - BAND_H, PAGE_W, BAND_H, stroke=0, fill=1)
        c.setFont('Sans-Bold', 10)
        c.setFillColor(MUTED)
        c.drawRightString(PAGE_W - MARGIN, PAGE_H - BAND_H - 0.3 * inch, "MyMusicBox Academy")
        c.setStrokeColor(BORDER)
        c.setLineWidth(0.75)
        c.line(MARGIN, 0.55 * inch, PAGE_W - MARGIN, 0.55 * inch)
        c.setFont('Sans', 9)
        c.setFillColor(MUTED)
        c.drawString(MARGIN, 0.38 * inch, "Teach with joy, teach with clarity.")
        c.restoreState()
    return on_page


def bullet_line(text, accent_txt, size=10.8):
    bullet = Paragraph("&#9679;", ParagraphStyle("bd", fontName="Sans-Bold", fontSize=size - 1,
                                                   textColor=accent_txt, leading=size + 5))
    label = Paragraph(text, ParagraphStyle("bt", fontName="Sans-Bold", fontSize=size,
                                            leading=size + 3.5, textColor=DARK))
    return bullet, label


def plain_bullet_column(subhead, items, footer, accent_txt, width):
    rows = [[Paragraph(subhead, ParagraphStyle(
        "pch", fontName="Sans-Bold", fontSize=12.5, leading=15, textColor=accent_txt))]]
    rows.append([Spacer(1, 10)])
    bullet_w = 0.2 * inch
    for it in items:
        b, l = bullet_line(it, accent_txt)
        cell = Table([[b, l]], colWidths=[bullet_w, width - bullet_w])
        cell.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 11),
        ]))
        rows.append([cell])
    rows.append([Spacer(1, 6)])
    rows.append([Paragraph(footer, ParagraphStyle(
        "ft", fontName="Sans", fontSize=10, leading=14, textColor=MUTED))])
    t = Table(rows, colWidths=[width])
    t.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    return t


def chart_card(header_title, top_items, full_sentences, accent, accent_txt, width):
    header = Table([[Paragraph(header_title, ParagraphStyle(
        "lh", fontName="Sans-Bold", fontSize=13.5, leading=16, textColor=accent_txt))]],
        colWidths=[width])
    header.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), accent),
        ("LEFTPADDING", (0, 0), (-1, -1), 14), ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
    ]))

    body_rows = [[Spacer(1, 8)]]
    bullet_w = 0.2 * inch
    for it in top_items:
        b, l = bullet_line(it, accent_txt)
        cell = Table([[b, l]], colWidths=[bullet_w, width - bullet_w - 24])
        cell.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
        ]))
        body_rows.append([cell])

    for sentence in full_sentences:
        p = Paragraph(sentence, ParagraphStyle("note", fontName="Sans", fontSize=10.8,
                                                leading=15.3, textColor=DARK))
        body_rows.append([p])
        body_rows.append([Spacer(1, 9)])

    body = Table(body_rows, colWidths=[width - 24])
    body.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PANEL),
        ("LEFTPADDING", (0, 0), (-1, -1), 12), ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    body_wrap = Table([[body]], colWidths=[width])
    body_wrap.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("BACKGROUND", (0, 0), (-1, -1), PANEL),
    ]))

    outer = Table([[header], [body_wrap]], colWidths=[width])
    outer.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1, BORDER),
        ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    return outer


def build(filename, title, subtitle, left, right, closing, band_color):
    story = [
        Paragraph(title, ParagraphStyle("title", fontName="Sans-Bold", fontSize=23, leading=27,
                                        textColor=DARK, spaceAfter=6)),
        Paragraph(subtitle, ParagraphStyle("sub", fontName="Sans", fontSize=11.5, leading=16,
                                           textColor=MUTED, spaceAfter=22)),
    ]
    LEFT_W, RIGHT_W, GAP = 2.5 * inch, 4.1 * inch, 20
    grid = Table([[plain_bullet_column(*left, LEFT_W), chart_card(*right, RIGHT_W)]],
                 colWidths=[LEFT_W + GAP, RIGHT_W])
    grid.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LINEAFTER", (0, 0), (0, 0), 1, BORDER),
        ("LEFTPADDING", (0, 0), (0, 0), 0), ("RIGHTPADDING", (0, 0), (0, 0), GAP),
        ("LEFTPADDING", (1, 0), (1, 0), GAP), ("RIGHTPADDING", (1, 0), (1, 0), 0),
    ]))
    story += [grid, Spacer(1, 16), HRFlowable(width="100%", thickness=0.75, color=BORDER, spaceAfter=8)]
    for line in closing:
        story.append(Paragraph(line, ParagraphStyle("foot", fontName="Sans", fontSize=10.3,
                                                    leading=14.5, textColor=MUTED, spaceAfter=4)))

    path = os.path.join(OUT_DIR, filename)
    doc = BaseDocTemplate(path, pagesize=LETTER, leftMargin=MARGIN, rightMargin=MARGIN,
                          topMargin=MARGIN + BAND_H, bottomMargin=0.75 * inch,
                          title="MyMusicBox Academy", author="MyMusicBox Academy")
    frame = Frame(MARGIN, 0.75 * inch, PAGE_W - 2 * MARGIN, PAGE_H - MARGIN - BAND_H - 0.75 * inch, id="c")
    doc.addPageTemplates([PageTemplate(id="c", frames=[frame], onPage=make_on_page(band_color))])
    doc.build(story)
    return path


# ------------------------------ payback brochures ------------------------------

REGIONS = {
    "Region1": dict(standard=2800, founding=2200, private="$60 to $80", per_student=30),
    "Region2": dict(standard=2000, founding=1600, private="$25 to $45", per_student=15),
}
WEEKS_PER_MONTH = 4  # conservative; a month averages about 4.3 weeks


def months_to_payback(price, monthly):
    m = price / monthly
    if m < 2:
        return "under 2 months"
    return f"about {round(m)} months"


def payback_brochure(region, r):
    p, fee = r["per_student"], r["founding"]
    scenarios = []
    for classes, students in [(1, 4), (1, 6), (2, 6)]:
        monthly = classes * students * p * WEEKS_PER_MONTH
        label = "class" if classes == 1 else "classes"
        scenarios.append(
            f"{classes} weekly {label} of {students}: ${monthly:,}/month, "
            f"paid back in {months_to_payback(fee, monthly)}")
    group_hour = 4 * p

    left = (
        "Your investment",
        [f"Book 1 training: ${fee:,} founding price (standard ${r['standard']:,})",
         "Annual license: first year free, then $499/year",
         "Payment plans available at checkout",
         "Teach as soon as you are certified on Book 1",
         "Group classes of 4 to 8 students"],
        "Spread your training over monthly payments, so your first group class "
        "starts paying you back before you finish paying.",
        PURPLE_TXT,
    )
    right = (
        "How fast your training pays back",
        [f"1 private hour: {r['private']}",
         f"1 group hour with 4 students: ${group_hour}",
         *scenarios],
        [f"These examples assume each student pays ${p} for a one hour group class, "
         "about half of a private lesson or less, so families save while you earn more per hour.",
         "Book 1 runs about 22 weeks with your students. Every new group you open "
         "brings your payback date closer."],
        PURPLE1, PURPLE1_TXT,
    )
    closing = [
        "Examples only. You set your own tuition and schedule. Monthly figures use 4 weeks per month "
        "and do not include the $120 student book set, which each student needs.",
        "From year two, the $499 annual license works out to about $42 a month.",
    ]
    return build(f"MyMusicBox_Training_Payback_{region}.pdf",
                 "How fast your training pays for itself",
                 "One hour, more students. Here is the group class math for a certified "
                 "My Music Box teacher.",
                 left, right, closing, PURPLE)


# ------------------------------ launch kit brochure ------------------------------

def launch_kit_brochure():
    left = (
        "What's in your launch kit",
        ["Parent info night script",
         "Free trial class plan and script",
         "Flyer and social post templates",
         "Enrollment follow-up email templates",
         "Two live group coaching calls in your first semester"],
        "Everything you need to fill your first group class, ready to use the day "
        "you are certified on Book 1.",
        GREEN_TXT,
    )
    right = (
        "Your first group class in four weeks",
        ["Week 1: Invite families with your flyer and posts",
         "Week 2: Host a parent info night",
         "Week 3: Teach a free trial class",
         "Week 4: Enroll families and start your class"],
        ["At the parent info night, you show families how My Music Box works: children take "
         "the music in through the ear, the body, and the voice first, then connect those "
         "abilities to the score and the keyboard.",
         "The trial class lets children sing first, then play, so parents see the joy for "
         "themselves. Your follow-up emails turn that first visit into an enrolled class of 4 to 8.",
         "On the live coaching calls, you bring your questions and we help you plan your "
         "next group."],
        GREEN, GREEN_TXT,
    )
    closing = ["Included with your Book 1 training as a founding teacher. Start with 4 students "
               "and grow from there."]
    return build("MyMusicBox_Group_Class_Launch_Kit.pdf",
                 "Group Class Launch Kit",
                 "From certified to your first full group class, step by step.",
                 left, right, closing, GREEN)


if __name__ == "__main__":
    for region, r in REGIONS.items():
        print(payback_brochure(region, r))
    print(launch_kit_brochure())
