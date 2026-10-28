"""Give any name, username or ID a cute SVG face that never changes.

A stdlib-only Python port of @blobz/avatar-core (lirena00/blobz, MIT): the same name and
palette give the same SVG, byte for byte.
"""
import argparse
import math
import sys
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

CHOICES = {
    "brows": ["none", "raised", "angry", "worried", "flat", "quizzical", "high", "tilted", "unibrow"],
    "eyes": ["big", "dots", "sleepy", "happy", "wink", "squint", "distorted", "grumpy", "uneven", "oval",
             "side-eye", "crossed", "shocked", "peep wink"],
    "gap": ["close", "medium", "wide"],
    "look": ["centre", "left", "right", "up", "down"],
    "mouth": ["smile", "flat", "open", "frown", "oh", "smirk", "tongue out", "grin", "buck teeth", "wobbly",
              "wide smile"],
    "shape": ["eared", "lopsided", "pillow", "star", "ghost", "pebble", "squircle", "pentagon", "flower", "clover",
              "sun", "fuzz", "sparkle", "pill", "quarter", "round", "leaf", "soft triangle", "cloud", "drop", "bean"],
}
DEFAULT_PALETTE = ("#f2f1f4", "#7c6cf2")
FRAME_RADII = {"circle": 40, "rounded": 18, "square": 0}
GLINTS = [
    ("M15.4 31.8C15.8 31.1 16.7 28.8 17.6 27.4C18.4 26.0 19.4 24.5 20.6 23.4C21.7 22.2 23.9 21.0 24.6 20.5", "M14.0 36.1L13.4 39.1"),
    ("M15.4 37.4C15.6 36.7 16.1 34.6 16.6 33.3C17.1 31.9 17.7 30.6 18.4 29.4C19.1 28.1 20.4 26.4 20.8 25.8", "M14.7 41.9L14.8 44.9"),
    ("M19.4 23.1L19.7 21.8L20.5 20.5L21.4 19.9L23.1 19.4L24.4 19.6L25.9 20.1L27.3 20.6L28.4 20.9", "M20.7 27.7L21.3 30.3"),
    ("M33.7 25.7L37.7 18.9", "M21.1 32.1L24.1 31.5"),
    ("M18.9 36.4C19.0 35.7 19.2 33.5 19.5 32.1C19.9 30.7 20.3 29.3 21.0 28.1C21.6 26.8 22.9 25.0 23.3 24.4", "M18.9 40.9L18.9 44.0"),
    ("M17.2 41.6C17.3 41.1 17.6 39.2 18.2 38.2C18.7 37.1 19.5 36.2 20.4 35.4C21.3 34.6 23.0 33.7 23.5 33.4", "M17.6 46.1L18.7 49.0"),
    ("M16.9 34.9C16.9 34.1 17.0 32.0 17.2 30.6C17.3 29.1 17.4 27.7 17.8 26.3C18.1 24.9 19.0 23.0 19.2 22.3", "M16.9 39.4L17.0 42.5"),
    ("M19.7 40.9L18.6 37.6A2.5 2.5 0 0 1 19.5 34.8L24.8 31.0", "M27.6 28.9L29.7 27.4"),
    ("M24.7 25.8A7 7 0 0 1 29.3 20.6", "M15.5 39.3A8 8 0 0 1 16.4 37.5"),
    ("M18.6 27.8A8.5 8.5 0 0 1 23.3 21.4", "M18.9 31.6A8.5 8.5 0 0 1 18.6 30.2"),
    ("M25.0 31.6L24.2 24.8", "M18.3 36.4L21.1 35.2"),
    ("M21.9 32.8Q24.0 27.4 29.1 24.4", "M20.5 37.2L20.0 39.0"),
    ("M33.6 30.8L36.7 23.4", "M19.3 39.5L23.1 38.0"),
    ("M12.2 34.5C12.5 33.9 13.2 31.8 14.0 30.7C14.8 29.5 15.8 28.4 17.0 27.6C18.1 26.8 20.2 26.1 20.9 25.8", "M11.1 38.9L10.6 42.0"),
    ("M21.5 37V31Q21.5 22.6 28.5 22.6", "M21.5 45V42.5"),
    ("M17.5 36.0C17.8 35.3 18.4 33.3 19.1 32.0C19.8 30.7 20.6 29.5 21.5 28.4C22.3 27.3 23.9 25.8 24.4 25.3", "M16.7 40.4L16.7 43.5"),
    ("M23.0 28.1L24.0 26.8L25.2 25.7L26.0 24.8L27.2 23.7L28.2 23.0L29.5 22.0L30.8 21.1L31.9 20.5", "M20.4 31.7L19.1 34.2"),
    ("M20.2 44.6L26.2 33.2", "M18.1 48.6L16.6 51.4"),
    ("M18.7 31.8A12.5 12.5 0 0 1 25.1 23.0", "M13.0 44.1A9.5 9.5 0 0 1 13.9 42.0"),
    ("M21.9 44.1L27.7 32.6", "M21.0 48.5L21.0 51.6"),
    ("M17.4 39.0C17.6 38.3 18.1 36.2 18.5 34.8C18.9 33.4 19.4 32.1 20.0 30.8C20.7 29.5 22.0 27.8 22.3 27.2", "M16.6 43.4L16.5 46.5"),
]
M32 = 0xFFFFFFFF


