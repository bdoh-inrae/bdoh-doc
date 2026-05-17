# CLAUDE.md -- Instructions pour futures conversations BDOH

---

## Contexte du projet

BDOH (Base de Données des Observatoires Hydrologiques) est un système
d'information développé à INRAE UR RiverLy pour la gestion et le partage
de données issues d'une dizaine d'observatoires environnementaux français,
en lien direct avec les réseaux OZCAR et Theia.

Le modèle de données est aligné avec :
- OGC SensorThings API 1.1 (base, couche IoT)
- OGC CS API v1.0 (publié fév. 2026 -- référence pour System/Deployment)
- ODM2 Horsburgh et al. 2016 (métadonnées environnementales)
- ISO 19115 (gouvernance et responsabilités, CI_RoleCode complet)
- NERC NVS P01 + Theia/OZCAR thesaurus (variables)
- STAMPLATE Helmholtz (extensions STA, schéma Zenodo 2025)
- CodeMeta + ISO/IEC 18670 SWHID (métadonnées logicielles sur Machine)

---

## Posture épistémique

Ce projet a deux besoins qui coexistent dans la même conversation.

Le premier est philosophique : s'assurer que les décisions reposent sur
une compréhension claire de ce qu'on modélise, pas sur une habitude
technique ou un confort d'implémentation. Les meilleures décisions de
ce projet sont venues de questions en amont -- "qu'est-ce qu'un agent
dans ce domaine ?", "Station représente quoi en métrologie réelle ?" --
et non de réponses directes à des questions techniques.

Le second est ingénieur : traduire ces décisions correctement dans le
modèle, maintenir la cohérence, documenter les ADR, éviter les doubles
vérités.

La conversation guidera lequel des deux est utile à chaque moment.
Mais le premier ne doit jamais disparaître complètement, même quand
les questions deviennent granulaires. Un schéma techniquement cohérent
peut reposer sur une erreur conceptuelle fondamentale. Le signal que
quelque chose ne va pas est souvent une question technique qui résiste
-- c'est alors qu'il faut remonter en amont, pas aller plus loin dans
le détail.

**Quand une question technique résiste, chercher la question conceptuelle
qu'elle présuppose. La répondre d'abord.**

**Les standards sont des boussoles, pas des autorités.** STA, ODM2,
CS API -- comprendre le raisonnement qui les a produits avant de
les appliquer. Quand un standard ne sert pas le projet, le dire et
documenter pourquoi. Chercher sur internet l'état actuel des standards
avant de conseiller -- ils évoluent.

---

## Fichiers de référence

```
modele_donnees_v11.md    <- modèle de données principal -- SOURCE DE VERITE
decisions_index.md       <- journal des décisions de conception (ADR-001 à ADR-046)
SOUL.md                  <- comment travailler avec l'utilisateur
sources.md               <- sources scientifiques et standards annotés
integrity_checks.md      <- vérifications d'intégrité TPC à implémenter
agent_TPC_philosophie_synthese.md <- justification philosophique du pattern TPC
```

---

## Nature du fichier modele_donnees_v11.md

C'est un modèle de données BDD, pas un ERD conceptuel ni un schéma API.
Chaque tableau décrit les colonnes réelles d'une table SQL.
Les relations inverses (0..*) n'apparaissent pas dans les tableaux --
elles sont documentées dans les notes de chaque entité et accessibles
via requête sur la table qui porte la FK.

Pour l'API : toutes les relations inverses réapparaissent comme endpoints
de navigation. Le fichier BDD est la source de vérité, l'API s'en déduit.

---

## Architecture du modèle v11

### Deux couches distinctes

```
Couche IoT (STA 1.1)
  Datastream           -> flux de données brutes par capteur (System)
  Observation          -> valeur brute, phenomenonTimeStart/End, sans qualityFlag
  ObservationBatch     -> import groupé optionnel (saisie manuelle terrain)

Couche métier BDOH (centrale)
  TimeSerie            -> contrat analytique, agrège N Datastreams via HistoricalDatastream
  ValidatedObservation -> données validées par opérateur ou pipeline
  TransformedTimeSerie -> données dérivées via TransformationBatch
```

