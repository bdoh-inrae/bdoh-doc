# Modèle de données — Métadonnées des entités


D'abord : qui c'est ?        → id, code, name, description
Ensuite : où ça s'accroche ? → les relations parents (station, sensor, property...)
Puis :    comment c'est ?    → les métadonnées techniques (processingLevel, status...)
Enfin :   ce qui en dépend  → les listes d'objets liés (identifier, memory, keyword...)


---

## ACTEURS

### Person
Utilisé par : SamplingFeature (operator), ValidatedObservation (validatedBy), Responsibility (person), Transformation (appliedBy), Memory (author)

| Champ          | Cardinalité   | Définition                          | Valeurs possibles                         |
|----------------|---------------|-------------------------------------|-------------------------------------------|
| `id`           | 1             | Identifiant unique                  | uuid                                      |
| `firstName`    | 1             | Prénom                              | "Julie"                                   |
| `lastName`     | 1             | Nom de famille                      | "Dupont"                                  |
| `email`        | 0..1          | Adresse email                       | "julie.dupont@inrae.fr"                   |
| `orcid`        | 0..1          | Identifiant chercheur ORCID         | "0000-0001-1234-1234"                     |
| `organization` | 0..* → Org    | Employeur / labo de rattachement    | → Organization[]                          |
| `affiliation`  | 0..1          | Affiliation                         | "INRAE, UR RiverLy, Villeurbanne, France" |


### Organization
Utilisé par : Person (organization), Sensor (laboratory), Station (operator), Equipment (owner), Observatory (operator), Responsibility (organization)

| Champ        | Cardinalité  | Définition                                       | Valeurs possibles                                                                      |
|--------------|--------------|--------------------------------------------------|----------------------------------------------------------------------------------------|
| `id`         | 1            | Identifiant unique                               | uuid                                                                                   |
| `code`       | 0..1         | Code depuis acronym, optionnel                   | "inrae"                                                                                |
| `name`       | 1            | Nom complet                                      | "Institut national de recherche pour l'agriculture, l'alimentation et l'environnement" |
| `acronym`    | 0..1         | Sigle                                            | "INRAE"                                                                                |
| `identifier` | 0..* → Ident | Codes externes et PID                            | → Identifier[]                                                                         |
| `type`       | 1            | Catégorie d'organisation                         | `laboratory` \| `monitoring_network` \| `research` \| `agency` \| `university`         |
| `country`    | 1            | Pays (code ISO)                                  | "FR"                                                                                   |
| `url`        | 0..1         | Site web                                         | "https://www.inrae.fr"                                                                 |
| `logoUrl`    | 0..1         | URL vers le logo (hébergeur officiel, S3, minIO) | "https://www.inrae.fr/themes/custom/inrae_socle/logo.svg"                              |


### Responsibility
Utilisé par : Observatory, Site, Station, TimeSerie (via resourceType + resourceId)
Note : lie une Person à une ressource du modèle avec un rôle fonctionnel (CI_Responsibility ISO 19115). Distinct de Person.organization qui décrit l'appartenance institutionnelle.

| Champ          | Cardinalité | Définition                         | Valeurs possibles                                                                                              |
|----------------|-------------|------------------------------------|----------------------------------------------------------------------------------------------------------------|
| `id`           | 1           | Identifiant unique                 | uuid                                                                                                           |
| `person`       | 1 → Person  | Personne responsable               | → Person                                                                                                       |
| `organization` | 0..1 → Org  | Organisation impliquée             | → Organization                                                                                                 |
| `role`         | 1           | Rôle fonctionnel (ISO 19115)       | `pointOfContact` \| `principalInvestigator` \| `author` \| `processor` \| `publisher` \| `custodian` \| `owner` \| `distributor` \| `originator` \| `resourceProvider` \| `user` |
| `resourceType` | 1           | Type de ressource ciblée           | `Observatory` \| `Site` \| `Station` \| `TimeSerie`                                                            |
| `resourceId`   | 1           | UUID de la ressource ciblée        | uuid                                                                                                           |
| `validFrom`    | 0..1        | Début de responsabilité            | "2022-01-01"                                                                                                   |
| `validTo`      | 0..1        | Fin, null si toujours actif        | "2024-12-31" \| null                                                                                           |


---

## RÉSEAU DE SURVEILLANCE

### Observatory
Aligné avec : STA Thing, schema.org/ResearchProject, ISO 19115, INSPIRE
Utilisé par : Site (observatory), TimeSeriesBundle (observatory), Memory (resourceType=Observatory)
Note : entité racine, agrège des Sites et porte la description du réseau de surveillance global.

| Champ            | Cardinalité  | Définition                                      | Valeurs possibles                         |
|------------------|--------------|-------------------------------------------------|-------------------------------------------|
| `id`             | 1            | Identifiant technique, clé primaire             | uuid                                      |
| `code`           | 1            | Code court unique, saisi par curateur           | "yzr"                                     |
| `name`           | 1            | Nom du réseau                                   | "Observatoire de l'Yzeron"                |
| `description`    | 0..1         | Description scientifique                        |                                           |
| `operator`       | 1 →Org       | Organisme gestionnaire principal                | → Organization                            |
| `location`       | 1 →Loc       | Emprise géographique courante                   | → Location                                |
| `startDate`      | 1            | Date de début                                   | "2010-01-01"                              |
| `endDate`        | 0..1         | Date de fin, null si actif                      | null                                      |
| `status`         | 1            | État de l'observatoire                          | `active` \| `inactive` \| `discontinued` |
| `url`            | 0..1         | Site web du réseau                              | "https://..."                             |
| `historicalLocation` | 0..* →HistLoc | Succession des emprises géographiques      | → HistoricalLocation[]                    |
| `historicalProject`  | 0..* →HistProj | Succession des projets structurants        | → HistoricalProject[]                     |
| `responsibility` | 0..* →Resp   | Personnes et organisations responsables         | → Responsibility[]                        |
| `keyword`        | 0..* →Keyw   | Keywords thématiques pour catalogues            | → Keyword[]                               |
| `identifier`     | 0..* →Ident  | Codes externes et PID                           | → Identifier[]                            |
| `memory`         | 0..* →Mem    | Notes et événements                             | → Memory[]                                |


