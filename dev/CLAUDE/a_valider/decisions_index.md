# Décisions de conception BDOH

Ce journal documente les choix structurants du modèle -- pourquoi telle option
a été retenue, quelles alternatives ont été écartées et pour quelle raison.
L'objectif est de rendre le modèle maintenable dans le temps sans avoir à
reconstruire le raisonnement depuis zéro.

---

## ADR-001 -- STA comme base, étendu par ODM2

**Décision** : utiliser OGC SensorThings API comme modèle de base et l'enrichir
avec les métadonnées d'ODM2.

**Contexte** : STA est léger, REST/JSON, orienté IoT -- mais trop générique pour
les observatoires environnementaux. ODM2 est riche sémantiquement mais daté
technologiquement (XML, WaterOneFlow).

**Choix retenu** : STA pour la structure et l'interface, ODM2 pour la sémantique
des métadonnées environnementales. C'est l'approche de Horsburgh et al. (2024)
avec HydroServer. STA 1.1 reste la référence de production -- STA 2.0 (appel
à commentaires jan. 2026) et OGC CS API v1.0 (publié fév. 2026) sont surveillés
pour la v2.

**Références** : Horsburgh et al. (2024), *Environmental Modelling and Software*
doi:10.1016/j.envsoft.2024.106241

---

## ADR-002 -- TimeSerie comme contrat analytique

**Décision** : la `TimeSerie` porte tout ce qui est fixe pour toute la série --
variable, protocole analytique, milieu.

**Contexte** : dans STA, le `Datastream` est déjà ce concept. BDOH le renforce
en y attachant `procedure.observation` comme contrat immuable.

**Conséquence** : si un paramètre analytique change, c'est une nouvelle `TimeSerie`.
Le changement de capteur sans impact sur la comparabilité est tracé via
`HistoricalDatastream` (ex-`TimeSerieDatastream`, renommé ADR-036).

---

## ADR-003 -- Station vs FeatureOfInterest

**Décision** : distinguer explicitement la `Station` (ancrage institutionnel
permanent, code SANDRE) de la `FeatureOfInterest` (entité réelle du monde observée).

**Choix retenu** : la `Station` est l'objet institutionnel -- elle existe
indépendamment de tout équipement, a un code SANDRE et une continuité historique.
La `FeatureOfInterest` est l'eau de surface, les sédiments, la nappe.
Une même station peut avoir plusieurs FOI (ADR-038).

---

## ADR-004 -- Pattern resourceType + resourceId (TPC)

**Décision** : pattern polymorphique TPC pour les entités transversales
(`Memory`, `Identifier`, `HistoricalLocation`, `HistoricalProject`,
`Responsibility`, `KeywordAssignment`).

**Choix retenu** : schéma uniforme et extensible. L'intégrité référentielle est
garantie par trigger BEFORE INSERT/UPDATE, pas par FK native PostgreSQL.
Voir integrity_checks.md pour les requetes de verification periodique.

**Justification philosophique** : documentée dans agent_TPC_philosophie_synthese.md.
TPC est choisi parce que les types cibles sont ontologiquement distincts et
partagent seulement un role fonctionnel. La semantique voyage avec les donnees
(discriminant lisible dans les exports CSV).

---

## ADR-005 -- Historical* : pattern uniforme

**Décision** : toutes les entités `Historical*` partagent la même structure :
`resourceType + resourceId + validFrom + validTo`.

**Choix retenu** : cohérence des requêtes -- un développeur qui connaît
`HistoricalLocation` comprend immédiatement les autres.

---

## ADR-006 -- Project et HistoricalProject : source de vérité unique

**Décision** : le lien Project → ressources passe uniquement par `HistoricalProject`.
`Project.fundingAgency` supprimé -- les organisations et leurs rôles passent
entièrement par `Responsibility` (resourceType='Project', role=funder|...).

**Choix retenu** : évite les incohérences entre deux sources d'information.
Un même observatoire peut être porté successivement par OSR6, OSR7, OSR8.
`Responsibility` avec `validFrom/validTo` porte la temporalité et la multiplicite
sans double vérité.

---

## ADR-007 -- LIMS hors modèle

**Décision** : la chaîne analytique interne au laboratoire est hors modèle.
Le lien se fait via `Specimen.limsReference`.

**Contexte** : `limsReference` est sur `Specimen` (renommé depuis SamplingFeature,
ADR-039) car c'est le prélèvement qui reçoit un numéro de dossier LIMS --
plusieurs observations peuvent découler du même prélèvement.

---

