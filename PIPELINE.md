# Production quotidienne @fanoffootball (TikTok)

Ce document est la procédure suivie chaque matin par la tâche planifiée Claude.
Propriétaire : Olivier. Compte TikTok : `fanoffootball_fof`, publié via Metricool (marque `7925135`, fuseau `Europe/Paris`).

## Campagne

- Du **samedi 7 novembre au vendredi 4 décembre 2026** inclus : **2 vidéos par jour, à 12:00 et 18:00** (heure de Paris). On reste à 2 par jour.
- Objectif : des vidéos **virales** sur le foot, avec **beaucoup de joueurs différents** (pas de joueur favori).
- **Diversité :** deux joueurs différents chaque jour ; un même joueur au plus **2 fois par semaine** (sauf très grosse actu) ; alterner joueurs actuels et légendes. Vérifier dans `journal.md`.
- Les vidéos restent courtes (15 à 25 s). Le format long (≥ 1 min, seul rémunéré par TikTok) ne démarre qu'après accord d'Olivier.

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
| mercredi | actu de la semaine (Ligue des champions, etc.) | « le saviez-vous » (`cards`) |
| jeudi | record ou objectif en cours (`progress`) | quiz « devine le joueur » |
| vendredi | duel entre joueurs actuels | top 3 (`cards` numérotées : records, buts, titres) |
| samedi | stats avant le week-end | quiz « devine le joueur » |
| dimanche | bilan du week-end (buts, notes, records) | sondage / débat entre légendes |

Une **grosse actu** (record, retraite, blessure officielle, transfert officiel, Ballon d'Or…) passe devant la rotation au créneau suivant.

## Recettes virales

- **Accroche dans la 1re seconde** : chiffre choc, question clivante ou affirmation forte (« Le Ballon d'Or le plus volé de l'histoire ? »).
- Des débats qui font réagir sans être insultants : Ballon d'Or contesté, meilleur joueur d'une génération, duel de légendes.
- Toujours finir par une question fermée (2 ou 3 choix) qui pousse au commentaire.
- Varier les accents de couleur et les `seed` pour que deux vidéos d'affilée ne se ressemblent pas.

## Procédure (à suivre dans l'ordre)

1. **Date.** Si on est après le 4 décembre 2026 : ne rien produire, prévenir Olivier que la campagne est terminée et qu'il peut supprimer la tâche planifiée. Fin.
2. **Créneaux libres.** Charger les outils Metricool (ToolSearch `select:mcp__Metricool_Social_Media_Management__getScheduledPosts,mcp__Metricool_Social_Media_Management__createScheduledPost`), puis `getScheduledPosts` (brandId `7925135`, timezone `Europe/Paris`) sur la journée. Un créneau déjà occupé (post à 12:00 ou 18:00) est laissé tel quel. Si les deux le sont : fin. Si l'heure d'un créneau est déjà passée ou à moins de 20 min : le sauter.
3. **Contexte.** Lire `journal.md` (sujets et joueurs déjà traités : ne pas répéter un sujet ni un quiz, respecter la règle de diversité).
   **Abonnés.** Avec les outils d'analytics Metricool (`getAnalyticsAvailableMetrics` puis `getAnalyticsDataByMetrics`, réseau TikTok), relever le nombre d'abonnés. S'il atteint **10 000**, l'écrire en première ligne du compte rendu (« Seuil des 10 000 abonnés atteint : on peut lancer le format long d'1 minute »), sans rien changer d'autre.
4. **Recherche.** Pour chaque créneau libre, choisir le format (rotation) et le joueur, puis vérifier **chaque chiffre et chaque fait** avec WebSearch + WebFetch du jour (Foot Mercato, FotMob, L'Équipe, sites officiels des clubs/ligues, Transfermarkt). Si deux sources divergent, en choisir une seule pour tous les chiffres de la vidéo et la citer avec la date dans `source`. Un fait non vérifié n'entre pas dans la vidéo. Indices de quiz : faits stables et vérifiables (lieu et année de naissance, clubs, titres).
5. **Spec.** Écrire `specs/AAAA-MM-JJ_HHMM_sujet.json` (format : `tools/SPEC.md`, exemples : `specs/exemples/`). 15 à 25 s, 4 à 6 scènes, `seed` différent à chaque vidéo.
6. **Contrôle.** `python3 tools/make_video.py <spec> --stills /tmp/stills_<sujet>` puis ouvrir chaque image avec Read : aucun texte coupé, superposé ou trop près des bords ; orthographe et accents corrects ; chiffres identiques aux sources. Corriger et recommencer si besoin.
7. **Rendu.** `python3 tools/make_video.py <spec> videos/AAAA-MM-JJ_HHMM_sujet.mp4`.
8. **Publication des fichiers.** `git pull --rebase`, `git add videos specs journal.md`, commit, `git push`. Vérifier `curl -sI https://raw.githubusercontent.com/fanoffootball-fof/media/main/videos/<fichier>` → HTTP 200.
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
10. **Journal.** Ajouter une ligne par vidéo dans `journal.md` (date, heure, format, joueur(s), sujet, fichier, sources, id Metricool), commit + push.
11. **Compte rendu.** Terminer par 2 ou 3 lignes pour Olivier : ce qui est programmé, et tout problème rencontré.

## Règles permanentes

- **Jamais** d'images de match, d'extraits YouTube/TV, de photos de joueurs, de logos de clubs ni de musique protégée (le beat est généré par `tools/music.py`).
- Pas de rumeur sur la vie privée, pas de moquerie sur une blessure, pas de propos insultants. Une blessure ne se traite que si elle est officiellement communiquée.
- Ne jamais supprimer ni modifier un post déjà programmé, ni un fichier existant de `videos/`.
- `tools/` ne se modifie que pour corriger un bug bloquant (commit dédié qui explique le correctif).
- En cas d'échec d'un sujet (fait invérifiable, rendu cassé) : se rabattre sur un format intemporel (quiz, « le saviez-vous ») plutôt que laisser le créneau vide.
- Si Metricool ou GitHub sont indisponibles : ne rien inventer, expliquer précisément le blocage dans le compte rendu.
