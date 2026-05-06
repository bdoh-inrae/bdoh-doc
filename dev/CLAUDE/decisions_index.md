# Décisions de conception

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
avec HydroServer.

**Références** : Horsburgh et al. (2024), *Environmental Modelling and Software*
doi:10.1016/j.envsoft.2024.106241

---

## ADR-002 -- TimeSerie comme contrat analytique

**Décision** : la `TimeSerie` porte tout ce qui est fixe pour toute la série --
capteur, variable, protocole analytique, milieu.

**Contexte** : dans STA, le `Datastream` est déjà ce concept. BDOH le renforce
en y attachant `procedure.observation` comme contrat immuable.

**Conséquence** : si un paramètre analytique change, c'est une nouvelle `TimeSerie`.
Le changement de capteur sans impact sur la comparabilité est tracé via
`TimeSerieDatastream`.

---

## ADR-003 -- Station vs FeatureOfInterest

**Décision** : distinguer explicitement la `Station` (plateforme physique) de la
`FeatureOfInterest` (entité réelle du monde observée).

**Choix retenu** : la `Station` est le Thing STA. La `FeatureOfInterest` est l'eau
de surface, les sédiments, la nappe. Une même station peut avoir plusieurs FOI.

---

## ADR-004 -- Pattern resourceType + resourceId

**Décision** : pattern polymorphique pour les entités transversales (`Memory`,
`Identifier`, `HistoricalLocation`, `HistoricalProject`).

**Choix retenu** : schéma uniforme et extensible. L'intégrité référentielle est
garantie par l'application, pas par la base.

---

## ADR-005 -- Historical* : pattern uniforme

**Décision** : toutes les entités `Historical*` partagent la même structure :
`resourceType + resourceId + validFrom + validTo`.

**Choix retenu** : cohérence des requêtes -- un développeur qui connaît
`HistoricalLocation` comprend immédiatement les autres.

---

## ADR-006 -- Project et HistoricalProject : source de vérité unique

**Décision** : le lien Project → ressources passe uniquement par `HistoricalProject`.

**Choix retenu** : évite les incohérences entre deux sources d'information.
Un même observatoire peut être porté successivement par OSR6, OSR7, OSR8.

---

## ADR-007 -- LIMS hors modèle

**Décision** : la chaîne analytique interne au laboratoire est hors modèle.
Le lien se fait via `SamplingFeature.limsReference`.

**Contexte** : `limsReference` est sur `SamplingFeature` (pas sur
`ValidatedObservation`) car c'est le prélèvement qui reçoit un numéro de dossier
LIMS -- plusieurs observations peuvent découler du même prélèvement.

---

## ADR-008 -- Property : champs directs vs Keyword

**Décision** : `discipline` et `theme` sont des champs directs dans `Property`,
pas des `Keyword`.

**Choix retenu** : enums fixes gérés par les curateurs. `Keyword` reste réservé
à la classification éditoriale pour les catalogues.

---

## ADR-009 -- Identifiants : UUID + code lisible

**Décision** : `id` UUID immuable + `code` kebab-case lisible sur toutes les entités.

**Convention** : `{parent.code}-{segment}` → "yzr-mer-d610-no3"

---

## ADR-010 -- Deployment : grouper les capteurs co-localisés

**Décision** : entité `Deployment` pour les plateformes multi-capteurs.
`deploymentDepth` sur `Sensor` groupe les capteurs co-localisés.

---

## ADR-011 -- SamplingFeature vs FeatureOfInterest

**Décision** :
- `FeatureOfInterest` = entité réelle du monde, stable, avec géométrie
- `SamplingFeature` = acte de prélèvement terrain, événement daté

**Note** : cette distinction couvre les mêmes cas que Proximate/UltimateFOI
de OMS/STA 2.0 draft sans adopter la terminologie non finalisée.

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

**Contexte** : BDOH sert une dizaine d'observatoires français (OZCAR/Theia).
Helmholtz a une instance par centre (18 centres indépendants). HydroServer a
une instance centralisée par déploiement. BDOH choisit l'approche centralisée.

**Choix retenu** :
- Couche IoT STA 1.1 : Datastream + Observation (données brutes, raw)
- Couche métier BDOH : TimeSerie + ValidatedObservation (données validées)
- Même base TimescaleDB -- TimescaleDB scale largement au-delà des besoins
  d'une dizaine d'observatoires
