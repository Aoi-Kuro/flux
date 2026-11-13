"""Quiz 1 problem figures (PHYS 162 Exam 1), redrawn as theme-aware SVG.

Image numbers are the exam's: 0 is unnamed.webp, n is unnamed(n).webp.
unnamed(6) (P19's integral) and unnamed(8) (P23's answer note) are formulas,
not figures: P19 states its integral in the text, and P23's note is left out.
"""
import math
from svgkit import Fig, INK, PAPER, BLUE, RED, GOLD, DARK, pt, n
from common import ceiling, dim_h, dim_v, charge, dot, capacitor, battery


def hat(g, x, y, s, size=17):
    """An upright unit-vector letter with a hat (x̂)."""
    g.text(x, y, s, size, italic=False, weight='bold')
    g.path(f'M{n(x - size * 0.22)},{n(y - size * 0.42)} L{n(x)},{n(y - size * 0.62)} L{n(x + size * 0.22)},{n(y - size * 0.42)}', INK, 1.1)


def f00():  # two equal charges Q on threads from one point, 5.0° to the vertical
    g = Fig(230, 400)
    ax, ay, L, a = 115, 19, 335, 7.0
    ceiling(g, 45, 185, 4, 15)
    g.line(ax, ay, ax, 392, w=1, dash='6 5', op=0.7)
    for s in (-1, 1):
        bx, by = ax + s * L * math.sin(math.radians(a)), ay + L * math.cos(math.radians(a))
        g.line(ax, ay, bx, by, w=1.3)
        g.disc(bx, by, 12, BLUE, 0.55)
        g.text(bx + s * 27, by, 'Q', 17)
    g.arc(ax, ay, 150, 270, 270 + a, w=1.1)
    lx, ly = pt(ax, ay, 150, 270 + a / 2)
    g.line(lx + 4, ly + 2, 168, 196, w=0.9, op=0.75)
    g.text(190, 190, '5.0°', 15, italic=False)
    return g


def f01():  # NaF dipole p at 40° in a uniform field E along x
    g = Fig(380, 230)
    ox, oy = 38, 128
    g.arrow(ox, 216, ox, 10, w=1.1, size=10)
    g.text(ox - 16, 16, 'y', 17)
    g.arrow(12, oy, 368, oy, w=1.1, size=10)
    g.text(362, oy + 18, 'x', 17)
    g.text(ox - 14, oy + 16, 'O', 15, italic=False)
    nx, ny, px, py = 92, 186, 166, 74
    L = math.hypot(px - nx, py - ny)
    ux, uy = (px - nx) / L, (py - ny) / L
    g.line(nx, ny, px, py, w=1.2)
    # p along the dipole, drawn beside it
    qx, qy = uy * 16, -ux * 16
    g.arrow(nx + ux * 22 + qx, ny + uy * 22 + qy, nx + ux * 92 + qx, ny + uy * 92 + qy, BLUE, w=2.4, size=11)
    g.text(nx + ux * 55 + qx * 2.2, ny + uy * 55 + qy * 2.2, 'p', 17, italic=False, weight='bold')
    # bond spacing a, on the other side
    rx, ry = -uy * 18, ux * 18
    g.arrow(nx + rx + ux * 4, ny + ry + uy * 4, px + rx - ux * 4, py + ry - uy * 4, w=1, size=8, both=True)
    g.text((nx + px) / 2 + rx * 1.9, (ny + py) / 2 + ry * 1.9, 'a', 17)
    charge(g, nx, ny, '-', 11)
    charge(g, px, py, '+', 11)
    g.text(nx - 6, ny + 28, 'Halogen', 13, italic=False)
    g.text(nx - 34, ny - 4, '−e', 15)
    g.text(px + 8, py - 28, 'Alkali metal', 13, italic=False)
    g.text(px - 30, py - 12, '+e', 15)
    for y in (46, 100, 172):
        g.arrow(232, y, 340, y, RED, w=2, size=11)
        g.text(286, y - 14, 'E', 16, italic=False, weight='bold')
    return g


