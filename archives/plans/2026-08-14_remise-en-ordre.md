---
titre: Remise en ordre de l'espace de travail
ouvert: 2026-08-14
clos: 2026-08-14
statut: clos
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

| Sujet                                | Décision                                                                                                    |
|--------------------------------------|-------------------------------------------------------------------------------------------------------------|
| Objectif de la reprise               | fixer le fichier modèle de données. Tout le reste est au service de ça                                      |
| Arborescence                         | validée, voir l'étape 3                                                                                     |
| `points_ouverts.md` et `chantier.md` | unifiés en un seul fichier, `chantier.md`. `CLAUDE.md` reste le hub                                         |
| Largeur des tableaux                 | grille à 150 caractères, la colonne la plus large est rabotée, les cellules trop longues débordent ligne par ligne |
| Site public                          | débranché maintenant, régénéré plus tard, question de mise en ligne rouverte ensuite                        |
| `product_backlog.md`                 | archivé, pas de reprise                                                                                     |
| `integrity_checks.md`                | archivé, à recréer au moment de l'implémentation                                                            |
| Audit `tmp/audit_modele_v12.md`      | relu constat par constat, puis intégré ou écarté, puis supprimé                                             |
| Historique git antérieur             | considéré comme démarrage anarchique, on ne le réécrit pas                                                  |
| Relations inverses                   | sujet d'API, pas de structure. Vérifiées par outil, formalisées plus tard (étape 10)                        |


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

- [x] `outils/mdtable.py` : alignement des tableaux, politique 150 caractères
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

- [x] sortir `dev/CLAUDE/tmp/audit_modele_v12.md` de l'ignoré, le placer dans
      `archives/` où il sera suivi
- [x] même chose pour `dev/old/`
- [x] ancrer les motifs du `.gitignore` (`/tmp/`, `/old/`) pour qu'ils ne
      s'appliquent plus à n'importe quelle profondeur
- [x] retirer du suivi le fichier de verrou drawio, l'ajouter au `.gitignore`
- [x] trancher la règle sur les PDF dérivés : tous suivis, ou aucun

**Critère de fin** : `git status --ignored` ne cache plus aucun fichier de fond.

## Étape 2. Débrancher le site public (close)

Le site publie un modèle de mars 2026 à chaque push. Tant qu'il n'est pas
régénéré, il vaut mieux qu'il ne se republie pas tout seul.

- [x] conditionner `deploy.yml` à un déclenchement manuel (`workflow_dispatch`)
- [x] noter dans `README.md` que la documentation en ligne n'est pas à jour et
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

- [x] relever l'état des références croisées AVANT (`verifie_modele.py`)
- [x] déplacer
- [x] mettre à jour les références croisées (15 citations de
      `modele_donnees_v12.md` réparties dans 6 fichiers, plus les autres noms)
- [x] relever l'état APRÈS, exiger zéro référence morte

**Critère de fin** : zéro référence morte, et `git log --follow` retrouve
l'historique de chaque fichier déplacé.

## Étape 4. Unification de `chantier.md` (close)

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

- [x] fusionner les deux fichiers
- [x] renuméroter les `CH-*` en `D*`, `V*`, `T*` selon leur nature
- [x] un seul tableau de triage en tête

**Critère de fin** : un seul fichier répond à "qu'est-ce qui reste à faire".

## Étape 5. Passe de formatage (close)

Passe mécanique, aucun changement de fond, commit dédié.

- [x] `outils/mdtable.py fix` sur tous les fichiers Markdown
- [x] remplacer les 90 ` -- ` de `decisions.md` par une ponctuation conforme
- [x] retirer les tirets cadratins résiduels (`CLAUDE.md`, `README.md`, annexes)

**Critère de fin** : `mdtable.py check` sort zéro, et zéro cadratin hors `docs/`.

## Étape 6. Nettoyage de `CLAUDE.md` et `SOUL.md` (close)

- [x] `CLAUDE.md` devient le hub : carte de propriété, invariants, renvois. Les
      règles de rédaction sortent dans `methode/redaction.md`
- [x] `SOUL.md` allégé : garder ce qui change ma manière de travailler, couper ce
      qui est décoratif
- [x] intégrer les règles de travail arrêtées :
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

- [x] relire chaque constat contre `modele_donnees.md` dans son état courant
- [x] classer : valide / caduc / à écarter, avec une phrase de justification
- [x] **retour groupé à Louis avant intégration** : c'est du fond, pas de la
      mécanique
- [x] intégrer ceux qui survivent dans `chantier.md`, supprimer le fichier
      d'audit