### Site
Utilisé par : Observatory (sites), Station (site)
Note : subdivision géographique d'un Observatory, regroupe des Stations sur une entité physique cohérente.

| Champ         | Cardinalité  | Définition                                       | Valeurs possibles                                                           |
|---------------|--------------|--------------------------------------------------|-----------------------------------------------------------------------------|
| `id`          | 1            | Identifiant unique                               | uuid                                                                        |
| `code`        | 1            | Code court unique, généré depuis observatory     | "yzr-mer"                                                                   |
| `name`        | 1            | Nom du site                                      | "Bassin versant du Mercier"                                                 |
| `description` | 0..1         | Description libre                                |                                                                             |
| `identifier`  | 0..* → Ident | Codes externes et PID                            | → Identifier[]                                                              |
| `observatory` | 1 → Obs      | Observatoire parent                              | → Observatory                                                               |
| `type`        | 1            | Type d'entité physique                           | `watershed` \| `lake` \| `wetland` \| `aquifer` \| `catchment` \| `estuary` |
| `location`    | 1 → Loc      | Géométrie (polygone ou point)                    | → Location                                                                  |
| `area`        | 0..1         | Superficie en km²                                | "245.3"                                                                     |
| `operator`    | 0..1 → Org   | Opérateur si différent de l'Observatory          | → Organization                                                              |


### Station
Utilisé par : Site (stations), TimeSerie (station), TransferFunction (station), TransformedTimeSerie (station)
Note : point de mesure physique, peut porter son propre équipement fixe installé à poste.

| Champ               | Cardinalité    | Définition                              | Valeurs possibles                                                                      |
|---------------------|----------------|-----------------------------------------|----------------------------------------------------------------------------------------|
| `id`                | 1              | Identifiant unique                      | uuid                                                                                   |
| `code`              | 1              | Code court unique, généré depuis site   | "yzr-mer-d610"                                                                         |
| `name`              | 1              | Nom de la station                       | "Mercier au pont D610"                                                                 |
| `description`       | 0..1           | Description libre                       |                                                                                        |
| `site`              | 0..* → Site    | Site parent                             | → Site                                                                                 |
| `type`              | 1              | Type de station                         | `streamgage` \| `weatherstation` \| `well` \| `soilpit` \| `lakestation` \| `tidegage` |
| `location`          | 1 → Loc        | Position GPS                            | → Location                                                                             |
| `elevation`         | 0..1           | Altitude en mètres NGF                  | "312.5"                                                                                |
| `operator`          | 0..1 → Org     | Organisme opérateur                     | → Organization                                                                         |
| `installationDate`  | 1              | Date d'installation                     | "2015-06-01"                                                                           |
| `status`            | 1              | État de la station                      | `active` \| `inactive` \| `discontinued`                                               |
| `equipment`         | 0..* → Equip   | Équipements fixes installés             | → Equipment[]                                                                          |
| `memory`            | 0..* → Mem     | Notes et événements                     | → Memory[]                                                                             |
| `identifier`        | 0..* → Ident   | Codes externes et PID                   | → Identifier[]                                                                         |


### Location
Utilisé par : HistoricalLocation (location), Observatory (location courante),
              Site (location courante), Station (location courante), SamplingFeature (location)
Note : décrit uniquement la géométrie, sans dimension temporelle.
       La temporalité est portée par HistoricalLocation.

| Champ          | Cardinalité | Définition                           | Valeurs possibles                    |
|----------------|-------------|--------------------------------------|--------------------------------------|
| `id`           | 1           | Identifiant technique, clé primaire  | uuid                                 |
| `encodingType` | 1           | Type d'encodage (conformité STA)     | "application/geo+json"               |
| `geometry`     | 1           | Géométrie GeoJSON                    | `Point` \| `Polygon` \| `LineString` |
| `crs`          | 1           | Système de référence de coordonnées  | "EPSG:4326"                          |
| `description`  | 0..1        | Description libre                    |                                      |


### HistoricalLocation
Aligné avec : STA HistoricalLocation
Note : trace les changements de position géographique dans le temps.
       Source de vérité unique pour le lien ressource → localisation.

| Champ          | Cardinalité | Définition                          | Valeurs possibles                                          |
|----------------|-------------|-------------------------------------|------------------------------------------------------------|
| `id`           | 1           | Identifiant technique, clé primaire | uuid                                                       |
| `location`     | 1 →Loc      | Géométrie associée                  | → Location                                                 |
| `resourceType` | 1           | Type de ressource ciblée            | `Observatory` \| `Site` \| `Station` \| `SamplingFeature` |
| `resourceId`   | 1           | UUID de la ressource ciblée         | uuid                                                       |
| `validFrom`    | 1           | Début de validité                   | "2014-04-17T00:00:00Z"                                     |
| `validTo`      | 0..1        | Fin de validité, null si courant    | null                                                       |


### Project
Aligné avec : schema.org/ResearchProject, STAplus Campaign, DataCite relatedIdentifier
Utilisé par : HistoricalProject (project), SamplingFeature (project)
Note : projet structurant de long terme ou campagne ponctuelle — même objet,
       granularité gérée par parent et les dates.