def n(v):
    """Format a number the way JavaScript template literals do (shortest round-trip)."""
    if v == int(v) and abs(v) < 1e21:
        return str(int(v))
    r = repr(float(v))
    if "e" in r:  # JS: 1e-7, Python: 1e-07
        m, e = r.split("e")
        r = f"{m}e{'+' if int(e) > 0 else '-'}{abs(int(e))}"
    return r


def fixed1(v):
    """JavaScript toFixed(1): half away from zero on the exact binary value."""
    return str(Decimal(v).quantize(Decimal("0.1"), ROUND_HALF_UP))


def imul(a, b):
    r = (a * b) & M32
    return r - (1 << 32) if r & 0x80000000 else r


def i32(v):
    v &= M32
    return v - (1 << 32) if v & 0x80000000 else v


def hash_seed(value, seed=0):
    """cyrb53 over UTF-16 code units, like String.charCodeAt."""
    first, second = i32(0xDEADBEEF ^ seed), i32(0x41C6CE57 ^ seed)
    units = value.encode("utf-16-le")
    for i in range(0, len(units), 2):
        ch = units[i] | units[i + 1] << 8
        first = imul(first ^ ch, 2654435761)
        second = imul(second ^ ch, 1597334677)
    first = imul(first ^ ((first & M32) >> 16), 2246822507) ^ imul(second ^ ((second & M32) >> 13), 3266489909)
    second = imul(second ^ ((second & M32) >> 16), 2246822507) ^ imul(first ^ ((first & M32) >> 13), 3266489909)
    return 4294967296 * (2097151 & second) + (first & M32)


def seeded_random(seed):
    """mulberry32."""
    state = i32(seed)

    def rnd():
        nonlocal state
        state = i32(state + 0x6D2B79F5)
        v = imul(state ^ ((state & M32) >> 15), 1 | state)
        v = i32(v ^ i32(v + imul(v ^ ((v & M32) >> 7), 61 | v)))
        return ((v ^ ((v & M32) >> 14)) & M32) / 4294967296
    return rnd


def base36(v):
    s = ""
    while True:
        v, d = divmod(v, 36)
        s = "0123456789abcdefghijklmnopqrstuvwxyz"[d] + s
        if not v:
            return s


def rgb(h):
    v = int(h[1:], 16)
    return v >> 16, (v >> 8) & 255, v & 255


def mix(a, b, t):
    return "#" + "".join(f"{math.floor(x + (y - x) * t + 0.5):02x}" for x, y in zip(rgb(a), rgb(b)))


