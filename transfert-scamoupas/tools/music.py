"""Musiques de fond originales générées en code (libres de droits) pour @scamoupas.

Cinq ambiances légères, en tonalité majeure, pour varier d'une vidéo à l'autre :
  lofi     lo-fi hip-hop détendu (piano électrique, swing, grain vinyle)
  pop      pop lumineuse (arpège de cordes pincées, claps)
  house    house « feel good » (piano sur les contretemps, marimba)
  funk     funk léger (basse groovy, accords staccato)
  marimba  acoustique joyeux (marimba, cordes grattées, shaker)

Le choix se fait avec la clé "music" de la spec ; sans elle, l'ambiance découle de "seed".
Pas d'impacts ni de montées dramatiques : un souffle doux marque les changements de scène,
et les « tic » du compte à rebours sont des petits coups de bois.

  python music.py <durée_s> <cuts séparés par des virgules> <sortie.wav> [graine] [ticks] [ambiance]
"""
import sys
from functools import lru_cache

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

SR = 44100
RNG = np.random.default_rng(7)


# ---------------------------------------------------------------- outils
def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def tt(n):
    return np.arange(n) / SR


def env(n, attack=0.005, decay=0.5, release=0.04, sustain_s=None):
    """Attaque linéaire, décroissance exponentielle, petit relâchement à la fin de la note."""
    t = tt(n)
    e = np.exp(-t / decay)
    a = max(1, int(attack * SR))
    e[:a] *= np.linspace(0, 1, a)
    r = min(n, max(1, int(release * SR)))
    e[-r:] *= np.linspace(1, 0, r)
    return e


def filt(x, kind, f, order=2):
    return sosfilt(butter(order, f, btype=kind, fs=SR, output="sos"), x)


def add(buf, snd, at, gain=1.0):
    i = int(round(at * SR))
    if i >= len(buf) or i + len(snd) <= 0:
        return
    s0 = max(0, -i)
    i = max(0, i)
    j = min(len(buf), i + len(snd) - s0)
    buf[i:j] += snd[s0:s0 + j - i] * gain


# ---------------------------------------------------------------- instruments
@lru_cache(maxsize=512)
def epiano(m, dur, bright=1.0):
    """Piano électrique (FM douce) : fondamentale ronde + petit « ding » de lame."""
    n = int((dur + 0.6) * SR)
    t = tt(n)
    f = hz(m)
    idx = (0.9 * bright) * np.exp(-t / 0.35)
    x = np.sin(2 * np.pi * f * t + idx * np.sin(2 * np.pi * f * t))
    x += 0.12 * bright * np.sin(2 * np.pi * f * 7 * t) * np.exp(-t / 0.05)
    x *= 1 + 0.04 * np.sin(2 * np.pi * 4.5 * t)  # léger trémolo
    e = env(n, 0.004, 1.1, 0.25)
    cut = int(dur * SR)
    if cut < n:  # relâchement doux après la durée de la note
        e[cut:] *= np.exp(-tt(n - cut) / 0.12)
    return x * e * 0.22


@lru_cache(maxsize=512)
def pluck(m, dur, bright=0.5):
    """Corde pincée (Karplus-Strong) : guitare, ukulélé ou clavinet selon la brillance."""
    f = hz(m)
    N = max(2, int(SR / f))
    L = int((dur + 0.4) * SR)
    y = np.zeros(L)
    init = RNG_P.uniform(-1, 1, N)
    init = filt(init, "low", 1500 + 6000 * bright)
    y[:N] = init
    d = 0.996 if bright < 0.7 else 0.992
    for s in range(N, L, N):
        e_ = min(s + N, L)
        a = y[s - N:e_ - N]
        b = y[s - N - 1:e_ - N - 1] if s - N - 1 >= 0 else np.concatenate(([0.0], y[0:e_ - N - 1]))
        y[s:e_] = d * 0.5 * (a + b)
    e = np.ones(L)
    cut = int(dur * SR)
    if cut < L:
        e[cut:] = np.exp(-tt(L - cut) / 0.06)
    return y * e * 0.5


RNG_P = np.random.default_rng(11)


@lru_cache(maxsize=512)
def marimba(m, dur):
    n = int((dur + 0.5) * SR)
    t = tt(n)
    f = hz(m)
    x = np.sin(2 * np.pi * f * t) * np.exp(-t / 0.32)
    x += 0.35 * np.sin(2 * np.pi * f * 3.9 * t) * np.exp(-t / 0.05)
    x += 0.1 * np.sin(2 * np.pi * f * 9.2 * t) * np.exp(-t / 0.015)
    a = int(0.002 * SR)
    x[:a] *= np.linspace(0, 1, a)
    return x * 0.35