| Champ            | Cardinalité  | Définition                                | Valeurs possibles                       |
|------------------|--------------|-------------------------------------------|-----------------------------------------|
| `id`             | 1            | Identifiant technique, clé primaire       | uuid                                    |
| `code`           | 1            | Code court unique                         | "osr8" \| "camp-yzr-2023-metaux"        |
| `name`           | 1            | Nom du projet ou de la campagne           | "OSR8" \| "Campagne métaux Yzeron 2023" |
| `description`    | 0..1         | Description scientifique                  |                                         |
| `parent`         | 0..1 →Proj   | Projet parent si sous-projet ou campagne  | → Project                               |
| `fundingAgency`  | 0..1 →Org    | Organisme financeur                       | → Organization                          |
| `startDate`      | 1            | Début du projet                           | "2020-01-01"                            |
| `endDate`        | 0..1         | Fin du projet, null si actif              | "2024-12-31"                            |
| `status`         | 1            | État du projet                            | `planned` \| `active` \| `completed`   |
| `url`            | 0..1         | Site web du projet                        | "https://..."                           |
| `responsibility` | 0..* →Resp   | Personnes et organisations responsables   | → Responsibility[]                      |
| `identifier`     | 0..* →Ident  | PIDs externes (ANR, EU Grant...)          | → Identifier[]                          |
| `memory`         | 0..* →Mem    | Notes et événements                       | → Memory[]                              |


### HistoricalProject
Note : trace la succession des projets qui portent une ressource dans le temps.
       Source de vérité unique pour le lien Project → ressource.

| Champ          | Cardinalité | Définition                          | Valeurs possibles                                    |
|----------------|-------------|-------------------------------------|------------------------------------------------------|
| `id`           | 1           | Identifiant technique, clé primaire | uuid                                                 |
| `project`      | 1 →Proj     | Projet actif sur cette période      | → Project                                            |
| `resourceType` | 1           | Type de ressource ciblée            | `Observatory` \| `Site` \| `Station` \| `TimeSerie` |
| `resourceId`   | 1           | UUID de la ressource ciblée         | uuid                                                 |
| `validFrom`    | 1           | Début de la période                 | "2012-01-01"                                         |
| `validTo`      | 0..1        | Fin de la période, null si actif    | null                                                 |


---

## OBSERVATION

### TimeSerie
Utilisé par : Station (timeSeries), ValidatedObservation (timeSerie), ControlObservation (timeSerie), TransferFunction (inputSeries), Transformation (inputSeries)
Note : porte tout ce qui est fixe et commun à toute la série — contrat analytique garantissant la comparabilité de tous les points.

| Champ                    | Cardinalité    | Définition                                    | Valeurs possibles                                                                        |
|--------------------------|----------------|-----------------------------------------------|------------------------------------------------------------------------------------------|
| `id`                     | 1              | Identifiant technique, clé primaire           | uuid                                                                                     |
| `code`                   | 1              | Code généré depuis station + property.code    | "yzr-mer-d610-hea"                                                                       |
| `name`                   | 1              | Nom lisible de la série                       | "Hauteur d'eau — Mercier au pont D610"                                                   |
| `description`            | 0..1           | Description libre                             |                                                                                          |
| `station`                | 1 →Sta         | Station de rattachement                       | → Station                                                                                |
| `sensor`                 | 1 →Sen         | Instrument d'analyse                          | → Sensor                                                                                 |
| `property`               | 1 →Prop        | Variable mesurée                              | → Property                                                                               |
| `unit`                   | 1 →Unit        | Unité de mesure                               | → Unit                                                                                   |
| `procedure.observation`  | 1 →Proc        | Protocole analytique fixe pour toute la série | → Procedure (type=observation)                                                           |
| `procedure.validation`   | 0..1 →Proc     | Règles de validation des données              | → Procedure (type=validation)                                                            |
| `processingLevel`        | 1              | Niveau de traitement                          | `raw` \| `validated` \| `derived`                                                       |
| `sampledMedium`          | 1              | Milieu échantillonné (CV ODM2)                | `surfaceWater` \| `groundwater` \| `soil` \| `sediment` \| `poreWater` \| `atmosphere` |
| `observationType`        | 1              | Mode d'acquisition                            | `sensor_continuous` \| `lab_sample`                                                     |
| `startDate`              | 1              | Date de début de la série                     | "1997-01-14T08:01:00Z"                                                                   |
| `endDate`                | 0..1           | Date de fin, null si active                   | null                                                                                     |
| `status`                 | 1              | État de la série                              | `active` \| `inactive` \| `discontinued`                                                |
| `license`                | 1              | Licence des données                           | `ODbL` \| `CC-BY` \| `CC-BY-SA`                                                         |
| `historicalSensor`       | 0..* →HistSen  | Succession des instruments                    | → HistoricalSensor[]                                                                     |
| `historicalProject`      | 0..* →HistProj | Succession des projets porteurs               | → HistoricalProject[]                                                                    |
| `memory`                 | 0..* →Mem      | Notes et événements                           | → Memory[]                                                                               |
| `identifier`             | 0..* →Ident    | Codes externes et PID                         | → Identifier[]                                                                           |
| `deployment` | 0..1 →Dep | Déploiement auquel appartient cette série | → Deployment |



### ValidatedObservation
Utilisé par : TimeSerie (observations)
Note : un point de mesure de la série avec son contexte de validation, optionnellement rattaché à un prélèvement terrain.