## ADR-008 -- SUPERSEDE par ADR-030

**Statut** : obsolète. `discipline` et `theme` sur `Property` passent en
`KeywordAssignment` conformément à ADR-030.

---

## ADR-009 -- Identifiants : UUID + code lisible

**Décision** : `id` UUID immuable + `code` kebab-case lisible sur toutes les entités.

**Convention** : suggestion automatique depuis `name` (ou `serialNumber` pour System).

---

## ADR-010 -- SUPERSEDE par ADR-037

**Statut** : obsolète. `Deployment` a été profondément refactorisé (ADR-037).

---

## ADR-011 -- Specimen vs FeatureOfInterest

**Décision** :
- `FeatureOfInterest` = entité réelle du monde, stable, avec géométrie
- `Specimen` = acte de prélèvement terrain, événement daté (renommé depuis
  SamplingFeature, ADR-039)

**Note** : cette distinction couvre les mêmes cas que Proximate/UltimateFOI
de OMS/STA 2.0 sans adopter la terminologie non finalisée.

---

## ADR-012 -- Property : symbol + code

**Décision** : `code` obligatoire (2-8 cars kebab-case) + `symbol` optionnel
(notation scientifique standard).

---

## ADR-013 -- variableType : intensive vs extensive

**Décision** : champ `variableType` explicite sur `Property` pour guider les
calculs de delta.

---

## ADR-014 -- Architecture deux couches IoT / backend

**Décision** : une seule base TimescaleDB, deux couches applicatives distinctes.

**Couche IoT STA 1.1** : Datastream + Observation (données brutes, raw).
**Couche métier BDOH** : TimeSerie + ValidatedObservation (données validées).

**API** : deux vues sur la même base -- FastAPI (STA) + Django (BDOH metier).
L'API STA expose /Sensors comme vue filtrée `System WHERE systemType='sensor'`.
La FOI est absente de la couche IoT -- portée par Station et TimeSerie (ADR-038).

---

## ADR-015 -- SUPERSEDE par ADR-036

**Statut** : obsolète. `TimeSerieDatastream` renommé `HistoricalDatastream`
et simplifié (ADR-036).

---

## ADR-016 -- processingLevel absent du modèle

**Décision** : `processingLevel` supprimé. La structure encode le niveau :
- `Observation` (IoT) = raw
- `ValidatedObservation` (BDOH) = validated
- `TransformedTimeSerie` (BDOH) = derived

---

## ADR-017 -- unitOfMeasurement gardé sur Datastream

**Décision** : BDOH garde `unitOfMeasurement` comme FK vers `Unit` sur `Datastream`,
plutôt que le `resultType` SWE-Common de STA 2.0.

---

## ADR-018 -- SUPERSEDE par ADR-031

**Statut** : obsolète. `license` et `access` remplacés par `License` table
obligatoire (ADR-031).

---

## ADR-019 -- ValidationBatch pour les sessions de validation

**Décision** : objet `ValidationBatch` séparé pour grouper les observations
validées en une même session. `ValidatedObservation.validationBatch 0..1`.

---

## ADR-020 -- TimeSerie : une procédure de validation unique

**Décision** : `procedure.validation` est unique et obligatoire sur `TimeSerie`.
Plusieurs validations parallèles = plusieurs `TimeSerie` distinctes.

---

## ADR-021 -- TransferFunction analogue à TimeSerie

**Décision** : `TransferFunction` liée à une ancre géographique via
`anchorType + anchorId` (pattern TPC, ADR-041).

---

## ADR-022 -- TransformationBatch et Transformation

**Décision** : `Transformation` renommée `TransformationBatch`, `TransformedObservation`
pour les points calculés.

---

## ADR-023 -- samplingPeriod sur Property : trois champs

**Décision** : `samplingPeriod` remplacé par `samplingPeriodStart`,
`samplingPeriodEnd`, `samplingPeriodMode`.

---

## ADR-024 -- qualityFlag : vocabulaire unique mappé vers standards

**Décision** : quatre valeurs internes BDOH mappées vers ODM2/SANDRE/OGC.

| BDOH | ODM2 | SANDRE | OGC resultQuality |
|---|---|---|---|
| `good` | Good | 1 Bonne | `good` |
| `suspect` | Suspect | 3 Douteuse | `suspect` |
| `bad` | Bad | 4 Mauvaise | `invalid` |
| `missing` | Missing | lacune | `missing` |

---

## ADR-025 -- Instance centralisée nationale

**Décision** : une seule instance BDOH centralisée pour tous les observatoires
français. TimescaleDB scale largement au-delà des besoins de 10 observatoires.

