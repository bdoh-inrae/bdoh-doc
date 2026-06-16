# Décisions de conception BDOH

Ce journal documente les choix structurants du modèle -- pourquoi telle option
a été retenue, quelles alternatives ont été écartées et pour quelle raison.
L'objectif est de rendre le modèle maintenable dans le temps sans avoir à
reconstruire le raisonnement depuis zéro.

Comment lire ce fichier. Chaque décision vivante porte son raisonnement : la
décision, le contexte, le choix retenu, et pourquoi il ne faut pas le rouvrir à
la légère. Les décisions remplacées par une décision ultérieure sont regroupées
en fin de fichier (section « Décisions remplacées »), pour ne pas couper le fil
de lecture sept fois. Les invariants structurels les plus porteurs sont rappelés
dans `CLAUDE.md`, chacun avec un renvoi vers son ADR.

Un ADR est un **instantané daté** de la décision. Quand il énumère des tables ou
des valeurs (par exemple les tables portant un pattern, ou les tables à `status`
contre `archivedAt`), cette liste reflète l'état au moment de la décision. La
liste courante, elle, fait foi dans `modele_donnees_v12.md` ; on ne resynchronise
pas un ADR a posteriori pour suivre une évolution du modèle.

---

## ADR-001 -- STA comme base, étendu par ODM2

**Décision** : utiliser OGC SensorThings API comme modèle de base et l'enrichir
avec les métadonnées d'ODM2.

**Contexte** : STA est léger, REST/JSON, orienté IoT -- mais trop générique pour
les observatoires environnementaux. ODM2 est riche sémantiquement mais daté
technologiquement (XML, WaterOneFlow).

**Choix retenu** : STA pour la structure et l'interface, ODM2 pour la sémantique
des métadonnées environnementales. C'est l'approche de Horsburgh et al. (2024)
avec HydroServer. STA 1.1 reste la référence de production ; STA 2.0 et OGC CS
API sont surveillés pour la v2 (état daté de ces standards : voir sources.md).

**Références** : Horsburgh et al. (2024), *Environmental Modelling and Software*
doi:10.1016/j.envsoft.2024.106241

---

## ADR-002 -- TimeSeries comme contrat analytique

**Décision** : la `TimeSeries` porte tout ce qui est fixe pour toute la série --
variable, protocole analytique, milieu.

**Contexte** : dans STA, le `Datastream` est déjà ce concept. BDOH le renforce
en y attachant `procedureObservation` comme contrat immuable.

**Conséquence** : si un paramètre analytique change, c'est une nouvelle `TimeSeries`.
Le changement de capteur sans impact sur la comparabilité est tracé via
`TimeSeriesSource` (ex-`TimeSerieDatastream` puis `HistoricalDatastream`,
renommé ADR-036 puis ADR-048).

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

## ADR-009 -- Identifiants : UUID + code lisible

**Décision** : `id` UUID immuable + `code` kebab-case lisible sur toutes les entités.

**Convention** : suggestion automatique depuis `name` (ou `serialNumber` pour System).

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
**Couche métier BDOH** : TimeSeries + ValidatedObservation (données validées).

**API** : deux vues sur la même base -- FastAPI (STA) + Django (BDOH metier).
L'API STA expose /Sensors comme vue filtrée `System WHERE systemType='sensor'`.
La FOI est absente de la couche IoT -- portée par Station et TimeSeries (ADR-038).

---

## ADR-016 -- processingLevel absent du modèle

**Décision** : `processingLevel` supprimé. La structure encode le niveau :
- `Observation` (IoT) = raw
- `ValidatedObservation` (BDOH) = validated
- `TransformedTimeSeries` (BDOH) = derived

---

## ADR-017 -- unitOfMeasurement gardé sur Datastream

**Décision** : BDOH garde `unitOfMeasurement` comme FK vers `Unit` sur `Datastream`,
plutôt que le `resultType` SWE-Common de STA 2.0.

