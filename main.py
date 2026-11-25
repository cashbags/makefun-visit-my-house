"""Draw the invitation letter: one 1024x1024 PNG, pure stdlib only.

Reads nothing, needs no network, no clock, no randomness: two runs are
byte-identical. Writes /output/entry.png (or $OUTPUT_DIR/entry.png).
"""
import math
import os
import struct
import zlib

W = H = 1024
PAPER = (247, 233, 201)
INK = (43, 33, 24)
BROWN = (139, 94, 52)
RED = (176, 58, 46)
CREAM = (250, 243, 226)
BLUE = (43, 108, 176)
BROTH = (232, 169, 76)
NOODLE = (242, 212, 146)
GREEN = (90, 143, 60)
YOLK = (214, 110, 20)
EGG = (255, 243, 214)
STEAM = (154, 139, 122)

# 5x7 bitmap font. Each glyph is 7 chars, one per row, top to bottom.
# A char encodes one 5-bit row as base32: '0'-'9' = 0-9, 'a'-'v' = 10-31,
# bit 4 = leftmost pixel. Order matches CHARS. A-Z, a-z, 0-9, punctuation.
CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 .,'-!?:;()\"/"
FONT = (
"ehhvhhh" "uhhuhhu" "fgggggf" "uhhhhhu" "vgguggv" "vgguggg" "fggnhhe"
"hhhvhhh" "e44444e" "72222ic" "hikokih" "ggggggv" "hrllhhh" "hppljjh"
"ehhhhhe" "uhhuggg" "ehhhlid" "uhhukih" "fgge11u" "v444444" "hhhhhhe"
"hhhhha4" "hhhllrh" "hha4ahh" "hha4444" "v1248gv"
"00e1fhe" "gguhhhu" "00fgggf" "11fhhhe" "00ehvge" "698u888" "0fhhf1e"
"gguhhhh" "040c44e" "020622c" "ggikoki" "c44444e" "00qllll" "00uhhhh"
"00ehhhe" "00uhhug" "00fhhe1" "00mpggg" "00fge1u" "88u8886" "00hhhhe"
"00hhha4" "00hllrh" "00ha4ah" "00hhf1e" "00v248v"
"ehjlphe" "4c4444e" "eh1248v" "u11e11u" "26aiv22" "vgu11he" "egguhhe"
"v122444" "ehhehhe" "ehhu11e"
"0000000" "00000cc" "0000cc8" "4480000" "000e000" "4444404" "eh12404"
"0cc0cc0" "0cc0cc8" "2488842" "8422248" "aa00000" "11248gg"
)

buf = bytearray(bytes(PAPER) * (W * H))


def fill(x, y, w, h, c):
    c3 = bytes(c)
    x0 = max(0, x)
    x1 = min(W, x + w)
    if x1 <= x0:
        return
    for yy in range(max(0, y), min(H, y + h)):
        o = (yy * W + x0) * 3
        buf[o:o + (x1 - x0) * 3] = c3 * (x1 - x0)


def disc(cx, cy, r, c):
    for dy in range(-r, r + 1):
        dx = int(math.sqrt(max(0, r * r - dy * dy)))
        fill(cx - dx, cy + dy, dx * 2 + 1, 1, c)


def line(x0, y0, x1, y1, c, w=3):
    n = max(abs(x1 - x0), abs(y1 - y0), 1)
    for i in range(n + 1):
        x = x0 + (x1 - x0) * i // n
        y = y0 + (y1 - y0) * i // n
        disc(x, y, w // 2, c)


def arc(cx, cy, r, a0, a1, c, w=4):
    steps = max(8, r * 2)
    for i in range(steps + 1):
        a = a0 + (a1 - a0) * i / steps
        disc(int(cx + r * math.cos(a)), int(cy + r * math.sin(a)), w // 2, c)


def png(w, h, raw):
    body = b"".join(b"\x00" + bytes(raw[y * w * 3:(y + 1) * w * 3])
                    for y in range(h))

    def chunk(t, data):
        c = t + data
        return struct.pack(">I", len(data)) + c + struct.pack(
            ">I", zlib.crc32(c) & 0xffffffff)

    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(body, 9)) + chunk(b"IEND", b""))


def text(s, x, y, sc, c):
    for ch in s:
        i = CHARS.index(ch) * 7
        g = FONT[i:i + 7]
        for r in range(7):
            d = ord(g[r]) - 48
            if d > 9:
                d -= 39
            for k in range(5):
                if (d >> (4 - k)) & 1:
                    fill(x + k * sc, y + r * sc, sc, sc, c)
        x += 6 * sc


def border():
    fill(34, 34, 956, 4, BROWN)
    fill(34, 986, 956, 4, BROWN)
    fill(34, 34, 4, 956, BROWN)
    fill(986, 34, 4, 956, BROWN)
    fill(52, 52, 920, 2, BROWN)
    fill(52, 970, 920, 2, BROWN)
    fill(52, 52, 2, 920, BROWN)
    fill(970, 52, 2, 920, BROWN)


def seal():
    disc(888, 596, 34, RED)
    disc(888, 596, 26, (146, 44, 34))
    text("F", 873, 575, 6, CREAM)


def half(cx, cy, rx, ry, c):
    for dy in range(ry):
        dx = int(rx * math.sqrt(1 - (dy / ry) ** 2))
        fill(cx - dx, cy + dy, dx * 2, 1, c)


def bowl(cx, rim):
    half(cx, rim, 175, 150, RED)
    half(cx, rim + 8, 158, 110, BROTH)
    fill(cx - 175, rim - 6, 350, 10, CREAM)
    line(cx - 175, rim - 1, cx + 175, rim - 1, RED, 3)
    for k, ph in ((0, 0.0), (1, 1.3), (2, 2.6)):
        y0 = rim + 42 + k * 18
        for x in range(cx - 120, cx + 120, 6):
            disc(x, y0 + int(5 * math.sin(x * 0.05 + ph)), 3, NOODLE)
    disc(cx - 70, rim + 55, 20, EGG)
    disc(cx - 70, rim + 55, 10, YOLK)
    fill(cx + 30, rim + 30, 8, 8, GREEN)
    fill(cx + 48, rim + 52, 8, 8, GREEN)
    fill(cx - 10, rim + 70, 8, 8, GREEN)
    line(cx + 55, rim - 80, cx + 150, rim + 5, BROWN, 5)
    line(cx + 78, rim - 88, cx + 168, rim - 8, BROWN, 5)
    for bx, ph in ((-90, 0.0), (0, 2.0), (90, 4.0)):
        for y in range(rim - 95, rim - 8, 6):
            disc(cx + bx + int(8 * math.sin(y * 0.05 + ph)), y, 3, STEAM)
    disc(cx, rim - 120, 7, BLUE)
    arc(cx, rim - 120, 28, -2.8, -0.35, BLUE, 6)
    arc(cx, rim - 120, 48, -2.8, -0.35, BLUE, 6)


def main():
    border()
    text("AN INVITATION", 358, 96, 4, BROWN)
    fill(200, 108, 120, 3, BROWN)
    fill(704, 108, 120, 3, BROWN)
    lines = ["Dear Judge,", "Come over Sunday, 7pm.", "Ramen's on. The chair",
             "by the window is yours.", "No RSVP - the wifi",
             "password is your reply.", "You can't eat. Log in.", "- Feyza"]
    y = 176
    for ln in lines:
        text(ln, 92, y, 6, INK)
        y += 56
    seal()
    bowl(512, 800)
    out = os.environ.get("OUTPUT_DIR", "/output")
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "entry.png"), "wb") as f:
        f.write(png(W, H, buf))


main()
