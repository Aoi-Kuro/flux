"""Quiz 3 problem figures (PHYS 162 Exam 3), redrawn as theme-aware SVG.

Image numbers are the exam's: 0 is unnamed.webp, n is unnamed(n).webp.
Images 6, 10, 12, 14 and 16 have hand-drawn SVGs (handmade/quiz3/), which
export.py uses instead; everything else is drawn here. B-field marks are
neutral ink, velocities blue, forces red, currents gold.
"""
import math
from svgkit import Fig, INK, PAPER, BLUE, RED, GOLD, DARK, pt, n
from common import (dim_h, dim_v, dot, capacitor, resistor, inductor, switch, cell,
                    ac_source, field, rod)


def blabel(g, x, y):
    g.vec(x, y, 'B', 16)


def f00():  # circular loop with a resistor R in an outward field
    g = Fig(320, 190)
    field(g, 22, 22, 214, 172, 32, 'dot')
    cx, cy, r = 112, 98, 56
    a = math.degrees(math.asin(14 / r))
    g.raw(f'<path d="M{n(cx + r * math.cos(math.radians(a)))},{n(cy - 14)} '
          f'A{r},{r} 0 1 0 {n(cx + r * math.cos(math.radians(a)))},{n(cy + 14)}" fill="none" stroke="{INK}" stroke-width="1.6"/>')
    x0 = cx + r * math.cos(math.radians(a))
    g.path(f'M{n(x0)},{cy - 14} L232,{cy - 14} L232,40 L292,40 L292,{cy - 30}', w=1.6)
    resistor(g, 292, cy - 30, 292, cy + 30, body=40, w=1.6)
    g.path(f'M292,{cy + 30} L292,156 L232,156 L232,{cy + 14} L{n(x0)},{cy + 14}', w=1.6)
    g.text(310, cy, 'R', 16, italic=False)
    blabel(g, 20, 182)
    return g


def moving_rod(kind, label):
    g = Fig(440, 210)
    field(g, 30, 30, 410, 190, 64, kind)
    blabel(g, 20, 14)
    rod(g, 140, 60, 160)
    dim_v(g, 92, 60, 160, '', 0, 0, tick=9)
    g.rect(56, 98, 72, 24, stroke=None, fill=PAPER)
    g.text(92, 110, label, 15, italic=False)
    g.arrow(150, 110, 222, 110, BLUE, w=2.6, size=12)
    g.vec(236, 112, 'v', 16)
    return g


def f01():  # rod 5.0 cm long moving right through an outward field
    return moving_rod('dot', '5.0 cm')


def f02():  # rod 25 cm long moving right through an inward field
    return moving_rod('cross', '25 cm')


def f03():  # rod sliding left on U-shaped rails 4.0 cm apart, a from the end
    g = Fig(440, 200)
    field(g, 26, 26, 410, 186, 64, 'dot')
    blabel(g, 20, 12)
    top, bot, x0, xr = 66, 142, 44, 318
    g.path(f'M420,{top} L{x0},{top} L{x0},{bot} L420,{bot}', BLUE, 3.2)
    rod(g, xr, top - 18, bot + 18)
    g.arrow(xr - 8, 104, xr - 70, 104, BLUE, w=2.6, size=12)
    g.vec(xr - 84, 106, 'v', 16)
    dim_v(g, 362, top, bot, '', 0, 0, tick=9)
    g.rect(366, 92, 58, 24, stroke=None, fill=PAPER)
    g.text(395, 104, '4.0 cm', 15, italic=False)
    dim_h(g, 176, x0, xr, '', 0, 0, tick=9)
    g.rect((x0 + xr) / 2 - 12, 165, 24, 22, stroke=None, fill=PAPER)
    g.text((x0 + xr) / 2, 175, 'a', 17)
    return g


def f04():  # square loop moving right into an inward field region B
    g = Fig(470, 230)
    g.rect(172, 10, 288, 210, stroke=None, fill=INK, fop=0.06)
    field(g, 196, 32, 446, 200, 50, 'cross', size=6.5, op=0.7)
    g.rect(300, 92, 34, 28, stroke=None, fill=PAPER)
    g.text(317, 106, 'B', 20, italic=False, weight='bold')
    g.rect(20, 92, 102, 102, w=2.4)
    g.arrow(30, 68, 112, 68, BLUE, w=2.4, size=12)
    g.vec(71, 46, 'v', 17)
    return g