- Deux API sur la même base : FastAPI (STA) + Django (BDOH métier)

**Ce qui définit "brut" dans la couche IoT** : une donnée est brute dès lors
qu'elle est telle que mesurée -- sans modification, sans jugement de qualité.
Peu importe le mode d'arrivée :
- capteur télétransmis en continu -> Observation sans batch
- technicien qui récupère des données sur une centrale d'acquisition
  terrain non connectée et les importe manuellement -> Observation via ObservationBatch

Dans les deux cas la donnée est brute. C'est dans la couche métier
(ValidationBatch + ValidatedObservation) que commence le jugement de qualité.

---

## ADR-015 -- TimeSerieDatastream remplace HistoricalSensor

**Décision** : `TimeSerieDatastream` lie une `TimeSerie` à ses `Datastream`
sources successifs dans le temps. `HistoricalSensor` est supprimé.

**Contexte** : le lien pertinent est entre flux de données, pas entre capteurs.
Un changement de capteur = nouveau Datastream dans l'IoT = nouvelle ligne
dans `TimeSerieDatastream`.

**Structure** :
```
TimeSerieDatastream
  datastream  0..1 →DS   FK directe si source interne (même base)
  datastreamId 0..1      UUID si source externe
  sourceUrl   1          URL de base du STA source
  sourceType  1          sta_2.0 | sta_1.1 | other
  validFrom / validTo
```

Contrainte : `datastream` ou `datastreamId` -- pas les deux null, pas les deux
renseignés simultanément.

---

## ADR-016 -- processingLevel absent du modèle

**Décision** : `processingLevel` supprimé de `TimeSerie` et `TransformedTimeSerie`.

**Contexte** : la structure encode déjà le niveau de traitement :
- `Observation` (IoT) = raw
- `ValidatedObservation` (BDOH) = validated
- `TransformedTimeSerie` (BDOH) = derived

Répéter cette information dans un champ est redondant.

---

## ADR-017 -- unitOfMeasurement gardé sur Datastream

**Décision** : BDOH garde `unitOfMeasurement` comme FK vers `Unit` sur `Datastream`,
plutôt que le `resultType` SWE-Common de STA 2.0 draft.

**Contexte** : STA 2.0 (draft non finalisé) remplace `unitOfMeasurement` par
`resultType` (objet SWE-Common JSON). USGS, HydroServer et FROST-Server
gardent `unitOfMeasurement` en production.

**Choix retenu** : STA 2.0 est un draft. `unitOfMeasurement → Unit` est plus
simple, suffisant pour les données environnementales, et aligné avec les
implémentations de référence.

---

## ADR-018 -- license + access sur les flux de données

**Décision** : `license 0..1` et `access 1` sur `TimeSerie`, `Datastream`,
`TransformedTimeSerie`. Pas de `license` sur `Observatory`.

**Contexte** : un même observatoire peut avoir des séries en ODbL, CC-BY, ou
fermées. La licence appartient au flux de données, pas au réseau.

**Structure** :
```
license  0..1  "ODbL" | "CC-BY" | "CC-BY-SA" | "proprietary" | ...
access   1     open | restricted | closed | unknown
```

`access` toujours obligatoire -- on sait toujours si une donnée est accessible,
même si la licence formelle n'est pas encore définie.

---

## ADR-019 -- ValidationBatch pour les sessions de validation

**Décision** : objet `ValidationBatch` séparé pour grouper les observations
validées en une même session.

**Contexte** : sans batch, `validatedBy`, `validatedAt`, `validationLogUrl`
seraient répétés sur chaque `ValidatedObservation` -- redondance massive sur
des tables volumineuses.

**Choix retenu** : `ValidationBatch` porte les métadonnées de session.
`ValidatedObservation.validationBatch 0..1` -- une observation peut être
validée hors batch (correction ponctuelle).

Les fichiers CSV d'import ne sont pas stockés dans S3 -- la base de données
est la source de vérité. `validationLogUrl` pointe vers les logs externes
si ils existent (Wiski, Hydrolab...).

---

## ADR-020 -- TimeSerie : une procédure de validation unique

