# Modèle de données BDOH — Métadonnées des entités

## Convention de lecture

Chaque entité suit le même ordre :
- **Identifiants** : `id`, `code`, `name`, `description`
- **Relations parents** : liens vers d'autres entités
- **Métadonnées techniques** : champs typés, enums, dates
- **Objets liés** : listes `0..*`

### Cardinalités
- `1` = obligatoire — `0..1` = optionnel — `1..*` = un ou plus — `0..*` = zéro ou plus

### Patterns transversaux
- `resourceType + resourceId` : lien polymorphique vers n'importe quelle ressource.
  Utilisé par `Memory`, `Identifier`, `HistoricalLocation`, `HistoricalProject`.
- `Historical*` : trace les changements dans le temps.
  Structure commune : `resourceType`, `resourceId`, `validFrom`, `validTo`.
- `identifier 0..* →Ident` : PIDs vers référentiels tiers. Sur toutes les entités navigables.
- `memory 0..* →Mem` : notes et événements. Sur toutes les entités avec cycle de vie.

### Architecture deux couches
```
Couche IoT (STA 2.0)           Couche métier BDOH
──────────────────────         ──────────────────────────────
Datastream                  ←→ TimeSerie (via TimeSerieDatastream)
Observation (raw)           ←→ ValidatedObservation (validée)
Station = Thing STA            Station (enrichie, métadonnées métier)
Sensor  = Sensor STA           Sensor (enrichi, historique)
Property = ObservedProperty    Property (enrichie, discipline, thème...)
```

---

## 1. ACTEURS

### Person
Aligné avec : ODM2 People, STAMPLATE schema.org/Person, ISO 19115
Utilisé par : SamplingFeature (operator), ValidatedObservation (validatedBy),
             Responsibility (person), Transformation (appliedBy), Memory (author)

| Champ          | Cardinalité | Définition                          | Valeurs possibles                          |
|----------------|-------------|-------------------------------------|--------------------------------------------|
| `id`           | 1           | Identifiant technique, clé primaire | uuid                                       |
| `firstName`    | 1           | Prénom                              | "Julie"                                    |
| `lastName`     | 1           | Nom de famille                      | "Dupont"                                   |
| `email`        | 0..1        | Adresse email                       | "julie.dupont@inrae.fr"                    |
| `orcid`        | 0..1        | Identifiant chercheur ORCID         | "0000-0001-1234-1234"                      |
| `organization` | 0..* →Org   | Employeur / labo de rattachement    | → Organization[]                           |
| `affiliation`  | 0..1        | Affiliation textuelle libre         | "INRAE, UR RiverLy, Villeurbanne, France"  |

---

### Organization
Aligné avec : ODM2 Organizations, STAMPLATE schema.org/Organization, ROR
Utilisé par : Person (organization), Sensor (laboratory), Station (operator),
             Equipment (owner), Observatory (operator), Responsibility (organization),
             Project (fundingAgency)

| Champ        | Cardinalité | Définition                                  | Valeurs possibles                                               |
|--------------|-------------|---------------------------------------------|-----------------------------------------------------------------|
| `id`         | 1           | Identifiant technique, clé primaire         | uuid                                                            |
| `code`       | 0..1        | Code depuis acronym, optionnel              | "inrae"                                                         |
| `name`       | 1           | Nom complet                                 | "Institut national de recherche pour l'agriculture..."          |
| `acronym`    | 0..1        | Sigle                                       | "INRAE"                                                         |
| `type`       | 1           | Catégorie d'organisation                    | `laboratory` \| `monitoring_network` \| `research` \| `agency` \| `university` |
| `country`    | 1           | Pays (code ISO 3166-1 alpha-2)              | "FR"                                                            |
| `url`        | 0..1        | Site web                                    | "https://www.inrae.fr"                                          |
| `logoUrl`    | 0..1        | URL vers le logo (S3 ou hébergeur officiel) | "https://www.inrae.fr/logo.svg"                                 |
| `identifier` | 0..* →Ident | Codes externes et PID (ROR, ISNI...)        | → Identifier[]                                                  |

---

### Responsibility
Aligné avec : ISO 19115 CI_Responsibility + CI_RoleCode, ODM2 Affiliations,
             STAMPLATE schema.org/Role
Utilisé par : Observatory, Site, Station, TimeSerie, Project, TransferFunction
             (via resourceType + resourceId)
Note : lie une Person ou une Organization à une ressource avec un rôle fonctionnel.
       Distinct de Person.organization (appartenance institutionnelle).
       Contrainte : person et organization ne peuvent pas être tous les deux null.

| Champ          | Cardinalité | Définition                               | Valeurs possibles                                                |
|----------------|-------------|------------------------------------------|------------------------------------------------------------------|
| `id`           | 1           | Identifiant technique, clé primaire      | uuid                                                             |
| `person`       | 0..1 →Per   | Personne responsable                     | → Person                                                         |
| `organization` | 0..1 →Org   | Organisation responsable                 | → Organization                                                   |
| `role`         | 1           | Rôle fonctionnel CI_RoleCode ISO 19115   | `pointOfContact` \| `principalInvestigator` \| `author` \| `processor` \| `publisher` \| `custodian` \| `owner` \| `distributor` \| `originator` \| `resourceProvider` \| `user` |
| `resourceType` | 1           | Type de ressource ciblée                 | `Observatory` \| `Site` \| `Station` \| `TimeSerie` \| `Project` \| `TransferFunction` |
| `resourceId`   | 1           | UUID de la ressource ciblée              | uuid                                                             |
| `validFrom`    | 0..1        | Début de responsabilité                  | "2022-01-01"                                                     |
| `validTo`      | 0..1        | Fin, null si toujours actif              | "2024-12-31" \| null                                             |

---

## 2. RÉFÉRENTIELS

### Property
Aligné avec : STA ObservedProperty, NERC NVS P01, Helmholtz SMS CV,
             ODM2 Variables, HydroServer ObservedProperty
Utilisé par : TimeSerie (property), TransformedTimeSerie (property),
             TransferFunction (inputProperty, outputProperty), Datastream (property)
Note : géré par les curateurs — chaque variable est unique et non dupliquée.
       URIs vers thésaurus externes via identifier.
       Correspond à ObservedProperty dans l'API STA exposée.

| Champ                 | Cardinalité | Définition                                  | Valeurs possibles                                                |
|-----------------------|-------------|---------------------------------------------|------------------------------------------------------------------|
| `id`                  | 1           | Identifiant technique, clé primaire         | uuid                                                             |
| `code`                | 1           | Code court unique, curateur (2-8 cars)      | "no3" \| "debit" \| "doc" \| "bact-div"                          |
| `symbol`              | 0..1        | Symbole scientifique universel              | "NO3" \| "Q" \| "DOC"                                            |
| `name`                | 1           | Nom de la variable                          | "Nitrate" \| "Débit journalier maximal annuel"                   |
| `definition`          | 0..1        | Définition textuelle                        | "Maximum annuel du débit journalier"                             |
| `defaultUnit`         | 0..1 →Unit  | Unité par défaut                            | → Unit                                                           |
| `sourceProperty`      | 0..1 →Prop  | Variable source pour les dérivées           | → Property (ex: "Q" pour "QJXA")                                 |
| `discipline`          | 1           | Famille majeure (CV BDOH)                   | `hydrology` \| `chemistry` \| `meteorology` \| `sediment` \| `microbiology` \| `general` |
| `theme`               | 0..1        | Famille mineure (CV BDOH)                   | `metals` \| `nutrients` \| `bacterialDiversity` \| `bacterialAbundance` \| `bacterialResistance` \| `radionuclides` \| `pesticides` \| `pharmaceuticals` \| `persistentOrganicPollutants` \| `organicMicropollutants` \| `general` |
| `samplingMedium`      | 0..1        | Milieu intrinsèque (CV ODM2/NERC)           | `air` \| `surfaceWater` \| `groundwater` \| `soil` \| `sediment` \| `poreWater` \| `atmosphere` |
| `aggregationType`     | 0..1        | Type d'agrégation temporelle                | `average` \| `sum` \| `min` \| `max` \| `instantaneous` \| `cumulative` |
| `samplingPeriodStart` | 0..1        | Début de période MM-JJ                      | "09-01" \| "05-01"                                               |
| `samplingPeriodEnd`   | 0..1        | Fin MM-JJ, null = année complète            | "11-30" \| null                                                  |
| `samplingPeriodMode`  | 0..1        | Calcul dynamique si pas de dates            | `min` \| `max`                                                   |
| `variableType`        | 0..1        | Nature physique — calcul de delta           | `intensive` \| `extensive`                                       |
| `valueType`           | 0..1        | Nature des valeurs                          | `continuous` \| `discrete` \| `categorical` \| `temporal`        |
| `origin`              | 0..1        | Mode de production                          | `observed` \| `derived` \| `simulated`                           |
| `status`              | 1           | Statut géré par les curateurs               | `accepted` \| `deprecated` \| `proposed`                         |
| `identifier`          | 0..* →Ident | URIs vers vocabulaires externes             | → Identifier[] (NERC P01, Theia/OZCAR, SANDRE, QUDT...)          |

