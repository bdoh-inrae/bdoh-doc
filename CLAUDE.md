# CLAUDE.md : routeur du projet BDOH

## Rôle de ce fichier

Ce fichier ne contient **aucune vérité de fond**. Il donne le contexte minimal,
dit qui possède quoi, rappelle les invariants à ne pas casser sans décision, et
renvoie au reste. Rien de ce qui est ici ne fait autorité sur autre chose.

Règle de propriété, valable pour tous les fichiers du projet : **une information
a un seul propriétaire, les autres fichiers pointent et ne recopient pas.**
Quand une information vit à deux endroits, elle finit par diverger ; c'est la
double vérité que le modèle lui-même s'interdit. Le projet en a déjà fait les
frais : la version de DataCite était figée dans le modèle alors que
`modele/sources.md` en est le propriétaire, et elle a vieilli sans que personne
le voie.


## Contexte du projet

BDOH (Base de Données des Observatoires Hydrologiques) est un système
d'information développé à INRAE UR RiverLy pour la gestion et le partage de
données issues d'une dizaine d'observatoires environnementaux français, en lien
avec les réseaux OZCAR et Theia.

Le modèle repose sur une base TimescaleDB et deux couches : une couche IoT brute
(STA 1.1) et une couche métier BDOH (données validées et dérivées), cousues par
`TimeSeriesSource`. Il s'aligne sur plusieurs standards, dont la liste et l'état
daté vivent dans `modele/sources.md` et nulle part ailleurs.

**Statut : conception, rien d'implémenté.** Aucune base ne tourne, aucun schéma
SQL n'est appliqué. Le travail porte sur les fichiers Markdown eux-mêmes.
Conséquence directe : une incohérence relevée maintenant se corrige en éditant
le modèle, sans coût de migration. C'est le bon moment pour lever les
divergences ; ce ne le sera plus une fois l'implémentation commencée.


## Qui possède quoi

| Fichier                               | Possède, en propre                                                                                         |
|---------------------------------------|------------------------------------------------------------------------------------------------------------|
| `modele/modele_donnees.md`            | la **structure** : entités, colonnes, patterns TPC, nommage, scopes d'unicité, enums SQL, suppression logique, Keyword |
| `modele/decisions.md`                 | le **pourquoi** : ADR-001 à ADR-065, alternatives écartées                                                 |
| `modele/chantier.md`                  | **tout ce qui reste à faire** : constats (C), modélisation (M), structure (S), divergences (D), veille (V), travaux (T) |
| `modele/sources.md`                   | les **standards externes**, leur état daté, la table source vers entités                                   |
| `methode/SOUL.md`                     | la **posture** : neuf réflexes de travail                                                                  |
| `methode/redaction.md`                | les **règles d'écriture** : formalisme, tableaux, ponctuation, contrôles                                   |
| `methode/notes.md`                    | le **carnet de Louis**. Lecture libre, écriture seulement sur demande explicite                            |
| `annexes/tpc_philosophie_synthese.md` | la **justification philosophique** du pattern TPC                                                          |
| `archives/plans/`                     | les **plans de travail**, datés de leur ouverture. Le plan courant, s'il y en a un, est un fichier plan.md à la racine |
| `outils/`                             | les **vérificateurs** : alignement des tableaux, cohérence interne du modèle                               |
| `archives/`                           | les **états anciens** conservés sciemment. Aucun ne fait autorité, voir son README                         |

`modele/modele_donnees.md` est la source de vérité de la base ; l'API s'en
déduit. Les relations inverses absentes des tableaux y réapparaissent comme
endpoints de navigation (ADR-028), et leur formalisation propre est un chantier
ouvert (T4 dans `modele/chantier.md`).


## Par où commencer

1. `methode/SOUL.md`, la posture. Le plus important pour bien démarrer.
2. Ce fichier, pour la carte et les invariants.
3. `modele/modele_donnees.md` en entier avant de modifier quoi que ce soit.
4. `modele/decisions.md`, pour comprendre pourquoi avant de rouvrir.
5. `modele/chantier.md`, pour savoir ce qui reste ouvert.
6. `modele/sources.md`, pour les standards. Vérifier leur état en ligne plutôt
   que de le supposer : ils évoluent, les connaissances d'entraînement
   vieillissent.

Un ADR est un **instantané daté**. Quand il énumère des tables ou des valeurs,
cette liste reflète l'état au moment de la décision. La liste courante fait foi
dans le modèle ; on ne resynchronise pas un ADR a posteriori.


## Invariants à ne pas casser sans ADR

Rappels, pas spécifications. La spec est dans le modèle, le pourquoi dans les
ADR. Ne pas modifier l'un de ces points sans ouvrir une décision.

1. **Deux couches sur une base.** IoT brute (`Datastream`, `Observation`) et
   métier (`TimeSeries`, `ValidatedObservation`, `TransformedTimeSeries`). La
   FOI est absente de la couche IoT (ADR-014, ADR-038).
2. **TimeSeries = contrat analytique.** Changer un paramètre analytique crée une
   nouvelle TimeSeries. Un changement de capteur est une nouvelle ligne
   `TimeSeriesSource`, pas une nouvelle série (ADR-002, ADR-048).
3. **Un seul pattern TPC, cinq déclinaisons** (resource, anchor, agent, series,
   system). Intégrité applicative, pas de FK native (ADR-047, ADR-062).
4. **Cinq entités d'instrumentation** (Sensor, Actuator, Sampler, Platform, Kit),
   reliées à Deployment récursif par le TPC system. Remplace l'ancienne fusion
   System et InstrumentUsage (ADR-062, remplace ADR-037).
5. **Vocabulaires évolutifs via quadriptyque Keyword**, jamais via enum SQL.
   L'enum SQL est réservé aux discriminants qui satisfont les trois conditions
   de la grille (ADR-030, ADR-058) : le code branche sur la valeur, l'ensemble
   est fermé, ajouter une valeur est un acte de développement.
6. **Suppression logique universelle** (`status`, `archivedAt` ou `validTo`).
   Jamais de delete physique sur une entité référencée (ADR-043).
7. **Bornes temporelles des flux calculées**, pas stockées (ADR-050).
8. **UUID = identité pérenne**, cible de tout lien ou citation. `code` = confort
   modifiable, jamais cité ni partagé (ADR-009, ADR-027).
9. **BDOH n'archive pas.** Les snapshots figés citables vivent sur l'entrepôt
   externe (Dataverse, RDG). `Dataset` est un reçu d'export, pas un conteneur de
   données (ADR-055). La TTS est vivante ; le fork curé et le Dataset couvrent
   les besoins de citation sans versionnement automatique (ADR-054).


## Avant de clore une passe

```bash
python3 outils/mdtable.py check <fichiers.md>   # alignement des tableaux
python3 outils/verifie_modele.py                # cohérence interne du modèle
```

Les deux doivent sortir zéro. Le détail de ce qu'ils vérifient, et la règle de
mise en forme qu'ils appliquent, sont dans `methode/redaction.md`.
