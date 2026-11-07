# Production quotidienne @scamoupas (TikTok + Instagram)

Ce document est la procédure suivie chaque jour par la tâche planifiée Claude.
Propriétaire : Olivier. Comptes TikTok et Instagram : `@scamoupas` (Instagram en Reels), publiés via **Buffer** (forfait gratuit) par la GitHub Action
`.github/workflows/buffer.yml`. Fuseau : `Europe/Paris`.

## Concept

« **Arnaque ou pas ?** » : un vrai type de message (SMS, mail, appel) s'affiche, le spectateur a 3 secondes pour
trancher, puis les indices sont entourés et expliqués. Le compte est tenu par un expert en sécurité : ton clair,
précis, jamais moqueur. Deux moteurs : **les partages** (« envoie-la à tes parents ») et **les commentaires**
(chacun donne sa réponse avant la révélation).

## Rythme

- **Mode lancement, jusqu'au lundi 30 novembre 2026 inclus : 2 vidéos par jour, à 12:30 et 19:00** (heure de Paris).
  Un compte neuf grandit plus vite avec 1 à 2 vidéos par jour dans une niche bien définie.
- **À partir du mardi 1er décembre 2026 : 1 vidéo par jour à 19:00**, sauf nouvelle consigne d'Olivier.
- Vidéos de 20 à 30 s. Choix d'Olivier : **pas de format long (≥ 1 min) tant que les conditions de monétisation
  ne sont pas remplies** (10 000 abonnés et 100 000 vues sur 30 jours). D'ici là, tout l'effort va à la croissance :
  partages et **conversion en abonnés**.
- Créneau de 12:30 : le sujet de la rotation du jour. Créneau de 19:00 : « le piège du moment » (vague récente
  documentée par une source officielle ou la presse) ; s'il n'y en a pas, un grand classique pas traité depuis 30 jours.

## Recettes de croissance (à appliquer à chaque vidéo)

- **Accroche en moins de 1,5 s** : scène `title` de `dur: 1.5`, qui nomme le piège avec les mots que les gens
  tapent dans la recherche TikTok (« LE SMS DU LIVREUR », « LE FAUX CONSEILLER »). Le message arrive juste après.
- **Série numérotée** : `kicker` de la scène titre = « ARNAQUE OU PAS ? N°<n> » (n = nombre de lignes du journal + 1),
  pour donner envie de s'abonner et de voir les autres numéros. Jamais « ARNAQUE N° » seul : ça trahirait la réponse
  des vidéos dont le verdict est « VRAI ».
- **Légende qui commence par le mot-clé recherché** (« Arnaque au SMS du livreur : … »), puis une question ou un
  appel au partage, puis 3 à 5 hashtags dont `#arnaque` et un hashtag précis (`#colis`, `#banque`…).
- **Musique variée et légère** : clé `music` de la spec, en rotation `lofi`, `pop`, `house`, `funk`, `marimba`.
  Jamais la même ambiance que la vidéo publiée juste avant ou juste après (voir `journal.md` et `specs/`).
  Ton du compte : rassurant et malin, jamais angoissant.
- **Dernière scène : rotation des appels à l'action**, d'une vidéo à l'autre, dans cet ordre (le partage aux
  proches est le levier le plus fort de la niche : il revient une fois sur deux) :
  1. **parents** : `poll` « TES PARENTS AURAIENT CLIQUÉ ? » OUI / NON avec `cta` « Envoie-la-leur maintenant » ;
  2. **commentaire** : `poll` « TU L'AS DÉJÀ REÇU ? » OUI / NON avec `cta` « Raconte en commentaire, je décode » ;
  3. **parents** : `poll` « TU AURAIS CLIQUÉ ? » OUI / NON avec `cta` « Envoie-la à tes parents » ;
  4. **abonnement** : `poll` « TU AURAIS CLIQUÉ ? » OUI / NON avec `cta` « Abonne-toi : un nouveau piège chaque jour ».
  Le type utilisé est noté dans `journal.md` (`[cta : …]` à la fin de la colonne sujet) ; reprendre la rotation
  après celui de la dernière vidéo publiée (sans repère : commencer par 1).
- **Signature sonore** : `tools/music.py` ouvre chaque vidéo par deux notes de marimba qui montent (toujours le
  même motif), pour qu'on reconnaisse le compte à l'oreille. Ne pas la désactiver (`"signature": false` n'est prévu
  que pour un test).
- Les commentaires transmis par Olivier (messages suspects reçus par les abonnés) passent en priorité dans la
  rotation, toujours anonymisés et vérifiés comme le reste.

## Rotation des sujets