def escape_xml(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def render(c, colours, frame, id_, key):
    tilt, dx, dy, face_tilt = (c["tiltI"] - 7) * 2, c["dxI"] - 2, c["dyI"] - 1, c["faceTiltI"] - 12
    background, blob = colours
    r, g, b = rgb(blob)
    dark = 0.299 * r + 0.587 * g + 0.114 * b < 90
    pupil = "#1b1b1b" if dark else mix(blob, "#0a1030", 0.78)
    ink = "#ffffff" if dark else pupil

    def shape_path(d, w=2.5):
        return f'<path d="{d}" fill="{blob}" stroke="{blob}" stroke-width="{n(w)}" stroke-linejoin="round"/>'

    def polygon(points, w):
        return f'<polygon points="{points}" fill="{blob}" stroke="{blob}" stroke-width="{n(w)}" stroke-linejoin="round"/>'

    def burst(points, outer, inner, w):
        pts = []
        for i in range(points * 2):
            a = ((-90 + i * (180 / points)) * math.pi) / 180
            rad = inner if i % 2 else outer
            pts.append(f"{fixed1(40 + rad * math.cos(a))},{fixed1(42 + rad * math.sin(a))}")
        return polygon(" ".join(pts), w)

    def lobes(lst):
        return "".join(f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(rr)}" fill="{blob}"/>' for x, y, rr in lst)

    bodies = [
        ((40, 46, 1), lambda: shape_path("M10 46C10 27 21 15 30 17C35 18 36 24 40 24C44 24 45 18 50 17C59 15 70 27 70 46C70 61 56 68 40 68C24 68 10 61 10 46Z")),
        ((40, 44, 1), lambda: shape_path("M12 40C14 24 26 14 36 18C40 20 42 26 48 24C60 20 70 30 68 46C66 62 50 68 36 66C22 64 10 54 12 40Z")),
        ((40, 40, 0.95), lambda: shape_path("M20 20Q40 29 60 20Q51 40 60 60Q40 51 20 60Q29 40 20 20Z", 12)),
        ((40, 45, 0.78), lambda: burst(5, 27, 15, 8)),
        ((40, 42, 1), lambda: shape_path("M16 66V38C16 22 28 14 40 14C52 14 64 22 64 38V66Q58 62 52 66T40 66T28 66T16 66Z")),
        ((41, 48, 1), lambda: shape_path("M16 50C10 38 20 28 30 30C36 31 38 22 46 22C58 22 70 36 68 50C66 62 56 68 42 68C30 68 20 62 16 50Z")),
        ((40, 41, 1), lambda: shape_path("M14 38C14 18 18 14 38 14C60 14 67 18 67 40C67 62 60 67 40 67C20 67 14 60 14 38Z")),
        ((40, 43, 0.95), lambda: polygon("40,23 59,36.8 51.8,59.2 28.2,59.2 21,36.8", 14)),
        ((40, 42, 0.95), lambda: lobes([(57, 42, 12), (48.5, 56.7, 11), (31.5, 56.7, 13), (23, 42, 12), (31.5, 27.3, 11), (48.5, 27.3, 13), (40, 42, 19)])),
        ((40, 42, 0.9), lambda: lobes([(27, 29, 13), (53, 29, 14), (27, 55, 14), (53, 55, 13), (40, 42, 17)])),
        ((40, 42, 0.95), lambda: burst(9, 25, 17, 7)),
        ((40, 42, 0.98), lambda: burst(16, 26, 22.5, 4)),
        ((40, 42, 0.68), lambda: burst(4, 24, 10, 12)),
        ((40, 42, 1), lambda: shape_path("M24 22C34 20 46 24 56 22C68 20 74 30 72 42C70 56 62 64 52 62C42 60 30 64 22 62C12 60 6 50 8 40C10 28 14 24 24 22Z")),
        ((38, 44, 1), lambda: shape_path("M21 61V20A41 41 0 0 1 62 61Z", 10)),
        ((40, 42, 1), lambda: f'<ellipse cx="40" cy="42" rx="27.5" ry="26.5" fill="{blob}"/>'),
        ((40, 41, 0.9), lambda: shape_path("M19 61C8 38 30 8 61 19C72 50 44 72 19 61Z", 9)),
        ((40, 50, 0.88), lambda: shape_path("M40 13C47 13 51 22 58 35L68 54C73 64 64 69 53 69H27C16 69 7 64 12 54L22 35C29 22 33 13 40 13Z")),
        ((40, 46, 0.92), lambda: lobes([(22, 47, 14), (31, 34, 17), (47, 34, 18), (59, 47, 14), (48, 56, 16), (31, 56, 16), (40, 46, 20)])),
        ((40, 49, 0.9), lambda: shape_path("M40 12C47 22 62 36 62 50C62 63 52 70 40 70C28 70 18 63 18 50C18 36 33 22 40 12Z")),
        ((40, 45, 0.96), lambda: shape_path("M15 37C18 21 32 14 45 18C54 21 57 30 64 36C73 44 68 59 56 65C43 72 23 67 16 55C13 50 13 43 15 37Z")),
    ]
    body_f, body_g = bodies[c["shapeI"]]
    body_svg = body_g()
    glint = GLINTS[c["shapeI"]]
    white_body = body_svg.replace(blob, "#fff")
    shine = (f'<g mask="url(#{id_}s)" fill="none" stroke="#fff" stroke-linecap="round" stroke-linejoin="round" opacity=".62">'
             f'<path d="{glint[0]}" stroke-width="2.3"/><path d="{glint[1]}" stroke-width="2"/></g>')

    gap = (8.5, 10, 11.5)[c["gapI"]]
    L, R = -gap, gap
    lx, ly = ((0, 0), (-1.6, 0), (1.6, 0), (0, -1.6), (0, 1.6))[c["lookI"]]

    def stroke(w):
        return f'fill="none" stroke="{ink}" stroke-width="{n(w)}" stroke-linecap="round" stroke-linejoin="round"'

    def big(x, y=-2, rad=7.2):
        return (f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(rad)}" fill="#fff"/>'
                f'<circle cx="{n(x + lx)}" cy="{n(y + ly)}" r="{n(rad * 0.6)}" fill="{pupil}"/>')

    def happy(x):
        return f'<path d="M{n(x - 4.5)} 0Q{n(x)} -8 {n(x + 4.5)} 0" {stroke(2.4)}/>'

    def sleepy(x):
        return f'<path d="M{n(x - 4.5)} -4Q{n(x)} 3 {n(x + 4.5)} -4" {stroke(2.4)}/>'

    def grumpy(x, side):
        cid = f"{id_}{'a' if side > 0 else 'b'}"
        return (f'<clipPath id="{cid}"><polygon points="{n(x - 9 * side)},-5.5 {n(x + 9 * side)},0.5 {n(x + 9 * side)},9 {n(x - 9 * side)},9"/></clipPath>'
                f'<g clip-path="url(#{cid})"><circle cx="{n(x)}" cy="-2" r="7.2" fill="#fff"/><circle cx="{n(x + lx)}" cy="{n(1 + ly)}" r="4.2" fill="{pupil}"/></g>'
                f'<path d="M{n(x - 4.8 * side)} -4.1L{n(x + 4.8 * side)} -0.9" {stroke(2)}/>')

    def oval(x):
        return (f'<ellipse cx="{n(x)}" cy="-2" rx="3.7" ry="4.7" fill="{ink}"/>'
                f'<circle cx="{n(x + 1.2)}" cy="-3.6" r="1.1" fill="{"#1b1b1b" if dark else "#fff"}"/>')

    def lidded(x, cid):
        return (f'<clipPath id="{cid}"><polygon points="{n(x - 9)},-3.5 {n(x + 9)},-3.5 {n(x + 9)},9 {n(x - 9)},9"/></clipPath>'
                f'<g clip-path="url(#{cid})"><circle cx="{n(x)}" cy="-2" r="7.2" fill="#fff"/><circle cx="{n(x + lx * 1.5)}" cy="{n(1 + ly * 0.5)}" r="3.8" fill="{pupil}"/></g>'
                f'<path d="M{n(x - 6.4)} -3.5H{n(x + 6.4)}" {stroke(2.2)}/>')

    def cross(x, side):
        return f'<circle cx="{n(x)}" cy="-2" r="7.2" fill="#fff"/><circle cx="{n(x + 3 * side)}" cy="-1.5" r="3.6" fill="{pupil}"/>'

    def shocked(x):
        return f'<circle cx="{n(x)}" cy="-2" r="7.2" fill="#fff"/><circle cx="{n(x + lx * 0.8)}" cy="{n(-2 + ly * 0.8)}" r="1.9" fill="{pupil}"/>'

    def distorted(x, side):
        ex, cy = x - side * 0.9, -3.4
        px, py = ex - side * 1.8 + lx * 1.2, cy - 0.6 + ly * 1.2
        return (f'<path transform="translate({n(ex)} {n(cy)}) scale({n(1.04 * side)} 1.04)" d="M-7.5 2.9C-7.6 -3.5 -4.2 -8.8 -0.5 -9.2C2.8 -9.5 6.2 -8.2 7 -5.6C7.9 -2.8 7.6 1.2 5.8 4.8C4 8.2 0.8 9.4 -1.2 9.3C-4.8 9.2 -7.3 6.2 -7.5 2.9Z" fill="#fff"/>'
                f'<ellipse cx="{n(px)}" cy="{n(py)}" rx="2.6" ry="4.3" fill="{pupil}" transform="rotate({n(25 * side)} {n(px)} {n(py)})"/>')

    eyes = [
        lambda: big(L) + big(R),
        lambda: f'<circle cx="{n(L)}" cy="-2" r="3.6" fill="{ink}"/><circle cx="{n(R)}" cy="-2" r="3.6" fill="{ink}"/>',
        lambda: sleepy(L) + sleepy(R),
        lambda: happy(L) + happy(R),
        lambda: big(L) + happy(R),
        lambda: f'<path d="M{n(L - 4)} -6L{n(L + 3)} -2L{n(L - 4)} 2M{n(R + 4)} -6L{n(R - 3)} -2L{n(R + 4)} 2" {stroke(2.4)}/>',
        lambda: distorted(L, 1) + distorted(R, -1),
        lambda: grumpy(L, 1) + grumpy(R, -1),
        lambda: big(L, -3.5, 8) + big(R, -0.5, 5.6),
        lambda: oval(L) + oval(R),
        lambda: lidded(L, f"{id_}c") + lidded(R, f"{id_}d"),
        lambda: cross(L, 1) + cross(R, -1),
        lambda: shocked(L) + shocked(R),
        lambda: (f'<circle cx="{n(L)}" cy="-2.5" r="4.8" fill="#fff"/>'
                 f'<circle cx="{n(L + lx * 0.45)}" cy="{n(-2.5 + ly * 0.45)}" r="2.45" fill="{pupil}"/>'
                 f'<path d="M{n(R - 4.2)} -1.4Q{n(R)} -7.2 {n(R + 4.4)} -1.8" {stroke(2.1)}/>'),
    ][c["eyeI"]]()

    my = 8
    mouth_fill = "#4a4a58" if dark else pupil

    def open_mouth(w, h, top, teeth):
        d = (f"M{n(-w)} {n(top)}H{n(w)}C{n(w)} {n(top + h * 0.8)} {n(w * 0.55)} {n(top + h)} 0 {n(top + h)}"
             f"C{n(-w * 0.55)} {n(top + h)} {n(-w)} {n(top + h * 0.8)} {n(-w)} {n(top)}Z")
        t = f'<rect x="{n(-w)}" y="{n(top)}" width="{n(w * 2)}" height="2.6" fill="#fff"/>' if teeth else ""
        return (f'<clipPath id="{id_}m"><path d="{d}"/></clipPath>'
                f'<path d="{d}" fill="{mouth_fill}" stroke="{mouth_fill}" stroke-width="1.6" stroke-linejoin="round"/>'
                f'<g clip-path="url(#{id_}m)">{t}<ellipse cx="0" cy="{n(top + h)}" rx="{n(w * 0.62)}" ry="{n(h * 0.42)}" fill="#ff8fa3"/></g>')

    mouth = [
        lambda: f'<path d="M-3.2 {my}Q0 {n(my + 3.8)} 3.2 {my}" {stroke(2.2)}/>',
        lambda: f'<path d="M-2.6 {my + 1}H2.6" {stroke(2.2)}/>',
        lambda: open_mouth(4.4, 7.2, 6.2, False),
        lambda: f'<path d="M-3 {my + 2}Q0 {n(my - 1.6)} 3 {my + 2}" {stroke(2.2)}/>',
        lambda: f'<ellipse cx="0" cy="{my + 1}" rx="2" ry="2.5" fill="{ink}"/>',
        lambda: f'<path d="M-3 {my}Q0.5 {my + 4} 3.5 {my - 1}" {stroke(2.2)}/>',
        lambda: f'<path d="M0.4 9.2V13.2a2.4 2.4 0 0 0 4.8 0V8.6Z" fill="#ff7a93"/><path d="M-5.5 7Q0 13 5.5 7" {stroke(2.2)}/>',
        lambda: open_mouth(7, 7.8, 5.6, True),
        lambda: (f'<path d="M-4 7.5H4" {stroke(2.2)}/><rect x="-2.6" y="8" width="2.4" height="3.2" rx=".7" fill="#fff" stroke="{pupil}" stroke-width=".8"/>'
                 f'<rect x=".2" y="8" width="2.4" height="3.2" rx=".7" fill="#fff" stroke="{pupil}" stroke-width=".8"/>'),
        lambda: f'<path d="M-5 8Q-2.5 5 0 8T5 8" {stroke(2.2)}/>',
        lambda: f'<path d="M-7 5.4Q0 14.6 7 5.4" {stroke(2.4)}/>',
    ][c["mouthI"]]()

    def brow(x, side):
        return [
            lambda: "",
            lambda: f'<path d="M{n(x - 4.5)} -12Q{n(x)} -16 {n(x + 4.5)} -12" {stroke(2.2)}/>',
            lambda: f'<path d="M{n(x - 5 * side)} -15.5L{n(x + 5 * side)} -11.5" {stroke(2.2)}/>',
            lambda: f'<path d="M{n(x - 5 * side)} -11.5L{n(x + 5 * side)} -15.5" {stroke(2.2)}/>',
            lambda: f'<path d="M{n(x - 4.6)} -12.6H{n(x + 4.6)}" {stroke(2.4)}/>',
            lambda: (f'<path d="M{n(x - 4.5)} -13Q{n(x)} -18.2 {n(x + 4.5)} -13" {stroke(2.2)}/>' if side > 0
                     else f'<path d="M{n(x - 4.5)} -11.8H{n(x + 4.5)}" {stroke(2.2)}/>'),
            lambda: f'<path d="M{n(x - 5)} -14.6Q{n(x)} -22.4 {n(x + 5)} -14.6" {stroke(2.2)}/>',
            lambda: f'<path d="M{n(x - 4.6)} -11.6L{n(x + 4.6)} -14.4" {stroke(2.2)}/>',
            lambda: f'<path d="M{n(x - 5)} -12.6Q0 -15.8 {n(-x + 5)} -12.6" {stroke(2.4)}/>' if side > 0 else "",
        ][c["browI"]]()

    shift = {8: -2.5, 6: -3}.get(c["eyeI"], 0)
    brows = f'<g transform="translate(0 {n(shift)})">{brow(L, 1)}{brow(R, -1)}</g>'
    face = (f'<g transform="translate({n(body_f[0] + dx)} {n(body_f[1] + dy)}) scale({n(body_f[2])}) rotate({n(face_tilt)})">'
            f"{brows}{eyes}{mouth}</g>")
    flip = ' transform="translate(80 0) scale(-1 1)"' if c["flip"] else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 80" width="80" height="80" role="img" aria-label="Blob avatar for {escape_xml(key)}">'
            f'<defs><clipPath id="{id_}"><rect width="80" height="80" rx="{FRAME_RADII.get(frame, 18)}"/></clipPath>'
            f'<mask id="{id_}s" maskUnits="userSpaceOnUse" x="0" y="0" width="80" height="80">{white_body}</mask></defs>'
            f'<g clip-path="url(#{id_})"><rect width="80" height="80" fill="{background}"/>'
            f'<g transform="translate(40 42) rotate({n(tilt)}) scale(1.15) translate(-40 -42)"><g{flip}>{body_svg}{shine}</g><g{flip}>{face}</g></g></g></svg>')


