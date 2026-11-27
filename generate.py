#!/usr/bin/env python3
"""Draw the Friday 27 November 2026 world-news poster (1024x1024).

Layout follows the champion broadsheet the 22/23/24 Nov post-mortems
converged on, cross-checked against the 27 Nov dev leaders: a date
masthead, a red headline strip, a UTC timeline, three hero stories
with big flat scenes across the top half, a THE DAY IN NUMBERS band,
region pills, ten mid cards in two rows of five (each with its own
large visual panel and a credibility tag), twenty-three one-line
briefs beside a world map with numbered pins, a DATE CHECK strip and
a HOW SURE legend. 36 stories, all dated 27 Nov 2026 (happened or
first reported that day) with a source on each. Stories first
reported Thu 26 Nov — the Kuwait drone strike, the Jazan refinery
hit, the Bangkok refinery blast, the Cairo tanker fire, Macy's
100th parade postponement, SpaceX shares for every US child — are
listed in DATE CHECK and appear nowhere else in the image. Pure
Pillow, no network, byte-identical on every run.
"""
import os

from PIL import Image, ImageDraw, ImageFont

SIZE = (1024, 1024)
C = {
    "paper": (248, 244, 236), "ink": (24, 24, 24), "red": (186, 16, 28),
    "navy": (18, 32, 60), "teal": (13, 110, 102), "gold": (176, 84, 8),
    "grey": (104, 99, 88), "line": (208, 201, 186), "card": (255, 255, 255),
    "body": (60, 58, 52),
}
TAGC = {"CONFIRMED": (18, 110, 60), "OFFICIAL": (18, 60, 110),
        "REPORTED": (150, 110, 10), "CLAIM": (170, 60, 30)}

SERIF = ["/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf",
         "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"]