def f02():  # charged semicircular rod of radius R, centre P
    g = Fig(280, 180)
    cx, cy, R = 140, 26, 124
    g.arc(cx, cy, R, 180, 360, RED, 3)
    dot(g, cx, cy, 3.6)
    g.text(cx + 15, cy - 6, 'P', 16)
    g.arrow(cx, cy, cx, cy + R - 2, w=1.1, size=9)
    g.text(cx + 12, cy + R * 0.52, 'R', 16)
    return g


def f03():  # four charges q at the corners of a square, Q at its centre
    g = Fig(250, 230)
    xs, ys = (56, 194), (45, 185)
    g.rect(xs[0], ys[0], xs[1] - xs[0], ys[1] - ys[0], w=1.2, extra=' stroke-dasharray="7 5"')
    for x in xs:
        for y in ys:
            g.disc(x, y, 13, BLUE, 0.5)
            g.text(x + (-28 if x == xs[0] else 28), y, 'q', 17)
    g.disc(125, 115, 12, RED, 0.5)
    g.text(150, 115, 'Q', 17)
    return g


def f04():  # electron enters the field between two plates, 1.00 cm by 2.00 cm
    g = Fig(470, 236)
    x1, x2, top, bot, t = 166, 446, 54, 206, 11
    for y in (top - t, bot):
        g.rect(x1, y, x2 - x1, t, fill=RED, fop=0.22, w=1.2)
    for x in (178, 244, 310, 376, 440):
        g.arrow(x, top + 2, x, bot - 2, RED, w=1.3, size=9)
    g.vec(420, 176, 'E', 17)
    g.path(f'M300,130 Q392,128 444,{top + 6}', GOLD, 1.8, dash='5 4')
    g.arrow(196, 130, 300, 130, BLUE, w=6, size=17)
    charge(g, 186, 130, '-', 15)
    g.sub(252, 104, 'v', '0', 17)
    # 1.00 cm between the plates, 2.00 cm along them
    g.line(52, top, x1 - 6, top, w=0.9, op=0.75)
    g.line(52, bot, x1 - 6, bot, w=0.9, op=0.75)
    dim_v(g, 98, top, bot, '', 0, 0, tick=0)
    g.rect(64, (top + bot) / 2 - 11, 68, 22, stroke=None, fill=PAPER)
    g.text(98, (top + bot) / 2, '1.00 cm', 15, italic=False)
    dim_h(g, 18, x1, x2, '', 0, 0, tick=9)
    g.rect((x1 + x2) / 2 - 36, 7, 72, 22, stroke=None, fill=PAPER)
    g.text((x1 + x2) / 2, 18, '2.00 cm', 15, italic=False)
    return g


def f05():  # two parallel charged sheets σ₂, σ₁ a distance d apart; point A; x̂
    g = Fig(320, 260)

    def sheet(x):
        g.poly([(x, 104), (x + 44, 80), (x + 44, 198), (x, 222)], fill=INK, fop=0.16, w=1.2)

    sheet(64)
    sheet(152)
    g.sub(86, 150, 'σ', '2', 18)
    g.sub(174, 150, 'σ', '1', 18)
    dot(g, 252, 132, 3.4)
    g.text(252, 114, 'A', 16, italic=False)
    g.arrow(238, 200, 300, 200, w=2, size=11)
    hat(g, 300, 178, 'x', 16)
    dim_h(g, 244, 86, 174, 'd', 130, 230, tick=0)
    return g


