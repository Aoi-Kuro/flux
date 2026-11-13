"""Drawing helpers shared by the quiz figure modules."""
from svgkit import INK, PAPER, RED, BLUE, n


def ceiling(g, x1, x2, y=4, h=15):
    g.rect(x1, y, x2 - x1, h, fill=INK, fop=0.1, stroke=None)
    parts = []
    x = x1 + h * 0.7
    while x <= x2:
        parts.append(f'M{n(x)},{y} L{n(x - h * 0.7)},{y + h}')
        x += 6
    g.path(' '.join(parts), INK, 0.8, op=0.55)
    g.line(x1, y + h, x2, y + h, w=1.5)


def dim_v(g, x, y1, y2, label, lx, ly, tick=10, italic=True, size=17):
    if tick:
        g.line(x - tick, y1, x + tick, y1, w=0.9, op=0.75)
        g.line(x - tick, y2, x + tick, y2, w=0.9, op=0.75)
    g.arrow(x, (y1 + y2) / 2, x, y1 + 1, w=1.1, size=9)
    g.arrow(x, (y1 + y2) / 2, x, y2 - 1, w=1.1, size=9)
    if label:
        g.text(lx, ly, label, size, italic)


def dim_h(g, y, x1, x2, label, lx, ly, tick=10, italic=True, size=17):
    if tick:
        g.line(x1, y - tick, x1, y + tick, w=0.9, op=0.75)
        g.line(x2, y - tick, x2, y + tick, w=0.9, op=0.75)
    g.arrow((x1 + x2) / 2, y, x1 + 1, y, w=1.1, size=9)
    g.arrow((x1 + x2) / 2, y, x2 - 1, y, w=1.1, size=9)
    if label:
        g.text(lx, ly, label, size, italic)


def charge(g, x, y, sign, r=11):
    """A charged ball: red for +, blue for -, with its sign on it."""
    c = RED if sign == '+' else BLUE
    g.disc(x, y, r, c, 0.6)
    s = r * 0.5
    g.line(x - s, y, x + s, y, w=1.6)
    if sign == '+':
        g.line(x, y - s, x, y + s, w=1.6)


def dot(g, x, y, r=3.2):
    g.circle(x, y, r, stroke=None, fill=INK)


def capacitor(g, x1, y1, x2, y2, gap=8, plate=20, w=1.4):
    """Wire from (x1,y1) to (x2,y2) with a capacitor's two plates at its middle."""
    import math
    L = math.hypot(x2 - x1, y2 - y1)
    ux, uy = (x2 - x1) / L, (y2 - y1) / L
    px, py = -uy, ux
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    a = (mx - ux * gap / 2, my - uy * gap / 2)
    b = (mx + ux * gap / 2, my + uy * gap / 2)
    g.line(x1, y1, *a, w=w)
    g.line(*b, x2, y2, w=w)
    for cx, cy in (a, b):
        g.line(cx - px * plate / 2, cy - py * plate / 2, cx + px * plate / 2, cy + py * plate / 2, w=2.2)
    return mx, my, px, py


def battery(g, x, y1, y2, gap=8, long_=20, short=11, w=1.4):
    """Vertical wire from y1 to y2 with a cell in the middle: long plate (+) on top."""
    m = (y1 + y2) / 2
    g.line(x, y1, x, m - gap / 2, w=w)
    g.line(x, m + gap / 2, x, y2, w=w)
    g.line(x - long_ / 2, m - gap / 2, x + long_ / 2, m - gap / 2, w=1.6)
    g.line(x - short / 2, m + gap / 2, x + short / 2, m + gap / 2, w=3)
    return m


# ── circuits and fields (Set 3) ─────────────────────────────────────────────
def _axis(x1, y1, x2, y2):
    import math
    L = math.hypot(x2 - x1, y2 - y1)
    ux, uy = (x2 - x1) / L, (y2 - y1) / L
    return L, ux, uy, -uy, ux