@lru_cache(maxsize=256)
def bass(m, dur, kind="soft"):
    n = int((dur + 0.08) * SR)
    t = tt(n)
    f = hz(m)
    if kind == "funk":  # corde pincée : harmoniques qui s'éteignent vite
        x = sum((1 / k) * np.sin(2 * np.pi * f * k * t) * np.exp(-t * (3 + 9 * k)) for k in range(1, 7))
        x += 0.6 * np.sin(2 * np.pi * f * t) * np.exp(-t / 0.4)
    else:  # basse ronde, avec des harmoniques pour rester audible sur un haut-parleur de téléphone
        x = np.sin(2 * np.pi * f * t) + 0.45 * np.sin(2 * np.pi * 2 * f * t) + 0.18 * np.sin(2 * np.pi * 3 * f * t)
    e = env(n, 0.008, 0.9 if kind == "soft" else 0.5, 0.05)
    return filt(x * e, "low", 1200) * 0.55


# ---------------------------------------------------------------- percussions
def kick_soft():
    n = int(0.3 * SR)
    t = tt(n)
    f = 48 + 70 * np.exp(-t / 0.035)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.13)
    click = filt(RNG.uniform(-1, 1, n), "band", [1500, 5000]) * np.exp(-t / 0.004) * 0.25  # attaque audible sur téléphone
    return x * 0.8 + click


def snare(lofi=False):
    n = int(0.25 * SR)
    t = tt(n)
    nz = filt(RNG.uniform(-1, 1, n), "band", [1200, 5500 if not lofi else 3500]) * np.exp(-t / 0.07)
    tone = np.sin(2 * np.pi * 190 * t) * np.exp(-t / 0.035)
    return (nz * 0.7 + tone * 0.35) * 0.8


def clap():
    n = int(0.25 * SR)
    nz = RNG.uniform(-1, 1, n)
    e = np.zeros(n)
    for d in (0, 0.01, 0.02):
        i = int(d * SR)
        e[i:] += np.exp(-tt(n - i) / (0.01 if d < 0.02 else 0.08))
    return filt(nz, "band", [1000, 3500]) * e * 0.55


def hat(open_=False):
    n = int((0.18 if open_ else 0.04) * SR)
    x = filt(RNG.uniform(-1, 1, n), "high", 7500) * np.exp(-tt(n) / (0.06 if open_ else 0.012))
    return x * 0.35


def shaker():
    n = int(0.08 * SR)
    t = tt(n)
    e = np.minimum(t / 0.012, 1) * np.exp(-t / 0.03)
    return filt(RNG.uniform(-1, 1, n), "band", [4500, 11000]) * e * 0.3


def snap():
    n = int(0.12 * SR)
    t = tt(n)
    x = filt(RNG.uniform(-1, 1, n), "band", [1800, 4200]) * np.exp(-t / 0.018)
    return (x + 0.3 * np.sin(2 * np.pi * 1300 * t) * np.exp(-t / 0.01)) * 0.6


def swoosh(dur=0.35):
    n = int(dur * SR)
    t = tt(n)
    e = np.sin(np.pi * t / dur) ** 2
    return filt(RNG.uniform(-1, 1, n), "band", [800, 5000]) * e * 0.35


def woodblock():
    n = int(0.08 * SR)
    t = tt(n)
    x = np.sin(2 * np.pi * 880 * t) + 0.45 * np.sin(2 * np.pi * 2380 * t)
    return x * np.exp(-t / 0.018) * 0.45


def crackle(n):
    x = np.zeros(n)
    k = int(n / SR * 25)
    idx = RNG.integers(0, n, k)
    x[idx] = RNG.uniform(-1, 1, k)
    return filt(x, "low", 3500) * 0.25 + filt(RNG.uniform(-1, 1, n), "band", [2000, 8000]) * 0.004