---

## ADR-026 -- Coexistence sans hiérarchie des TransformedTimeSerie

**Décision** : plusieurs `TransformedTimeSerie` coexistent sans `isReference`.
Le contexte scientifique et l'expertise technique désignent laquelle utiliser.

---

## ADR-027 -- code slug obligatoire avec scopes d'unicité

**Décision** : `code` obligatoire sur toutes les entités, unique dans son scope.

**Scopes** :
- Unique globalement : Observatory, Organization, System, Project, Procedure,
  Property, Unit
- Unique par Observatory : Site
- Unique par Site : Station
- Unique par ancre : TimeSerie, Datastream, TransferFunction, TransformedTimeSerie

---

## ADR-028 -- Relations inverses absentes des tableaux BDD

**Décision** : les relations inverses (0..*) ne sont jamais des colonnes dans
les tableaux. Accessibles via requête sur la table qui porte la FK.

---

## ADR-029 -- SUPERSEDE par ADR-037

**Statut** : obsolète. `InstrumentUsage` supprimé, remplacé par `System` +
`Deployment` récursif (ADR-037).

---

## ADR-030 -- Système de vocabulaires contrôlés via quadriptyque Keyword

**Décision** : tous les vocabulaires contrôlés évolutifs passent par
`KeywordType`, `Keyword`, `KeywordAssignment`, `KeywordRequirement`.

---

## ADR-031 -- License obligatoire sur les flux de données

**Décision** : `License` table obligatoire (1) sur Datastream, TimeSerie,
TransformedTimeSerie et Bundle (renommé depuis TimeSeriesBundle, ADR-042).

---

## ADR-032 -- SUPERSEDE par ADR-036

**Statut** : obsolète. `TimeSerieDatastream` renommé `HistoricalDatastream`
et sa structure a évolué (ADR-036).

---

## ADR-033 -- Procedure.type : ajout de aggregation

**Décision** : `Procedure.type` inclut `aggregation` pour les agrégations
temporelles (QJXA, cumuls...).

**Valeurs complètes** :
```
sampling | observation | modeling | aggregation | transformation | validation
```

---

## ADR-034 -- SUPERSEDE par ADR-037

**Statut** : obsolète. Sensor et Equipment fusionnés en `System` (ADR-037).

---

## ADR-035 -- ObservationBatch pour les imports manuels terrain

**Décision** : `ObservationBatch` est optionnel sur `Observation`.
Créé uniquement pour les imports manuels groupés. `agentType + agentId`
(pattern TPC) -- peut être une personne ou une machine.

---

## ADR-036 -- HistoricalDatastream : renommage et enrichissement

**Décision** : `TimeSerieDatastream` renommé `HistoricalDatastream`.
Champs `deploymentDepth` et `depthReference` migrés vers `Deployment`.
La position nominale du capteur appartient au contexte de déploiement,
pas au lien temporel entre série et flux.

**Structure finale** :
```
HistoricalDatastream : id, timeSerie 1->TS, datastream 1->DS, validFrom, validTo
```

**Rôle** : couture entre le monde physique (System -> Deployment -> Datastream)
et le monde analytique (TimeSerie -> ValidatedObservation).

---

## ADR-037 -- System + Deployment récursif remplace Sensor/Equipment/Platform/InstrumentUsage

**Décision** : Platform, Sensor, Equipment fusionnés en une entité unique `System`
avec discriminant `systemType` (sensor | platform | equipment). `InstrumentUsage`
supprimé. `Deployment` devient récursif et universel.

**Justification** : TPC appliqué à la couche instrumentale. Sensor, Platform et
Equipment sont ontologiquement distincts mais partagent le même rôle fonctionnel
d'objet physique traçable. La vue API STA /Sensors est une vue filtrée
`System WHERE systemType='sensor'`.

**Deployment récursif** :
- `parentDeployment 0..1` -- hiérarchie de Systems imbriqués
- `anchorType + anchorId` -- TPC vers Station ou Site
- `deploymentDepth + depthReference` -- position nominale du System
- Couvre tout : capteur sur bouée sur station, drone sur site, équipement
  pendant un prélèvement

**Position dans le temps -- deux mécanismes** :
- `HistoricalLocation` sur Deployment : position événementielle (repositionnement
  ponctuel)
- `TimeSerie` de position : position continue (trajectoire drone, profileur
  autonome) -- property=position, aggregationStatistic=Instantaneous

**Références** : OGC CS API v1.0 (fév. 2026), SOSA/SSN, SensorML