---

### Unit
Aligné avec : ODM2 Units, HydroServer Unit, QUDT, UCUM
Utilisé par : Property (defaultUnit), TimeSerie (unit),
             TransformedTimeSerie (unit), Datastream (unitOfMeasurement)
Note : HydroServer ajoute Unit comme entité séparée car STA standard
       n'a qu'un objet JSON inline pour unitOfMeasurement dans Datastream.

| Champ        | Cardinalité | Définition                          | Valeurs possibles                                  |
|--------------|-------------|-------------------------------------|----------------------------------------------------|
| `id`         | 1           | Identifiant technique, clé primaire | uuid                                               |
| `code`       | 1           | Code court pour URLs (kebab-case)   | "mg-l" \| "m3-s" \| "degc"                        |
| `symbol`     | 1           | Symbole textuel affiché             | "mg/L" \| "m³/s" \| "°C"                          |
| `name`       | 1           | Nom complet de l'unité              | "milligram per litre"                              |
| `definition` | 1           | URI QUDT ou UCUM                    | "http://qudt.org/vocab/unit/MilliGM-PER-L"         |

---

### Procedure
Aligné avec : STA Sensor (procédure de mesure), ODM2 Methods,
             OGC OMS ObservingProcedure, Helmholtz SMS
Utilisé par : TimeSerie (procedure.observation, procedure.validation),
             ControlObservation (procedure.control),
             TransferFunction (procedure),
             TransformedTimeSerie (procedure.transformation),
             Datastream (procedure)
Note : entité générique pour tout protocole. Le champ type discrimine le rôle.
       Dans STA, Procedure correspond à l'entité Sensor quand elle décrit
       une méthode de mesure (encodingType + metadata).

| Champ          | Cardinalité | Définition                           | Valeurs possibles                                              |
|----------------|-------------|--------------------------------------|----------------------------------------------------------------|
| `id`           | 1           | Identifiant technique, clé primaire  | uuid                                                           |
| `code`         | 1           | Code court unique, curateur          | "iso-10304-1"                                                  |
| `name`         | 1           | Nom du protocole                     | "NF EN ISO 10304-1"                                            |
| `type`         | 1           | Rôle du protocole                    | `observation` \| `validation` \| `control` \| `transformation` |
| `description`  | 0..1        | Description libre                    |                                                                |
| `version`      | 0..1        | Version du protocole                 | "2021"                                                         |
| `reference`    | 0..1        | URI ou DOI du document normatif      | "https://www.iso.org/standard/..."                             |
| `encodingType` | 1           | Type d'encodage (conformité STA)     | "application/pdf" \| URI                                       |

---

### Keyword
Aligné avec : ISO 19115 MD_Keywords + MD_KeywordTypeCode,
             DataCite subject, DCAT keyword, GCMD Science Keywords
Utilisé par : Property (keyword), Observatory (keyword),
             TimeSerie (keyword), TimeSeriesBundle (keyword)
Note : MD_KeywordTypeCode ISO 19115 :
       discipline → domaine scientifique (Hydrologie, Chimie...)
       theme → sujet thématique fin (Métaux, Nutrients...)
       place → lieu géographique ("Bassin Rhône", "France")
       temporal → période ("Holocène", "21e siècle")
       stratum → couche géologique ("Zone saturée")
       taxon → taxon biologique ("Escherichia coli")
       instrument → type d'instrument / process → processus observé

| Champ         | Cardinalité | Définition                                     | Valeurs possibles                                               |
|---------------|-------------|------------------------------------------------|-----------------------------------------------------------------|
| `id`          | 1           | Identifiant technique, clé primaire            | uuid                                                            |
| `term`        | 1           | Terme de classification                        | "Hydrologie" \| "Métaux et métalloïdes"                        |
| `keywordType` | 1           | Type MD_KeywordTypeCode ISO 19115              | `discipline` \| `theme` \| `place` \| `temporal` \| `stratum` \| `taxon` \| `instrument` \| `process` |
| `thesaurus`   | 0..1        | Vocabulaire source                             | "BDOH" \| "TheiaOZCAR" \| "GCMD" \| "SANDRE" \| "free"        |
| `uri`         | 0..1        | URI du terme dans le thésaurus                 | "https://w3id.org/ozcar-theia/..."                              |

---

### Identifier
Aligné avec : ODM2 ExternalIdentifiers, schema.org identifier,
             INSPIRE ExternalObjectIdentifier
Utilisé par : Observatory, Site, Station, Sensor, Equipment, TimeSerie,
             Person, Organization, SamplingFeature, Property, Project
             (via resourceType + resourceId)
Note : permet autant de PIDs que nécessaire sur n'importe quelle ressource.
       Si codeType = uri alors code contient directement l'URI de résolution.

| Champ          | Cardinalité | Définition                              | Valeurs possibles                                               |
|----------------|-------------|-----------------------------------------|-----------------------------------------------------------------|
| `id`           | 1           | Identifiant technique, clé primaire     | uuid                                                            |
| `code`         | 1           | Valeur de l'identifiant ou URI          | "V3015810" \| "https://w3id.org/ozcar-theia/c_xxx"             |
| `codeType`     | 1           | Type d'identifiant                      | `localCode` \| `uri` \| `doi` \| `orcid` \| `ror` \| `sandre` \| `wigos` \| `igsn` \| `other` |
| `codeSource`   | 1           | Système ou organisme émetteur           | "SANDRE" \| "TheiaOZCAR" \| "NERC" \| "DataCite" \| "ROR"     |
| `resourceType` | 1           | Type de ressource ciblée                | `Observatory` \| `Site` \| `Station` \| `Sensor` \| `Equipment` \| `TimeSerie` \| `Person` \| `Organization` \| `SamplingFeature` \| `Property` \| `Project` \| `TransferFunction` |
| `resourceId`   | 1           | UUID de la ressource ciblée             | uuid                                                            |

---

## 3. GÉOGRAPHIE

### Location
Aligné avec : STA Location, OGC GeoJSON, ISO 19107
Utilisé par : HistoricalLocation (location), Observatory (location courante),
             Site (location courante), Station (location courante),
             Deployment (location), SamplingFeature (location)
Note : décrit uniquement la géométrie, sans dimension temporelle.
       La temporalité est portée par HistoricalLocation.
       Partagée entre couche IoT STA et backend BDOH — même UUID.

| Champ          | Cardinalité | Définition                          | Valeurs possibles                    |
|----------------|-------------|-------------------------------------|--------------------------------------|
| `id`           | 1           | Identifiant technique, clé primaire | uuid                                 |
| `encodingType` | 1           | Type d'encodage (conformité STA)    | "application/geo+json"               |
| `geometry`     | 1           | Géométrie GeoJSON                   | `Point` \| `Polygon` \| `LineString` |
| `crs`          | 1           | Système de référence de coordonnées | "EPSG:4326" \| "EPSG:2154"           |
| `description`  | 0..1        | Description libre                   |                                      |

---