# ---------------------------------------------------------------- ambiances
# chords : un accord par mesure (notes MIDI) ; roots : basse de chaque mesure
# comp : (pas de double-croche, durée en doubles-croches) des accords ; arp : 16 pas, indice dans l'accord
#   (indice >= taille de l'accord = même note une octave plus haut), None = silence
# bass : (pas, demi-tons au-dessus de la basse, durée) ; drums : pas de chaque percussion
MOODS = {
    "lofi": dict(
        bpm=84, swing=0.18, keys="epiano", bright=0.8, lead="epiano", lead_oct=12, lead_gain=0.5,
        chords=[[53, 57, 60, 64], [52, 55, 59, 62], [50, 53, 57, 60], [48, 52, 55, 59]],
        roots=[41, 40, 38, 36], comp=[(0, 7), (10, 6)],
        arp=[None, None, None, None, None, None, 3, None, None, None, None, None, 2, None, 1, None],
        bass=[(0, 0, 6), (7, 0, 2), (10, 7, 4)], bass_kind="soft",
        kick=[0, 7, 10], snare=[4, 12], hats=[0, 2, 4, 6, 8, 10, 12, 14], hat_gain=0.5, crackle=True),
    "pop": dict(
        bpm=112, swing=0.0, keys="epiano", bright=0.6, lead="pluck", lead_oct=12, lead_gain=0.8,
        chords=[[60, 64, 67], [59, 62, 67], [60, 64, 69], [60, 65, 69]],
        roots=[36, 43, 45, 41], comp=[(0, 16)], keys_gain=0.45,
        arp=[0, 1, 2, 3, 2, 1, 0, 1, 0, 1, 2, 3, 2, 1, 2, 1],
        bass=[(0, 0, 2), (2, 0, 2), (4, 0, 2), (6, 0, 2), (8, 0, 2), (10, 0, 2), (12, 0, 2), (14, 12, 2)],
        bass_kind="soft", kick=[0, 8, 10], clap=[4, 12], hats=[2, 6, 10, 14], shaker=list(range(16)),
        hat_gain=0.7),
    "house": dict(
        bpm=118, swing=0.0, keys="epiano", bright=1.3, lead="marimba", lead_oct=12, lead_gain=0.7,
        chords=[[55, 59, 62, 69], [54, 57, 62, 64], [55, 59, 62, 64], [55, 60, 64, 67]],
        roots=[43, 38, 40, 36], comp=[(2, 2), (6, 2), (10, 2), (14, 2)], keys_gain=0.7,
        arp=[0, None, 2, None, 3, None, 2, None, None, 1, None, 2, None, 3, None, None],
        bass=[(2, 0, 2), (6, 0, 2), (10, 0, 2), (14, 0, 2)], bass_kind="soft",
        kick=[0, 4, 8, 12], kick_gain=0.75, clap=[4, 12], open_hats=[2, 6, 10, 14],
        hats=list(range(16)), hat_gain=0.35),
    "funk": dict(
        bpm=100, swing=0.08, keys="pluck", bright=0.9, lead=None,
        chords=[[56, 59, 62, 66], [56, 59, 62, 66], [55, 59, 61, 64], [55, 59, 61, 64]],
        roots=[40, 40, 45, 45], comp=[(3, 1), (6, 1), (11, 1), (14, 1)], keys_gain=0.9, strum=0.004,
        bass=[(0, 0, 2), (3, 12, 1), (6, 0, 1), (7, 10, 1), (10, 7, 2), (12, 0, 1), (14, 12, 1)],
        bass_kind="funk", kick=[0, 3, 8, 10], snare=[4, 12], ghost=[7, 15], hats=list(range(16)),
        hat_gain=0.45),
    "marimba": dict(
        bpm=100, swing=0.0, keys="pluck", bright=0.45, lead="marimba", lead_oct=12, lead_gain=0.8,
        chords=[[62, 66, 69], [61, 64, 69], [62, 66, 71], [62, 67, 71]],
        roots=[38, 45, 47, 43], comp=[(0, 3), (6, 2), (8, 2), (12, 3)], keys_gain=0.7, strum=0.012,
        arp=[0, None, 1, None, 2, None, 3, None, 2, None, 1, None, 2, None, 0, None],
        bass=[(0, 0, 4), (8, 7, 4)], bass_kind="soft",
        kick=[0, 8], kick_gain=0.7, snap=[4, 12], shaker=list(range(16))),
}
ORDER = ["lofi", "pop", "house", "funk", "marimba"]


def pick(seed, mood=None):
    if mood in MOODS:
        return mood
    return ORDER[int(seed) % len(ORDER)]


def signature(m):
    """Signature sonore du compte : deux notes de marimba qui montent, comme une question (« arnaque… ou pas ? »).
    Même motif sur chaque vidéo, calé sur la tonalité de l'ambiance pour ne jamais sonner faux."""
    base = m["chords"][0][0] + 12
    out = np.zeros(int(1.0 * SR))
    add(out, marimba(base, 0.2), 0.0)
    add(out, marimba(base + 7, 0.5), 0.17, 1.1)
    return out


