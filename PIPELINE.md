# Production quotidienne @fanoffootball (TikTok + YouTube Shorts)

Ce document est la procédure suivie chaque matin par la tâche planifiée Claude.
Propriétaire : Olivier. Compte TikTok : `fanoffootball_fof` et chaîne YouTube (Shorts) connectée le 07/11/2026, tous deux publiés via Metricool (marque `7925135`, fuseau `Europe/Paris`).

**Chaque vidéo part sur les deux réseaux, à la même heure, en deux posts Metricool séparés** (un post `tiktok`, un post `youtube`), pour qu'un refus sur un réseau ne bloque pas l'autre.

## Campagne

- Du **samedi 7 novembre au vendredi 4 décembre 2026** inclus : **2 vidéos par jour, à 12:00 et 18:00** (heure de Paris). On reste à 2 par jour.
- Objectif : des vidéos **virales** sur le foot, avec **beaucoup de joueurs différents** (pas de joueur favori).
- **Diversité :** deux joueurs différents chaque jour ; un même joueur au plus **2 fois par semaine** (sauf très grosse actu) ; alterner joueurs actuels et légendes. Vérifier dans `journal.md`.
- Les vidéos restent courtes (15 à 25 s). Choix d'Olivier : **pas de format long (≥ 1 min) tant que les conditions de monétisation ne sont pas remplies** (10 000 abonnés et 100 000 vues sur 30 jours). D'ici là, tout l'effort va à la croissance : vues, partages et surtout **conversion en abonnés**. Le format long ne démarre ensuite qu'après accord d'Olivier.

## Réservoir de joueurs : top 5 du Ballon d'Or (éditions 2006 à 2026, pas d'édition en 2020)

| année | 1er | 2e | 3e | 4e | 5e |
|---|---|---|---|---|---|
| 2006 | Cannavaro | Buffon | Henry | Ronaldinho | Zidane |
| 2007 | Kaká | C. Ronaldo | Messi | Drogba | Pirlo |
| 2008 | C. Ronaldo | Messi | Torres | Casillas | Xavi |
| 2009 | Messi | C. Ronaldo | Xavi | Iniesta | Eto'o |
| 2010 | Messi | Iniesta | Xavi | Sneijder | Forlán |
| 2011 | Messi | C. Ronaldo | Xavi | Iniesta | Rooney |
| 2012 | Messi | C. Ronaldo | Iniesta | Xavi | Falcao |
| 2013 | C. Ronaldo | Messi | Ribéry | Ibrahimović | Neymar |
| 2014 | C. Ronaldo | Messi | Neuer | Robben | Müller |
| 2015 | Messi | C. Ronaldo | Neymar | Lewandowski | Suárez |
| 2016 | C. Ronaldo | Messi | Griezmann | Suárez | Neymar |
| 2017 | C. Ronaldo | Messi | Neymar | Buffon | Modrić |
| 2018 | Modrić | C. Ronaldo | Griezmann | Mbappé | Messi |
| 2019 | Messi | Van Dijk | C. Ronaldo | Mané | Salah |
| 2021 | Messi | Lewandowski | Jorginho | Benzema | Kanté |
| 2022 | Benzema | Mané | De Bruyne | Lewandowski | Salah |
| 2023 | Messi | Haaland | Mbappé | De Bruyne | Rodri |
| 2024 | Rodri | Vinícius Jr | Bellingham | Carvajal | Lautaro Martínez |
| 2025 | Dembélé | Yamal | Vitinha | Salah | Raphinha |
| 2026 | Kane | Mbappé | Yamal | Rodri | Messi |

Tableau établi le 06/11/2026 : revérifier un rang ou un chiffre avant de l'utiliser dans une vidéo. Les joueurs à l'actu de la semaine (hors liste) sont permis, au plus 3 fois par semaine en tout.

## Rotation des formats

