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
modele_donnees_v12.md    <- modèle de données principal -- SOURCE DE VERITE
points_ouverts.md        <- chantiers structurels et décisions en attente
                            (document de travail pour discussions collectives)
decisions_index.md       <- journal des décisions de conception (ADR-001 à ADR-046)
SOUL.md                  <- comment travailler avec l'utilisateur
sources.md               <- sources scientifiques et standards annotés
integrity_checks.md      <- vérifications d'intégrité TPC à implémenter
agent_TPC_philosophie_synthese.md <- justification philosophique du pattern TPC
```

---

## Nature du fichier modele_donnees_v12.md

C'est un modèle de données BDD, pas un ERD conceptuel ni un schéma API.
Chaque tableau décrit les colonnes réelles d'une table SQL.
Les relations inverses (0..*) n'apparaissent pas dans les tableaux --
elles sont documentées dans les notes de chaque entité et accessibles
via requête sur la table qui porte la FK.

Pour l'API : toutes les relations inverses réapparaissent comme endpoints
de navigation. Le fichier BDD est la source de vérité, l'API s'en déduit.

---

## Architecture du modèle v12

### Deux couches distinctes

```
Couche IoT (STA 1.1)
  Datastream           -> flux de données brutes par capteur (System)
  Observation          -> valeur brute, phenomenonTimeStart/End, sans qualityFlag
  ObservationBatch     -> import groupé optionnel (saisie manuelle terrain)

Couche métier BDOH (centrale)
  TimeSeries            -> contrat analytique, agrège N Datastreams via TimeSeriesSource
  ValidatedObservation -> données validées par opérateur ou pipeline
  TransformedTimeSeries -> données dérivées via TransformationBatch
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
6. COUTURE       TimeSeriesSource
7. MONDE ANALYTIQUE  TimeSeries, ValidationBatch, ValidatedObservation,
                     ControlObservation, Specimen, specimen_deployment
8. TRANSFORMATION  TransferFunction, TransferFunctionPoint, TransferFunctionBatch,
                   TransferFunctionSet, TransformationBatch,
                   Transformation, TransformedTimeSeries
9. ORGANISATION  Project, HistoricalProject, Bundle, bundle_series, Memory
```

---

## Patterns transversaux -- NE PAS MODIFIER SANS ADR

Le modèle utilise un même mécanisme, appelé TPC, pour les liens
polymorphiques (liens qui peuvent pointer vers plusieurs types d'entités).
Une table porte un couple `xxxType + xxxId` : `xxxType` discrimine le type
d'entité ciblée, `xxxId` porte son UUID. Intégrité applicative
(trigger, vérification périodique), pas de FK native.

Quatre déclinaisons du pattern TPC :

### Pattern TPC resource (resourceType + resourceId)

Rattacher une donnée transverse à n'importe quelle ressource.

```
Identifier         -> PIDs vers référentiels externes
Memory             -> notes, événements, photos (mediaUrl text[])
                      cible : Observatory, Site, Station, System, TimeSeries,
                      TransformedTimeSeries, Deployment, Project, TransferFunction
Responsibility     -> rôles d'acteurs (ISO 19115 CI_RoleCode complet, 20 valeurs)
                      cible : Observatory, Site, Station, System, Datastream,
                      TimeSeries, TransformedTimeSeries, TransferFunction,
                      Project, Bundle
KeywordAssignment  -> mots-clés et classifications contrôlées
HistoricalLocation -> positions géographiques successives (Observatory, Site, Station, Deployment)
HistoricalProject  -> projets porteurs successifs
```

### Pattern TPC anchor (anchorType + anchorId)

Ancrer une entité à un contexte géographique.
Domaine variable selon l'entité :
- `Deployment` et `Specimen` : `Site | Station` seulement (on ne déploie pas
  un instrument ou ne prélève pas un échantillon sur tout un Observatory).
- Toutes les autres : `Observatory | Site | Station`.

```
Tables portant ce pattern :
  Deployment, Datastream, TimeSeries, TransformedTimeSeries,
  TransferFunction, TransferFunctionSet, Specimen
```

Règle de vérité : l'ancrage des flux (Datastream, TimeSeries,
TransformedTimeSeries) fait foi pour l'API et les requêtes. Le Deployment
documente l'installation physique et doit s'y conformer.

### Pattern TPC agent (agentType + agentId)

Désigner l'acteur d'un acte. Remplace toutes les FK directes vers Person.

```
Tables portant ce pattern :
  ValidationBatch (validatedBy)       Person | Machine
  TransformationBatch (appliedBy)     Person | Machine
  ObservationBatch (importedBy)       Person | Machine
  TransferFunctionBatch (builtBy)     Person | Machine
  Memory (author)                     Person | Machine
  Specimen (operator)                 Person | Machine
  Responsibility (agentType/agentId)  Person | Machine | Organization
