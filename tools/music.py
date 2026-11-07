"""Musiques de fond originales générées en code (libres de droits) pour @fanoffootball.

Ambiances sport / foot, toutes à 120 BPM pour que les changements de scène
(durées sur une grille de 0,5 s) tombent sur le temps :

  stade    hymne de stade : grosses frappes 3-3-2, claps, cuivres, rumeur de foule
  samba    batucada brésilienne : sifflet, surdo, caixa, tamborim, agogô, cavaquinho
  epique   bande-annonce de match : tambours graves, ostinato de cordes, « braam »
  electro  hymne électro de résumé de match : kick 4 temps, basse, accords qui pompent
  phonk    ancien beat (cloche + 808), hors rotation

La spec choisit l'ambiance avec "music" ; sans ce champ, elle découle de "seed".

  python music.py <durée_s> <cuts séparés par des virgules> <sortie.wav> [graine] [ticks] [style]

Les « cuts » sont les instants (en s) des changements de scène : un impact y est
placé, le morceau complet démarre au premier cut (avant : intro qui monte).
"""
import sys

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, fftconvolve, sosfilt

SR = 44100
BPM = 120
BEAT = 60 / BPM
S16 = BEAT / 4

ROTATION = ["stade", "samba", "epique", "electro"]
STYLES = ROTATION + ["phonk"]

RNG = np.random.default_rng(7)


# ---------------------------------------------------------------- outils

def env_exp(n, decay_s):
    t = np.arange(n) / SR
    return np.exp(-t / decay_s)


def bp(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo, hi], btype="band", fs=SR, output="sos"), x)


def hp(x, f, order=2):
    return sosfilt(butter(order, f, btype="high", fs=SR, output="sos"), x)


def lp(x, f, order=2):
    return sosfilt(butter(order, f, btype="low", fs=SR, output="sos"), x)


def noise(n):
    return RNG.uniform(-1, 1, n)