ORDER = [("shapeI", 21), ("eyeI", 14), ("lookI", 5), ("mouthI", 11), ("tiltI", 15), ("dxI", 5), ("dyI", 3),
         ("gapI", 3), ("flip", 2), ("browI", 9), ("faceTiltI", 25)]


def choices_for(name, overrides=None):
    """The 11 feature indexes a name maps to, plus its hash."""
    key = str(name).strip().lower()
    h = hash_seed(key)
    rnd = seeded_random((h % 4294967296) ^ (h // 4294967296))
    rnd(), rnd()
    c = {k: math.floor(rnd() * count) for k, count in ORDER}
    for k, count in ORDER:
        v = (overrides or {}).get(k)
        if isinstance(v, int) and not isinstance(v, bool) and 0 <= v < count:
            c[k] = v
    return key, h, c


def avatar(name, palette=DEFAULT_PALETTE, frame="rounded", overrides=None):
    """SVG string for a name. Same name + palette + frame -> same SVG as @blobz/avatar-core."""
    key, h, c = choices_for(name, overrides)
    id_ = f"fp{base36(h)}-{c['shapeI']}-{c['eyeI']}-{c['mouthI']}-{c['gapI']}{frame[:1]}"
    return render(c, palette, frame, id_, key)


def describe(name):
    _, _, c = choices_for(name)
    return {"shape": CHOICES["shape"][c["shapeI"]], "eyes": CHOICES["eyes"][c["eyeI"]],
            "mouth": CHOICES["mouth"][c["mouthI"]], "brows": CHOICES["brows"][c["browI"]],
            "look": CHOICES["look"][c["lookI"]], "mirrored": bool(c["flip"])}


def main(argv=None):
    p = argparse.ArgumentParser(description="Give any name a stable SVG blob face.")
    p.add_argument("names", nargs="+", help="names, usernames, emails or IDs")
    p.add_argument("--bg", default=DEFAULT_PALETTE[0], help="background colour, #rrggbb")
    p.add_argument("--body", default=DEFAULT_PALETTE[1], help="body colour, #rrggbb")
    p.add_argument("--frame", choices=list(FRAME_RADII), default="rounded")
    p.add_argument("-o", "--out", type=Path, help="folder for <name>.svg files (default: print SVG)")
    p.add_argument("--html", type=Path, help="also write a gallery page with every face")
    a = p.parse_args(argv)
    for col in (a.bg, a.body):
        if len(col) != 7 or col[0] != "#" or any(ch not in "0123456789abcdefABCDEF" for ch in col[1:]):
            p.error(f"colours must look like #7c6cf2, got {col!r}")
    svgs = [(nm, avatar(nm, (a.bg, a.body), a.frame)) for nm in a.names]
    if a.out:
        a.out.mkdir(parents=True, exist_ok=True)
        for nm, svg in svgs:
            safe = "".join(ch if ch.isalnum() or ch in "-_." else "_" for ch in nm.strip().lower()) or "avatar"
            (a.out / f"{safe}.svg").write_text(svg, encoding="utf-8")
        print(f"wrote {len(svgs)} SVG files to {a.out}", file=sys.stderr)
    elif not a.html:
        print("\n".join(svg for _, svg in svgs))
    if a.html:
        cells = "".join(f"<figure>{svg}<figcaption>{escape_xml(nm)}</figcaption></figure>" for nm, svg in svgs)
        a.html.write_text("<!doctype html><meta charset=utf-8><title>name2face</title><style>body{font:14px system-ui;"
                          "display:flex;flex-wrap:wrap;gap:16px;padding:16px}figure{margin:0;text-align:center}"
                          f"svg{{width:96px;height:96px}}</style>{cells}", encoding="utf-8")
        print(f"wrote {a.html}", file=sys.stderr)


if __name__ == "__main__":
    main()