---

## ADR-038 -- FOI dans la couche métier uniquement

**Décision** : `featureOfInterest` absente de `Datastream` et `Observation`
(couche IoT). Portée par `Station` (FOI ultime), `TimeSerie` et
`TransformedTimeSerie` (FOI proximate optionnelle).

**Règle de résolution API STA** :
```
FOI exposée = TimeSerie.featureOfInterest si renseignée
              sinon anchor.featureOfInterest (Station ou Site)
```

**Conséquence** : une seule source de vérité par niveau. Pas de double vérité
entre couche IoT et couche métier.

---

## ADR-039 -- SamplingFeature renommée Specimen

**Décision** : `SamplingFeature` renommée `Specimen` pour lever l'ambiguïté
avec la notion de SamplingFeature spatiale qu'est Station.

**Justification** : un Specimen est un acte de prélèvement physique daté,
pas un point de surveillance permanent. Terme aligné avec OGC OMS SF_Specimen.

**Ancrage géographique** : pattern TPC `anchorType + anchorId` (station | site),
cohérent avec Deployment. L'ancrage est également hérité via `specimen_deployment`.

**Lien équipements** : via `specimen_deployment` (many-to-many avec Deployment) --
un prélèvement mobilise un ou plusieurs Deployments d'équipements.
Pas de `specimen_system` séparé -- Deployment est le mécanisme universel.

---

## ADR-040 -- Pattern TPC agent universel

**Décision** : `Person` et `Machine` sont deux tables distinctes (TPC).
Le discriminant `agentType + agentId` remplace toutes les FK directes vers Person.

**Tables portant ce pattern** : ValidationBatch, TransformationBatch,
ObservationBatch, TransferFunctionBatch, Memory, Specimen, Responsibility.

**Responsibility** : agentType etendu a `person | organization | machine`.
Roles ISO 19115-1 complets (20 valeurs dont funder, custodian, collaborator...).
`Project.fundingAgency` supprime -- passe par Responsibility.

---

## ADR-041 -- Pattern TPC anchor universel

**Décision** : `anchorType + anchorId` remplace les FK directes vers Station
sur toutes les entités qui peuvent etre rattachees a Observatory, Site ou Station.

**Tables portant ce pattern** : Deployment, Datastream, TimeSerie,
TransformedTimeSerie, TransferFunction, TransferFunctionSet, Specimen.

**Valeurs** : `observatory | site | station`

**Justification** : un drone est ancré sur un Site, pas une Station. Une série
de chimie sans station fixe est ancrée sur un Site. Un bateau peut etre ancré
sur un Observatory. La FK directe vers Station etait trop restrictive.

**Double vérité assumée** : Datastream.anchorType doit etre cohérent avec
l'ancrage du Deployment du System associé. Contrainte applicative verifiable
périodiquement (voir integrity_checks.md).

---

## ADR-042 -- Bundle : renommage depuis TimeSeriesBundle

**Décision** : `TimeSeriesBundle` renommé `Bundle`.

**Justification** : le nom original était trompeur -- un Bundle regroupe aussi
des TransformedTimeSerie, TransferFunction et ControlObservation. `Bundle`
est plus neutre et plus juste pour un regroupement éditorial general.

---

## ADR-043 -- Suppression logique universelle

**Décision** : aucune suppression physique sur les entités référencées.
Trigger `prevent_physical_delete` sur toutes les entités.

**Deux mécanismes selon les tables** :
- Tables avec `status` : utiliser `status` comme mécanisme de désactivation
- Tables sans `status` : `archivedAt TIMESTAMPTZ NULL` (null = actif)

**Tables avec `archivedAt`** : Person, Machine, Organization, Site, Unit, Procedure,
KeywordType, Keyword, License, Location, FeatureOfInterest, Bundle,
Property (a déjà `status=accepted|deprecated|proposed`).

Note : `Project` a à la fois `status` et `archivedAt` dans le modèle v11 --
point ouvert à trancher, préférence pour `status` seul par cohérence avec ADR-043.

**Tables de jointure exemptées** : `person_organization`, `specimen_deployment`,
`transformationbatch_inputseries`, `bundle_serie` -- leurs lignes peuvent etre
supprimées physiquement car elles ne sont pas elles-mêmes référencées.

---

## ADR-044 -- aggregationStatistic et acquisitionType sur les séries

**Décision** : trois nouveaux champs sur Datastream, TimeSerie et
TransformedTimeSerie, alignés ODM2.