| Champ               | Cardinalité    | Définition                                          | Valeurs possibles                              |
|---------------------|----------------|-----------------------------------------------------|------------------------------------------------|
| `id`                | 1              | Identifiant unique                                  | uuid                                           |
| `timeSerie`         | 1 → TS         | Série parente                                       | → TimeSerie                                    |
| `datetime`          | 1              | Horodatage de la mesure                             | "2024-03-15T09:30:00Z"                         |
| `result`            | 1              | Valeur numérique mesurée                            | "2.4"                                          |
| `qualityFlag`       | 1              | Indicateur qualité                                  | `good` \| `suspect` \| `bad` \| `missing`      |
| `qualityComment`    | 0..1           | Justification du flag qualité                       | "pic de crue suspect"                          |
| `validatedBy`       | 0..1 → Per     | Personne ayant validé                               | → Person                                       |
| `validatedAt`       | 0..1           | Date de validation                                  | "2024-03-20T14:00:00Z"                         |
| `limsReference`     | 0..1           | Identifiant externe dans le LIMS                    | "LIMS-2024-03-001"                             |
| `samplingFeature`   | 0..1 → SF      | Prélèvement terrain associé (lab_sample uniquement) | → SamplingFeature                              |
| `featureOfInterest` | 0..1 → FOI     | Entité réelle observée                              | → FeatureOfInterest                            |


### ControlObservation
Utilisé par : TimeSerie (controlObservations)
Note : observation de contrôle qualité (blanc terrain, duplicate, étalon), structure parallèle à ValidatedObservation avec rôle QC explicite.

| Champ                | Cardinalité  | Définition                                      | Valeurs possibles                                           |
|----------------------|--------------|-------------------------------------------------|-------------------------------------------------------------|
| `id`                 | 1            | Identifiant unique                              | uuid                                                        |
| `timeSerie`          | 1 → TS       | Série parente                                   | → TimeSerie                                                 |
| `datetime`           | 1            | Horodatage                                      | "2024-03-15T09:30:00Z"                                      |
| `type`               | 1            | Type de contrôle                                | `field_blank` \| `duplicate` \| `standard` \| `spike`       |
| `result`             | 1            | Valeur mesurée                                  | "0.02"                                                      |
| `expectedResult`     | 0..1         | Valeur théorique pour étalon                    | "0.00"                                                      |
| `qualityFlag`        | 1            | Résultat du contrôle                            | `pass` \| `warn` \| `fail`                                  |
| `sensor`             | 0..1 → Sen   | Instrument si différent de la TimeSerie         | → Sensor                                                    |
| `procedure.control`  | 1 → Proc     | Protocole QC appliqué                           | → Procedure (type=control)                                  |
| `samplingFeature`    | 0..1 → SF    | Prélèvement terrain associé                     | → SamplingFeature                                           |
| `featureOfInterest`  | 0..1 → FOI   | Entité réelle observée                          | → FeatureOfInterest                                         |


### SamplingFeature
Utilisé par : ValidatedObservation (samplingFeature), ControlObservation (samplingFeature)
Note : acte de prélèvement terrain, présent uniquement pour les séries de type lab_sample.

| Champ                 | Cardinalité   | Définition                                         | Valeurs possibles                                                              |
|-----------------------|---------------|----------------------------------------------------|--------------------------------------------------------------------------------|
| `id`                  | 1             | Identifiant technique, clé primaire                | uuid                                                                           |
| `datetime`            | 1             | Horodatage du prélèvement                          | "2024-03-15T09:30:00Z"                                                         |
| `project`             | 0..1 →Proj    | Projet ou campagne dont dépend ce prélèvement      | → Project                                                                      |
| `specimenType`        | 1             | Type de matériau prélevé (CV ODM2)                 | `water` \| `soil` \| `sediment` \| `poreWater` \| `rock` \| `biological`      |
| `medium`              | 1             | Milieu de prélèvement (CV ODM2)                    | `surfaceWater` \| `groundwater` \| `depth` \| `interstitial`                  |
| `depth`               | 0..1          | Profondeur de prélèvement en mètres                | "0.30"                                                                         |
| `volume`              | 0..1          | Volume prélevé en litres                           | "1.0"                                                                          |
| `filtrationOnSite`    | 0..1          | Filtration effectuée sur le terrain                | `true` \| `false`                                                              |
| `filtrationThreshold` | 0..1          | Seuil de filtration en µm                          | "0.45"                                                                         |
| `operator`            | 0..1 →Per     | Personne ayant effectué le prélèvement             | → Person                                                                       |
| `equipment`           | 0..1 →Equip   | Matériel de collecte utilisé                       | → Equipment                                                                    |
| `location`            | 0..1 →Loc     | Position exacte si différente de la Station        | → Location                                                                     |
| `condition`           | 0..1          | Observations terrain libres                        | "turbidité élevée, eau brune"                                                  |
| `derivedFrom`         | 0..1 →SF      | Specimen parent si sous-échantillon                | → SamplingFeature                                                              |
| `identifier`          | 0..* →Ident   | Codes externes et PID                              | → Identifier[]                                                                 |

### FeatureOfInterest
Utilisé par : ValidatedObservation (featureOfInterest), ControlObservation (featureOfInterest)
Note : entité réelle du monde observée — cours d'eau, nappe, sol. Indépendante de la station ou du prélèvement.

| Champ          | Cardinalité  | Définition                              | Valeurs possibles                                                         |
|----------------|--------------|-----------------------------------------|---------------------------------------------------------------------------|
| `id`           | 1            | Identifiant unique                      | uuid                                                                      |
| `code`         | 1            | Code court unique, saisi par curateur   | "mercier-eau" \| "mercier-sed" \| "yzeron-bv"                             |
| `name`         | 1            | Nom de l'entité observée                | "Rivière Saône tronçon amont Lyon"                                        |
| `identifier`   | 0..* → Ident | Codes externes et PID                   | → Identifier[]                                                            |
| `type`         | 1            | Type d'entité                           | `river` \| `lake` \| `groundwater` \| `soil` \| `atmosphere` \| `wetland` |
| `encodingType` | 1            | Type d'encodage (conformité STA)        | "application/geo+json"                                                    |
| `geometry`     | 1            | Emprise GeoJSON de l'entité             | `Point` \| `Polygon` \| `LineString`                                      |
| `description`  | 0..1         | Description libre                       |                                                                           |