```

### Pattern TPC series (seriesType + seriesId)

Pointer vers une série ou une fonction, quel que soit son type.

```
Tables portant ce pattern :
  bundle_series       Bundle <-> (TimeSeries | TransformedTimeSeries |
                                  TransferFunction | ControlObservation)
  ControlObservation  -> série analytique de référence (seriesType + seriesId)
```

### Tables de jointure explicites (many-to-many)

```
person_organization             Person <-> Organization
transformationbatch_inputseries TransformationBatch <-> TimeSeries
specimen_deployment             Specimen <-> Deployment
bundle_series                   Bundle <-> série (via pattern TPC series)
```

### Associations datées (`validFrom` / `validTo`)

Toutes ces tables encodent une relation valable sur une période. Le nommage
suit une règle de sens, pas de forme :
- Préfixe `Historical*` : historise un **attribut courant** d'une ressource
  (HistoricalLocation, HistoricalProject). La ressource « a » cet attribut
  à tout instant, la table garde la trace des valeurs passées.
- Nom décrivant le **rôle** : relie deux entités dans le temps sans qu'aucune
  ne soit l'attribut courant de l'autre (TimeSeriesSource, Deployment,
  TransferFunctionSet, Responsibility).

### Identifiants

- UUID : clé primaire technique, immuable, **identifiant de référence** pour
  tout partage, citation, lien pérenne. `/resources/{uuid}` est le permalink.
- code : slug obligatoire (1), modifiable. **Confort de navigation** pour les
  techniciens, jamais cible d'un lien partagé ou d'une citation.
- Codes externes : via Identifier, jamais via code.

### Scopes d'unicité du code

```
Observatory, Organization, System,
Project, Procedure, Property, Unit      -> unique globalement
Site                                    -> unique par Observatory
Station                                 -> unique par Site
TimeSeries, Datastream,
TransferFunction, TransformedTimeSeries -> unique par ancre (Observatory | Site | Station)
```

### Identifier vs Keyword.uri

Distinction de nature, pas de persistance :
- `Identifier` rattache une ressource à elle-même dans un autre système
  (relation d'identité : code SANDRE de station, DOI, ORCID).
- `Keyword.uri` classe une ressource dans un vocabulaire (relation de
  classification : un terme Theia/OZCAR, NERC P01, ODM2).
Les deux peuvent être des URIs persistantes ; ce qui les sépare, c'est le
rôle (identifier vs catégoriser).

### Suppression logique universelle

Aucune suppression physique sur les entités. Deux mécanismes :
- Tables avec `status` : status comme désactivation (Observatory, Station, System, Deployment, Datastream, TimeSeries, TransformedTimeSeries, Project...)
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
depthReference      surface_relative | bottom_relative | absolute_elevation
systemType          sensor | platform | equipment
agentType           Person | Machine | Organization
anchorType          Observatory | Site | Station
seriesType          TimeSeries | TransformedTimeSeries | TransferFunction | ControlObservation
codeType            doi | orcid | ror | sandre | wigos | igsn | pidinst | other
Procedure.type      sampling | observation | modeling | aggregation | transformation | validation
origin              observed | derived (sur Property)
TransferFunctionSet.type  function | identity | manual
acquisitionType     sensor_continuous | lab_sample
aggregationStatistic  instantaneous | average | cumulative | maximum | minimum |
                      variance | standard_deviation | sporadic
```

---

## Décisions clés -- à ne pas remettre en question sans contexte

- Station = objet institutionnel permanent (code SANDRE), pas un équipement
- System remplace Sensor + Equipment + Platform (ADR-037)
- Deployment récursif et universel -- System -> Deployment -> ancre (ADR-037)
- InstrumentUsage supprimé (ADR-037)
- TimeSeriesSource = couture entre monde physique et analytique (ADR-036).
  Anciens noms : TimeSeriesDatastream, puis HistoricalDatastream. Renommé en
  TimeSeriesSource parce qu'il relie deux entités dans le temps, il
  n'historise pas un attribut courant (cf. règle de nommage des associations
  datées).
