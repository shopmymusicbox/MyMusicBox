#!/usr/bin/env python3
"""Basic-license trial class materials: invite flyer, reminder flyer and Instagram posts.

Licensed teachers keep their own studio name. The My Music Box palette, fonts, artwork and
logo are reserved for Ambassador Studios, so these use a neutral look. The only brand
mention is the text line teachers may use: "Book 1 Certified My Music Box Teacher".
"""

import os

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import simpleSplit
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from build_trial_class_flyers import INVITE, REMINDER

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "basic", "plain")
LIB = "/usr/share/fonts/truetype/liberation"
pdfmetrics.registerFont(TTFont("Plain", f"{LIB}/LiberationSans-Regular.ttf"))
pdfmetrics.registerFont(TTFont("Plain-Bold", f"{LIB}/LiberationSans-Bold.ttf"))

INK, GRAY, LIGHT, RULE, ACCENT = "#2B2F33", "#5F676E", "#F3F4F5", "#D5D9DD", "#34506B"
CERT_LINE = "Taught by a Book 1 Certified My Music Box Teacher"

PAGE_W, PAGE_H = A4
M = 56  # side margin


def hex_(c):
    return colors.HexColor(c)


# ------------------------------------ flyers ------------------------------------

def write_line(c, x1, x2, y, label=None):
    c.setStrokeColor(hex_(RULE))
    c.setLineWidth(0.8)
    c.line(x1, y, x2, y)
    if label:
        c.setFillColor(hex_(GRAY))
        c.setFont("Plain", 8.5)
        c.drawString(x1, y - 11, label)


def flyer(spec, filename):
    path = os.path.join(OUT, filename)
    c = canvas.Canvas(path, pagesize=A4)
    c.setTitle(spec["title"])
    width = PAGE_W - 2 * M

    def Y(top):
        return PAGE_H - top

    # top bar and studio name line
    c.setFillColor(hex_(ACCENT))
    c.rect(0, Y(14), PAGE_W, 14, stroke=0, fill=1)
    write_line(c, M, M + 260, Y(70), "Your studio name")

    c.setFillColor(hex_(INK))
    c.setFont("Plain-Bold", 28)
    c.drawString(M, Y(130), spec["title"])
    c.setFillColor(hex_(GRAY))
    c.setFont("Plain", 13)
    c.drawString(M, Y(154), spec["subtitle"])

    def cards(top):
        gap = 14
        tw = (width - 2 * gap) / 3
        inner = tw - 34
        def needed(items):
            lines = sum(len(simpleSplit(t, "Plain", 10.5, inner)) for t in items)
            return 40 + lines * 14 + (len(items) - 1) * 6 + 14
        th = max(needed(items) for _, items, _, _ in spec["cards"])
        for i, (head, items, _, _) in enumerate(spec["cards"]):
            x = M + i * (tw + gap)
            c.setStrokeColor(hex_(RULE))
            c.setLineWidth(1)
            c.setFillColor(colors.white)
            c.rect(x, Y(top + th), tw, th, stroke=1, fill=1)
            c.setFillColor(hex_(ACCENT))
            c.rect(x, Y(top + 3), tw, 3, stroke=0, fill=1)
            c.setFillColor(hex_(INK))
            c.setFont("Plain-Bold", 12)
            c.drawString(x + 12, Y(top + 24), head)
            y = top + 44
            for it in items:
                c.setFillColor(hex_(ACCENT))
                c.rect(x + 12, Y(y - 1), 4, 4, stroke=0, fill=1)
                c.setFillColor(hex_(INK))
                c.setFont("Plain", 10.5)
                for line in simpleSplit(it, "Plain", 10.5, inner):
                    c.drawString(x + 22, Y(y + 3), line)
                    y += 14
                y += 6
            assert y - 6 <= top + th - 8, f"{head} runs past its box"
        return top + th

    def details(top):
        row = 52
        h = 40 + len(spec["fields"]) * row
        c.setFillColor(hex_(LIGHT))
        c.rect(M, Y(top + h), width, h, stroke=0, fill=1)
        c.setFillColor(hex_(INK))
        c.setFont("Plain-Bold", 14)
        c.drawString(M + 16, Y(top + 26), spec["details_title"])
        for i, f in enumerate(spec["fields"]):
            y = top + 40 + (i + 1) * row - 10
            c.setFillColor(hex_(INK))
            c.setFont("Plain-Bold", 11)
            c.drawString(M + 16, Y(y), f)
            write_line(c, M + 110, M + width - 16, Y(y + 3))
        return top + h

    y = 196
    if spec["cards_first"]:
        y = details(cards(y) + 40) + 56
    else:
        y = cards(details(y) + 40) + 56
    c.setFillColor(hex_(ACCENT))
    c.setFont("Plain-Bold", 16)
    c.drawCentredString(PAGE_W / 2, Y(y), spec["closing"])
    assert y < PAGE_H - 80, f"{filename}: content runs into the footer"

    c.setStrokeColor(hex_(RULE))
    c.setLineWidth(0.75)
    c.line(M, 52, PAGE_W - M, 52)
    c.setFillColor(hex_(GRAY))
    c.setFont("Plain", 9.5)
    c.drawString(M, 36, CERT_LINE)
    c.showPage()
    c.save()
    return path


