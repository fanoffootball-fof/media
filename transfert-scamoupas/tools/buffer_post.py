"""Programme dans Buffer les posts en attente de queue/*.json (lancé par la GitHub Action).

Un fichier de la file (queue/AAAA-MM-JJ_HHMM_sujet.json) :
    {"video": "videos/2026-11-08_1900_sms-livreur.mp4",
     "text": "Légende du post",
     "due": "2026-11-08T19:00:00+01:00",
     "services": ["tiktok"],
     "status": "pending"}
Après passage : "status" devient "scheduled" (avec "buffer_post_ids") ou "error" (avec "error").
"status": "hold" = fichier mis de côté (ex. file Buffer pleine) : ignoré jusqu'à ce qu'il repasse à "pending".
"status": "update" (avec "buffer_post_ids") = remplacer la vidéo d'un post déjà programmé par celle de "video".

    python3 tools/buffer_post.py            # programme les posts "pending"
    python3 tools/buffer_post.py --check    # vérifie la clé et liste les comptes Buffer
    python3 tools/buffer_post.py --dry-run  # affiche les requêtes sans rien envoyer

La clé est lue dans la variable d'environnement BUFFER_API_KEY (secret GitHub), jamais dans un fichier.
"""
import argparse
import datetime as dt
import glob
import json
import os
import sys
import time
import urllib.error
import urllib.request

API = "https://api.buffer.com"
REPO = os.environ.get("GITHUB_REPOSITORY", "scamoupas/media")
REF = os.environ.get("GITHUB_SHA", "main")
THUMB_MS = 1500  # image de couverture : l'écran titre, une fois apparu


def api_key():
    key = os.environ.get("BUFFER_API_KEY") or ""
    # un copier-coller depuis un téléphone peut ajouter des guillemets typographiques ou des caractères invisibles
    key = key.strip().strip("\"'“”‘’«»  ​‌‍﻿\r\n\t")
    if not key:
        sys.exit("BUFFER_API_KEY manquant : ajoute le secret dans Settings > Secrets and variables > Actions")
    if not key.isascii() or any(c.isspace() for c in key):
        bad = sorted({f"U+{ord(c):04X}" for c in key if not c.isascii() or c.isspace()})
        # forme de la clé sans dévoiler son contenu (x = caractère valide) : repère une clé masquée « abcd•••• »
        shape = "".join("x" if c.isascii() and not c.isspace() else ("•" if c == "•" else "?") for c in key)
        sys.exit(f"BUFFER_API_KEY contient des caractères invalides ({', '.join(bad)}, longueur {len(key)}, "
                 f"forme {shape}) : recolle la clé complète, sans guillemets ni espaces, dans le secret GitHub")
    return key


def gql(query):
    key = api_key()
    req = urllib.request.Request(
        API, data=json.dumps({"query": query}).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json",
                 "User-Agent": "scamoupas-media"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.load(r)
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Buffer HTTP {e.code} : {e.read().decode(errors='replace')[:500]}")
    if data.get("errors"):
        raise RuntimeError("Buffer : " + json.dumps(data["errors"], ensure_ascii=False)[:800])
    return data["data"]


def s(v):
    """Littéral de chaîne GraphQL (l'échappement JSON est compatible)."""
    return json.dumps(v, ensure_ascii=False)


def list_channels():
    out = []
    for org in gql("query { account { organizations { id name } } }")["account"]["organizations"]:
        q = f"query {{ channels(input: {{ organizationId: {s(org['id'])} }}) {{ id name service }} }}"
        for ch in gql(q)["channels"]:
            out.append(dict(ch, organization=org["name"]))
    return out


def video_url(path):
    return f"https://raw.githubusercontent.com/{REPO}/{REF}/{path}"


def url_ok(url, tries=4):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "scamoupas-media"})
            with urllib.request.urlopen(req, timeout=30) as r:
                if r.status == 200:
                    return True
        except urllib.error.URLError:
            pass
        time.sleep(10 * (i + 1))
    return False


def due_utc(due):
    d = dt.datetime.fromisoformat(due)
    if d.tzinfo is None:
        raise ValueError("'due' doit contenir le fuseau, ex. 2026-11-08T19:00:00+01:00")
    d = d.astimezone(dt.timezone.utc)
    if d < dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=5):
        raise ValueError(f"heure de publication passée ou trop proche : {due}")
    return d.strftime("%Y-%m-%dT%H:%M:%S.000Z")


# options propres à chaque réseau (Instagram : la vidéo part en Reel, affiché aussi dans la grille du profil)
def network_meta(service, ai=False):
    """Options propres à chaque réseau. ai=True : mention « contenu généré par IA » (voix off de synthèse)."""
    flag = " isAiGenerated: true" if ai else ""
    if service == "instagram":
        return f" metadata: {{ instagram: {{ type: reel, shouldShareToFeed: true{',' if ai else ''}{flag} }} }},"
    if service == "tiktok" and ai:
        return f" metadata: {{ tiktok: {{{flag} }} }},"
    return ""