{nom-court-entité}-{type-ou-milieu}

mercier-eau-surf     ← eau de surface du Mercier
mercier-sed          ← sédiments du Mercier
yzeron-bv            ← bassin versant de l'Yzeron
p12-nappe-a          ← nappe horizon A du piézomètre P12
saone-eau-fond       ← eau de fond de la Saône


---

## INSTRUMENTATION

### HistoricalSensor
Note : trace la succession des instruments sur une ressource dans le temps.

| Champ          | Cardinalité | Définition                          | Valeurs possibles        |
|----------------|-------------|-------------------------------------|--------------------------|
| `id`           | 1           | Identifiant technique, clé primaire | uuid                     |
| `sensor`       | 1 →Sen      | Instrument actif sur cette période  | → Sensor                 |
| `resourceType` | 1           | Type de ressource ciblée            | `TimeSerie`              |
| `resourceId`   | 1           | UUID de la ressource ciblée         | uuid                     |
| `validFrom`    | 1           | Début d'utilisation                 | "2022-03-01"             |
| `validTo`      | 0..1        | Fin d'utilisation, null si actif    | null                     |


### Sensor
Utilisé par : TimeSerie (sensor), ControlObservation (sensor), HistoricalSensor (sensor)
Note : instrument de mesure. HistoricalSensor trace les changements d'instrument sur une TimeSerie.

| Champ                    | Cardinalité  | Définition                               | Valeurs possibles                                                                        |
|--------------------------|--------------|------------------------------------------|------------------------------------------------------------------------------------------|
| `id`                     | 1            | Identifiant technique, clé primaire      | uuid                                                                                     |
| `code`                   | 0..1         | Code optionnel depuis serialNumber       | "sn-2023-00412"                                                                          |
| `name`                   | 1            | Nom de l'instrument                      | "ICP-MS Thermo iCAP RQ"                                                                  |
| `type`                   | 1            | Catégorie d'instrument                   | `icp_ms` \| `spectrophotometer` \| `hplc` \| `probe` \| `autoanalyzer` \| `datalogger` |
| `make`                   | 1            | Fabricant                                | "Thermo Fisher"                                                                          |
| `model`                  | 1            | Modèle                                   | "iCAP RQ"                                                                                |
| `serialNumber`           | 0..1         | Numéro de série                          | "SN-2023-00412"                                                                          |
| `laboratory`             | 0..1 →Org    | Laboratoire opérateur                    | → Organization                                                                           |
| `calibrationDate`        | 0..1         | Date de dernière calibration             | "2024-01-15"                                                                             |
| `calibrationCertificate` | 0..1         | Référence ou URI du certificat           | "CERT-2024-ICP-001"                                                                      |
| `encodingType`           | 1            | Type d'encodage (conformité STA)         | "application/pdf" \| URI                                                                 |
| `metadata`               | 0..1         | URI vers la fiche technique              | "https://..."                                                                            |
| `deployment`             | 0..1 →Dep    | Déploiement auquel appartient ce capteur | → Deployment                                                                             |
| `deploymentDepth`        | 0..1         | Profondeur relative sur la ligne         | "-1.5"                                                                                   |
| `depthReference`         | 0..1         | Référence de profondeur                  | `surfaceRelative` \| `bottomRelative` \| `NGF` \| `absoluteElevation`                    |
| `identifier`             | 0..* →Ident  | Codes externes et PID                    | → Identifier[]                                                                           |
| `memory`                 | 0..* →Mem    | Notes et événements                      | → Memory[]                                                                               |


### Deployment
Aligné avec : STAMPLATE Platform, SensorML DeploymentProperty, ODM2 Equipment
Utilisé par : Sensor (deployment), Station (deployment)
Note : plateforme physique regroupant plusieurs capteurs comme entité cohérente.
       Exemples : ligne de capteurs verticale, bouée multi-paramètres,
       station météo multi-capteurs.

| Champ             | Cardinalité  | Définition                                    | Valeurs possibles                                      |
|-------------------|--------------|-----------------------------------------------|--------------------------------------------------------|
| `id`              | 1            | Identifiant technique, clé primaire           | uuid                                                   |
| `code`            | 1            | Code court unique                             | "dep-ret-yzr-01"                                       |
| `name`            | 1            | Nom du déploiement                            | "Ligne de capteurs retenue Yzeron"                     |
| `description`     | 0..1         | Description libre                             |                                                        |
| `station`         | 1 →Sta       | Station de rattachement                       | → Station                                              |
| `type`            | 1            | Type de plateforme                            | `verticalChain` \| `buoy` \| `weatherStation` \| `multiProbe` \| `other` |
| `deploymentDepth` | 0..1         | Profondeur de référence du déploiement        | "-2.0"                                                 |
| `depthReference`  | 0..1         | Référence de profondeur                       | `surfaceRelative` \| `bottomRelative` \| `NGF`        |
| `installDate`     | 0..1         | Date d'installation                           | "2020-06-01"                                           |
| `removeDate`      | 0..1         | Date de retrait, null si actif                | null                                                   |
| `status`          | 1            | État du déploiement                           | `active` \| `inactive` \| `removed`                   |
| `location`        | 0..1 →Loc    | Position si différente de la Station          | → Location                                             |
| `equipment`       | 0..* →Equip  | Matériel associé au déploiement               | → Equipment[]                                          |
| `memory`          | 0..* →Mem    | Notes et événements                           | → Memory[]                                             |
| `identifier`      | 0..* →Ident  | Codes externes et PID                         | → Identifier[]                                         |