def build(duration, cuts, seed=7, ticks=(), mood=None, sig=True):
    global RNG
    RNG = np.random.default_rng(seed)
    name = pick(seed, mood)
    m = MOODS[name]
    n = int((duration + 1.0) * SR)
    drums, low, keys, lead, fx = (np.zeros(n) for _ in range(5))
    s16 = 60 / m["bpm"] / 4
    start = cuts[0] if cuts else 0.0
    K, SN, CL, HC, HO, SH, SP = kick_soft(), snare(name == "lofi"), clap(), hat(), hat(True), shaker(), snap()
    keys_fn = {"epiano": lambda x, d: epiano(x, d, m.get("bright", 1.0)),
               "pluck": lambda x, d: pluck(x, d, m.get("bright", 0.5))}[m["keys"]]
    lead_fn = {"epiano": lambda x, d: epiano(x, d, 1.2), "pluck": lambda x, d: pluck(x, d, 0.55),
               "marimba": marimba, None: None}[m.get("lead")]
    step = 0
    while step * s16 < duration:
        bar, s = divmod(step, 16)
        t = step * s16 + (m["swing"] * s16 if s % 2 == 1 else 0.0)
        chord = m["chords"][bar % len(m["chords"])]
        root = m["roots"][bar % len(m["roots"])]
        for st, ln in m["comp"]:
            if s == st:
                for i, note in enumerate(chord):
                    add(keys, keys_fn(note, round(ln * s16, 3)), t + i * m.get("strum", 0.0))
        arp = m.get("arp")
        if lead_fn and arp and arp[s] is not None:
            k = arp[s]
            note = chord[k % len(chord)] + 12 * (k // len(chord)) + m.get("lead_oct", 0)
            add(lead, lead_fn(note, round(1.6 * s16, 3)), t, m.get("lead_gain", 0.6))
        if t >= start - 1e-6:
            for st, off, ln in m["bass"]:
                if s == st:
                    add(low, bass(root + off, round(ln * s16, 3), m["bass_kind"]), t)
            if s in m.get("kick", []):
                add(drums, K, t, m.get("kick_gain", 1.0))
            if s in m.get("snare", []):
                add(drums, SN, t, 0.7)
            if s in m.get("ghost", []):
                add(drums, SN, t, 0.18)
            if s in m.get("clap", []):
                add(drums, CL, t, 0.8)
            if s in m.get("snap", []):
                add(drums, SP, t, 0.7)
            if s in m.get("hats", []):
                add(drums, HC, t, m.get("hat_gain", 0.5) * (1.0 if s % 2 == 0 else 0.6))
            if s in m.get("open_hats", []):
                add(drums, HO, t, 0.45)
            if s in m.get("shaker", []):
                add(drums, SH, t, 0.55 if s % 2 == 0 else 0.35)
        step += 1

    # intro (écran titre) : instruments seuls, adoucis, la rythmique entre au premier changement de scène
    i0 = int(start * SR)
    if i0 > 0:
        keys[:i0] = filt(keys[:i0], "low", 1400) * 0.8
        lead[:i0] = filt(lead[:i0], "low", 1800) * 0.8
    sw = swoosh()
    for c in cuts:
        add(fx, sw, c - 0.2, 0.8)
    wb = woodblock()
    for c in ticks:
        add(fx, wb, c, 1.0)
    if m.get("crackle"):
        drums += crackle(n)
    if sig:  # signature du compte au tout début (écran titre)
        add(fx, signature(m), 0.04, 1.8)

    mix = drums * 0.7 + low * 0.5 + keys * 1.7 * m.get("keys_gain", 0.6) + lead * 1.1 + fx * 0.6
    mix = mix[: int(duration * SR)]
    fade = int(0.8 * SR)
    mix[-fade:] *= np.linspace(1, 0, fade)
    mix = np.tanh(1.05 * mix)
    mix /= np.max(np.abs(mix)) + 1e-9
    mix *= 0.85
    st = np.stack([mix, mix], axis=1)
    return (st * 32767).astype(np.int16)


if __name__ == "__main__":
    dur = float(sys.argv[1])
    cuts = [float(c) for c in sys.argv[2].split(",") if c]
    out = sys.argv[3]
    seed = int(sys.argv[4]) if len(sys.argv) > 4 else 7
    ticks = [float(c) for c in sys.argv[5].split(",") if c] if len(sys.argv) > 5 else []
    mood = sys.argv[6] if len(sys.argv) > 6 else None
    wavfile.write(out, SR, build(dur, cuts, seed, ticks, mood))
    print("ok", out, pick(seed, mood))