### Sections du modèle (ordre dans le fichier)

```
1. ACTEURS       Person, Machine, Organization, Responsibility
2. REFERENTIELS  KeywordType, Keyword, KeywordAssignment, KeywordRequirement,
                 License, Property, Unit, Procedure, Identifier
3. GEOGRAPHIE    Location, HistoricalLocation, FeatureOfInterest
4. MONDE PHYSIQUE  Observatory, Site, Station,
                   System, Deployment,
                   Datastream, ObservationBatch, Observation
6. COUTURE       HistoricalDatastream
7. MONDE ANALYTIQUE  TimeSerie, ValidationBatch, ValidatedObservation,
                     ControlObservation, Specimen, specimen_deployment
8. TRANSFORMATION  TransferFunction, TransferFunctionPoint, TransferFunctionBatch,
                   TransferFunctionSet, TransformationBatch,
                   Transformation, TransformedTimeSerie
9. ORGANISATION  Project, HistoricalProject, Bundle, BundleSerie, Memory
```

---

## Patterns transversaux -- NE PAS MODIFIER SANS ADR

### Tables polymorphiques TPC (resourceType + resourceId)

```
Identifier         -> PIDs vers référentiels externes
Memory             -> notes, événements, photos (mediaUrl text[])
Responsibility     -> rôles d'acteurs (ISO 19115 CI_RoleCode complet, 20 valeurs)
KeywordAssignment  -> mots-clés et classifications contrôlées
HistoricalLocation -> positions géographiques successives (Observatory, Site, Station, Deployment)
HistoricalProject  -> projets porteurs successifs
BundleSerie        -> lien Bundle vers TimeSerie | TransformedTimeSerie | TransferFunction | ControlObservation
```

### Pattern TPC agent (agentType + agentId)

Remplace toutes les FK directes vers Person.
`agentType` : `person | machine | organization` (selon la table).

```
Tables portant ce pattern :
  ValidationBatch (validatedBy)       person | machine
  TransformationBatch (appliedBy)     person | machine
  ObservationBatch (importedBy)       person | machine
  TransferFunctionBatch (builtBy)     person | machine
  Memory (author)                     person | machine
  Specimen (operator)                 person | machine
  Responsibility (agentType/agentId)  person | machine | organization
```

### Pattern TPC anchor (anchorType + anchorId)

Remplace les FK directes vers Station sur les entités qui peuvent etre
rattachées à des granularités géographiques différentes.
`anchorType` : `observatory | site | station`

```
Tables portant ce pattern :
  Deployment, Datastream, TimeSerie, TransformedTimeSerie,
  TransferFunction, TransferFunctionSet, Specimen
```

### Tables de jointure explicites (many-to-many)

```
person_organization             Person <-> Organization
transformationbatch_inputseries TransformationBatch <-> TimeSerie
specimen_deployment             Specimen <-> Deployment
bundle_serie                    Bundle <-> (TimeSerie | TransformedTimeSerie | TransferFunction | ControlObservation)
```

### Identifiants

- UUID : clé primaire technique, immuable, permalink /resources/{uuid}
- code : slug obligatoire (1), unique par scope anchor, modifiable
- Codes externes : via Identifier, jamais via code

### Scopes d'unicité du code

```
Observatory, Organization, System,
Project, Procedure, Property, Unit    -> unique globalement
Site                                  -> unique par Observatory
Station                               -> unique par Site
TimeSerie, Datastream,
TransferFunction, TransformedTimeSerie -> unique par ancre (Observatory | Site | Station)
```

### Suppression logique universelle

Aucune suppression physique sur les entités. Deux mécanismes :
- Tables avec `status` : status comme désactivation (Observatory, Station, System, Deployment, Datastream, TimeSerie, TransformedTimeSerie, Project...)
- Tables sans `status` : `archivedAt TIMESTAMPTZ NULL` (Person, Machine, Organization, Site, Unit, Procedure, KeywordType, Keyword, License, Location, FeatureOfInterest, Bundle)
- Tables de jointure : suppression physique OK (non référencées)

---

