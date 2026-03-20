# Observation

---

## FeatureOfInterest

Aligné avec : STA FeatureOfInterest, OGC O&M domainFeature

Utilisé par : [ValidatedObservation](#validatedobservation) (featureOfInterest), [ControlObservation](#controlobservation) (featureOfInterest)

!!! note
    Entité réelle du monde observée — cours d'eau, nappe, sol, atmosphère.
    **Distincte de la [Station](network.md#station)** (Thing STA) qui porte les capteurs.
    Une même Station peut observer plusieurs FeatureOfInterest différentes.

    Convention de code : `{nom-court-entité}-{type-ou-milieu}`
    Exemples : "mercier-eau-surf", "mercier-sed", "yzeron-bv", "p12-nappe-a"

| Champ          | Cardinalité  | Définition                              | Valeurs possibles                                                          |
|----------------|--------------|-----------------------------------------|----------------------------------------------------------------------------|
| `id`           | 1            | Identifiant technique, clé primaire     | uuid                                                                       |
| `code`         | 1            | Code court unique, saisi par curateur   | "mercier-eau-surf" \| "yzeron-bv"                                          |
| `name`         | 1            | Nom de l'entité observée                | "Eau de surface du Mercier"                                                |
| `description`  | 0..1         | Description libre                       |                                                                            |
| `type`         | 1            | Type d'entité                           | `river` \| `lake` \| `groundwater` \| `soil` \| `atmosphere` \| `wetland` |
| `encodingType` | 1            | Type d'encodage (conformité STA)        | "application/geo+json"                                                     |
| `geometry`     | 1            | Emprise GeoJSON de l'entité             | `Point` \| `Polygon` \| `LineString`                                       |
| `identifier`   | 0..* →Ident  | Codes externes et PID                   | → [Identifier](references.md#identifier)[]                                 |

---

## TimeSerie

Aligné avec : STA Datastream

Utilisé par : [Station](network.md#station) (timeSeries), [ValidatedObservation](#validatedobservation) (timeSerie), [ControlObservation](#controlobservation) (timeSerie), [TransferFunction](transformation.md#transferfunction) (inputSeries), [Transformation](transformation.md#transformation) (inputSeries)

!!! note
    Porte tout ce qui est fixe et commun à toute la série.
    **Contrat analytique** garantissant la comparabilité de tous les points.

    Code généré : `{station.code}-{property.code}` ex: "yzr-mer-d610-hea"

| Champ                   | Cardinalité    | Définition                                    | Valeurs possibles                                                                        |
|-------------------------|----------------|-----------------------------------------------|------------------------------------------------------------------------------------------|
| `id`                    | 1              | Identifiant technique, clé primaire           | uuid                                                                                     |
| `code`                  | 1              | Code généré depuis station + property.code    | "yzr-mer-d610-hea"                                                                       |
| `name`                  | 1              | Nom lisible de la série                       | "Hauteur d'eau — Mercier au pont D610"                                                   |
| `description`           | 0..1           | Description libre                             |                                                                                          |
| `station`               | 1 →Sta         | Station de rattachement                       | → [Station](network.md#station)                                                          |
| `sensor`                | 1 →Sen         | Instrument actif (snapshot courant)           | → [Sensor](instrumentation.md#sensor)                                                    |
| `deployment`            | 0..1 →Dep      | Déploiement auquel appartient cette série     | → [Deployment](instrumentation.md#deployment)                                            |
| `property`              | 1 →Prop        | Variable mesurée                              | → [Property](references.md#property)                                                     |
| `unit`                  | 1 →Unit        | Unité de mesure                               | → [Unit](references.md#unit)                                                             |
| `procedure.observation` | 1 →Proc        | Protocole analytique fixe pour toute la série | → [Procedure](references.md#procedure) (type=observation)                                |
| `procedure.validation`  | 0..1 →Proc     | Règles de validation des données              | → [Procedure](references.md#procedure) (type=validation)                                 |
| `processingLevel`       | 1              | Niveau de traitement                          | `raw` \| `validated` \| `derived`                                                       |
| `sampledMedium`         | 1              | Milieu échantillonné (CV ODM2)                | `surfaceWater` \| `groundwater` \| `soil` \| `sediment` \| `poreWater` \| `atmosphere` |
| `observationType`       | 1              | Mode d'acquisition                            | `sensor_continuous` \| `lab_sample`                                                     |
| `startDate`             | 1              | Date de début de la série                     | "1997-01-14T08:01:00Z"                                                                   |
| `endDate`               | 0..1           | Date de fin, null si active                   | null                                                                                     |
| `status`                | 1              | État de la série                              | `active` \| `inactive` \| `discontinued`                                                |
| `license`               | 1              | Licence des données                           | `ODbL` \| `CC-BY` \| `CC-BY-SA`                                                         |
| `historicalSensor`      | 0..* →HistSen  | Succession des instruments                    | → [HistoricalSensor](instrumentation.md#historicalsensor)[]                              |
| `historicalProject`     | 0..* →HistProj | Succession des projets porteurs               | → [HistoricalProject](project.md#historicalproject)[]                                    |
| `keyword`               | 0..* →Keyw     | Keywords thématiques pour catalogues          | → [Keyword](references.md#keyword)[]                                                     |
| `identifier`            | 0..* →Ident    | Codes externes et PID                         | → [Identifier](references.md#identifier)[]                                               |
| `memory`                | 0..* →Mem      | Notes et événements                           | → [Memory](organisation.md#memory)[]                                                     |

---

## ValidatedObservation

Aligné avec : STA Observation

Utilisé par : [TimeSerie](#timeserie) (observations)

!!! note
    Un point de mesure de la série avec son contexte de validation.
    Optionnellement rattaché à un prélèvement terrain (`lab_sample` uniquement).

| Champ               | Cardinalité  | Définition                                          | Valeurs possibles                             |
|---------------------|--------------|-----------------------------------------------------|-----------------------------------------------|
| `id`                | 1            | Identifiant technique, clé primaire                 | uuid                                          |
| `timeSerie`         | 1 →TS        | Série parente                                       | → [TimeSerie](#timeserie)                     |
| `datetime`          | 1            | Horodatage de la mesure                             | "2024-03-15T09:30:00Z"                        |
| `result`            | 1            | Valeur numérique mesurée                            | "2.4"                                         |
| `qualityFlag`       | 1            | Indicateur qualité                                  | `good` \| `suspect` \| `bad` \| `missing`    |
| `qualityComment`    | 0..1         | Justification du flag qualité                       | "pic de crue suspect"                         |
| `validatedBy`       | 0..1 →Per    | Personne ayant validé                               | → [Person](actors.md#person)                  |
| `validatedAt`       | 0..1         | Date de validation                                  | "2024-03-20T14:00:00Z"                        |
| `limsReference`     | 0..1         | Identifiant externe dans le LIMS                    | "LIMS-2024-03-001"                            |
| `samplingFeature`   | 0..1 →SF     | Prélèvement terrain associé (lab_sample uniquement) | → [SamplingFeature](#samplingfeature)         |
| `featureOfInterest` | 0..1 →FOI    | Entité réelle observée                              | → [FeatureOfInterest](#featureofinterest)     |

---

## ControlObservation

Utilisé par : [TimeSerie](#timeserie) (controlObservations)

!!! note
    Observation de contrôle qualité — blanc terrain, duplicate, étalon.
    Structure parallèle à [ValidatedObservation](#validatedobservation) avec rôle QC explicite.

| Champ                | Cardinalité  | Définition                                      | Valeurs possibles                                      |
|----------------------|--------------|-------------------------------------------------|--------------------------------------------------------|
| `id`                 | 1            | Identifiant technique, clé primaire             | uuid                                                   |
| `timeSerie`          | 1 →TS        | Série parente                                   | → [TimeSerie](#timeserie)                              |
| `datetime`           | 1            | Horodatage                                      | "2024-03-15T09:30:00Z"                                 |
| `type`               | 1            | Type de contrôle                                | `field_blank` \| `duplicate` \| `standard` \| `spike` |
| `result`             | 1            | Valeur mesurée                                  | "0.02"                                                 |
| `expectedResult`     | 0..1         | Valeur théorique pour étalon                    | "0.00"                                                 |
| `qualityFlag`        | 1            | Résultat du contrôle                            | `pass` \| `warn` \| `fail`                            |
| `sensor`             | 0..1 →Sen    | Instrument si différent de la TimeSerie         | → [Sensor](instrumentation.md#sensor)                  |
| `procedure.control`  | 1 →Proc      | Protocole QC appliqué                           | → [Procedure](references.md#procedure) (type=control)  |
| `samplingFeature`    | 0..1 →SF     | Prélèvement terrain associé                     | → [SamplingFeature](#samplingfeature)                  |
| `featureOfInterest`  | 0..1 →FOI    | Entité réelle observée                          | → [FeatureOfInterest](#featureofinterest)              |

---

## SamplingFeature

Aligné avec : STA FeatureOfInterest (specimen), ODM2 Specimen

Utilisé par : [ValidatedObservation](#validatedobservation) (samplingFeature), [ControlObservation](#controlobservation) (samplingFeature)

!!! note
    Acte de prélèvement terrain. Présent uniquement pour les séries de type `lab_sample`.
    La chaîne analytique interne au laboratoire est hors modèle — le lien se fait via `limsReference` sur [ValidatedObservation](#validatedobservation).

| Champ                 | Cardinalité  | Définition                                         | Valeurs possibles                                                             |
|-----------------------|--------------|----------------------------------------------------|-------------------------------------------------------------------------------|
| `id`                  | 1            | Identifiant technique, clé primaire                | uuid                                                                          |
| `datetime`            | 1            | Horodatage du prélèvement                          | "2024-03-15T09:30:00Z"                                                        |
| `project`             | 0..1 →Proj   | Projet ou campagne dont dépend ce prélèvement      | → [Project](project.md#project)                                               |
| `specimenType`        | 1            | Type de matériau prélevé (CV ODM2)                 | `water` \| `soil` \| `sediment` \| `poreWater` \| `rock` \| `biological`     |
| `medium`              | 1            | Milieu de prélèvement (CV ODM2)                    | `surfaceWater` \| `groundwater` \| `depth` \| `interstitial`                 |
| `depth`               | 0..1         | Profondeur de prélèvement en mètres                | "0.30"                                                                        |
| `volume`              | 0..1         | Volume prélevé en litres                           | "1.0"                                                                         |
| `filtrationOnSite`    | 0..1         | Filtration effectuée sur le terrain                | `true` \| `false`                                                             |
| `filtrationThreshold` | 0..1         | Seuil de filtration en µm                          | "0.45"                                                                        |
| `operator`            | 0..1 →Per    | Personne ayant effectué le prélèvement             | → [Person](actors.md#person)                                                  |
| `equipment`           | 0..1 →Equip  | Matériel de collecte utilisé                       | → [Equipment](instrumentation.md#equipment)                                   |
| `location`            | 0..1 →Loc    | Position exacte si différente de la Station        | → [Location](geography.md#location)                                           |
| `condition`           | 0..1         | Observations terrain libres                        | "turbidité élevée, eau brune"                                                 |
| `derivedFrom`         | 0..1 →SF     | Specimen parent si sous-échantillon                | → [SamplingFeature](#samplingfeature)                                         |
| `identifier`          | 0..* →Ident  | Codes externes et PID                              | → [Identifier](references.md#identifier)[]                                    |