def resistor(g, x1, y1, x2, y2, body=34, teeth=6, amp=6, w=1.4, c=None):
    """Wire from (x1,y1) to (x2,y2) with a zigzag resistor at its middle."""
    from svgkit import INK
    L, ux, uy, px, py = _axis(x1, y1, x2, y2)
    a = (L - body) / 2
    pts = [(x1, y1), (x1 + ux * a, y1 + uy * a)]
    for k in range(teeth):
        t = a + body * (k + 0.5) / teeth
        s = amp if k % 2 == 0 else -amp
        pts.append((x1 + ux * t + px * s, y1 + uy * t + py * s))
    pts += [(x1 + ux * (a + body), y1 + uy * (a + body)), (x2, y2)]
    g.path('M' + ' L'.join(f'{n(x)},{n(y)}' for x, y in pts), c or INK, w)
    return (x1 + x2) / 2, (y1 + y2) / 2


def inductor(g, x1, y1, x2, y2, loops=4, r=6, w=1.4, c=None):
    """Wire with a coil of `loops` half-turns bulging to the left of travel."""
    from svgkit import INK
    L, ux, uy, px, py = _axis(x1, y1, x2, y2)
    body = loops * 2 * r
    a = (L - body) / 2
    sx, sy = x1 + ux * a, y1 + uy * a
    d = f'M{n(x1)},{n(y1)} L{n(sx)},{n(sy)}'
    for k in range(loops):
        ex, ey = sx + ux * 2 * r, sy + uy * 2 * r
        d += f' A{n(r)},{n(r)} 0 0 1 {n(ex)},{n(ey)}'
        sx, sy = ex, ey
    d += f' L{n(x2)},{n(y2)}'
    g.path(d, c or INK, w)
    return (x1 + x2) / 2, (y1 + y2) / 2


def switch(g, x1, y, x2, gap=34, w=1.4):
    """Horizontal wire with an open switch in the middle."""
    from svgkit import INK, PAPER
    m = (x1 + x2) / 2
    a, b = m - gap / 2, m + gap / 2
    g.line(x1, y, a, y, w=w)
    g.line(b, y, x2, y, w=w)
    g.line(a, y, b - 3, y - 14, w=1.6)
    for x in (a, b):
        g.circle(x, y, 3, fill=PAPER, w=1.2)
    return m


def cell(g, x1, y1, x2, y2, gap=8, long_=22, short=12, w=1.4):
    """Wire with a cell at its middle; the long (+) plate faces (x1,y1)."""
    L, ux, uy, px, py = _axis(x1, y1, x2, y2)
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    a = (mx - ux * gap / 2, my - uy * gap / 2)
    b = (mx + ux * gap / 2, my + uy * gap / 2)
    g.line(x1, y1, *a, w=w)
    g.line(*b, x2, y2, w=w)
    g.line(a[0] - px * long_ / 2, a[1] - py * long_ / 2, a[0] + px * long_ / 2, a[1] + py * long_ / 2, w=1.6)
    g.line(b[0] - px * short / 2, b[1] - py * short / 2, b[0] + px * short / 2, b[1] + py * short / 2, w=3)
    return mx, my


def ac_source(g, cx, cy, r=14):
    from svgkit import PAPER
    g.circle(cx, cy, r, fill=PAPER, w=1.4)
    g.path(f'M{n(cx - r * 0.6)},{n(cy)} C{n(cx - r * 0.3)},{n(cy - r * 0.7)} {n(cx)},{n(cy - r * 0.7)} {n(cx)},{n(cy)} '
           f'S{n(cx + r * 0.3)},{n(cy + r * 0.7)} {n(cx + r * 0.6)},{n(cy)}', w=1.3)


def field(g, x1, y1, x2, y2, step, kind, size=4.5, op=0.55):
    """A grid of B-field marks: 'dot' (out of the page) or 'cross' (into it)."""
    from svgkit import INK
    y = y1
    while y <= y2 + 0.1:
        x = x1
        while x <= x2 + 0.1:
            if kind == 'dot':
                g.raw(f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(size * 0.55)}" fill="{INK}" opacity="{op}"/>')
            else:
                s = size * 0.7
                g.path(f'M{n(x - s)},{n(y - s)} L{n(x + s)},{n(y + s)} M{n(x - s)},{n(y + s)} L{n(x + s)},{n(y - s)}', INK, 1.3, op=op)
            x += step
        y += step


def rod(g, x, y1, y2, w=9):
    """A metal rod seen side-on, vertical."""
    from svgkit import INK, PAPER
    g.rect(x - w / 2, y1, w, y2 - y1, stroke=None, fill=PAPER, rx=w / 2)
    g.rect(x - w / 2, y1, w, y2 - y1, fill=INK, fop=0.2, w=1.1, rx=w / 2)
