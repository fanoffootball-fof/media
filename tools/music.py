"""Beat original type « phonk foot » généré en code (libre de droits).

  python music.py <durée_s> <cuts séparés par des virgules> <sortie.wav> [graine]

Les « cuts » sont les instants (en s) des changements de scène : un impact y est
placé, le beat complet démarre au premier cut (le premier passage est l'intro).
"""
import sys

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

SR = 44100
BPM = 120
BEAT = 60 / BPM
S16 = BEAT / 4


def env_exp(n, decay_s):
    t = np.arange(n) / SR
    return np.exp(-t / decay_s)


def bp(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo, hi], btype="band", fs=SR, output="sos"), x)


def hp(x, f, order=2):
    return sosfilt(butter(order, f, btype="high", fs=SR, output="sos"), x)


def lp(x, f, order=2):
    return sosfilt(butter(order, f, btype="low", fs=SR, output="sos"), x)


RNG = np.random.default_rng(7)


def kick():
    n = int(0.45 * SR)
    t = np.arange(n) / SR
    f = 45 + 110 * np.exp(-t / 0.03)
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) * env_exp(n, 0.16)
    x[:200] += np.linspace(0.6, 0, 200) * RNG.uniform(-1, 1, 200)  # attaque
    return np.tanh(1.6 * x)


def bass808(freq, dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = freq * (1 + 1.0 * np.exp(-t / 0.025))  # petite glissade d'attaque
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) * env_exp(n, dur * 0.55)
    x *= np.clip(np.arange(n) / 80, 0, 1)
    return np.tanh(2.2 * x) * 0.8


def clap():
    n = int(0.3 * SR)
    noise = RNG.uniform(-1, 1, n)
    e = np.zeros(n)
    for d in (0, 0.011, 0.022):
        i = int(d * SR)
        e[i:] += env_exp(n - i, 0.012 if d < 0.02 else 0.11)
    x = bp(noise, 900, 3200) * e
    t = np.arange(n) / SR
    x += 0.35 * np.sin(2 * np.pi * 190 * t) * env_exp(n, 0.05)
    return x * 1.4


def hat(open_=False):
    n = int((0.22 if open_ else 0.05) * SR)
    x = hp(RNG.uniform(-1, 1, n), 7000) * env_exp(n, 0.07 if open_ else 0.014)
    return x * 0.5


def cowbell(ratio=1.0, dur=0.28):
    n = int(dur * SR)
    t = np.arange(n) / SR
    sq = np.sign(np.sin(2 * np.pi * 587 * ratio * t)) + np.sign(np.sin(2 * np.pi * 845 * ratio * t))
    x = bp(sq, 600 * ratio, 2600 * ratio) * (0.25 * env_exp(n, 0.012) + 0.75 * env_exp(n, 0.09))
    return np.tanh(1.5 * x) * 0.5


def impact():
    n = int(1.6 * SR)
    t = np.arange(n) / SR
    boom = np.sin(2 * np.pi * (38 + 40 * np.exp(-t / 0.08)) * t) * env_exp(n, 0.45)
    crash = lp(hp(RNG.uniform(-1, 1, n), 2500), 11000) * env_exp(n, 0.5) * 0.35
    return np.tanh(1.3 * (boom + crash))


def riser(dur):
    n = int(dur * SR)
    ramp = np.linspace(0, 1, n)
    noise = hp(RNG.uniform(-1, 1, n), 2500) * ramp ** 3 * 0.45
    f = 180 + 900 * ramp ** 2  # balayage montant
    saw = 2 * ((np.cumsum(f) / SR) % 1.0) - 1
    sweep = lp(saw, 3000) * ramp ** 2 * 0.25
    return noise + sweep


def tick():
    n = int(0.06 * SR)
    t = np.arange(n) / SR
    x = (np.sin(2 * np.pi * 1900 * t) + 0.5 * np.sin(2 * np.pi * 3100 * t)) * env_exp(n, 0.012)
    return x * 0.7


def add(buf, snd, at, gain=1.0):
    i = int(at * SR)
    if i >= len(buf):
        return
    j = min(len(buf), i + len(snd))
    buf[i:j] += snd[: j - i] * gain


# mélodie de cloche (demi-tons) sur 2 mesures en doubles-croches, None = silence
BELL = [0, None, 0, None, 3, None, 0, None, 7, None, 5, None, 3, None, 0, None,
        0, None, 0, None, 3, None, 5, None, 3, None, 0, None, -2, None, 0, None]
# basse 808 : (pas de double-croche, demi-tons, durée en doubles-croches)
BASS = [(0, 0, 6), (6, 0, 4), (10, 3, 6), (16, 0, 6), (22, -2, 4), (26, -4, 6)]
ROOT = 41.2  # mi grave (E1)


def build(duration, cuts, seed=7, ticks=()):
    global RNG
    RNG = np.random.default_rng(seed)
    n = int((duration + 0.5) * SR)
    drums = np.zeros(n)
    bass = np.zeros(n)
    bells = np.zeros(n)
    fx = np.zeros(n)
    start = cuts[0] if cuts else 0.0
    K, C = kick(), clap()
    HC, HO = hat(), hat(True)
    bell_cache = {}

    # intro : cloche seule filtrée + montée vers le premier cut
    add(fx, impact(), 0.0, 0.9)
    if start > 0.6:
        add(fx, riser(start), 0.0, 0.8)
    t = 0.0
    step = 0
    while t < duration:
        s = step % 32
        bar_step = step % 16
        semis = BELL[s]
        if semis is not None:
            key = semis
            if key not in bell_cache:
                bell_cache[key] = cowbell(2 ** (key / 12))
            add(bells, bell_cache[key], t, 0.55 if t >= start else 0.3)
        if t >= start:
            if bar_step in (0, 7, 10):
                add(drums, K, t, 1.0)
            if bar_step in (4, 12):
                add(drums, C, t, 0.7)
            add(drums, HO if bar_step == 14 else HC, t, 0.55 if bar_step % 2 == 0 else 0.3)
            if bar_step == 15 and (step // 16) % 2 == 1:  # petit roulement de charleston
                add(drums, HC, t + S16 / 2, 0.3)
            for st, semi, ln in BASS:
                if s == st:
                    add(bass, bass808(ROOT * 2 ** (semi / 12), ln * S16), t, 1.0)
        t += S16
        step += 1

    for c in cuts:
        add(fx, impact(), c, 0.85)
    tk = tick()
    for c in ticks:
        add(fx, tk, c, 1.0)

    # l'intro cloche est filtrée (effet « téléphone ») pour que le drop claque
    i0 = int(start * SR)
    if i0 > 0:
        bells[:i0] = bp(bells[:i0], 700, 2200)

    mix = drums * 0.9 + bass * 0.85 + bells * 0.6 + fx * 0.7
    mix = mix[: int(duration * SR)]
    fade = int(0.6 * SR)
    mix[-fade:] *= np.linspace(1, 0, fade)
    mix = np.tanh(1.2 * mix)
    mix /= np.max(np.abs(mix)) + 1e-9
    mix *= 0.89
    st = np.stack([mix, mix], axis=1)
    return (st * 32767).astype(np.int16)


if __name__ == "__main__":
    dur = float(sys.argv[1])
    cuts = [float(c) for c in sys.argv[2].split(",") if c]
    out = sys.argv[3]
    seed = int(sys.argv[4]) if len(sys.argv) > 4 else 7
    ticks = [float(c) for c in sys.argv[5].split(",") if c] if len(sys.argv) > 5 else []
    wavfile.write(out, SR, build(dur, cuts, seed, ticks))
    print("ok", out)