def f05():  # rod sliding right on rails through an inward field; resistor R closes the circuit
    g = Fig(470, 270)
    top, bot, xl, xr = 74, 206, 40, 430
    field(g, 30, 32, 410, 248, 54, 'cross')
    g.rect(222, top, 46, bot - top, stroke=None, fill=GOLD, fop=0.18)
    g.line(222, top - 30, 222, bot + 30, w=1, dash='4 3', op=0.75)
    for y in (top, bot):
        g.rect(xl, y - 4, xr - xl, 8, stroke=None, fill=PAPER)
        g.rect(xl, y - 4, xr - xl, 8, fill=INK, fop=0.18, w=1)
    g.line(xl, top + 4, xl, 116, w=1.4)
    resistor(g, xl, 116, xl, 164, body=40)
    g.line(xl, 164, xl, bot - 4, w=1.4)
    g.text(xl + 20, 140, 'R', 16)
    rod(g, 268, top - 20, bot + 20)
    g.arrow(278, 156, 340, 156, BLUE, w=2.4, size=11)
    g.text(310, 176, 'v', 16)
    g.arrow(200, top - 14, 150, top - 14, GOLD, w=2.2, size=10)
    g.text(176, top - 30, 'I', 16)
    g.line(240, 52, 252, 20, w=0.9, op=0.75)
    g.raw(f'<text x="252" y="12" font-size="15" text-anchor="middle" dominant-baseline="central" fill="{INK}" stroke="none">'
          f'Δ<tspan font-style="italic">A</tspan> = <tspan font-style="italic">ℓ</tspan>Δ<tspan font-style="italic">x</tspan></text>')
    dim_h(g, 236, 222, 268, '', 0, 0, tick=0)
    g.raw(f'<text x="245" y="256" font-size="15" text-anchor="middle" dominant-baseline="central" fill="{INK}" stroke="none">'
          f'Δ<tspan font-style="italic">x</tspan></text>')
    dim_v(g, 450, top, bot, 'ℓ', 462, (top + bot) / 2, tick=8)
    return g


def f07():  # rod between a and b below a long wire with current i, moving right
    g = Fig(380, 260)
    y0 = 40
    g.line(10, y0, 50, y0, w=1.5, dash='7 5')
    g.line(50, y0, 300, y0, w=1.8)
    g.line(300, y0, 360, y0, w=1.5, dash='7 5')
    g.head(250, y0, 1, 0, GOLD, 13)
    g.text(250, y0 - 16, 'i', 17)
    dim_v(g, 112, y0, 232, '', 0, 0, tick=0)
    g.text(96, 140, 'b', 17)
    dim_v(g, 152, y0, 104, '', 0, 0, tick=0)
    g.text(166, 74, 'a', 17)
    g.rect(196, 104, 12, 128, fill=INK, fop=0.85, w=1)
    g.arrow(208, 168, 280, 168, BLUE, w=2.4, size=12)
    g.vec(296, 170, 'v', 16)
    return g


def f08():  # square coil of side a in an inward field, pulled out across the edge
    g = Fig(440, 260)
    edge = 300
    field(g, 118, 26, edge - 10, 222, 26, 'cross', size=4.5, op=0.6)
    g.line(edge, 14, edge, 236, w=1.2, dash='5 4')
    g.text(178, 12, 'B', 17)
    g.text(edge + 46, 40, 'B = 0', 16)
    g.rect(150, 64, edge - 150, 150, stroke=None, fill=PAPER, fop=0)
    g.rect(150, 64, edge - 150, 150, w=4.2, fill='none')
    g.arrow(150, 140, 88, 140, RED, w=2.6, size=12)
    g.vecsub(62, 128, 'F', 'M', 17)
    g.arrow(edge, 140, edge + 66, 140, RED, w=2.6, size=12)
    g.vecsub(edge + 92, 128, 'F', 'ext', 17)
    dim_h(g, 246, 150, edge, '', 0, 0, tick=9)
    g.rect(212, 236, 26, 22, stroke=None, fill=PAPER)
    g.text(225, 246, 'a', 17)
    return g


def f09():  # series RL circuit: battery ε, inductor L, resistor R, switch S
    g = Fig(380, 220)
    x1, x2, y1, y2 = 40, 330, 40, 180
    inductor(g, x1, y1, x2, y1, loops=4, r=7)
    g.text((x1 + x2) / 2, y1 - 24, 'L', 18)
    resistor(g, x2, y1, x2, y2, body=46)
    g.text(x2 + 24, (y1 + y2) / 2, 'R', 18)
    cell(g, x1, y1, x1, y2)
    g.text(x1 - 22, (y1 + y2) / 2, 'ε', 18)
    switch(g, x1, y2, x2)
    g.text((x1 + x2) / 2, y2 + 22, 'S', 17, italic=False)
    return g