| jour | sujet |
|---|---|
| lundi | SMS (colis, amende, carte Vitale, CPF, Crit'Air…) |
| mardi | appel téléphonique (faux conseiller bancaire, numéro usurpé, faux support technique) |
| mercredi | **« VRAI ou ARNAQUE »** : un message légitime, ou un vrai message suivi du piège (cf. `faux_conseiller.json`) |
| jeudi | mail (impôts, énergie, remboursement, colis, faux recrutement) |
| vendredi | achat / vente en ligne (Vinted, Leboncoin, faux site, investissement miracle) |
| samedi | l'alerte de la semaine (vague signalée par une source officielle ou la presse) |
| dimanche | arnaque aux proches (« Maman, j'ai changé de numéro », voix clonée par IA, faux ami en difficulté) |

Une **alerte officielle récente** (Cybermalveillance, ministère de l'Intérieur, police/gendarmerie, banque de France,
AMF…) passe devant la rotation. Au moins **1 vidéo sur 4 a pour verdict « VRAI »** (au moins une partie du message
est légitime), pour que répondre « arnaque » à chaque fois ne suffise pas.

## Voix off (test, seulement si la consigne de la tâche quotidienne dit « voix off activée »)

Voix clonée d'Olivier (ElevenLabs), générée par la GitHub Action « Voix off ElevenLabs » avec ses secrets
`ELEVENLABS_API_KEY` et `ELEVENLABS_VOICE_ID`. Sans la mention « voix off activée » dans la consigne du jour : aucune
réplique `say`, rien ne change.

- **Une vidéo sur deux**, en alternance d'une vidéo à l'autre, pour comparer avec et sans voix. Repère : `[voix]` à la
  fin de la colonne sujet de `journal.md` (après le `[cta : …]`).
- **Ton** : l'expert sécu qui parle à un proche, tutoiement, calme et rassurant, jamais alarmiste. La voix **ajoute**
  quelque chose à l'écran (le pourquoi, le réflexe) : elle ne relit pas le texte affiché.
- **Répliques** (champ `say` des scènes, voir `tools/SPEC.md`) : scène titre ≤ 6 mots (« Arnaque ou pas ? Le SMS du
  livreur. ») ; **aucune réplique sur la scène du compte à rebours** (le spectateur réfléchit) ; 1 à 2 phrases courtes
  par scène d'explication ; la dernière scène dit l'appel à l'action. 300 à 450 caractères en tout par vidéo (environ
  1 crédit ElevenLabs par caractère).
- **Écrire pour l'oreille** : nombres en lettres, pas d'abréviation ni de symbole, jamais d'adresse web ni de numéro
  prononcés.
- **Déroulé** (en plus de la procédure) : après l'étape 4, `git add specs/<spec>` + commit + `git pull --rebase` +
  `git push` de la spec seule ; l'Action génère `voice/<nom de la spec>/`. Attendre (jusqu'à 5 min, outil Monitor et
  boucle `until` sur `git pull -q && ls voice/<nom>/manifest.json voice/<nom>/erreur.txt`) que `manifest.json` contienne
  toutes les scènes, ou que `erreur.txt` apparaisse. Puis contrôle (étape 5) et rendu (étape 6) : `make_video.py`
  place la voix et baisse la musique dessous.
- **En cas d'erreur** (`erreur.txt`, Action en échec ou plus de 5 min) : retirer les `say` de la spec, faire la vidéo
  sans voix, et recopier le message d'erreur dans le compte rendu.
- **Mention IA** : dans le fichier de `queue/` d'une vidéo narrée, ajouter `"ai_generated": true` (la GitHub Action
  active alors l'étiquette « contenu généré par IA » sur TikTok et Instagram).

## Procédure (à suivre dans l'ordre)

1. **Créneaux.** Selon le rythme ci-dessus, lister les créneaux du jour (12:30 et 19:00 en mode lancement, 19:00
   ensuite). Laisser de côté un créneau qui a déjà un fichier dans `queue/` (`AAAA-MM-JJ_HHMM_*.json`) ou qui
   tombe dans moins de 90 min. S'il n'en reste aucun : fin (rien à faire). Sinon, faire les étapes 2 à 10 pour
   chaque créneau restant.
2. **Contexte.** Lire `journal.md` : ne pas refaire un sujet traité dans les 30 derniers jours (sauf nouvelle vague
   documentée), respecter la proportion de « VRAI ».
3. **Recherche.** Choisir le sujet (rotation, ou alerte récente), puis vérifier **chaque fait** avec WebSearch +
   WebFetch du jour, en priorité : cybermalveillance.gouv.fr, interieur.gouv.fr, service-public.fr, impots.gouv.fr,
   ameli.fr, antai.gouv.fr, banque-france.fr, amf-france.org, inc-conso.fr, puis la presse nationale. Noter la source
   citée dans la vidéo (`source`). Un fait non vérifié n'entre pas dans la vidéo. Pour un verdict « VRAI », la
   source doit décrire à quoi ressemble le message légitime.