- TimeSeries.sensor snapshot supprimé -- capteur courant via TimeSeriesSource WHERE validTo IS NULL
- FOI absente de Datastream et Observation -- portée par Station et TimeSeries (ADR-038)
- SamplingFeature renommée Specimen (ADR-039)
- Specimen.anchorType + anchorId : domaine `Site | Station` (pas Observatory)
  -- pattern TPC cohérent avec Deployment (ADR-041)
- specimen_deployment : many-to-many Specimen <-> Deployment (ADR-039)
- Bundle renommé depuis TimeSeriesBundle (ADR-042)
- Bundle (vivant éditorial) distinct de Dataset (figé citable) -- décision de
  conception confirmée en réunion, Dataset reste à créer (chantier A7 du
  document points_ouverts.md)
- aggregationStatistic aligné ODM2 + phenomenonTimeStart/End (ADR-044)
- ControlObservation.seriesType + seriesId -- TPC cohérent avec bundle_series (ADR-045)
- Responsibility étendue à System, Datastream, TransformedTimeSeries, Bundle
  -- pas seulement TimeSeries et Project (ADR-046 et extensions session)
- Memory étendue à TransferFunction (en plus des entités initiales)
- Project.fundingAgency supprimé -- passe par Responsibility (ADR-006)
- Project.archivedAt retiré -- Project a status, status fait foi (cohérent ADR-043)
- processingLevel absent : la structure encode le niveau (ADR-016)
- unitOfMeasurement gardé sur Datastream -- choix HydroServer/USGS (ADR-017)
- STA 2.0 Proximate/UltimateFOI non adopté -- couvert par Station.FOI + TimeSeries.FOI
- qualityFlag unique (good/suspect/bad/missing), mapping ODM2/SANDRE (ADR-024)
- Relations inverses absentes des tableaux BDD (ADR-028)
- Suppression logique universelle via status ou archivedAt (ADR-043)

### Acquis de la passe de consolidation v12

- **Pattern TPC unifié** : un seul mécanisme, quatre déclinaisons (resource,
  anchor, agent, series). Voir Patterns transversaux.
- **Bornes temporelles des flux calculées, pas stockées** : `phenomenonTime`
  Start/End sur Datastream, TimeSeries, TransformedTimeSeries sont des
  propriétés calculées (MIN/MAX des observations), pas des colonnes.
  TimescaleDB rend le calcul peu coûteux. Recomposé en l'intervalle STA
  `phenomenonTime` à l'export.
- **resultTime uniformisé à 0..1** sur Observation, ValidatedObservation,
  Transformation (conforme STA Part 1, qui définit `resultTime` nullable).
  Sémantique : moment de production de la valeur. À ne pas confondre avec
  la date de validation (qui est sur ValidationBatch).
- **TransferFunction.validFrom / validTo** (et non plus startDate/endDate) :
  une courbe de tarage est une association datée, comme un Deployment.
- **Renvois vers Procedure typés** : toute colonne pointant vers une Procedure
  est suffixée du type attendu (procedureObservation, procedureValidation,
  procedureSampling, procedureModeling, procedureTransformation). Même si
  l'entité n'a qu'une seule procédure, on suffixe.
- **Notation des "Utilisé par"** : `(FK colonne)`, `(anchor)`,
  `(via resourceType + resourceId)`, `(table jointure)` pour distinguer
  les natures de liens.
- **Keyword.notation** (1, obligatoire) : identifiant court kebab-case,
  immuable, unique par keywordType. Sert de segment d'URI pour la publication
  du vocabulaire BDOH (équivalent skos:notation). Suggéré depuis term_en à la
  création, puis figé.
- **Distinction Identifier / Keyword.uri** : Identifier = identité d'une
  ressource (code SANDRE, DOI, ORCID) ; Keyword.uri = classification dans un
  vocabulaire (terme Theia/OZCAR, NERC, ODM2). Les deux peuvent être des
  URIs persistantes, c'est le rôle qui les sépare.
