---
titre: Remise en ordre de l'espace de travail
ouvert: 2026-08-14
clos:
statut: en cours
---

# Ce que ce fichier est

Le **plan de travail courant**. Un seul à la fois, toujours nommé `plan.md`,
toujours à la racine. Il donne l'ordre dans lequel on traite les choses, et
pourquoi cet ordre. Il ne possède aucune vérité de fond : chaque étape renvoie
aux fichiers qui la portent.

Il ne remplace pas `chantier.md`, qui possède les constats. Ici il n'y a que
la séquence.

## Cycle de vie d'un plan

Un plan n'est jamais supprimé : une fois toutes ses étapes closes, il est
**archivé daté**, pour que les raisons d'un choix de séquencement restent
retrouvables quand on se demandera, dans deux ans, pourquoi telle chose a été
faite avant telle autre.

```
plan.md                                          le plan courant, un seul
archives/plans/2026-08-14_remise-en-ordre.md     les plans clos, datés
```

Clôture d'un plan, trois gestes :

1. renseigner `clos:` et passer `statut:` à `clos` dans l'en-tête ;
2. écrire une section *Bilan* en fin de fichier : ce qui a été fait, ce qui a
   été abandonné en route et pourquoi, ce qui a débordé sur le plan suivant ;
3. `git mv plan.md archives/plans/AAAA-MM-JJ_titre-en-kebab-case.md`, la date
   étant celle d'**ouverture**, pour que les plans se trient dans l'ordre où le
   travail a commencé.

Pas de fichier d'index des plans archivés : le nom des fichiers et leur en-tête
suffisent, et un index serait une deuxième vérité à tenir à jour. `CLAUDE.md`
porte un simple renvoi vers le dossier.


# Ce qui est acté

Décisions prises dans l'échange du 14 août 2026, à ne pas rouvrir sans raison
neuve.

| Sujet                                | Décision                                                                             |
|--------------------------------------|--------------------------------------------------------------------------------------|
| Objectif de la reprise               | fixer le fichier modèle de données. Tout le reste est au service de ça               |
| Arborescence                         | validée, voir l'étape 3                                                              |
| `points_ouverts.md` et `chantier.md` | unifiés en un seul fichier, `chantier.md`. `CLAUDE.md` reste le hub                  |
| Largeur des tableaux                 | grille à 153 caractères, seule la dernière colonne déborde ligne par ligne           |
| Site public                          | débranché maintenant, régénéré plus tard, question de mise en ligne rouverte ensuite |
| `product_backlog.md`                 | archivé, pas de reprise                                                              |
| `integrity_checks.md`                | archivé, à recréer au moment de l'implémentation                                     |
| Audit `tmp/audit_modele_v12.md`      | relu constat par constat, puis intégré ou écarté, puis supprimé                      |
| Historique git antérieur             | considéré comme démarrage anarchique, on ne le réécrit pas                           |
| Relations inverses                   | sujet d'API, pas de structure. Vérifiées par outil, formalisées plus tard (étape 10) |


# Ordre des étapes, et pourquoi cet ordre

Trois principes de séquencement :

1. **Sauver avant de bouger.** Rien ne se déplace tant que ce qui risque d'être
   perdu n'est pas dans un commit.
2. **Mécanique avant fond.** Les passes qui touchent beaucoup de lignes sans rien
   décider (déplacements, formatage) passent avant les corrections de contenu,
   pour que les diffs de fond restent lisibles.
3. **Un commit, un sujet.** Un déplacement de fichier et une modification de son
   contenu ne sont jamais dans le même commit : git perd la trace du renommage et
   le diff devient illisible.


# Étapes

## Étape 0. Outillage, garde-fous (close)

Écrire les vérificateurs avant de toucher au contenu, pour que chaque étape
suivante soit contrôlable.

- [x] `outils/mdtable.py` : alignement des tableaux, politique 153 caractères
- [x] `outils/verifie_modele.py` : cinq contrôles sur le modèle
      - cible de FK inexistante
      - mention `(FK x)` dont la colonne n'existe pas dans la table citée
      - valeur de discriminant TPC hors du domaine déclaré
      - entité portant un discriminant sans figurer dans l'index de son pattern
      - référence croisée entre fichiers pointant un fichier absent

**Critère de fin** : les deux outils tournent et reproduisent les constats déjà
identifiés (D1 à D11). Un outil qui ne retrouve pas un défaut connu ne sert à
rien.

## Étape 1. Sauver ce qui risque de se perdre (close)

- [ ] sortir `dev/CLAUDE/tmp/audit_modele_v12.md` de l'ignoré, le placer dans
      `archives/` où il sera suivi
- [ ] même chose pour `dev/old/`
- [ ] ancrer les motifs du `.gitignore` (`/tmp/`, `/old/`) pour qu'ils ne
      s'appliquent plus à n'importe quelle profondeur