SAN_B = ["/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
         "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]
SAN_R = ["/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
         "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]


def load_font(bold, size, serif=False):
    for path in (SERIF if serif else SAN_B if bold else SAN_R):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            pass
    return ImageFont.load_default()


def fit(draw, text, fnt, width, limit):
    """Wrap text greedily to at most `limit` lines, ellipsising the tail."""
    out, rest = [], text.split()
    while rest and len(out) < limit:
        line, i = "", 0
        while i < len(rest):
            cand = (line + " " + rest[i]).strip()
            if draw.textlength(cand, font=fnt) <= width:
                line, i = cand, i + 1
            else:
                break
        if not line:
            line, i = rest[0], 1
        out.append(line)
        rest = rest[i:]
    if rest and out:
        tail = out[-1]
        while tail and draw.textlength(tail + " ...", font=fnt) > width:
            tail = tail.rsplit(" ", 1)[0] if " " in tail else ""
        out[-1] = (tail + " ...") if tail else "..."
    return out


def tag(draw, x, y, label):
    fnt = load_font(True, 10)
    w = draw.textlength(label, font=fnt) + 10
    draw.rounded_rectangle([x, y, x + w, y + 15], radius=7, fill=TAGC[label])
    draw.text((x + 5, y + 2), label, font=fnt, fill=(255, 255, 255))


def marker(draw, x, y, n):
    draw.ellipse([x - 8, y - 8, x + 8, y + 8], fill=C["red"],
                 outline=(255, 255, 255), width=2)
    fnt = load_font(True, 10)
    s = str(n)
    draw.text((x - draw.textlength(s, font=fnt) / 2, y - 6), s, font=fnt,
              fill=(255, 255, 255))


# ---------------------------------------------------------------- stories
# (number, place, region, tag, source, headline, body, art, big number)
# regions: NA North America, SA Latin America, EU Europe, ME Middle East,
# AF Africa, SAS South Asia, EA East Asia, SEA Southeast Asia, OC Oceania
HEROES = [
    (1, "USA", "NA", "REPORTED", "Adobe / NDTV",
     "BLACK FRIDAY OPENS: $12.9BN DAY AHEAD",
     "Adobe forecasts a record $12.9bn in US online spending; 126m Americans to shop today.",
     "bags", "$12.9B"),
    (2, "WELLINGTON", "OC", "OFFICIAL", "Electoral Commission / ET",
     "NZ FINAL COUNT LANDS TODAY",
     "Coalition loses its majority; 400,000 special votes decide a 67-seat hold.",
     "ballot", "67/131"),
    (3, "GAZA", "ME", "REPORTED", "Dawn / Reuters",
     "HAMAS WEIGHS REPLY AFTER 10 DIE IN GAZA",
     "Strikes kill 10, incl. a Hamas deputy minister; third night of attacks despite the ceasefire.",
     "night", "10"),
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
    (4, "LONDON", "EU", "OFFICIAL", "ONS / Reuters",
     "UK NET MIGRATION LOWEST SINCE '97",
     "Falls to 77,000 in the year to June, down from 204,000.",
     "down", "77,000"),
    (5, "GENEVA", "EU", "REPORTED", "NDTV",
     "GUKESH-SINDAROV GAME 3 ENDS DRAWN",
     "Marathon Game 3 ends 1\u00bd-\u00bd; Game 4 is played today.",
     "chess", "1\u00bd-\u00bd"),
    (6, "PARIS", "EU", "CONFIRMED", "BBC / Reuters",
     "DEPARDIEU TO STAND TRIAL FOR RAPE",
     "French court orders trial over alleged 2018 rape.",
     "court", "2018"),
    (7, "IBIZA", "EU", "REPORTED", "BBC",
     "TANKER CAPSIZES OFF IBIZA, ONE DEAD",
     "Diesel tanker carrying up to 7,000 tonnes capsizes; one killed.",
     "sea", "7,000T"),
    (8, "WASHINGTON", "NA", "CLAIM", "Reuters / AP",
     "TRUMP SEEKS PROBE INTO 'FAKE' GDP",
     "Demands inquiry after US growth is revised up to 4.3%.",
     "chart", "4.3%"),
    (9, "USA", "NA", "CONFIRMED", "NDTV / FlightAware",
     "THANKSGIVING STORM CUTS POWER TO 724,000",
     "Storm cancels 400 flights, delays 2,000+; 80m travel for the holiday.",
     "storm", "724,000"),
    (10, "NEW DELHI", "SAS", "OFFICIAL", "NDTV",
     "DELHI POLICE BUST CYBER SLAVERY RACKET",
     "164 foreigners rescued, incl. 92 Indonesians and 72 Malaysians.",
     "shield", "164"),
    (11, "PYONGYANG", "EA", "OFFICIAL", "AFP",
     "KIM VOWS TO EXPAND NUCLEAR PROGRAMME",
     "Kim calls for more warheads after Trump's outreach.",
     "missile", "KIM"),
    (12, "KYIV", "EU", "REPORTED", "Reuters",
     "ZELENSKY WARNS OF NEW MASS STRIKE",
     "Russian strikes kill 5 and cut power; Kyiv braces for more.",
     "jet", "5"),
    (13, "VADODARA", "SAS", "CONFIRMED", "NDTV",
     "INDIA U-19 WOMEN BEAT ENGLAND",
     "India win the T20 opener by 36 runs; Ahire hits 63 not out.",
     "bat", "36-RUN"),
]

# (text, source, region)
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

PINS = {1: (50, 28), 2: (282, 60), 3: (198, 44), 4: (138, 16), 5: (162, 22),
        6: (148, 36), 7: (130, 46), 8: (66, 40), 9: (78, 24), 10: (214, 50),
        11: (264, 26), 12: (186, 16), 13: (238, 62)}


# ------------------------------------------------------------------- art
def scene(draw, box, kind, big, bg):
    """Flat illustration for a hero card: motif plus a big word/number."""
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=bg)
    cx = (x0 + x1) // 2
    white = (255, 255, 255)
    if kind == "bags":
        for bx, bh, shade in ((x0 + 26, 58, (235, 120, 40)),
                              (cx - 30, 68, (250, 190, 40)),
                              (x1 - 86, 58, (120, 200, 220))):
            draw.rectangle([bx, y0 + 84 - bh, bx + 56, y0 + 84], fill=shade)
            draw.arc([bx + 12, y0 + 84 - bh - 16, bx + 44, y0 + 84 - bh + 8],
                     180, 360, fill=shade, width=4)
        for xx in (x0 + 14, x1 - 46):
            draw.ellipse([xx, y0 + 12, xx + 26, y0 + 38], fill=white)
    elif kind == "ballot":
        draw.rectangle([cx - 40, y0 + 40, cx + 40, y0 + 84], fill=white)
        draw.rectangle([cx - 48, y0 + 32, cx + 48, y0 + 42], fill=(240, 240, 240))
        draw.rectangle([cx - 12, y0 + 34, cx + 12, y0 + 40], fill=bg)
        draw.polygon([(cx - 52, y0 + 8), (cx - 30, y0 + 8), (cx - 30, y0 + 34),
                      (cx - 52, y0 + 34)], fill=white)
        draw.polygon([(cx - 46, y0 + 22), (cx - 40, y0 + 28), (cx - 32, y0 + 16)],
                     fill=(18, 110, 60))
        draw.ellipse([x0 + 16, y0 + 12, x0 + 40, y0 + 36], fill=(255, 210, 90))
        draw.ellipse([x1 - 40, y0 + 10, x1 - 16, y0 + 34], fill=white)
    elif kind == "night":
        draw.rectangle([x0, y1 - 30, x1, y1], fill=(10, 16, 34))
        for bx, bh in ((x0 + 18, 44), (x0 + 66, 58), (x0 + 118, 40),
                       (x0 + 168, 52), (x0 + 218, 46), (x0 + 262, 36)):
            draw.rectangle([bx, y1 - 30 - bh, bx + 36, y1 - 30], fill=(40, 48, 70))
        draw.ellipse([cx - 30, y0 + 30, cx + 30, y0 + 84], fill=(240, 90, 20))
        draw.ellipse([cx - 16, y0 + 46, cx + 16, y0 + 84], fill=(250, 190, 40))
        for px, py in ((x0 + 22, y0 + 12), (x1 - 30, y0 + 16), (x0 + 60, y0 + 24),
                       (cx + 60, y0 + 10)):
            draw.ellipse([px, py, px + 4, py + 4], fill=white)
    fnt = load_font(True, 30)
    draw.text((x1 - draw.textlength(big, font=fnt) - 10, y1 - 40), big,
              font=fnt, fill=white)


def panel(draw, box, kind, big, bg):
    """Big visual panel for a mid card: motif plus a big word/number."""
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=bg)
    cx = (x0 + x1) // 2
    white = (255, 255, 255)
    if kind in ("sea", "oil"):
        for yy in (y0 + 22, y0 + 38, y0 + 54):
            draw.arc([x0 + 14, yy - 10, x1 - 14, yy + 16], 0, 180,
                     fill=white, width=3)
        draw.polygon([(cx - 34, y0 + 10), (cx + 34, y0 + 10), (cx, y0 + 34)],
                     fill=white)
    elif kind == "chess":
        for i in range(5):
            for j in range(3):
                if (i + j) % 2 == 0:
                    draw.rectangle([x0 + 12 + i * 16, y0 + 10 + j * 16,
                                    x0 + 28 + i * 16, y0 + 26 + j * 16],
                                   fill=white)
        draw.ellipse([cx + 20, y0 + 12, cx + 40, y0 + 32], fill=white)
    elif kind == "missile":
        draw.polygon([(cx - 6, y0 + 6), (cx + 6, y0 + 6), (cx, y0 + 26)],
                     fill=white)
        draw.rectangle([cx - 6, y0 + 26, cx + 6, y0 + 48], fill=white)
    elif kind == "court":
        for xx in (x0 + 18, cx - 4, x1 - 34):
            draw.rectangle([xx, y0 + 14, xx + 14, y0 + 44], fill=white)
        draw.rectangle([x0 + 10, y0 + 44, x1 - 10, y0 + 50], fill=white)
    elif kind in ("jet", "radar"):
        draw.polygon([(x0 + 20, y0 + 38), (x1 - 30, y0 + 26), (x1 - 14, y0 + 32),
                      (x1 - 30, y0 + 38), (x0 + 20, y0 + 44)], fill=white)
        draw.polygon([(cx - 10, y0 + 14), (cx + 6, y0 + 14), (cx + 2, y0 + 34),
                      (cx - 14, y0 + 34)], fill=white)
        draw.polygon([(cx + 8, y0 + 40), (cx + 22, y0 + 40), (cx + 16, y0 + 52),
                      (cx + 4, y0 + 52)], fill=white)
    elif kind == "down":
        draw.line([x0 + 18, y0 + 16, cx, y0 + 34, x1 - 18, y0 + 52],
                  fill=white, width=5)
        draw.polygon([(x1 - 18, y0 + 52), (x1 - 34, y0 + 46), (x1 - 30, y0 + 60)],
                     fill=white)
    elif kind == "chart":
        draw.line([x0 + 16, y0 + 52, x0 + 60, y0 + 36, x0 + 104, y0 + 42,
                   x0 + 148, y0 + 22], fill=white, width=5)
        draw.polygon([(x0 + 148, y0 + 22), (x0 + 160, y0 + 22), (x0 + 148, y0 + 34)],
                     fill=white)
    elif kind == "storm":
        draw.ellipse([cx - 34, y0 + 12, cx + 10, y0 + 40], fill=white)
        draw.ellipse([cx - 10, y0 + 6, cx + 34, y0 + 34], fill=white)
        draw.polygon([(cx - 6, y0 + 36), (cx + 8, y0 + 36), (cx - 2, y0 + 52),
                      (cx + 12, y0 + 52), (cx - 8, y0 + 74), (cx + 2, y0 + 52),
                      (cx - 10, y0 + 52)], fill=(255, 210, 90))
    elif kind == "shield":
        draw.polygon([(cx, y0 + 8), (cx + 26, y0 + 18), (cx + 26, y0 + 44),
                      (cx, y0 + 62), (cx - 26, y0 + 44), (cx - 26, y0 + 18)],
                     fill=white)
        draw.line([cx - 12, y0 + 34, cx - 4, y0 + 44, cx + 14, y0 + 24],
                  fill=bg, width=4)
    elif kind == "bat":
        draw.rectangle([cx - 24, y0 + 10, cx - 8, y0 + 52], fill=white)
        draw.rectangle([cx - 22, y0 + 52, cx - 10, y0 + 66], fill=white)
        draw.ellipse([cx + 12, y0 + 14, cx + 34, y0 + 36], fill=(255, 210, 90))
    size = 30
    while size > 14 and draw.textlength(big, font=load_font(True, size)) > (x1 - x0) - 16:
        size -= 2
    fnt = load_font(True, size)
    draw.text((x1 - draw.textlength(big, font=fnt) - 8, y1 - size - 8), big,
              font=fnt, fill=white)