- **TimeSeriesSource** (ex-HistoricalDatastream) : nommé d'après son rôle
  (la source d'une TimeSeries) et non avec préfixe Historical*, parce que
  c'est une association datée et non l'historique d'un attribut. Voir règle
  de nommage des associations datées.
- **Theia/OZCAR thesaurus ajouté en alignement de Property** (en plus de
  Keyword). C'est le rattachement national des variables, essentiel pour
  l'interopérabilité avec le portail in-situ.theia-land.fr.

### Conventions de nommage (issues de la passe v12)

- Entités (tables principales) : TitleCase (`Observatory`, `TimeSeries`)
- Tables de jointure : snake_case (`person_organization`, `bundle_series`,
  `specimen_deployment`, `transformationbatch_inputseries`)
- Colonnes : camelCase (`phenomenonTimeStart`, `procedureObservation`).
  Exception : suffixes de langue conservés en snake_case (`term_en`,
  `label_fr`, `definition_en`).
- Discriminants TPC (`resourceType`, `anchorType`, `seriesType`, `agentType`
  pour Organization) : `TitleCase` = nom exact de l'entité ciblée. Cela rend
  le discriminant auto-explicite.
- Autres valeurs d'enum : `lowercase` pour mots simples (`active`, `good`),
  `snake_case` pour composés (`sensor_continuous`, `standard_deviation`).
- Valeurs de Keyword : `term_en` lisible (avec espaces : "surface water"),
  `notation` en kebab-case ("surface-water"). Pas de snake_case sur les
  termes de vocabulaire, qui ne sont pas des enums SQL.

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

1. Lire `modele_donnees_v12.md` en entier
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

L'inventaire complet et structuré des points en suspens est maintenant dans
le fichier `points_ouverts.md` (document de travail pour discussions
collectives). Lire ce fichier en début de session pour avoir l'état actuel
des chantiers et des questions non tranchées.

Résumé des chantiers structurels (Partie A de points_ouverts.md) :

- **A1. Transformation comme moteur d'exécution**. BDOH exécute les
  transformations, runners = entités Machine. `transferFunctionSet`
  actuellement obligatoire, à élargir aux autres familles (agrégations,
  comblement de lacunes, corrections, linéarisation, combinaisons). Q0
  préalable : inventaire exhaustif des familles avant conception.
- **A2. Incertitude de mesure**. Manquante sur Observation, ValidatedObservation,
  Transformation. Standards de référence (ODM2 resultUncertainty,
  Helmholtz SMS) la portent.
- **A3. Bundle pour la mise en avant éditoriale de flux vivants**.
  Recentré sur la diffusion éditoriale (Bundle = vivant), la publication
  citable est traitée à part dans A7.
- **A4. Historisation TFSet et versionnement TTS**. Les anciennes valeurs
  publiées ne doivent pas disparaître quand une nouvelle courbe de tarage
  arrive. Distinction entre historiser la recette (TFSet) et versionner
  le produit (TTS).
- **A5. Plusieurs Datastreams alimentant simultanément une TimeSeries**.
  Cas master/save et fusion statistique. La structure le permet déjà mais
  la documentation décrit du séquentiel ; à amender.
- **A6. Instrumentation labo et extension System/Deployment au laboratoire**.
  Deux voies à mener de front : lien LIMS externe ET représentation interne
  de la chaîne CUAHSI (prélèvement / préparation / analyse). Pattern
  System+Deployment réutilisé avec Specimen comme ancrage.
- **A7. Entité Dataset distincte de Bundle**. Snapshot figé citable avec
  DOI pour Recherche Data Gouv / Theia/OZCAR, et traçabilité de
  réutilisation (quels Datasets utilisent telle ressource).

Décisions en attente (Partie B) :
- **B1. Frontière enum SQL / Keyword**. Plusieurs enums vocabulaire métier
  (aggregationStatistic, Procedure.type) à arbitrer enum par enum.

Ambiguïtés locales (Partie C) : ControlObservation ancrage/qualité (C1),
Procedure DS vs TS (C2), asymétrie KeywordAssignment/Requirement (C3),
Specimen.operator Machine (C4, réglé pour mémoire).

Veille standards (Partie D) : OGC CS API approuvé 2026, STA 2.0 en
ratification, STAMPLATE Zenodo 2025, eLTER-RI / ENVRI-Hub NEXT.

### INTÉGRITÉ -- À IMPLÉMENTER (voir integrity_checks.md)

- Triggers prevent_physical_delete sur toutes les entités
- Triggers BEFORE INSERT/UPDATE pour les relations TPC (resource, anchor,
  agent, series)
- Requêtes de vérification périodique

### DOCUMENTATION

- Régénérer bdoh-doc depuis modele_donnees_v12.md (toutes sections)
- Mettre à jour standards/index.md (OGC CS API v1.0, STAMPLATE 2025)
- Sections à créer : instrumentation.md (System+Deployment)

### INGESTION -- priorité basse (v2)

- Format CSV d'import : spécification du format attendu par l'API
  (pas de modèle de données supplémentaire nécessaire -- ValidationBatch
  et ObservationBatch couvrent déjà la traçabilité)
- Pipeline de validation automatique : workflow Wiski/Hydrolab → ValidationBatch
  (validationLogUrl suffit pour l'instant)
