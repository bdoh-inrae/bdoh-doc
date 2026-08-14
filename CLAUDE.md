# CLAUDE.md : état du travail et règles de rédaction BDOH

## Rôle de ce fichier

Ce fichier est **temporel** : il dit où en est le travail, comment rédiger le
modèle, et comment collaborer. Il ne contient aucune vérité de fond ; il pointe
vers le fichier qui la détient.

Règle de propriété, valable pour tous les fichiers du projet : **une information
a un seul propriétaire. Les autres fichiers pointent, ils ne recopient pas.**
Quand une information vit à deux endroits, elle finit par diverger ; c'est la
double vérité que le modèle lui-même s'interdit.

Pour la manière de penser et de collaborer, lire `methode/SOUL.md`. Ce n'est pas
répété ici.


## Contexte du projet

BDOH (Base de Données des Observatoires Hydrologiques) est un système
d'information développé à INRAE UR RiverLy pour la gestion et le partage de
données issues d'une dizaine d'observatoires environnementaux français, en lien
avec les réseaux OZCAR et Theia.

Le modèle s'aligne sur plusieurs standards (STA, ODM2, CS API, ISO 19115,
NERC P01, STAMPLATE, Theia/OZCAR...). La liste, l'état daté de chaque standard
et la table source vers entités sont dans `modele/sources.md`, et nulle part ailleurs.

Le modèle repose sur une base TimescaleDB et deux couches : une couche IoT brute
(STA 1.1) et une couche métier BDOH (données validées et dérivées), cousues par
`TimeSeriesSource`. Le détail est dans `modele/modele_donnees.md`.

**Statut du chantier : conception, rien d'implémenté.** Aucune base ne tourne, aucun
schéma SQL n'est appliqué quelque part. Le travail avec Claude porte sur les fichiers
Markdown eux-mêmes. Conséquence directe : une incohérence relevée maintenant se
corrige en éditant le modèle, sans coût de migration. C'est le bon moment pour lever
les divergences ; ce ne sera plus le cas une fois l'implémentation commencée.


## Carte des fichiers : qui possède quoi

| Fichier                               | Possède (source de vérité de...)                                                                           |
|---------------------------------------|------------------------------------------------------------------------------------------------------------|
| `modele/modele_donnees.md`            | la **structure** : entités, colonnes, patterns TPC, conventions de nommage, scopes d'unicité, enums SQL, suppression logique, vocabulaires Keyword |
| `modele/decisions.md`                 | le **pourquoi** : ADR-001 à ADR-065, alternatives écartées                                                 |
| `modele/chantier.md`                  | **tout ce qui reste à faire** : constats (C), modélisation (M), risques structurels (S), divergences documentaires (D), veille (V), travaux (T), avec triage sévérité/effort |
| `modele/sources.md`                   | les **standards externes** et leur état daté, table source vers entités                                    |
| `methode/SOUL.md`                     | la **manière de penser et de collaborer**                                                                  |
| `plan.md`                             | l'**ordre d'exécution** du travail en cours. Les plans clos vivent dans `archives/plans/`                  |
| `outils/`                             | les **vérificateurs** : alignement des tableaux, cohérence interne du modèle                               |
| `CLAUDE.md` (ce fichier)              | l'**état du travail** et les **règles de rédaction**                                                       |
| `annexes/tpc_philosophie_synthese.md` | la **justification philosophique** du pattern TPC                                                          |

Le fichier BDD (`modele/modele_donnees.md`) est la source de vérité ; l'API s'en
déduit. Les relations inverses absentes des tableaux y réapparaissent comme
endpoints de navigation (ADR-028).


## Invariants à ne pas casser sans ADR

Rappels, pas spécifications. La spec est dans le modèle, le pourquoi dans les
ADR. Ne pas modifier l'un de ces points sans ouvrir une décision.

1. **Deux couches sur une base.** IoT brute (`Datastream`, `Observation`) et
   métier (`TimeSeries`, `ValidatedObservation`, `TransformedTimeSeries`). La
   FOI est absente de la couche IoT (ADR-014, ADR-038).
2. **TimeSeries = contrat analytique.** Changer un paramètre analytique crée une
   nouvelle TimeSeries. Un changement de capteur est une nouvelle ligne
   `TimeSeriesSource`, pas une nouvelle série (ADR-002, ADR-048).
3. **Un seul pattern TPC, cinq déclinaisons** (resource, anchor, agent,
   series, system). Intégrité applicative, pas de FK native (ADR-047, ADR-062).
4. **Cinq entités d'instrumentation** (Sensor, Actuator, Sampler, Platform, Kit),
   reliées à Deployment récursif par le TPC system. Remplace l'ancienne fusion
   System et InstrumentUsage (ADR-062, remplace ADR-037).
5. **Vocabulaires évolutifs via quadriptyque Keyword**, jamais via enum SQL.
   L'enum SQL est réservé aux discriminants qui satisfont les trois conditions
   de la grille (ADR-030, ADR-058) : le code branche sur la valeur, l'ensemble
   est fermé, ajouter une valeur est un acte de développement.
6. **Suppression logique universelle** (`status` ou `archivedAt`). Jamais de
   delete physique sur une entité référencée (ADR-043).
