# Format des specs vidéo (`specs/*.json`)

Une spec décrit une vidéo verticale 1080×1920 de 20 à 30 s, découpée en scènes.
Rendu : `python3 tools/make_video.py specs/x.json videos/x.mp4`
Contrôle visuel : `python3 tools/make_video.py specs/x.json --stills <dossier>` (dernière image de chaque scène).

Le son (musique originale générée en code, libre de droits, 5 ambiances légères) est ajouté automatiquement ;
un souffle doux marque les changements de scène et les comptes à rebours ajoutent des petits coups de bois.

## Racine

| clé | rôle |
|---|---|
| `accent` | couleur du halo de fond (`"red"` par défaut pour @scamoupas) |
| `seed` | entier : varie les sons d'une vidéo à l'autre |
| `music` | ambiance de la musique de fond : `lofi`, `pop`, `house`, `funk` ou `marimba` (sans elle : choisie d'après `seed`) |
| `signature` | `true` par défaut : deux notes de marimba qui montent (signature sonore du compte) au tout début. `false` seulement pour un test. |
| `voice_speed` | voix off : vitesse de la voix (défaut `1.0`, `1.08` pour accélérer un peu) |
| `scenes` | liste des scènes (ci-dessous) |

Couleurs : `white gold grey light red green blue pink purple orange cyan dark`, ou `"#RRGGBB"`.
Durées (`dur`, en secondes) arrondies à 0,5 s (minimum 1,5 s). Une ligne = `"texte"` ou `{"t": "texte", "color": "gold"}`.
Toute scène accepte `"source": "Source : Cybermalveillance.gouv.fr"` (petite mention en bas).
Toute scène accepte `"say": "réplique"` : voix off prononcée au début de la scène (voir « Voix off » dans
`PIPELINE.md`). La scène est allongée automatiquement si la réplique est plus longue qu'elle. Le fichier audio vient
de l'Action « Voix off ElevenLabs » (`voice/<nom de la spec>/`) : le rendu s'arrête s'il manque ou si le texte a changé.

## La scène clé : `message`

Le message reçu (SMS, mail ou appel retranscrit) dans un cadre de téléphone.

```json
{"type": "message", "dur": 5.0,
 "msg": {"kind": "sms", "sender": "+33 6 •• •• •• 47", "meta": "SMS · aujourd'hui 09:41", "sender_flag": 1,
         "lines": ["Bonjour, c'est le livreur.",
                   {"t": "point-relais-fr[.]info/k7Qe", "link": true, "flag": 2},
                   {"t": "Frais de réexpédition : 1,99 €", "flag": 3}]},
 "question": ["ARNAQUE OU PAS ?"], "countdown": true}
```

- `msg.kind` : `sms` (bulle grise), `email` (ajouter `subject`, en gras en 1re ligne), `call` (bulle sombre, texte de l'appel entre « »),
  `alert` (alerte officielle sur le téléphone, bulle jaune pâle), `popup` (fenêtre surgissante sur un ordinateur).
- `msg.sender` : un numéro masqué (`+33 6 •• •• •• 47` → silhouette) ou un nom **générique** (`TA BANQUE`, `LIVRAISON`, `IMPÔTS`…).
- `msg.lines` : 3 à 6 lignes de **30 caractères max** (déjà coupées). `link: true` = lien bleu souligné, **toujours désamorcé** avec `[.]`.
- `flag` (1, 2, 3…) sur une ligne, `sender_flag` sur l'expéditeur : indices numérotés, encadrés en rouge quand `highlight` est vrai.
- Options de scène :
  - `question` + `countdown: true` → la question et le compte à rebours de 3 s (prévoir `dur: 5.0`) ;
  - `highlight: true` → encadre les indices un par un (le message ne se ré-anime pas) ; encadrés rouges, ou verts
    quand `verdict` vaut `"VRAI"` (les signes que le message est légitime) ; `mark_color` pour forcer une couleur ;
  - `verdict: "ARNAQUE"` (rouge) ou `"VRAI"` (vert), `verdict_sub` (phrase sous le tampon) ;
  - `static: true` → message déjà affiché, sans animation d'entrée (pour un verdict sans indices).

Enchaînement type : `title` → `message` (question + compte à rebours) → `message` (`highlight` + `verdict`) → `cards` (les indices) → `statement` (le bon réflexe) → `poll` (question + appel au partage).

## Autres types de scènes

- `title` — accroche : `kicker` (pastille, ex. "ARNAQUE OU PAS ?"), `lines` (gros texte, 1 à 3 lignes), `sub`, `pill`, `size` (défaut 220).
- `cards` — liste de cartes : `title`, `subtitle`, `items` = `["Texte", ["Texte", "sous-texte"]]`, `numbered`, `badge_color` (`"red"` pour les indices).
- `statement` — phrase choc sur 1 à 3 lignes colorées : `lines`, `box` = `["ligne 1", "ligne 2 dorée"]`, `size` (défaut 92).
- `poll` — appel au commentaire : `lines`, `options` = `[{"label": "OUI", "color": "red"}, {"label": "NON", "color": "green"}]`, `filled`, `cta` (ex. « Envoie-la à tes parents »), `size`.
- `counters`, `progress`, `reveal`, `quiz_clue`, `custom` — hérités du générateur @fanoffootball (voir `make_video.py`), utiles pour un chiffre choc (« 500 000 victimes aidées en 2025 »).

## Règles de mise en page

- Le contenu utile tient entre y≈360 et y≈1450 : le bas est couvert par la légende TikTok, la droite par les boutons. Le script avertit si une scène dépasse.
- Textes courts : 2 à 4 mots par grosse ligne, 6 à 8 mots max pour un sous-texte.
- Jamais de logo, de capture d'écran réelle, de vrai numéro ni de lien cliquable.

Exemples complets : `specs/exemples/`.
