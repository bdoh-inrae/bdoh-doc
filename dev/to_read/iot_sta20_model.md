# Modèle IoT STA 2.0 — Entités minimales

## Principes

Ce modèle décrit les entités du système IoT STA 2.0 de BDOH.
Il est **aligné avec OGC SensorThings API 2.0** et conçu pour être
le plus simple possible pour les techniciens terrain.

Trois règles fondamentales :
- **Minimal** : chaque entité ne porte que ce dont l'IoT a besoin
- **Raw** : les observations sont brutes, sans qualité, sans validation
- **Indépendant** : fonctionne sans le backend BDOH

Le lien avec le backend BDOH se fait via `TimeSerieDatastream` —
chaque `Datastream` IoT est référencé par une `TimeSerie` BDOH.

## Correspondance IoT ↔ Backend BDOH

| IoT STA 2.0         | Backend BDOH        | Lien                              |
|---------------------|---------------------|-----------------------------------|
| `Thing`             | `Station`           | Station.thingId + sourceUrl       |
| `Sensor`            | `Sensor`            | Sensor.sensorId + sourceUrl       |
| `ObservedProperty`  | `Property`          | Property.observedPropertyId       |
| `Procedure`         | `Procedure`         | partagé directement               |
| `Datastream`        | `TimeSerie`         | TimeSerieDatastream               |
| `FeatureOfInterest` | `FeatureOfInterest` | partagé ou référencé              |
| `SamplingFeature`   | `SamplingFeature`   | SamplingFeature.iotSfId           |
| `Observation`       | `ValidatedObservation` | via phenomenonTime + datastreamId |
| `Location`          | `Location`          | partagé directement               |

---

## Convention de lecture

| Notation   | Signification                  |
|------------|-------------------------------|
| `1`        | Obligatoire, exactement un    |
| `0..1`     | Optionnel, zéro ou un         |
| `1..*`     | Un ou plusieurs               |
| `0..*`     | Zéro ou plusieurs             |

---

## 1. PLATEFORME

### Thing
Aligné avec : STA 2.0 Thing
Note : tout objet physique capable de mesurer — station fixe, bouée,
       plateforme mobile, drone instrumenté.
       Dans BDOH, correspond à une Station avec thingId pour faire le lien.

| Champ         | Cardinalité | Définition                              | Valeurs possibles                                        |
|---------------|-------------|-----------------------------------------|----------------------------------------------------------|
| `id`          | 1           | Identifiant unique                      | uuid                                                     |
| `name`        | 1           | Nom du Thing                            | "Mercier au pont D610"                                   |
| `description` | 0..1        | Description libre                       | "Station hydrométrique sur le Mercier"                   |
| `properties`  | 0..1        | Métadonnées libres JSON                 | {"type": "streamgage", "elevation": 312.5}               |
| `location`    | 1 →Loc      | Position courante                       | → Location                                               |
| `datastream`  | 0..* →DS    | Flux de données associés                | → Datastream[]                                           |

---

### Location
Aligné avec : STA 2.0 Location
Note : position géographique du Thing. Partagé avec le backend BDOH
       — même objet, même UUID.

| Champ          | Cardinalité | Définition                          | Valeurs possibles                    |
|----------------|-------------|-------------------------------------|--------------------------------------|
| `id`           | 1           | Identifiant unique                  | uuid                                 |
| `name`         | 1           | Nom du lieu                         | "Station Mercier D610"               |
| `description`  | 0..1        | Description libre                   |                                      |
| `encodingType` | 1           | Type d'encodage                     | "application/geo+json"               |
| `location`     | 1           | Géométrie GeoJSON                   | `Point` \| `Polygon` \| `LineString` |

---

## 2. INSTRUMENTATION

### Sensor
Aligné avec : STA 2.0 Sensor
Note : capteur individuel attaché à un Datastream.
       Dans BDOH, correspond à un Sensor avec sensorId pour faire le lien.
       Les métadonnées riches (calibration, laboratoire, historique)
       sont dans le backend BDOH — pas ici.

