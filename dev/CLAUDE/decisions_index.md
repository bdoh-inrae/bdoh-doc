# Décisions de conception

Ce journal documente les choix structurants du modèle — pourquoi telle option
a été retenue, quelles alternatives ont été écartées et pour quelle raison.
L'objectif est de rendre le modèle maintenable dans le temps sans avoir à
reconstruire le raisonnement depuis zéro.

---

## ADR-001 — STA comme base, étendu par ODM2

**Décision** : utiliser OGC SensorThings API comme modèle de base et l'enrichir
avec les métadonnées d'ODM2.

**Contexte** : STA est léger, REST/JSON, orienté IoT — mais trop générique pour
les observatoires environnementaux. ODM2 est riche sémantiquement mais daté
technologiquement (XML, WaterOneFlow).

**Choix retenu** : STA pour la structure et l'interface, ODM2 pour la sémantique
des métadonnées environnementales. C'est l'approche de Horsburgh et al. (2024)
avec HydroServer.

**Références** : Horsburgh et al. (2024), *Environmental Modelling and Software*
doi:10.1016/j.envsoft.2024.106241

---

## ADR-002 — TimeSerie comme contrat analytique

**Décision** : la `TimeSerie` porte tout ce qui est fixe pour toute la série —
capteur, variable, protocole analytique, milieu.

**Contexte** : dans STA, le `Datastream` est déjà ce concept. BDOH le renforce
en y attachant `procedure.observation` comme contrat immuable.

**Conséquence** : si un paramètre analytique change, c'est une nouvelle `TimeSerie`.
Le changement de capteur sans impact sur la comparabilité est tracé via
`TimeSerieDatastream`.

---

## ADR-003 — Station vs FeatureOfInterest

**Décision** : distinguer explicitement la `Station` (plateforme physique) de la
`FeatureOfInterest` (entité réelle du monde observée).

**Choix retenu** : la `Station` est le Thing STA. La `FeatureOfInterest` est l'eau
de surface, les sédiments, la nappe. Une même station peut avoir plusieurs FOI.

---

## ADR-004 — Pattern resourceType + resourceId

**Décision** : pattern polymorphique pour les entités transversales (`Memory`,
`Identifier`, `HistoricalLocation`, `HistoricalProject`).

**Choix retenu** : schéma uniforme et extensible. L'intégrité référentielle est
garantie par l'application, pas par la base.

---

## ADR-005 — Historical* : pattern uniforme

**Décision** : toutes les entités `Historical*` partagent la même structure :
`resourceType + resourceId + validFrom + validTo`.

**Choix retenu** : cohérence des requêtes — un développeur qui connaît
`HistoricalLocation` comprend immédiatement les autres.

---

## ADR-006 — Project et HistoricalProject : source de vérité unique

**Décision** : le lien Project → ressources passe uniquement par `HistoricalProject`.

**Choix retenu** : évite les incohérences entre deux sources d'information.
Un même observatoire peut être porté successivement par OSR6, OSR7, OSR8.

---

## ADR-007 — LIMS hors modèle

**Décision** : la chaîne analytique interne au laboratoire est hors modèle.
Le lien se fait via `SamplingFeature.limsReference`.

**Contexte** : `limsReference` est sur `SamplingFeature` (pas sur
`ValidatedObservation`) car c'est le prélèvement qui reçoit un numéro de dossier
LIMS — plusieurs observations peuvent découler du même prélèvement.

---

## ADR-008 — Property : champs directs vs Keyword

**Décision** : `discipline` et `theme` sont des champs directs dans `Property`,
pas des `Keyword`.

**Choix retenu** : enums fixes gérés par les curateurs. `Keyword` reste réservé
à la classification éditoriale pour les catalogues.

---

## ADR-009 — Identifiants : UUID + code lisible

**Décision** : `id` UUID immuable + `code` kebab-case lisible sur toutes les entités.

**Convention** : `{parent.code}-{segment}` → "yzr-mer-d610-no3"

---

## ADR-010 — Deployment : grouper les capteurs co-localisés

**Décision** : entité `Deployment` pour les plateformes multi-capteurs.
`deploymentDepth` sur `Sensor` groupe les capteurs co-localisés.

---

## ADR-011 — SamplingFeature vs FeatureOfInterest