### Equipment
Utilisé par : SamplingFeature (equipment), Station (equipment)
Note : matériel de collecte terrain, réutilisable entre plusieurs prélèvements. Peut aussi être installé de façon fixe sur une Station.

| Champ                 | Cardinalité  | Définition                           | Valeurs possibles                                                                                   |
|-----------------------|--------------|--------------------------------------|-----------------------------------------------------------------------------------------------------|
| `id`                  | 1            | Identifiant unique                   | uuid                                                                                                |
| `code`                | 0..1         | Code optionnel depuis serialNumber   | "sn-2023-00412"                                                                                     |
| `name`                | 1            | Nom descriptif                       | "Flacon HDPE 1L bouchon bleu"                                                                       |
| `identifier`          | 0..* → Ident | Codes externes et PID                | → Identifier[]                                                                                      |
| `type`                | 1            | Type de matériel                     | `bottle` \| `pump` \| `autosampler` \| `corer` \| `syringe` \| `filterHolder` \| `datalogger` \| `sensor_probe` |
| `material`            | 0..1         | Matériau de construction             | "HDPE" \| "verre ambré" \| "inox"                                                                   |
| `volume`              | 0..1         | Contenance ou volume en litres       | "1.0"                                                                                               |
| `preservationMethod`  | 0..1         | Méthode de conservation              | "acidification HNO3" \| "congélation" \| "obscurité"                                                |
| `manufacturer`        | 0..1         | Fabricant                            | "Nalgene"                                                                                           |
| `serialNumber`        | 0..1         | Numéro de série                      | "SN-EQ-00231"                                                                                       |
| `owner`               | 0..1 → Org   | Organisation propriétaire            | → Organization                                                                                      |


---

## RÉFÉRENTIELS

### Keyword
Aligné avec : ISO 19115 MD_Keywords, DataCite subject, DCAT keyword
Utilisé par : Property (keyword), Observatory (keyword), Site (keyword),
              TimeSerie (keyword), TimeSeriesBundle (keyword)

| Champ         | Cardinalité | Définition                                     | Valeurs possibles                                                                                     |
|---------------|-------------|------------------------------------------------|-------------------------------------------------------------------------------------------------------|
| `id`          | 1           | Identifiant unique                             | uuid                                                                                                  |
| `term`        | 1           | Terme de classification                        | "Hydrologie" \| "Métaux et métalloïdes" \| "Bassin Rhône"                                             |
| `keywordType` | 1           | Type de keyword (MD_KeywordTypeCode ISO 19115) | `discipline` \| `theme` \| `place` \| `temporal` \| `stratum` \| `taxon` \| `instrument` \| `process` |
| `thesaurus`   | 0..1        | Vocabulaire source                             | "BDOH" \| "TheiaOZCAR" \| "GCMD" \| "SANDRE" \| "free"                                                |
| `uri`         | 0..1        | URI du terme dans le thésaurus                 | "https://w3id.org/ozcar-theia/..."                                                                    |

keywordType — les valeurs viennent d'ISO 19115
ISO 19115 définit un vocabulaire contrôlé MD_KeywordTypeCode avec ces valeurs :
discipline    → domaine scientifique (Hydrologie, Chimie, Météorologie...)
theme         → sujet thématique fin (Métaux, Nutrients, Bacterial diversity...)
place         → lieu géographique ("Bassin Rhône", "France")
temporal      → période temporelle ("Holocène", "21e siècle")
stratum       → couche géologique ou verticale ("Zone saturée", "Horizon A")
taxon         → taxon biologique ("Escherichia coli")
instrument    → type d'instrument
process       → processus observé


### Property
Aligné avec : STA ObservedProperty, NERC NVS P01, Helmholtz SMS CV, ODM2 Variable
Utilisé par : TimeSerie (property), TransformedTimeSerie (property),
              TransferFunction (inputProperty, outputProperty)
Note : géré par les curateurs, chaque variable est unique. Les URIs vers
       les thésaurus externes sont portées par identifier.

| Champ              | Cardinalité  | Définition                                  | Valeurs possibles                                                                                  |
|--------------------|--------------|---------------------------------------------|----------------------------------------------------------------------------------------------------|
| `id`               | 1            | Identifiant unique                          | uuid                                                                                               |
| `code`             | 1            | Code court unique, saisi par curateur       | "no3" \| "debit" \| "doc" \| "bact-div"                                                            |
| `symbol`           | 0..1         | Symbole scientifique universel              | "NO3" \| "Q" \| "DOC"                                                                              |
| `name`             | 1            | Nom de la variable                          | "Débit journalier maximal annuel"                                                                  |
| `description`      | 0..1         | Description textuelle                       | "Maximum annuel du débit journalier"                                                               |
| `identifier`       | 0..* → Ident | URIs vers vocabulaires externes             | → Identifier[]                                                                                     |
| `defaultUnit`      | 0..1 → Unit  | Unité par défaut                            | → Unit                                                                                             |
| `discipline`       | 1            | Famille majeure                             | `hydrology` \| `chemistry` \| `meteorology` \| `sediment` \| `microbiology` \| `general`           |
| `theme`            | 0..1         | Famille mineure                             | `metals` \| `nutrients` \| `bacterialDiversity` \| `bacterialAbundance` \| `bacterialResistance` \| `radionuclides` \| `pesticides` \| `pharmaceuticals` \| `persistentOrganicPollutants` \| `organicMicropollutants` \| `general` |
| `samplingMedium`   | 0..1         | Milieu intrinsèque à la variable            | `air` \| `surfaceWater` \| `groundwater` \| `soil` \| `sediment` \| `poreWater` \| `atmosphere`    |
| `aggregationType`  | 0..1         | Type d'agrégation temporelle                | `average` \| `sum` \| `min` \| `max` \| `instantaneous` \| `cumulative`                            |
| `samplingPeriod`   | 0..1         | Période de référence pour l'agrégation      | null \| "09-01" \| "01-01"                                                                         |
| `variableType`     | 0..1         | Nature physique (calcul de delta)           | `intensive` \| `extensive`                                                                         |
| `valueType`        | 0..1         | Nature des valeurs                          | `continuous` \| `discrete` \| `categorical` \| `temporal`                                          |
| `origin`           | 0..1         | Mode de production                          | `observed` \| `derived` \| `simulated`                                                             |
| `status`           | 1            | Statut du terme géré par les curateurs      | `accepted` \| `deprecated` \| `proposed`                                                           |
| `sourceProperty`   | 0..1 → Prop  | Variable source pour les variables dérivées | → Property                                                                                         |