---

## ADR-019 -- ValidationBatch pour les sessions de validation

**Décision** : objet `ValidationBatch` séparé pour grouper les observations
validées en une même session. `ValidatedObservation.validationBatch 0..1`.

---

## ADR-020 -- TimeSeries : une procédure de validation unique

**Décision** : `procedureValidation` est unique et obligatoire sur `TimeSeries`.
Plusieurs validations parallèles = plusieurs `TimeSeries` distinctes.

---

## ADR-021 -- TransferFunction analogue à TimeSeries

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

## ADR-026 -- Coexistence sans hiérarchie des TransformedTimeSeries

**Décision** : plusieurs `TransformedTimeSeries` coexistent sans `isReference`.
Le contexte scientifique et l'expertise technique désignent laquelle utiliser.

---

## ADR-027 -- code slug obligatoire avec scopes d'unicité

**Décision** : `code` obligatoire sur toutes les entités, unique dans son scope.

**Scopes** :
- Unique globalement : Observatory, Organization, System, Project, Procedure,
  Property, Unit
- Unique par Observatory : Site
- Unique par Site : Station
- Unique par ancre : TimeSeries, Datastream, TransferFunction, TransformedTimeSeries

---

## ADR-028 -- Relations inverses absentes des tableaux BDD

**Décision** : les relations inverses (0..*) ne sont jamais des colonnes dans
les tableaux. Accessibles via requête sur la table qui porte la FK.

---

## ADR-030 -- Système de vocabulaires contrôlés via quadriptyque Keyword

**Décision** : tous les vocabulaires contrôlés évolutifs passent par
`KeywordType`, `Keyword`, `KeywordAssignment`, `KeywordRequirement`.

---

## ADR-031 -- License obligatoire sur les flux de données

**Décision** : `License` table obligatoire (1) sur Datastream, TimeSeries,
TransformedTimeSeries et Bundle (renommé depuis TimeSeriesBundle, ADR-042).

---

## ADR-033 -- Procedure.type : ajout de aggregation puis analysis

**Décision** : `Procedure.type` inclut `aggregation` pour les agrégations
temporelles (QJXA, cumuls...) et `analysis` pour les analyses laboratoire sur
Specimen (dosages chimiques, mesures ex situ).

**Valeurs complètes** :
```
sampling | observation | analysis | modeling | aggregation | transformation | validation
```

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
HistoricalDatastream : id, timeSeries 1->TS, datastream 1->DS, validFrom, validTo
```

**Rôle** : couture entre le monde physique (System -> Deployment -> Datastream)
et le monde analytique (TimeSeries -> ValidatedObservation).

**Note historique (post-ADR-048)** : cette entité a été renommée une seconde
fois en `TimeSeriesSource` lors de la passe de consolidation v12 -- voir
ADR-048 pour la règle de nommage des associations datées qui justifie ce
second renommage.

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
- `TimeSeries` de position : position continue (trajectoire drone, profileur
  autonome) -- property=position, aggregationStatistic=Instantaneous

**Références** : OGC CS API v1.0, SOSA/SSN, SensorML

---

## ADR-038 -- FOI dans la couche métier uniquement

**Décision** : `featureOfInterest` absente de `Datastream` et `Observation`
(couche IoT). Portée par `Station` (FOI ultime), `TimeSeries` et
`TransformedTimeSeries` (FOI proximate optionnelle).

**Règle de résolution API STA** :
```
FOI exposée = TimeSeries.featureOfInterest si renseignée
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

**Ancrage géographique** : pattern TPC `anchorType + anchorId` (Station | Site),
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

**Tables portant ce pattern** : Deployment, Datastream, TimeSeries,
TransformedTimeSeries, TransferFunction, TransferFunctionSet, Specimen.

**Valeurs** : `Observatory | Site | Station`

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
des TransformedTimeSeries, TransferFunction et ControlObservation. `Bundle`
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