## Système de vocabulaires contrôlés -- QUADRIPTYQUE KEYWORD (ADR-030)

Tous les vocabulaires évolutifs passent par ce système, jamais par enums SQL.

```
KeywordType       -> types de métadonnées, alignés avec les standards
Keyword           -> termes bilingues alignés avec thésaurus externes
KeywordAssignment -> lien polymorphique multi-valeurs ressource -> keyword
KeywordRequirement -> règles de complétion minimale configurables sans migration
```

### Enums SQL fixes (conditionnent du code applicatif)

```
qualityFlag         good | suspect | bad | missing
status              active | inactive | discontinued | retired | removed...
validationMode      auto | manual
transmissionMode    auto | manual
depthReference      surfaceRelative | bottomRelative | absoluteElevation
systemType          sensor | platform | equipment
agentType           person | machine | organization
anchorType          observatory | site | station
serieType           TimeSerie | TransformedTimeSerie (sur ControlObservation)
codeType            doi | orcid | ror | sandre | wigos | igsn | pidinst | other
Procedure.type      sampling | observation | modeling | aggregation | transformation | validation
origin              observed | derived (sur Property)
TransferFunctionSet.type  function | identity | manual
acquisitionType     sensor_continuous | lab_sample
aggregationStatistic  Instantaneous | Average | Cumulative | Maximum | Minimum |
                      Variance | StandardDeviation | Sporadic
```

---

## Décisions clés -- à ne pas remettre en question sans contexte

- Station = objet institutionnel permanent (code SANDRE), pas un équipement
- System remplace Sensor + Equipment + Platform (ADR-037)
- Deployment récursif et universel -- System -> Deployment -> ancre (ADR-037)
- InstrumentUsage supprimé (ADR-037)
- HistoricalDatastream = couture entre monde physique et analytique (ADR-036)
- TimeSerie.sensor snapshot supprimé -- capteur courant via HistoricalDatastream WHERE validTo IS NULL
- FOI absente de Datastream et Observation -- portée par Station et TimeSerie (ADR-038)
- SamplingFeature renommée Specimen (ADR-039)
- Specimen.anchorType + anchorId -- pattern TPC cohérent avec Deployment (ADR-041)
- specimen_deployment : many-to-many Specimen <-> Deployment (ADR-039)
- Bundle renommé depuis TimeSeriesBundle (ADR-042)
- aggregationStatistic aligné ODM2 + phenomenonTimeStart/End (ADR-044)
- ControlObservation.serieType + serieId -- TPC cohérent avec BundleSerie (ADR-045)
- Responsibility étendue à System -- rôles owner/pointOfContact/custodian sur instruments (ADR-046)
- Project.fundingAgency supprimé -- passe par Responsibility (ADR-006)
- processingLevel absent : la structure encode le niveau (ADR-016)
- unitOfMeasurement gardé sur Datastream -- choix HydroServer/USGS (ADR-017)
- STA 2.0 Proximate/UltimateFOI non adopté -- couvert par Station.FOI + TimeSerie.FOI
- qualityFlag unique (good/suspect/bad/missing), mapping ODM2/SANDRE (ADR-024)
- Relations inverses absentes des tableaux BDD (ADR-028)
- Suppression logique universelle via status ou archivedAt (ADR-043)

---

## Mode de collaboration

Modifications mineures (un champ, une ligne) : indiquer et laisser
l'utilisateur éditer dans son propre éditeur.
Modifications larges (plusieurs entités, passes transversales) :
édition programmatique via str_replace ou script Python.

Quand une question devient très granulaire (quelle colonne exactement,
quel trigger, quel index), s'arrêter et vérifier : la structure est-elle
correcte avant d'en optimiser les détails ? Si le doute existe, remonter
en amont avant de descendre dans le détail.

---

## Contraintes de formatage -- IMPORTANT

- Tableaux Markdown : 150 caractères de large maximum
- Jamais de tiret long dans les fichiers générés, utiliser " - " ou reformuler
- En-têtes d'entité : format standard à respecter

```
### NomEntité
> Mini-définition en une ligne.

Aligné avec : standard1, standard2
Utilisé par : Entite1 (champ), Entite2 (champ)
Relations inverses (requêter par resourceType='X') : Table1, Table2
Note : rôle, contraintes, valeurs courantes si keyword.
```