def f07():  # dipole ±q₁ a distance d apart, charge q₂ a from each
    g = Fig(210, 260)
    tx, ty, bx, by, qx, qy = 78, 42, 78, 214, 172, 128
    g.line(tx, ty, bx, by, w=1.3, dash='5 4')
    g.line(tx, ty, qx, qy, w=1.3, dash='5 4')
    g.line(bx, by, qx, qy, w=1.3, dash='5 4')
    g.line(28, ty, tx - 14, ty, w=0.9, op=0.75)
    g.line(28, by, bx - 14, by, w=0.9, op=0.75)
    dim_v(g, 38, ty, by, 'd', 24, (ty + by) / 2, tick=0)
    charge(g, tx, ty, '+', 12)
    charge(g, bx, by, '-', 12)
    charge(g, qx, qy, '-', 12)
    g.sub(tx + 28, ty - 4, 'q', '1', 17)
    g.sub(bx + 28, by + 4, 'q', '1', 17)
    g.sub(qx + 26, qy, 'q', '2', 17)
    g.text((tx + qx) / 2 + 12, (ty + qy) / 2 - 10, 'a', 17)
    g.text((bx + qx) / 2 + 12, (by + qy) / 2 + 10, 'a', 17)
    return g


def f09():  # Q₁ and Q₂ on the x-axis, point P between them at r₁ and r₂
    g = Fig(570, 100)
    y, x1, xp, x2 = 32, 30, 174, 498
    g.arrow(18, y, 560, y, w=1.2, size=10)
    g.text(552, y - 16, 'x', 17)
    charge(g, x1, y, '-', 10)
    charge(g, x2, y, '+', 10)
    dot(g, xp, y, 3.6)
    g.sub(x1, y - 22, 'Q', '1', 17)
    g.sub(x2, y - 22, 'Q', '2', 17)
    g.text(xp, y - 20, 'P', 16, italic=False)
    dim_h(g, 74, x1, xp, '', 0, 0, tick=8)
    dim_h(g, 74, xp, x2, '', 0, 0, tick=8)
    for (a, b, s) in ((x1, xp, '1'), (xp, x2, '2')):
        g.rect((a + b) / 2 - 15, 63, 30, 22, stroke=None, fill=PAPER)
        g.sub((a + b) / 2, 72, 'r', s, 17)
    return g


def f10():  # cube of side a at the origin, edges along x, y, z
    g = Fig(380, 330)
    O, s = (170, 238), 108
    ex, ey, ez = (-0.66, 0.44), (1, 0.12), (0, -1)

    def P(x, y, z):
        return (O[0] + s * (x * ex[0] + y * ey[0] + z * ez[0]), O[1] + s * (x * ex[1] + y * ey[1] + z * ez[1]))

    # axes, drawn first so the cube covers them
    g.arrow(*P(0, 0, 0), *P(1.62, 0, 0), w=1.1, size=10)
    x, y = P(1.62, 0, 0)
    g.text(x - 14, y + 4, 'x', 17)
    g.arrow(*P(0, 0, 0), *P(0, 1.75, 0), w=1.1, size=10)
    x, y = P(0, 1.75, 0)
    g.text(x + 4, y - 16, 'y', 17)
    g.arrow(*P(0, 0, 0), *P(0, 0, 2.05), w=1.1, size=10)
    x, y = P(0, 0, 2.05)
    g.text(x - 14, y + 6, 'z', 17)
    front = [P(1, 0, 0), P(1, 1, 0), P(1, 1, 1), P(1, 0, 1)]
    right = [P(1, 1, 0), P(0, 1, 0), P(0, 1, 1), P(1, 1, 1)]
    top = [P(1, 0, 1), P(1, 1, 1), P(0, 1, 1), P(0, 0, 1)]
    for face, op in ((front, 0.45), (right, 0.2), (top, 0.3)):
        g.poly(face, stroke=None, fill=PAPER)
        g.poly(face, fill=BLUE, fop=op, w=1.3)
    lx, ly = P(1, 0, 0.5)
    g.text(lx - 14, ly, 'a', 17)
    lx, ly = P(1, 0.5, 0)
    g.text(lx - 2, ly + 16, 'a', 17)
    lx, ly = P(0.5, 1, 0)
    g.text(lx + 12, ly + 12, 'a', 17)
    return g