| Champ          | Cardinalité | Définition                            | Valeurs possibles                                |
|----------------|-------------|---------------------------------------|--------------------------------------------------|
| `id`           | 1           | Identifiant unique                    | uuid                                             |
| `name`         | 1           | Nom du capteur                        | "OTT PLS 500 SN-2023-00412"                      |
| `description`  | 0..1        | Description libre                     |                                                  |
| `encodingType` | 1           | Type d'encodage de la fiche technique | "application/pdf" \| "text/html"                 |
| `metadata`     | 1           | URI vers la fiche technique           | "https://www.ott.com/products/water-level/..."   |
| `properties`   | 0..1        | Métadonnées libres JSON               | {"make": "OTT", "model": "PLS 500", "serialNumber": "SN-2023-00412"} |

---

### ObservedProperty
Aligné avec : STA 2.0 ObservedProperty
Note : version minimale de Property BDOH pour l'IoT.
       Contient uniquement ce dont le Datastream a besoin.
       Les métadonnées riches (discipline, theme, aggregationType...)
       sont dans Property BDOH.

| Champ         | Cardinalité | Définition                              | Valeurs possibles                               |
|---------------|-------------|-----------------------------------------|-------------------------------------------------|
| `id`          | 1           | Identifiant unique                      | uuid                                            |
| `name`        | 1           | Nom de la variable                      | "Hauteur d'eau"                                 |
| `definition`  | 1           | URI vers vocabulaire contrôlé           | "https://w3id.org/ozcar-theia/c_xxx"            |
| `description` | 0..1        | Description libre                       | "Hauteur d'eau mesurée par capteur de pression" |

---

### Procedure
Aligné avec : STA 2.0 Procedure
Note : protocole de mesure appliqué par le Sensor dans le Datastream.
       Partagé avec le backend BDOH — même objet, même UUID.

| Champ          | Cardinalité | Définition                       | Valeurs possibles                      |
|----------------|-------------|----------------------------------|----------------------------------------|
| `id`           | 1           | Identifiant unique               | uuid                                   |
| `name`         | 1           | Nom du protocole                 | "Mesure hauteur pression OTT"          |
| `description`  | 0..1        | Description libre                |                                        |
| `encodingType` | 1           | Type d'encodage                  | "application/pdf" \| "text/plain"      |
| `metadata`     | 0..1        | URI vers le document du protocole| "https://..."                          |

---

## 3. OBSERVATION

### Datastream
Aligné avec : STA 2.0 Datastream
Note : flux de données pour un unique Thing + Sensor + ObservedProperty.
       Un changement de capteur crée un nouveau Datastream.
       Dans BDOH, plusieurs Datastreams successifs sont agrégés
       en une TimeSerie via TimeSerieDatastream.

| Champ               | Cardinalité  | Définition                              | Valeurs possibles                                                                        |
|---------------------|-------------|------------------------------------------|------------------------------------------------------------------------------------------| 
| `id`                | 1           | Identifiant unique                       | uuid                                                                                     |
| `name`              | 1           | Nom du flux                              | "Hauteur d'eau — Mercier D610 — OTT PLS 500"                                             |
| `description`       | 0..1        | Description libre                        |                                                                                          |
| `observationType`   | 1           | Type de résultat                         | "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement"                  |
| `unitOfMeasurement` | 1           | Unité de mesure                          | {"name": "metre", "symbol": "m", "definition": "http://qudt.org/vocab/unit/M"}           |
| `phenomenonTime`    | 0..1        | Période couverte par le flux             | "2024-01-01T00:00:00Z/2024-12-31T23:59:59Z"                                              |
| `resultTime`        | 0..1        | Période de production des résultats      | "2024-01-01T00:00:00Z/2024-12-31T23:59:59Z"                                              |
| `thing`             | 1 →Thing    | Plateforme source                        | → Thing                                                                                  |
| `sensor`            | 1 →Sen      | Capteur source                           | → Sensor                                                                                 |
| `observedProperty`  | 1 →ObsProp  | Variable mesurée                         | → ObservedProperty                                                                       |
| `procedure`         | 0..1 →Proc  | Protocole de mesure                      | → Procedure                                                                              |
| `observation`       | 0..* →Obs   | Observations du flux                     | → Observation[]                                                                          |