**Décision** :
- `FeatureOfInterest` = entité réelle du monde, stable, avec géométrie
- `SamplingFeature` = acte de prélèvement terrain, événement daté

**Note** : cette distinction couvre les mêmes cas que Proximate/UltimateFOI
de OMS/STA 2.0 draft sans adopter la terminologie non finalisée.

---

## ADR-012 — Property : symbol + code

**Décision** : `code` obligatoire (2-8 cars kebab-case) + `symbol` optionnel
(notation scientifique standard).

---

## ADR-013 — variableType : intensive vs extensive

**Décision** : champ `variableType` explicite sur `Property` pour guider les
calculs de delta.

---

## ADR-014 — Architecture deux couches IoT / backend

**Décision** : une seule base TimescaleDB, deux couches applicatives distinctes.

**Contexte** : BDOH sert une dizaine d'observatoires français (OZCAR/Theia).
Helmholtz a une instance par centre (18 centres indépendants). HydroServer a
une instance centralisée par déploiement. BDOH choisit l'approche centralisée.

**Choix retenu** :
- Couche IoT STA 1.1 : Datastream + Observation (données brutes, raw)
- Couche métier BDOH : TimeSerie + ValidatedObservation (données validées)
- Même base TimescaleDB — TimescaleDB scale largement au-delà des besoins
  d'une dizaine d'observatoires
- Deux API sur la même base : FastAPI (STA) + Django (BDOH métier)

---

## ADR-015 — TimeSerieDatastream remplace HistoricalSensor

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

Contrainte : `datastream` ou `datastreamId` — pas les deux null, pas les deux
renseignés simultanément.

---

## ADR-016 — processingLevel absent du modèle

**Décision** : `processingLevel` supprimé de `TimeSerie` et `TransformedTimeSerie`.

**Contexte** : la structure encode déjà le niveau de traitement :
- `Observation` (IoT) = raw
- `ValidatedObservation` (BDOH) = validated
- `TransformedTimeSerie` (BDOH) = derived

Répéter cette information dans un champ est redondant.

---

## ADR-017 — unitOfMeasurement gardé sur Datastream

**Décision** : BDOH garde `unitOfMeasurement` comme FK vers `Unit` sur `Datastream`,
plutôt que le `resultType` SWE-Common de STA 2.0 draft.

**Contexte** : STA 2.0 (draft non finalisé) remplace `unitOfMeasurement` par
`resultType` (objet SWE-Common JSON). USGS, HydroServer et FROST-Server
gardent `unitOfMeasurement` en production.

**Choix retenu** : STA 2.0 est un draft. `unitOfMeasurement → Unit` est plus
simple, suffisant pour les données environnementales, et aligné avec les
implémentations de référence.

---

## ADR-018 — license + access sur les flux de données

**Décision** : `license 0..1` et `access 1` sur `TimeSerie`, `Datastream`,
`TransformedTimeSerie`. Pas de `license` sur `Observatory`.

**Contexte** : un même observatoire peut avoir des séries en ODbL, CC-BY, ou
fermées. La licence appartient au flux de données, pas au réseau.

**Structure** :
```
license  0..1  "ODbL" | "CC-BY" | "CC-BY-SA" | "proprietary" | ...
access   1     open | restricted | closed | unknown
```

`access` toujours obligatoire — on sait toujours si une donnée est accessible,
même si la licence formelle n'est pas encore définie.

---

## ADR-019 — ValidationBatch pour les sessions de validation

**Décision** : objet `ValidationBatch` séparé pour grouper les observations
validées en une même session.

**Contexte** : sans batch, `validatedBy`, `validatedAt`, `validationLogUrl`
seraient répétés sur chaque `ValidatedObservation` — redondance massive sur
des tables volumineuses.

**Choix retenu** : `ValidationBatch` porte les métadonnées de session.
`ValidatedObservation.validationBatch 0..1` — une observation peut être
validée hors batch (correction ponctuelle).

Les fichiers CSV d'import ne sont pas stockés dans S3 — la base de données
est la source de vérité. `validationLogUrl` pointe vers les logs externes
si ils existent (Wiski, Hydrolab...).

---

## ADR-020 — Validations parallèles et procédure de référence