def f11():  # wire on the axis of two long coaxial cylinders, radii a and b
    g = Fig(560, 380)
    c0 = (96, 284)
    d = (1, -0.56)
    L = math.hypot(*d)
    ux, uy = d[0] / L, d[1] / L
    px, py = -uy, ux
    length = 400
    c1 = (c0[0] + ux * length, c0[1] + uy * length)
    b, a = 82, 52
    # outer and inner tubes: two lines each, the far end left open
    for r, op in ((b, 1), (a, 0.85)):
        for s in (-1, 1):
            g.line(c0[0] + s * px * r, c0[1] + s * py * r, c1[0] + s * px * r, c1[1] + s * py * r, INK, 1.2, op=op)
    g.circle(*c0, b, fill=BLUE, fop=0.12, w=1.4)
    g.circle(*c0, a, fill=PAPER, w=1.3)
    g.circle(*c0, a, fill=RED, fop=0.1, w=1.3)
    g.line(*c0, *c1, w=1.4)
    dot(g, *c0, 3)
    # charges: + on the outer cylinder and the wire, − on the inner one
    for k in range(5):
        t = 70 + k * 72
        for s in (-1, 1):
            x, y = c0[0] + ux * t + s * px * b, c0[1] + uy * t + s * py * b
            g.text(x, y, '+', 14, italic=False, c=RED, weight='bold')
            x, y = c0[0] + ux * (t + 30) + s * px * a, c0[1] + uy * (t + 30) + s * py * a
            g.text(x, y, '−', 14, italic=False, c=BLUE, weight='bold')
        x, y = c0[0] + ux * (t + 14), c0[1] + uy * (t + 14)
        g.text(x - px * 9, y - py * 9, '+', 13, italic=False, c=RED, weight='bold')
    # radii a and b
    m = 230
    mx, my = c0[0] + ux * m, c0[1] + uy * m
    g.line(mx, my, mx - px * a, my - py * a, w=1, op=0.8)
    g.text(mx - px * a * 0.5 + ux * 12, my - py * a * 0.5 + uy * 12, 'a', 17)
    m2 = 150
    mx, my = c0[0] + ux * m2, c0[1] + uy * m2
    g.line(mx, my, mx - px * b, my - py * b, w=1, op=0.8)
    g.text(mx - px * b * 0.62 - ux * 12, my - py * b * 0.62 - uy * 12, 'b', 17)
    return g


def f12():  # charged ball on a thread at θ from the vertical, beside a charged sheet
    g = Fig(180, 210)
    g.rect(8, 4, 10, 202, fill=GOLD, fop=0.45, w=1.1)
    g.rect(96, 4, 76, 28, fill=INK, fop=0.18, w=1.1)
    vx, vy = 128, 32
    bx, by = 54, 150
    g.line(vx, vy, vx, 96, w=1, dash='4 3', op=0.75)
    g.line(vx, vy, bx, by, w=1.3)
    ang = math.degrees(math.atan2(-(by - vy), bx - vx)) % 360
    g.arc(vx, vy, 34, ang, 270, w=1)
    g.text(*pt(vx, vy, 48, (ang + 270) / 2), 'θ', 16)
    charge(g, bx, by, '+', 11)
    return g


def f13():  # surface A₁ around objects O₁, O₂ and O₃; O₃ inside A₂
    g = Fig(480, 300)
    g.blob([(30, 160), (70, 90), (190, 80), (300, 96), (420, 62), (466, 120), (462, 210), (400, 250),
            (280, 236), (150, 252), (60, 232)], fill=BLUE, fop=0.12, w=1.4)
    g.circle(368, 146, 50, fill=RED, fop=0.16, w=1.3)
    g.sub(256, 40, 'A', '1', 22)
    g.sub(380, 168, 'A', '2', 20)
    for (x, y, s, dx) in ((92, 128, '1', -26), (152, 210, '2', -26), (352, 118, '3', 26)):
        dot(g, x, y, 5)
        g.raw(f'<text x="{n(x + dx)}" y="{n(y)}" font-size="19" text-anchor="middle" dominant-baseline="central" '
              f'fill="{INK}" stroke="none">O<tspan font-size="13" dy="5">{s}</tspan></text>')
    return g