Note : `Project` a à la fois `status` et `archivedAt` dans le modèle v12 --
point ouvert à trancher, préférence pour `status` seul par cohérence avec ADR-043.

**Tables de jointure exemptées** : `person_organization`, `specimen_deployment`,
`transformationbatch_inputseries`, `bundle_series` -- leurs lignes peuvent etre
supprimées physiquement car elles ne sont pas elles-mêmes référencées.

---

## ADR-044 -- aggregationStatistic et acquisitionType sur les séries

**Décision** : trois nouveaux champs sur Datastream, TimeSeries et
TransformedTimeSeries, alignés ODM2.

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
null si aggregationStatistic=Sporadic. Migré sur TimeSeries et TTS.

**phenomenonTime split** : `phenomenonTime` remplacé par deux colonnes sur
Observation, ValidatedObservation, ControlObservation et Transformation :
- `phenomenonTimeStart 1 TIMESTAMPTZ` -- colonne de partitionnement TimescaleDB
- `phenomenonTimeEnd 0..1 TIMESTAMPTZ` -- null si Instantaneous ou Sporadic

**Contrainte applicative** : phenomenonTimeEnd obligatoire si aggregationStatistic
different de Instantaneous ou Sporadic.

---

## ADR-045 -- ControlObservation : TPC seriesType + seriesId

**Décision** : `ControlObservation.timeSeries` remplacé par `seriesType + seriesId`
(pattern TPC), cohérent avec `bundle_series`.

**Valeurs** : `TimeSeries | TransformedTimeSeries`

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
dans le modèle (déjà présent dans la liste `resourceType` de `Responsibility`).
Aucune migration de schéma requise.

---

## ADR-047 -- Pattern TPC unifié à quatre déclinaisons

**Décision** : formaliser le pattern TPC comme **mécanisme unique** du modèle,
décliné en quatre usages explicites.

**Contexte** : ADR-004 (TPC resource), ADR-040 (TPC agent) et ADR-041 (TPC anchor)
avaient été posés séparément. Le modèle utilise en réalité le même mécanisme
(`xxxType + xxxId` avec intégrité applicative) dans quatre contextes différents.
La documentation, en particulier le passage entre les notions de « table
polymorphique » et de « pattern TPC », créait une ambiguïté de vocabulaire pour
un même objet.

**Choix retenu** : un mécanisme, quatre déclinaisons nommées de façon homogène :
- **TPC resource** (`resourceType + resourceId`) -- rattacher une donnée
  transverse à n'importe quelle ressource (Identifier, Memory, Responsibility,
  KeywordAssignment, HistoricalLocation, HistoricalProject).
- **TPC anchor** (`anchorType + anchorId`) -- ancrer une entité à un contexte
  géographique (Deployment, Datastream, TimeSeries, TransformedTimeSeries,
  TransferFunction, TransferFunctionSet, Specimen).
- **TPC agent** (`agentType + agentId`) -- désigner l'acteur d'un acte
  (ValidationBatch, TransformationBatch, ObservationBatch, TransferFunctionBatch,
  Memory, Specimen, Responsibility).
- **TPC series** (`seriesType + seriesId`) -- pointer vers une série ou une
  fonction (bundle_series, ControlObservation). C'est cette quatrième déclinaison
  qui était la moins visible avant cette consolidation.

**Conséquence** : la documentation du modèle pose le pattern TPC une fois en
introduction, puis présente les quatre déclinaisons comme des variantes. Le
mot « polymorphique » reste autorisé comme synonyme explicatif d'introduction,
mais le pattern lui-même est nommé TPC partout.

**Justification philosophique** : agent_TPC_philosophie_synthese.md reste la
référence sur le choix de TPC vs TPH/TPT. Cette unification n'est pas une
nouvelle décision technique mais la mise en cohérence du vocabulaire.

---

## ADR-048 -- Associations datées : règle de nommage Historical* vs nom de rôle

