"""Mini-moteur de vidéos verticales 1080x1920 pour @fanoffootball.

Chaque scène = une fonction draw(frame, f) appelée pour chaque image ;
les images sont envoyées brutes à ffmpeg (un fichier .mp4 par scène),
puis les scènes sont assemblées sans ré-encodage.
"""
import math
import os
import subprocess
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
FONT_DIR = "/usr/share/fonts/opentype/inter/"
WEIGHTS = {
    "black": "InterDisplay-Black.otf",
    "xbold": "InterDisplay-ExtraBold.otf",
    "bold": "Inter-Bold.otf",
    "semi": "Inter-SemiBold.otf",
    "med": "Inter-Medium.otf",
}
SAFE_W = 900  # largeur max du texte (évite les bords et la colonne de boutons TikTok)

WHITE = (255, 255, 255)
GREY = (150, 156, 170)
GOLD = (242, 193, 78)


# ---------- easing ----------
def clamp01(x):
    return max(0.0, min(1.0, x))


def prog(f, start, dur):
    return clamp01((f - start) / dur)


def ease_out(x):
    return 1 - (1 - x) ** 3


def ease_back(x):
    c1, c3 = 1.70158, 2.70158
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2


# ---------- fonts / text ----------
@lru_cache(maxsize=512)
def font(weight, size):
    return ImageFont.truetype(FONT_DIR + WEIGHTS[weight], max(8, int(size)))


@lru_cache(maxsize=256)
def fit_size(text, weight, size, max_w=SAFE_W):
    s = size
    while s > 20:
        l, t, r, b = font(weight, s).getbbox(text)
        if r - l <= max_w:
            return s
        s -= 4
    return s


@lru_cache(maxsize=2048)
def text_img(text, weight, size, fill):
    f = font(weight, size)
    l, t, r, b = f.getbbox(text)
    pad = 6
    im = Image.new("RGBA", (r - l + 2 * pad, b - t + 2 * pad), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((pad - l, pad - t), text, font=f, fill=fill + (255,))
    return im


def with_alpha(im, alpha):
    if alpha >= 0.999:
        return im
    im = im.copy()
    a = np.asarray(im.getchannel("A"), dtype=np.float32) * alpha
    im.putalpha(Image.fromarray(a.astype(np.uint8)))
    return im


def put(frame, im, cx, cy, alpha=1.0):
    if alpha <= 0.001:
        return
    x = int(round(cx - im.width / 2))
    y = int(round(cy - im.height / 2))
    # recadre si l'élément dépasse du cadre
    sx, sy = max(0, -x), max(0, -y)
    x, y = max(0, x), max(0, y)
    w = min(im.width - sx, W - x)
    h = min(im.height - sy, H - y)
    if w <= 0 or h <= 0:
        return
    if sx or sy or w != im.width or h != im.height:
        im = im.crop((sx, sy, sx + w, sy + h))
    frame.alpha_composite(with_alpha(im, alpha), (x, y))


def text(frame, s, cx, cy, weight="bold", size=60, fill=WHITE, alpha=1.0, scale=1.0, fit=True):
    base = fit_size(s, weight, size) if fit else size
    put(frame, text_img(s, weight, int(base * scale), fill), cx, cy, alpha)


# ---------- shapes ----------
@lru_cache(maxsize=256)
def rrect_img(w, h, r, fill, alpha):
    im = Image.new("RGBA", (int(w), int(h)), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, int(w) - 1, int(h) - 1), radius=int(r),
                                         fill=fill + (int(255 * alpha),))
    return im


def rrect(frame, cx, cy, w, h, r, fill, alpha=1.0, fade=1.0):
    if w < 2 or h < 2:
        return
    put(frame, rrect_img(int(w), int(h), int(min(r, h / 2, w / 2)), fill, alpha), cx, cy, fade)


