# Format des specs vidéo (`specs/*.json`)

Une spec décrit une vidéo verticale 1080×1920 de 15 à 25 s, découpée en scènes.
Rendu : `python3 tools/make_video.py specs/x.json videos/x.mp4`
Contrôle visuel : `python3 tools/make_video.py specs/x.json --stills /tmp/stills_x` (dernière image de chaque scène).

Le son (musique originale générée en code par `tools/music.py`, libre de droits) est ajouté automatiquement
et calé sur les changements de scène ; les comptes à rebours des quiz ajoutent des « tic ».

## Racine

| clé | rôle |
|---|---|
| `accent` | couleur du halo de fond (`"red"`, `"blue"`, `"purple"`…) ou `{"split": ["blue", "pink"]}` pour un duel (gauche/droite) |
| `left_name`, `right_name` | noms pour les scènes `duel` (si `split`) |
| `seed` | entier : varie les détails du son d'une vidéo à l'autre |
| `music` | ambiance sonore : `"stade"` (hymne de stade, cuivres, foule), `"samba"` (batucada, sifflet), `"epique"` (bande-annonce, tambours, cordes) ou `"electro"` (hymne électro de résumé de match). `"phonk"` (ancien beat) reste possible mais hors rotation. Sans ce champ, l'ambiance découle de `seed`. |
| `signature` | `true` par défaut : deux coups de sifflet (signature sonore du compte) au tout début. `false` seulement pour un test. |
| `scenes` | liste des scènes (ci-dessous) |

Couleurs : `white gold grey light red green blue pink purple orange cyan dark`, ou `"#RRGGBB"`.
Durées (`dur`, en secondes) arrondies à 0,5 s (minimum 1,5 s). Une ligne = `"texte"` ou `{"t": "texte", "color": "gold"}`.
Toute scène accepte `"source": "Stats Foot Mercato, au 07/11/2026"` (petite mention en bas).

## Types de scènes