def midi(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def ramp_env(n, attack, release):
    e = np.ones(n)
    a = min(n, max(1, int(attack * SR)))
    e[:a] = np.linspace(0, 1, a)
    r = min(n - a, max(1, int(release * SR)))
    if r > 0:
        e[n - r:] *= np.linspace(1, 0, r)
    return e


def smooth_random(n, rate, lo, hi):
    k = max(2, int(n / SR * rate) + 2)
    pts = RNG.uniform(lo, hi, k)
    return np.interp(np.linspace(0, k - 1, n), np.arange(k), pts)


def add(buf, snd, at, gain=1.0):
    i = int(round(at * SR))
    if i >= len(buf) or i < 0:
        return
    j = min(len(buf), i + len(snd))
    buf[i:j] += snd[: j - i] * gain


def reverb(x, rt=1.2, wet=0.3, lo=250, hi=5000):
    n = int(rt * SR)
    t = np.arange(n) / SR
    ir = bp(noise(n), lo, hi) * np.exp(-6.9 * t / rt)
    ir /= np.sqrt(np.sum(ir ** 2)) + 1e-9
    return x + wet * fftconvolve(x, ir)[: len(x)]


def bl_saw(f, n, fmax=4000.0, detune=0.0):
    """Dent de scie sans repliement (somme d'harmoniques jusqu'à fmax)."""
    t = np.arange(n) / SR
    f = f * 2 ** (detune / 1200)
    ph = RNG.uniform(0, 2 * np.pi)
    k_max = max(1, int(fmax // f))
    out = np.zeros(n)
    for k in range(1, k_max + 1):
        w = 1.0 / k
        if k > 0.7 * k_max:  # coupure adoucie
            w *= (k_max - k + 1) / (0.3 * k_max + 1)
        out += w * np.sin(2 * np.pi * k * f * t + k * ph)
    return out * 0.55


def echo(x, delay_s, fb=0.35, taps=3):
    out = x.copy()
    d = int(delay_s * SR)
    g = fb
    for k in range(1, taps + 1):
        if k * d >= len(x):
            break
        out[k * d:] += x[: len(x) - k * d] * g
        g *= fb
    return out


# ---------------------------------------------------------------- sons communs

def kick():
    n = int(0.45 * SR)
    t = np.arange(n) / SR
    f = 45 + 110 * np.exp(-t / 0.03)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * env_exp(n, 0.16)
    x[:200] += np.linspace(0.6, 0, 200) * RNG.uniform(-1, 1, 200)  # attaque
    return np.tanh(1.6 * x)


def kick_house():
    n = int(0.4 * SR)
    t = np.arange(n) / SR
    f = 50 + 140 * np.exp(-t / 0.035)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * env_exp(n, 0.2)
    x[:150] += np.linspace(0.5, 0, 150) * RNG.uniform(-1, 1, 150)
    return np.tanh(1.8 * x)


def clap():
    n = int(0.3 * SR)
    e = np.zeros(n)
    for d in (0, 0.011, 0.022):
        i = int(d * SR)
        e[i:] += env_exp(n - i, 0.012 if d < 0.02 else 0.11)
    x = bp(noise(n), 900, 3200) * e
    t = np.arange(n) / SR
    x += 0.35 * np.sin(2 * np.pi * 190 * t) * env_exp(n, 0.05)
    return x * 1.4


def hat(open_=False):
    n = int((0.22 if open_ else 0.05) * SR)
    return hp(noise(n), 7000) * env_exp(n, 0.07 if open_ else 0.014) * 0.5


def snare(tone=190, decay=0.13):
    n = int(0.4 * SR)
    t = np.arange(n) / SR
    body = np.sin(2 * np.pi * tone * t) * env_exp(n, 0.04)
    wires = bp(noise(n), 1500, 8000) * env_exp(n, decay)
    return np.tanh(1.4 * (0.6 * body + wires))


def stomp():
    n = int(0.5 * SR)
    t = np.arange(n) / SR
    f = 48 + 90 * np.exp(-t / 0.025)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * env_exp(n, 0.15)
    thud = lp(noise(n), 700) * env_exp(n, 0.025)
    return np.tanh(1.8 * (body + 0.9 * thud))


def tom(freq, decay=0.22):
    n = int(0.6 * SR)
    t = np.arange(n) / SR
    f = freq * (1 + 0.6 * np.exp(-t / 0.03))
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * env_exp(n, decay)
    stick = bp(noise(n), 1500, 6000) * env_exp(n, 0.006) * 0.5
    return np.tanh(1.5 * (body + stick))


def taiko(freq=52):
    n = int(1.2 * SR)
    t = np.arange(n) / SR
    f = freq * (1 + 0.9 * np.exp(-t / 0.02))
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * env_exp(n, 0.35)
    skin = lp(noise(n), 1200) * env_exp(n, 0.04) * 0.7
    return np.tanh(2.0 * (body + skin))


def impact():
    n = int(1.6 * SR)
    t = np.arange(n) / SR
    boom = np.sin(2 * np.pi * (38 + 40 * np.exp(-t / 0.08)) * t) * env_exp(n, 0.45)
    crash = lp(hp(noise(n), 2500), 11000) * env_exp(n, 0.5) * 0.35
    return np.tanh(1.3 * (boom + crash))


def riser(dur):
    n = int(dur * SR)
    ramp = np.linspace(0, 1, n)
    nz = hp(noise(n), 2500) * ramp ** 3 * 0.45
    f = 180 + 900 * ramp ** 2  # balayage montant
    saw = 2 * ((np.cumsum(f) / SR) % 1.0) - 1
    return nz + lp(saw, 3000) * ramp ** 2 * 0.25


def tick():
    n = int(0.06 * SR)
    t = np.arange(n) / SR
    return (np.sin(2 * np.pi * 1900 * t) + 0.5 * np.sin(2 * np.pi * 3100 * t)) * env_exp(n, 0.012) * 0.7


def whistle(dur, trill=True):
    """Sifflet d'arbitre (bille qui roule = trille vers 26 Hz)."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = 2900 + 25 * np.sin(2 * np.pi * 5 * t)
    am = np.ones(n)
    if trill:
        f = f + 90 * np.sin(2 * np.pi * 26 * t)
        am = 0.65 + 0.35 * np.sin(2 * np.pi * 26 * t)
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR)
    breath = bp(noise(n), 2500, 3400) * 0.3
    return (tone * am + breath) * ramp_env(n, 0.012, 0.04) * 0.45


def crowd(n, swells=(), level=1.0):
    """Rumeur de stade : bandes de bruit à modulation lente + brouhaha, pics aux temps forts."""
    out = np.zeros(n)
    for lo, hi, g in ((180, 700, 0.8), (500, 1600, 1.0), (1400, 3800, 0.4)):
        band = bp(noise(n), lo, hi)
        out += g * band * smooth_random(n, 0.8, 0.6, 1.0) * smooth_random(n, 7.0, 0.7, 1.0)
    out /= np.sqrt(np.mean(out ** 2)) + 1e-9
    env = np.full(n, 0.55)
    t = np.arange(n) / SR
    for s in swells:  # « ooooh » de la foule
        rel = t - s
        env += np.where(rel < 0, np.exp(rel / 0.25) * 0.15, 0.6 * np.exp(-rel / 1.4)) * (rel > -1.0)
    return out * env * level


def brass(freqs, dur, bright=3200.0):
    """Accord de cuivres synthétiques : attaque cuivrée qui s'éclaircit."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    dark = sum(bl_saw(f, n, 900, d) for f in freqs for d in (-6, 6))
    lit = sum(bl_saw(f, n, bright, d) for f in freqs for d in (-6, 6))
    b = np.clip(t / 0.08, 0, 1) * (0.55 + 0.45 * np.exp(-t / 0.35))
    x = (dark * (1 - b) + lit * b) * (1 - np.exp(-t / 0.05))
    x *= ramp_env(n, 0.005, min(0.12, dur * 0.3))
    return np.tanh(1.3 * x / (2 * len(freqs)))


def pad(freqs, dur, fmax=1800.0, attack=0.4, voices=(-9, 0, 9)):
    n = int(dur * SR)
    x = sum(bl_saw(f, n, fmax, d) for f in freqs for d in voices)
    return x / (len(voices) * len(freqs)) * ramp_env(n, attack, 0.25)


def pluck(freq, dur, decay=0.993):
    """Corde pincée (Karplus-Strong), calcul par blocs d'une période."""
    n = int(dur * SR)
    p = max(2, int(round(SR / freq)))
    y = np.zeros(n + p + 1)
    y[1:p + 1] = lp(noise(p), 6000)
    i = p + 1
    while i < len(y):
        j = min(i + p, len(y))
        y[i:j] = decay * 0.5 * (y[i - p:j - p] + y[i - p - 1:j - p - 1])
        i = j
    return y[1:n + 1] * ramp_env(n, 0.001, 0.03)


# ---------------------------------------------------------------- grille

def grid(duration, start):
    """(t, p, mesure) pour chaque double-croche, calé sur le premier cut."""
    s0 = int(round(start / S16))
    for step in range(int(duration / S16) + 1):
        rel = step - s0
        yield step * S16, rel % 16, rel // 16


# ---------------------------------------------------------------- stade

STADE_PROG = [(40, [52, 55, 59]), (36, [48, 52, 55]), (43, [50, 55, 59]), (38, [50, 54, 57])]  # Mi m, Do, Sol, Ré
STADE_MELODY = [
    [(0, 71, 6), (6, 71, 2), (8, 74, 4), (12, 71, 4)],
    [(0, 72, 6), (6, 71, 2), (8, 67, 8)],
    [(0, 74, 6), (6, 74, 2), (8, 79, 4), (12, 78, 4)],
    [(0, 78, 6), (6, 76, 2), (8, 74, 8)],
]


def style_stade(n, duration, start, cuts):
    drums, bass, horns, lead = (np.zeros(n) for _ in range(4))
    ST, C, SN, H = stomp(), clap(), snare(200, 0.16), hat()
    TOMS = [tom(f) for f in (165, 135, 112, 92)]
    cache = {}

    def get(key, fn):
        if key not in cache:
            cache[key] = fn()
        return cache[key]

    for t, p, bar in grid(duration, start):
        if t < start:  # avant le coup d'envoi : frappes de pieds sur le temps + claps
            if p % 4 == 0:
                add(drums, ST, t, 0.45)
            if start - t <= 4 * S16 + 1e-6 and p % 2 == 0:
                add(drums, C, t, 0.5)
            continue
        root, chord = STADE_PROG[bar % 4]
        ci = bar % 4
        if p in (0, 6, 12):
            add(drums, ST, t, 1.0)
        if p in (4, 12):
            add(drums, C, t, 0.8)
            add(drums, SN, t, 0.5)
        if p % 2 == 0:
            add(drums, H, t, 0.35 if p % 4 == 2 else 0.2)
        if bar % 4 == 3 and p >= 12:
            add(drums, TOMS[p - 12], t, 0.75)
        if p % 2 == 0:
            add(bass, get(("b", root), lambda: bl_saw(midi(root), int(0.22 * SR), 700) * ramp_env(int(0.22 * SR), 0.004, 0.05)), t)
        for st, ln in ((0, 6), (6, 6), (12, 4)):
            if p == st:
                add(horns, get(("h", ci, ln), lambda: brass([midi(m) for m in chord], ln * S16 * 0.92)), t)
        for st, m, ln in STADE_MELODY[ci]:
            if p == st:
                add(lead, get(("l", m, ln), lambda: brass([midi(m)], ln * S16 * 0.95, 4500)), t)

    drums = reverb(drums, 1.3, 0.22)
    horns = reverb(horns, 1.6, 0.3)
    lead = reverb(lead, 1.6, 0.3)
    i0 = int(start * SR)
    fx = np.zeros(n)
    if start > 0.6:
        add(fx, riser(start), 0.0, 0.6)
    fans = crowd(n, swells=cuts, level=1.0)
    fans[:i0] *= 1.6  # ambiance d'avant-match
    return drums * 0.95 + bass * 0.55 + horns * 0.55 + lead * 0.38 + fans * 0.12 + fx * 0.6


# ---------------------------------------------------------------- samba

SAMBA_PROG = [(45, [69, 73, 76, 81]), (42, [66, 69, 73, 78]), (38, [66, 69, 74, 78]), (40, [68, 71, 76, 80])]  # La, Fa# m, Ré, Mi
CAIXA_ACC = [1.0, 0.4, 0.55, 0.85, 0.7, 0.4, 0.55, 0.9]
TAMB = {0, 2, 5, 7, 9, 11, 13, 14}
AGOGO = {0: True, 2: True, 3: False, 6: True, 8: False, 10: False, 11: True, 14: False}
SHAKE = [0.5, 0.9, 0.6, 1.0]
CAVACO = {0: "d", 2: "u", 3: "d", 5: "u", 6: "d"}
SAMBA_BASS = [(0, 0, 3), (3, 7, 1), (4, 0, 2), (6, 12, 2)]


def strum(notes, dur, down=True):
    n = int(dur * SR)
    x = np.zeros(n)
    order = notes if down else notes[::-1]
    for k, m in enumerate(order):
        add(x, pluck(midi(m), dur), k * 0.007, 0.8 if down else 0.6)
    return x / len(notes)


def style_samba(n, duration, start, cuts):
    perc, surdos, cav, bass, fx = (np.zeros(n) for _ in range(5))
    S_HI, S_LO, S_MUTE, S_CUT = (surdo(68), surdo(55), surdo(68, False), surdo(88, False))
    CX, TB, SH = caixa(), tamborim(), shaker()
    AG = {True: agogo(True), False: agogo(False)}
    cache = {}

    def get(key, fn):
        if key not in cache:
            cache[key] = fn()
        return cache[key]

    # chamada : sifflet de départ puis roulement de caixa qui monte
    if start > 1.2:
        add(fx, whistle(0.12, False), 0.05)
        add(fx, whistle(0.12, False), 0.30)
        add(fx, whistle(0.45), 0.55)
    for t, p, bar in grid(duration, start):
        p8 = p % 8
        if t < start:
            if start - t <= 1.0 + 1e-6:
                k = 1 - (start - t) / 1.0
                add(perc, CX, t, 0.25 + 0.6 * k)
            continue
        root, chord = SAMBA_PROG[bar % 4]
        ci = bar % 4
        if p8 == 0:
            add(surdos, S_HI, t, 0.8)
        if p8 == 4:
            add(surdos, S_LO, t, 1.0)
        if p8 == 3:
            add(surdos, S_MUTE, t, 0.45)
        if p8 in (2, 6, 7):
            add(surdos, S_CUT, t, 0.35)
        add(perc, CX, t, 0.55 * CAIXA_ACC[p8])
        if p in TAMB:
            add(perc, TB, t, 0.7)
        if p in AGOGO:
            add(perc, AG[AGOGO[p]], t, 0.6)
        add(perc, SH, t, 0.35 * SHAKE[p % 4])
        if p8 in CAVACO:
            d = CAVACO[p8] == "d"
            add(cav, get(("c", ci, d), lambda: strum(chord, 0.3, d)), t, 1.0 if p8 in (3, 6) else 0.8)
        for st, semi, ln in SAMBA_BASS:
            if p8 == st:
                f = midi(root + semi)
                add(bass, get(("b", root, semi, ln), lambda: (bl_saw(f, int(ln * S16 * SR), 450) + 0.6 * np.sin(2 * np.pi * f * np.arange(int(ln * S16 * SR)) / SR)) * ramp_env(int(ln * S16 * SR), 0.004, 0.04)), t)

    if len(cuts) > 1:  # coup de sifflet avant la dernière scène
        add(fx, whistle(0.1, False), cuts[-1] - 0.25)
        add(fx, whistle(0.25), cuts[-1] - 0.05)
    perc = reverb(perc, 0.9, 0.15)
    cav = reverb(cav, 1.0, 0.2)
    fans = crowd(n, swells=cuts[1:], level=1.0)
    return surdos * 0.6 + perc * 0.95 + cav * 1.7 + bass * 0.35 + fx * 0.8 + fans * 0.09


def surdo(freq=58, open_=True):
    n = int(0.9 * SR)
    t = np.arange(n) / SR
    f = freq * (1 + 0.25 * np.exp(-t / 0.04))
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * env_exp(n, 0.45 if open_ else 0.08)
    skin = lp(noise(n), 900) * env_exp(n, 0.015) * 0.5
    return np.tanh(1.6 * (body + skin))


def caixa():
    n = int(0.12 * SR)
    t = np.arange(n) / SR
    wires = bp(noise(n), 2500, 9000) * env_exp(n, 0.035)
    body = np.sin(2 * np.pi * 340 * t) * env_exp(n, 0.012) * 0.5
    return (wires + body) * 0.8


def tamborim():
    n = int(0.08 * SR)
    t = np.arange(n) / SR
    return (np.sin(2 * np.pi * 780 * t) * env_exp(n, 0.02) + bp(noise(n), 2000, 6000) * env_exp(n, 0.008) * 0.8) * 0.7


def agogo(high=True):
    f = 1250 if high else 940
    n = int(0.25 * SR)
    t = np.arange(n) / SR
    x = sum(a * np.sin(2 * np.pi * f * r * t) for r, a in ((1, 1.0), (2.4, 0.45), (3.9, 0.2)))
    return x * (0.3 * env_exp(n, 0.008) + 0.7 * env_exp(n, 0.12)) * 0.35


def shaker():
    n = int(0.05 * SR)
    return hp(noise(n), 5000) * np.sin(np.linspace(0, np.pi, n)) ** 2 * 0.5


# ---------------------------------------------------------------- épique

EPIC_PROG = [(38, 50, [50, 53, 57]), (34, 46, [50, 53, 58]), (41, 53, [48, 53, 57]), (36, 48, [48, 52, 55])]  # Ré m, Si b, Fa, Do
OSTINATO = [0, 0, 12, 0, 7, 0, 12, 7]


def style_epique(n, duration, start, cuts):
    drums, strings, pads, braams = (np.zeros(n) for _ in range(4))
    BIG, MID = taiko(50), taiko(78)
    TOMS = [tom(115, 0.3), tom(95, 0.3)]
    cache = {}

    def get(key, fn):
        if key not in cache:
            cache[key] = fn()
        return cache[key]

    for t, p, bar in grid(duration, start):
        root_b, root_o, chord = EPIC_PROG[max(bar, 0) % 4]
        ci = max(bar, 0) % 4
        m = root_o + OSTINATO[p % 8]
        g = (0.9 if p % 4 == 0 else 0.6)
        if t < start:
            k = 0.25 + 0.5 * (t / max(start, 1e-6))
            add(strings, get(("s", m), lambda: string_stab(midi(m), 0.11)), t, g * k)
            if p % 4 == 0:
                add(drums, BIG, t, 0.35 + 0.4 * t / max(start, 1e-6))
            continue
        add(strings, get(("s", m), lambda: string_stab(midi(m), 0.11)), t, g)
        add(strings, get(("s", m + 12), lambda: string_stab(midi(m + 12), 0.11)), t, g * 0.45)
        if p in (0, 3, 6, 10):
            add(drums, BIG, t, 1.0)
        if p in (8, 12):
            add(drums, MID, t, 0.8)
        if bar % 2 == 1 and p in (14, 15):
            add(drums, TOMS[p - 14], t, 0.7)
        if p == 0:
            add(pads, get(("p", ci), lambda: pad([midi(x) for x in chord], 16 * S16 + 0.3, 1500, 0.3)), t)
            if bar % 4 == 0:
                add(braams, get(("br", root_b), lambda: braam(midi(root_b))), t)

    strings = reverb(strings, 1.4, 0.3)
    drums = reverb(drums, 1.8, 0.3, 80, 3000)
    i0 = int(start * SR)
    if i0 > 0:
        strings[:i0] = lp(strings[:i0], 1200)
    fx = np.zeros(n)
    if start > 0.6:
        add(fx, riser(start), 0.0, 0.6)
    fans = crowd(n, swells=cuts, level=1.0)
    return drums * 0.75 + strings * 1.1 + pads * 0.4 + braams * 0.5 + fx * 0.6 + fans * 0.06


def string_stab(freq, dur):
    n = int(dur * SR)
    return (bl_saw(freq, n, 4500, -5) + bl_saw(freq, n, 4500, 5)) * ramp_env(n, 0.006, dur * 0.5) * 0.5


def braam(freq, dur=2.2):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = sum(bl_saw(freq * r, n, 1400, d) for r in (1, 1.5, 2) for d in (-8, 8))
    x = np.tanh(1.8 * x / 4) * (1 - np.exp(-t / 0.04)) * np.exp(-t / 1.1)
    return x * ramp_env(n, 0.01, 0.3)


# ---------------------------------------------------------------- électro

ELECTRO_PROG = [(45, [57, 60, 64, 69]), (41, [57, 60, 65, 69]), (48, [55, 60, 64, 67]), (43, [55, 59, 62, 67])]  # La m, Fa, Do, Sol
ARP_STEPS = {0: 0, 2: 1, 3: 2, 5: 3, 6: 2, 8: 1, 10: 2, 11: 3, 13: 2, 14: 1}


def style_electro(n, duration, start, cuts):
    drums, bass, chords, lead, fx = (np.zeros(n) for _ in range(5))
    K, C, HC, HO = kick_house(), clap(), hat(), hat(True)
    cache = {}

    def get(key, fn):
        if key not in cache:
            cache[key] = fn()
        return cache[key]

    pump = np.ones(n)
    t_all = np.arange(n) / SR
    voices = (-15, -7, 0, 7, 15)
    if start > 0:  # intro : accord filtré qui tient jusqu'au drop
        add(chords, pad([midi(x) for x in ELECTRO_PROG[0][1]], start + 0.05, 5500, 0.3, voices), 0.0)
    for t, p, bar in grid(duration, start):
        ci = max(bar, 0) % 4
        root, chord = ELECTRO_PROG[ci]
        if p == 0 and t >= start:
            add(chords, get(("c", ci), lambda: pad([midi(x) for x in chord], 16 * S16 + 0.2, 5500, 0.02, voices)), t)
        if t < start:  # montée : roulement de claps qui accélère
            if start - t <= 1.0 + 1e-6 and (p % 2 == 0 or start - t <= 0.5 + 1e-6):
                add(drums, C, t, 0.25 + 0.5 * (1 - (start - t)))
            continue
        if p % 4 == 0:
            add(drums, K, t, 1.0)
            seg = (t_all >= t) & (t_all < t + BEAT)
            pump[seg] = 1 - 0.7 * np.exp(-(t_all[seg] - t) / 0.12)
        if p in (4, 12):
            add(drums, C, t, 0.7)
        if p in (2, 6, 10, 14):
            add(drums, HO, t, 0.45)
            f = midi(root)
            add(bass, get(("b", root), lambda: (bl_saw(f, int(0.2 * SR), 1500) + 0.7 * np.sin(2 * np.pi * f / 2 * np.arange(int(0.2 * SR)) / SR)) * ramp_env(int(0.2 * SR), 0.003, 0.05)), t)
        elif p % 2 == 1:
            add(drums, HC, t, 0.25)
        if p in ARP_STEPS:
            m = chord[ARP_STEPS[p]] + 12
            add(lead, get(("l", m), lambda: bl_saw(midi(m), int(0.14 * SR), 5000) * env_exp(int(0.14 * SR), 0.05)), t)

    i0 = int(start * SR)
    if i0 > 0:
        chords[:i0] = lp(chords[:i0], 700)
        add(fx, riser(start), 0.0, 0.7)
    chords *= pump
    bass *= 0.4 + 0.6 * pump
    lead = reverb(echo(lead, 3 * S16, 0.35), 1.0, 0.2)
    drums = reverb(drums, 0.6, 0.1)
    return drums * 0.9 + bass * 0.6 + chords * 0.5 + lead * 0.3 + fx * 0.6


# ---------------------------------------------------------------- phonk (ancien beat)

def bass808(freq, dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = freq * (1 + 1.0 * np.exp(-t / 0.025))
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * env_exp(n, dur * 0.55)
    x *= np.clip(np.arange(n) / 80, 0, 1)
    return np.tanh(2.2 * x) * 0.8


def cowbell(ratio=1.0, dur=0.28):
    n = int(dur * SR)
    t = np.arange(n) / SR
    sq = np.sign(np.sin(2 * np.pi * 587 * ratio * t)) + np.sign(np.sin(2 * np.pi * 845 * ratio * t))
    x = bp(sq, 600 * ratio, 2600 * ratio) * (0.25 * env_exp(n, 0.012) + 0.75 * env_exp(n, 0.09))
    return np.tanh(1.5 * x) * 0.5


BELL = [0, None, 0, None, 3, None, 0, None, 7, None, 5, None, 3, None, 0, None,
        0, None, 0, None, 3, None, 5, None, 3, None, 0, None, -2, None, 0, None]
PHONK_BASS = [(0, 0, 6), (6, 0, 4), (10, 3, 6), (16, 0, 6), (22, -2, 4), (26, -4, 6)]


def style_phonk(n, duration, start, cuts):
    drums, bass, bells, fx = (np.zeros(n) for _ in range(4))
    K, C, HC, HO = kick(), clap(), hat(), hat(True)
    bell_cache = {}
    if start > 0.6:
        add(fx, riser(start), 0.0, 0.8)
    t, step = 0.0, 0
    while t < duration:
        s, bar_step = step % 32, step % 16
        if BELL[s] is not None:
            if BELL[s] not in bell_cache:
                bell_cache[BELL[s]] = cowbell(2 ** (BELL[s] / 12))
            add(bells, bell_cache[BELL[s]], t, 0.55 if t >= start else 0.3)
        if t >= start:
            if bar_step in (0, 7, 10):
                add(drums, K, t, 1.0)
            if bar_step in (4, 12):
                add(drums, C, t, 0.7)
            add(drums, HO if bar_step == 14 else HC, t, 0.55 if bar_step % 2 == 0 else 0.3)
            for st, semi, ln in PHONK_BASS:
                if s == st:
                    add(bass, bass808(41.2 * 2 ** (semi / 12), ln * S16), t, 1.0)
        t += S16
        step += 1
    i0 = int(start * SR)
    if i0 > 0:
        bells[:i0] = bp(bells[:i0], 700, 2200)
    return drums * 0.9 + bass * 0.85 + bells * 0.6 + fx * 0.7


# ---------------------------------------------------------------- assemblage

BUILDERS = {"stade": style_stade, "samba": style_samba, "epique": style_epique,
            "electro": style_electro, "phonk": style_phonk}
IMPACT_GAIN = {"stade": 0.75, "samba": 0.4, "epique": 0.85, "electro": 0.55, "phonk": 0.85}


def pick_style(style, seed):
    if style in BUILDERS:
        return style
    return ROTATION[seed % len(ROTATION)]


def build(duration, cuts, seed=7, ticks=(), style=None):
    global RNG
    RNG = np.random.default_rng(seed)
    style = pick_style(style, seed)
    n = int((duration + 0.5) * SR)
    start = cuts[0] if cuts else 0.0
    mix = BUILDERS[style](n, duration, start, list(cuts))
    fx = np.zeros(n)
    add(fx, impact(), 0.0, 0.9)
    for c in cuts:
        add(fx, impact(), c, 1.0)
    tk = tick()
    for c in ticks:
        add(fx, tk, c, 1.4)
    mix = mix + fx * IMPACT_GAIN[style]
    mix = mix[: int(duration * SR)]
    mix -= np.mean(mix)
    fade = int(0.6 * SR)
    mix[-fade:] *= np.linspace(1, 0, fade)
    mix /= np.percentile(np.abs(mix), 99.9) + 1e-9
    mix = np.tanh(1.1 * mix)
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
    style = sys.argv[6] if len(sys.argv) > 6 else None
    wavfile.write(out, SR, build(dur, cuts, seed, ticks, style))
    print("ok", out, pick_style(style, seed))