### HistoricalLocation
Aligné avec : STA HistoricalLocation, OGC O&M
Utilisé par : Observatory, Site, Station (via resourceType + resourceId)
Note : trace les changements de position géographique dans le temps.
       Source de vérité unique pour le lien ressource → localisation.
       Les ressources gardent un lien direct vers leur location courante
       pour les requêtes simples.

| Champ          | Cardinalité | Définition                          | Valeurs possibles                    |
|----------------|-------------|-------------------------------------|--------------------------------------|
| `id`           | 1           | Identifiant technique, clé primaire | uuid                                 |
| `location`     | 1 →Loc      | Géométrie associée                  | → Location                           |
| `resourceType` | 1           | Type de ressource ciblée            | `Observatory` \| `Site` \| `Station` |
| `resourceId`   | 1           | UUID de la ressource ciblée         | uuid                                 |
| `validFrom`    | 1           | Début de validité                   | "2014-04-17T00:00:00Z"               |
| `validTo`      | 0..1        | Fin de validité, null si courant    | null                                 |

---

## 4. RÉSEAU DE SURVEILLANCE

### Observatory
Aligné avec : STA Thing (properties), schema.org/ResearchProject,
             ISO 19115 MD_DataIdentification, INSPIRE, STAMPLATE memberOf
Utilisé par : Site (observatory), TimeSeriesBundle (observatory)
Note : entité racine du réseau. La licence s'applique par défaut à tout le réseau.
       Correspond à un Thing STA avec properties enrichies (STAMPLATE).

| Champ                | Cardinalité    | Définition                              | Valeurs possibles                        |
|----------------------|----------------|-----------------------------------------|------------------------------------------|
| `id`                 | 1              | Identifiant technique, clé primaire     | uuid                                     |
| `code`               | 1              | Code court unique, curateur             | "yzr"                                    |
| `name`               | 1              | Nom du réseau                           | "Observatoire de l'Yzeron"               |
| `description`        | 0..1           | Description scientifique                |                                          |
| `operator`           | 1 →Org         | Organisme gestionnaire principal        | → Organization                           |
| `location`           | 1 →Loc         | Emprise géographique courante           | → Location                               |
| `startDate`          | 1              | Date de début                           | "2010-01-01"                             |
| `endDate`            | 0..1           | Date de fin, null si actif              | null                                     |
| `status`             | 1              | État de l'observatoire                  | `active` \| `inactive` \| `discontinued` |
| `url`                | 0..1           | Site web du réseau                      | "https://..."                            |
| `historicalLocation` | 0..* →HistLoc  | Succession des emprises géographiques   | → HistoricalLocation[]                   |
| `historicalProject`  | 0..* →HistProj | Succession des projets structurants     | → HistoricalProject[]                    |
| `responsibility`     | 0..* →Resp     | Personnes et organisations responsables | → Responsibility[]                       |
| `keyword`            | 0..* →Keyw     | Keywords thématiques pour catalogues    | → Keyword[]                              |
| `identifier`         | 0..* →Ident    | Codes externes et PID                   | → Identifier[]                           |
| `memory`             | 0..* →Mem      | Notes et événements                     | → Memory[]                               |

---

### Site
Aligné avec : STA Thing (properties), ISO 19115, INSPIRE
Utilisé par : Observatory (sites), Station (site)
Note : subdivision géographique d'un Observatory.
       Code généré : {observatory.code}-{segment} ex: "yzr-mer"

| Champ                | Cardinalité    | Définition                                | Valeurs possibles                                               |
|----------------------|----------------|-------------------------------------------|-----------------------------------------------------------------|
| `id`                 | 1              | Identifiant technique, clé primaire       | uuid                                                            |
| `code`               | 1              | Code court unique                         | "yzr-mer"                                                       |
| `name`               | 1              | Nom du site                               | "Bassin versant du Mercier"                                     |
| `description`        | 0..1           | Description libre                         |                                                                 |
| `observatory`        | 1 →Obs         | Observatoire parent                       | → Observatory                                                   |
| `type`               | 1              | Type d'entité physique                    | `watershed` \| `lake` \| `wetland` \| `aquifer` \| `catchment` \| `estuary` |
| `location`           | 1 →Loc         | Géométrie courante                        | → Location                                                      |
| `area`               | 0..1           | Superficie en km²                         | "245.3"                                                         |
| `operator`           | 0..1 →Org      | Opérateur si différent de l'Observatory   | → Organization                                                  |
| `historicalLocation` | 0..* →HistLoc  | Succession des périmètres                 | → HistoricalLocation[]                                          |
| `historicalProject`  | 0..* →HistProj | Succession des projets porteurs           | → HistoricalProject[]                                           |
| `responsibility`     | 0..* →Resp     | Personnes et organisations responsables   | → Responsibility[]                                              |
| `identifier`         | 0..* →Ident    | Codes externes et PID                     | → Identifier[]                                                  |
| `memory`             | 0..* →Mem      | Notes et événements                       | → Memory[]                                                      |

---

### Station
Aligné avec : STA Thing, STAMPLATE ThingProperties, ODM2 SamplingFeatures (Site)
Utilisé par : Site (stations), TimeSerie (station), TransferFunction (station),
             TransformedTimeSerie (station), Deployment (station), Datastream (station)
Note : point de mesure physique — le "Thing" STA.
       Peut appartenir à plusieurs Sites (many-to-many).
       Code généré : {site.code}-{segment} ex: "yzr-mer-d610"

| Champ                | Cardinalité    | Définition                              | Valeurs possibles                                               |
|----------------------|----------------|-----------------------------------------|-----------------------------------------------------------------|
| `id`                 | 1              | Identifiant technique, clé primaire     | uuid                                                            |
| `code`               | 1              | Code court unique                       | "yzr-mer-d610"                                                  |
| `name`               | 1              | Nom de la station                       | "Mercier au pont D610"                                          |
| `description`        | 0..1           | Description libre                       |                                                                 |
| `site`               | 0..* →Site     | Sites parents (many-to-many)            | → Site[]                                                        |
| `type`               | 1              | Type de station                         | `streamgage` \| `weatherstation` \| `well` \| `soilpit` \| `lakestation` \| `tidegage` |
| `location`           | 1 →Loc         | Position GPS courante                   | → Location                                                      |
| `elevation`          | 0..1           | Altitude en mètres (référentiel local)  | "312.5"                                                         |
| `operator`           | 0..1 →Org      | Organisme opérateur                     | → Organization                                                  |
| `installationDate`   | 0..1           | Date d'installation                     | "1997-01-14"                                                    |
| `status`             | 1              | État de la station                      | `active` \| `inactive` \| `discontinued`                        |
| `historicalLocation` | 0..* →HistLoc  | Succession des positions                | → HistoricalLocation[]                                          |
| `historicalProject`  | 0..* →HistProj | Succession des projets porteurs         | → HistoricalProject[]                                           |
| `responsibility`     | 0..* →Resp     | Personnes et organisations responsables | → Responsibility[]                                              |
| `equipment`          | 0..* →Equip    | Équipements fixes installés à poste     | → Equipment[]                                                   |
| `identifier`         | 0..* →Ident    | Codes externes et PID                   | → Identifier[]                                                  |
| `memory`             | 0..* →Mem      | Notes et événements                     | → Memory[]                                                      |

---

## 4bis. DONNÉES BRUTES (couche IoT STA 2.0)

### Datastream
Aligné avec : STA 1.1 Datastream, FROST-Server, HydroServer Datastream
Utilisé par : TimeSerieDatastream (datastream), Observation (datastream)
Note : flux de données brutes pour un unique Thing + Sensor + ObservedProperty.
       Un changement de capteur crée un nouveau Datastream (STA standard).
       Plusieurs Datastreams successifs → une TimeSerie via TimeSerieDatastream.
       BDOH garde unitOfMeasurement comme FK vers Unit (choix HydroServer/USGS)
       plutôt que le resultType SWE-Common de STA 2.0 draft — plus simple
       et suffisant pour les données environnementales.

