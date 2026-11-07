"""Génère les voix off avec ElevenLabs (lancé par la GitHub Action « Voix off »).

    python3 tools/tts.py           # pour chaque spec de specs/ qui contient des "say" : génère ce qui manque
    python3 tools/tts.py --check   # vérifie la clé et la voix, puis crée voice/echantillons/*.mp3 à écouter

Résultat : voice/<nom de la spec>/scene_NN.mp3 + manifest.json (texte prononcé, modèle, date).
En cas d'échec : voice/<nom de la spec>/erreur.txt (lu par la tâche quotidienne).

La clé (ELEVENLABS_API_KEY) et l'identifiant de la voix clonée (ELEVENLABS_VOICE_ID) viennent des secrets
GitHub, jamais d'un fichier. Le modèle peut être choisi avec la variable ELEVENLABS_MODEL (défaut : eleven_v4).
"""
import argparse
import datetime as dt
import glob
import json
import os
import sys
import urllib.error
import urllib.request

API = "https://api.elevenlabs.io/v1"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL = os.environ.get("ELEVENLABS_MODEL") or "eleven_v4"
FALLBACK = "eleven_multilingual_v2"
SETTINGS = {"stability": 0.45, "similarity_boost": 0.85, "style": 0.15, "use_speaker_boost": True}
MAX_CHARS = 4000  # garde-fou : caractères générés au plus par passage (1 caractère ≈ 1 crédit)
SAMPLE = ("Arnaque ou pas ? Tu as trois secondes pour trancher. Regarde bien l'adresse : un vrai livreur "
          "ne te demande jamais de payer des frais par SMS. Dans le doute, tu ne cliques pas.")


def env(name):
    v = os.environ.get(name, "").strip()
    if not v:
        sys.exit(f"{name} manquant : l'ajouter dans Settings > Secrets and variables > Actions du dépôt")
    return v


def request(method, path, body=None, accept="application/json"):
    req = urllib.request.Request(API + path, method=method,
                                 data=json.dumps(body).encode() if body is not None else None,
                                 headers={"xi-api-key": env("ELEVENLABS_API_KEY"), "Content-Type": "application/json",
                                          "Accept": accept, "User-Agent": "media-voice"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()


def synth(text):
    """Renvoie (mp3, modèle utilisé). Essaie le modèle choisi, sans réglages, puis le modèle de repli."""
    voice_id = env("ELEVENLABS_VOICE_ID")
    tries = [(MODEL, SETTINGS), (MODEL, None)]
    if MODEL != FALLBACK:
        tries.append((FALLBACK, SETTINGS))
    last = None
    for model, settings in tries:
        body = {"text": text, "model_id": model}
        if settings:
            body["voice_settings"] = settings
        try:
            return request("POST", f"/text-to-speech/{voice_id}?output_format=mp3_44100_128", body, "audio/mpeg"), model
        except urllib.error.HTTPError as e:
            last = f"ElevenLabs HTTP {e.code} ({model}) : {e.read().decode(errors='replace')[:400]}"
            if e.code in (401, 403, 429) or e.code >= 500:  # clé, droits, quota ou panne : inutile d'insister
                break
    raise RuntimeError(last)


def lines(spec):
    return {i: str(sc["say"]).strip() for i, sc in enumerate(spec["scenes"]) if str(sc.get("say", "")).strip()}


def process():
    specs = [p for p in sorted(glob.glob(os.path.join(ROOT, "specs", "*.json")))]
    work = []
    for p in specs:
        try:
            todo = lines(json.load(open(p, encoding="utf-8")))
        except (json.JSONDecodeError, KeyError):
            continue
        if not todo:
            continue
        d = os.path.join(ROOT, "voice", os.path.splitext(os.path.basename(p))[0])
        man_path = os.path.join(d, "manifest.json")
        man = json.load(open(man_path, encoding="utf-8")) if os.path.exists(man_path) else {}
        stale = {i: t for i, t in todo.items()
                 if man.get(f"scene_{i + 1:02d}", {}).get("text") != t
                 or not os.path.exists(os.path.join(d, f"scene_{i + 1:02d}.mp3"))}
        if stale:
            work.append((d, man_path, man, stale))
    if not work:
        print("rien à générer")
        return 0
    used, failed = 0, False
    for d, man_path, man, stale in work:
        os.makedirs(d, exist_ok=True)
        err_path = os.path.join(d, "erreur.txt")
        try:
            for i, text in stale.items():
                if used + len(text) > MAX_CHARS:
                    raise RuntimeError(f"garde-fou : plus de {MAX_CHARS} caractères à générer en un passage")
                mp3, model = synth(text)
                used += len(text)
                key = f"scene_{i + 1:02d}"
                open(os.path.join(d, key + ".mp3"), "wb").write(mp3)
                man[key] = {"text": text, "model": model,
                            "generated": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
            json.dump(man, open(man_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            if os.path.exists(err_path):
                os.remove(err_path)
            print(f"ok {os.path.relpath(d, ROOT)} ({len(stale)} réplique(s))")
        except RuntimeError as e:
            failed = True
            json.dump(man, open(man_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            open(err_path, "w", encoding="utf-8").write(str(e) + "\n")
            print(f"erreur {os.path.relpath(d, ROOT)} : {e}")
    print(f"{used} caractères générés")
    return 1 if failed else 0


def check():
    voice_id = env("ELEVENLABS_VOICE_ID")
    info = json.loads(request("GET", f"/voices/{voice_id}"))
    print(f"voix trouvée : {info.get('name')} ({info.get('category')})")
    d = os.path.join(ROOT, "voice", "echantillons")
    os.makedirs(d, exist_ok=True)
    global MODEL
    for model in dict.fromkeys([MODEL, FALLBACK]):
        MODEL = model
        mp3, used = synth(SAMPLE)
        path = os.path.join(d, f"echantillon_{used}.mp3")
        open(path, "wb").write(mp3)
        print(f"échantillon : {os.path.relpath(path, ROOT)}")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    sys.exit(check() if ap.parse_args().check else process())