| jour | 12:00 | 18:00 |
|---|---|---|
| lundi | stats d'un joueur actuel en forme (`counters` / `progress`) | quiz « devine le joueur » (légende) |
| mardi | duel (légende vs légende ou légende vs actuel, carrière comparée) | débat « Ballon d'Or volé ? » (`poll`) |
| mercredi | actu de la semaine (Ligue des champions, etc.) | « Ce jour-là » (éphéméride, voir plus bas) |
| jeudi | record ou objectif en cours (`progress`) | quiz « devine le joueur » |
| vendredi | duel entre joueurs actuels | top 3 (`cards` numérotées : records, buts, titres) |
| samedi | stats avant le week-end | but refait en 2D (scène `pitch`, voir plus bas) |
| dimanche | bilan du week-end (buts, notes, records) | choix impossible (voir plus bas) |

Une **grosse actu** (record, retraite, blessure officielle, transfert officiel, Ballon d'Or…) passe devant la rotation au créneau suivant.

**Jour de gros match : le pronostic passe devant tout** (y compris une grosse actu, qui prend alors l'autre créneau). Le format de la rotation qu'il remplace est sauté ce jour-là, pas reporté.

## Formats spéciaux

### Pronostic (prioritaire les jours de gros match)

- **Repérage, chaque jour à l'étape 3** : chercher les matchs du jour et leurs heures de coup d'envoi (WebSearch + WebFetch : L'Équipe, Foot Mercato, sites officiels).
- **Gros match** = un match de l'équipe de France ; un match de Ligue des champions avec un club français, ou entre deux clubs de cette liste : Real Madrid, Barcelone, Atlético, Bayern, Dortmund, Manchester City, Liverpool, Arsenal, Chelsea, Manchester United, Inter, Milan, Juventus, PSG ; tout match de Ligue des champions à élimination directe ; PSG-OM, OM-OL, PSG-OL ; Real-Barça, derby de Madrid ; Premier League entre deux clubs de la liste ; Inter-Milan, Inter-Juventus, Milan-Juventus ; Bayern-Dortmund ; toute finale.
- **Créneau** : le dernier créneau qui tombe au moins 1 h avant le coup d'envoi (18:00 pour un match à 20:45 ou 21:00, 12:00 pour un coup d'envoi entre 13:00 et 18:59). Coup d'envoi avant 13:00 : pas de pronostic. Au plus un pronostic par jour, pour le plus gros match (équipe de France, puis club français, puis Real-Barça, puis le reste).
- **Structure** : `title` (pastille « PRONOSTIC », l'affiche en gros, heure et compétition en sous-titre) → `duel` (forme sur les 5 derniers matchs, buts marqués, classement : chiffres vérifiés le jour même) → éventuellement `counters` (confrontations directes) → `poll` « QUI GAGNE ? » à 3 options (équipe 1 / NUL / équipe 2), cta « Ton score exact en commentaire ». Fond `split` aux couleurs des deux équipes, jamais de logo.
- **Interdit** : cotes, sites de paris, toute incitation à parier.

### Ce jour-là (mercredi 18:00)

- Un événement marquant survenu **à la même date (jour et mois)** une année passée : but légendaire, titre, record, transfert, débuts d'un joueur. Priorité aux anniversaires ronds (10, 15, 20, 25, 30 ans…).
- Date exacte vérifiée dans **deux sources** (Wikipédia + UEFA, FIFA, site du club ou presse).
- **Structure** : `title` (pastille « CE JOUR-LÀ », « IL Y A 20 ANS » + le joueur ou l'équipe, la date en sous-titre) → `counters` ou `cards` (les faits) → `statement` (pourquoi c'est historique) → `poll`.
- Rien de solide pour la date : se rabattre sur un « le saviez-vous » (`cards`).

### But refait en 2D (samedi 18:00)

- Un but célèbre (finale, but mythique d'une légende) ou un très grand but de la semaine. Modèle : `specs/exemples/but_2d_zidane.json`.
- **Faits** : le déroulé (passeur, buteur, pied, type de frappe, contexte, date, score) est vérifié dans un compte rendu de match (UEFA.com, site du club, L'Équipe, Wikipédia). Les positions sont approximatives : chaque scène `pitch` porte `"source": "Reconstitution schématique · d'après <source>"`. Seuls les joueurs cités par la source ont un `label` ; les autres restent anonymes. Aucun détail invérifié dans les légendes (ex. ne pas dire « lucarne » si la source ne le dit pas).
- **Structure** : `title` (accroche, nom du buteur en gros) → `pitch` à vitesse réelle (4,5 à 5,5 s) → `pitch` avec `"replay": true`, `"speed": 0.6` et `t0` au début de l'action décisive (5 à 6 s) → `statement` ou `counters` (contexte) → `poll`.
- **Animation** : 3 à 6 joueurs impliqués, quelques défenseurs et le gardien ; une image clé toutes les 0,5 à 1,5 s ; le ballon reste collé au porteur (même position à ±1) ; `"air"` pour un centre ou une passe lobée ; `goal_t` = instant où le ballon franchit la ligne. Le contrôle visuel (étape 6) inclut les images intermédiaires `scene_XXa/b.jpg` : joueurs et ballon cohérents, étiquettes lisibles.

### Choix impossible (dimanche 18:00)

- « Tu ne peux en garder qu'un » : 3 manches de 2 joueurs (légendes et/ou actuels), par exemple un attaquant, un milieu, un gardien, ou « 2006 contre 2026 ».
- **Structure** : `title` (pastille « CHOIX IMPOSSIBLE », « TU EN GARDES » / « UN SEUL ») → 3 scènes `poll` de 3,0 s (le thème de la manche en `lines`, les 2 joueurs en `options`, cta « Lequel tu gardes ? ») → `statement` final avec cta « Tes 3 choix en commentaire ».
- Les joueurs de ce format ne comptent pas dans la limite de diversité ; ne pas reprendre la même paire de joueurs pendant la campagne.

## Recettes virales

- **Accroche dans la 1re seconde** : chiffre choc, question clivante ou affirmation forte (« Le Ballon d'Or le plus volé de l'histoire ? »).
- Des débats qui font réagir sans être insultants : Ballon d'Or contesté, meilleur joueur d'une génération, duel de légendes.
- Toujours finir par une question fermée (2 ou 3 choix) qui pousse au commentaire.
- **Mot-clé de recherche partout** : le nom du joueur (ou le duel) est écrit en gros dans la 1re scène et ouvre la légende et le titre YouTube. TikTok lit le texte à l'écran et la légende pour classer la vidéo dans sa recherche.
- **Séries numérotées** (on s'abonne pour voir la suite) : les formats récurrents portent leur numéro dans la pastille de la 1re scène — « CE JOUR-LÀ N°<n> », « BUT REFAIT N°<n> », « CHOIX IMPOSSIBLE N°<n> », « PRONOSTIC N°<n> », avec n = nombre de vidéos de ce format déjà dans `journal.md` + 1.
- **Rotation des appels à l'action** (le `cta` de la dernière scène), d'une vidéo à l'autre, dans cet ordre :
  1. **commentaire** : « Ton choix en commentaire », « Ton score exact en commentaire »… (formule variée) ;
  2. **partage** : « Envoie-la à ton pote qui dit le contraire » / « Envoie-la à un fan de <club ou joueur> » ;
  3. **abonnement**, seulement pour un format récurrent : « Abonne-toi : <format> chaque <jour> » (ex. « Abonne-toi : Ce jour-là chaque mercredi ») ; pour un autre format, passer directement au type suivant.
  Le type de `cta` utilisé est noté dans `journal.md` (colonne `cta`) ; reprendre la rotation après celui de la dernière vidéo publiée.
- Varier les accents de couleur et les `seed` pour que deux vidéos d'affilée ne se ressemblent pas.
- **Voix off** : l'outil existe (`tools/voice.py`, `tools/tts.py`, Action « Voix off ElevenLabs ») mais elle est en test sur @scamoupas. Ne pas mettre de `say` dans les specs de ce compte sans consigne d'Olivier.
- **Signature sonore** : `tools/music.py` ouvre chaque vidéo par deux coups de sifflet (toujours les mêmes), pour qu'on reconnaisse le compte à l'oreille. Ne pas la désactiver (`"signature": false` n'est prévu que pour un test).
- **Musique** : champ `music` obligatoire dans chaque spec, en rotation `stade` → `samba` → `epique` → `electro` → `stade`… Prendre l'ambiance qui suit celle de la dernière spec (dernier fichier de `specs/` par ordre alphabétique, hors `exemples/`) ; si elle n'a pas de champ `music`, commencer par `stade`. Deux vidéos d'affilée n'ont jamais la même ambiance.

## Procédure (à suivre dans l'ordre)

1. **Date.** Si on est après le 4 décembre 2026 : ne rien produire, prévenir Olivier que la campagne est terminée et qu'il peut supprimer la tâche planifiée. Fin.
2. **Créneaux libres.** Charger les outils Metricool (ToolSearch `select:mcp__Metricool_Social_Media_Management__getScheduledPosts,mcp__Metricool_Social_Media_Management__createScheduledPost`), puis `getScheduledPosts` (brandId `7925135`, timezone `Europe/Paris`) sur la journée. Un créneau est occupé quand il a déjà son post TikTok à 12:00 ou 18:00 : on le laisse tel quel. S'il a son post TikTok mais pas son post YouTube, programmer seulement le post YouTube avec la même vidéo (fichier indiqué dans `journal.md`). Si tout est déjà programmé sur les deux réseaux : fin. Les republications YouTube de rattrapage à 09:30 (du 07/11 au 10/11) ne comptent pas comme des créneaux. Si l'heure d'un créneau est déjà passée ou à moins de 20 min : le sauter.
3. **Contexte.** Lire `journal.md` (sujets et joueurs déjà traités : ne pas répéter un sujet ni un quiz, respecter la règle de diversité).
   **Abonnés.** Avec les outils d'analytics Metricool (`getAnalyticsAvailableMetrics` puis `getAnalyticsDataByMetrics`, réseau TikTok), relever le nombre d'abonnés. S'il atteint **10 000**, l'écrire en première ligne du compte rendu (« Seuil des 10 000 abonnés atteint : on peut lancer le format long d'1 minute »), sans rien changer d'autre.
4. **Recherche.** Pour chaque créneau libre, choisir le format (rotation) et le joueur, puis vérifier **chaque chiffre et chaque fait** avec WebSearch + WebFetch du jour (Foot Mercato, FotMob, L'Équipe, sites officiels des clubs/ligues, Transfermarkt). Si deux sources divergent, en choisir une seule pour tous les chiffres de la vidéo et la citer avec la date dans `source`. Un fait non vérifié n'entre pas dans la vidéo. Indices de quiz : faits stables et vérifiables (lieu et année de naissance, clubs, titres).
5. **Spec.** Écrire `specs/AAAA-MM-JJ_HHMM_sujet.json` (format : `tools/SPEC.md`, exemples : `specs/exemples/`). 15 à 25 s, 4 à 6 scènes, `seed` différent à chaque vidéo, `music` selon la rotation ci-dessus.
6. **Contrôle.** `python3 tools/make_video.py <spec> --stills /tmp/stills_<sujet>` puis ouvrir chaque image avec Read : aucun texte coupé, superposé ou trop près des bords ; orthographe et accents corrects ; chiffres identiques aux sources. Corriger et recommencer si besoin.
7. **Rendu.** `python3 tools/make_video.py <spec> videos/AAAA-MM-JJ_HHMM_sujet.mp4`.
8. **Publication des fichiers.** `git checkout main` (la copie de la session peut être sur un commit détaché), puis `git pull --rebase origin main`, `git add videos specs journal.md`, commit, `git push`. Vérifier `curl -sI https://raw.githubusercontent.com/fanoffootball-fof/media/main/videos/<fichier>` → HTTP 200.
9. **Programmation Metricool.** `createScheduledPost` avec `blogId` `7925135`, `date` `AAAA-MM-JJTHH:MM:00+01:00`, et dans `info` :
   ```json
   {"autoPublish": true, "descendants": [], "draft": false, "firstCommentText": "", "hasNotReadNotes": false,
    "media": ["https://raw.githubusercontent.com/fanoffootball-fof/media/main/videos/<fichier>"], "mediaAltText": [],
    "videoCoverMilliseconds": 2500, "providers": [{"network": "tiktok"}],
    "publicationDate": {"dateTime": "AAAA-MM-JJTHH:MM:00", "timezone": "Europe/Paris"},
    "shortener": false, "smartLinkData": {"ids": []}, "text": "<légende>",
    "tiktokData": {"disableComment": false, "disableDuet": false, "disableStitch": false,
                   "privacyOption": "PUBLIC_TO_EVERYONE", "commercialContentThirdParty": false,
                   "commercialContentOwnBrand": false, "title": "<titre court, obligatoire>",
                   "autoAddMusic": false, "isAigc": false}}
   ```
   Légende : 1 phrase d'accroche + une question + 3 à 5 hashtags (≤ 150 caractères). Pour un quiz, ne pas révéler la réponse dans la légende ni dans les hashtags.

   **Puis un 2e post, YouTube Shorts**, même vidéo, même heure : `providers` `[{"network": "youtube"}]`, pas de `tiktokData` ni de `videoCoverMilliseconds`, et :
   ```json
   "text": "<même légende, avec #shorts parmi les hashtags>",
   "youtubeData": {"title": "<titre ≤ 100 caractères qui commence par le nom du joueur ou le sujet, + #shorts>",
                   "type": "short", "privacy": "public", "tags": ["<joueur>", "<club/sélection>", "football"],
                   "category": "SPORTS", "madeForKids": false, "isAiGeneratedContent": false}
   ```
   Pour un quiz, ni le titre ni les tags ne révèlent la réponse. Si l'un des deux posts est refusé, garder l'autre et recopier l'erreur dans le compte rendu.
10. **Journal.** Ajouter une ligne par vidéo dans `journal.md` (date, heure, format, joueur(s), sujet, `cta` : commentaire / partage / abonnement, fichier, sources, id Metricool sous la forme `TT 123 / YT 456`), commit + push.
11. **Compte rendu.** Pour Olivier, une ligne par vidéo programmée : heure, format, joueur, **l'accroche de la 1re scène et la question finale, mot pour mot**. Il peut ainsi les relire et, s'il le souhaite, modifier la légende dans Metricool avant la publication (sans que rien ne l'attende : la publication reste automatique). Puis tout problème rencontré.

## Règles permanentes

- **Jamais** d'images de match, d'extraits YouTube/TV, de photos de joueurs, de logos de clubs ni de musique protégée (la musique est générée par `tools/music.py`).
- Pas de rumeur sur la vie privée, pas de moquerie sur une blessure, pas de propos insultants. Une blessure ne se traite que si elle est officiellement communiquée.
- Ne jamais supprimer ni modifier un post déjà programmé, ni un fichier existant de `videos/`.
- `tools/` ne se modifie que pour corriger un bug bloquant (commit dédié qui explique le correctif).
- En cas d'échec d'un sujet (fait invérifiable, rendu cassé) : se rabattre sur un format intemporel (quiz, « le saviez-vous ») plutôt que laisser le créneau vide.
- Si Metricool ou GitHub sont indisponibles : ne rien inventer, expliquer précisément le blocage dans le compte rendu.