- [ ] retirer du suivi le fichier de verrou drawio, l'ajouter au `.gitignore`
- [ ] trancher la règle sur les PDF dérivés : tous suivis, ou aucun

**Critère de fin** : `git status --ignored` ne cache plus aucun fichier de fond.

## Étape 2. Débrancher le site public (close)

Le site publie un modèle de mars 2026 à chaque push. Tant qu'il n'est pas
régénéré, il vaut mieux qu'il ne se republie pas tout seul.

- [ ] conditionner `deploy.yml` à un déclenchement manuel (`workflow_dispatch`)
- [ ] noter dans `README.md` que la documentation en ligne n'est pas à jour et
      renvoyer vers le modèle source

**Critère de fin** : un push sur `main` ne republie plus rien.

## Étape 3. Migration de l'arborescence (close)

Un seul commit, uniquement des déplacements, aucune modification de contenu sauf
les chemins cités.

```
bdoh-doc/
├── CLAUDE.md              hub, à la racine pour être lu d'office
├── README.md  LICENSE  .gitignore  mkdocs.yml  plan.md
├── .github/workflows/deploy.yml
│
├── modele/
│   ├── modele_donnees.md      (ex modele_donnees_v12.md, version en en-tête YAML)
│   ├── decisions.md           (ex decisions_index.md)
│   ├── chantier.md            (ex points_ouverts.md + chantier.md, unifiés)
│   └── sources.md
│
├── methode/
│   ├── SOUL.md
│   ├── redaction.md           (règles de rédaction extraites de CLAUDE.md)
│   ├── notes.md               (ex note.md, carnet de Louis, je n'y touche pas)
│   └── prompts/
│       └── demarrage.md       (ex start_prompt.txt)
│
├── annexes/
│   ├── tpc_philosophie.md
│   └── tpc_philosophie_synthese.md   (la v2, la v1 part en archives)
│
├── references/
│   ├── lectures/              PDF et présentations d'autres instituts
│   ├── jeux_exemple/          données d'exemple
│   ├── echanges/              correspondance
│   └── relecture/             PDF exportés pour relecture
│
├── schemas/                   drawio, png, svg
├── outils/                    mdtable.py, verifie_modele.py
├── archives/                  états anciens conservés sciemment, suivis par git
└── docs/                      site public mkdocs
```

- [ ] relever l'état des références croisées AVANT (`verifie_modele.py`)
- [ ] déplacer
- [ ] mettre à jour les références croisées (15 citations de
      `modele_donnees_v12.md` réparties dans 6 fichiers, plus les autres noms)
- [ ] relever l'état APRÈS, exiger zéro référence morte

**Critère de fin** : zéro référence morte, et `git log --follow` retrouve
l'historique de chaque fichier déplacé.

## Étape 4. Unification de `chantier.md`

Un seul fichier pour tout ce qui reste ouvert ou à faire, avec un jeu de lettres
unique. `CLAUDE.md` est le hub qui y renvoie.

| Lettre | Nature                                | Se résout par               |
|--------|---------------------------------------|-----------------------------|
| `S`    | risque structurel                     | décision de fond, puis ADR  |
| `M`    | point de modélisation                 | décision de fond, puis ADR  |
| `C`    | constat concret et vérifiable         | décision de fond, puis ADR  |
| `D`    | divergence documentaire               | édition, sans décision      |
| `V`    | veille standards                      | mise à jour de `sources.md` |
| `T`    | travaux (outillage, publication, API) | exécution                   |

- [ ] fusionner les deux fichiers
- [ ] renuméroter les `CH-*` en `D*`, `V*`, `T*` selon leur nature
- [ ] un seul tableau de triage en tête

**Critère de fin** : un seul fichier répond à "qu'est-ce qui reste à faire".

## Étape 5. Passe de formatage

Passe mécanique, aucun changement de fond, commit dédié.

- [ ] `outils/mdtable.py fix` sur tous les fichiers Markdown
- [ ] remplacer les 90 ` -- ` de `decisions.md` par une ponctuation conforme
- [ ] retirer les tirets cadratins résiduels (`CLAUDE.md`, `README.md`, annexes)

**Critère de fin** : `mdtable.py check` sort zéro, et zéro cadratin hors `docs/`.

## Étape 6. Nettoyage de `CLAUDE.md` et `SOUL.md`

- [ ] `CLAUDE.md` devient le hub : carte de propriété, invariants, renvois. Les
      règles de rédaction sortent dans `methode/redaction.md`
- [ ] `SOUL.md` allégé : garder ce qui change ma manière de travailler, couper ce
      qui est décoratif