**Décision** : plusieurs `ValidatedObservation` peuvent coexister pour le même
`phenomenonTime` sur une `TimeSerie` (validation manuelle, pipeline automatique,
IA...). `TimeSerie.referenceValidationProcedure` dit laquelle fait foi.

**Structure** :
```
TimeSerie
  procedure.validation       0..*  procédures autorisées
  referenceValidationProcedure 0..1  laquelle fait foi

ValidatedObservation
  procedure  0..1  procédure ayant produit cette validation
  validationBatch 0..1  session parente
```

**Choix retenu** : pas de champ `isReference` sur l'observation — trop fragile
à maintenir. La procédure de référence est une métadonnée de la `TimeSerie`,
modifiable sans toucher aux observations.

---

## ADR-021 — TransferFunctionSet et HistoricalTransferFunction

**Décision** : refonte complète de la section transformation avec quatre objets
distincts aux rôles clairs.

**Contexte** : l'ancien modèle avec `TransferFunction.validFrom/validTo` ne
permettait pas de gérer la coexistence de plusieurs barèmes ni les cas
identité/manuel.

**Nouveaux objets** :

```
TransferFunction          → fonction pure, pas de date, réutilisable
                            contient des TransferFunctionPoint (couples x/y)

TransferFunctionPoint     → couple (x, y) de calibration empirique
                            ex: (hauteur=1.23m, débit=4.5m³/s)

TransferFunctionSet       → jeu propre à une station + paire de variables
                            isReference dit lequel fait foi parmi plusieurs
                            Contrainte : inputProperty/outputProperty doivent
                            être compatibles avec les TF qu'il référence

HistoricalTransferFunction → lie une TF à un TFSet avec période de validité
                             type : function | identity | manual
                             si identity ou manual → transferFunction null
```

**Analogie avec STA** :
```
TransferFunction     ≈ Datastream (définit le flux)
TransferFunctionPoint ≈ Observation (les valeurs)
TransferFunctionSet  ≈ contrat d'utilisation dans le temps
HistoricalTransferFunction ≈ HistoricalLocation (temporalité)
```

---

## ADR-022 — Transformation : acte de calcul générique

**Décision** : `Transformation` est l'acte de calcul — comme une `Observation`
est un acte de mesure. Peut utiliser un `TransferFunctionSet` ou une `Procedure`
algorithmique pure.

**Structure** :
```
Transformation
  transferFunctionSet  0..1  si calcul empirique (courbe de tarage...)
  procedure            0..1  si algorithme pur (script Python, filtre...)
  inputSeries          1..*
  outputSeries         1 →TTS
  appliedAt / appliedBy / validFrom / validTo
```

Contrainte : `transferFunctionSet` ou `procedure` obligatoire — pas les deux null.

**TransformedTimeSerie** garde `procedure.transformation 0..1` pour le cas
algorithmique pur sans TFSet.

---

## ADR-023 — samplingPeriod sur Property : trois champs

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

## ADR-024 — qualityFlag : vocabulaire unique mappé vers standards

**Décision** : un seul champ `qualityFlag` avec quatre valeurs internes BDOH,
documenté par un mapping vers les standards dans `standards/index.md`.

| BDOH | ODM2 | SANDRE | OGC resultQuality |
|---|---|---|---|
| `good` | Good | 1 Bonne | `good` |
| `suspect` | Suspect | 3 Douteuse | `suspect` |
| `bad` | Bad | 4 Mauvaise | `invalid` |
| `missing` | Missing | lacune | `missing` |

---

## ADR-025 — Instance centralisée nationale

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
- Asymétrie TimeSerie/TransformedTimeSerie :
  changement de TransferFunctionSet de référence →
  recalcul TTS existante ou nouvelle TTS ?
  qui déclenche ? comment tracer dans Transformation ?

SCIENCE OUVERTE
- Incertitude de mesure sur ValidatedObservation
  (resultUncertainty — ODM2, Helmholtz SMS)
- Catalogue et découverte FAIR :
  DataCite DOI sur TimeSeriesBundle,
  lien CSW / OGC API Records

DIVERS
- Plateforme mobile (bateau, drone) :
  HistoricalLocation sur Sensor ? (YAGNI pour l'instant)
- Format CSV d'import : spécification API (pas modèle de données)
- Pipeline de validation automatique : workflow à définir
```
