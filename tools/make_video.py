"""Génère une vidéo TikTok @fanoffootball à partir d'une spec JSON.

    python tools/make_video.py specs/ma_video.json videos/ma_video.mp4
    python tools/make_video.py specs/ma_video.json --stills /chemin/dossier   # images de contrôle

Format de la spec : voir tools/SPEC.md et les exemples dans specs/.
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from functools import lru_cache  # noqa: E402

from PIL import Image, ImageDraw  # noqa: E402
from scipy.io import wavfile  # noqa: E402

import music  # noqa: E402
from engine import (FPS, GOLD, GREY, H, W, WHITE, assemble, bar_lr, ease_back,  # noqa: E402
                    ease_out, fit_size, font, make_background, make_split_background, prog, put,
                    render_scene, render_still, rrect, text)

COLORS = {
    "white": WHITE, "gold": GOLD, "grey": GREY, "light": (220, 222, 230),
    "red": (215, 38, 61), "green": (46, 160, 90), "blue": (61, 123, 255),
    "pink": (255, 59, 92), "purple": (120, 70, 220), "orange": (255, 140, 40),
    "cyan": (40, 190, 220), "dark": (20, 20, 30),
}


def col(c, default=WHITE):
    if c is None:
        return default
    if isinstance(c, (list, tuple)):
        return tuple(int(v) for v in c)
    if isinstance(c, str) and c.startswith("#") and len(c) == 7:
        return tuple(int(c[i:i + 2], 16) for i in (1, 3, 5))
    return COLORS[c]


def appear(f, start, dur=12):
    p = prog(f, start, dur)
    a = ease_out(p)
    s = (0.6 + 0.4 * ease_back(p)) if p > 0 else 0.6
    return a, s, (1 - a) * 40


# ---------------------------------------------------------------- éléments
class El:
    h = 100
    gap = 7          # images avant l'élément suivant
    y = None         # position absolue (sinon empilement automatique)
    start = 0

    def draw(self, fr, f, cy):
        raise NotImplementedError


class Big(El):
    def __init__(self, t, color="white", size=200, anim="zoom", fit_to=None):
        self.t, self.c, self.anim = t, col(color), anim
        self.size = fit_size(fit_to or t, "black", size)
        self.h = self.size * 1.18 + 18

    def draw(self, fr, f, cy):
        if self.anim == "pop":
            a, s, _ = appear(f, self.start)
            text(fr, self.t, W / 2, cy, "black", self.size, self.c, alpha=a, scale=s, fit=False)
        else:
            p = ease_out(prog(f, self.start, 12))
            text(fr, self.t, W / 2, cy, "black", self.size, self.c, alpha=p, scale=1.25 - 0.25 * p, fit=False)


class Txt(El):
    gap = 6

    def __init__(self, t, weight="semi", size=56, color="white"):
        self.t, self.w, self.c = t, weight, col(color)
        self.size = fit_size(t, weight, size)
        self.h = self.size * 1.45

    def draw(self, fr, f, cy):
        a, _, dy = appear(f, self.start)
        text(fr, self.t, W / 2, cy + dy, self.w, self.size, self.c, alpha=a, fit=False)


class Pill(El):
    gap = 8

    def __init__(self, t, color="red", text_color="white", size=36, alpha=1.0):
        self.t, self.c, self.tc, self.size, self.fa = t, col(color), col(text_color), size, alpha
        self.h = 110
        l, tt, r, b = font("bold", size).getbbox(t)
        self.w = min(960, r - l + 90)

    def draw(self, fr, f, cy):
        a, s, _ = appear(f, self.start)
        rrect(fr, W / 2, cy, self.w * s, 74, 37, self.c, self.fa, a)
        text(fr, self.t, W / 2, cy, "bold", self.size, self.tc, alpha=a, scale=s, fit=False)


class Counter(El):
    gap = 40

    def __init__(self, value, frm=0, size=280, color="gold", prefix="", suffix=""):
        self.v, self.frm, self.size, self.c = value, frm, size, col(color)
        self.pre, self.suf = prefix, suffix
        self.h = size * 1.08

    def draw(self, fr, f, cy):
        v = self.frm + (self.v - self.frm) * ease_out(prog(f, self.start + 2, 36))
        if isinstance(self.v, int) and isinstance(self.frm, int):
            s = f"{int(round(v))}"
        else:
            s = f"{v:.1f}".replace(".", ",")
        a = ease_out(prog(f, self.start, 6))
        text(fr, self.pre + s + self.suf, W / 2, cy, "black", self.size, self.c, alpha=a)


class Card(El):
    gap = 14

    def __init__(self, main, sub=None, badge=None, dim=False):
        self.main, self.sub, self.badge, self.dim = main, sub, badge, dim
        self.h = 190 if sub else 165

    def draw(self, fr, f, cy):
        a, _, dy = appear(f, self.start, 14)
        y = cy + dy
        hh = 170 if self.sub else 145
        rrect(fr, W / 2, y, 900, hh, 30, (255, 255, 255), 0.06 if self.dim else 0.11, a)
        tx = W / 2
        if self.badge is not None:
            bc = GOLD if not self.dim else (150, 130, 80)
            rrect(fr, 160, y, 76, 76, 38, bc, 1.0, a)
            text(fr, str(self.badge), 160, y, "black", 44, (20, 20, 30), alpha=a, fit=False)
            tx = W / 2 + 50
        else:
            bar_lr(fr, W / 2 - 400, W / 2 - 388, y, hh - 60, GOLD, a)
        tcol = WHITE if not self.dim else (170, 174, 186)
        if self.sub:
            text(fr, self.main, tx, y - 28, "xbold", 54, tcol, alpha=a)
            text(fr, self.sub, tx, y + 34, "med", 40, (200, 204, 214) if not self.dim else GREY, alpha=a)
        else:
            text(fr, self.main, tx, y, "xbold", 58, tcol, alpha=a)


class Bar(El):
    gap = 45

    def __init__(self, value, target, left_label="0", right_label=None, color="gold"):
        self.v, self.t = value, target
        self.ll, self.rl = left_label, right_label if right_label is not None else str(target)
        self.c = col(color)
        self.h = 120

    def draw(self, fr, f, cy):
        a = ease_out(prog(f, self.start, 10))
        x0, x1 = 130, 950
        rrect(fr, (x0 + x1) / 2, cy, x1 - x0, 34, 17, (255, 255, 255), 0.15, a)
        fill = ease_out(prog(f, self.start + 2, 40)) * max(0, min(1, self.v / self.t))
        bar_lr(fr, x0, x0 + (x1 - x0) * fill, cy, 34, self.c, a)
        text(fr, self.ll, x0 + 10, cy + 52, "semi", 30, GREY, alpha=a, fit=False)
        text(fr, self.rl, x1 - 30, cy + 52, "semi", 30, GREY, alpha=a, fit=False)


class NamesRow(El):
    gap = 8

    def __init__(self, left, right, lc, rc):
        self.l, self.r, self.lc, self.rc = left, right, lc, rc
        self.h = 130

    def draw(self, fr, f, cy):
        a, _, dy = appear(f, self.start)
        sz = min(fit_size(self.l, "black", 64, 420), fit_size(self.r, "black", 64, 420))
        text(fr, self.l, 270, cy + dy, "black", sz, self.lc, alpha=a, fit=False)
        text(fr, self.r, 810, cy + dy, "black", sz, self.rc, alpha=a, fit=False)


class DuelRow(El):
    gap = 50

    def __init__(self, label, lv, rv, lc, rc, fmt="{:g}"):
        self.label, self.lv, self.rv, self.lc, self.rc, self.fmt = label, lv, rv, lc, rc, fmt
        self.h = 240

    def draw(self, fr, f, cy):
        a, _, dy = appear(f, self.start, 12)
        y = cy + 40
        text(fr, self.label, W / 2, y - 80 + dy * 0.75, "bold", 42, (220, 222, 230), alpha=a)
        g = ease_out(prog(f, self.start + 6, 30))
        vmax = max(self.lv, self.rv, 1e-9)
        lw, rw = self.lv >= self.rv, self.rv >= self.lv
        dimc = (75, 80, 100)
        bar_lr(fr, 505, 505 - 225 * (self.lv / vmax) * g, y + dy * 0.75, 64, self.lc if lw else dimc, a)
        bar_lr(fr, 575, 575 + 225 * (self.rv / vmax) * g, y + dy * 0.75, 64, self.rc if rw else dimc, a)

        def show(v):
            x = v * g
            return self.fmt.format(round(x) if float(v).is_integer() else round(x, 1)).replace(".", ",")
        text(fr, show(self.lv), 175, y + dy * 0.75, "black", 104, WHITE if lw else GREY, alpha=a, fit=False)
        text(fr, show(self.rv), 905, y + dy * 0.75, "black", 104, WHITE if rw else GREY, alpha=a, fit=False)


class Options(El):
    gap = 6

    def __init__(self, opts, filled=True):
        self.opts = [(o["label"], col(o.get("color", "grey"))) for o in opts]
        self.filled = filled
        self.h = 200

    def draw(self, fr, f, cy):
        n = len(self.opts)
        spacing = 420 if n == 2 else 260
        bw = 380 if n == 2 else 220
        for i, (lab, c) in enumerate(self.opts):
            a, s, _ = appear(f, self.start + i * 6)
            cx = W / 2 + (i - (n - 1) / 2) * spacing
            rrect(fr, cx, cy, bw * s, 150 * s, 40, c, 1.0 if self.filled else 0.14, a)
            sz = fit_size(lab, "black", 72 if n == 2 else 90, bw - 40)
            text(fr, lab, cx, cy, "black", sz, WHITE, alpha=a, scale=s, fit=False)


class Chips(El):
    gap = 6

    def __init__(self, chips):
        self.chips = [(c["label"], c.get("sub"), col(c.get("color", "grey"))) for c in chips]
        self.h = 190

    def draw(self, fr, f, cy):
        n = len(self.chips)
        for i, (lab, sub, c) in enumerate(self.chips):
            a, _, dy = appear(f, self.start + i * 6)
            cx = W / 2 + (i - (n - 1) / 2) * 420
            rrect(fr, cx, cy + dy, 380, 150, 30, c, 0.22, a)
            if sub:
                text(fr, lab, cx, cy - 30 + dy, "xbold", fit_size(lab, "xbold", 54, 340), WHITE, alpha=a, fit=False)
                text(fr, sub, cx, cy + 35 + dy, "semi", fit_size(sub, "semi", 40, 340), (220, 222, 230), alpha=a, fit=False)
            else:
                text(fr, lab, cx, cy + dy, "xbold", fit_size(lab, "xbold", 54, 340), WHITE, alpha=a, fit=False)


class Box(El):
    gap = 8

    def __init__(self, line1, line2=None, color2="gold"):
        self.l1, self.l2, self.c2 = line1, line2, col(color2)
        self.h = 190 if line2 else 140

    def draw(self, fr, f, cy):
        a, _, dy = appear(f, self.start)
        hh = 150 if self.l2 else 110
        rrect(fr, W / 2, cy + dy, 900, hh, 30, (255, 255, 255), 0.09, a)
        if self.l2:
            text(fr, self.l1, W / 2, cy - 30 + dy, "semi", fit_size(self.l1, "semi", 46, 840), WHITE, alpha=a, fit=False)
            text(fr, self.l2, W / 2, cy + 30 + dy, "semi", fit_size(self.l2, "semi", 46, 840), self.c2, alpha=a, fit=False)
        else:
            text(fr, self.l1, W / 2, cy + dy, "semi", fit_size(self.l1, "semi", 46, 840), WHITE, alpha=a, fit=False)


@lru_cache(maxsize=256)
def ring_img(frac_q, color):
    r, w = 92, 14
    size = 2 * r + 8
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    box = (4, 4, size - 4, size - 4)
    d.ellipse(box, outline=(255, 255, 255, 50), width=w)
    if frac_q > 0:
        d.arc(box, -90, -90 + 360 * frac_q / 100, fill=color + (255,), width=w)
    return im


class Countdown(El):
    gap = 0
    h = 220

    def draw(self, fr, f, cy):
        if f < self.start:
            return
        el = (f - self.start) / FPS
        sec = 0 if el >= 3.0 else 3 - int(el)
        frac = 1 - min(el, 3.0) / 3.0
        a = ease_out(prog(f, self.start, 8))
        c = GOLD if sec > 1 else (255, 90, 90)
        put(fr, ring_img(int(frac * 100), c), W / 2, cy, a)
        if sec > 0:
            s = 1.25 - 0.25 * ease_out(min(1, (el - int(el)) * 4))
            text(fr, str(sec), W / 2, cy, "black", 90, WHITE, alpha=a, scale=s, fit=False)
        else:
            text(fr, "?", W / 2, cy, "black", 90, WHITE, alpha=a, fit=False)


class Spacer(El):
    gap = 0

    def __init__(self, h):
        self.h = h

    def draw(self, fr, f, cy):
        pass


# ---------------------------------------------------------------- scènes
def L(lines, default_color="white"):
    out = []
    for ln in lines:
        if isinstance(ln, str):
            out.append((ln, default_color))
        else:
            out.append((ln["t"], ln.get("color", default_color)))
    return out


def scene_elements(sc, ctx):
    t = sc["type"]
    els = []
    if t == "title":
        if sc.get("kicker"):
            els.append(Pill(sc["kicker"], "gold", "dark", 44))
        lines = L(sc["lines"])
        longest = max((x for x, _ in lines), key=len)
        size = sc.get("size", 220 if len(lines) <= 2 else 160)
        for x, c in lines:
            els.append(Big(x, c, size, fit_to=longest))
        for i, s in enumerate(sc.get("sub", [])):
            els.append(Txt(s, "bold" if i == 0 else "med", 74 if i == 0 else 50, "white" if i == 0 else "light"))
        if sc.get("pill"):
            els.append(Pill(sc["pill"], ctx["accent"]))
    elif t == "counters":
        if sc.get("top"):
            els.append(Txt(sc["top"], "bold", 50, "light"))
        for it in sc["items"]:
            els.append(Counter(it["value"], it.get("from", 0), it.get("size", 260), it.get("color", "gold"),
                               it.get("prefix", ""), it.get("suffix", "")))
            els.append(Txt(it["label"], "xbold", 70, "white"))
        if sc.get("chips"):
            els.append(Chips(sc["chips"]))
        if sc.get("badge"):
            els.append(Pill(sc["badge"], "white", "white", 40, 0.12))
    elif t == "cards":
        if sc.get("title"):
            els.append(Big(sc["title"], "white", 96, anim="pop"))
        if sc.get("subtitle"):
            els.append(Txt(sc["subtitle"], "med", 52, "light"))
        els.append(Spacer(30))
        for i, it in enumerate(sc["items"]):
            main, sub = (it, None) if isinstance(it, str) else (it[0], it[1] if len(it) > 1 else None)
            els.append(Card(main, sub, badge=(i + 1) if sc.get("numbered") else None))
    elif t == "progress":
        if sc.get("top"):
            els.append(Txt(sc["top"], "bold", 52, "light"))
        els.append(Counter(sc["value"], sc.get("from", 0), 280, sc.get("color", "white")))
        els.append(Txt(sc["label"], "xbold", 64, "white"))
        els.append(Bar(sc["value"], sc["target"], sc.get("left_label", "0"), sc.get("right_label")))
        if sc.get("big"):
            els.append(Big(sc["big"], "gold", 130, anim="pop"))
        if sc.get("sub"):
            els.append(Txt(sc["sub"], "semi", 54, "white"))
    elif t == "duel":
        lc, rc = col(ctx["left_color"]), col(ctx["right_color"])
        els.append(NamesRow(sc.get("left", ctx.get("left_name", "")).upper(),
                            sc.get("right", ctx.get("right_name", "")).upper(), lc, rc))
        els.append(Spacer(20))
        for r in sc["rows"]:
            els.append(DuelRow(r["label"], r["l"], r["r"], lc, rc))
    elif t == "statement":
        lines = L(sc["lines"])
        longest = max((x for x, _ in lines), key=len)
        for x, c in lines:
            els.append(Big(x, c, sc.get("size", 92), anim="pop", fit_to=longest))
        if sc.get("box"):
            b = sc["box"]
            els.append(Spacer(30))
            els.append(Box(b[0], b[1] if len(b) > 1 else None))
    elif t == "poll":
        lines = L(sc["lines"])
        longest = max((x for x, _ in lines), key=len)
        for x, c in lines:
            els.append(Big(x, c, sc.get("size", 130), anim="pop", fit_to=longest))
        els.append(Spacer(30))
        els.append(Options(sc["options"], sc.get("filled", True)))
        els.append(Txt(sc.get("cta", "Réponds en commentaire"), "semi", 54, "white"))
    elif t == "reveal":
        if sc.get("pre"):
            els.append(Txt(sc["pre"], "black", 80, "white"))
        lines = L(sc["lines"], "gold")
        longest = max((x for x, _ in lines), key=len)
        for x, c in lines:
            els.append(Big(x, c, sc.get("size", 180), fit_to=longest))
        if sc.get("sub"):
            els.append(Txt(sc["sub"], "semi", 54, "white"))
        if sc.get("pill"):
            els.append(Pill(sc["pill"], "white", "white", 40, 0.14))
    elif t == "quiz_clue":
        return quiz_elements(sc, ctx)
    elif t == "custom":
        for e in sc["elements"]:
            els.append(custom_el(e, ctx))
    else:
        raise ValueError(f"type de scène inconnu : {t}")
    return els


def custom_el(e, ctx):
    k = e["kind"]
    if k == "big":
        return Big(e["t"], e.get("color", "white"), e.get("size", 160), e.get("anim", "zoom"))
    if k == "text":
        return Txt(e["t"], e.get("weight", "semi"), e.get("size", 56), e.get("color", "white"))
    if k == "pill":
        return Pill(e["t"], e.get("color", ctx["accent"]), e.get("text_color", "white"))
    if k == "counter":
        return Counter(e["value"], e.get("from", 0), e.get("size", 260), e.get("color", "gold"),
                       e.get("prefix", ""), e.get("suffix", ""))
    if k == "card":
        return Card(e["main"], e.get("sub"), e.get("badge"))
    if k == "bar":
        return Bar(e["value"], e["target"], e.get("left_label", "0"), e.get("right_label"))
    if k == "options":
        return Options(e["options"], e.get("filled", True))
    if k == "chips":
        return Chips(e["chips"])
    if k == "box":
        return Box(e["line1"], e.get("line2"))
    if k == "spacer":
        return Spacer(e.get("h", 40))
    raise ValueError(f"élément inconnu : {k}")


CARD_Y = [660, 860, 1060]


def quiz_elements(sc, ctx):
    els = []
    p = Pill(sc.get("kicker", "QUIZ"), "gold", "dark", 36)
    p.y, p.start = 365, -100
    els.append(p)
    tt = Big(sc.get("title", "DEVINE LE JOUEUR"), "white", 84)
    tt.y, tt.start = 465, -100
    els.append(tt)
    i = sc["index"]
    for j, cl in enumerate(sc["clues"][: i + 1]):
        c = Card(cl[0], cl[1] if len(cl) > 1 else None, badge=j + 1, dim=j < i)
        c.y = CARD_Y[j]
        c.start = -100 if j < i else 0
        els.append(c)
    cd = Countdown()
    cd.y, cd.start = 1290, 15
    els.append(cd)
    return els


def layout(els, dur_frames, center=930):
    # départs échelonnés (sauf éléments déjà positionnés/démarrés)
    t = 0
    seq = [e for e in els if e.start == 0 and not isinstance(e, Countdown)]
    for e in seq:
        e.start = t
        t += e.gap
    last = max((e.start for e in seq), default=0)
    limit = max(1, dur_frames - 30)
    if last > limit:  # compresse si la scène est trop courte
        k = limit / last
        for e in seq:
            e.start = int(e.start * k)
    stack = [e for e in els if e.y is None]
    total = sum(e.h for e in stack)
    y = center - total / 2
    if total > 1060:
        print(f"  ! attention : contenu haut de {int(total)} px (max conseillé 1060)", file=sys.stderr)
    for e in stack:
        e.cy = y + e.h / 2
        y += e.h
    for e in els:
        if e.y is not None:
            e.cy = e.y
    return els


def build_scene(sc, ctx, dur_frames):
    els = layout(scene_elements(sc, ctx), dur_frames)
    source = sc.get("source")

    def draw(fr, f):
        for e in els:
            e.draw(fr, f, e.cy)
        if source:
            text(fr, source, W / 2, 1420, "med", 30, GREY, alpha=ease_out(prog(f, 20, 10)))
    ticks = []
    for e in els:
        if isinstance(e, Countdown):
            ticks += [(e.start / FPS) + k for k in (0, 1, 2)]
    return draw, ticks


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    ap.add_argument("out", nargs="?")
    ap.add_argument("--stills")
    a = ap.parse_args()
    spec = json.load(open(a.spec, encoding="utf-8"))

    acc = spec.get("accent", "red")
    if isinstance(acc, dict) and "split" in acc:
        lc, rc = acc["split"]
        bg = make_split_background(col(lc), col(rc))
        ctx = {"accent": lc, "left_color": lc, "right_color": rc}
    else:
        bg = make_background(col(acc))
        ctx = {"accent": acc, "left_color": spec.get("left_color", "blue"),
               "right_color": spec.get("right_color", "pink")}
    ctx.update({"left_name": spec.get("left_name", ""), "right_name": spec.get("right_name", "")})

    work = tempfile.mkdtemp(prefix="fof_")
    offset, t0, paths, cuts, ticks = 0, 0.0, [], [], []
    for i, sc in enumerate(spec["scenes"]):
        dur = max(1.5, round(float(sc.get("dur", 3.5)) * 2) / 2)  # grille de 0,5 s (calée sur le tempo)
        n = int(round(dur * FPS))
        draw, tks = build_scene(sc, ctx, n)
        ticks += [t0 + x for x in tks]
        if i > 0:
            cuts.append(t0)
        if a.stills:
            os.makedirs(a.stills, exist_ok=True)
            render_still(os.path.join(a.stills, f"scene_{i + 1:02d}.jpg"), bg, draw, n - 1, offset)
        else:
            p = os.path.join(work, f"s{i:02d}.mp4")
            render_scene(p, n, bg, draw, offset)
            paths.append(p)
        offset += n
        t0 += dur
    if a.stills:
        print(f"images de contrôle dans {a.stills} (durée totale {t0:.1f} s)")
        return
    if not a.out:
        sys.exit("indiquer un fichier de sortie")
    silent = os.path.join(work, "silent.mp4")
    assemble(paths, silent)
    wav = os.path.join(work, "music.wav")
    wavfile.write(wav, music.SR, music.build(t0, cuts, spec.get("seed", 7), ticks, spec.get("music")))
    tmp = a.out[:-4] + ".part.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", silent, "-i", wav, "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-af", "loudnorm=I=-14:TP=-2:LRA=11,alimiter=limit=0.84:level=false,aresample=44100",
                    "-shortest", "-movflags", "+faststart", tmp], check=True)
    os.replace(tmp, a.out)
    print(f"ok {a.out} ({t0:.1f} s)")


if __name__ == "__main__":
    main()