### Unit
Utilisé par : Property (unit), TimeSerie (unit), TransformedTimeSerie (unit)

| Champ        | Cardinalité | Définition                              | Valeurs possibles                                      |
|--------------|-------------|-----------------------------------------|--------------------------------------------------------|
| `id`         | 1           | Identifiant unique                      | uuid                                                   |
| `code`       | 1           | Symbole de l'unité, depuis QUDT ou UCUM | "mg-l" \| "m3-s" \| "degc" |
| `name`       | 1           | Nom complet de l'unité                  | "milligram per litre"                                  |
| `symbol`     | 1           | Symbole textuel                         | "mg/L"                                                 |
| `definition` | 1           | URI QUDT ou UCUM                        | "http://qudt.org/vocab/unit/MilliGM-PER-L"             |


### Procedure
Utilisé par : TimeSerie (procedure.observation, procedure.validation), ControlObservation (procedure.control), TransferFunction (procedure), TransformedTimeSerie (procedure.transformation)
Note : entité générique pour tout protocole, le champ type discrimine le rôle.

| Champ          | Cardinalité | Définition                              | Valeurs possibles                                                   |
|----------------|-------------|-----------------------------------------|---------------------------------------------------------------------|
| `id`           | 1           | Identifiant unique                      | uuid                                                                |
| `code`         | 1           | Code court unique, saisi par curateur   | "iso-10304-1"                                                       |
| `name`         | 1           | Nom du protocole                        | "NF EN ISO 10304-1"                                                 |
| `type`         | 1           | Rôle du protocole                       | `observation` \| `validation` \| `control` \| `transformation`      |
| `description`  | 0..1        | Description libre                       |                                                                     |
| `version`      | 0..1        | Version du protocole                    | "2021"                                                              |
| `reference`    | 0..1        | URI ou DOI du document normatif         | "https://www.iso.org/standard/..."                                  |
| `encodingType` | 1           | Type d'encodage (conformité STA)        | "application/pdf" \| URI                                            |


---

## TRANSFORMATION

### TransferFunction / HistoricalTransferFunction
Utilisé par : Station (transferFunctions), Transformation (transferFunction)
Note : fonction de conversion d'une mesure brute en valeur physique (ex: hauteur → débit). HistoricalTransferFunction trace les changements de courbe dans le temps.

| Champ             | Cardinalité   | Définition                                  | Valeurs possibles                                                     |
|-------------------|---------------|---------------------------------------------|-----------------------------------------------------------------------|
| `id`              | 1             | Identifiant unique                          | uuid                                                                  |
| `name`            | 1             | Nom de la fonction                          | "Courbe de tarage LBR-04 v3"                                          |
| `station`         | 1 → Sta       | Station associée                            | → Station                                                             |
| `inputProperty`   | 1 → Prop      | Variable en entrée                          | → Property (ex: hauteur)                                              |
| `outputProperty`  | 1 → Prop      | Variable en sortie                          | → Property (ex: débit)                                                |
| `type`            | 1             | Type de fonction                            | `rating_curve` \| `linear` \| `polynomial` \| `lookup_table`          |
| `parameters`      | 1             | Coefficients ou table de valeurs (JSON)     | {"a":2.1,"b":1.5}                                                     |
| `procedure`       | 0..1 → Proc   | Méthode de construction de la courbe        | → Procedure                                                           |
| `operator`        | 0..1 → Org    | Organisation responsable                    | → Organization                                                        |
| `validFrom`       | 1             | Début de validité                           | "2020-01-01T00:00:00Z"                                                |
| `validTo`         | 0..1          | Fin de validité, null si courante           | null                                                                  |


### Transformation
Utilisé par : TransformedTimeSerie (transformation)
Note : instance d'exécution, lie les séries sources à la série produite via une TransferFunction.

| Champ               | Cardinalité   | Définition                                    | Valeurs possibles          |
|---------------------|---------------|-----------------------------------------------|----------------------------|
| `id`                | 1             | Identifiant unique                            | uuid                       |
| `transferFunction`  | 1 → TF        | Fonction appliquée                            | → TransferFunction         |
| `inputSeries`       | 1..* → TS     | Séries sources                                | → TimeSerie[]              |
| `outputSeries`      | 1 → TTS       | Série produite                                | → TransformedTimeSerie     |
| `appliedAt`         | 1             | Date d'exécution                              | "2024-04-01T08:00:00Z"     |
| `appliedBy`         | 0..1 → Per    | Personne ayant lancé la transformation        | → Person                   |
| `validFrom`         | 1             | Début de validité du résultat                 | "2024-01-01T00:00:00Z"     |
| `validTo`           | 0..1          | Fin de validité                               | null                       |


### TransformedTimeSerie
Utilisé par : Station (transformedSeries), TimeSeriesBundle (transformedSeries), Transformation (outputSeries)
Note : série dérivée d'une ou plusieurs TimeSerie via une Transformation.