**Décision** : poser une règle de nommage générale pour les tables d'association
datée du modèle (toutes celles qui portent `validFrom` / `validTo`), et
renommer `HistoricalDatastream` en `TimeSeriesSource` en application de cette
règle.

**Contexte** : le modèle a plusieurs tables structurellement identiques --
(entité cible) + (valeur ou entité liée) + (`validFrom` / `validTo`) -- mais
nommées de deux façons. Le préfixe `Historical*` (HistoricalLocation,
HistoricalProject) et des noms par le rôle (Deployment, TransferFunctionSet,
Responsibility). `HistoricalDatastream` portait le préfixe `Historical*` mais
ne jouait pas le rôle que ce préfixe annonce, ce qui induisait en erreur sur
sa fonction.

**Règle posée** :
- Préfixe `Historical*` : la table historise un **attribut courant** d'une
  ressource (la ressource « a » cet attribut à tout instant, la table garde la
  trace des valeurs passées). Cas : HistoricalLocation, HistoricalProject.
- Nom décrivant le **rôle** : la table relie deux entités dans le temps sans
  qu'aucune ne soit l'attribut courant de l'autre. Cas : TimeSeriesSource,
  Deployment, TransferFunctionSet, Responsibility.

La structure (`validFrom` / `validTo`) est commune dans les deux cas. Le nom
doit refléter le jeu de rôle réel de la table, pas une apparence formelle.

**Conséquence sur le modèle** : `HistoricalDatastream` renommé `TimeSeriesSource`
(les sources successives, ou simultanées, d'une TimeSeries). ADR-036 amendé
d'une note historique. Le tableau d'entités du modèle, les notes des entités
référencées, le diagramme et les requêtes type sont mis à jour.

**Justification philosophique** : la cohérence visée n'est pas typographique
(tous les noms se ressemblent) mais d'usage (chaque nom dit la vérité sur le
rôle de la table). Une table qui ne joue pas le jeu de langage annoncé par son
préfixe est mal nommée, indépendamment de la régularité de la convention.

---

## ADR-049 -- Keyword.notation : identifiant SKOS pour la publication du vocabulaire

**Décision** : ajouter un champ `notation` obligatoire (1) sur `Keyword`,
destiné à servir de segment d'URI pour la publication du vocabulaire BDOH.

**Contexte** : avant cette décision, `Keyword` était identifié par son `id`
(uuid, technique) et désigné par ses libellés bilingues `term_fr` / `term_en`
(lisibles mais modifiables). Aucun champ ne pouvait servir à construire une
URI publiable de manière stable. Or BDOH a vocation à publier son vocabulaire
en SKOS pour permettre l'interopérabilité et la citation des termes (Theia/OZCAR,
ENVRI-Hub).

**Choix retenu** :
- `notation` est un identifiant court en `kebab-case` (`surface-water`,
  `stream-gage`), unique par `keywordType`.
- Suggéré automatiquement à la création depuis `term_en` (slugification :
  minuscules, accents et caractères spéciaux retirés, espaces remplacés par
  des tirets).
- **Immuable après création** : contrairement au `code` des autres entités,
  `notation` ne change plus une fois posée, car des URIs publiques peuvent en
  dépendre.

**Alignement** : équivalent direct de `skos:notation`. Une publication SKOS
future du vocabulaire BDOH mappe `notation` sur `skos:notation`,
`term_fr` / `term_en` sur `skos:prefLabel`, `uri` sur l'identifiant du
concept, `definition_*` sur `skos:definition`.

**Justification du choix obligatoire** : un identifiant rattrapé après coup
crée des risques d'incohérence quand des URIs ont déjà été construites
autrement. Imposer `notation` dès la création évite cette dette technique.