- `title` — accroche : `kicker` (pastille dorée, ex. "QUIZ"), `lines` (gros texte, 1 à 3 lignes), `sub` (1re ligne blanche, suivantes plus petites), `pill` (pastille couleur d'accent), `size` (défaut 220).
- `counters` — compteurs animés : `top`, `items` = `[{"value": 234, "from": 0, "label": "SÉLECTIONS", "size": 260, "color": "gold", "suffix": ""}]` (1 ou 2 items), `chips` = `[{"label": "Mbappé", "sub": "27 ans", "color": "blue"}]`, `badge`.
- `cards` — liste de cartes : `title`, `subtitle`, `items` = `["EURO 2016", ["Texte", "sous-texte"]]`, `numbered` (true pour un top 3 / top 5).
- `progress` — jauge vers un objectif : `top`, `value`, `from`, `label`, `target`, `big` (texte doré), `sub`, `left_label`, `right_label`.
- `duel` — comparaison barre à barre : `rows` = `[{"label": "BUTS", "l": 16, "r": 13}]` (2 ou 3 lignes), `left`/`right` (sinon `left_name`/`right_name`).
- `statement` — phrase choc sur 1 à 3 lignes colorées : `lines`, `box` = `["ligne 1", "ligne 2 dorée"]`, `size` (défaut 92).
- `poll` — appel au commentaire : `lines`, `options` = `[{"label": "OUI", "color": "green"}]` (2 ou 3), `filled` (false = boutons discrets), `cta`, `size` (défaut 130).
- `quiz_clue` — indice de quiz avec compte à rebours 3 s : `clues` (les 3 indices, toujours la même liste), `index` (0, 1 puis 2), `title`, `kicker`. Prévoir `dur: 4.0`.
- `reveal` — réponse : `pre` ("C'EST…"), `lines` (nom en doré), `sub`, `pill`.
- `pitch` — but refait en 2D (moteur : `tools/pitch.py`, modèle : `specs/exemples/but_2d_zidane.json`). Terrain vu de dessus, l'équipe qui attaque monte vers le haut.
  - Coordonnées : `x` 0 → 100 de la ligne de touche gauche à la droite ; `y` 0 → 100 de sa propre ligne de but à la ligne de but adverse (au-delà de 100 : dans le but, filet jusqu'à ≈ 101,9). Repères : surface de réparation x 20,4 à 79,6 et y ≥ 84,3 ; point de penalty (50 ; 89,5) ; poteaux x 44,6 et 55,4.
  - `view_from` : partie du terrain affichée à partir de ce `y` (50 par défaut = moitié adverse ; 30 pour une action qui part de plus loin, le terrain rétrécit).
  - `players` : `[{"team": "att"|"def"|"gk", "label": "Zidane", "star": true, "path": [[x, y, t], ...]}]` ; `att` prend la couleur `accent` (ou `att_color`), `def` est blanc, `gk` jaune ; `star` = cercle doré et course en pointillés ; `label` seulement pour les joueurs cités par la source.
  - `ball` : `[[x, y, t], ...]` ; ajouter `"air"` en 4e valeur pour un segment aérien (centre, lob) jusqu'à ce point. Une trace dorée suit le ballon.
  - `goal_t` : instant (s) où le ballon franchit la ligne → flash, « BUT ! » et clameur de foule dans le son.
  - `captions` : `[[t, "Solari lance Roberto Carlos"], ...]` (légende du moment, sous le terrain).
  - `kicker`, `title` : en-tête au-dessus du terrain ; `keep_header` : true pour ne pas réanimer le titre.
  - `speed` (1 = temps réel, 0,6 = ralenti), `t0` (instant de départ), `replay` : true pour reprendre `players`, `ball`, `goal_t`, `captions` et `view_from` de la scène `pitch` précédente.
  - Les temps sont en secondes « réelles » depuis le début de l'action ; prévoir `dur` ≥ (dernier temps − `t0`) / `speed` + 1,5 s pour voir le « BUT ! ».
- `pitch3d` — même but en 3D stylisée (moteur : `tools/pitch3d.py` + `tools/render3d/scene.js`, three.js fourni dans `tools/vendor/three` ; modèle : `specs/exemples/but_3d_zidane.json`). Stade de nuit, joueurs-mannequins sans visage ni logo, ballon avec sa vraie hauteur. Mêmes champs que `pitch` (sauf `view_from`), plus :
  - `camera` : `{"mode": "follow"}` (caméra aérienne qui suit l'action, par défaut) ou `{"mode": "goal"}` (en hauteur derrière le but adverse, idéal pour le ralenti) ; réglages facultatifs `height`, `back`, `fov`, `side`.
  - Ballon : 4e valeur d'une image clé = mots séparés par des espaces : `air` (centre, lob), `z=0.7` (hauteur d'arrivée en m, ex. une volée), `high` / `low` (frappe qui finit haut ou à ras de terre dans le but).
  - `def_color` : couleur des défenseurs (rouge par défaut en 3D).
  - Rendu lent (≈ 0,7 s par image, soit 3 à 4 min pour 10 s de 3D) : Chrome sans écran + Playwright, déjà présents dans l'environnement.
- `custom` — `elements` libres, empilés et centrés : `{"kind": "big"|"text"|"pill"|"counter"|"card"|"bar"|"options"|"chips"|"box"|"spacer", ...}` (mêmes champs que ci-dessus).

## Règles de mise en page

- Le contenu utile tient entre y≈400 et y≈1450 : le bas de l'écran est couvert par la légende TikTok, la droite par les boutons. Le script avertit si une scène dépasse.
- Textes courts : 2 à 4 mots par grosse ligne, 6 à 8 mots max pour un sous-texte.
- Jamais de photo de joueur, de logo de club ou d'image de match.

Exemples complets : `specs/exemples/`.