---

## Comment régénérer bdoh-doc

### Prérequis

```bash
pip install mkdocs-material
```

### Structure cible du dépôt

```
bdoh-doc/
  .github/workflows/deploy.yml
  docs/
    index.md
    overview.md
    model/
      index.md
      actors.md
      references.md
      geography.md
      network.md
      rawdata.md
      project.md
      instrumentation.md   <- System + Deployment (à créer)
      observation.md
      transformation.md
      organisation.md
    standards/
      index.md
    decisions/
      index.md
  mkdocs.yml
  README.md
```

### Processus de régénération

1. Lire `modele_donnees_v11.md` en entier
2. Découper en pages selon la structure ci-dessus
3. Ajouter les liens internes entre entités
4. Mettre à jour `decisions/index.md` avec les ADR courants
5. Mettre à jour `standards/index.md` (OGC CS API v1.0, STAMPLATE 2025)
6. Tester avec `mkdocs serve` avant de pousser

### Points de vigilance

- `instrumentation.md` est à créer (System + Deployment récursif)
- `transformation.md` a été profondément remanié -- ne pas partir de l'ancienne version
- Le mapping `qualityFlag` ODM2/SANDRE doit apparaître dans `standards/index.md`
- STA 2.0 non adopté -- le noter dans `standards/index.md`

---

## Points ouverts pour prochaines sessions

### TRANSFORMATION -- session dédiée recommandée (point MAJEUR)

`TransformationBatch.transferFunctionSet` est obligatoire (1), bloquant
les cas sans barème structuré.

Cas à couvrir :
1. Barème (TransferFunctionSet) -- couvert actuellement
2. Agrégation temporelle via fichier config externe (QJXA, etc.)
3. Script ad hoc (comblement lacunes, correction chimie)

Piste validée non implémentée :
- transferFunctionSet 0..1 + parameterUrl 0..1
- Contrainte : au moins un des deux renseigné

Question architecturale non tranchée : BDOH exécute-t-il les transformations
ou les documente-t-il ? Cette décision conditionne tout.

### SCIENCE OUVERTE

- Incertitude de mesure : resultUncertainty sur ValidatedObservation ?
  ODM2 et Helmholtz SMS l'ont -- important pour la reproductibilité scientifique.
- Catalogue FAIR : DataCite DOI sur Bundle, lien CSW / OGC API Records.
- i-Adopt Framework pour interopérabilité des variables (utilisé par FairTOIS).

### INTÉGRITÉ -- À IMPLÉMENTER (voir integrity_checks.md)

- Triggers prevent_physical_delete sur toutes les entités
- Triggers BEFORE INSERT/UPDATE pour les relations TPC (agent, anchor, serieType)
- Requêtes de vérification périodique

### DOCUMENTATION

- Régénérer bdoh-doc depuis modele_donnees_v11.md (toutes sections)
- Mettre à jour standards/index.md (OGC CS API v1.0, STAMPLATE 2025)
- Sections à créer : instrumentation.md (System+Deployment)

### QUESTIONS NON TRANCHÉES

- Bundle : métadonnées obligatoires pour publication DataCite ? (à soumettre aux collègues)
- Export vocabulaires BDOH avec URIs persistantes (infrastructure à prévoir)
- eLTER-RI et ENVRI-Hub NEXT : alignement vocabulaires BDOH à surveiller
- Project.archivedAt : le modèle v11 a à la fois status et archivedAt sur Project --
  trancher en faveur de status seul (cohérent avec ADR-043 et les autres entités à status)
- Specimen.anchorType : valider si observatory est pertinent ou si station | site suffit

### INGESTION -- priorité basse (v2)

- Format CSV d'import : spécification du format attendu par l'API
  (pas de modèle de données supplémentaire nécessaire -- ValidationBatch
  et ObservationBatch couvrent déjà la traçabilité)
- Pipeline de validation automatique : workflow Wiski/Hydrolab → ValidationBatch
  (validationLogUrl suffit pour l'instant)