def f14():  # uniformly charged sphere with an off-centre spherical cavity
    g = Fig(300, 230)
    cx, cy, R = 132, 115, 104
    hx, hy, r = 182, 96, 46
    g.circle(cx, cy, R, fill=BLUE, fop=0.3, w=1.4)
    g.circle(hx, hy, r, fill=PAPER, w=1.4)
    dot(g, cx, cy, 3)
    dot(g, hx, hy, 3)
    g.arrow(cx, cy, hx - 2, hy + 1, w=1, size=8, both=True)
    g.text((cx + hx) / 2 - 4, (cy + hy) / 2 + 15, 'd', 17)
    return g


def f15():  # charged semicircle of radius R centred on the origin
    g = Fig(320, 200)
    ox, oy, R = 150, 150, 82
    g.arrow(30, oy, 308, oy, w=1.1, size=10)
    g.text(304, oy + 18, 'x', 17)
    g.arrow(ox, 194, ox, 20, w=1.1, size=10)
    g.text(ox + 14, 24, 'y', 17)
    g.arc(ox, oy, R, 0, 180, RED, 3)
    x, y = pt(ox, oy, R, 45)
    g.line(ox, oy, x, y, w=1)
    g.text(ox + 30, oy - 44, 'R', 16)
    g.text(ox - 14, oy + 16, 'O', 15, italic=False)
    return g


def f16():  # dipole q₁ (+) and q₂ (−), point a on the line between them
    g = Fig(500, 96)
    y, x1, xa, x2 = 38, 40, 348, 460
    g.line(x1, y, x2, y, w=1.3)
    charge(g, x1, y, '+', 15)
    charge(g, x2, y, '-', 15)
    dot(g, xa, y, 5)
    g.text(xa, y - 20, 'a', 18)
    g.sub(x1, y + 34, 'q', '1', 18)
    g.sub(x2, y + 34, 'q', '2', 18)
    return g


def f17():  # particle moves from a to b between charges +q and −q
    g = Fig(560, 80)
    y = 46
    g.line(20, y, 540, y, w=1.3)
    charge(g, 92, y, '+', 15)
    charge(g, 452, y, '-', 15)
    dot(g, 214, y, 5)
    dot(g, 330, y, 5)
    g.text(214, y - 22, 'a', 18)
    g.text(330, y - 22, 'b', 18)
    g.line(220, y, 318, y, BLUE, 2.2, dash='7 5')
    g.head(326, y, 1, 0, BLUE, 11)
    g.disc(272, y, 9, RED, 0.45)
    return g


def plates(g, x1, x2, y_top, y_bot, t=10):
    g.rect(x1, y_top - t, x2 - x1, t, fill=INK, fop=0.85, w=1)
    g.rect(x1, y_bot, x2 - x1, t, fill=INK, fop=0.85, w=1)


def kappa(g, x, y, s):
    g.rect(x - 22, y - 13, 44, 26, stroke=None, fill=PAPER, rx=4)
    g.sub(x, y, 'κ', s, 18)