---

### FeatureOfInterest
Aligné avec : STA 2.0 FeatureOfInterest
Note : entité réelle observée par le Datastream.
       Version minimale de FeatureOfInterest BDOH.
       Peut être partagé avec le backend BDOH (même UUID)
       ou référencé depuis BDOH via featureOfInterestId.

| Champ          | Cardinalité | Définition                       | Valeurs possibles                                                          |
|----------------|-------------|----------------------------------|----------------------------------------------------------------------------|
| `id`           | 1           | Identifiant unique               | uuid                                                                       |
| `name`         | 1           | Nom de l'entité observée         | "Eau de surface du Mercier"                                                |
| `description`  | 0..1        | Description libre                |                                                                            |
| `encodingType` | 1           | Type d'encodage                  | "application/geo+json"                                                     |
| `feature`      | 1           | Géométrie GeoJSON de l'entité    | `Point` \| `Polygon` \| `LineString`                                       |

---

### SamplingFeature
Aligné avec : OGC O&M Specimen, ODM2 Specimen
Note : prélèvement terrain enregistré dans l'IoT au moment de la collecte.
       Enrichi dans le backend BDOH avec les métadonnées complètes
       (operator, equipment, filtration, limsReference...).
       Le lien BDOH se fait via SamplingFeature.iotSfId.

| Champ          | Cardinalité | Définition                          | Valeurs possibles                                                         |
|----------------|-------------|-------------------------------------|---------------------------------------------------------------------------|
| `id`           | 1           | Identifiant unique                  | uuid                                                                      |
| `name`         | 0..1        | Nom ou code du prélèvement          | "SF-2024-03-15-001"                                                       |
| `description`  | 0..1        | Description libre                   | "Prélèvement eau surface Mercier"                                         |
| `encodingType` | 1           | Type d'encodage de la position      | "application/geo+json"                                                    |
| `feature`      | 1           | Position exacte du prélèvement      | `Point` GeoJSON                                                           |
| `sampledAt`    | 1           | Horodatage du prélèvement           | "2024-03-15T09:30:00Z"                                                    |
| `specimenType` | 0..1        | Type de matériau prélevé            | `water` \| `soil` \| `sediment` \| `poreWater` \| `rock` \| `biological` |
| `datastream`   | 0..1 →DS    | Datastream associé si mesure terrain| → Datastream                                                              |

---

### Observation
Aligné avec : STA 2.0 Observation
Note : valeur brute horodatée — raw, sans qualityFlag, sans validation.
       La validation est entièrement dans le backend BDOH
       via ValidatedObservation.
       Le lien BDOH se fait via phenomenonTime + datastreamId.

| Champ               | Cardinalité | Définition                                     | Valeurs possibles                                                     |
|---------------------|-------------|------------------------------------------------|-----------------------------------------------------------------------|
| `id`                | 1           | Identifiant unique                             | uuid                                                                  |
| `phenomenonTime`    | 1           | Instant ou période du phénomène (STA standard) | "2024-03-15T09:30:00Z" \| "2024-03-15T09:00:00Z/09:30:00Z"          |
| `resultTime`        | 1           | Instant d'enregistrement du résultat           | "2024-03-15T09:30:05Z"                                                |
| `result`            | 1           | Valeur brute mesurée                           | 4.523                                                                 |
| `datastream`        | 1 →DS       | Flux de données parent                         | → Datastream                                                          |
| `featureOfInterest` | 1 →FOI      | Entité réelle observée                         | → FeatureOfInterest                                                   |
| `samplingFeature`   | 0..1 →SF    | Prélèvement terrain associé                    | → SamplingFeature                                                     |
| `parameters`        | 0..1        | Métadonnées libres JSON (STA 1.1+)             | {"sensorDepth": -1.5, "batteryLevel": 87}                             |
