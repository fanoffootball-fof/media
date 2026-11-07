"""Voix off : place les répliques générées par ElevenLabs au début de chaque scène, allonge les scènes
trop courtes pour la réplique et baisse la musique pendant que la voix parle.

Une scène porte sa réplique dans le champ "say" de la spec. Les fichiers audio sont produits par
tools/tts.py (GitHub Action « Voix off ») dans voice/<nom de la spec>/scene_NN.mp3, avec un
manifest.json qui garde le texte prononcé : si le texte de la spec change, la voix est « périmée ».

Utilisé par make_video.py :
    clips = voice.prepare(spec, chemin_spec, strict)   # avant le calcul des durées
    musique = voice.mix(musique, spec, clips)          # après music.build
Ce module ne fait rien pour une spec sans "say".
"""
import json
import os
import subprocess
import sys

import numpy as np

SR = 44100
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # racine du dépôt
LEAD = 0.15        # la voix démarre 0,15 s après le début de la scène…
LEAD_FIRST = 0.55  # … et après la signature sonore pour la première scène
TAIL = 0.35        # marge après la dernière syllabe
DUCK = 0.3         # niveau de la musique sous la voix (environ -10 dB)


def scene_dur(sc):
    """Même règle que make_video.py : 1,5 s minimum, grille de 0,5 s."""
    return max(1.5, round(float(sc.get("dur", 3.5)) * 2) / 2)


def lines(spec):
    return {i: str(sc["say"]).strip() for i, sc in enumerate(spec["scenes"]) if str(sc.get("say", "")).strip()}


def folder(spec_path):
    return os.path.join(ROOT, "voice", os.path.splitext(os.path.basename(spec_path))[0])


def decode(path, speed=1.0):
    af = ["-af", f"atempo={speed:.3f}"] if abs(speed - 1.0) > 1e-3 else []
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, *af, "-f", "s16le", "-ac", "1", "-ar", str(SR), "-"],
                         check=True, capture_output=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768


def trim(x, thr=0.02):
    """Retire les silences du début et de la fin (en gardant 30 ms)."""
    idx = np.flatnonzero(np.abs(x) > thr)
    if len(idx) == 0:
        return x
    pad = int(0.03 * SR)
    return x[max(0, idx[0] - pad): idx[-1] + pad]


def prepare(spec, spec_path, strict=True):
    """Charge les répliques et allonge les scènes qui en ont besoin (modifie spec en place)."""
    todo = lines(spec)
    if not todo:
        return {}
    d = folder(spec_path)
    man_path = os.path.join(d, "manifest.json")
    man = json.load(open(man_path, encoding="utf-8")) if os.path.exists(man_path) else {}
    speed = float(spec.get("voice_speed", 1.0))
    clips, missing = {}, []
    for i, text in todo.items():
        key = f"scene_{i + 1:02d}"
        path = os.path.join(d, key + ".mp3")
        if man.get(key, {}).get("text") != text or not os.path.exists(path):
            missing.append(key)
            continue
        clips[i] = trim(decode(path, speed))
    if missing:
        msg = (f"voix manquante ou périmée ({', '.join(missing)}) dans {os.path.relpath(d, ROOT)} : "
               "pousser la spec puis attendre l'Action « Voix off »")
        if strict:
            sys.exit(msg)
        print("attention : " + msg)
    for i, c in clips.items():
        lead = LEAD_FIRST if i == 0 else LEAD
        need = lead + len(c) / SR + TAIL
        if scene_dur(spec["scenes"][i]) < need:
            spec["scenes"][i]["dur"] = float(np.ceil(need * 2) / 2)
    return clips


def duck_envelope(v, n):
    """1 hors voix, DUCK pendant la voix, avec attaque (60 ms) et relâchement (300 ms) progressifs."""
    hop = int(0.01 * SR)
    frames = int(np.ceil(n / hop))
    pad = np.zeros(frames * hop, np.float32)
    pad[:n] = v
    rms = np.sqrt(np.mean(pad.reshape(frames, hop) ** 2, axis=1))
    active = (rms > 0.01).astype(np.float32)
    hold = 15  # 150 ms : pas de remontée de la musique entre deux mots
    active = np.convolve(active, np.ones(hold), mode="same") > 0
    env = np.zeros(frames, np.float32)
    a_up, a_down, e = np.exp(-1 / 6), np.exp(-1 / 30), 0.0
    for k in range(frames):
        target = 1.0 if active[k] else 0.0
        coef = a_up if target > e else a_down
        e = target + (e - target) * coef
        env[k] = e
    gain = 1.0 - (1.0 - DUCK) * env
    return np.repeat(gain, hop)[:n]


def mix(music16, spec, clips):
    """Mélange la voix à la musique (tableau int16 stéréo de music.build)."""
    if not clips:
        return music16
    m = music16[:, 0].astype(np.float32) / 32767
    n = len(m)
    starts, t = [], 0.0
    for sc in spec["scenes"]:
        starts.append(t)
        t += scene_dur(sc)
    v = np.zeros(n, np.float32)
    for i, c in clips.items():
        a = int(round((starts[i] + (LEAD_FIRST if i == 0 else LEAD)) * SR))
        b = min(n, a + len(c))
        if b > a:
            v[a:b] += c[: b - a]
    peak = np.max(np.abs(v)) + 1e-9
    v *= 0.9 / peak
    out = m * duck_envelope(v, n) + v
    out /= np.max(np.abs(out)) + 1e-9
    out *= 0.89
    return (np.stack([out, out], axis=1) * 32767).astype(np.int16)