**Décision** : `procedure.validation` est unique et obligatoire sur `TimeSerie`.
`referenceValidationProcedure` est supprimé.

**Contexte** : l'ancien modèle permettait plusieurs `ValidatedObservation`
parallèles pour le même instant sur une même `TimeSerie`, avec
`referenceValidationProcedure` pour désigner laquelle fait foi.

**Choix retenu** : une procédure par série. Plusieurs validations parallèles
sur la même variable et la même station = plusieurs `TimeSerie` distinctes.
La `Station` est le point de regroupement naturel -- on filtre par
`(station, property, procedure)` pour naviguer entre séries concurrentes.

**Conséquence** : `ValidatedObservation` ne porte plus de `procedure` --
elle est portée par la `TimeSerie` parente. `ValidationBatch.procedure`
également supprimé -- la cohérence est garantie par le choix de la
`TimeSerie` cible au moment du dépôt.

---

## ADR-021 -- TransferFunction analogue à TimeSerie

**Décision** : `TransferFunction` est repositionnée comme analogue à
`TimeSerie` -- elle est liée à une station et porte les données
(points de calibration).

**Contexte** : l'ancien modèle traitait `TransferFunction` comme une fonction
pure réutilisable sans ancrage physique. En pratique une courbe de tarage
est toujours liée à une section de rivière précise.

**Analogie complète** :
```
TimeSerie              <-> TransferFunction
ValidationBatch        <-> TransformationBatch
ValidatedObservation   <-> TransformedObservation
TransformedTimeSerie      (inchangé, output final)
```

**Objets supprimés** : `HistoricalTransferFunction` (remplacé par
`validFrom/validTo` directement sur `TransferFunctionSet`).
`Transformation` renommée `TransformationBatch`.

**`TransferFunction`** gagne : `station 1`, `code`, `startDate`, `endDate`,
`status`, `responsibility`, `identifier`, `memory`.
Perd : `operator`.

**`TransferFunctionSet`** : conteneur obligatoire même pour une seule TF.
`isReference` supprimé -- plusieurs TFSet coexistent sans hiérarchie imposée.
`inputProperty`/`outputProperty` supprimés -- portés par `TransferFunction`.

---

## ADR-022 -- TransformationBatch et TransformedObservation

**Décision** : `Transformation` renommée `TransformationBatch`, nouvel objet
`TransformedObservation` pour les points calculés.

**Contexte** : cohérence avec le pattern `ValidationBatch` /
`ValidatedObservation` côté observation.

**Structure** :
```
TransformationBatch
  transformedTimeSerie  1 ->TTS
  transferFunctionSet   1 ->TFS
  inputSeries           1..* ->TS
  appliedAt / appliedBy / validFrom / validTo / status / comment

TransformedObservation
  transformedTimeSerie  1 ->TTS
  transformationBatch   0..1 ->TB
  phenomenonTime / result / qualityFlag
```

---

## ADR-023 -- samplingPeriod sur Property : trois champs

**Décision** : `samplingPeriod` remplacé par trois champs sur `Property`.

**Contexte** : plusieurs cas d'usage incompatibles avec un seul champ :
- Année hydrologique complète décalée (09-01 → 08-31)
- Période partielle fixe (05-01 → 11-30, été climatique)
- Période dynamique basée sur min/max de la variable

**Structure** :
```
samplingPeriodStart  0..1  MM-JJ début de période    "09-01"
samplingPeriodEnd    0..1  MM-JJ fin, null=année complète  "08-31"
samplingPeriodMode   0..1  calcul dynamique           min | max
```

Contrainte : `samplingPeriodStart` ou `samplingPeriodMode` doit être renseigné.

---

## ADR-024 -- qualityFlag : vocabulaire unique mappé vers standards

**Décision** : un seul champ `qualityFlag` avec quatre valeurs internes BDOH,
documenté par un mapping vers les standards dans `standards/index.md`.

| BDOH | ODM2 | SANDRE | OGC resultQuality |
|---|---|---|---|
| `good` | Good | 1 Bonne | `good` |
| `suspect` | Suspect | 3 Douteuse | `suspect` |
| `bad` | Bad | 4 Mauvaise | `invalid` |
| `missing` | Missing | lacune | `missing` |

---

## ADR-025 -- Instance centralisée nationale