7. **Bornes temporelles des flux calculées**, pas stockées (ADR-050).
8. **UUID = identité pérenne**, cible de tout lien ou citation. `code` = confort
   modifiable, jamais cité ni partagé (ADR-009, ADR-027).
9. **BDOH n'archive pas.** Les snapshots figés citables vivent sur l'entrepôt
   externe (Dataverse, RDG). `Dataset` est un reçu d'export, pas un conteneur
   de données (ADR-055). La TTS est vivante ; le fork curé et le Dataset couvrent
   les besoins de citation sans versionnement automatique (ADR-054).


## Règles de rédaction du modèle

Formalisme strict pour `modele/modele_donnees.md`.

- Les tableaux de colonnes ne contiennent que des **colonnes réelles** de la table SQL correspondante. Les relations portées par des tables de jointure séparées (many-to-many, TPC series) ne figurent jamais dans le tableau de l'entité parente : elles sont documentées dans la note et dans la table des jointures explicites.
- Les tableaux Markdown s'alignent visuellement : les barres verticales de chaque colonne sont alignées sur la ligne la plus large de cette colonne, les lignes courtes sont paddées d'espaces jusqu'à cette largeur. Le contenu ne doit jamais être tronqué ni appauvri pour des raisons de largeur : si une ligne dépasse parce que les valeurs possibles sont nombreuses, elle dépasse, c'est normal et attendu.
- Pas de tiret cadratin (—) ni demi-cadratin (–) dans les fichiers générés.
  Utiliser les deux-points, des parenthèses, ou reformuler.
- Conventions de nommage (tables, colonnes, enums, valeurs de Keyword) : voir la
  section *Conventions de nommage* de `modele/modele_donnees.md`. Ne pas les
  ressaisir ici.
- En-tête d'entité, format standard à respecter :

```
### NomEntité
> Mini-définition en une ligne.

Aligné avec : standard1, standard2
Utilisé par : Entite1 (champ), Entite2 (champ)
Relations inverses (requêter par resourceType='X') : Table1, Table2
Note : rôle, contraintes, valeurs courantes si keyword.
```


## Dette de formatage connue

Aucune dette connue à ce jour.


## Mode de collaboration

- Modification mineure (un champ, une ligne) : l'indiquer et laisser
  l'utilisateur éditer dans son propre éditeur.
- Modification large (plusieurs entités, passe transversale) : édition
  programmatique via `str_replace` ou script Python.

Le réflexe de remonter en amont quand une question devient trop granulaire est
décrit dans `methode/SOUL.md` (réflexe 3). Il s'applique ici aussi.


## Régénérer bdoh-doc

Site de documentation publique, généré depuis le modèle.

Prérequis : `pip install mkdocs-material`.

Structure cible du dépôt :

```
bdoh-doc/
  .github/workflows/deploy.yml
  docs/
    index.md  overview.md
    model/
      index.md  actors.md  references.md  geography.md  network.md
      rawdata.md  instrumentation.md  observation.md  transformation.md
      organisation.md  project.md
    standards/index.md
    decisions/index.md
  mkdocs.yml  README.md
```

Processus :
1. Lire `modele/modele_donnees.md` en entier.
2. Découper en pages selon la structure ci-dessus, ajouter les liens internes.
3. Mettre à jour `docs/decisions/index.md` depuis `modele/decisions.md`.
4. Mettre à jour `docs/standards/index.md` depuis `modele/sources.md` (ne pas ressaisir
   l'état des standards à la main : il vit dans `modele/sources.md`).
5. Tester avec `mkdocs serve` avant de pousser.

Points de vigilance :
- `instrumentation.md` (cinq entités d'instrumentation + Deployment récursif) est à créer.
- `transformation.md` a été profondément remanié : ne pas repartir de l'ancienne
  version.
- Le mapping `qualityFlag` ODM2 / SANDRE et l'état de STA 2.0 viennent de
  `modele/decisions.md` (ADR-024) et `modele/sources.md`.


## Chantiers techniques en cours

Tâches d'implémentation, hors conception. Les questions de conception non
tranchées sont dans `modele/chantier.md` et ne sont pas dupliquées ici.

- **Intégrité applicative** : triggers `prevent_physical_delete`, triggers
  BEFORE INSERT/UPDATE pour les relations TPC (dont le nouveau TPC system),
  requêtes de vérification périodique. Inventaire à consolider (voir S3 dans
  `modele/chantier.md`).
- **Documentation** : régénérer bdoh-doc (procédure ci-dessus). Section
  `transformation.md` profondément remaniée (Algorithm, TransferFunctionParameter,
  incertitude). Section `organisation.md` à mettre à jour (Bundle, Dataset,
  mapping DataCite).
- **Dépôt de scripts BDOH** (B2) : conventions de nommage, format des fichiers
  de paramétrage, processus de versionnement. À traiter avant l'implémentation
  des TransformationBatch algorithmiques.
- **Ingestion** (v2, priorité basse) : spécifier le format CSV attendu par l'API
  et le pipeline de validation automatique. Aucun modèle de données
  supplémentaire requis : `ObservationBatch` et `ValidationBatch` couvrent déjà
  la traçabilité.