| Champ               | Cardinalité | Définition                                | Valeurs possibles                                               |
|---------------------|-------------|-------------------------------------------|-----------------------------------------------------------------|
| `id`                | 1           | Identifiant technique, clé primaire       | uuid                                                            |
| `name`              | 1           | Nom du flux                               | "Hauteur d'eau — Mercier D610 — OTT PLS 500"                    |
| `description`       | 0..1        | Description libre                         |                                                                 |
| `observationType`   | 1           | Type de résultat (URI OGC OM 2.0)         | "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement" |
| `unitOfMeasurement` | 1 →Unit     | Unité de mesure                           | → Unit                                                          |
| `station`           | 1 →Sta      | Station source (= Thing STA)              | → Station                                                       |
| `sensor`            | 1 →Sen      | Capteur source                            | → Sensor                                                        |
| `property`          | 1 →Prop     | Variable mesurée (= ObservedProperty STA) | → Property                                                      |
| `procedure`         | 0..1 →Proc  | Protocole de mesure                       | → Procedure                                                     |
| `featureOfInterest` | 0..1 →FOI   | Entité réelle observée par défaut         | → FeatureOfInterest                                             |
| `startTime`         | 0..1        | Début de la période couverte              | "2024-01-01T00:00:00Z"                                          |
| `endTime`           | 0..1        | Fin de la période couverte, null si actif | null                                                            |
| `status`            | 1           | État du flux                              | `active` \| `inactive` \| `closed`                              |
| `license`           | 0..1        | Licence des données par défaut            | `ODbL` \| `CC-BY` \| `CC-BY-SA`                                 |
| `access`            | 1           | Niveau d'accès aux données                | `open` \| `restricted` \| `closed` \| `unknown`                 |

---

### Observation
Aligné avec : STA 2.0 Observation, OGC OMS, FROST-Server
Utilisé par : Datastream (observations)
Note : valeur brute horodatée — raw, sans qualityFlag, sans validation.
       La validation est dans ValidatedObservation du backend BDOH.
       Le lien se fait via phenomenonTime + datastream → TimeSerieDatastream.
       STA 2.0 : FeatureOfInterest devient ProximateFeatureOfInterest.
       BDOH garde featureOfInterest pour compatibilité STA 1.1/2.0.

| Champ               | Cardinalité | Définition                                       | Valeurs possibles                                    |
|---------------------|-------------|--------------------------------------------------|------------------------------------------------------|
| `id`                | 1           | Identifiant technique, clé primaire              | uuid                                                 |
| `phenomenonTime`    | 1           | Instant ou période du phénomène (STA standard)   | "2024-03-15T09:30:00Z" \| "2024-03-15T09:00:00Z/09:30:00Z" |
| `resultTime`        | 1           | Instant d'enregistrement du résultat             | "2024-03-15T09:30:05Z"                               |
| `result`            | 1           | Valeur brute mesurée                             | 4.523                                                |
| `datastream`        | 1 →DS       | Flux de données parent                           | → Datastream                                         |
| `featureOfInterest` | 0..1 →FOI   | Entité observée si différente du Datastream      | → FeatureOfInterest                                  |
| `samplingFeature`   | 0..1 →SF    | Prélèvement terrain associé                      | → SamplingFeature                                    |

---

## 5. PROJET

### Project
Aligné avec : schema.org/ResearchProject, STAplus Campaign,
             DataCite relatedIdentifier, STAMPLATE memberOf
Utilisé par : HistoricalProject (project), SamplingFeature (project)
Note : projet structurant ou campagne de mesure — même objet.
       Lien vers Observatory/Site/Station/TimeSerie via HistoricalProject
       (source de vérité unique).

| Champ            | Cardinalité | Définition                               | Valeurs possibles                       |
|------------------|-------------|------------------------------------------|-----------------------------------------|
| `id`             | 1           | Identifiant technique, clé primaire      | uuid                                    |
| `code`           | 1           | Code court unique                        | "osr8" \| "camp-yzr-2023-metaux"        |
| `name`           | 1           | Nom du projet ou de la campagne          | "OSR8" \| "Campagne métaux Yzeron 2023" |
| `description`    | 0..1        | Description scientifique                 |                                         |
| `parent`         | 0..1 →Proj  | Projet parent si sous-projet ou campagne | → Project                               |
| `fundingAgency`  | 0..1 →Org   | Organisme financeur                      | → Organization                          |
| `startDate`      | 1           | Début du projet                          | "2020-01-01"                            |
| `endDate`        | 0..1        | Fin du projet, null si actif             | "2024-12-31"                            |
| `status`         | 1           | État du projet                           | `planned` \| `active` \| `completed`    |
| `url`            | 0..1        | Site web du projet                       | "https://..."                           |
| `responsibility` | 0..* →Resp  | Personnes et organisations responsables  | → Responsibility[]                      |
| `identifier`     | 0..* →Ident | PIDs externes (ANR, EU Grant...)         | → Identifier[]                          |
| `memory`         | 0..* →Mem   | Notes et événements                      | → Memory[]                              |

---

### HistoricalProject
Note : trace la succession des projets qui portent une ressource.
       Source de vérité unique pour le lien Project → ressource.
       Même pattern que HistoricalLocation.

| Champ          | Cardinalité | Définition                          | Valeurs possibles                                    |
|----------------|-------------|-------------------------------------|------------------------------------------------------|
| `id`           | 1           | Identifiant technique, clé primaire | uuid                                                 |
| `project`      | 1 →Proj     | Projet actif sur cette période      | → Project                                            |
| `resourceType` | 1           | Type de ressource ciblée            | `Observatory` \| `Site` \| `Station` \| `TimeSerie`  |
| `resourceId`   | 1           | UUID de la ressource ciblée         | uuid                                                 |
| `validFrom`    | 1           | Début de la période                 | "2012-01-01"                                         |
| `validTo`      | 0..1        | Fin de la période, null si actif    | null                                                 |

---

## 6. INSTRUMENTATION