def bar_lr(frame, x0, x1, cy, h, fill, fade=1.0):
    """Barre horizontale entre x0 et x1 (dans n'importe quel ordre)."""
    a, b = sorted((x0, x1))
    if b - a < 2:
        return
    rrect(frame, (a + b) / 2, cy, b - a, h, h / 2, fill, 1.0, fade)


# ---------- background ----------
def make_background(accent):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    base = np.array([10, 12, 17], np.float32)
    img = np.broadcast_to(base, (H, W, 3)).copy()
    d = np.sqrt((xx - W * 0.5) ** 2 + (yy - H * 0.40) ** 2) / 1000
    g = np.clip(1 - d, 0, 1) ** 2 * 0.42
    img += g[..., None] * (np.array(accent, np.float32) - base)
    # vignette
    v = np.sqrt(((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H / 2) / (H * 0.7)) ** 2)
    img *= np.clip(1.15 - 0.45 * v, 0.55, 1)[..., None]
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert("RGBA")


def make_split_background(col_l, col_r):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    base = np.array([10, 12, 17], np.float32)
    img = np.broadcast_to(base, (H, W, 3)).copy()
    for cx, col in ((0, col_l), (W, col_r)):
        d = np.sqrt((xx - cx) ** 2 + (yy - H * 0.45) ** 2) / 900
        g = np.clip(1 - d, 0, 1) ** 2 * 0.45
        img += g[..., None] * (np.array(col, np.float32) - base)
    v = np.sqrt(((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H / 2) / (H * 0.7)) ** 2)
    img *= np.clip(1.15 - 0.45 * v, 0.55, 1)[..., None]
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert("RGBA")


def make_stripes():
    """Texture de fines diagonales qui défile lentement (donne du mouvement au fond)."""
    tw = W + 400
    im = Image.new("RGBA", (tw, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for x in range(-H, tw + H, 64):
        d.line([(x, H), (x + H * 0.55, 0)], fill=(255, 255, 255, 9), width=14)
    return im


STRIPES = None


def background_frame(bg, f):
    global STRIPES
    if STRIPES is None:
        STRIPES = make_stripes()
    fr = bg.copy()
    off = int((f * 2) % 128)
    fr.alpha_composite(STRIPES.crop((off, 0, off + W, H)))
    return fr


def brand(frame):
    text(frame, "FAN OF FOOTBALL", W / 2, 250, "bold", 30, (210, 214, 224), alpha=0.85, fit=False)
    bar_lr(frame, W / 2 - 40, W / 2 + 40, 285, 5, GOLD, 0.9)


# ---------- rendering ----------
def render_scene(path, n_frames, bg, draw, global_offset=0):
    tmp = path[:-4] + ".part.mp4"
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p",
           "-r", str(FPS), tmp]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for f in range(n_frames):
        fr = background_frame(bg, f + global_offset)
        brand(fr)
        draw(fr, f)
        p.stdin.write(fr.convert("RGB").tobytes())
    p.stdin.close()
    if p.wait() != 0:
        raise RuntimeError("ffmpeg a échoué pour " + path)
    os.replace(tmp, path)


def render_still(path, bg, draw, f, global_offset=0):
    fr = background_frame(bg, f + global_offset)
    brand(fr)
    draw(fr, f)
    fr.convert("RGB").save(path, quality=92)


def assemble(scene_paths, out_path):
    lst = out_path + ".txt"
    with open(lst, "w") as fh:
        for p in scene_paths:
            fh.write(f"file '{os.path.abspath(p)}'\n")
    joined = out_path[:-4] + ".video.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
                    "-i", lst, "-c", "copy", joined], check=True)
    # piste audio silencieuse (compatibilité des outils d'upload) ; le son se choisit sur TikTok
    tmp = out_path[:-4] + ".part.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", joined,
                    "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
                    "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
                    "-shortest", "-movflags", "+faststart", tmp], check=True)
    os.replace(tmp, out_path)
    os.remove(joined)
    os.remove(lst)