**Décision** : une seule instance BDOH centralisée pour tous les observatoires
français, pas une instance par observatoire.

**Contexte** : Helmholtz a une instance par centre (contraintes légales
allemandes sur la localisation des données). BDOH n'a pas ces contraintes.
TimescaleDB scale largement au-delà des besoins de 10 observatoires.

**Choix retenu** : instance centralisée INRAE. Si un observatoire veut son
propre IoT séparé, `TimeSerieDatastream.sourceUrl` permet de pointer vers
n'importe quel STA externe sans modifier le modèle.

---

## Points ouverts

```
TRANSFORMATION
- Transformation algorithmique pure :
  Une TransformedTimeSerie peut être produite sans TransferFunctionSet
  (agrégation temporelle, filtre, script Python, correction offset...).
  TransformationBatch.transferFunctionSet est actuellement obligatoire (1),
  ce qui exclut ces cas. Deux options : passer à 0..1 avec contrainte
  applicative (soit transferFunctionSet soit procedure.transformation obligatoire),
  ou confirmer hors périmètre v1 (YAGNI).
  A trancher avant toute implémentation de TransformationBatch.

- Série de référence entre TransformedTimeSerie concurrentes :
  Plusieurs TTS peuvent coexister sur la même station et la même variable
  sans hiérarchie formelle (isReference supprimé, ADR-021).
  Décision actée : pas de désignation de référence dans le modèle,
  c'est le contexte scientifique et l'expertise technique qui tranchent,
  comme pour les TimeSerie concurrentes (ADR-020).
  Voir ADR-026.

SCIENCE OUVERTE
- Incertitude de mesure sur ValidatedObservation
  (resultUncertainty -- ODM2, Helmholtz SMS)
- Catalogue et découverte FAIR :
  DataCite DOI sur TimeSeriesBundle,
  lien CSW / OGC API Records

DIVERS
- Plateforme mobile (bateau, drone) :
  HistoricalLocation sur Sensor ? (YAGNI pour l'instant)
- Format CSV d'import : spécification API (pas modèle de données)
- Pipeline de validation automatique : workflow à définir
```

---

## ADR-026 -- Coexistence sans hiérarchie des TransformedTimeSerie

**Décision** : plusieurs `TransformedTimeSerie` peuvent coexister sur la même
station et la même variable sans qu'aucune soit désignée "de référence" dans
le modèle. Aucun champ `isReference` n'est ajouté.

**Contexte** : un opérateur externe peut fournir un débit calculé avec sa propre
procédure de transformation, pendant que BDOH produit le sien via son pipeline
de tarage. Les deux coexistent légitimement. Le `code` (unique par Station) et
le `status` permettent de naviguer entre elles.

**Choix retenu** : même principe que pour `TimeSerie` (ADR-020) -- la Station
est le point de regroupement, c'est le contexte scientifique et l'expertise
technique qui désignent laquelle utiliser selon le besoin. Le modèle ne tranche
pas à la place des scientifiques.

**Conséquence** : les URLs API permettent de lister toutes les TTS d'une station
pour une variable donnée. La désignation de référence est une métadonnée
éditoriale, pas une contrainte du modèle de données.

---

## ADR-027 -- code slug obligatoire avec scopes d'unicité

**Décision** : `code` est obligatoire (`1`) sur toutes les entités. Il est unique
dans son scope parent (pas globalement sauf pour les entités racines). Il est
modifiable par l'utilisateur. Une suggestion automatique est proposée à la
création depuis `name` (ou `serialNumber` pour Sensor et Equipment).

**Contexte** : l'UUID est la clé technique immuable, exposée via un permalink
stable (`/resources/{uuid}`) adapté aux citations scientifiques. Le `code` est
le slug lisible pour les URLs courantes de l'API et l'interface utilisateur.
Les codes externes (SANDRE, TheiaOZCAR, WIGOS...) passent par `identifier`.

**Scopes d'unicité** :
- Unique globalement : Observatory, Organization, Sensor, Equipment, Project,
  Procedure, Property, Unit
- Unique par Observatory : Site
- Unique par Site : Station
- Unique par Station : Deployment, TimeSerie, Datastream, TransferFunction,
  TransformedTimeSerie

