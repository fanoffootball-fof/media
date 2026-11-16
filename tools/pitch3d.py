"""Scène « pitch3d » : but refait en 3D stylisée (stade, mannequins, ballon avec sa hauteur réelle).

Le rendu 3D est fait par tools/render3d/scene.js (three.js, fourni dans tools/vendor/three)
dans Chrome sans écran, piloté par Playwright ; une image est rendue par image de la vidéo.
Les textes (en-tête, étiquettes, légendes, « BUT ! ») sont dessinés ici par-dessus.
Mêmes champs que la scène « pitch » (voir tools/SPEC.md), plus `camera`.
"""
import atexit
import base64
import io
import json
import math
import os
import shutil

import numpy as np
from PIL import Image

from engine import FPS, GOLD, H, W, WHITE, brand, ease_back, ease_out, fit_size, font, prog, rrect, text

HERE = os.path.dirname(os.path.abspath(__file__))
ORIGIN = "http://fof.local/"
CAP_Y = 1300
QUERY = os.environ.get("FOF3D_QUERY", "q=1&aa=1")

_pw = _browser = _page = None
_current = None
LAST_MS = [0, 0]


def _chrome():
    for name in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser"):
        p = shutil.which(name)
        if p:
            return p
    return None


def _serve(route):
    rel = route.request.url[len(ORIGIN):].split("?")[0]
    full = os.path.normpath(os.path.join(HERE, rel))
    if not full.startswith(HERE + os.sep) or not os.path.isfile(full):
        route.fulfill(status=404, body="")
        return
    ctype = "text/html" if full.endswith(".html") else "text/javascript"
    with open(full, "rb") as fh:
        route.fulfill(status=200, body=fh.read(), headers={"Content-Type": ctype})


def _page_get():
    global _pw, _browser, _page
    if _page is None:
        from playwright.sync_api import sync_playwright
        _pw = sync_playwright().start()
        kw = {"args": ["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"]}
        exe = _chrome()
        if exe:
            kw["executable_path"] = exe
        _browser = _pw.chromium.launch(**kw)
        _page = _browser.new_page(viewport={"width": W, "height": H})
        _page.route(ORIGIN + "**", _serve)
        _page.goto(ORIGIN + "render3d/index.html?" + QUERY)
        _page.wait_for_function("window.fof !== undefined", timeout=120000)
        atexit.register(close)
    return _page


def close():
    global _pw, _browser, _page, _current
    try:
        if _browser:
            _browser.close()
        if _pw:
            _pw.stop()
    except Exception:
        pass
    _pw = _browser = _page = _current = None


def render(spec_js, t):
    """Rend l'instant t (s) : renvoie (image RGB 1080x1920, étiquettes [{x, y, text, star}])."""
    global _current
    page = _page_get()
    key = json.dumps(spec_js, sort_keys=True)
    if key != _current:
        page.evaluate("s => window.fof.init(s)", spec_js)
        _current = key
    r = page.evaluate("t => window.fof.renderAt(t)", float(t))
    img = Image.open(io.BytesIO(base64.b64decode(r["img"].split(",", 1)[1]))).convert("RGB")
    if img.size != (W, H):
        img = img.resize((W, H), Image.LANCZOS)
    LAST_MS[:] = r.get("ms", [0, 0])
    return img, r["labels"]


def _shade():
    """Assombrit le haut (en-tête) et le bas (légende) pour la lisibilité des textes."""
    a = np.zeros(H, np.float32)
    top = np.linspace(0.62, 0.0, 560)
    a[:560] = top
    a[1120:1500] = np.linspace(0.0, 0.78, 380)
    a[1500:] = 0.78
    arr = np.zeros((H, W, 4), np.uint8)
    arr[..., :3] = (6, 8, 14)
    arr[..., 3] = (a * 255).astype(np.uint8)[:, None]
    return Image.fromarray(arr, "RGBA")


SHADE = None


class View3D:
    """Élément de scène : même interface que les éléments de make_video (y, start, h, gap, draw)."""
    h, gap = 0, 0

    def __init__(self, sc, att_color):
        self.y = 0
        self.start = -100          # pas d'animation d'entrée : la 3D est là dès la 1re image
        self.speed = float(sc.get("speed", 1.0))
        self.t0 = float(sc.get("t0", 0.0))
        self.goal_t = sc.get("goal_t")
        self.captions = sorted((float(c[0]), c[1]) for c in sc.get("captions", []))
        self.js = {"players": sc.get("players", []), "ball": sc.get("ball"), "goal_t": self.goal_t,
                   "camera": sc.get("camera", {}), "att_color": list(att_color)}
        if sc.get("def_color"):
            self.js["def_color"] = list(sc["def_color"])

    def hits(self):
        if self.goal_t is None or self.goal_t < self.t0:
            return []
        return [(self.goal_t - self.t0) / self.speed]

    def draw(self, fr, f, cy):
        global SHADE
        if SHADE is None:
            SHADE = _shade()
        t = self.t0 + f / FPS * self.speed
        img, labels = render(self.js, t)
        fr.paste(img.convert("RGBA"), (0, 0))
        fr.alpha_composite(SHADE)
        brand(fr)
        for lb in labels:
            if not (60 < lb["x"] < W - 60 and 575 < lb["y"] < 1200):
                continue
            sz = 30 if lb["star"] else 26
            l, _, r, _ = font("bold", sz).getbbox(lb["text"])
            rrect(fr, lb["x"], lb["y"] - 10, r - l + 26, sz + 18, (sz + 18) / 2, (10, 12, 18), 0.75, 1.0)
            text(fr, lb["text"], lb["x"], lb["y"] - 10, "bold", sz, GOLD if lb["star"] else WHITE, fit=False)
        if self.goal_t is not None and t >= self.goal_t:   # « BUT ! » prend la place de la légende
            k = (t - self.goal_t) / self.speed
            rrect(fr, W / 2, H / 2, W, H, 0, WHITE, 0.35 * math.exp(-7 * k), 1.0)
            pop = ease_back(min(1.0, k * FPS / 9))
            text(fr, "BUT !", W / 2 + 5, CAP_Y + 6, "black", 160, (0, 0, 0), alpha=0.5, scale=pop, fit=False)
            text(fr, "BUT !", W / 2, CAP_Y, "black", 160, GOLD, scale=pop, fit=False)
            return
        cap = None
        for ct, s in self.captions:
            if t >= ct:
                cap = (ct, s)
        if cap:
            ca = ease_out(min(1.0, (t - cap[0]) / self.speed * FPS / 6))
            sz = fit_size(cap[1], "xbold", 58, 900)
            text(fr, cap[1], W / 2, CAP_Y + (1 - ca) * 20, "xbold", sz, WHITE, alpha=ca, fit=False)