- [ ] intégrer les règles de travail arrêtées :
      1. montrer le tableau avant de l'écrire
      2. ne pas confondre "tu ne comprends pas" et "j'ai tort"
      3. une passe un sujet, et signaler quand le contexte dérive ou doit être vidé
      4. l'alignement est garanti par outil, pas par vigilance
      5. toute modification du modèle cite ce qui l'autorise
      6. le site public suit le modèle, ou il est débranché

**Critère de fin** : aucune règle n'est écrite à deux endroits.

## Étape 7. Relecture de l'audit claude.ai

Les 18 constats (C7 à C18, M10 à M14, S6) n'ont jamais été relus. Ils sont à
vérifier un par un contre le modèle actuel : toujours valides, déjà résolus
depuis, ou à écarter.

- [ ] relire chaque constat contre `modele_donnees.md` dans son état courant
- [ ] classer : valide / caduc / à écarter, avec une phrase de justification
- [ ] **retour groupé à Louis avant intégration** : c'est du fond, pas de la
      mécanique
- [ ] intégrer ceux qui survivent dans `chantier.md`, supprimer le fichier
      d'audit

**Critère de fin** : `archives/audit_modele_v12.md` supprimé, rien de perdu.

## Étape 8. Correction des divergences documentaires

Les onze divergences internes au modèle (D1 à D11 après renumérotation). Aucune
ne demande de décision de fond, mais chacune touche un tableau.

- [ ] montrer chaque tableau modifié en avant/après avant de l'écrire
- [ ] traiter par groupes cohérents, un commit par groupe

**Critère de fin** : `verifie_modele.py` sort zéro.

## Étape 9. Mise à jour de `sources.md`

- [ ] liens CS API : passer de `/DRAFTS/` à `docs.ogc.org/is/`
- [ ] ajouter l'extension STA WebSub 1.0
- [ ] créer l'entrée DataCite avec son état daté (4.7, 3 mars 2026), et retirer
      le numéro de version du modèle
- [ ] ajouter I-ADOPT avec son état daté
- [ ] dater la vérification de chaque état

**Critère de fin** : aucune version de standard n'est écrite ailleurs que dans
`sources.md`.

## Étape 10. Chantiers ultérieurs, hors de ce plan

Notés ici pour ne pas les perdre, pas pour les traiter maintenant.

- **Modèle d'endpoints API** (`modele_api.md`). Les champs *Utilisé par* et
  *Relations inverses* du modèle décrivent de la navigation, pas de la structure
  SQL : c'est de l'API. Ils restent dans le modèle comme index dérivé, vérifié
  par outil, et le vrai modèle d'API se construit par-dessus, dans son fichier.
- **Projection I-ADOPT** de la décomposition `Property` / `Unit` /
  `aggregationStatistic` / milieu, en lien avec l'alignement Theia/OZCAR déjà
  mené sur le dépôt CARD. Ouvre peut-être un `M*`.
- **Régénération du site public**, puis décision sur sa mise en ligne.


# Journal

| Date       | Étape | Fait                                                                                                                             |
|------------|-------|----------------------------------------------------------------------------------------------------------------------------------|
| 2026-08-14 | 0     | `mdtable.py` écrit, politique de largeur 153 arrêtée                                                                             |
| 2026-08-14 | 0     | `verifie_modele.py` écrit. Il retrouve les 11 divergences connues et en révèle une 12e : Facility et SamplingBatch hors des domaines de référence dans six tableaux |
| 2026-08-14 | 1     | `archives/` créé et documenté. Audit, backlog, conversation initiale et deux brouillons orphelins sauvés. `.gitignore` ancré     |
| 2026-08-14 | 1     | Perte : les sauvegardes `~` des modèles v3 et v5 à v10, jamais suivies par git, ont été supprimées avec `dev/`. Voir la note ci-dessous |
| 2026-08-14 | 2     | Publication du site passée en déclenchement manuel, avertissement dans le README                                                 |
| 2026-08-14 | 3     | Migration faite, 37 renommages, `git log --follow` fonctionne, zéro renvoi mort hors `chantier.md`                               |

## Note sur la perte du 14 août 2026

En vidant `dev/` après la migration, j'ai supprimé sans les regarder les
sauvegardes d'éditeur `modele_donnees_v3.md~`, `v5~` à `v10~`. Elles n'étaient
suivies par aucun commit : elles sont irrécupérables depuis le dépôt.

Ce qui subsiste de ces états : les 65 ADR de `modele/decisions.md`, qui portent
le raisonnement de chaque transition, `archives/bdoh_model_v0.txt` qui capture
un état très antérieur, et les exports PDF de `references/relecture/`. Ce qui
est perdu : la possibilité de différer mot à mot un état intermédiaire contre la
version courante.

Règle qui en découle, à appliquer désormais : **avant tout `rm -rf` d'un dossier
contenant des fichiers non suivis, en lister le contenu et décider fichier par
fichier.** Un fichier ignoré par git n'est pas un fichier sans valeur, c'est un
fichier sans filet.