**Conséquence** : suppression des conventions de code auto-généré
({station.code}-{property.code}-{procedure.code}) dans les notes des entités.
Ces conventions restent des suggestions indicatives dans la documentation
utilisateur, pas des contraintes du modèle. `serialNumber` sur Sensor et
Equipment reste distinct du `code` -- c'est la valeur brute fabricant,
le `code` en est le slug normalisé.

---

## ADR-028 -- Relations inverses absentes des tableaux BDD

**Décision** : les relations inverses (listes 0..*) ne sont jamais des champs
dans les tableaux des entités. Elles sont accessibles via requête sur la table
qui porte la FK.

**Contexte** : plusieurs entités portaient des champs comme `responsibility 0..*`,
`historicalProject 0..*`, `historicalLocation 0..*`, `equipment 0..*` -- ces
champs n'existent pas en BDD, ce sont des vues API. Le modèle documente des
tables, pas des vues.

**Règle** : si une entité B pointe vers une entité A via une FK, A ne liste pas
B dans son tableau. L'accès se fait par requête `WHERE resource_id={id}`.
Seule exception : les snapshots courants (`location 1 →Loc`, `sensor 1 →Sen`)
qui sont de vraies FK directes pour accès rapide.

---

## ADR-029 -- ResourceInstrument : jointure temporalisée pour les instruments

**Décision** : `ResourceInstrument` remplace tous les liens directs entre
ressources et instruments (Sensor, Equipment).

**Contexte** : un capteur ou un équipement peut être utilisé successivement
sur plusieurs stations, déploiements, séries temporelles ou prélèvements.
Les liens directs ne permettent pas de tracer cette mobilité dans le temps.

**Structure** :
```
ResourceInstrument
  resourceType   Station | TimeSerie | Deployment | SamplingFeature
  resourceId     uuid
  instrumentType sensor | equipment
  instrumentId   uuid
  deploymentDepth 0..1
  depthReference  0..1
  validFrom       0..1
  validTo         0..1
```

**Ce qui est supprimé** :
- `Sensor.deployment`, `Sensor.deploymentDepth`, `Sensor.depthReference`,
  `Sensor.laboratory`
- `TimeSerie.deployment`
- `Station.equipment`, `Deployment.equipment`
- `responsibility 0..*` sur toutes les entités (géré via Responsibility polymorphique)

**Ce qui est gardé** :
- `TimeSerie.sensor 1` -- snapshot courant du capteur actif, accès rapide
- `Responsibility.resourceType` étendu à `Equipment` et `Sensor`

---

## ADR-030 -- Système de vocabulaires contrôlés via quadriptyque Keyword

**Décision** : tous les vocabulaires contrôlés évolutifs passent par un
quadriptyque de tables : `KeywordType`, `Keyword`, `KeywordAssignment`,
`KeywordRequirement`. Les enums SQL restent uniquement pour les valeurs
techniques fixes qui conditionnent du code applicatif.

**Contexte** : les champs enum comme `discipline`, `theme`, `samplingMedium`,
`stationType`, `sensorType` etc. nécessitent une gouvernance par les curateurs
sans migration de schéma. Une table unique de vocabulaire contrôlé avec
discriminant de type est plus flexible et extensible qu'une table par vocabulaire
(approche ODM2) ou des enums SQL rigides.

**Structure du quadriptyque** :
- `KeywordType` : types de métadonnées, alignés avec les standards (ISO 19115, ODM2...)
- `Keyword` : termes bilingues (fr/en) alignés avec des thésaurus externes autant que possible
- `KeywordAssignment` : lien polymorphique multi-valeurs entre keyword et ressource
- `KeywordRequirement` : règles de complétion minimale configurables sans migration

**Deux usages de Keyword** :
1. Via `KeywordAssignment` -- toutes les classifications (discipline, theme,
   stationType, sensorType...) -- mono ou multi-valeur
2. Les valeurs courantes de chaque keywordType sont documentées dans les notes
   des entités, pas hardcodées dans le schéma

**Champs supprimés des entités** (passent en KeywordAssignment) :
Organization.type, Site.type, Station.type, Deployment.type, Sensor.type,
Equipment.type, FeatureOfInterest.type, Memory.type, ControlObservation.type,
Property.discipline, Property.theme, Property.samplingMedium,
TimeSerie.sampledMedium, SamplingFeature.specimenType, SamplingFeature.medium,
TimeSeriesBundle.theme