# ------------------------------------------------------------------ build
def build():
    im = Image.new("RGB", SIZE, C["paper"])
    draw = ImageDraw.Draw(im)
    mx = 24
    # masthead
    draw.text((mx, 14), "FRIDAY 27 NOVEMBER 2026",
              font=load_font(True, 40, serif=True), fill=C["ink"])
    draw.text((mx, 60), "THE WORLD IN ONE PAGE  \u00b7  36 dated stories  \u00b7  9 regions",
              font=load_font(True, 15), fill=C["grey"])
    draw.text((SIZE[0] - mx - 150, 22), "ONE DAY.",
              font=load_font(True, 26, serif=True), fill=C["red"])
    draw.text((SIZE[0] - mx - 150, 52), "EVERY REGION.",
              font=load_font(True, 15), fill=C["ink"])
    draw.line([mx, 84, SIZE[0] - mx, 84], fill=C["ink"], width=2)
    # red headline strip
    draw.rectangle([mx, 90, SIZE[0] - mx, 114], fill=C["red"])
    strip = ("1  BLACK FRIDAY OPENS   \u2022   2  NZ FINAL COUNT LANDS   \u2022   "
             "3  HAMAS WEIGHS REPLY AFTER 10 DIE IN GAZA")
    draw.text((mx + 10, 97), strip, font=load_font(True, 15), fill=(255, 255, 255))
    # UTC timeline
    draw.text((mx, 120), "FRIDAY UTC", font=load_font(True, 11), fill=C["red"])
    draw.line([mx + 108, 128, SIZE[0] - mx, 128], fill=C["line"], width=2)
    marks = [("01:00", "NZ final count lands"), ("06:00", "Tokyo prices out"),
             ("11:00", "Black Friday opens"), ("14:00", "Game 4, Geneva"),
             ("18:00", "Storm peaks, US East"), ("24:00", "Day ends")]
    step = (SIZE[0] - 2 * mx - 108) / 5
    for i, (when, what) in enumerate(marks):
        x = mx + 108 + i * step
        draw.ellipse([x - 3, 125, x + 3, 131], fill=C["red"])
        tw = draw.textlength(when, font=load_font(True, 9))
        tx = min(max(x - tw / 2, mx + 108), SIZE[0] - mx - tw)
        draw.text((tx, 114), when, font=load_font(True, 9), fill=C["ink"])
        lw = draw.textlength(what, font=load_font(False, 9))
        lx = min(max(x - lw / 2, mx + 108), SIZE[0] - mx - lw)
        draw.text((lx, 132), what, font=load_font(False, 9), fill=C["grey"])
    # heroes: three across the top half
    hy, hh = 142, 194
    hw = (SIZE[0] - 2 * mx - 2 * 12) // 3
    bgs = [C["navy"], C["teal"], C["gold"]]
    for i, (n, place, region, badge, src, head, body, art, big) in enumerate(HEROES):
        x0 = mx + i * (hw + 12)
        x1 = x0 + hw
        draw.rounded_rectangle([x0, hy, x1, hy + hh], radius=8, fill=C["card"],
                               outline=C["line"], width=1)
        scene(draw, (x0 + 1, hy + 1, x1 - 1, hy + 84), art, big, bgs[i])
        marker(draw, x0 + 16, hy + 16, n)
        draw.text((x0 + 10, hy + 90), place, font=load_font(True, 11), fill=C["red"])
        for j, ln in enumerate(fit(draw, head, load_font(True, 17), hw - 20, 2)):
            draw.text((x0 + 10, hy + 104 + j * 20), ln, font=load_font(True, 17),
                      fill=C["ink"])
        for j, ln in enumerate(fit(draw, body, load_font(False, 12.5), hw - 20, 2)):
            draw.text((x0 + 10, hy + 142 + j * 15), ln, font=load_font(False, 12.5),
                      fill=C["body"])
        draw.text((x0 + 10, hy + hh - 16), src, font=load_font(False, 10),
                  fill=C["grey"])
        tag(draw, x1 - 78, hy + hh - 18, badge)
    # numbers band
    ny = 344
    draw.rectangle([mx, ny, SIZE[0] - mx, ny + 48], fill=C["navy"])
    draw.text((mx + 12, ny + 7), "THE DAY\nIN NUMBERS", font=load_font(True, 12),
              fill=(255, 255, 255))
    seg = (SIZE[0] - 2 * mx - 150) // 6
    for i, (num, cap) in enumerate(NUMBERS):
        x = mx + 150 + i * seg
        draw.text((x, ny + 2), num, font=load_font(True, 24), fill=(255, 210, 90))
        for j, ln in enumerate(cap.split("\n")):
            draw.text((x, ny + 27 + j * 10), ln, font=load_font(False, 9.5),
                      fill=(220, 225, 235))
        if i:
            draw.line([x - 8, ny + 7, x - 8, ny + 41], fill=(90, 105, 130), width=1)
    # region pills
    counts = {}
    for story in HEROES + CARDS:
        counts[story[2]] = counts.get(story[2], 0) + 1
    for _, _, region in BRIEFS:
        counts[region] = counts.get(region, 0) + 1
    px, py = mx, 400
    for name, code in REGIONS:
        label = f"{name} {counts.get(code, 0)}"
        fnt = load_font(True, 11)
        w = draw.textlength(label, font=fnt) + 16
        draw.rounded_rectangle([px, py, px + w, py + 20], radius=10,
                               fill=(255, 255, 255), outline=C["line"], width=1)
        draw.text((px + 8, py + 4), label, font=fnt, fill=C["ink"])
        px += w + 7
    # mid cards: two rows of five
    gy, gh = 428, 171
    cw = (SIZE[0] - 2 * mx - 4 * 10) // 5
    cols = [C["navy"], C["teal"], C["gold"], (120, 40, 90), (40, 90, 120),
            (90, 90, 40), (150, 60, 20), (30, 90, 60), (100, 30, 60), (60, 60, 120)]
    for i, (n, place, region, badge, src, head, body, art, big) in enumerate(CARDS):
        row, col = divmod(i, 5)
        x0 = mx + col * (cw + 10)
        y0 = gy + row * (gh + 8)
        x1, y1 = x0 + cw, y0 + gh
        draw.rounded_rectangle([x0, y0, x1, y1], radius=6, fill=C["card"],
                               outline=C["line"], width=1)
        panel(draw, (x0 + 1, y0 + 1, x1 - 1, y0 + 84), art, big, cols[i])
        marker(draw, x0 + 13, y0 + 13, n)
        for j, ln in enumerate(fit(draw, head, load_font(True, 11.5), cw - 16, 2)):
            draw.text((x0 + 8, y0 + 90 + j * 14), ln, font=load_font(True, 11.5),
                      fill=C["ink"])
        for j, ln in enumerate(fit(draw, body, load_font(False, 10), cw - 16, 2)):
            draw.text((x0 + 8, y0 + 120 + j * 12), ln, font=load_font(False, 10),
                      fill=C["body"])
        draw.text((x0 + 8, y1 - 13), src, font=load_font(False, 9), fill=C["grey"])
        tag(draw, x1 - 80, y1 - 14, badge)
    # bottom band: map and date check left, briefs right
    by = 786
    draw.text((mx, by), "WHERE IT HAPPENED", font=load_font(True, 12), fill=C["navy"])
    mapx, mapy, mapw, maph = mx, by + 20, 306, 124
    draw.rounded_rectangle([mapx, mapy, mapx + mapw, mapy + maph], radius=6,
                           fill=(205, 225, 238), outline=C["line"], width=1)
    land = (150, 175, 140)
    draw.polygon([(mapx + 16, mapy + 22), (mapx + 84, mapy + 16), (mapx + 92, mapy + 34),
                  (mapx + 66, mapy + 48), (mapx + 32, mapy + 46), (mapx + 14, mapy + 34)],
                 fill=land)
    draw.polygon([(mapx + 82, mapy + 52), (mapx + 104, mapy + 50), (mapx + 110, mapy + 68),
                  (mapx + 96, mapy + 74), (mapx + 84, mapy + 62)], fill=land)
    draw.polygon([(mapx + 146, mapy + 16), (mapx + 176, mapy + 14), (mapx + 182, mapy + 32),
                  (mapx + 164, mapy + 38), (mapx + 148, mapy + 32)], fill=land)
    draw.polygon([(mapx + 156, mapy + 40), (mapx + 184, mapy + 38), (mapx + 190, mapy + 62),
                  (mapx + 176, mapy + 72), (mapx + 160, mapy + 58)], fill=land)
    draw.polygon([(mapx + 184, mapy + 14), (mapx + 280, mapy + 12), (mapx + 292, mapy + 32),
                  (mapx + 264, mapy + 46), (mapx + 220, mapy + 44), (mapx + 190, mapy + 32)],
                 fill=land)
    draw.ellipse([mapx + 258, mapy + 50, mapx + 276, mapy + 58], fill=land)
    draw.ellipse([mapx + 278, mapy + 58, mapx + 300, mapy + 68], fill=land)
    for n, (px_, py_) in PINS.items():
        marker(draw, mapx + px_, mapy + py_, n)
    draw.text((mapx + 8, mapy + maph - 14), "Pins 1-13: heroes and mid cards",
              font=load_font(False, 9), fill=C["navy"])
    # date check box under the map
    dx, dw = mx, mapw
    ty = mapy + maph + 8
    draw.rounded_rectangle([dx, ty, dx + dw, ty + 66], radius=6,
                           fill=(255, 248, 230), outline=(220, 190, 120), width=1)
    draw.text((dx + 8, ty + 4), "DATE CHECK \u2014 LEFT OUT ON PURPOSE",
              font=load_font(True, 10), fill=C["gold"])
    for i, (item, when) in enumerate(DATECHECK):
        y = ty + 17 + i * 9
        whenw = draw.textlength(when, font=load_font(True, 8.5))
        text = item
        f9 = load_font(False, 9)
        while text and draw.textlength("x " + text, font=f9) > dw - 16 - whenw - 6:
            text = text.rsplit(" ", 1)[0] if " " in text else ""
        draw.text((dx + 8, y), "x " + text, font=f9, fill=(90, 80, 60))
        draw.text((dx + dw - 8 - whenw, y), when, font=load_font(True, 8.5),
                  fill=C["gold"])
    # briefs on the right
    bx = mapx + mapw + 12
    bw = SIZE[0] - mx - bx
    draw.text((bx, by), "THE REST OF THE DAY \u2014 23 MORE STORIES",
              font=load_font(True, 13), fill=C["red"])
    draw.line([bx, by + 18, SIZE[0] - mx, by + 18], fill=C["line"], width=1)
    bf = load_font(False, 12)
    colw = (bw - 8) // 2
    half = 12
    for i, (txt, src, _) in enumerate(BRIEFS):
        col, row = divmod(i, half)
        x = bx if col == 0 else bx + colw + 8
        y = by + 24 + row * 17
        draw.text((x, y), f"{14 + i}.", font=load_font(True, 11), fill=C["red"])
        srcw = draw.textlength(src, font=load_font(False, 8.5))
        avail = colw - 24 - srcw - 10
        t = txt
        while t and draw.textlength(t + " ...", font=bf) > avail:
            t = t.rsplit(" ", 1)[0] if " " in t else ""
        if t != txt:
            t = t + " ..."
        draw.text((x + 24, y), t, font=bf, fill=C["ink"])
        draw.text((x + colw - 8 - srcw, y + 1), src, font=load_font(False, 8.5),
                  fill=C["grey"])
    # footer: how sure + sources
    draw.text((mx, SIZE[1] - 16),
              "HOW SURE: CONFIRMED verified \u00b7 OFFICIAL announced \u00b7 "
              "REPORTED sourced \u00b7 CLAIM alleged  |  Reuters \u00b7 AP \u00b7 Dawn \u00b7 AFP \u00b7 "
              "BBC \u00b7 ONS \u00b7 NDTV \u00b7 ET \u00b7 Qatar Tribune \u00b7 NZ Herald \u00b7 Guardian",
              font=load_font(False, 9), fill=C["grey"])
    return im


if __name__ == "__main__":
    out = os.environ.get("OUT", "entry.png")
    img = build()
    img.save(out, optimize=True)
    print(out, img.size, os.path.getsize(out), "bytes")
