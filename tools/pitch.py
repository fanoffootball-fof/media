"""Scène « but refait en 2D » pour @fanoffootball : terrain vu de dessus, joueurs et ballon animés.

L'équipe qui attaque monte vers le haut de l'écran. Coordonnées des specs :
  x : 0 = ligne de touche gauche, 100 = ligne de touche droite (68 m)
  y : 0 = propre ligne de but, 100 = ligne de but adverse (105 m), au-delà de 100 = dans le but
Seule la portion y >= view_from est affichée (50 = moitié de terrain adverse, par défaut).
Les temps des images clés sont en secondes « réelles » ; speed < 1 donne un ralenti.
"""
import math
from functools import lru_cache

import numpy as np
from PIL import Image, ImageChops, ImageDraw

from engine import FPS, GOLD, W, WHITE, ease_back, ease_out, fit_size, prog, put, rrect, text, with_alpha

PL, PW = 105.0, 68.0         # longueur, largeur (m)
MAX_W, MAX_H, TOP = 820, 650, 545
NET = 2.0                    # profondeur du filet (m)
CAP_Y = 1300                 # ligne des légendes
SS = 2                       # suréchantillonnage des traits

TURF_A, TURF_B = (22, 88, 50, 165), (28, 100, 58, 165)
LINE = (255, 255, 255, 215)
DEF_COLOR, GK_COLOR = (232, 235, 242), (255, 196, 40)


class Geo:
    def __init__(self, view_from=50.0):
        self.y0 = PL * max(0.0, min(80.0, float(view_from))) / 100
        length = PL - self.y0
        self.s = min(MAX_W / PW, MAX_H / (length + NET + 1))
        self.w, self.h = PW * self.s, length * self.s
        self.left = W / 2 - self.w / 2
        self.top = TOP + (NET + 1) * self.s      # ligne de but adverse
        self.bottom = self.top + self.h
        self.ox, self.oy = int(self.left - 30), TOP - 10
        self.rw, self.rh = int(self.w + 60), int(self.bottom - self.oy + 30)

    def m(self, mx, my):
        return self.left + mx * self.s, self.top + (PL - my) * self.s

    def pt(self, x, y):
        return self.m(x / 100 * PW, y / 100 * PL)