**Conséquence sur la convention de casse** : les exemples de termes
(« Keywords attendus » dans les notes d'entités) sont en `term_en` lisible
(« surface water »), pas en `snake_case` (« surface_water »). Le `kebab-case`
n'apparaît que sur `notation`.

---

## ADR-050 -- Bornes temporelles des flux comme propriétés calculées

**Décision** : les bornes temporelles d'un flux de données (la période couverte
par les observations) ne sont **plus stockées** comme colonnes sur Datastream,
TimeSeries et TransformedTimeSeries. Elles deviennent des **propriétés
calculées** à la demande, exposées en lecture seule par l'API.

**Contexte** : le modèle portait `Datastream.startTime/endTime` et
`TimeSeries.startDate/endDate` (et l'équivalent sur TransformedTimeSeries) comme
colonnes stockées. Cette information est en réalité dérivée des observations
rattachées au flux (`MIN/MAX` du `phenomenonTime`), donc soumise à un risque
permanent de désynchronisation : il fallait recalculer ces colonnes à chaque
ajout ou suppression d'observation, ce qui crée une dette d'intégrité.

**Choix retenu** :
- Les colonnes `startTime/endTime` (Datastream) et `startDate/endDate`
  (TimeSeries, TransformedTimeSeries) sont supprimées du schéma.
- À l'API, deux propriétés calculées sont exposées sur chaque flux :
```
phenomenonTimeStart = MIN(phenomenonTimeStart) des observations du flux
phenomenonTimeEnd   = MAX(phenomenonTimeEnd ou phenomenonTimeStart) des observations
```
- Le nom `phenomenonTime` est repris de STA pour rendre l'export STA direct
  (recomposition de l'intervalle unique `phenomenonTime` du Datastream STA).

**Justification de la faisabilité** : le calcul `MIN/MAX` est peu coûteux
parce que `phenomenonTimeStart` est la colonne de partitionnement temporel
TimescaleDB des tables d'observations. TimescaleDB connaît les bornes de
chaque chunk sans scanner les données. Sur PostgreSQL nu, ce choix serait
discutable ; ici il est techniquement sain.

**Conséquence pour le futur** : si un besoin de performance imposait un jour
de matérialiser ces valeurs, ce serait une dénormalisation explicite à
documenter, pas le mode par défaut.

**Distinction avec d'autres bornes temporelles** : seules les bornes
*de couverture* d'un flux deviennent calculées. Les bornes d'existence
d'entités (Observatory, Project, TransferFunction) restent des données saisies
sur ces entités, sous le nom `validFrom/validTo` pour les associations datées
et `startDate/endDate` pour les durées d'existence d'entité (cf. règle générale
de nommage temporel).

---

## ADR-051 -- TransformationBatch : moteur d'exécution unifié

**Décision** : `TransformationBatch` devient le mécanisme universel pour toute
transformation, qu'elle applique un barème stocké ou un algorithme externe.
`transferFunctionSet` passe à `0..1`. Deux champs obligatoires ajoutés :
`runner 1 →Machine` (le système qui exécute) et `algorithm 1 →Algorithm`
(le code qui tourne). `parameters 0..1` (JSON ou référence vers un fichier
de paramétrage externe) porte la configuration d'exécution propre au batch.

**Contexte** : `transferFunctionSet` était obligatoire (1), forçant toute
transformation à passer par un jeu de fonctions de transfert. Or l'agrégation,
le comblement de lacunes, le ré-échantillonnage et la correction n'ont pas de
fonction de transfert stockée.

**Familles de transformation couvertes** : agrégation, ré-échantillonnage,
comblement de lacunes, correction, application de barème (via `transferFunctionSet`),
combinaison multi-séries (plusieurs entrées + rôles dans `parameters`).

**`transformationbatch_inputseries`** : étendu en TPC series (`seriesType` +
`seriesId`) pour accepter `TimeSeries` et `TransformedTimeSeries` en entrée.

**`TransformedTimeSeries.recalculationMode`** (`auto`|`manual`) : contrôle le
déclenchement du recalcul quand une série source change.

---

## ADR-052 -- Algorithm : objet dédié pour le code versionné

**Décision** : nouvel objet `Algorithm` (section 8. TRANSFORMATION) pour
référencer le code exécuté par un `TransformationBatch`. Séparation claire entre
`Machine` (le système qui tourne) et `Algorithm` (le code qui tourne dessus).

**Champs clés** : `codeRepository` (URL de la forge), `path` (script dans le
dépôt), `version` (tag git par convention), `swhid` (Software Heritage, épingle
la version exacte), `doi` (publication si elle existe).

**Règle de versionnement** : une version de code = une ligne `Algorithm`. Le
`swhid` est immuable par ligne. `status` (`active`|`superseded`|`deprecated`)
désigne la version courante pour un `name` donné. Contrainte d'unicité sur
`swhid` quand non-null.

**`Machine`** allégé en conséquence : ne porte plus les métadonnées du code
(migrées sur `Algorithm`), uniquement l'identité du système qui tourne
(`name`, `description`, `serviceUrl`).

**Justification** : un runner peut exécuter plusieurs algorithmes différents ;
le même algorithme peut tourner sur plusieurs runners. Les deux sont des objets
distincts avec des cycles de vie distincts.

---

## ADR-053 -- TransferFunctionSet refondation : réservoir de TF + jointure datée

**Décision** : refonte du cluster TF. `TransferFunctionSet` ne porte plus de
FK directe vers `TransferFunction`. La composition est portée par une nouvelle
table de jointure `transferfunctionset_function` (`tfSet`, `tf`, `validFrom`,
`validTo`). Les champs `type` (identity|manual|function) et `validFrom`/`validTo`
sont supprimés de `TransferFunctionSet`.

**Conséquence** : une même `TransferFunction` peut appartenir à plusieurs TFSet
(réservoir). La succession temporelle des courbes dans un barème est portée par
la jointure, pas par les objets eux-mêmes. La temporalité "vecteurs de paramètres
qui évoluent dans le temps" est ainsi gratuite : une TF par période via la
jointure, des paramètres par période.

**Sur `TransferFunction`** : `validFrom`/`validTo` retirés (la période d'application
est dans la jointure) ; remplacés par `acquisitionStart`/`acquisitionEnd` (période
d'acquisition des données de calibration). Le JSON `parameters` retiré et
remplacé par `TransferFunctionParameter` (voir ADR-056).

---

## ADR-054 -- TTS vivante, fork curé, Dataset pour la citation

**Décision** : `Transformation` est l'état courant, sans versionnement
automatique. Un recalcul écrase les valeurs. Les batches archivés constituent
le journal de méthode. La reproductibilité totale (figer aussi les entrées)
n'est pas une promesse de BDOH.

**Fork curé** : quand un état de calcul a une valeur scientifique durable
(comparaison de barèmes, version ayant servi à une publication), le curateur
crée une TTS coexistante avant de recalculer. Analogie git : une lignée diverge
volontairement. Pas d'objet nouveau, ADR-026 l'autorise déjà.

**Dataset** (voir ADR-055) : pour les états publiés avec un DOI, c'est `Dataset`
qui porte le snapshot figé, pas une TTS fork.

---

## ADR-055 -- Dataset : reçu d'export vers entrepôt externe

**Décision** : nouvel objet `Dataset`. Ce n'est pas un conteneur de données
mais un **reçu d'export** : BDOH calcule le snapshot au vol, l'envoie à
l'entrepôt (Dataverse, RDG, Zenodo), et ne le conserve pas. La reproductibilité
repose sur l'entrepôt, pas sur BDOH.

**BDOH n'archive pas.** Il met à disposition et crée des données. Les snapshots
figés citables vivent sur l'entrepôt externe.

**Structure** : `title`, `exportedAt`, `temporalCoverageStart`/`End` (fenêtre
globale, calculée si non saisie), `sourceBundle 0..1`, `repositoryUrl 0..1`.
Ressources via `dataset_resource` (TPC series). DOI via `Identifier`.

**Mapping DataCite** : commun à `Bundle` et `Dataset`, documenté dans la section
*Mapping DataCite* en tête de section 9. La quasi-totalité des propriétés
obligatoires est dérivable du modèle ; seul `abstract` est à stocker.

**Compteur de réutilisation** : compter les `Dataset` incluant une ressource
donne le nombre d'exports la citant. Partiel par construction (ne couvre que
les exports passés par la passerelle BDOH), assumé comme tel.

**Distinction Bundle/Dataset** : Bundle = suivi éditorial vivant, interne.
Dataset = citation figée, sortante, référence un dépôt externe immuable.

---

## ADR-056 -- TransferFunctionParameter : dualité empirique/modèle sur TransferFunction

**Décision** : nouvel objet `TransferFunctionParameter`, frère de
`TransferFunctionPoint`. Chaque ligne est un coefficient du modèle ajusté
avec sa loi marginale d'incertitude (`distributionType`, `distributionParam1`,
`distributionParam2`). Le JSON `parameters` est retiré de `TransferFunction`.

**Dualité** : `TransferFunctionPoint` = face empirique (jaugeages, couples x/y
terrain) ; `TransferFunctionParameter` = face modèle (coefficients avec
distribution). `TransferFunctionBatch` = acte de calage.

**Covariance** : `TransferFunction.covariance` (JSON) porte la matrice de
covariance entre coefficients. Seul blob JSON résiduel justifié : une matrice
dense ne se décompose pas naturellement en lignes.

**Générateur d'ensemble** : lignes `TransferFunctionParameter` + matrice
`covariance` constituent le générateur complet pour la propagation ensembliste
d'incertitude (spaghetti BaRatin) sans stocker les tirages.

**Alignement** : GUM (JCGM 100:2008) pour l'expression de l'incertitude ;
BaRatin / Le Coz et al. 2014 pour le cadre bayésien. Objet voué à évoluer
avec l'état de l'art sans casser la structure.

---

## ADR-057 -- Incertitude sur les valeurs : bornes asymétriques optionnelles

**Décision** : ajout de `uncertaintyLow 0..1` / `uncertaintyHigh 0..1` sur
`ValidatedObservation` et `Transformation` (bornes asymétriques de l'incertitude
propagée). Ajout de `uncertaintyX 0..1` / `uncertaintyY 0..1` sur
`TransferFunctionPoint` (incertitude sur le jaugeage lui-même, deux composantes
distinctes nécessaires pour BaRatin).

**Trois niveaux** :
- Niveau 1 (bornes sur les valeurs) : les champs ci-dessus, optionnels.
- Niveau 2 (générateur) : `TransferFunctionParameter` + `covariance` (ADR-056).
- Niveau 3 (propagation) : un `TransformationBatch` ordinaire dont l'algorithme
  propage l'incertitude. Aucun objet nouveau.

**Justification** : l'incertitude sur un débit calculé est asymétrique et
variable dans le temps (dépend du point de fonctionnement sur la courbe et de
l'incertitude de la hauteur en entrée, voir Le Coz et al. 2014). Un `± x`
constant ne suffit pas.

---

## ADR-058 -- Frontière enum SQL / Keyword : grille de décision formalisée

**Décision** : formaliser le critère de choix entre enum SQL et Keyword dans
une section dédiée du modèle (*Choix enum SQL ou vocabulaire Keyword*, section
introductive avant KeywordType).

**Grille** : reste enum SQL si les trois conditions sont vraies, sinon Keyword :
(1) le code branche sur la valeur (logique de calcul, contrainte ou résolution
de FK changent selon la valeur) ; (2) l'ensemble est petit et fermé ; (3) ajouter
une valeur est un acte de développement, pas de curation.

**Application** : tous les enums actuels restent en SQL. `aggregationStatistic`
examiné comme candidat Keyword, gardé SQL : le calcul et l'interprétation
dépendent du type (`sporadic` conditionne `observationFrequency`). `Procedure.type`
gardé SQL : garde-fou structurel (la bonne procédure au bon emplacement).
L'option hybride (épine SQL + queue Keyword) écartée comme inélégante.

**Note** : l'invariant 5 de `CLAUDE.md` (vocabulaires évolutifs via Keyword)
reste valide ; cette décision en précise le critère, elle ne le contredit pas.

---

## ADR-059 -- Chaîne analytique labo : AnalysisBatch + AnalysisObservation

**Décision** : modéliser la chimie de laboratoire par deux nouveaux objets,
frères des Batch et observations existants, sans étendre `Deployment` ni
créer de table ad hoc.

**AnalysisBatch** : l'acte analytique (quel Specimen, quelle méthode, quel
appareil, qui, quand). Frère de `ValidationBatch`, `TransformationBatch`...
même famille, même pattern TPC agent. Porte les métadonnées de session.

**AnalysisObservation** : la valeur mesurée sur le Specimen, symétrique de
`ValidatedObservation` pour la couche lab_sample. Pointe vers sa `TimeSeries`
parente (flux unifiant portant property, unité, license) et son `AnalysisBatch`.
Porte les métadonnées propres à la mesure individuelle (LD, LQ, qualityFlag,
uncertainty). Pas d'unité propre : c'est sur la TimeSeries.

**Chaîne CUAHSI** (collecte, préparation, analyse) : portée par la filiation
des Specimens (`derivedFrom`) plus un `AnalysisBatch` par étape analytique.
Pas de hiérarchie de Batch.

**Coexistence LIMS/interne** : si la chimie est traitée dans un LIMS externe,
`Specimen.limsReference` suffit et `AnalysisBatch` n'est pas créé. Si la
chaîne analytique est interne, `AnalysisBatch` + `AnalysisObservation` la
documentent complètement. Les deux voies sont non exclusives. ADR-007 amendé
en conséquence : "LIMS externe possible **ou** chaîne interne, au choix".

**`Procedure.type`** : valeur `analysis` ajoutée (voir ADR-033 amendé).

**Alignement** : ODM2 LabAnalyses + CUAHSI Specimen Actions. L'`AnalysisObservation`
correspond au Measurement Result ODM2, l'`AnalysisBatch` à l'Action d'analyse.

---

## Décisions remplacées

Ces décisions ont été remplacées par une décision ultérieure. Leur numéro est
conservé pour que les références anciennes restent résolvables ; le raisonnement
à jour est dans la décision qui les remplace.

| ADR | Objet | Remplacée par |
|---------|------------------------------------------|-------------------------------------------|
| ADR-008 | `discipline` / `theme` sur Property      | ADR-030 (quadriptyque Keyword)            |
| ADR-010 | Deployment (version initiale)            | ADR-037 (System + Deployment récursif)    |
| ADR-015 | TimeSerieDatastream                      | ADR-036 puis ADR-048 (TimeSeriesSource)   |
| ADR-018 | `license` / `access` en colonnes         | ADR-031 (table License obligatoire)       |
| ADR-029 | InstrumentUsage                          | ADR-037 (System + Deployment récursif)    |
| ADR-032 | TimeSerieDatastream (structure)          | ADR-036 puis ADR-048 (TimeSeriesSource)   |
| ADR-034 | Sensor / Equipment séparés               | ADR-037 (fusion dans System)              |

---

## Renvois

Les décisions non tranchées (chantiers de conception A1 à A7, décisions en
attente, ambiguïtés locales, veille standards) sont dans `points_ouverts.md`.
Les tâches d'implémentation (intégrité applicative, régénération de la
documentation, ingestion) sont dans `CLAUDE.md`, et le détail des triggers et
requêtes d'intégrité dans `integrity_checks.md`. Ce fichier ne les duplique pas.