4. **Spec.** Écrire `specs/AAAA-MM-JJ_HHMM_sujet.json` (format : `tools/SPEC.md`, exemples : `specs/exemples/`).
   Structure : accroche (1,5 s) → message + question + compte à rebours → indices + verdict → explication des
   indices → bon réflexe → question finale qui fait commenter (voir « Recettes de croissance »). `seed` différent
   à chaque vidéo.
5. **Contrôle.** `python3 tools/make_video.py <spec> --stills <scratchpad>/stills_<sujet>` puis ouvrir chaque image
   avec Read : aucun texte coupé, superposé ou trop près des bords ; orthographe et accents corrects ; liens
   désamorcés `[.]` ; numéros masqués. Corriger et recommencer si besoin.
6. **Rendu.** `python3 tools/make_video.py <spec> videos/AAAA-MM-JJ_HHMM_sujet.mp4`.
7. **File d'attente.** Écrire `queue/AAAA-MM-JJ_HHMM_sujet.json` :
   ```json
   {"video": "videos/AAAA-MM-JJ_HHMM_sujet.mp4",
    "text": "<légende>",
    "due": "AAAA-MM-JJTHH:MM:00+01:00",
    "services": ["tiktok", "instagram"],
    "status": "pending"}
   ```
   Légende : voir « Recettes de croissance » ; **5 hashtags au maximum** (limite Buffer pour TikTok, et limite d'Instagram),
   ≤ 150 caractères. Ne jamais donner la réponse (« arnaque » / « vrai ») dans la légende.
   Fuseau : `+01:00` en hiver, `+02:00` entre le dernier dimanche de mars et le dernier dimanche d'octobre.
8. **Publication.** `git config user.name Claude && git config user.email noreply@anthropic.com` (commits vérifiés),
   puis `git pull --rebase`, `git add videos specs queue journal.md`, commit, `git push`. La GitHub
   Action programme le post dans Buffer et réécrit le fichier de `queue/` (`status` : `scheduled` ou `error`).
9. **Vérification.** Attendre le passage de l'Action (jusqu'à 5 min) avec l'outil Monitor et une boucle
   `until` sur `git pull -q && grep -q '"status": "pending"' queue/<fichier>` (sans `sleep` au premier plan).
   - `scheduled` : c'est bon.
   - `error` : lire le message ; si la cause est corrigeable (heure passée, faute dans le fichier), corriger,
     remettre `"status": "pending"` et repousser. Sinon, le décrire dans le compte rendu.
10. **Journal.** Ajouter une ligne dans `journal.md` (date, heure, sujet terminé par `[cta : parents / commentaire /
    abonnement]`, verdict, fichier, sources, statut Buffer), commit + push.
11. **Compte rendu.** Pour Olivier, une ligne par vidéo programmée : heure, sujet, verdict, réseaux, **l'accroche de
    la scène titre et la question finale, mot pour mot**. Il peut ainsi les relire et, s'il le souhaite, modifier la
    légende dans Buffer avant la publication (rien ne l'attend : la publication reste automatique). Puis tout
    problème rencontré.

## Instagram

- Chaque vidéo part **en même temps sur TikTok et en Reel sur Instagram** (`"services": ["tiktok", "instagram"]`),
  avec la même légende.
- Buffer gratuit : **10 posts programmés au maximum par réseau**. Les fichiers `queue/*_ig_*.json` sont des
  republications Instagram (vidéos sorties avant l'ajout d'Instagram) ; un `"status": "hold"` attend une place.
- Si Buffer refuse le post Instagram seulement, le fichier passe en `error` : le dire dans le compte rendu
  (ne pas recréer le post TikTok déjà programmé : créer un fichier `_ig_` avec `"services": ["instagram"]`).

## Règles permanentes

- **Expéditeurs génériques** (« TA BANQUE », « LIVRAISON », numéro masqué) : jamais de logo ni de faux message
  attribué nommément à une vraie entreprise. On peut écrire dans l'explication qui est imité (« se fait passer pour
  l'Assurance Maladie »).
- **Liens toujours désamorcés** (`[.]`) et inventés ; jamais une vraie adresse frauduleuse ni une vraie adresse
  officielle dans le faux message. Numéros toujours masqués (`•• ••`).
- On apprend à **reconnaître** une arnaque, jamais à la monter : pas de mode opératoire détaillé côté escroc.
- Pas de moquerie des victimes ni des personnes âgées.
- Ne jamais supprimer ni modifier un post déjà programmé, ni un fichier existant de `videos/`.
- `tools/` ne se modifie que pour corriger un bug bloquant (commit dédié qui explique le correctif).
- Si Buffer, GitHub ou le rendu sont indisponibles : ne rien inventer, expliquer précisément le blocage dans le
  compte rendu.