**`acquisitionType`** : remplace l'ancien `observationType` -- discrimine
`sensor_continuous` (capteur en continu) et `lab_sample` (analyse laboratoire).

**`aggregationStatistic`** : nature metrologique de la valeur, aligné vocabulaire
ODM2 aggregationStatistic :
```
Instantaneous | Average | Cumulative | Maximum | Minimum |
Variance | StandardDeviation | Sporadic
```
Sporadic = pas de temps irrégulier (ex : accélération lors d'une crue).

**`observationFrequency`** : fréquence nominale ISO 8601, conditionnel --
null si aggregationStatistic=Sporadic. Migré sur TimeSerie et TTS.

**phenomenonTime split** : `phenomenonTime` remplacé par deux colonnes sur
Observation, ValidatedObservation, ControlObservation et Transformation :
- `phenomenonTimeStart 1 TIMESTAMPTZ` -- colonne de partitionnement TimescaleDB
- `phenomenonTimeEnd 0..1 TIMESTAMPTZ` -- null si Instantaneous ou Sporadic

**Contrainte applicative** : phenomenonTimeEnd obligatoire si aggregationStatistic
different de Instantaneous ou Sporadic.

---

## ADR-045 -- ControlObservation : TPC serieType + serieId

**Décision** : `ControlObservation.timeSerie` remplacé par `serieType + serieId`
(pattern TPC), cohérent avec `BundleSerie`.

**Valeurs** : `TimeSerie | TransformedTimeSerie`

**Justification** : une observation de contrôle peut verifier une série mesurée
ou une série calculée. Les deux sont ontologiquement distincts. TPC est le pattern
consistant avec le reste du modèle.

---

## ADR-046 -- Responsibility étendue à System

**Décision** : `System` ajouté au `resourceType` de `Responsibility`.

**Justification** : un instrument physique (capteur, plateforme, équipement) a
des responsabilités institutionnelles propres, indépendamment de la Station sur
laquelle il est déployé : propriétaire (owner), responsable de maintenance
(pointOfContact), entité de garde (custodian). Ces rôles sont temporalisés
(un capteur peut changer de propriétaire lors d'un transfert entre laboratoires)
et multiples (plusieurs contacts selon le rôle). `Responsibility` avec
`validFrom/validTo` couvre ces cas sans colonne spécialisée sur `System`.

**Rôles pertinents sur System** : `owner`, `pointOfContact`, `custodian`,
`originator` (pour un System de type sensor, l'entité qui a produit les données).

**Alignement** : Helmholtz SMS et ODM2 Equipment ont tous deux une notion de
propriétaire et de responsable de calibration sur les instruments.

**Conséquence** : `System` ajouté à la liste `resourceType` de `Responsibility`
dans le modèle (déjà présent en v11 ligne 39). Aucune migration de schéma requise.

---

## Points ouverts pour prochaines sessions

### TRANSFORMATION -- session dédiée recommandée (point majeur)

`TransformationBatch.transferFunctionSet` est actuellement obligatoire (1),
bloquant les cas sans barème structuré dans BDOH.

**Cas à couvrir** :
1. Barème (TransferFunctionSet dans BDOH) -- couvert
2. Agrégation temporelle via fichier config externe (QJXA, paramètres S3/git)
3. Script ad hoc (comblement lacunes, correction chimie)

**Piste validée** : `transferFunctionSet 0..1` + `parameterUrl 0..1`,
contrainte applicative : au moins un des deux renseigné.

**Question architecturale non tranchée** : BDOH exécute-t-il les transformations
(backend Python) ou documente-t-il des transformations exécutées ailleurs ?
Cette décision conditionne l'implémentation.

### SCIENCE OUVERTE

- Incertitude de mesure : `resultUncertainty` sur ValidatedObservation ?
  ODM2 et Helmholtz SMS l'ont -- important pour la reproductibilité scientifique.
- Catalogue et découverte FAIR : DataCite DOI sur Bundle, lien CSW / OGC API Records.

### INTÉGRITÉ -- à implementer

- Triggers `prevent_physical_delete` sur toutes les entités (ADR-043)
- Triggers BEFORE INSERT/UPDATE pour les relations TPC (ADR-004, ADR-040, ADR-041)
- Requêtes de vérification périodique (voir integrity_checks.md)

### DOCUMENTATION

- Régénérer bdoh-doc depuis modele_donnees_v11.md
- Mettre à jour standards/index.md (OGC CS API v1.0, STAMPLATE schema 2025)
- Sections à créer/revoir : instrumentation.md (System+Deployment), rawdata.md
