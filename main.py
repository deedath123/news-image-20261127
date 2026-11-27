#!/usr/bin/env python3
"""THE WORLD TODAY - Friday 27 November 2026. One-image newspaper.

Python 3.13 stdlib ONLY. Hand-rolled zlib/struct PNG encoder plus a
self-defined 5x7 bitmap font. No network, fully deterministic: every run
writes the same bytes. Writes entry.png (1024x1024) to MAKEFUN_OUTPUT_DIR
or /output.

Layout: navy masthead, red lead banner (Jazan refinery), 15 pictured
stories in a 5x3 grid with flat pictograms, dotted world map with numbered
dots + key, by-the-numbers strip, 20 listed stories. 35 stories total.
"""
import os
import struct
import sys
import zlib

W, H = 1024, 1024
CREAM = (247, 243, 232)
PAPER = (255, 253, 247)
NAVY = (18, 32, 62)
NAVY2 = (28, 48, 92)
RED = (178, 34, 34)
GOLD = (176, 124, 24)
INK = (24, 24, 24)
GREY = (110, 110, 105)
LINE = (205, 198, 182)
MAPBG = (226, 233, 240)
LAND = (132, 142, 158)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
ORANGE = (214, 96, 20)
YELLOW = (232, 184, 32)
GREEN = (34, 128, 74)
SKY = (70, 130, 180)