def f11():  # battery ε with switch S₁, branch a–R–b–L–c, switch S₂ below
    g = Fig(420, 290)
    xl, xr, yt, ym, yb = 30, 390, 40, 145, 250
    g.line(xl, yt, xl, yb, w=1.4)
    g.line(xr, yt, xr, yb, w=1.4)
    cell(g, xl, yt, 200, yt)
    g.text(115, yt - 24, 'ε', 18)
    g.text(102, yt - 20, '+', 13, italic=False)
    switch(g, 200, yt, xr, gap=40)
    g.sub(295, yt + 24, 'S', '1', 17)
    switch(g, xl, yb, xr, gap=40)
    g.sub(210, yb + 24, 'S', '2', 17)
    xa, xb, xc = 70, 210, 350
    g.line(xl, ym, xa, ym, w=1.4)
    resistor(g, xa, ym, xb, ym, body=58)
    inductor(g, xb, ym, xc, ym, loops=4, r=7)
    g.line(xc, ym, xr, ym, w=1.4)
    for x, s in ((xa, 'a'), (xb, 'b'), (xc, 'c')):
        dot(g, x, ym, 3.4)
        g.text(x, ym - 18, s, 17)
    for x in (xl, xr):
        dot(g, x, ym, 3.4)
    g.text((xa + xb) / 2, ym + 24, 'R', 17)
    g.text((xb + xc) / 2, ym + 26, 'L', 17)
    g.arrow(126, ym + 46, 168, ym + 46, GOLD, w=2, size=10)
    g.text(147, ym + 64, 'i', 17)
    return g


def f13():  # AC source with C and R in series; voltages V_C and V_R
    g = Fig(440, 230)
    xl, xr, yt, yb = 30, 410, 40, 140
    g.line(xl, yt, 205, yt, w=1.4)
    ac_source(g, 220, yt, 15)
    g.line(235, yt, xr, yt, w=1.4)
    g.line(xl, yt, xl, yb, w=1.4)
    g.line(xr, yt, xr, yb, w=1.4)
    g.arrow(130, yt - 18, 84, yt - 18, GOLD, w=2, size=10)
    g.text(107, yt - 34, 'i', 17)
    p1, p2, p3, p4 = 64, 170, 250, 360
    g.line(xl, yb, p1, yb, w=1.4)
    capacitor(g, p1, yb, p2, yb, gap=8, plate=24)
    g.line(p2, yb, p3, yb, w=1.4)
    resistor(g, p3, yb, p4, yb, body=48)
    g.line(p4, yb, xr, yb, w=1.4)
    for x in (p1, p2, p3, p4):
        dot(g, x, yb, 3.4)
    g.text((p1 + p2) / 2, yb - 26, 'C', 17)
    g.text((p3 + p4) / 2, yb - 22, 'R', 17)
    for a, b, s in ((p1, p2, 'C'), (p3, p4, 'R')):
        g.line(a, yb + 8, a, 192, w=0.9, op=0.75)
        g.line(b, yb + 8, b, 192, w=0.9, op=0.75)
        dim_h(g, 184, a, b, '', 0, 0, tick=0)
        g.rect((a + b) / 2 - 18, 196, 36, 26, stroke=None, fill=PAPER)
        g.sub((a + b) / 2, 208, 'V', s, 17)
    return g


def f15():  # a plug-in transformer (wall adapter)
    g = Fig(300, 240)
    # body
    g.rect(70, 50, 170, 150, fill=INK, fop=0.08, w=1.6, rx=18)
    g.rect(70, 50, 170, 150, stroke=None, fill=PAPER, fop=0)
    g.path('M70,82 Q155,64 240,82', w=1, op=0.6)
    for y in (110, 128, 146, 164):
        g.line(92, y, 140, y, w=1.4, op=0.55)
    g.rect(170, 104, 50, 34, fill=GOLD, fop=0.35, w=1.1, rx=4)
    g.text(195, 121, '7.5 V', 13, italic=False)
    # prongs into the wall socket
    for y in (98, 152):
        g.rect(28, y - 6, 42, 12, fill=INK, fop=0.55, w=1.1, rx=2)
    # cable to the device
    g.path('M240,175 C268,175 270,215 292,214', w=3.2)
    g.text(155, 226, 'plug-in transformer', 14, italic=False, op=0.8)
    return g


FIGURES = [
    (0, f00, 'Circular loop with resistor R in an outward field B', 1),
    (1, f01, 'Rod 5.0 cm long moving at v through an outward field', 1),
    (2, f02, 'Rod 25 cm long moving at v through an inward field', 1),
    (3, f03, 'Rod sliding left on rails 4.0 cm apart, a from the end', 1),
    (4, f04, 'Square loop moving at v into a field region B', 1),
    (5, f05, 'Rod sliding on rails with resistor R, strip ΔA = ℓΔx', 3),
    (7, f07, 'Rod from a to b below a wire with current i, moving at v', 1),
    (8, f08, 'Square coil of side a pulled out of a field region', 3),
    (9, f09, 'RL circuit: battery ε, inductor L, resistor R, switch S', 4),
    (11, f11, 'Battery ε with switches S₁, S₂ and branch a–R–b–L–c', 2),
    (13, f13, 'AC source with capacitor C and resistor R in series', 1),
    (15, f15, 'Plug-in transformer', 2),
]