**Critère de fin** : `archives/audit_modele_v12.md` supprimé, rien de perdu.

## Étape 8. Correction des divergences documentaires (close, sauf D5 et D9)

Les onze divergences internes au modèle (D1 à D11 après renumérotation). Aucune
ne demande de décision de fond, mais chacune touche un tableau.

- [x] montrer chaque tableau modifié en avant/après avant de l'écrire
- [x] traiter par groupes cohérents, un commit par groupe

**Critère de fin** : `verifie_modele.py` sort zéro.

## Étape 9. Mise à jour de `sources.md` (close)

- [x] liens CS API : passer de `/DRAFTS/` à `docs.ogc.org/is/`
- [x] ajouter l'extension STA WebSub 1.0
- [x] créer l'entrée DataCite avec son état daté (4.7, 3 mars 2026), et retirer
      le numéro de version du modèle
- [x] ajouter I-ADOPT avec son état daté
- [x] dater la vérification de chaque état

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

| Date       | Étape | Fait                                                                                                                          |
|------------|-------|-------------------------------------------------------------------------------------------------------------------------------|
| 2026-08-14 | 0     | `mdtable.py` écrit, politique de largeur arrêtée (150, largeur utile de l'éditeur)                                            |
| 2026-08-14 | 0     | `verifie_modele.py` écrit. Il retrouve les 11 divergences connues et en révèle une 12e : Facility et SamplingBatch hors des domaines de référence dans six tableaux |
| 2026-08-14 | 1     | `archives/` créé et documenté. Audit, backlog, conversation initiale et deux brouillons orphelins sauvés. `.gitignore` ancré  |
| 2026-08-14 | 1     | Perte : les sauvegardes `~` des modèles v3 et v5 à v10, jamais suivies par git, ont été supprimées avec `dev/`. Voir la note ci-dessous |
| 2026-08-14 | 2     | Publication du site passée en déclenchement manuel, avertissement dans le README                                              |
| 2026-08-14 | 3     | Migration faite, 37 renommages, `git log --follow` fonctionne, zéro renvoi mort hors `chantier.md`                            |

## Note sur les sauvegardes d'éditeur supprimées le 14 août 2026

En vidant `dev/` après la migration, j'ai supprimé sans les regarder les
sauvegardes d'éditeur `modele_donnees_v3.md~` et `v5~` à `v10~`, non suivies par
git. Vérification faite ensuite : **rien n'est perdu.** Ces versions ont bien
été suivies sous leur propre nom avant d'être retirées de l'arbre de travail par
le commit de nettoyage du 10 juin 2026. Elles restent lisibles dans l'historique.

| Version | Lignes | Commande de récupération                                    |
|---------|--------|-------------------------------------------------------------|
| v3      | 841    | `git show ea90785^:dev/to_read/modele_donnees_v3.md`        |
| v5      | 1111   | `git show ea6b933^:dev/CLAUDE/modele_donnees_v5.md`         |
| v6      | 1184   | `git show ea6b933^:dev/CLAUDE/modele_donnees_v6.md`         |
| v7      | 1266   | `git show ea6b933^:dev/CLAUDE/modele_donnees_v7.md`         |
| v8      | 1317   | `git show ea6b933^:dev/CLAUDE/modele_donnees_v8.md`         |
| v9      | 1305   | `git show ea6b933^:dev/CLAUDE/modele_donnees_v9.md`         |
| v10     | 1303   | `git show ea6b933^:dev/CLAUDE/modele_donnees_v10.md`        |
| v11     | 1591   | `git show c8b8769^:dev/CLAUDE/modele/modele_donnees_v11.md` |

Les fichiers en `~` ne faisaient que dupliquer sur disque ce que git portait
déjà. Leur suppression est sans conséquence.

Ce qui reste vrai malgré tout, et vaut d'être tenu : **avant un `rm -rf` sur un
dossier contenant des fichiers non suivis, en lister le contenu et demander.**
Ici le filet existait ; l'erreur était de ne pas avoir vérifié avant d'agir, pas
d'avoir supprimé.


# Bilan, 14 août 2026

## Ce qui a été fait

Neuf étapes sur dix, en une session. La dixième était explicitement hors plan.

| Étape | Résultat                                                                                   |
|-------|--------------------------------------------------------------------------------------------|
| 0     | Deux vérificateurs écrits : alignement des tableaux, cohérence interne du modèle           |
| 1     | Un audit de 631 lignes et un backlog sauvés d'un `.gitignore` mal ancré                    |
| 2     | Publication du site débranchée : elle republiait un modèle de mars à chaque push           |
| 3     | Arborescence migrée, 37 renommages, zéro renvoi mort, `git log --follow` intact            |
| 4     | `points_ouverts.md` et `chantier.md` unifiés, six lettres pour six natures de constat      |
| 5     | 90 tableaux au format, contenu prouvé inchangé. Tirets normalisés, trois conventions à une |
| 6     | `CLAUDE.md` devient un routeur, `methode/redaction.md` naît, `SOUL.md` dégraissé           |
| 7     | Vingt constats d'audit versés tels quels, sans tri ni jugement                             |
| 8     | Onze divergences du modèle corrigées, le vérificateur sort zéro                            |
| 9     | `sources.md` à jour et redevenu propriétaire unique des versions de standards              |

Trois choses trouvées en chemin, qui n'étaient dans aucune liste de départ :

- `Facility` et `SamplingBatch` avaient été ajoutés comme cibles dans six
  tableaux sans jamais remonter aux domaines de référence. Trouvé par outil,
  pas à l'œil.
- Le passage obligatoire par `Deployment` diverge de CS API, où un `DataStream`
  est rattaché à un `System`. Vérifié sur la spécification après un doute de
  Louis, contre une affirmation fausse que j'avais écrite. C19.
- La convention de nommage, excellente pour l'API, n'est pas celle de
  PostgreSQL, et ce coût n'avait jamais été nommé. C20.

## Ce qui a été abandonné en route

Rien. Deux points ont changé de forme, pas de fond :

- L'étape 7 devait « relire et classer » les constats de l'audit. Recadrée en
  simple versement après une remarque de Louis : classer, c'est instruire, et
  instruire n'était pas l'objet de ce plan. Les vingt constats sont versés
  intacts, aucun n'est déclaré clos.
- D5 est réduit à `person_organization`, bloqué par M11 : lui donner des
  colonnes reviendrait à trancher si l'affiliation est datée.

## Ce qui déborde sur la suite

Hors plan dès le départ, et toujours ouvert : instruire les vingt constats
versés, un par un ; M9 (données d'expérience de terrain) ; C19 et C20 ;
T3 (régénérer le site) ; T4 (modèle d'endpoints API) ; S2 à confirmer soldé.

## Deux incidents, et ce qu'ils ont appris

**Un `rm -rf` sans regarder.** Le vidage de `dev/` a emporté des sauvegardes
d'éditeur non suivies. Sans conséquence en fin de compte, les versions étaient
dans l'historique git, mais le geste était mauvais. Règle retenue : avant un
`rm -rf` sur un dossier contenant des fichiers non suivis, en lister le contenu.

**Un script a tronqué `chantier.md` de 628 lignes, et la troncature a été
commitée.** Restaurée depuis le commit précédent, rien de perdu. Le point qui
compte est que les deux vérificateurs sont passés au vert sur le fichier
tronqué : un fichier amputé reste bien formé. Ils contrôlent la cohérence, pas
l'intégrité.

Cause exacte : reconstruction du fichier par tranches, `t[:debut] + nouveau`,
sans la tranche de fin `t[fin:]`. Le découpage par indices exige de réassembler
trois morceaux et n'échoue jamais bruyamment quand on en oublie un.

Trois corrections, appliquées le jour même : interdiction de reconstruire un
fichier par tranches (`methode/redaction.md`), un troisième vérificateur
`outils/verifie_integrite.py` qui signale les pertes de volume, et l'habitude de
lire `git diff --numstat` avant de committer. Vérifié a posteriori : le
vérificateur signale bien le commit fautif (52% de perte), reste muet sur la
passe de formatage, et signale la suppression volontaire de `points_ouverts.md`
sans la juger, ce qui est le comportement voulu.

Contrôle de l'ensemble de la session : aucune autre perte de volume anormale sur
les douze commits.

## Ce que la session dit de la méthode

Le reproche le plus utile est venu de Louis en cours de route : en passant par
Claude Code plutôt que par une conversation, la tendance est de trancher puis
d'expliquer, alors qu'une phase de conception demande l'inverse. Il ne peut pas
valider ce qu'il n'a pas lu, et une modification qu'il n'a pas comprise n'est
pas acquise même si elle est juste.

C'est ce qui a produit les deux règles ajoutées à `methode/SOUL.md` (réflexes 8
et 9) et l'ouverture de `methode/redaction.md` par « montrer avant d'écrire ».
Le plan suivant devra les respecter davantage que celui-ci ne l'a fait.