### Deployment
Aligné avec : STAMPLATE Platform, STA 2.0 Deployment (draft), SensorML DeploymentProperty
Utilisé par : Sensor (deployment), Station (deployment), TimeSerie (deployment)
Note : plateforme physique regroupant plusieurs capteurs.
       deploymentDepth sur chaque Sensor groupe les capteurs co-localisés.
       STA 2.0 introduit une entité Deployment dans son draft (issue #167).

| Champ             | Cardinalité | Définition                                     | Valeurs possibles                                               |
|-------------------|-------------|------------------------------------------------|-----------------------------------------------------------------|
| `id`              | 1           | Identifiant technique, clé primaire            | uuid                                                            |
| `code`            | 1           | Code court unique                              | "dep-ret-yzr-01"                                                |
| `name`            | 1           | Nom du déploiement                             | "Ligne de capteurs retenue Yzeron"                              |
| `description`     | 0..1        | Description libre                              |                                                                 |
| `station`         | 1 →Sta      | Station de rattachement                        | → Station                                                       |
| `type`            | 1           | Type de plateforme                             | `verticalChain` \| `buoy` \| `weatherStation` \| `multiProbe` \| `other` |
| `deploymentDepth` | 0..1        | Profondeur de référence globale                | "-2.0"                                                          |
| `depthReference`  | 0..1        | Référence de profondeur                        | `surfaceRelative` \| `bottomRelative` \| `absoluteElevation`    |
| `installDate`     | 0..1        | Date d'installation                            | "2020-06-01"                                                    |
| `removeDate`      | 0..1        | Date de retrait, null si actif                 | null                                                            |
| `status`          | 1           | État du déploiement                            | `active` \| `inactive` \| `removed`                             |
| `location`        | 0..1 →Loc   | Position si différente de la Station           | → Location                                                      |
| `equipment`       | 0..* →Equip | Matériel associé au déploiement                | → Equipment[]                                                   |
| `identifier`      | 0..* →Ident | Codes externes et PID                          | → Identifier[]                                                  |
| `memory`          | 0..* →Mem   | Notes et événements                            | → Memory[]                                                      |

---

### Sensor
Aligné avec : STA Sensor, STAMPLATE SensorProperties, ODM2 Equipment,
             Helmholtz SMS instrument metadata
Utilisé par : TimeSerie (sensor), ControlObservation (sensor), Datastream (sensor)
Note : instrument de mesure. Correspond au Sensor STA pour l'API IoT.
       Les métadonnées riches (calibration, laboratoire, déploiement)
       sont dans BDOH — absentes du Sensor STA minimal.

| Champ                    | Cardinalité | Définition                                  | Valeurs possibles                                             |
|--------------------------|-------------|---------------------------------------------|---------------------------------------------------------------|
| `id`                     | 1           | Identifiant technique, clé primaire         | uuid                                                          |
| `code`                   | 0..1        | Code optionnel depuis serialNumber          | "sn-2023-00412"                                               |
| `name`                   | 1           | Nom de l'instrument                         | "ICP-MS Thermo iCAP RQ"                                       |
| `type`                   | 1           | Catégorie d'instrument                      | `icp_ms` \| `spectrophotometer` \| `hplc` \| `probe` \| `autoanalyzer` \| `datalogger` |
| `make`                   | 1           | Fabricant                                   | "Thermo Fisher"                                               |
| `model`                  | 1           | Modèle                                      | "iCAP RQ"                                                     |
| `serialNumber`           | 0..1        | Numéro de série                             | "SN-2023-00412"                                               |
| `laboratory`             | 0..1 →Org   | Laboratoire opérateur                       | → Organization                                                |
| `deployment`             | 0..1 →Dep   | Déploiement auquel appartient ce capteur    | → Deployment                                                  |
| `deploymentDepth`        | 0..1        | Profondeur relative du capteur sur la ligne | "-1.5"                                                        |
| `depthReference`         | 0..1        | Référence de profondeur                     | `surfaceRelative` \| `bottomRelative` \| `absoluteElevation`  |
| `calibrationDate`        | 0..1        | Date de dernière calibration                | "2024-01-15"                                                  |
| `calibrationCertificate` | 0..1        | Référence ou URI du certificat              | "CERT-2024-ICP-001"                                           |
| `encodingType`           | 1           | Type d'encodage (conformité STA)            | "application/pdf" \| URI                                      |
| `metadata`               | 0..1        | URI vers la fiche technique                 | "https://..."                                                 |
| `identifier`             | 0..* →Ident | Codes externes et PID                       | → Identifier[]                                                |
| `memory`                 | 0..* →Mem   | Notes et événements                         | → Memory[]                                                    |

---

### Equipment
Aligné avec : ODM2 Equipment, STAMPLATE Platform (matériel terrain)
Utilisé par : SamplingFeature (equipment), Station (equipment), Deployment (equipment)
Note : matériel de collecte terrain ou équipement fixe installé à poste.
       Distinct de Sensor (instrument de mesure électronique).

| Champ                | Cardinalité | Définition                           | Valeurs possibles                                               |
|----------------------|-------------|--------------------------------------|-----------------------------------------------------------------|
| `id`                 | 1           | Identifiant technique, clé primaire  | uuid                                                            |
| `code`               | 0..1        | Code optionnel                       | "flacon-hdpe-1l"                                                |
| `name`               | 1           | Nom descriptif                       | "Flacon HDPE 1L bouchon bleu"                                   |
| `type`               | 1           | Type de matériel                     | `bottle` \| `pump` \| `autosampler` \| `corer` \| `syringe` \| `filterHolder` \| `datalogger` \| `sensor_probe` |
| `material`           | 0..1        | Matériau de construction             | "HDPE" \| "verre ambré" \| "inox"                               |
| `volume`             | 0..1        | Contenance ou volume en litres       | "1.0"                                                           |
| `preservationMethod` | 0..1        | Méthode de conservation              | "acidification HNO3" \| "congélation" \| "obscurité"            |
| `manufacturer`       | 0..1        | Fabricant                            | "Nalgene"                                                       |
| `serialNumber`       | 0..1        | Numéro de série                      | "SN-EQ-00231"                                                   |
| `owner`              | 0..1 →Org   | Organisation propriétaire            | → Organization                                                  |
| `identifier`         | 0..* →Ident | Codes externes et PID                | → Identifier[]                                                  |

---

## 7. OBSERVATION

### FeatureOfInterest
Aligné avec : STA FeatureOfInterest, OGC OMS domainFeature, ISO 19156
Utilisé par : ValidatedObservation (featureOfInterest),
             ControlObservation (featureOfInterest), Datastream (featureOfInterest),
             Observation (featureOfInterest)
Note : entité réelle du monde observée — cours d'eau, nappe, sol, atmosphère.
       Distincte de SamplingFeature (acte de prélèvement) — la distinction
       couvre les mêmes cas que Proximate/UltimateFOI de OMS sans l'adopter.
       Convention code : {nom-court-entité}-{type} ex: "mercier-eau-surf"

| Champ          | Cardinalité | Définition                           | Valeurs possibles                                               |
|----------------|-------------|--------------------------------------|-----------------------------------------------------------------|
| `id`           | 1           | Identifiant technique, clé primaire  | uuid                                                            |
| `code`         | 1           | Code court unique, curateur          | "mercier-eau-surf" \| "yzeron-bv"                               |
| `name`         | 1           | Nom de l'entité observée             | "Eau de surface du Mercier"                                     |
| `description`  | 0..1        | Description libre                    |                                                                 |
| `type`         | 1           | Type d'entité                        | `river` \| `lake` \| `groundwater` \| `soil` \| `atmosphere` \| `wetland` |
| `encodingType` | 1           | Type d'encodage (conformité STA)     | "application/geo+json"                                          |
| `geometry`     | 1           | Emprise GeoJSON de l'entité          | `Point` \| `Polygon` \| `LineString`                            |
| `identifier`   | 0..* →Ident | Codes externes et PID                | → Identifier[]                                                  |

---

### TimeSerieDatastream
Aligné avec : ODM2 Datasets, HydroServer (liaison Datastream→TimeSerie)
Utilisé par : TimeSerie (timeserieDatastream)
Note : lie une TimeSerie à ses Datastreams sources successifs dans le temps.
       Constitue l'historique complet : changements de capteur, de système, de réseau.
       sourceUrl distingue source interne (même base BDOH) et source externe (STA tiers).

| Champ          | Cardinalité | Définition                               | Valeurs possibles                                   |
|----------------|-------------|------------------------------------------|-----------------------------------------------------|
| `id`           | 1           | Identifiant technique, clé primaire      | uuid                                                |
| `timeSerie`    | 1 →TS       | Série parente                            | → TimeSerie                                         |
| `datastream`   | 0..1 →DS    | Datastream interne (même base BDOH)      | → Datastream                                        |
| `datastreamId` | 0..1        | ID Datastream si source externe          | uuid \| code externe                                |
| `sourceUrl`    | 1           | URL de base du STA source                | "https://iot.bdoh.inrae.fr/v1.1"                    |
| `sourceType`   | 1           | Type de source                           | `sta_2.0` \| `sta_1.1` \| `csv_archive` \| `other`  |
| `validFrom`    | 1           | Début de la période                      | "1997-01-14T00:00:00Z"                              |
| `validTo`      | 0..1        | Fin de la période, null si courant       | null                                                |

Note : contrainte — `datastream` ou `datastreamId` doit être renseigné, pas les deux.

---

### TimeSerie
Utilisé par : Station (timeSeries), ValidatedObservation (timeSerie),
             ControlObservation (timeSerie), Transformation (inputSeries)
Note : porte tout ce qui est fixe et commun à toute la série.
       Contrat analytique garantissant la comparabilité de tous les points.
       Une procédure de validation unique par série — plusieurs validations
       parallèles sur la même variable impliquent des TimeSerie distinctes.
       OZCAR note que leur "Observation" pivot correspond à un Datastream STA.
       Code généré : {station.code}-{property.code}-{procedure.code}
       ex: "yzr-mer-d610-hea-wiski"

| Champ                   | Cardinalité    | Définition                                    | Valeurs possibles                                         |
|-------------------------|----------------|-----------------------------------------------|-----------------------------------------------------------|
| `id`                    | 1              | Identifiant technique, clé primaire           | uuid                                                      |
| `code`                  | 1              | Code généré station + property + procedure    | "yzr-mer-d610-hea-wiski"                                  |
| `name`                  | 1              | Nom lisible de la série                       | "Hauteur d'eau — Mercier au pont D610"                    |
| `description`           | 0..1           | Description libre                             |                                                           |
| `station`               | 1 →Sta         | Station de rattachement                       | → Station                                                 |
| `sensor`                | 1 →Sen         | Instrument actif (snapshot courant)           | → Sensor                                                  |
| `deployment`            | 0..1 →Dep      | Déploiement auquel appartient cette série     | → Deployment                                              |
| `property`              | 1 →Prop        | Variable mesurée                              | → Property                                                |
| `unit`                  | 1 →Unit        | Unité de mesure                               | → Unit                                                    |
| `procedure.observation` | 1 →Proc        | Protocole analytique fixe pour toute la série | → Procedure (type=observation)                            |
| `procedure.validation`  | 1 →Proc        | Procédure de validation de cette série        | → Procedure (type=validation)          |
| `sampledMedium`         | 1              | Milieu échantillonné (CV ODM2)                | `surfaceWater` \| `groundwater` \| `soil` \| `sediment` \| `poreWater` \| `atmosphere` |
| `observationType`       | 1              | Mode d'acquisition                            | `sensor_continuous` \| `lab_sample`                       |
| `startDate`             | 1              | Date de début de la série                     | "1997-01-14T08:01:00Z"                                    |
| `endDate`               | 0..1           | Date de fin, null si active                   | null                                                      |
| `status`                | 1              | État de la série                              | `active` \| `inactive` \| `discontinued`                  |
| `license`               | 0..1           | Licence des données                           | `ODbL` \| `CC-BY` \| `CC-BY-SA`                           |
| `access`                | 1              | Niveau d'accès aux données                    | `open` \| `restricted` \| `closed` \| `unknown`           |
| `timeserieDatastream`   | 0..* →TSD      | Datastreams sources successifs                | → TimeSerieDatastream[]                                   |
| `historicalProject`     | 0..* →HistProj | Succession des projets porteurs               | → HistoricalProject[]                                     |
| `keyword`               | 0..* →Keyw     | Keywords thématiques pour catalogues          | → Keyword[]                                               |
| `identifier`            | 0..* →Ident    | Codes externes et PID                         | → Identifier[]                                            |
| `memory`                | 0..* →Mem      | Notes et événements                           | → Memory[]                                                |

---

### Vocabulaire qualityFlag
Aligné avec : ODM2 ResultQualifiers, SANDRE codes qualité, STA resultQuality OGC

| BDOH      | ODM2    | SANDRE           | OGC resultQuality |
|-----------|---------|------------------|-------------------|
| `good`    | Good    | 1 — Bonne        | `good`            |
| `suspect` | Suspect | 3 — Douteuse     | `suspect`         |
| `bad`     | Bad     | 4 — Mauvaise     | `invalid`         |
| `missing` | Missing | — (lacune)       | `missing`         |

---

### ValidationBatch
Aligné avec : ODM2 Actions (validation), W3C PROV-O Activity
Utilisé par : ValidatedObservation (validationBatch)
Note : groupe d'observations validées en une même session.
       Un batch couvre une fenêtre temporelle sur une TimeSerie.
       Alléger ValidatedObservation — les métadonnées de session
       sont ici, pas répétées sur chaque observation.

| Champ              | Cardinalité | Définition                              | Valeurs possibles                        |
|--------------------|-------------|-----------------------------------------|------------------------------------------|
| `id`               | 1           | Identifiant technique, clé primaire     | uuid                                     |
| `timeSerie`        | 1 →TS       | Série validée                           | → TimeSerie                              |
| `periodStart`      | 1           | Début de la fenêtre validée             | "2024-01-01T00:00:00Z"                   |
| `periodEnd`        | 1           | Fin de la fenêtre validée               | "2024-03-31T23:59:59Z"                   |
| `validatedBy`      | 1 →Per      | Personne ou pipeline ayant validé       | → Person                                 |
| `validatedAt`      | 1           | Date d'exécution du batch               | "2024-04-01T08:00:00Z"                   |
| `validationLogUrl` | 0..1        | URI vers le log externe (Wiski...)      | "https://wiski.inrae.fr/log-2024-q1.csv" |
| `procedure`        | 0..1 →Proc  | Protocole de validation appliqué        | → Procedure (type=validation)            |
| `status`           | 1           | État du batch                           | `pending` \| `validated` \| `rejected`   |
| `comment`          | 0..1        | Commentaire libre sur la session        | "Validation Q1 2024 après crue janvier"  |

---

### ValidatedObservation
Aligné avec : STA Observation (enrichie), ODM2 Result + DataQuality,
             Helmholtz SMS observation metadata, HydroServer ProcessingLevel
Utilisé par : TimeSerie (observations)
Note : point de mesure validé par opérateur humain ou pipeline automatique.
       Lien vers données brutes : TimeSerie → TimeSerieDatastream + phenomenonTime.
       Métadonnées de session (validatedBy, validatedAt, log) portées par ValidationBatch.
       La procédure de validation est portée par la TimeSerie parente.
       validationBatch 0..1 — une observation peut être validée hors batch.

| Champ               | Cardinalité | Définition                                          | Valeurs possibles                                          |
|---------------------|-------------|-----------------------------------------------------|------------------------------------------------------------|
| `id`                | 1           | Identifiant technique, clé primaire                 | uuid                                                       |
| `timeSerie`         | 1 →TS       | Série parente                                       | → TimeSerie                                                |
| `phenomenonTime`    | 1           | Instant ou période du phénomène (STA)               | "2024-03-15T09:30:00Z" \| "2024-03-15T09:00:00Z/10:00:00Z" |
| `resultTime`        | 0..1        | Instant où le résultat a été produit (STA)          | "2024-03-15T09:35:00Z"                                     |
| `result`            | 1           | Valeur numérique mesurée                            | "2.4"                                                      |
| `qualityFlag`       | 1           | Indicateur qualité (mapping ODM2/SANDRE en annexe)  | `good` \| `suspect` \| `bad` \| `missing`                  |
| `qualityComment`    | 0..1        | Justification libre du flag qualité                 | "pic de crue suspect"                                      |
| `validationBatch`   | 0..1 →VB    | Batch de validation parent                          | → ValidationBatch                                          |
| `samplingFeature`   | 0..1 →SF    | Prélèvement terrain associé (lab_sample uniquement) | → SamplingFeature                                          |
| `featureOfInterest` | 0..1 →FOI   | Entité réelle observée                              | → FeatureOfInterest                                        |

---

### ControlObservation
Aligné avec : ODM2 (ResultQualifier + ControlledVocabulary),
             ISO 17025 (contrôle qualité analytique)
Utilisé par : TimeSerie (controlObservations)
Note : observation de contrôle qualité — blanc terrain, duplicate, étalon, spike.
       Se greffe directement sur une TimeSerie sans Datastream dédié.
       sensor et procedure.control peuvent différer de ceux de la TimeSerie parente
       — c'est intentionnel, le contrôle utilise volontairement un autre capteur
       ou protocole pour vérifier la cohérence.

| Champ               | Cardinalité | Définition                                | Valeurs possibles                                      |
|---------------------|-------------|-------------------------------------------|--------------------------------------------------------|
| `id`                | 1           | Identifiant technique, clé primaire       | uuid                                                   |
| `timeSerie`         | 1 →TS       | Série parente                             | → TimeSerie                                            |
| `phenomenonTime`    | 1           | Instant ou période du phénomène (STA)     | "2024-03-15T09:30:00Z"                                 |
| `resultTime`        | 0..1        | Instant où le résultat a été produit      | "2024-03-15T09:35:00Z"                                 |
| `result`            | 1           | Valeur mesurée                            | "0.02"                                                 |
| `expectedResult`    | 0..1        | Valeur théorique pour étalon              | "0.00"                                                 |
| `type`              | 1           | Type de contrôle                          | `field_blank` \| `duplicate` \| `standard` \| `spike`  |
| `qualityFlag`       | 1           | Résultat du contrôle                      | `pass` \| `warn` \| `fail`                             |
| `qualityComment`    | 0..1        | Justification libre du flag qualité       | "valeur hors tolérance de 5%"                          |
| `sensor`            | 0..1 →Sen   | Capteur si différent de la TimeSerie      | → Sensor                                               |
| `procedure.control` | 1 →Proc     | Protocole QC appliqué                     | → Procedure (type=control)                             |
| `samplingFeature`   | 0..1 →SF    | Prélèvement terrain associé               | → SamplingFeature                                      |
| `featureOfInterest` | 0..1 →FOI   | Entité réelle observée                    | → FeatureOfInterest                                    |

---

### SamplingFeature
Aligné avec : STA FeatureOfInterest (specimen), ODM2 Specimen,
             OGC OMS SF_Specimen, ISO 19156
Utilisé par : ValidatedObservation (samplingFeature),
             ControlObservation (samplingFeature), Observation (samplingFeature)
Note : acte de prélèvement terrain. Présent pour les séries de type lab_sample.
       La chaîne analytique interne au laboratoire est hors modèle — lien via limsReference.
       Présent aussi dans la couche IoT pour l'enregistrement terrain immédiat.

| Champ                 | Cardinalité | Définition                                         | Valeurs possibles                                         |
|-----------------------|-------------|----------------------------------------------------|-----------------------------------------------------------|
| `id`                  | 1           | Identifiant technique, clé primaire                | uuid                                                      |
| `datetime`            | 1           | Horodatage du prélèvement                          | "2024-03-15T09:30:00Z"                                    |
| `project`             | 0..1 →Proj  | Projet ou campagne dont dépend ce prélèvement      | → Project                                                 |
| `specimenType`        | 1           | Type de matériau prélevé (CV ODM2)                 | `water` \| `soil` \| `sediment` \| `poreWater` \| `rock` \| `biological` |
| `medium`              | 1           | Milieu de prélèvement (CV ODM2)                    | `surfaceWater` \| `groundwater` \| `depth` \| `interstitial` |
| `depth`               | 0..1        | Profondeur de prélèvement en mètres                | "0.30"                                                    |
| `volume`              | 0..1        | Volume prélevé en litres                           | "1.0"                                                     |
| `filtrationOnSite`    | 0..1        | Filtration effectuée sur le terrain                | `true` \| `false`                                         |
| `filtrationThreshold` | 0..1        | Seuil de filtration en µm                          | "0.45"                                                    |
| `operator`            | 0..1 →Per   | Personne ayant effectué le prélèvement             | → Person                                                  |
| `equipment`           | 0..1 →Equip | Matériel de collecte utilisé                       | → Equipment                                               |
| `location`            | 0..1 →Loc   | Position exacte si différente de la Station        | → Location                                                |
| `condition`           | 0..1        | Observations terrain libres                        | "turbidité élevée, eau brune"                             |
| `derivedFrom`         | 0..1 →SF    | Specimen parent si sous-échantillon                | → SamplingFeature                                         |
| `limsReference`       | 0..1        | Identifiant du prélèvement dans le LIMS            | "LIMS-2024-03-001"                                        |
| `identifier`          | 0..* →Ident | Codes externes et PID                              | → Identifier[]                                            |

---

## 8. TRANSFORMATION

### TransferFunction
Aligné avec : ODM2 Methods, WMO rating curve standards
Utilisé par : TransferFunctionSet (transferFunction)
Note : fonction de conversion liée à une station — analogue à TimeSerie.
       Les points de calibration (couples x/y) définissent la fonction empiriquement.
       Code généré : {station.code}-{inputProperty.code}-{outputProperty.code}
       ex: "yzr-mer-d610-hea-qmj"

| Champ            | Cardinalité    | Définition                             | Valeurs possibles                                            |
|------------------|----------------|----------------------------------------|--------------------------------------------------------------|
| `id`             | 1              | Identifiant technique, clé primaire    | uuid                                                         |
| `code`           | 1              | Code généré station + properties       | "yzr-mer-d610-hea-qmj"                                       |
| `name`           | 1              | Nom de la fonction                     | "Courbe de tarage Mercier D610 v3"                           |
| `description`    | 0..1           | Description libre                      |                                                              |
| `station`        | 1 →Sta         | Station associée                       | → Station                                                    |
| `inputProperty`  | 1 →Prop        | Variable en entrée                     | → Property (ex: hauteur)                                     |
| `outputProperty` | 1 →Prop        | Variable en sortie                     | → Property (ex: débit)                                       |
| `type`           | 1              | Type de fonction                       | `rating_curve` \| `linear` \| `polynomial` \| `lookup_table` |
| `parameters`     | 0..1           | Coefficients analytiques (JSON)        | {"a":2.1,"b":1.5}                                            |
| `procedure`      | 0..1 →Proc     | Méthode de construction de la fonction | → Procedure (type=transformation)                            |
| `responsibility` | 0..* →Resp     | Personnes et organisations responsables| → Responsibility[]                                           |
| `startDate`      | 1              | Date de début de validité              | "2024-01-01T00:00:00Z"                                       |
| `endDate`        | 0..1           | Date de fin, null si active            | null                                                         |
| `status`         | 1              | État de la fonction                    | `active` \| `inactive` \| `deprecated`                       |
| `point`          | 0..* →TFP      | Points de calibration (couples x/y)    | → TransferFunctionPoint[]                                    |
| `identifier`     | 0..* →Ident    | Codes externes et PID                  | → Identifier[]                                               |
| `memory`         | 0..* →Mem      | Notes et événements                    | → Memory[]                                                   |

---

### TransferFunctionPoint
Utilisé par : TransferFunction (point)
Note : couple de valeurs (x/y) définissant empiriquement la fonction.
       Analogue à ValidatedObservation — c'est là que vivent les données.
       Ex : (hauteur=1.23m, débit=4.5m³/s) pour une courbe de tarage.
       Ex : (turbidité=120NTU, MES=245mg/L) pour une relation turbidité/MES.

| Champ      | Cardinalité | Définition                          | Valeurs possibles      |
|------------|-------------|-------------------------------------|------------------------|
| `id`       | 1           | Identifiant technique, clé primaire | uuid                   |
| `function` | 1 →TF       | Fonction parente                    | → TransferFunction     |
| `x`        | 1           | Valeur en entrée                    | 1.23                   |
| `y`        | 1           | Valeur en sortie                    | 4.5                    |
| `datetime` | 0..1        | Date du jaugeage ou de la mesure    | "2024-03-15T09:30:00Z" |
| `comment`  | 0..1        | Commentaire libre                   | "jaugeage crue"        |

---

### TransferFunctionSet
Aligné avec : WMO hydrological standards, ODM2 Methods
Utilisé par : TransformationBatch (transferFunctionSet)
Note : conteneur obligatoire pour une ou plusieurs TransferFunction sur une station.
       Même avec une seule TF on passe toujours par un TFSet.
       Plusieurs TFSet peuvent coexister sur une station sans hiérarchie imposée.
       type=identity ou manual -> transferFunction null, pas de calcul via TF.

| Champ              | Cardinalité | Définition                          | Valeurs possibles                      |
|--------------------|-------------|-------------------------------------|----------------------------------------|
| `id`               | 1           | Identifiant technique, clé primaire | uuid                                   |
| `name`             | 1           | Nom du jeu                          | "Barème Mercier D610 2024"             |
| `description`      | 0..1        | Description libre                   |                                        |
| `station`          | 1 →Sta      | Station associée                    | → Station                              |
| `transferFunction` | 0..1 →TF    | Fonction appliquée si type=function | → TransferFunction                     |
| `type`             | 1           | Type de transformation              | `function` \| `identity` \| `manual`  |
| `validFrom`        | 1           | Début de validité                   | "2024-01-01T00:00:00Z"                 |
| `validTo`          | 0..1        | Fin de validité, null si courant    | null                                   |
| `comment`          | 0..1        | Justification du choix              | "nouveau jaugeage après crue"          |
| `memory`           | 0..* →Mem   | Notes et événements                 | → Memory[]                             |

Contrainte : si type=function -> transferFunction obligatoire.
             si type=identity ou manual -> transferFunction null.

---

### TransformationBatch
Aligné avec : ODM2 Actions (dérivation), W3C PROV-O wasGeneratedBy
Utilisé par : TransformedObservation (transformationBatch)
Note : acte de calcul sur une ou plusieurs TimeSerie sources.
       Analogue à ValidationBatch — factorisation des métadonnées de calcul.
       Les points calculés sont dans TransformedObservation.

| Champ                  | Cardinalité | Définition                          | Valeurs possibles          |
|------------------------|-------------|-------------------------------------|----------------------------|
| `id`                   | 1           | Identifiant technique, clé primaire | uuid                       |
| `transformedTimeSerie` | 1 →TTS      | Série produite                      | → TransformedTimeSerie     |
| `transferFunctionSet`  | 1 →TFS      | Jeu de fonctions appliqué           | → TransferFunctionSet      |
| `inputSeries`          | 1..* →TS    | Séries sources                      | → TimeSerie[]              |
| `appliedAt`            | 1           | Date d'exécution du calcul          | "2024-04-01T08:00:00Z"     |
| `appliedBy`            | 0..1 →Per   | Personne ayant lancé le calcul      | → Person                   |
| `validFrom`            | 1           | Début de la période calculée        | "2024-01-01T00:00:00Z"     |
| `validTo`              | 0..1        | Fin de la période calculée          | null                       |
| `status`               | 1           | État du batch                       | `pending` \| `done` \| `failed` |
| `comment`              | 0..1        | Commentaire libre                   |                            |

---

### TransformedObservation
Aligné avec : STA Observation (enrichie), ODM2 DerivedResults
Utilisé par : TransformedTimeSerie (observations)
Note : point calculé par un TransformationBatch.
       Analogue à ValidatedObservation — c'est là que vivent les données calculées.

| Champ                  | Cardinalité | Définition                          | Valeurs possibles                         |
|------------------------|-------------|-------------------------------------|-------------------------------------------|
| `id`                   | 1           | Identifiant technique, clé primaire | uuid                                      |
| `transformedTimeSerie` | 1 →TTS      | Série parente                       | → TransformedTimeSerie                    |
| `transformationBatch`  | 0..1 →TB    | Batch de calcul parent              | → TransformationBatch                     |
| `phenomenonTime`       | 1           | Instant ou période du phénomène     | "2024-03-15T09:30:00Z"                    |
| `result`               | 1           | Valeur calculée                     | "4.5"                                     |
| `qualityFlag`          | 0..1        | Indicateur qualité                  | `good` \| `suspect` \| `bad` \| `missing` |

---

### TransformedTimeSerie
Aligné avec : STA Datastream (enrichi), ODM2 DerivedResults,
             HydroServer Datastream (processingLevel=derived)
Utilisé par : Station (transformedSeries), TimeSeriesBundle (transformedSeries),
             TransformationBatch (transformedTimeSerie)
Note : série dérivée d'une ou plusieurs TimeSerie via des TransformationBatch.
       Analogue à TimeSerie — même structure de métadonnées.
       Code généré : {station.code}-{property.code}-{procedure.code}
       ex: "yzr-mer-d610-debit-tarage"

| Champ                      | Cardinalité    | Définition                          | Valeurs possibles                               |
|----------------------------|----------------|-------------------------------------|-------------------------------------------------|
| `id`                       | 1              | Identifiant technique, clé primaire | uuid                                            |
| `code`                     | 1              | Code généré                         | "yzr-mer-d610-debit-tarage"                     |
| `name`                     | 1              | Nom de la série dérivée             | "Débit Mercier au pont D610"                    |
| `description`              | 0..1           | Description libre                   |                                                 |
| `station`                  | 1 →Sta         | Station de rattachement             | → Station                                       |
| `property`                 | 1 →Prop        | Variable produite                   | → Property                                      |
| `unit`                     | 1 →Unit        | Unité de la série dérivée           | → Unit                                          |
| `procedure.transformation` | 1 →Proc        | Procédure de transformation         | → Procedure (type=transformation)               |
| `startDate`                | 1              | Date de début de la série           | "2024-01-01T00:00:00Z"                          |
| `endDate`                  | 0..1           | Date de fin, null si active         | null                                            |
| `status`                   | 1              | État de la série                    | `active` \| `inactive` \| `discontinued`        |
| `license`                  | 0..1           | Licence des données                 | `ODbL` \| `CC-BY` \| `CC-BY-SA`                 |
| `access`                   | 1              | Niveau d'accès aux données          | `open` \| `restricted` \| `closed` \| `unknown` |
| `historicalProject`        | 0..* →HistProj | Succession des projets porteurs     | → HistoricalProject[]                           |
| `keyword`                  | 0..* →Keyw     | Keywords thématiques pour catalogues| → Keyword[]                                     |
| `identifier`               | 0..* →Ident    | Codes externes et PID               | → Identifier[]                                  |
| `memory`                   | 0..* →Mem      | Notes et événements                 | → Memory[]                                      |


---

## 9. ORGANISATION

### TimeSeriesBundle
Aligné avec : ODM2 Datasets, DataCite Dataset, DCAT Distribution
Utilisé par : Observatory (bundles)
Note : regroupe des TimeSerie et TransformedTimeSerie pour la publication.
       Objet éditorial — pas technique. Ne sert pas à encoder des relations entre séries.

| Champ               | Cardinalité | Définition                               | Valeurs possibles                 |
|---------------------|-------------|------------------------------------------|-----------------------------------|
| `id`                | 1           | Identifiant technique, clé primaire      | uuid                              |
| `name`              | 1           | Nom du bundle                            | "Qualité eau Saône 2024"          |
| `description`       | 0..1        | Description libre                        |                                   |
| `observatory`       | 1 →Obs      | Observatoire parent                      | → Observatory                     |
| `series`            | 0..* →TS    | Séries brutes incluses                   | → TimeSerie[]                     |
| `transformedSeries` | 0..* →TTS   | Séries dérivées incluses                 | → TransformedTimeSerie[]          |
| `theme`             | 0..1        | Thème du regroupement                    | "qualité eau" \| "hydrologie"     |
| `license`           | 0..1        | Licence si différente de l'Observatory   | "CC-BY"                           |
| `keyword`           | 0..* →Keyw  | Keywords thématiques pour catalogues     | → Keyword[]                       |

---

### Memory
Aligné avec : ODM2 Annotations, STAMPLATE schema.org/CreativeWork
Utilisé par : Observatory, Site, Station, Sensor, Equipment, TimeSerie,
             TransformedTimeSerie, Deployment, Project
             (via resourceType + resourceId)
Note : note contextuelle ou événement daté attaché à n'importe quelle ressource.
       Objet transversal de documentation du cycle de vie.
       Fichiers stockés en S3, référencés via mediaUrl.

| Champ          | Cardinalité | Définition                          | Valeurs possibles                                               |
|----------------|-------------|-------------------------------------|-----------------------------------------------------------------|
| `id`           | 1           | Identifiant technique, clé primaire | uuid                                                            |
| `resourceType` | 1           | Type de ressource ciblée            | `Observatory` \| `Site` \| `Station` \| `Sensor` \| `Equipment` \| `TimeSerie` \| `TransformedTimeSerie` \| `Deployment` \| `Project` \| `TransferFunction` |
| `resourceId`   | 1           | UUID de la ressource ciblée         | uuid                                                            |
| `datetime`     | 1           | Date de la note ou de l'événement   | "2014-04-17T00:00:00Z"                                          |
| `type`         | 1           | Type de mémo                        | `note` \| `event` \| `document` \| `photo` \| `installation` \| `hydraulic_change` \| `maintenance` \| `incident` \| `calibration` |
| `title`        | 0..1        | Titre court                         | "Modification contrôle hydraulique"                             |
| `content`      | 0..1        | Texte libre                         | "Installation d'une lame déversante"                            |
| `mediaUrl`     | 0..*        | Photos ou documents associés (S3)   | "https://storage.obs.fr/memories/2014-lame.jpg"                 |
| `author`       | 0..1 →Per   | Auteur de la note                   | → Person                                                        |