**Enums SQL conservés** (conditionnent du code) :
qualityFlag, status, validationMode, transmissionMode, depthReference,
instrumentType, codeType, Procedure.type, origin, TransferFunctionSet.type

**Alignement FAIR** : chaque Keyword doit idéalement avoir une URI vers un
thésaurus reconnu (ODM2, TheiaOZCAR, SANDRE, NERC...). Les termes BDOH sans
équivalent externe utilisent thesaurus='BDOH' et devraient être publiés
avec des URIs persistantes.

---

## ADR-031 -- License obligatoire sur les flux de données

**Décision** : `License` devient une table de référence gérée par les
administrateurs BDOH. Le champ `license` est obligatoire (1) sur
Datastream, TimeSerie, TransformedTimeSerie et TimeSeriesBundle.

**Contexte** : les anciens champs `license 0..1` (enum) et `access 1` (enum)
étaient redondants et trop rigides. L'accès est implicite dans la licence --
une CC-BY est ouverte, une licence contractuelle est fermée.

**Structure** :
```
License : id, code, name, url
```

**Conséquence** : `access` supprimé de toutes les entités.
Les administrateurs BDOH gèrent la liste des licences disponibles.

---

## ADR-032 -- TimeSerieDatastream simplifié

**Décision** : `TimeSerieDatastream` ne supporte que les Datastreams internes
à BDOH. Les champs `datastreamId`, `sourceUrl`, `sourceType` sont supprimés.

**Contexte** : le cas "source externe STA tiers" n'est pas dans le périmètre v1.
Si on adopte BDOH, on adopte tout le stack. La complexité multi-source
est reportée en v2.

**Structure simplifiée** :
```
TimeSerieDatastream : id, timeSerie 1->TS, datastream 1->DS, validFrom, validTo
```

---

## ADR-033 -- Procedure.type : ajout de aggregation

**Décision** : `Procedure.type` gagne la valeur `aggregation` pour documenter
les procédures d'agrégation temporelle ou spatiale.

**Contexte** : l'agrégation (QJXA, cumuls pluviométriques...) est un cas
distinct de la transformation -- elle produit une nouvelle variable depuis
une TimeSerie existante selon des règles de calcul documentées.

**Valeurs complètes** :
```
sampling | observation | modeling | aggregation | transformation | validation
```

---

## ADR-034 -- Sensor et Equipment indépendants du contexte

**Décision** : Sensor et Equipment ne portent aucun champ de contexte
d'utilisation. Tous les champs contextuels passent dans InstrumentUsage.

**Champs supprimés de Sensor** :
`deployment`, `deploymentDepth`, `depthReference`, `laboratory`

**Champs portés par InstrumentUsage** :
`deploymentDepth`, `depthReference`, `validFrom`, `validTo`

**Conséquence** : un capteur peut être utilisé sur plusieurs ressources
successivement sans ambiguïté. TimeSerie garde `sensor 1` comme snapshot
courant pour accès rapide.

---

## ADR-035 -- ObservationBatch pour les imports manuels terrain

**Décision** : `ObservationBatch` est optionnel sur `Observation`.
Il est créé uniquement quand un technicien importe manuellement des données
récupérées sur une centrale d'acquisition terrain non connectée.

**Contexte** : un capteur télétransmis en continu ne crée pas de batch --
ce serait absurde de créer un batch par mesure. Le batch existe quand
il y a un acte humain ou une sync groupée qui mérite d'être tracée.

---

## Points ouverts -- TRANSFORMATION (session dédiée recommandée)

**Problème central** : `TransformationBatch.transferFunctionSet 1` obligatoire
bloque les cas sans barème structuré dans BDOH.

**Cas à couvrir** :
1. Barème (TransferFunctionSet dans BDOH) -- couvert
2. Agrégation via fichier config externe (QJXA, paramètres S3/git)
3. Script ad hoc (comblement lacunes, correction chimie)

**Piste** : `transferFunctionSet 0..1` + `parameterUrl 0..1`,
contrainte applicative : au moins un des deux renseigné.

**Question architecturale non tranchée** : BDOH exécute-t-il les
transformations (backend Python) ou documente-t-il des transformations
exécutées ailleurs ? Cette décision conditionne l'implémentation.
