#!/usr/bin/env python3
"""Ambassador Studio Instagram posts (1080 x 1350) for the trial class, in the Welcome Flyer style.

Reserved for Ambassador Studios (brand palette, fonts and artwork).

Posts carry no dates or places, so teachers can post them as they are and put their
own details in the caption (see instagram/captions.md).
"""

import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "ambassador", "instagram")
FONTS = os.path.join(HERE, "fonts")
ART = os.path.join(HERE, "instagram", "header_art.png")

W, H = 1080, 1350
SKY, CLOUD = "#DCEEF9", "#C9E4F6"
BLUE, LIGHT_BLUE = "#3E8EC4", "#5A9ECC"
DARK, MUTED, PLUM = "#3A3A3A", "#6B6B6B", "#542E57"
LAVENDER, TEAL, ORANGE = ("#E0CBE2", "#542E57"), ("#4AC3D4", "#0F4F58"), ("#FAD294", "#845100")
CARD_X, CARD_TOP, CARD_BOTTOM = 56, 56, H - 56


def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, f"{name}.ttf"), size)


def text_w(d, s, f):
    return d.textbbox((0, 0), s, font=f)[2]


def centered(d, y, s, f, fill):
    d.text(((W - text_w(d, s, f)) / 2, y), s, font=f, fill=fill)
    b = d.textbbox((0, 0), s, font=f)
    return y + b[3]