# ---------------------------------- Instagram -----------------------------------

W, H = 1080, 1350


def pfont(bold, size):
    return ImageFont.truetype(f"{LIB}/LiberationSans-{'Bold' if bold else 'Regular'}.ttf", size)


def tw_(d, s, f):
    return d.textbbox((0, 0), s, font=f)[2]


def centered(d, y, s, f, fill):
    d.text(((W - tw_(d, s, f)) / 2, y), s, font=f, fill=fill)
    return y + d.textbbox((0, 0), s, font=f)[3]


def button(d, y, label, fill=ACCENT, text="white", h=92, pad=50, f=None):
    f = f or pfont(True, 38)
    w = tw_(d, label, f) + 2 * pad
    d.rounded_rectangle(((W - w) / 2, y, (W + w) / 2, y + h), radius=14, fill=fill)
    b = d.textbbox((0, 0), label, font=f)
    d.text(((W - (b[2] - b[0])) / 2 - b[0], y + (h - (b[3] - b[1])) / 2 - b[1]), label, font=f, fill=text)
    return y + h


def post(content):
    def draw(d, top):
        return content(d, top)
    _ = Image.new("RGB", (W, H), "white")
    end = content(ImageDraw.Draw(_), 0)
    im = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, W, 22), fill=ACCENT)
    foot = H - 120
    d.line((90, foot, W - 90, foot), fill=RULE, width=2)
    centered(d, foot + 34, CERT_LINE, pfont(False, 30), GRAY)
    room = foot - 60 - 80
    assert end <= room, f"{content.__name__} is too tall"
    content(d, 80 + (room - end) / 2)
    return im


def ig_invite(d, y):
    f = pfont(True, 80)
    y = centered(d, y, "Come try a", f, INK) + 10
    y = centered(d, y, "group piano class!", f, INK) + 36
    f = pfont(False, 38)
    y = centered(d, y, "A free 30 minute trial class", f, GRAY) + 12
    y = centered(d, y, "for children ages 4 to 7", f, GRAY) + 50
    f = pfont(True, 36)
    labels = ["Sing", "Move", "Play"]
    ws = [tw_(d, s, f) + 64 for s in labels]
    x = (W - sum(ws) - 2 * 24) / 2
    for s, w in zip(labels, ws):
        d.rounded_rectangle((x, y, x + w, y + 66), radius=33, outline=ACCENT, width=3, fill="white")
        b = d.textbbox((0, 0), s, font=f)
        d.text((x + (w - (b[2] - b[0])) / 2 - b[0], y + (66 - (b[3] - b[1])) / 2 - b[1]), s, font=f, fill=ACCENT)
        x += w + 24
    y += 66 + 60
    return button(d, y, "Message us to save a spot")


def ig_what_happens(d, y):
    f = pfont(True, 68)
    y = centered(d, y, "What happens in", f, INK) + 10
    y = centered(d, y, "a trial class?", f, INK) + 44
    rows = [("1", "Sing first", "Children sing the song before they play it."),
            ("2", "Move to the music", "Rhythm comes alive in the body."),
            ("3", "Play the piano", "First notes, together with new friends.")]
    left, right = 120, W - 120
    for num, head, body in rows:
        h = 124
        d.rectangle((left, y, right, y + h), fill=LIGHT)
        d.ellipse((left + 26, y + 30, left + 90, y + 94), fill=ACCENT)
        fn = pfont(True, 34)
        b = d.textbbox((0, 0), num, font=fn)
        d.text((left + 58 - (b[2] + b[0]) / 2, y + 62 - (b[3] + b[1]) / 2), num, font=fn, fill="white")
        d.text((left + 114, y + 24), head, font=pfont(True, 34), fill=INK)
        d.text((left + 114, y + 70), body, font=pfont(False, 28), fill=GRAY)
        assert left + 114 + tw_(d, body, pfont(False, 28)) < right - 16, body
        y += h + 18
    y += 16
    y = centered(d, y, "Parents watch, then stay for a short talk.", pfont(False, 32), GRAY) + 40
    return button(d, y, "Message us to save a spot")


def ig_last_spots(d, y):
    f = pfont(True, 90)
    y = centered(d, y, "Only a few", f, INK) + 10
    y = centered(d, y, "spots left!", f, INK) + 40
    f = pfont(False, 38)
    y = centered(d, y, "Free group piano trial class", f, GRAY) + 12
    y = centered(d, y, "for children ages 4 to 7", f, GRAY) + 50
    y = button(d, y, "Up to 8 children per class", fill=LIGHT, text=ACCENT, h=74, f=pfont(True, 34)) + 50
    return button(d, y, "Message us today")


if __name__ == "__main__":
    os.makedirs(os.path.join(OUT, "instagram"), exist_ok=True)
    print(flyer(INVITE, "Trial_Class_Invite_Flyer.pdf"))
    print(flyer(REMINDER, "Trial_Class_Reminder_Flyer.pdf"))
    for name, fn in [("post1_invite", ig_invite), ("post2_what_happens", ig_what_happens),
                     ("post3_last_spots", ig_last_spots)]:
        path = os.path.join(OUT, "instagram", f"{name}.png")
        post(fn).save(path, optimize=True)
        print(path)