| Champ                       | Cardinalité   | Définition                                    | Valeurs possibles                        |
|-----------------------------|---------------|-----------------------------------------------|------------------------------------------|
| `id`                        | 1             | Identifiant unique                            | uuid                                     |
| `code`                      | 1             | Code généré depuis station + property.cod     | "yzr-mer-d610-debit"                     |
| `name`                      | 1             | Nom de la série dérivée                       | "Débit LBR-04 2024"                      |
| `description`               | 0..1          | Description libre                             |                                          |
| `station`                   | 1 → Sta       | Station de rattachement                       | → Station                                |
| `property`                  | 1 → Prop      | Variable produite                             | → Property                               |
| `unit`                      | 1 → Unit      | Unité de la série dérivée                     | → Unit                                   |
| `processingLevel`           | 1             | Niveau de traitement (toujours derived)       | `derived`                                |
| `procedure.transformation`  | 1 → Proc      | Algorithme appliqué                           | → Procedure (type=transformation)        |
| `transformation`            | 1 → Trans     | Instance de calcul                            | → Transformation                         |
| `sourceSeries`              | 1..* → TS     | Séries sources utilisées                      | → TimeSerie[]                            |
| `status`                    | 1             | État de la série                              | `active` \| `inactive`                   |


---

## ORGANISATION DES DONNÉES

### TimeSeriesBundle
Utilisé par : Observatory (bundles)
Note : regroupe des TimeSerie et TransformedTimeSerie pour la publication ou l'accès thématique groupé.

| Champ                | Cardinalité   | Définition                                       | Valeurs possibles                          |
|----------------------|---------------|--------------------------------------------------|--------------------------------------------|
| `id`                 | 1             | Identifiant unique                               | uuid                                       |
| `name`               | 1             | Nom du bundle                                    | "Qualité eau Saône 2024"                   |
| `description`        | 0..1          | Description libre                                |                                            |
| `observatory`        | 1 → Obs       | Observatoire parent                              | → Observatory                              |
| `series`             | 0..* → TS     | Séries brutes incluses                           | → TimeSerie[]                              |
| `transformedSeries`  | 0..* → TTS    | Séries dérivées incluses                         | → TransformedTimeSerie[]                   |
| `theme`              | 0..1          | Thème du regroupement                            | "qualité eau" \| "hydrologie"              |
| `license`            | 0..1          | Licence si différente de l'Observatory           | "CC-BY"                                    |


### Memory
Utilisé par : Observatory, Site, Station, Sensor, TimeSerie, Equipment... (via resourceType + resourceId)
Note : note contextuelle ou événement daté rattaché à n'importe quelle ressource du modèle.

| Champ          | Cardinalité  | Définition                        | Valeurs possibles                                                                                           |
|----------------|--------------|-----------------------------------|-------------------------------------------------------------------------------------------------------------|
| `id`           | 1            | Identifiant unique                | uuid                                                                                                        |
| `resourceType` | 1            | Type de ressource ciblée          | `Observatory` \| `Site` \| `Station` \| `Sensor` \| `Equipment` \| `TimeSerie` \| `SamplingFeature`         |
| `resourceId`   | 1            | UUID de la ressource ciblée       | uuid                                                                                                        |
| `datetime`     | 1            | Date de la note ou de l'événement | "2014-04-17T00:00:00Z"                                                                                      |
| `type`         | 1            | Type de mémo                      | `note` \| `event` \| `document` \| `photo` \| `installation` \| `hydraulic_change` \| `maintenance` \| `incident` \| `calibration` |
| `title`        | 0..1         | Titre court                       | "Modification contrôle hydraulique"                                                                         |
| `content`      | 0..1         | Texte libre                       | "Installation d'une lame déversante"                                                                        |
| `mediaUrl`     | 0..*         | Photos ou documents associés (S3) | "https://storage.obs.fr/memories/2014-lame.jpg"                                                             |
| `author`       | 0..1 → Per   | Auteur de la note                 | → Person                                                                                                    |


### Identifier
Utilisé par : Station, Site, Observatory, TimeSerie, Person, Organization, SamplingFeature...
Note : identifiant externe dans un système de référence tiers. Permet autant de PID que nécessaire.

| Champ          | Cardinalité | Définition                                 | Valeurs possibles                                                                                      |
|----------------|-------------|--------------------------------------------|--------------------------------------------------------------------------------------------------------|
| `id`           | 1           | Identifiant unique                         | uuid                                                                                                   |
| `code`         | 1           | Valeur de l'identifiant                    | "V3015810"                                                                                             |
| `codeType`     | 1           | Type d'identifiant                         | `localCode` \| `sandre` \| `doi` \| `orcid` \| `ror` \| `wigos` \| `other`                             |
| `codeSource`   | 1           | Système ou organisme émetteur              | "SANDRE" \| "DataCite" \| "ORCID" \| "WMO"                                                             |
| `url`          | 0..1        | URI de résolution de l'identifiant         | "https://id.eaufrance.fr/station/V3015810"                                                             |
| `resourceType` | 1           | Type de ressource ciblée                   | `Observatory` \| `Site` \| `Station` \| `TimeSerie` \| `Person` \| `Organization` \| `SamplingFeature` |
| `resourceId`   | 1           | UUID de la ressource ciblée                | uuid                                                                                                   |




INFO :
Thing / Station          FeatureOfInterest
────────────────         ─────────────────────────────────────
Station Mercier    →     Eau de surface du Mercier
Station Mercier    →     Sédiments du lit du Mercier
Station Mercier    →     Berge rive gauche du Mercier
Piézomètre P12     →     Nappe phréatique horizon A
Station météo YZR  →     Atmosphère bassin Yzeron


PB :
- derived time serie et time serie mais time serie a une metadonnée possible "derived"
- dans property, samplingPeriod mal défini pour le début et la fin
- ajouter projet campagne
- ajouter grappe de capteur