def f18():  # capacitor filled with two slabs κ₁, κ₂ one above the other, d/2 each
    g = Fig(380, 190)
    x1, x2, top, mid, bot = 10, 300, 22, 92, 162
    plates(g, x1, x2, top, bot)
    g.rect(x1, top + 1, x2 - x1, mid - top - 2, fill=BLUE, fop=0.18, w=1.1)
    g.rect(x1, mid + 1, x2 - x1, bot - mid - 2, fill=BLUE, fop=0.45, w=1.1)
    kappa(g, 155, (top + mid) / 2, '1')
    kappa(g, 155, (mid + bot) / 2, '2')
    for y in (top, mid, bot):
        g.line(x2 + 6, y, 350, y, w=0.9, op=0.75)
    dim_v(g, 330, top, mid, 'd/2', 362, (top + mid) / 2, tick=0)
    dim_v(g, 330, mid, bot, 'd/2', 362, (mid + bot) / 2, tick=0)
    return g


def f19():  # capacitor filled with two slabs κ₁, κ₂ side by side, gap d
    g = Fig(400, 140)
    x1, x2, top, bot = 10, 310, 26, 112
    plates(g, x1, x2, top, bot)
    g.rect(x1 + 2, top + 2, 142, bot - top - 4, fill=BLUE, fop=0.18, w=1.1)
    g.rect(x1 + 156, top + 2, 142, bot - top - 4, fill=BLUE, fop=0.45, w=1.1)
    kappa(g, x1 + 73, (top + bot) / 2, '1')
    kappa(g, x1 + 227, (top + bot) / 2, '2')
    for y in (top, bot):
        g.line(x2 + 6, y, 362, y, w=0.9, op=0.75)
    dim_v(g, 342, top, bot, 'd', 378, (top + bot) / 2, tick=0)
    return g


def f20():  # battery V and capacitors C₁ … C₄
    g = Fig(380, 210)
    A, B, D, M, E = (64, 22), (270, 22), (64, 160), (200, 160), (346, 160)
    g.line(*A, *B, w=1.4)
    g.line(*D, *M, w=1.4)
    battery(g, A[0], A[1], D[1])
    g.text(34, (A[1] + D[1]) / 2, 'V', 17)

    def cap(p, q, label, dx, dy):
        mx, my, px, py = capacitor(g, *p, *q)
        g.sub(mx + dx, my + dy, 'C', label, 17)

    cap(A, M, '1', 20, -18)
    cap(M, B, '2', -22, -16)
    cap(B, E, '3', 26, -14)
    cap(M, E, '4', 0, 28)
    for p in (A, B, M):
        dot(g, *p, 2.8)
    return g


FIGURES = [
    (0, f00, 'Two charges Q hanging on threads at 5.0° to the vertical', 1),
    (1, f01, 'NaF dipole p with bond spacing a in a uniform field E', 1),
    (2, f02, 'Charged semicircular rod of radius R, centre P', 1),
    (3, f03, 'Charges q at the corners of a square, Q at its centre', 1),
    (4, f04, 'Electron entering the field between two plates', 1),
    (5, f05, 'Two parallel charged sheets d apart, point A, unit vector x', 1),
    (7, f07, 'Dipole ±q₁ and charge q₂ at the corners of a triangle', 2),
    (9, f09, 'Charges Q₁ and Q₂ with point P between them', 2),
    (10, f10, 'Cube of side a at the origin', 1),
    (11, f11, 'Line charge inside two coaxial charged cylinders, radii a and b', 2),
    (12, f12, 'Charged sphere on a thread beside a charged sheet', 1),
    (13, f13, 'Closed surfaces A₁ and A₂ around objects O₁, O₂, O₃', 1),
    (14, f14, 'Charged sphere with an off-centre spherical cavity', 1),
    (15, f15, 'Charged semicircle of radius R about the origin', 1),
    (16, f16, 'Dipole q₁, q₂ with point a between them', 1),
    (17, f17, 'Particle moving from a to b between +q and −q', 1),
    (18, f18, 'Capacitor with two dielectric slabs one above the other', 1),
    (19, f19, 'Capacitor with two dielectric slabs side by side', 1),
    (20, f20, 'Battery V and capacitors C₁ to C₄', 1),
]
