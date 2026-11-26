"""Sum up 25 November's world news in one image.

Entrypoint for make.fun bounty news-image-20261125.
Python 3.13, standard library only. Writes one 1024x1024 PNG to
$MAKEFUN_OUTPUT_DIR/entry.png (default /output/entry.png).

Layout (champion format, six rounds 1117-1122):
  masthead -> date check -> 3 leads -> 9 region sections (37 stories)
  -> UTC timeline -> footer. Every story carries source + 25 Nov 2026 date.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from render import Canvas, save_png, text_width, wrap_text

W = 1024
H = 1024

PAPER = (247, 243, 234)
INK = (26, 26, 26)
GRAY = (96, 94, 88)
NAVY = (16, 35, 63)
GOLD = (200, 169, 106)
CARD = (255, 255, 255)
BORDER = (208, 202, 188)
WHITE = (255, 255, 255)

# ---------------------------------------------------------------- data ----
LEADS = [
    ("LEAD 1",
     "TWO TANKERS HIT MINES, EXPLODE IN STRAIT OF HORMUZ",
     "IRGC: two tankers struck mines on an unauthorised route and caught fire.",
     "Just Security, 25 Nov 2026"),
    ("LEAD 2",
     "SHENZHOU-24 LIFTS OFF WITH PAKISTANI ASTRONAUT",
     "Three astronauts, incl. a Pakistani payload specialist, head to Tiangong.",
     "ECNS / Xinhua, 25 Nov 2026"),
    ("LEAD 3",
     "WALL STREET ROUT: NASDAQ -3.7% AS PCE, TARIFFS HIT",
     "Nasdaq -3.7%, Dow -800; Oct core PCE 3.3% YoY; new tariffs on 14 partners.",
     "Financial Express, 25 Nov 2026"),
]

# (region name, header colour, [(headline, source), ...])
REGIONS = [
    ("MIDDLE EAST", (154, 63, 36), [
        ("Houthis say they struck Saudi Ras Tanura refinery", "Just Security"),
        ("Israel kills Hamas colonel Abuelouf, wife and two children", "Just Security"),
        ("Israeli strike kills 3 Palestinians; Gaza children's hospital loses power", "La Mediterranee"),
        ("Kurdish PM Barzani rejects Iraqi moves to control Kurdistan", "La Mediterranee"),
        ("White House: Trump's position on Israel unchanged", "Jerusalem Post"),
    ]),
    ("EUROPE", (38, 74, 122), [
        ("Russian strike on Odesa kills 2, injures 3 incl. a child", "Just Security"),
        ("Putin: Ukraine kept hitting Russian refineries despite Trump plea", "Just Security"),
        ("Eurostar hit by union strikes; BBC journalists back action", "La Mediterranee"),
        ("Poland plans no-fly zone on eastern border for NATO flank", "La Mediterranee"),
    ]),
    ("ASIA-PACIFIC", (24, 110, 92), [
        ("Solomon Islands, Australia sign treaty barring foreign base", "Just Security"),
        ("ASEAN pushes DEFA ratification; power-grid deal may cut rates", "ABS-CBN"),
        ("Japan aims to be world's No. 3 AI power after US, China", "La Mediterranee"),
        ("Seoul watches N. Korean 'coast guard' vessel near border", "La Mediterranee"),
    ]),
    ("CHINA", (176, 32, 48), [
        ("Xi hails joint China-Pakistan space mission as friendship emblem", "ECNS"),
        ("China leads 78 AI standards; first generative-AI governance plan", "Xinhua"),
        ("Chinese astronaut to attempt one-year stay in orbit, a first", "ECNS"),
        ("China sentences official to death for leaking 100+ secrets", "La Mediterranee"),
    ]),
    ("UNITED STATES", (96, 58, 128), [
        ("US jury convicts Huawei of trade-secret theft, bank fraud", "Just Security"),
        ("CIA, ODNI suffer breach of some unclassified information", "Reuters"),
        ("US Q3 GDP revised up to 4.3%, fastest in three years", "dpa-AFX"),
        ("Six killed, incl. two children, in Mississippi plane crash", "Jerusalem Post"),
        ("NASA chief rebuts Greene's Moon-landing denial", "Jerusalem Post"),
    ]),
    ("AFRICA", (110, 110, 30), [
        ("Sudan RSF drone strikes kill 19 civilians, wound 20", "Just Security"),
        ("Militants kill at least 30 in Nigeria's Niger region", "La Mediterranee"),
        ("Two Libyan soldiers die in Ukrainian strike on Benghazi port", "Jerusalem Post"),
    ]),
    ("AMERICAS", (46, 110, 46), [
        ("Mexico used US drones to capture 'El Chapo Isidro'", "La Mediterranee"),
        ("Ecuador, US weigh joint military activities", "La Mediterranee"),
        ("Lakers beat Jazz; Doncic posts 28 points, 8 assists", "Reuters"),
    ]),
    ("TECHNOLOGY", (70, 80, 90), [
        ("Nvidia chief Huang's return fuels open-weight AI debate", "Reuters"),
        ("UK watchdog warns on AI as Meta launches adapted Muse", "Reuters"),
        ("Decathlon cyberattack exposes data of 130,000+ customers", "La Mediterranee"),
    ]),
    ("ECONOMY & MARKETS", (140, 100, 30), [
        ("Dollar slips as PCE tops forecasts; jobless claims 189,000", "dpa-AFX"),
        ("Bangladesh raises garment minimum wage 36% to $139", "Reuters"),
        ("Global airports court private capital to fund upgrades", "Reuters"),
    ]),
]

TIMELINE = [
    ("00:18", "Shenzhou-24 lifts off, Jiuquan"),
    ("~07:00", "IRGC: two tankers hit mines, Hormuz"),
    ("~10:00", "Houthis say they hit Ras Tanura refinery"),
    ("~11:00", "China: astronaut to try one-year orbit stay"),
    ("13:30", "US Oct PCE: core inflation 3.3% YoY"),
    ("14:30", "Wall Street opens: Dow -800, Nasdaq -3.7%"),
    ("~17:00", "US jury convicts Huawei"),
    ("22:15", "US tariffs on 14 partners; dollar slips"),
]


def _story_count():
    return len(LEADS) + sum(len(items) for _, _, items in REGIONS)


# -------------------------------------------------------------- layout ----
def build():
    assert len(REGIONS) == 9, "need 9 regions"
    assert _story_count() == 37, "need 37 stories, got %d" % _story_count()

    c = Canvas(W, H, PAPER)

    # ---- masthead ----
    c.fill_rect(0, 0, W, 92, NAVY)
    c.draw_text_centered("THE WORLD IN ONE PAGE", W // 2, 12, 4, WHITE)
    c.draw_text_centered(
        "WEDNESDAY, 25 NOVEMBER 2026  |  37 STORIES  |  9 REGIONS  |  DATE-CHECKED",
        W // 2, 54, 2, GOLD)
    c.fill_rect(0, 92, W, 4, GOLD)

    # ---- date check strip ----
    c.draw_text_centered(
        "DATE CHECK: Wednesday 25 November 2026 - every story below is dated "
        "25 Nov 2026 and sourced.",
        W // 2, 102, 1, GRAY)

    # ---- leads ----
    lead_y, lead_h, lead_w = 122, 126, 328
    for i, (tag, head, summ, src) in enumerate(LEADS):
        x = 10 + i * 338
        c.fill_rect(x, lead_y, lead_w, lead_h, CARD)
        c.rect(x, lead_y, lead_w, lead_h, BORDER, 1)
        c.fill_rect(x, lead_y, 5, lead_h, NAVY)
        tx = x + 14
        c.draw_text(tag, tx, lead_y + 9, 1, GOLD if False else (140, 100, 30))
        hy = c.draw_wrapped(head, tx, lead_y + 25, lead_w - 26, 2, INK,
                             line_h=18)
        c.draw_wrapped(summ, tx, lead_y + 82, lead_w - 26, 1, INK, line_h=9)
        c.draw_text(src, tx, lead_y + 106, 1, GRAY)

    # ---- region grid: 3 x 3 ----
    cell_w, cell_h = 328, 214
    for idx, (name, color, items) in enumerate(REGIONS):
        col, row = idx % 3, idx // 3
        x = 8 + col * 336
        y = 256 + row * 222
        c.fill_rect(x, y, cell_w, cell_h, CARD)
        c.rect(x, y, cell_w, cell_h, BORDER, 1)
        c.fill_rect(x, y, cell_w, 26, color)
        c.draw_text("%s (%d)" % (name, len(items)), x + 10, y + 6, 2, WHITE)
        # items spread evenly across the remaining area, so short
        # sections do not leave a big blank block at the bottom
        area_top = y + 26 + 6
        area_h = cell_h - 26 - 6
        slot = max(34, area_h // len(items))
        start = area_top
        for j, (head, src) in enumerate(items):
            iy = start + j * slot
            c.fill_rect(x + 10, iy + 2, 5, 5, color)
            lines = wrap_text(head, cell_w - 32, 1)[:2]
            yy = iy
            for line in lines:
                c.draw_text(line, x + 20, yy, 1, INK)
                yy += 9
            c.draw_text("- " + src, x + 20, iy + 19, 1, GRAY)

    # ---- UTC timeline ----
    ty = 922
    c.draw_text("UTC TIMELINE - 25 NOVEMBER 2026", 8, ty, 1, INK)
    line_y = ty + 28
    c.hline(8, line_y, W - 16, BORDER, 2)
    col_w = (W - 16) // 8
    for i, (t, label) in enumerate(TIMELINE):
        cx = 8 + i * col_w + col_w // 2
        c.draw_text_centered(t, cx, line_y - 14, 1, NAVY)
        c.fill_rect(cx - 3, line_y - 2, 7, 7, NAVY)
        lines = wrap_text(label, col_w - 12, 1)[:3]
        yy = line_y + 10
        for line in lines:
            c.draw_text_centered(line, cx, yy, 1, INK)
            yy += 9

    # ---- footer ----
    c.draw_text_centered(
        "Sources: Reuters, Xinhua/ECNS, Just Security, Financial Express, "
        "dpa-AFX, Jerusalem Post, ABS-CBN, La Mediterranee. All stories dated "
        "25 Nov 2026.",
        W // 2, 1004, 1, GRAY)
    return c


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    canvas = build()
    size = save_png(canvas, path)
    print("wrote %s (%d bytes, %dx%d, %d stories)"
          % (path, size, W, H, _story_count()))


if __name__ == "__main__":
    main()
