#!/usr/bin/env python3
"""Render the Friday 27 November 2026 world-news poster, 1024x1024.

Champion layout (news-image-20261122/23/24 post-mortems, checked against
the 27 Nov dev leaders): date masthead, red headline strip, a UTC
timeline, three hero stories with big flat illustrations on the top
half, a THE DAY IN NUMBERS panel, region pills, ten mid cards in two
rows of five, each with its own large visual panel and credibility
badge, twenty-three one-line briefs beside a world map with numbered
pins, a DATE CHECK strip and a HOW SURE legend. 36 stories in all,
every one dated 27 Nov 2026 (happened or first reported that day) with
its source. Stories first reported Thu 26 Nov (Kuwait drone strike,
Jazan refinery hit, Bangkok refinery blast, Cairo tanker fire, Macy's
parade postponement, SpaceX shares for every US child) are listed in
DATE CHECK and appear nowhere else in the image. Drawn in code with
Pillow; no network; deterministic output.
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (248, 244, 236)
INK = (24, 24, 24)
RED = (186, 16, 28)
NAVY = (18, 32, 60)
TEAL = (13, 110, 102)
GOLD = (176, 84, 8)
GREY = (104, 99, 88)
LINE = (208, 201, 186)
CARD = (255, 255, 255)

FONTS = [
    "/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf",
    "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
    "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]


def font(bold, size, serif=False):
    cands = []
    if serif:
        cands = [FONTS[0], FONTS[3]]
    elif bold:
        cands = [FONTS[1], FONTS[4]]
    else:
        cands = [FONTS[2], FONTS[5]]
    for p in cands:
        try:
            return ImageFont.truetype(p, size)
        except OSError:
            continue
    return ImageFont.load_default()


def wrap(d, text, f, width, max_lines):
    """Greedy wrap; truncates with ... if it overflows max_lines."""
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= width:
            cur = t
        elif len(lines) < max_lines - 1:
            lines.append(cur)
            cur = w
        else:
            break
    if cur and len(lines) < max_lines:
        lines.append(cur)
    if len(words) > sum(len(l.split()) for l in lines) and lines:
        last = lines[-1]
        while last and d.textlength(last + " ...", font=f) > width:
            last = last.rsplit(" ", 1)[0] if " " in last else ""
        lines[-1] = (last + " ...") if last else "..."
    return lines


def badge(d, x, y, label):
    """Small credibility badge; returns width used."""
    cols = {"CONFIRMED": (18, 110, 60), "OFFICIAL": (18, 60, 110),
            "REPORTED": (150, 110, 10), "CLAIM": (170, 60, 30)}
    c = cols[label]
    f = font(True, 10)
    w = d.textlength(label, font=f) + 10
    d.rounded_rectangle([x, y, x + w, y + 15], radius=7, fill=c)
    d.text((x + 5, y + 2), label, font=f, fill=(255, 255, 255))
    return w


def pin(d, x, y, n):
    d.ellipse([x - 8, y - 8, x + 8, y + 8], fill=RED, outline=(255, 255, 255), width=2)
    f = font(True, 10)
    t = str(n)
    d.text((x - d.textlength(t, font=f) / 2, y - 6), t, font=f, fill=(255, 255, 255))


# ------------------------------------------------------------------ data
# region codes: NA North America, SA Latin America, EU Europe,
# ME Middle East, AF Africa, SAS South Asia, EA East Asia,
# SEA Southeast Asia, OC Oceania

HEROES = [
    dict(n=1, place="USA", region="NA", badge="REPORTED",
         src="Adobe / NDTV",
         head="BLACK FRIDAY OPENS: $12.9BN DAY AHEAD",
         body="Adobe forecasts a record $12.9bn in US online spending; 126m Americans to shop today.",
         art="bags", big="$12.9B"),
    dict(n=2, place="WELLINGTON", region="OC", badge="OFFICIAL",
         src="Electoral Commission / ET",
         head="NZ FINAL COUNT LANDS TODAY",
         body="Coalition loses its majority; 400,000 special votes decide a 67-seat hold.",
         art="ballot", big="67/131"),
    dict(n=3, place="GAZA", region="ME", badge="REPORTED",
         src="Dawn / Reuters",
         head="HAMAS WEIGHS REPLY AFTER 10 DIE IN GAZA",
         body="Strikes kill 10, incl. a Hamas deputy minister; third night of attacks despite the ceasefire.",
         art="night", big="10"),
]

NUMBERS = [
    ("$12.9B", "Black Friday\nUS online sales"),
    ("126M", "Americans\nto shop today"),
    ("400,000", "special votes\nin NZ count"),
    ("77,000", "UK net migration,\nlowest since 1997"),
    ("724,000", "without power\nin US storm"),
    ("10", "killed in Gaza\nin one day"),
]

CARDS = [
    dict(n=4, place="LONDON", region="EU", badge="OFFICIAL", src="ONS / Reuters",
         head="UK NET MIGRATION LOWEST SINCE '97",
         body="Falls to 77,000 in the year to June, down from 204,000.",
         big="77,000", art="down"),
    dict(n=5, place="GENEVA", region="EU", badge="REPORTED", src="NDTV",
         head="GUKESH-SINDAROV GAME 3 ENDS DRAWN",
         body="Marathon Game 3 ends 1\u00bd-\u00bd; Game 4 is played today.",
         big="1\u00bd-\u00bd", art="chess"),
    dict(n=6, place="PARIS", region="EU", badge="CONFIRMED", src="BBC / Reuters",
         head="DEPARDIEU TO STAND TRIAL FOR RAPE",
         body="French court orders trial over alleged 2018 rape.",
         big="2018", art="court"),
    dict(n=7, place="IBIZA", region="EU", badge="REPORTED", src="BBC",
         head="TANKER CAPSIZES OFF IBIZA, ONE DEAD",
         body="Diesel tanker carrying up to 7,000 tonnes capsizes; one killed.",
         big="7,000T", art="sea"),
    dict(n=8, place="WASHINGTON", region="NA", badge="CLAIM", src="Reuters / AP",
         head="TRUMP SEEKS PROBE INTO 'FAKE' GDP",
         body="Demands inquiry after US growth is revised up to 4.3%.",
         big="4.3%", art="chart"),
    dict(n=9, place="USA", region="NA", badge="CONFIRMED", src="NDTV / FlightAware",
         head="THANKSGIVING STORM CUTS POWER TO 724,000",
         body="Storm cancels 400 flights, delays 2,000+; 80m travel for the holiday.",
         big="724,000", art="storm"),
    dict(n=10, place="NEW DELHI", region="SAS", badge="OFFICIAL", src="NDTV",
         head="DELHI POLICE BUST CYBER SLAVERY RACKET",
         body="164 foreigners rescued, incl. 92 Indonesians and 72 Malaysians.",
         big="164", art="shield"),
    dict(n=11, place="PYONGYANG", region="EA", badge="OFFICIAL", src="AFP",
         head="KIM VOWS TO EXPAND NUCLEAR PROGRAMME",
         body="Kim calls for more warheads after Trump's outreach.",
         big="KIM", art="missile"),
    dict(n=12, place="KYIV", region="EU", badge="REPORTED", src="Reuters",
         head="ZELENSKY WARNS OF NEW MASS STRIKE",
         body="Russian strikes kill 5 and cut power; Kyiv braces for more.",
         big="5", art="jet"),
    dict(n=13, place="VADODARA", region="SAS", badge="CONFIRMED", src="NDTV",
         head="INDIA U-19 WOMEN BEAT ENGLAND",
         body="India win the T20 opener by 36 runs; Ahire hits 63 not out.",
         big="36-RUN", art="bat"),
]

BRIEFS = [
    ("India v NZ 2nd Test starts in Christchurch.", "NZ Herald", "OC"),
    ("Trump defends Huang's second term at Nvidia.", "ET", "NA"),
    ("Trump lashes out at foes in Thanksgiving message.", "ET", "NA"),
    ("Argentina bans central bank printing money.", "ET", "SA"),
    ("Second judge blocks birthright citizenship order.", "ET", "NA"),
    ("Trump: Putin can come to G20 if he wants.", "ET", "NA"),
    ("Hasina's ex-deputy press secretary arrested.", "ET", "SAS"),
    ("Ukraine, Russia exchange remains of fallen soldiers.", "Qatar Tribune", "EU"),
    ("Germany expands return plan for Syrians.", "Qatar Tribune", "EU"),
    ("NATO's Rutte praises Trump for testing Putin.", "Qatar Tribune", "EU"),
    ("Iran reports explosions on three tankers in Hormuz.", "Qatar Tribune", "ME"),
    ("Brent near $97 as Gulf attacks lift oil.", "NDTV", "ME"),
    ("Tokyo core prices up 2.9% in November.", "NDTV", "EA"),
    ("French students plan nationwide protests.", "Munich Eye", "EU"),
    ("Mayon erupts in Philippines, ash 3,000m high.", "Munich Eye", "SEA"),
    ("All hostages freed after 16-hour Colombia siege.", "Qatar Tribune", "SA"),
    ("Pope Leo XIV to vote in US midterms by mail.", "Munich Eye", "NA"),
    ("EU and Canada plan closer AI collaboration.", "Munich Eye", "EU"),
    ("Vance: Huang will not need any pardon.", "joyofgreen", "NA"),
    ("US clears F-16 equipment sale to Ukraine.", "joyofgreen", "NA"),
    ("Sisi, Qatari emir discuss Gaza ceasefire.", "joyofgreen", "ME"),
    ("French cyber chief warns of 'unprecedented' threat.", "joyofgreen", "EU"),
    ("Kenya joins Africa CDC board for two-year term.", "Guardian", "AF"),
]

REGIONS = [("NORTH AMERICA", "NA"), ("EUROPE", "EU"), ("MIDDLE EAST", "ME"),
           ("AFRICA", "AF"), ("SOUTH ASIA", "SAS"), ("EAST ASIA", "EA"),
           ("SOUTHEAST ASIA", "SEA"), ("LATIN AMERICA", "SA"), ("OCEANIA", "OC")]

DATECHECK = [
    ("Kuwait drone strike kills 2 Italians", "Thu 26 Nov"),
    ("Houthi strike on Jazan refinery, 1 killed", "Thu 26 Nov"),
    ("Bangkok refinery blast injures 9", "Thu 26 Nov"),
    ("Cairo tanker fire kills 31", "Thu 26 Nov"),
    ("Macy's 100th parade postponed", "Thu 26 Nov"),
    ("SpaceX shares for every US child", "Thu 26 Nov"),
]

# map pin positions (x, y) in the small map box, keyed by story number
PINS = {1: (50, 28), 2: (282, 60), 3: (198, 44), 4: (138, 16), 5: (162, 22),
        6: (148, 36), 7: (130, 46), 8: (66, 40), 9: (78, 24), 10: (214, 50),
        11: (264, 26), 12: (186, 16), 13: (238, 62)}


# ------------------------------------------------------------------ art
def draw_art(d, box, kind, big, col):
    """Flat illustration panel for a hero card."""
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=col)
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    if kind == "bags":
        for bx, bh, bc in ((x0 + 26, 58, (235, 120, 40)),
                           (cx - 30, 68, (250, 190, 40)),
                           (x1 - 86, 58, (120, 200, 220))):
            d.rectangle([bx, y0 + 84 - bh, bx + 56, y0 + 84], fill=bc)
            d.arc([bx + 12, y0 + 84 - bh - 16, bx + 44, y0 + 84 - bh + 8],
                  180, 360, fill=bc, width=4)
        for xx in (x0 + 14, x1 - 46):
            d.ellipse([xx, y0 + 12, xx + 26, y0 + 38], fill=(255, 255, 255))
    elif kind == "ballot":
        d.rectangle([cx - 40, y0 + 40, cx + 40, y0 + 84], fill=(255, 255, 255))
        d.rectangle([cx - 48, y0 + 32, cx + 48, y0 + 42], fill=(240, 240, 240))
        d.rectangle([cx - 12, y0 + 34, cx + 12, y0 + 40], fill=col)
        d.polygon([(cx - 52, y0 + 8), (cx - 30, y0 + 8), (cx - 30, y0 + 34),
                   (cx - 52, y0 + 34)], fill=(255, 255, 255))
        d.polygon([(cx - 46, y0 + 22), (cx - 40, y0 + 28), (cx - 32, y0 + 16)],
                  fill=(18, 110, 60))
        d.ellipse([x0 + 16, y0 + 12, x0 + 40, y0 + 36], fill=(255, 210, 90))
        d.ellipse([x1 - 40, y0 + 10, x1 - 16, y0 + 34], fill=(255, 255, 255))
    elif kind == "night":
        d.rectangle([x0, y1 - 30, x1, y1], fill=(10, 16, 34))
        for bx, bh in ((x0 + 18, 44), (x0 + 66, 58), (x0 + 118, 40),
                       (x0 + 168, 52), (x0 + 218, 46), (x0 + 262, 36)):
            d.rectangle([bx, y1 - 30 - bh, bx + 36, y1 - 30], fill=(40, 48, 70))
        d.ellipse([cx - 30, y0 + 30, cx + 30, y0 + 84], fill=(240, 90, 20))
        d.ellipse([cx - 16, y0 + 46, cx + 16, y0 + 84], fill=(250, 190, 40))
        for px, py in ((x0 + 22, y0 + 12), (x1 - 30, y0 + 16), (x0 + 60, y0 + 24),
                       (cx + 60, y0 + 10)):
            d.ellipse([px, py, px + 4, py + 4], fill=(255, 255, 255))
    f = font(True, 30)
    by_ = y0 + 6 if kind == "chart" else y1 - 40
    d.text((x1 - d.textlength(big, font=f) - 10, by_), big, font=f,
           fill=(255, 255, 255))


def draw_card_art(d, box, kind, big, col):
    """Large visual panel for a mid card: motif plus a big word/number."""
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=col)
    cx = (x0 + x1) // 2
    if kind in ("sea", "oil"):
        for yy in (y0 + 22, y0 + 38, y0 + 54):
            d.arc([x0 + 14, yy - 10, x1 - 14, yy + 16], 0, 180, fill=(255, 255, 255), width=3)
        d.polygon([(cx - 34, y0 + 10), (cx + 34, y0 + 10), (cx, y0 + 34)], fill=(255, 255, 255))
    elif kind == "space":
        d.ellipse([cx - 16, y0 + 10, cx + 16, y0 + 42], fill=(255, 255, 255))
        d.rectangle([cx - 34, y0 + 26, cx + 34, y0 + 36], fill=(255, 255, 255))
        for px, py in ((x0 + 16, y0 + 12), (x1 - 20, y0 + 16), (x0 + 26, y0 + 40)):
            d.ellipse([px, py, px + 4, py + 4], fill=(255, 255, 255))
    elif kind == "chess":
        for i in range(5):
            for j in range(3):
                if (i + j) % 2 == 0:
                    d.rectangle([x0 + 12 + i * 16, y0 + 10 + j * 16,
                                 x0 + 28 + i * 16, y0 + 26 + j * 16],
                                fill=(255, 255, 255))
        d.ellipse([cx + 20, y0 + 12, cx + 40, y0 + 32], fill=(255, 255, 255))
    elif kind == "missile":
        d.polygon([(cx - 6, y0 + 6), (cx + 6, y0 + 6), (cx, y0 + 26)], fill=(255, 255, 255))
        d.rectangle([cx - 6, y0 + 26, cx + 6, y0 + 48], fill=(255, 255, 255))
    elif kind == "guitar":
        d.ellipse([cx - 16, y0 + 16, cx + 16, y0 + 48], fill=(255, 255, 255))
        d.rectangle([cx - 4, y0 + 4, cx + 4, y0 + 22], fill=(255, 255, 255))
    elif kind == "court":
        for xx in (x0 + 18, cx - 4, x1 - 34):
            d.rectangle([xx, y0 + 14, xx + 14, y0 + 44], fill=(255, 255, 255))
        d.rectangle([x0 + 10, y0 + 44, x1 - 10, y0 + 50], fill=(255, 255, 255))
    elif kind == "aid":
        d.rectangle([cx - 16, y0 + 10, cx - 4, y0 + 48], fill=(255, 255, 255))
        d.rectangle([cx - 24, y0 + 22, cx + 4, y0 + 34], fill=(255, 255, 255))
    elif kind in ("jet", "radar"):
        d.polygon([(x0 + 20, y0 + 38), (x1 - 30, y0 + 26), (x1 - 14, y0 + 32),
                   (x1 - 30, y0 + 38), (x0 + 20, y0 + 44)], fill=(255, 255, 255))
        d.polygon([(cx - 10, y0 + 14), (cx + 6, y0 + 14), (cx + 2, y0 + 34),
                   (cx - 14, y0 + 34)], fill=(255, 255, 255))
        d.polygon([(cx + 8, y0 + 40), (cx + 22, y0 + 40), (cx + 16, y0 + 52),
                   (cx + 4, y0 + 52)], fill=(255, 255, 255))
    elif kind == "memorial":
        d.ellipse([cx - 18, y0 + 12, cx + 18, y0 + 50], fill=(255, 255, 255))
        d.rectangle([cx - 3, y0 + 30, cx + 3, y0 + 50], fill=(255, 255, 255))
    elif kind == "down":
        d.line([x0 + 18, y0 + 16, cx, y0 + 34, x1 - 18, y0 + 52],
               fill=(255, 255, 255), width=5)
        d.polygon([(x1 - 18, y0 + 52), (x1 - 34, y0 + 46), (x1 - 30, y0 + 60)],
                  fill=(255, 255, 255))
    elif kind == "chart":
        d.line([x0 + 16, y0 + 52, x0 + 60, y0 + 36, x0 + 104, y0 + 42,
                x0 + 148, y0 + 22], fill=(255, 255, 255), width=5)
        d.polygon([(x0 + 148, y0 + 22), (x0 + 160, y0 + 22), (x0 + 148, y0 + 34)],
                  fill=(255, 255, 255))
    elif kind == "storm":
        d.ellipse([cx - 34, y0 + 12, cx + 10, y0 + 40], fill=(255, 255, 255))
        d.ellipse([cx - 10, y0 + 6, cx + 34, y0 + 34], fill=(255, 255, 255))
        d.polygon([(cx - 6, y0 + 36), (cx + 8, y0 + 36), (cx - 2, y0 + 52),
                   (cx + 12, y0 + 52), (cx - 8, y0 + 74), (cx + 2, y0 + 52),
                   (cx - 10, y0 + 52)], fill=(255, 210, 90))
    elif kind == "shield":
        d.polygon([(cx, y0 + 8), (cx + 26, y0 + 18), (cx + 26, y0 + 44),
                   (cx, y0 + 62), (cx - 26, y0 + 44), (cx - 26, y0 + 18)],
                  fill=(255, 255, 255))
        d.line([cx - 12, y0 + 34, cx - 4, y0 + 44, cx + 14, y0 + 24],
               fill=col, width=4)
    elif kind == "bat":
        d.rectangle([cx - 24, y0 + 10, cx - 8, y0 + 52], fill=(255, 255, 255))
        d.rectangle([cx - 22, y0 + 52, cx - 10, y0 + 66], fill=(255, 255, 255))
        d.ellipse([cx + 12, y0 + 14, cx + 34, y0 + 36], fill=(255, 210, 90))
    size = 30
    while size > 14 and d.textlength(big, font=font(True, size)) > (x1 - x0) - 16:
        size -= 2
    f = font(True, size)
    tw = d.textlength(big, font=f)
    d.text((x1 - tw - 8, y1 - size - 8), big, font=f, fill=(255, 255, 255))


# ------------------------------------------------------------------ render
def render():
    im = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(im)
    mx = 24
    # masthead
    d.text((mx, 14), "FRIDAY 27 NOVEMBER 2026", font=font(True, 40, serif=True), fill=INK)
    d.text((mx, 60), "THE WORLD IN ONE PAGE  \u00b7  36 dated stories  \u00b7  9 regions",
           font=font(True, 15), fill=GREY)
    d.text((W - mx - 150, 22), "ONE DAY.", font=font(True, 26, serif=True), fill=RED)
    d.text((W - mx - 150, 52), "EVERY REGION.", font=font(True, 15), fill=INK)
    d.line([mx, 84, W - mx, 84], fill=INK, width=2)
    # red headline strip
    d.rectangle([mx, 90, W - mx, 114], fill=RED)
    strip = ("1  BLACK FRIDAY OPENS   \u2022   2  NZ FINAL COUNT LANDS   \u2022   "
             "3  HAMAS WEIGHS REPLY AFTER 10 DIE IN GAZA")
    d.text((mx + 10, 97), strip, font=font(True, 15), fill=(255, 255, 255))
    # UTC timeline
    d.text((mx, 120), "FRIDAY UTC", font=font(True, 11), fill=RED)
    d.line([mx + 108, 128, W - mx, 128], fill=LINE, width=2)
    marks = [("01:00", "NZ final count lands"), ("06:00", "Tokyo prices out"),
             ("11:00", "Black Friday opens"), ("14:00", "Game 4, Geneva"),
             ("18:00", "Storm peaks, US East"), ("24:00", "Day ends")]
    seg = (W - 2 * mx - 108) / 5
    for i, (t, label) in enumerate(marks):
        x = mx + 108 + i * seg
        d.ellipse([x - 3, 125, x + 3, 131], fill=RED)
        tw = d.textlength(t, font=font(True, 9))
        tx = min(max(x - tw / 2, mx + 108), W - mx - tw)
        d.text((tx, 114), t, font=font(True, 9), fill=INK)
        lw = d.textlength(label, font=font(False, 9))
        lx = min(max(x - lw / 2, mx + 108), W - mx - lw)
        d.text((lx, 132), label, font=font(False, 9), fill=GREY)
    # heroes
    hy, hh = 142, 194
    hw = (W - 2 * mx - 2 * 12) // 3
    cols = [(NAVY, (200, 220, 235)), (TEAL, (205, 225, 215)), (GOLD, (240, 220, 190))]
    for i, h in enumerate(HEROES):
        x0 = mx + i * (hw + 12)
        x1 = x0 + hw
        d.rounded_rectangle([x0, hy, x1, hy + hh], radius=8, fill=CARD, outline=LINE, width=1)
        draw_art(d, (x0 + 1, hy + 1, x1 - 1, hy + 84), h["art"], h["big"], cols[i][0])
        pin(d, x0 + 16, hy + 16, h["n"])
        d.text((x0 + 10, hy + 90), h["place"], font=font(True, 11), fill=RED)
        for j, ln in enumerate(wrap(d, h["head"], font(True, 17), hw - 20, 2)):
            d.text((x0 + 10, hy + 104 + j * 20), ln, font=font(True, 17), fill=INK)
        for j, ln in enumerate(wrap(d, h["body"], font(False, 12.5), hw - 20, 2)):
            d.text((x0 + 10, hy + 142 + j * 15), ln, font=font(False, 12.5), fill=(60, 58, 52))
        d.text((x0 + 10, hy + hh - 16), h["src"], font=font(False, 10), fill=GREY)
        badge(d, x1 - 78, hy + hh - 18, h["badge"])
    # numbers panel
    ny = 344
    d.rectangle([mx, ny, W - mx, ny + 48], fill=NAVY)
    d.text((mx + 12, ny + 7), "THE DAY\nIN NUMBERS", font=font(True, 12), fill=(255, 255, 255))
    seg = (W - 2 * mx - 150) // 6
    for i, (num, cap) in enumerate(NUMBERS):
        x = mx + 150 + i * seg
        d.text((x, ny + 2), num, font=font(True, 24), fill=(255, 210, 90))
        for j, ln in enumerate(cap.split("\n")):
            d.text((x, ny + 27 + j * 10), ln, font=font(False, 9.5), fill=(220, 225, 235))
        if i:
            d.line([x - 8, ny + 7, x - 8, ny + 41], fill=(90, 105, 130), width=1)
    # region pills
    counts = {}
    for s in HEROES + CARDS:
        counts[s["region"]] = counts.get(s["region"], 0) + 1
    for _, _, r in BRIEFS:
        counts[r] = counts.get(r, 0) + 1
    px = mx
    py = 400
    for name, code in REGIONS:
        label = f"{name} {counts.get(code, 0)}"
        f = font(True, 11)
        w = d.textlength(label, font=f) + 16
        d.rounded_rectangle([px, py, px + w, py + 20], radius=10,
                            fill=(255, 255, 255), outline=LINE, width=1)
        d.text((px + 8, py + 4), label, font=f, fill=INK)
        px += w + 7
    # mid cards: 2 rows of 5, each with a large visual panel
    gy, gh = 428, 171
    cw = (W - 2 * mx - 4 * 10) // 5
    card_cols = [NAVY, TEAL, GOLD, (120, 40, 90), (40, 90, 120), (90, 90, 40),
                 (150, 60, 20), (30, 90, 60), (100, 30, 60), (60, 60, 120)]
    for i, c in enumerate(CARDS):
        r, col = divmod(i, 5)
        x0 = mx + col * (cw + 10)
        y0 = gy + r * (gh + 8)
        x1, y1 = x0 + cw, y0 + gh
        d.rounded_rectangle([x0, y0, x1, y1], radius=6, fill=CARD, outline=LINE, width=1)
        draw_card_art(d, (x0 + 1, y0 + 1, x1 - 1, y0 + 84), c["art"], c["big"], card_cols[i])
        pin(d, x0 + 13, y0 + 13, c["n"])
        for j, ln in enumerate(wrap(d, c["head"], font(True, 11.5), cw - 16, 2)):
            d.text((x0 + 8, y0 + 90 + j * 14), ln, font=font(True, 11.5), fill=INK)
        for j, ln in enumerate(wrap(d, c["body"], font(False, 10), cw - 16, 2)):
            d.text((x0 + 8, y0 + 120 + j * 12), ln, font=font(False, 10), fill=(60, 58, 52))
        d.text((x0 + 8, y1 - 13), c["src"], font=font(False, 9), fill=GREY)
        badge(d, x1 - 80, y1 - 14, c["badge"])
    # bottom band: map + date check on the left, briefs on the right
    by = 786
    d.text((mx, by), "WHERE IT HAPPENED", font=font(True, 12), fill=NAVY)
    mapx, mapy, mapw, maph = mx, by + 20, 306, 124
    d.rounded_rectangle([mapx, mapy, mapx + mapw, mapy + maph], radius=6,
                        fill=(205, 225, 238), outline=LINE, width=1)
    land = (150, 175, 140)
    d.polygon([(mapx + 16, mapy + 22), (mapx + 84, mapy + 16), (mapx + 92, mapy + 34),
               (mapx + 66, mapy + 48), (mapx + 32, mapy + 46), (mapx + 14, mapy + 34)], fill=land)
    d.polygon([(mapx + 82, mapy + 52), (mapx + 104, mapy + 50), (mapx + 110, mapy + 68),
               (mapx + 96, mapy + 74), (mapx + 84, mapy + 62)], fill=land)
    d.polygon([(mapx + 146, mapy + 16), (mapx + 176, mapy + 14), (mapx + 182, mapy + 32),
               (mapx + 164, mapy + 38), (mapx + 148, mapy + 32)], fill=land)
    d.polygon([(mapx + 156, mapy + 40), (mapx + 184, mapy + 38), (mapx + 190, mapy + 62),
               (mapx + 176, mapy + 72), (mapx + 160, mapy + 58)], fill=land)
    d.polygon([(mapx + 184, mapy + 14), (mapx + 280, mapy + 12), (mapx + 292, mapy + 32),
               (mapx + 264, mapy + 46), (mapx + 220, mapy + 44), (mapx + 190, mapy + 32)], fill=land)
    d.ellipse([mapx + 258, mapy + 50, mapx + 276, mapy + 58], fill=land)
    d.ellipse([mapx + 278, mapy + 58, mapx + 300, mapy + 68], fill=land)
    for n, (px_, py_) in PINS.items():
        pin(d, mapx + px_, mapy + py_, n)
    d.text((mapx + 8, mapy + maph - 14), "Pins 1-13: heroes and mid cards",
           font=font(False, 9), fill=NAVY)
    # date check box under the map
    dx = mx
    dw = mapw
    ty = mapy + maph + 8
    d.rounded_rectangle([dx, ty, dx + dw, ty + 66], radius=6, fill=(255, 248, 230),
                        outline=(220, 190, 120), width=1)
    d.text((dx + 8, ty + 4), "DATE CHECK \u2014 LEFT OUT ON PURPOSE", font=font(True, 10), fill=GOLD)
    for i, (item, when) in enumerate(DATECHECK):
        y = ty + 17 + i * 9
        whenw = d.textlength(when, font=font(True, 8.5))
        it = item
        f9 = font(False, 9)
        while it and d.textlength("x " + it, font=f9) > dw - 16 - whenw - 6:
            it = it.rsplit(" ", 1)[0] if " " in it else ""
        d.text((dx + 8, y), "x " + it, font=f9, fill=(90, 80, 60))
        d.text((dx + dw - 8 - whenw, y), when, font=font(True, 8.5), fill=GOLD)
    # briefs on the right
    bx = mapx + mapw + 12
    bw = W - mx - bx
    d.text((bx, by), "THE REST OF THE DAY \u2014 23 MORE STORIES",
           font=font(True, 13), fill=RED)
    d.line([bx, by + 18, W - mx, by + 18], fill=LINE, width=1)
    bf = font(False, 12)
    colw = (bw - 8) // 2
    half = 12
    for i, (txt, src, _) in enumerate(BRIEFS):
        col, row = divmod(i, half)
        x = bx if col == 0 else bx + colw + 8
        y = by + 24 + row * 17
        d.text((x, y), f"{14 + i}.", font=font(True, 11), fill=RED)
        srcw = d.textlength(src, font=font(False, 8.5))
        avail = colw - 24 - srcw - 10
        t = txt
        while t and d.textlength(t + " ...", font=bf) > avail:
            t = t.rsplit(" ", 1)[0] if " " in t else ""
        if t != txt:
            t = t + " ..."
        d.text((x + 24, y), t, font=bf, fill=INK)
        d.text((x + colw - 8 - srcw, y + 1), src, font=font(False, 8.5), fill=GREY)
    # footer: how sure + sources on one line
    d.text((mx, H - 16), "HOW SURE: CONFIRMED verified \u00b7 OFFICIAL announced \u00b7 "
           "REPORTED sourced \u00b7 CLAIM alleged  |  Reuters \u00b7 AP \u00b7 Dawn \u00b7 AFP \u00b7 "
           "BBC \u00b7 ONS \u00b7 NDTV \u00b7 ET \u00b7 Qatar Tribune \u00b7 NZ Herald \u00b7 Guardian",
           font=font(False, 9), fill=GREY)
    return im


if __name__ == "__main__":
    out = os.environ.get("OUT", "entry.png")
    im = render()
    im.save(out, optimize=True)
    print(out, im.size, os.path.getsize(out), "bytes")