def make_pitch(g):
    S = SS
    im = Image.new("RGBA", (g.rw * S, g.rh * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    def P(mx, my):
        x, y = g.m(mx, my)
        return (x - g.ox) * S, (y - g.oy) * S

    # pelouse en bandes de tonte (5,25 m)
    my, k = PL, 0
    while my > g.y0 + 1e-6:
        a, b = P(0, my), P(PW, max(g.y0, my - 5.25))
        d.rectangle((a[0], a[1], b[0], b[1]), fill=TURF_A if k % 2 == 0 else TURF_B)
        my -= 5.25
        k += 1

    lw = 3 * S

    def line(p, q):
        d.line([P(*p), P(*q)], fill=LINE, width=lw)

    def rect(x0, y0, x1, y1):
        a, b = P(x0, y1), P(x1, y0)
        d.rectangle((a[0], a[1], b[0], b[1]), outline=LINE, width=lw)

    def circle(cx, cy, r, start=0, end=360):
        a, b = P(cx - r, cy + r), P(cx + r, cy - r)
        d.arc((a[0], a[1], b[0], b[1]), start, end, fill=LINE, width=lw)

    def spot(cx, cy):
        r = 0.35 * g.s * S
        x, y = P(cx, cy)
        d.ellipse((x - r, y - r, x + r, y + r), fill=LINE)

    line((0, g.y0), (0, PL))
    line((PW, g.y0), (PW, PL))
    if g.y0 <= 0.01:
        line((0, 0), (PW, 0))
    if g.y0 < PL / 2:
        line((0, PL / 2), (PW, PL / 2))
        circle(PW / 2, PL / 2, 9.15)
        spot(PW / 2, PL / 2)
    for end in (PL, 0.0):  # surface adverse puis propre surface
        sgn = 1 if end == PL else -1
        line((0, end), (PW, end))
        bx = (PW - 40.32) / 2
        rect(bx, min(end, end - sgn * 16.5), bx + 40.32, max(end, end - sgn * 16.5))
        gx = (PW - 18.32) / 2
        rect(gx, min(end, end - sgn * 5.5), gx + 18.32, max(end, end - sgn * 5.5))
        spot(PW / 2, end - sgn * 11)
        if sgn == 1:
            circle(PW / 2, end - 11, 9.15, 36.87, 143.13)
            circle(0, end, 1.0, 0, 90)
            circle(PW, end, 1.0, 90, 180)
        else:
            circle(PW / 2, end + 11, 9.15, 216.87, 323.13)
        # but et filet
        px0, px1 = PW / 2 - 3.66, PW / 2 + 3.66
        back = end + sgn * NET
        for xx in np.arange(px0, px1 + 0.01, 0.6):
            d.line([P(xx, end), P(xx, back)], fill=(255, 255, 255, 70), width=S)
        for yy in np.arange(0.5, NET, 0.5):
            d.line([P(px0, end + sgn * yy), P(px1, end + sgn * yy)], fill=(255, 255, 255, 70), width=S)
        d.line([P(px0, end), P(px0, back), P(px1, back), P(px1, end)], fill=LINE, width=lw)

    # on ne garde que le terrain visible (et le but adverse)
    mask = Image.new("L", im.size, 0)
    md = ImageDraw.Draw(mask)
    a, b = P(-0.3, PL + 0.3), P(PW + 0.3, g.y0)
    md.rectangle((a[0], a[1], b[0], b[1]), fill=255)
    a, b = P(PW / 2 - 4.2, PL + NET + 0.6), P(PW / 2 + 4.2, PL)
    md.rectangle((a[0], a[1], b[0], b[1]), fill=255)
    im.putalpha(ImageChops.multiply(im.getchannel("A"), mask))
    im = im.resize((g.rw, g.rh), Image.LANCZOS)
    if g.y0 > 0.01:  # le bas du terrain se fond dans le décor
        arr = np.asarray(im).copy()
        yb = int(g.bottom - g.oy)
        fade = int(min(140, g.h * 0.25))
        ramp = np.ones(arr.shape[0], np.float32)
        ramp[yb - fade:yb] = np.linspace(1, 0, fade)
        ramp[yb:] = 0
        arr[..., 3] = (arr[..., 3] * ramp[:, None]).astype(np.uint8)
        im = Image.fromarray(arr)
    return im


@lru_cache(maxsize=128)
def disc(r, fill, ring=None, ring_w=0.0, alpha=255):
    S = 4
    R = r + ring_w
    size = int(math.ceil(R * 2 + 4)) * S
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = size / 2
    if ring:
        d.ellipse((c - R * S, c - R * S, c + R * S, c + R * S), fill=tuple(ring) + (alpha,))
    d.ellipse((c - r * S, c - r * S, c + r * S, c + r * S), fill=tuple(fill) + (alpha,))
    return im.resize((size // S, size // S), Image.LANCZOS)


class Mover:
    """Trajectoire par images clés [x, y, t] ou [x, y, t, "air"] (segment aérien jusqu'à ce point)."""

    def __init__(self, path, kind="player"):
        self.k = sorted(((float(p[0]), float(p[1]), float(p[2]), len(p) > 3 and "air" in str(p[3]).split()) for p in path),
                        key=lambda q: q[2])
        self.kind = kind
        for x, y, _, _ in self.k:
            if not (-5 <= x <= 105 and -5 <= y <= 103):
                raise ValueError(f"coordonnées hors terrain : {x}, {y}")

    def at(self, t):
        k = self.k
        if t <= k[0][2] or len(k) == 1:
            return k[0][0], k[0][1], 0.0
        for i in range(len(k) - 1):
            a, b = k[i], k[i + 1]
            if t <= b[2]:
                u = (t - a[2]) / max(1e-6, b[2] - a[2])
                if self.kind == "ball":
                    v = u if b[3] else 1 - (1 - u) ** 1.4   # passe qui ralentit un peu
                else:
                    first, last = i == 0, i == len(k) - 2
                    if first and last:
                        v = u * u * (3 - 2 * u)
                    elif first:
                        v = u * u * (2 - u)
                    elif last:
                        v = 1 - (1 - u) ** 2
                    else:
                        v = u
                h = 4 * u * (1 - u) if b[3] else 0.0
                return a[0] + (b[0] - a[0]) * v, a[1] + (b[1] - a[1]) * v, h
        return k[-1][0], k[-1][1], 0.0

    def trail(self, t, step=1 / 60):
        t0 = self.k[0][2]
        if t <= t0:
            return []
        ts = list(np.arange(t0, t, step)) + [t]
        return [self.at(x)[:2] for x in ts]


class PitchView:
    """Élément de scène (même interface que les éléments de make_video : y, start, h, gap, draw)."""
    h, gap = 0, 0

    def __init__(self, sc, accent):
        self.y = 0
        self.start = 4
        self.g = Geo(sc.get("view_from", 50))
        self.img = make_pitch(self.g)
        self.speed = float(sc.get("speed", 1.0))
        self.t0 = float(sc.get("t0", 0.0))
        att = tuple(accent)
        self.players = []
        for p in sc.get("players", []):
            team = p.get("team", "att")
            base = {"att": att, "def": DEF_COLOR, "gk": GK_COLOR}[team]
            c = p.get("color")
            self.players.append({
                "m": Mover(p["path"]), "team": team, "label": p.get("label"),
                "star": bool(p.get("star")), "color": tuple(c) if c else base,
            })
        order = {"def": 0, "gk": 1, "att": 2}
        self.players.sort(key=lambda q: (order[q["team"]], q["star"]))
        self.ball = Mover(sc["ball"], "ball") if sc.get("ball") else None
        self.goal_t = sc.get("goal_t")
        self.captions = sorted((float(c[0]), c[1]) for c in sc.get("captions", []))

    def hits(self):
        if self.goal_t is None or self.goal_t < self.t0:
            return []
        return [self.start / FPS + (self.goal_t - self.t0) / self.speed]

    def draw(self, fr, f, cy):
        g = self.g
        a = ease_out(prog(f, self.start - 4, 8))
        t = self.t0 + max(0, f - self.start) / FPS * self.speed
        put(fr, self.img, g.ox + g.rw / 2, g.oy + g.rh / 2, a)

        ov = Image.new("RGBA", (g.rw * SS, g.rh * SS), (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)

        def P(x, y):
            sx, sy = g.pt(x, y)
            return (sx - g.ox) * SS, (sy - g.oy) * SS

        for p in self.players:   # course des joueurs clés, en pointillés
            if p["star"]:
                pts = p["m"].trail(t)
                for i in range(0, len(pts), 5):
                    x, y = P(*pts[i])
                    r = 3.5 * SS
                    d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 255, 255, 120))
        if self.ball:
            pts = [P(*q) for q in self.ball.trail(t)]
            if len(pts) > 1:
                d.line(pts, fill=GOLD + (200,), width=5 * SS, joint="curve")
        fr.alpha_composite(with_alpha(ov.resize((g.rw, g.rh), Image.BILINEAR), a), (g.ox, g.oy))

        r = 21
        for p in self.players:
            x, y, _ = p["m"].at(t)
            sx, sy = g.pt(x, y)
            ring = GOLD if p["star"] else (15, 18, 26)
            put(fr, disc(r, p["color"], ring, 5.0 if p["star"] else 2.5), sx, sy, a)
        if self.ball:
            x, y, hgt = self.ball.at(t)
            sx, sy = g.pt(x, y)
            put(fr, disc(9 + 3 * hgt, (0, 0, 0), None, 0, 110), sx + 4 * hgt, sy + 3, a)
            put(fr, disc(10 * (1 + 0.55 * hgt), WHITE, (20, 20, 30), 2.5), sx, sy - 34 * hgt, a)
        for p in self.players:
            if p["label"]:
                x, y, _ = p["m"].at(t)
                sx, sy = g.pt(x, y)
                lab = p["label"]
                sz = 30 if p["star"] else 26
                lw = text_w(lab, sz) + 26
                ly = sy + 44 if sy < g.bottom - 70 else sy - 44
                rrect(fr, sx, ly, lw, sz + 18, (sz + 18) / 2, (10, 12, 18), 0.72, a)
                text(fr, lab, sx, ly, "bold", sz, GOLD if p["star"] else WHITE, alpha=a, fit=False)

        if self.goal_t is not None and t >= self.goal_t:
            k = (t - self.goal_t) / self.speed      # secondes vidéo depuis le but
            nx, ny = g.m(PW / 2, PL + NET / 2)
            rrect(fr, nx, ny, 7.6 * g.s, NET * g.s + 8, 6, GOLD, 0.75 * math.exp(-2.0 * k), 1.0)
            rrect(fr, W / 2, (g.top + g.bottom) / 2, g.w, g.h, 18, WHITE, 0.30 * math.exp(-7 * k), 1.0)
            pop = ease_back(min(1.0, k * FPS / 9))
            by = g.bottom - 45   # dans le bas du terrain, loin de l'action
            text(fr, "BUT !", W / 2 + 5, by + 6, "black", 150, (0, 0, 0), alpha=0.45, scale=pop, fit=False)
            text(fr, "BUT !", W / 2, by, "black", 150, GOLD, scale=pop, fit=False)

        cap = None
        for ct, s in self.captions:
            if t >= ct:
                cap = (ct, s)
        if cap:
            ca = ease_out(min(1.0, (t - cap[0]) / self.speed * FPS / 6)) * a
            sz = fit_size(cap[1], "xbold", 58, 900)
            text(fr, cap[1], W / 2, CAP_Y + (1 - ca) * 20, "xbold", sz, WHITE, alpha=ca, fit=False)


def text_w(s, size):
    from engine import font
    l, _, r, _ = font("bold", size).getbbox(s)
    return r - l