def create_post(channel_id, text, url, due, service="tiktok", ai=False):
    m = (
        "mutation { createPost(input: {"
        f" text: {s(text)}, channelId: {s(channel_id)},"
        " schedulingType: automatic, mode: customScheduled,"
        f" dueAt: {s(due)},"
        f"{network_meta(service, ai)}"
        f" assets: [{{ video: {{ url: {s(url)}, metadata: {{ thumbnailOffset: {THUMB_MS} }} }} }}]"
        " }) { ... on PostActionSuccess { post { id dueAt } } ... on MutationError { message } } }"
    )
    return m


def edit_post(post_id, url):
    """Remplace la vidéo d'un post déjà programmé (le texte et l'horaire ne changent pas)."""
    return (
        "mutation { editPost(input: {"
        f" id: {s(post_id)},"
        f" assets: [{{ video: {{ url: {s(url)}, metadata: {{ thumbnailOffset: {THUMB_MS} }} }} }}]"
        " }) { ... on PostActionSuccess { post { id dueAt } } ... on MutationError { message } } }"
    )


def process(dry_run=False):
    files = sorted(glob.glob("queue/*.json"))
    pending = [(f, json.load(open(f, encoding="utf-8"))) for f in files]
    pending = [(f, it) for f, it in pending if it.get("status", "pending") in ("pending", "update")]
    if not pending:
        print("Rien à programmer.")
        return 0
    chans = None if dry_run else list_channels()
    errors = 0
    for f, it in pending:
        try:
            due = due_utc(it["due"])
            url = video_url(it["video"])
            if not dry_run and not url_ok(url):
                raise RuntimeError(f"vidéo introuvable en ligne : {url}")
            if it.get("status") == "update":  # nouvelle version de la vidéo d'un post déjà programmé
                if not it.get("buffer_post_ids"):
                    raise RuntimeError("status update sans buffer_post_ids")
                for pid in it["buffer_post_ids"]:
                    if dry_run:
                        print(f"[dry-run] {f} → edit {pid}\n{edit_post(pid, url)}\n")
                        continue
                    res = gql(edit_post(pid, url))["editPost"]
                    if "post" not in res:
                        raise RuntimeError(f"Buffer a refusé la modification de {pid} : {res.get('message')}")
                    print(f"ok {f} → vidéo remplacée sur le post {pid} (publication {res['post']['dueAt']})")
                if not dry_run:
                    it.update(status="scheduled", video_url=url,
                              edited_at=dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"))
                    it.pop("error", None)
            else:
                # un post par réseau ; ceux déjà créés (services_done) ne sont jamais recréés
                ids = list(it.get("buffer_post_ids") or [])
                done = list(it.get("services_done") or [])
                for service in it.get("services", ["tiktok"]):
                    if service in done:
                        continue
                    if dry_run:
                        print(f"[dry-run] {f} → {service}\n{create_post('<channel_id>', it['text'], url, due, service, it.get('ai_generated', False))}\n")
                        continue
                    matches = [c for c in chans if c["service"] == service]
                    if len(matches) != 1:
                        raise RuntimeError(f"{len(matches)} compte(s) {service} dans Buffer : il en faut exactement 1")
                    res = gql(create_post(matches[0]["id"], it["text"], url, due, service, it.get("ai_generated", False)))["createPost"]
                    if "post" not in res:
                        raise RuntimeError(f"Buffer a refusé le post {service} : {res.get('message')}")
                    ids.append(res["post"]["id"])
                    done.append(service)
                    it.update(buffer_post_ids=ids, services_done=done)  # gardé même si un réseau suivant échoue
                    print(f"ok {f} → {service} @{matches[0]['name']} le {res['post']['dueAt']} (id {res['post']['id']})")
                if dry_run:
                    continue
                it.update(status="scheduled", buffer_post_ids=ids, video_url=url,
                          scheduled_at=dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"))
        except Exception as e:  # noqa: BLE001 — on note l'erreur dans le fichier et on continue
            errors += 1
            print(f"ERREUR {f} : {e}", file=sys.stderr)
            if dry_run:
                continue
            it.update(status="error", error=str(e)[:500])
        with open(f, "w", encoding="utf-8") as fh:
            json.dump(it, fh, ensure_ascii=False, indent=2)
            fh.write("\n")
    return 1 if errors else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if a.check:
        chans = list_channels()
        print(f"Clé valide. {len(chans)} compte(s) dans Buffer :")
        for c in chans:
            print(f"  - {c['service']:10s} {c['name']}  ({c['organization']})")
        if not any(c["service"] == "tiktok" for c in chans):
            print("Aucun compte TikTok connecté : connecte @scamoupas dans Buffer.", file=sys.stderr)
            sys.exit(1)
        return
    sys.exit(process(a.dry_run))


if __name__ == "__main__":
    main()