def base():
    im = Image.new("RGB", (W, H), SKY)
    d = ImageDraw.Draw(im)
    for (x, y, r) in [(70, 40, 70), (150, 30, 60), (980, 1300, 80), (880, 1320, 60)]:
        d.ellipse((x - r, y - r, x + r, y + r), fill=CLOUD)
    d.rounded_rectangle((CARD_X, CARD_TOP, W - CARD_X, CARD_BOTTOM), radius=48, fill="white")
    art = Image.open(ART)
    art = art.crop((0, 0, art.width, 492))
    aw = 860
    art = art.resize((aw, int(art.height * aw / art.width)), Image.LANCZOS)
    im.paste(art, ((W - aw) // 2, 96))
    footer(im, d)
    return im, d, 96 + art.height + 18


LOGO = os.path.join(HERE, "assets", "mymusicbox_logo.png")


def footer(im, d):
    """My Music Box logo with the Certified Partner Studio mark (Ambassador Studios only)."""
    y = CARD_BOTTOM - 96
    d.line((110, y, W - 110, y), fill="#E5E4E2", width=2)
    logo = Image.open(LOGO)
    lh = 58
    logo = logo.resize((int(logo.width * lh / logo.height), lh), Image.LANCZOS)
    f = font("Fredoka-Medium", 30)
    label = "My Music Box Certified Partner Studio"
    gap = 16
    total = logo.width + gap + text_w(d, label, f)
    x = (W - total) / 2
    im.paste(logo, (int(x), int(y + 14)), logo)
    b = d.textbbox((0, 0), label, font=f)
    d.text((x + logo.width + gap, y + 14 + (lh - (b[3] - b[1])) / 2 - b[1]), label, font=f, fill=PLUM)


def pill(d, cx, y, label, colors_, f, pad_x=34, h=64):
    fill, txt = colors_
    w = text_w(d, label, f) + 2 * pad_x
    d.rounded_rectangle((cx - w / 2, y, cx + w / 2, y + h), radius=h / 2, fill=fill)
    b = d.textbbox((0, 0), label, font=f)
    d.text((cx - (b[2] - b[0]) / 2 - b[0], y + (h - (b[3] - b[1])) / 2 - b[1]), label, font=f, fill=txt)
    return w


def cta(d, y, label):
    f = font("Fredoka-SemiBold", 40)
    pill(d, W / 2, y, label, ("#542E57", "white"), f, pad_x=48, h=88)
    return y + 88


def render(content):
    """Draw the content once to measure it, then again centered between art and footer."""
    _, scratch, top = base()
    end = content(scratch, top)
    room = (CARD_BOTTOM - 96 - 40) - top
    used = end - top
    assert used <= room, f"{content.__name__}: content runs into the footer"
    im, d, top = base()
    content(d, top + (room - used) / 2)
    return im


def post_invite(d, y):
    y = centered(d, y, "Happy Musician", font("Fredoka-Medium", 34), LIGHT_BLUE) + 22
    f = font("Fredoka-SemiBold", 78)
    y = centered(d, y, "Come try a", f, BLUE) + 8
    y = centered(d, y, "group piano class!", f, BLUE) + 30
    f = font("Inter-Regular", 36)
    y = centered(d, y, "A free 30 minute trial class", f, MUTED) + 10
    y = centered(d, y, "for children ages 4 to 7", f, MUTED) + 44
    f = font("Fredoka-SemiBold", 38)
    labels = [("Sing", LAVENDER), ("Move", TEAL), ("Play", ORANGE)]
    widths = [text_w(d, s, f) + 68 for s, _ in labels]
    gap = 26
    x = (W - sum(widths) - gap * 2) / 2
    for (s, c), w in zip(labels, widths):
        pill(d, x + w / 2, y, s, c, f)
        x += w + gap
    y += 64 + 54
    y = cta(d, y, "Message us to save a spot")
    return y


def post_what_happens(d, y):
    f = font("Fredoka-SemiBold", 66)
    y = centered(d, y, "What happens in", f, BLUE) + 8
    y = centered(d, y, "a trial class?", f, BLUE) + 40
    rows = [("1", "Sing first", "Children sing the song before they play it.", LAVENDER),
            ("2", "Move to the music", "Rhythm comes alive in the body.", TEAL),
            ("3", "Play the piano", "First notes, together with new friends.", ORANGE)]
    left, right = 130, W - 130
    for num, head, body, (fill, txt) in rows:
        h = 120
        d.rounded_rectangle((left, y, right, y + h), radius=28, fill="#FAFAF9", outline="#E5E4E2", width=2)
        d.ellipse((left + 26, y + 28, left + 90, y + 92), fill=fill)
        fn = font("Fredoka-SemiBold", 36)
        b = d.textbbox((0, 0), num, font=fn)
        d.text((left + 58 - (b[2] + b[0]) / 2, y + 60 - (b[3] + b[1]) / 2), num, font=fn, fill=txt)
        d.text((left + 114, y + 22), head, font=font("Inter-Bold", 34), fill=DARK)
        d.text((left + 114, y + 68), body, font=font("Inter-Regular", 27), fill=MUTED)
        assert left + 114 + text_w(d, body, font("Inter-Regular", 27)) < right - 20, body
        y += h + 20
    y += 14
    y = centered(d, y, "Parents watch, then stay for a short talk.", font("Inter-Regular", 32), MUTED) + 36
    y = cta(d, y, "Message us to save a spot")
    return y


def post_last_spots(d, y):
    y = centered(d, y, "Happy Musician", font("Fredoka-Medium", 34), LIGHT_BLUE) + 26
    f = font("Fredoka-SemiBold", 86)
    y = centered(d, y, "Only a few", f, BLUE) + 8
    y = centered(d, y, "spots left!", f, BLUE) + 34
    f = font("Inter-Regular", 36)
    y = centered(d, y, "Free group piano trial class", f, MUTED) + 10
    y = centered(d, y, "for children ages 4 to 7", f, MUTED) + 46
    f = font("Fredoka-SemiBold", 36)
    pill(d, W / 2, y, "Up to 8 children per class", TEAL, f, pad_x=40, h=70)
    y += 70 + 56
    y = cta(d, y, "Message us today")
    return y


if __name__ == "__main__":
    for name, fn in [("post1_invite", post_invite), ("post2_what_happens", post_what_happens),
                     ("post3_last_spots", post_last_spots)]:
        path = os.path.join(OUT, f"{name}.png")
        render(fn).save(path, optimize=True)
        print(path)