# ---------------------------------------------------------------- font
# 5x7 bitmap font, each glyph = 7 rows of 5 bits (MSB = left column).
# Uppercase + digits + punctuation only; all page text is uppercased.
FONT = {
    'A': (0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    'B': (0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E),
    'C': (0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E),
    'D': (0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E),
    'E': (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F),
    'F': (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10),
    'G': (0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F),
    'H': (0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    'I': (0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    'J': (0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C),
    'K': (0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11),
    'L': (0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F),
    'M': (0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11),
    'N': (0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11),
    'O': (0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    'P': (0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10),
    'Q': (0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D),
    'R': (0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11),
    'S': (0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E),
    'T': (0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    'U': (0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    'V': (0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04),
    'W': (0x11, 0x11, 0x11, 0x15, 0x15, 0x15, 0x0A),
    'X': (0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11),
    'Y': (0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04),
    'Z': (0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F),
    '0': (0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E),
    '1': (0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E),
    '2': (0x0E, 0x11, 0x01, 0x06, 0x08, 0x10, 0x1F),
    '3': (0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E),
    '4': (0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02),
    '5': (0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E),
    '6': (0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E),
    '7': (0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08),
    '8': (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
    '9': (0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C),
    ' ': (0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00),
    '.': (0x00, 0x00, 0x00, 0x00, 0x00, 0x0C, 0x0C),
    ',': (0x00, 0x00, 0x00, 0x00, 0x0C, 0x04, 0x08),
    ':': (0x00, 0x0C, 0x0C, 0x00, 0x0C, 0x0C, 0x00),
    ';': (0x00, 0x0C, 0x0C, 0x00, 0x0C, 0x04, 0x08),
    "'": (0x04, 0x04, 0x08, 0x00, 0x00, 0x00, 0x00),
    '-': (0x00, 0x00, 0x00, 0x0E, 0x00, 0x00, 0x00),
    '/': (0x01, 0x02, 0x02, 0x04, 0x08, 0x08, 0x10),
    '(': (0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02),
    ')': (0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08),
    '%': (0x19, 0x1A, 0x02, 0x04, 0x08, 0x0B, 0x13),
    '+': (0x00, 0x04, 0x04, 0x0E, 0x04, 0x04, 0x00),
    '&': (0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D),
    '!': (0x04, 0x04, 0x04, 0x04, 0x04, 0x00, 0x04),
    '?': (0x0E, 0x11, 0x01, 0x06, 0x04, 0x00, 0x04),
    '=': (0x00, 0x00, 0x1F, 0x00, 0x1F, 0x00, 0x00),
    '"': (0x0A, 0x0A, 0x00, 0x00, 0x00, 0x00, 0x00),
    '*': (0x00, 0x15, 0x0E, 0x15, 0x00, 0x00, 0x00),
    '#': (0x0A, 0x0A, 0x1F, 0x0A, 0x1F, 0x0A, 0x0A),
    '$': (0x04, 0x0F, 0x14, 0x0E, 0x05, 0x1E, 0x04),
    '@': (0x0E, 0x11, 0x17, 0x15, 0x16, 0x10, 0x0E),
    '<': (0x02, 0x04, 0x08, 0x10, 0x08, 0x04, 0x02),
    '>': (0x08, 0x04, 0x02, 0x01, 0x02, 0x04, 0x08),
    '_': (0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x1F),
    '[': (0x0E, 0x08, 0x08, 0x08, 0x08, 0x08, 0x0E),
    ']': (0x0E, 0x02, 0x02, 0x02, 0x02, 0x02, 0x0E),
    '\\': (0x10, 0x08, 0x08, 0x04, 0x02, 0x02, 0x01),
    '|': (0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    '`': (0x08, 0x04, 0x00, 0x00, 0x00, 0x00, 0x00),
    '^': (0x04, 0x0A, 0x11, 0x00, 0x00, 0x00, 0x00),
    '~': (0x00, 0x00, 0x09, 0x16, 0x00, 0x00, 0x00),
}
BLANK = (0x00,) * 7
CHAR_W = 6  # advance per char at scale 1 (5 px glyph + 1 px gap)


def text_width(text, scale):
    return len(text) * CHAR_W * scale


def wrap(text, max_w, scale):
    """Greedy word wrap; returns list of lines fitting max_w pixels."""
    lines = []
    for para in text.split('\n'):
        words = para.split(' ')
        cur = ''
        for w in words:
            trial = w if not cur else cur + ' ' + w
            if text_width(trial, scale) <= max_w or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = w
        if cur or not lines:
            lines.append(cur)
    return lines


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(w * h * 3)
        self.rect(0, 0, w, h, bg)

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def rect(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i], self.px[i + 1], self.px[i + 2] = c

    def hline(self, x, y, w, c):
        self.rect(x, y, w, 1, c)

    def vline(self, x, y, h, c):
        self.rect(x, y, 1, h, c)

    def line(self, x0, y0, x1, y1, c):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set(x0, y0, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def poly(self, pts, c):
        """Filled polygon, scanline even-odd fill."""
        if len(pts) < 3:
            return
        ymin = min(y for _, y in pts)
        ymax = max(y for _, y in pts)
        n = len(pts)
        for y in range(ymin, ymax + 1):
            xs = []
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if y0 == y1:
                    continue
                if (y0 <= y < y1) or (y1 <= y < y0):
                    t = (y + 0.5 - y0) / (y1 - y0)
                    xs.append(x0 + t * (x1 - x0))
            xs.sort()
            for j in range(0, len(xs) - 1, 2):
                xa, xb = int(xs[j]), int(xs[j + 1])
                self.rect(xa, y, xb - xa + 1, 1, c)

    def ellipse(self, cx, cy, rx, ry, c):
        for dy in range(-ry, ry + 1):
            t = 1.0 - (dy * dy) / float(ry * ry)
            dx = int(rx * (t ** 0.5)) if t > 0 else 0
            self.rect(cx - dx, cy + dy, 2 * dx + 1, 1, c)

    def circle(self, cx, cy, r, c):
        self.ellipse(cx, cy, r, r, c)

    def ring(self, cx, cy, r, c):
        for dy in range(-r, r + 1):
            t = 1.0 - (dy * dy) / float(r * r)
            dx = int(r * (t ** 0.5)) if t > 0 else 0
            self.set(cx - dx, cy + dy, c)
            self.set(cx + dx, cy + dy, c)

    def text(self, x, y, s, scale, c):
        s = s.upper()
        cx = x
        for ch in s:
            rows = FONT.get(ch, BLANK)
            for ry in range(7):
                bits = rows[ry]
                for bx in range(5):
                    if bits & (1 << (4 - bx)):
                        self.rect(cx + bx * scale, y + ry * scale,
                                  scale, scale, c)
            cx += CHAR_W * scale

    def text_center(self, cx, y, s, scale, c):
        self.text(cx - text_width(s, scale) // 2, y, s, scale, c)


# ---------------------------------------------------------------- PNG out
def _chunk(tag, data):
    out = struct.pack('>I', len(data)) + tag + data
    out += struct.pack('>I', zlib.crc32(tag + data) & 0xFFFFFFFF)
    return out


def write_png(path, cv):
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * stride:(y + 1) * stride]
    png = b'\x89PNG\r\n\x1a\n'
    png += _chunk(b'IHDR', struct.pack('>IIBBBBB', cv.w, cv.h, 8, 2, 0, 0, 0))
    png += _chunk(b'IDAT', zlib.compress(bytes(raw), 9))
    png += _chunk(b'IEND', b'')
    with open(path, 'wb') as f:
        f.write(png)

# ---------------------------------------------------------------- pictograms
# Flat, simple pictograms drawn in a ~56x44 box centred on (cx, cy).
def pic_fire(cv, cx, cy):
    cv.poly([(cx - 13, cy + 16), (cx - 15, cy + 2), (cx - 7, cy - 8),
             (cx - 2, cy - 18), (cx + 4, cy - 7), (cx + 12, cy - 2),
             (cx + 15, cy + 10), (cx + 7, cy + 16)], RED)
    cv.poly([(cx - 7, cy + 16), (cx - 8, cy + 6), (cx - 2, cy - 2),
             (cx + 3, cy + 4), (cx + 8, cy + 8), (cx + 4, cy + 16)],
            ORANGE)
    cv.ellipse(cx, cy + 12, 4, 5, YELLOW)


def pic_storm(cv, cx, cy):
    # grey cloud + blue rain + yellow lightning, flat and simple
    cv.ellipse(cx - 11, cy - 8, 13, 10, (88, 96, 110))
    cv.ellipse(cx + 9, cy - 8, 12, 10, (88, 96, 110))
    cv.rect(cx - 22, cy - 10, 44, 9, (88, 96, 110))
    cv.ellipse(cx, cy - 12, 10, 8, (88, 96, 110))
    cv.line(cx - 15, cy + 4, cx - 18, cy + 14, SKY)
    cv.line(cx - 5, cy + 4, cx - 8, cy + 14, SKY)
    cv.line(cx + 5, cy + 4, cx + 2, cy + 14, SKY)
    cv.poly([(cx + 12, cy + 0), (cx + 19, cy + 0), (cx + 14, cy + 9),
             (cx + 18, cy + 9), (cx + 9, cy + 20), (cx + 11, cy + 10),
             (cx + 8, cy + 10)], YELLOW)


def pic_football(cv, cx, cy):
    cv.ellipse(cx, cy, 20, 13, (122, 74, 34))
    cv.ellipse(cx, cy, 20, 13, (122, 74, 34))
    cv.rect(cx - 20, cy - 2, 40, 4, (232, 226, 210))
    cv.line(cx - 4, cy - 12, cx - 4, cy + 12, WHITE)
    cv.line(cx + 4, cy - 12, cx + 4, cy + 12, WHITE)
    cv.rect(cx - 8, cy - 1, 16, 2, WHITE)


def pic_lock(cv, cx, cy):
    cv.rect(cx - 9, cy - 12, 18, 7, (120, 124, 130))
    cv.rect(cx - 6, cy - 12, 12, 7, CREAM)
    cv.rect(cx - 13, cy - 6, 26, 20, NAVY2)
    cv.circle(cx, cy + 2, 3, GOLD)
    cv.rect(cx - 1, cy + 2, 2, 6, GOLD)


def pic_missile(cv, cx, cy):
    cv.poly([(cx - 20, cy - 4), (cx + 8, cy - 4), (cx + 20, cy),
             (cx + 8, cy + 4), (cx - 20, cy + 4)], (150, 156, 164))
    cv.poly([(cx - 20, cy - 4), (cx - 14, cy - 12), (cx - 8, cy - 4)],
            (120, 124, 130))
    cv.poly([(cx - 20, cy + 4), (cx - 14, cy + 12), (cx - 8, cy + 4)],
            (120, 124, 130))
    cv.poly([(cx - 20, cy - 3), (cx - 28, cy), (cx - 20, cy + 3)], ORANGE)
    cv.circle(cx + 12, cy, 2, NAVY)


def pic_ball(cv, cx, cy):
    cv.circle(cx, cy, 15, WHITE)
    cv.ring(cx, cy, 15, INK)
    cv.poly([(cx - 4, cy - 5), (cx + 4, cy - 5), (cx + 6, cy + 2),
             (cx, cy + 6), (cx - 6, cy + 2)], INK)
    cv.rect(cx - 13, cy - 12, 5, 4, INK)
    cv.rect(cx + 9, cy - 11, 5, 4, INK)
    cv.rect(cx - 14, cy + 8, 5, 4, INK)
    cv.rect(cx + 10, cy + 8, 5, 4, INK)


def pic_chart_down(cv, cx, cy):
    cv.line(cx - 18, cy + 14, cx + 18, cy + 14, INK)
    cv.line(cx - 18, cy + 14, cx - 18, cy - 14, INK)
    cv.line(cx - 16, cy - 10, cx - 5, cy - 2, RED)
    cv.line(cx - 5, cy - 2, cx + 5, cy + 2, RED)
    cv.line(cx + 5, cy + 2, cx + 16, cy + 12, RED)
    cv.poly([(cx + 16, cy + 12), (cx + 9, cy + 11), (cx + 15, cy + 5)], RED)


def pic_chart_up(cv, cx, cy):
    cv.line(cx - 18, cy + 14, cx + 18, cy + 14, INK)
    cv.line(cx - 18, cy + 14, cx - 18, cy - 14, INK)
    cv.line(cx - 16, cy + 10, cx - 5, cy + 2, GREEN)
    cv.line(cx - 5, cy + 2, cx + 5, cy - 4, GREEN)
    cv.line(cx + 5, cy - 4, cx + 16, cy - 12, GREEN)
    cv.poly([(cx + 16, cy - 12), (cx + 9, cy - 13), (cx + 15, cy - 5)], GREEN)


def pic_plane(cv, cx, cy):
    cv.poly([(cx - 22, cy), (cx + 12, cy - 5), (cx + 22, cy),
             (cx + 12, cy + 5)], NAVY2)
    cv.poly([(cx - 4, cy - 4), (cx + 6, cy - 16), (cx + 10, cy - 4)], NAVY2)
    cv.poly([(cx - 2, cy + 4), (cx + 4, cy + 12), (cx + 8, cy + 4)], NAVY2)
    cv.poly([(cx - 22, cy - 2), (cx - 16, cy - 12), (cx - 12, cy - 2)],
            NAVY2)
    cv.circle(cx + 14, cy - 1, 2, WHITE)


def pic_ballot(cv, cx, cy):
    # ballot box, simple and flat, with paper + check
    cv.rect(cx - 8, cy - 18, 16, 10, WHITE)
    cv.rect(cx - 8, cy - 18, 16, 10, WHITE)
    cv.line(cx - 8, cy - 18, cx + 8, cy - 18, INK)
    cv.line(cx - 8, cy - 18, cx - 8, cy - 8, INK)
    cv.line(cx + 8, cy - 18, cx + 8, cy - 8, INK)
    cv.rect(cx - 14, cy - 8, 28, 22, NAVY2)
    cv.rect(cx - 7, cy - 5, 14, 2, CREAM)
    cv.poly([(cx - 8, cy + 6), (cx - 3, cy + 11), (cx + 9, cy - 1)],
            GREEN)
    cv.line(cx - 8, cy + 6, cx - 3, cy + 11, GREEN)
    cv.line(cx - 3, cy + 11, cx + 9, cy - 1, GREEN)


def pic_candle(cv, cx, cy):
    cv.poly([(cx, cy - 18), (cx + 4, cy - 10), (cx, cy - 6),
             (cx - 4, cy - 10)], YELLOW)
    cv.rect(cx - 1, cy - 6, 2, 3, INK)
    cv.rect(cx - 7, cy - 3, 14, 20, WHITE)
    cv.line(cx - 7, cy - 3, cx + 7, cy - 3, INK)
    cv.line(cx - 7, cy + 17, cx + 7, cy + 17, INK)
    cv.line(cx - 7, cy - 3, cx - 7, cy + 17, INK)
    cv.line(cx + 7, cy - 3, cx + 7, cy + 17, INK)
    cv.rect(cx - 12, cy + 17, 24, 2, GOLD)


def pic_shield(cv, cx, cy):
    cv.poly([(cx - 14, cy - 14), (cx + 14, cy - 14), (cx + 14, cy + 2),
             (cx, cy + 16), (cx - 14, cy + 2)], NAVY2)
    cv.poly([(cx - 7, cy - 2), (cx - 2, cy + 4), (cx + 9, cy - 7)],
            WHITE)
    cv.line(cx - 7, cy - 2, cx - 2, cy + 4, WHITE)
    cv.line(cx - 2, cy + 4, cx + 9, cy - 7, WHITE)


PICS = {
    'fire': pic_fire, 'storm': pic_storm, 'football': pic_football,
    'lock': pic_lock, 'missile': pic_missile, 'ball': pic_ball,
    'chart-down': pic_chart_down, 'plane': pic_plane,
    'chart-up': pic_chart_up, 'ballot': pic_ballot,
    'candle': pic_candle, 'shield': pic_shield,
}

# ---------------------------------------------------------------- data
LEAD_HEAD = "JAZAN REFINERY HIT KILLS 1"
LEAD_SUM = ("HOUTHI PROJECTILE HITS THE JAZAN REFINERY IN SOUTHWESTERN "
            "SAUDI ARABIA; 1 NEPALESE WORKER KILLED, SEVERAL HURT. FIRE "
            "BROUGHT UNDER CONTROL, SOME OPERATIONS HALTED; COALITION HIT "
            "50 TARGETS IN YEMEN; UNSC EXTENDS YEMEN SANCTIONS A YEAR. "
            "(CNN/REUTERS)")

# num, headline, summary, lon, lat, pictogram, map-key place label
PICTURED = [
    (1, "JAZAN REFINERY HIT KILLS 1",
     "HOUTHI PROJECTILE HITS JAZAN REFINERY; 1 NEPALESE WORKER KILLED, "
     "SEVERAL HURT; FIRE, SOME OPS HALTED; COALITION HIT 50 TARGETS IN "
     "YEMEN. (CNN)", 42.6, 16.9, 'fire', "JAZAN, SAUDI ARABIA"),
    (2, "US STORM WRECKS THANKSGIVING",
     "NOREASTER: 730,000+ WITHOUT POWER, 2,100 FLIGHTS DELAYED, 400+ "
     "CANCELLED; MACY'S 100TH PARADE POSTPONED TO SAT, A FIRST. (WSJ)",
     -74.0, 40.7, 'storm', "NEW YORK, USA"),
    (3, "BEARS STUN LIONS 39-35",
     "CALEB WILLIAMS HITS ROME ODUNZE WITH 3 SECONDS LEFT; GIBBS RAN FOR "
     "205 YARDS, 3 TDS; BEARS 9-2, LIONS 8-3. (NFL)",
     -83.0, 42.3, 'football', "DETROIT, USA"),
    (4, "DUTERTE ICC TRIAL SET",
     "TRIAL STARTS MONDAY; 81-YEAR-OLD FACES 85 MURDER COUNTS FROM THE "
     "2011-2018 DRUG WAR; PLEA TO BE ENTERED. (REUTERS)",
     4.35, 52.1, 'lock', "THE HAGUE, NETHERLANDS"),
    (5, "ITALIANS KILLED IN KUWAIT",
     "IRANIAN DRONE ATTACK IN KUWAIT KILLS 2 ITALIAN RHEINMETALL "
     "TECHNICIANS, ITALY SAYS. (REUTERS)",
     48.0, 29.4, 'missile', "KUWAIT"),
    (6, "PSG HELD 2-2 BY ROMA",
     "DEMBELE PENALTY, MALEN PENALTY; ROMA END PSG'S PERFECT CHAMPIONS "
     "LEAGUE START. (UEFA)",
     2.35, 48.86, 'ball', "PARIS, FRANCE"),
    (7, "EU BUDGET SUMMIT SPLIT",
     "LEADERS CLASH OVER 1.8T EURO BUDGET AND 45B EURO UKRAINE LOAN; "
     "GERMANY THREATENS VETO. (EURONEWS)",
     4.35, 50.85, 'chart-down', "BRUSSELS, BELGIUM"),
    (8, "NORTH KOREA HALTS MISSILES",
     "PYONGYANG TEMPORARILY HALTS KN-23 MISSILE SHIPMENTS TO RUSSIA AFTER "
     "DIPLOMATIC TENSIONS, KYIV SAYS. (REUTERS)",
     125.7, 39.0, 'missile', "PYONGYANG, N KOREA"),
    (9, "BANGKOK REFINERY BLAST HURTS 9",
     "BANGCHAK REFINERY EXPLOSION AND FIRE INJURES 9, 3 CRITICALLY; BLACK "
     "SMOKE OVER BANGKOK. (REUTERS)",
     100.5, 13.75, 'fire', "BANGKOK, THAILAND"),
    (10, "NATO AWACS TO POLAND",
     "NATO SENDS AWACS RADAR TO WATCH POLISH AIRSPACE AFTER 3 RUSSIAN "
     "CRUISE MISSILES FELL ON ITS TERRITORY. (EURONEWS)",
     19.0, 52.0, 'plane', "POLAND"),
    (11, "ARGENTINA IN RECESSION",
     "ECONOMY SHRANK 1.8% IN Q3, A SECOND STRAIGHT FALL, DESPITE MILEI'S "
     "REFORMS. (REPORTS)",
     -58.4, -34.6, 'chart-down', "BUENOS AIRES, ARGENTINA"),
    (12, "UK MIGRATION FALLS TO 77,000",
     "NET MIGRATION LOWEST SINCE 1997 OUTSIDE THE PANDEMIC, YEAR TO JUNE "
     "2026. (REPORTS)",
     -0.1, 51.5, 'chart-down', "LONDON, UK"),
    (13, "NZ ELECTION FINAL COUNT",
     "FINAL RESULTS DUE FRIDAY; CENTRE-RIGHT GOVERNMENT HOLDS A "
     "RAZOR-SLIM MAJORITY. (REUTERS)",
     174.8, -41.3, 'ballot', "WELLINGTON, NZ"),
    (14, "HONG KONG MOURNS 168",
     "ONE YEAR ON, RESIDENTS LAY FLOWERS FOR THE 168 VICTIMS OF THE WANG "
     "FUK COURT FIRE. (EURONEWS)",
     114.2, 22.3, 'candle', "HONG KONG, CHINA"),
    (15, "HOUTHIS THREATEN UK",
     "HOUTHI OFFICIAL WARNS BRITAIN TO REASSESS SUPPORT FOR SAUDI ARABIA; "
     "UK FLIES SORTIES, IMPOSED SANCTIONS. (THE TIMES)",
     44.2, 15.35, 'shield', "SANAA, YEMEN"),
]

LISTED = [
    "16. HOUTHIS CLAIM PIPELINE PUMP STATION AND YANBU FACILITY HITS; "
    "MISSILE AT KHAMIS MUSHAIT AIRBASE. (AL JAZEERA)",
    "17. FRANCE CONDEMNS HOUTHI ATTACKS ON SAUDI CIVILIAN SITES. "
    "(AL JAZEERA)",
    "18. NEPAL URGES RESTRAINT AFTER CITIZEN KILLED IN SAUDI STRIKES. (ANI)",
    "19. UN: 333,000 DISPLACED IN YEMEN SINCE AUGUST. (OCHA)",
    "20. US JUDGE STRIKES DOWN TRUMP ORDER ON SHARING EVIDENCE WITH ICC. "
    "(REPORTS)",
    "21. EISENKOT WINS FIRST COALITION PARTNER IN BID TO OUST NETANYAHU. "
    "(REPORTS)",
    "22. ISRAELI JUDGES URGE DROPPING NETANYAHU BRIBERY CASE 4000. (REPORTS)",
    "23. GAZA MINISTRY: 16 SCHOOLCHILDREN KILLED IN STRIKES THIS MONTH. "
    "(GUARDIAN)",
    "24. COPERNICUS: EARTH ABOVE 2C FOR 6 STRAIGHT DAYS, A FIRST. "
    "(COPERNICUS)",
    "25. DR CONGO EBOLA PASSES 12,021 CASES, 5,904 DEAD. (REPORTS)",
    "26. BELGIUM FARMERS MARCH IN BRUSSELS AGAINST EU FARM SUBSIDY CUTS. "
    "(EURONEWS)",
    "27. FRANCE'S MAINSTREAM FACES PRESIDENTIAL VOTE DEBACLE, NO CLEAR "
    "CANDIDATE. (BBC)",
    "28. INDIA TRADE BODY URGES RETALIATORY US TARIFFS, WARNS 500,000 JOBS "
    "AT RISK. (REPORTS)",
    "29. JAPAN SCHOOL ABSENTEEISM HITS RECORD 359,000, UP 13TH YEAR. "
    "(REPORTS)",
    "30. CHINA SHUTS GOLF COURSES IN APPARENT NEW CLAMPDOWN. (REPORTS)",
    "31. RAMS BEAT PACKERS 26-13 IN FIRST THANKSGIVING EVE GAME. (REPORTS)",
    "32. DEPARDIEU TO STAND TRIAL OVER RAPE CLAIM BY CHARLOTTE ARNOULD. "
    "(EURONEWS)",
    "33. IRAQ JAILS 8 FRENCH NATIONALS FOR LIFE FOR JOINING IS. (REPORTS)",
    "34. DIESEL TANKER CAPSIZES NEAR IBIZA, 1 KILLED, UP TO 7,000 TONNES. "
    "(EURONEWS)",
    "35. META FACES CONGRESS SUIT AND PROTESTS IN INDIA. (REPORTS)",
]

NUMBERS = [
    ("1", "KILLED AT JAZAN REFINERY"),
    ("730,000", "WITHOUT POWER, US STORM"),
    ("39-35", "BEARS STUN LIONS"),
    ("77,000", "UK NET MIGRATION"),
    ("+2C", "6 DAYS OVER PRE-INDUSTRIAL"),
]

# Stylised land mask: coarse lon/lat rectangles (lon_min, lon_max, lat_min, lat_max)
LAND_BOXES = [
    (-168, -52, 14, 71),    # North America
    (-58, -20, 60, 84),     # Greenland
    (-81, -34, -56, 12),    # South America
    (-11, 32, 36, 71),      # Europe
    (-18, 51, -35, 37),     # Africa
    (32, 60, 12, 42),       # Middle East / West Asia
    (60, 180, 42, 77),      # North Asia
    (60, 140, 5, 42),       # South / Southeast Asia
    (95, 141, -11, 6),      # Indonesia
    (113, 154, -39, -11),   # Australia
    (166, 178, -47, -34),   # New Zealand
]

# Leader-displaced map badges (true points collide): story num -> (dx, dy) px
DISPLACE = {1: (-16, -14), 3: (-12, -10), 4: (-18, -12),
            7: (14, 12), 12: (-20, 10), 15: (16, 14)}

# ---------------------------------------------------------------- layout
MARGIN = 20
GRID_X0, GRID_Y0 = 20, 138
CELL_W, CELL_H, GAP = 192, 146, 6
MAP_X, MAP_Y, MAP_W, MAP_H = 20, 612, 640, 136
KEY_X = 672
LAT_MIN, LAT_MAX = -56.0, 84.0


def map_xy(lon, lat):
    x = MAP_X + (lon + 180.0) / 360.0 * MAP_W
    y = MAP_Y + (LAT_MAX - lat) / (LAT_MAX - LAT_MIN) * MAP_H
    return int(x), int(y)


def audit():
    """Wrap audit: every text must fit its allotted lines. Raises on overflow."""
    problems = []
    lead_lines = wrap(LEAD_SUM, 944, 1)
    print("AUDIT lead: %d lines (max 2)" % len(lead_lines), file=sys.stderr)
    if len(lead_lines) > 2:
        problems.append("lead %d lines" % len(lead_lines))
    for num, head, summ, lon, lat, icon, place in PICTURED:
        hl = wrap(head, CELL_W - 12, 2)
        sl = wrap(summ, CELL_W - 12, 1)
        print("AUDIT #%02d headline %d lines (max 3), summary %d lines "
              "(max 5)" % (num, len(hl), len(sl)), file=sys.stderr)
        if len(hl) > 3:
            problems.append("#%d headline %d lines" % (num, len(hl)))
        if len(sl) > 5:
            problems.append("#%d summary %d lines" % (num, len(sl)))
    for item in LISTED:
        ll = wrap(item, 472, 1)
        if len(ll) > 2:
            problems.append("listed %r %d lines" % (item[:30], len(ll)))
    print("AUDIT listed: all <= 2 lines" if not problems else
          "AUDIT problems: %s" % problems, file=sys.stderr)
    if problems:
        raise SystemExit("WRAP OVERFLOW: " + "; ".join(problems))


def draw(cv):
    # ---- masthead
    cv.text_center(W // 2, 10, "THE WORLD TODAY", 4, NAVY)
    cv.text(20, 44, "No. 332", 2, NAVY)
    cv.text_center(W // 2, 44, "FRIDAY 27 NOVEMBER 2026", 2, NAVY)
    cv.text(W - 20 - text_width("35 STORIES", 2), 44, "35 STORIES", 2, NAVY)
    cv.hline(20, 62, W - 40, NAVY)
    cv.hline(20, 65, W - 40, NAVY)

    # ---- lead banner (red)
    cv.rect(20, 68, W - 40, 64, RED)
    cv.text_center(W // 2, 74, LEAD_HEAD, 3, WHITE)
    lead_lines = wrap(LEAD_SUM, 944, 1)
    for i, ln in enumerate(lead_lines):
        cv.text_center(W // 2, 100 + i * 10, ln, 1, WHITE)

    # ---- pictured grid 5x3
    for idx, (num, head, summ, lon, lat, icon, place) in enumerate(PICTURED):
        col, row = idx % 5, idx // 5
        x = GRID_X0 + col * (CELL_W + GAP)
        y = GRID_Y0 + row * (CELL_H + GAP)
        cv.rect(x, y, CELL_W, CELL_H, PAPER)
        cv.rect(x, y, CELL_W, 1, LINE)
        cv.rect(x, y, 1, CELL_H, LINE)
        cv.rect(x + CELL_W - 1, y, 1, CELL_H, LINE)
        cv.rect(x, y + CELL_H - 1, CELL_W, 1, LINE)
        # number badge, top-left
        cv.rect(x + 4, y + 4, 18, 14, NAVY)
        cv.text(x + 4 + (18 - text_width(str(num), 1)) // 2, y + 6,
                str(num), 1, WHITE)
        # pictogram centred in the top zone
        PICS[icon](cv, x + CELL_W // 2, y + 27)
        # headline, up to 3 lines, scale 2
        hl = wrap(head, CELL_W - 12, 2)
        for i, ln in enumerate(hl):
            cv.text(x + 6, y + 52 + i * 15, ln, 2, NAVY)
        # summary, up to 5 lines, scale 1
        sl = wrap(summ, CELL_W - 12, 1)
        for i, ln in enumerate(sl):
            cv.text(x + 6, y + 100 + i * 9, ln, 1, INK)

    # ---- world map + key
    cv.text(20, 594, "WORLD MAP", 2, NAVY)
    cv.text(KEY_X, 594, "KEY", 2, NAVY)
    cv.rect(MAP_X, MAP_Y, MAP_W, MAP_H, MAPBG)
    lon = -180.0
    while lon < 180.0:
        lat = LAT_MIN
        while lat < LAT_MAX:
            for (lo0, lo1, la0, la1) in LAND_BOXES:
                if lo0 <= lon < lo1 and la0 <= lat < la1:
                    px, py = map_xy(lon + 1.5, lat + 1.5)
                    cv.rect(px, py, 2, 2, LAND)
                    break
            lat += 3.0
        lon += 3.0
    for num, head, summ, lo, la, icon, place in PICTURED:
        px, py = map_xy(lo, la)
        dx, dy = DISPLACE.get(num, (0, 0))
        bx, by = px + dx, py + dy
        if (dx, dy) != (0, 0):
            cv.circle(px, py, 2, RED)
            cv.line(px, py, bx, by, GREY)
        cv.circle(bx, by, 8, NAVY)
        cv.ring(bx, by, 8, WHITE)
        ntxt = str(num)
        cv.text(bx - text_width(ntxt, 1) // 2, by - 3, ntxt, 1, WHITE)
    for i, (num, head, summ, lo, la, icon, place) in enumerate(PICTURED):
        cv.text(KEY_X, MAP_Y + i * 9, "%d  %s" % (num, place), 1, INK)

    # ---- by-the-numbers strip
    cv.rect(20, 754, W - 40, 46, NAVY)
    for i, (big, label) in enumerate(NUMBERS):
        cx = 20 + i * 197 + 98
        cv.text_center(cx, 760, big, 3, WHITE)
        cv.text_center(cx, 785, label, 1, (232, 184, 32))

    # ---- listed 20
    cv.text(20, 806, "MORE FROM AROUND THE WORLD", 2, NAVY)
    cv.hline(20, 822, W - 40, NAVY)
    for i, item in enumerate(LISTED):
        col = i // 10
        row = i % 10
        x = 20 + col * 492
        y = 828 + row * 18
        lines = wrap(item, 472, 1)
        for j, ln in enumerate(lines):
            cv.text(x, y + j * 9, ln, 1, INK)

    # ---- footer
    cv.hline(20, 1006, W - 40, NAVY)
    cv.text_center(W // 2, 1011,
                   "THE WORLD TODAY - FRIDAY 27 NOVEMBER 2026 - 35 STORIES",
                   1, GREY)


def main():
    audit()
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(outdir, exist_ok=True)
    cv = Canvas(W, H, CREAM)
    draw(cv)
    path = os.path.join(outdir, "entry.png")
    write_png(path, cv)
    print("wrote %s" % path)


if __name__ == "__main__":
    main()
