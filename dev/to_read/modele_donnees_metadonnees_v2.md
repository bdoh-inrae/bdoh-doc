# Modèle de données — Métadonnées des entités

## Convention de lecture des tableaux

Chaque entité suit le même ordre de champs :
- **Identifiants** : qui c'est ? → `id`, `code`, `name`, `description`
- **Relations parents** : où ça s'accroche ? → liens vers d'autres entités
- **Métadonnées techniques** : comment c'est ? → champs typés, enums, dates
- **Objets liés** : ce qui en dépend → listes `0..*`

### Cardinalités
- `1` = obligatoire, exactement un
- `0..1` = optionnel, zéro ou un
- `1..*` = un ou plusieurs
- `0..*` = zéro ou plusieurs

### Patterns transversaux
- `resourceType + resourceId` : pattern polymorphique pour lier un objet à n'importe quelle ressource sans créer de colonne par type. Utilisé par `Memory`, `Identifier`, `HistoricalLocation`, `HistoricalProject`, `HistoricalSensor`.
- `Historical*` : trace les changements dans le temps sur une ressource. Même structure pour tous : `resourceType`, `resourceId`, `validFrom`, `validTo`.
- `identifier 0..* →Ident` : codes externes et PIDs vers des référentiels tiers (SANDRE, ORCID, DOI...). Présent sur toutes les entités navigables.
- `memory 0..* →Mem` : notes et événements contextuels. Présent sur toutes les entités qui ont un cycle de vie documentable.

---

## 1. ACTEURS

### Person
Utilisé par : SamplingFeature (operator), ValidatedObservation (validatedBy), Responsibility (person), Transformation (appliedBy), Memory (author)

| Champ          | Cardinalité   | Définition                          | Valeurs possibles                         |
|----------------|---------------|-------------------------------------|-------------------------------------------|
| `id`           | 1             | Identifiant technique, clé primaire | uuid                                      |
| `firstName`    | 1             | Prénom                              | "Julie"                                   |
| `lastName`     | 1             | Nom de famille                      | "Dupont"                                  |
| `email`        | 0..1          | Adresse email                       | "julie.dupont@inrae.fr"                   |
| `orcid`        | 0..1          | Identifiant chercheur ORCID         | "1234-1234-1234-1234"                     |
| `organization` | 0..* →Org     | Employeur / labo de rattachement    | → Organization[]                          |
| `affiliation`  | 0..1          | Affiliation textuelle libre         | "INRAE, UR RiverLy, Villeurbanne, France" |

---

### Organization
Utilisé par : Person (organization), Sensor (laboratory), Station (operator), Equipment (owner), Observatory (operator), Responsibility (organization), Project (fundingAgency)

| Champ        | Cardinalité  | Définition                                       | Valeurs possibles                                                    |
|--------------|--------------|--------------------------------------------------|----------------------------------------------------------------------|
| `id`         | 1            | Identifiant technique, clé primaire              | uuid                                                                 |
| `code`       | 0..1         | Code depuis acronym, optionnel                   | "inrae"                                                              |
| `name`       | 1            | Nom complet                                      | "Institut national de recherche pour l'agriculture, l'alimentation et l'environnement" |
| `acronym`    | 0..1         | Sigle                                            | "INRAE"                                                              |
| `type`       | 1            | Catégorie d'organisation                         | `laboratory` \| `monitoring_network` \| `research` \| `agency` \| `university` |
| `country`    | 1            | Pays (code ISO)                                  | "FR"                                                                 |
| `url`        | 0..1         | Site web                                         | "https://www.inrae.fr"                                               |
| `logoUrl`    | 0..1         | URL vers le logo (S3 ou hébergeur officiel)      | "https://www.inrae.fr/themes/custom/inrae_socle/logo.svg"            |
| `identifier` | 0..* →Ident  | Codes externes et PID (ROR, ISNI...)             | → Identifier[]                                                       |

---

### Responsibility
Aligné avec : ISO 19115 CI_Responsibility, CI_RoleCode
Utilisé par : Observatory, Site, Station, TimeSerie, Project (via resourceType + resourceId)
Note : lie une Person ou une Organization à une ressource avec un rôle fonctionnel.
       Distinct de Person.organization qui décrit l'appartenance institutionnelle.
       Contrainte : person et organization ne peuvent pas être tous les deux null simultanément.

| Champ          | Cardinalité  | Définition                                    | Valeurs possibles                                                    |
|----------------|--------------|-----------------------------------------------|----------------------------------------------------------------------|
| `id`           | 1            | Identifiant technique, clé primaire           | uuid                                                                 |
| `person`       | 0..1 →Per    | Personne responsable                          | → Person                                                             |
| `organization` | 0..1 →Org    | Organisation responsable                      | → Organization                                                       |
| `role`         | 1            | Rôle fonctionnel (CI_RoleCode ISO 19115)      | `pointOfContact` \| `principalInvestigator` \| `author` \| `processor` \| `publisher` \| `custodian` \| `owner` \| `distributor` \| `originator` \| `resourceProvider` \| `user` |
| `resourceType` | 1            | Type de ressource ciblée                      | `Observatory` \| `Site` \| `Station` \| `TimeSerie` \| `Project`     |
| `resourceId`   | 1            | UUID de la ressource ciblée                   | uuid                                                                 |
| `validFrom`    | 0..1         | Début de responsabilité                       | "2022-01-01"                                                         |
| `validTo`      | 0..1         | Fin, null si toujours actif                   | "2024-12-31" \| null                                                 |

---

## 2. RÉFÉRENTIELS

### Property
Aligné avec : STA ObservedProperty, NERC NVS P01, Helmholtz SMS CV, ODM2 Variable
Utilisé par : TimeSerie (property), TransformedTimeSerie (property), TransferFunction (inputProperty, outputProperty)
Note : géré par les curateurs, chaque variable est unique et non dupliquée.
       Les URIs vers les thésaurus externes sont portées par identifier.

| Champ            | Cardinalité  | Définition                                  | Valeurs possibles                                                    |
|------------------|--------------|---------------------------------------------|----------------------------------------------------------------------|
| `id`             | 1            | Identifiant technique, clé primaire         | uuid                                                                 |
| `code`           | 1            | Code court unique, saisi par curateur (2-8 cars) | "no3" \| "debit" \| "doc" \| "bact-div"                         |
| `symbol`         | 0..1         | Symbole scientifique universel              | "NO3" \| "Q" \| "DOC"                                                |
| `name`           | 1            | Nom de la variable                          | "Nitrate" \| "Débit journalier maximal annuel"                       |
| `definition`     | 0..1         | Définition textuelle                        | "Maximum annuel du débit journalier"                                 |
| `defaultUnit`    | 0..1 →Unit   | Unité par défaut                            | → Unit                                                               |
| `sourceProperty` | 0..1 →Prop   | Variable source pour les variables dérivées | → Property (ex: "Q" pour "QJXA")                                     |
| `discipline`     | 1            | Famille majeure (vocabulaire contrôlé BDOH) | `hydrology` \| `chemistry` \| `meteorology` \| `sediment` \| `microbiology` \| `general` |
| `theme`          | 0..1         | Famille mineure (vocabulaire contrôlé BDOH) | `metals` \| `nutrients` \| `bacterialDiversity` \| `bacterialAbundance` \| `bacterialResistance` \| `radionuclides` \| `pesticides` \| `pharmaceuticals` \| `persistentOrganicPollutants` \| `organicMicropollutants` \| `general` |
| `samplingMedium` | 0..1         | Milieu intrinsèque à la variable (CV ODM2)  | `air` \| `surfaceWater` \| `groundwater` \| `soil` \| `sediment` \| `poreWater` \| `atmosphere` |
| `aggregationType`| 0..1         | Type d'agrégation temporelle                | `average` \| `sum` \| `min` \| `max` \| `instantaneous` \| `cumulative` |
| `samplingPeriod` | 0..1         | Début de la période de référence (MM-JJ)    | null \| "09-01" \| "01-01"                                           |
| `variableType`   | 0..1         | Nature physique — calcul de delta           | `intensive` \| `extensive`                                           |
| `valueType`      | 0..1         | Nature des valeurs                          | `continuous` \| `discrete` \| `categorical` \| `temporal`            |
| `origin`         | 0..1         | Mode de production                          | `observed` \| `derived` \| `simulated`                               |
| `status`         | 1            | Statut du terme géré par les curateurs      | `accepted` \| `deprecated` \| `proposed`                             |
| `identifier`     | 0..* →Ident  | URIs vers vocabulaires externes             | → Identifier[] (NERC P01, Theia/OZCAR, SANDRE, QUDT...)              |

---

### Unit
Utilisé par : Property (defaultUnit), TimeSerie (unit), TransformedTimeSerie (unit)

| Champ        | Cardinalité | Définition                          | Valeurs possibles                                  |
|--------------|-------------|-------------------------------------|----------------------------------------------------|
| `id`         | 1           | Identifiant technique, clé primaire | uuid                                               |
| `code`       | 1           | Code court pour URLs (kebab-case)   | "mg-l" \| "m3-s" \| "degc"                         |
| `symbol`     | 1           | Symbole textuel affiché             | "mg/L" \| "m³/s" \| "°C"                           |
| `name`       | 1           | Nom complet de l'unité              | "milligram per litre"                              |
| `definition` | 1           | URI QUDT ou UCUM                    | "http://qudt.org/vocab/unit/MilliGM-PER-L"         |

---

### Procedure
Utilisé par : TimeSerie (procedure.observation, procedure.validation), ControlObservation (procedure.control), TransferFunction (procedure), TransformedTimeSerie (procedure.transformation)
Note : entité générique pour tout protocole. Le champ type discrimine le rôle.

| Champ          | Cardinalité | Définition                              | Valeurs possibles                                                  |
|----------------|-------------|-----------------------------------------|--------------------------------------------------------------------|
| `id`           | 1           | Identifiant technique, clé primaire     | uuid                                                               |
| `code`         | 1           | Code court unique, saisi par curateur   | "iso-10304-1"                                                      |
| `name`         | 1           | Nom du protocole                        | "NF EN ISO 10304-1"                                                |
| `type`         | 1           | Rôle du protocole                       | `observation` \| `validation` \| `control` \| `transformation`     |
| `description`  | 0..1        | Description libre                       |                                                                    |
| `version`      | 0..1        | Version du protocole                    | "2021"                                                             |
| `reference`    | 0..1        | URI ou DOI du document normatif         | "https://www.iso.org/standard/..."                                 |
| `encodingType` | 1           | Type d'encodage (conformité STA)        | "application/pdf" \| URI                                           |

---

### Keyword
Aligné avec : ISO 19115 MD_Keywords, DataCite subject, DCAT keyword
Utilisé par : Property (keyword), Observatory (keyword), TimeSerie (keyword), TimeSeriesBundle (keyword)
Note : terme de classification thématique issu d'un vocabulaire contrôlé ou libre.
       keywordType suit le vocabulaire MD_KeywordTypeCode d'ISO 19115 :
       discipline → domaine scientifique (Hydrologie, Chimie...)
       theme → sujet thématique fin (Métaux, Nutrients...)
       place → lieu géographique ("Bassin Rhône", "France")
       temporal → période temporelle ("Holocène", "21e siècle")
       stratum → couche géologique ou verticale ("Zone saturée")
       taxon → taxon biologique ("Escherichia coli")
       instrument → type d'instrument
       process → processus observé

| Champ         | Cardinalité | Définition                                      | Valeurs possibles                                                    |
|---------------|-------------|-------------------------------------------------|----------------------------------------------------------------------|
| `id`          | 1           | Identifiant technique, clé primaire             | uuid                                                                 |
| `term`        | 1           | Terme de classification                         | "Hydrologie" \| "Métaux et métalloïdes" \| "Bassin Rhône"            |
| `keywordType` | 1           | Type de keyword (MD_KeywordTypeCode ISO 19115)  | `discipline` \| `theme` \| `place` \| `temporal` \| `stratum` \| `taxon` \| `instrument` \| `process` |
| `thesaurus`   | 0..1        | Vocabulaire source                              | "BDOH" \| "TheiaOZCAR" \| "GCMD" \| "SANDRE" \| "free"               |
| `uri`         | 0..1        | URI du terme dans le thésaurus                  | "https://w3id.org/ozcar-theia/..."                                   |

---

### Identifier
Aligné avec : ODM2 ExternalIdentifiers, schema.org identifier
Utilisé par : Observatory, Site, Station, Sensor, Equipment, TimeSerie, Person, Organization, SamplingFeature, Property, Project (via resourceType + resourceId)
Note : identifiant externe dans un système de référence tiers.
       Permet autant de PIDs que nécessaire sur n'importe quelle ressource.
       Si codeType = uri alors code contient directement l'URI de résolution.

| Champ          | Cardinalité | Définition                              | Valeurs possibles                                                           |
|----------------|-------------|-----------------------------------------|-----------------------------------------------------------------------------|
| `id`           | 1           | Identifiant technique, clé primaire     | uuid                                                                        |
| `code`         | 1           | Valeur de l'identifiant ou URI complète | "V3015810" \| "https://w3id.org/ozcar-theia/c_xxx"                          |
| `codeType`     | 1           | Type d'identifiant                      | `localCode` \| `uri` \| `doi` \| `orcid` \| `ror` \| `sandre` \| `wigos` \| `igsn` \| `other` |
| `codeSource`   | 1           | Système ou organisme émetteur           | "SANDRE" \| "TheiaOZCAR" \| "NERC" \| "DataCite" \| "ORCID" \| "ROR"        |
| `resourceType` | 1           | Type de ressource ciblée                | `Observatory` \| `Site` \| `Station` \| `Sensor` \| `Equipment` \| `TimeSerie` \| `Person` \| `Organization` \| `SamplingFeature` \| `Property` \| `Project` |
| `resourceId`   | 1           | UUID de la ressource ciblée             | uuid                                                                        |

---

## 3. GÉOGRAPHIE

### Location
Utilisé par : HistoricalLocation (location), Observatory (location courante), Site (location courante), Station (location courante), Deployment (location), SamplingFeature (location)
Note : décrit uniquement la géométrie, sans dimension temporelle.
       La temporalité est portée par HistoricalLocation.

| Champ          | Cardinalité | Définition                          | Valeurs possibles                    |
|----------------|-------------|-------------------------------------|--------------------------------------|
| `id`           | 1           | Identifiant technique, clé primaire | uuid                                 |
| `encodingType` | 1           | Type d'encodage (conformité STA)    | "application/geo+json"               |
| `geometry`     | 1           | Géométrie GeoJSON                   | `Point` \| `Polygon` \| `LineString` |
| `crs`          | 1           | Système de référence de coordonnées | "EPSG:4326" \| "EPSG:2154"           |
| `description`  | 0..1        | Description libre                   |                                      |

---

### HistoricalLocation
Aligné avec : STA HistoricalLocation
Utilisé par : Observatory, Site, Station (via resourceType + resourceId)
Note : trace les changements de position géographique dans le temps.
       Source de vérité unique pour le lien ressource → localisation.
       Les ressources gardent un lien direct vers leur location courante
       pour les requêtes simples — HistoricalLocation fait foi pour l'historique.

| Champ          | Cardinalité | Définition                          | Valeurs possibles                             |
|----------------|-------------|-------------------------------------|-----------------------------------------------|
| `id`           | 1           | Identifiant technique, clé primaire | uuid                                          |
| `location`     | 1 →Loc      | Géométrie associée                  | → Location                                    |
| `resourceType` | 1           | Type de ressource ciblée            | `Observatory` \| `Site` \| `Station`          |
| `resourceId`   | 1           | UUID de la ressource ciblée         | uuid                                          |
| `validFrom`    | 1           | Début de validité                   | "2014-04-17T00:00:00Z"                        |
| `validTo`      | 0..1        | Fin de validité, null si courant    | null                                          |

---

## 4. RÉSEAU DE SURVEILLANCE

### Observatory
Aligné avec : STA Thing, schema.org/ResearchProject, ISO 19115, INSPIRE
Utilisé par : Site (observatory), TimeSeriesBundle (observatory)
Note : entité racine du réseau de surveillance. Agrège des Sites.
       La licence définie ici s'applique par défaut à toutes les données du réseau.

| Champ                | Cardinalité    | Définition                                  | Valeurs possibles                         |
|----------------------|----------------|---------------------------------------------|-------------------------------------------|
| `id`                 | 1              | Identifiant technique, clé primaire         | uuid                                      |
| `code`               | 1              | Code court unique, saisi par curateur       | "yzr"                                     |
| `name`               | 1              | Nom du réseau                               | "Observatoire de l'Yzeron"                |
| `description`        | 0..1           | Description scientifique                    |                                           |
| `operator`           | 1 →Org         | Organisme gestionnaire principal            | → Organization                            |
| `location`           | 1 →Loc         | Emprise géographique courante               | → Location                                |
| `startDate`          | 1              | Date de début                               | "2010-01-01"                              |
| `endDate`            | 0..1           | Date de fin, null si actif                  | null                                      |
| `status`             | 1              | État de l'observatoire                      | `active` \| `inactive` \| `discontinued`  |
| `url`                | 0..1           | Site web du réseau                          | "https://..."                             |
| `license`            | 1              | Licence des données par défaut              | `ODbL` \| `CC-BY` \| `CC-BY-SA`           |
| `historicalLocation` | 0..* →HistLoc  | Succession des emprises géographiques       | → HistoricalLocation[]                    |
| `historicalProject`  | 0..* →HistProj | Succession des projets structurants         | → HistoricalProject[]                     |
| `responsibility`     | 0..* →Resp     | Personnes et organisations responsables     | → Responsibility[]                        |
| `keyword`            | 0..* →Keyw     | Keywords thématiques pour catalogues        | → Keyword[]                               |
| `identifier`         | 0..* →Ident    | Codes externes et PID                       | → Identifier[]                            |
| `memory`             | 0..* →Mem      | Notes et événements                         | → Memory[]                                |

---

### Site
Utilisé par : Observatory (sites), Station (site)
Note : subdivision géographique d'un Observatory.
       Regroupe des Stations sur une entité physique cohérente (bassin versant, lac...).
       Code généré : {observatory.code}-{segment court} ex: "yzr-mer"

| Champ                | Cardinalité    | Définition                                       | Valeurs possibles                                         |
|----------------------|----------------|--------------------------------------------------|-----------------------------------------------------------|
| `id`                 | 1              | Identifiant technique, clé primaire              | uuid                                                      |
| `code`               | 1              | Code court unique                                | "yzr-mer"                                                 |
| `name`               | 1              | Nom du site                                      | "Bassin versant du Mercier"                               |
| `description`        | 0..1           | Description libre                                |                                                           |
| `observatory`        | 1 →Obs         | Observatoire parent                              | → Observatory                                             |
| `type`               | 1              | Type d'entité physique                           | `watershed` \| `lake` \| `wetland` \| `aquifer` \| `catchment` \| `estuary` |
| `location`           | 1 →Loc         | Géométrie courante (polygone ou point)           | → Location                                                |
| `area`               | 0..1           | Superficie en km²                                | "245.3"                                                   |
| `operator`           | 0..1 →Org      | Opérateur si différent de l'Observatory          | → Organization                                            |
| `historicalLocation` | 0..* →HistLoc  | Succession des périmètres géographiques          | → HistoricalLocation[]                                    |
| `historicalProject`  | 0..* →HistProj | Succession des projets porteurs                  | → HistoricalProject[]                                     |
| `responsibility`     | 0..* →Resp     | Personnes et organisations responsables          | → Responsibility[]                                        |
| `identifier`         | 0..* →Ident    | Codes externes et PID                            | → Identifier[]                                            |
| `memory`             | 0..* →Mem      | Notes et événements                              | → Memory[]                                                |

---

### Station
Aligné avec : STA Thing
Utilisé par : Site (stations), TimeSerie (station), TransferFunction (station), TransformedTimeSerie (station), Deployment (station)
Note : point de mesure physique — le "Thing" STA.
       Peut appartenir à plusieurs Sites (relation many-to-many).
       Code généré : {site.code}-{segment court} ex: "yzr-mer-d610"

| Champ                | Cardinalité    | Définition                              | Valeurs possibles                                                 |
|----------------------|----------------|-----------------------------------------|-------------------------------------------------------------------|
| `id`                 | 1              | Identifiant technique, clé primaire     | uuid                                                              |
| `code`               | 1              | Code court unique                       | "yzr-mer-d610"                                                    |
| `name`               | 1              | Nom de la station                       | "Mercier au pont D610"                                            |
| `description`        | 0..1           | Description libre                       |                                                                   |
| `site`               | 0..* →Site     | Sites parents (many-to-many)            | → Site[]                                                          |
| `type`               | 1              | Type de station                         | `streamgage` \| `weatherstation` \| `well` \| `soilpit` \| `lakestation` \| `tidegage` |
| `location`           | 1 →Loc         | Position GPS courante                   | → Location                                                        |
| `elevation`          | 0..1           | Altitude en mètres (référentiel local)  | "312.5"                                                           |
| `operator`           | 0..1 →Org      | Organisme opérateur                     | → Organization                                                    |
| `installationDate`   | 0..1           | Date d'installation                     | "1997-01-14"                                                      |
| `status`             | 1              | État de la station                      | `active` \| `inactive` \| `discontinued`                          |
| `historicalLocation` | 0..* →HistLoc  | Succession des positions                | → HistoricalLocation[]                                            |
| `historicalProject`  | 0..* →HistProj | Succession des projets porteurs         | → HistoricalProject[]                                             |
| `responsibility`     | 0..* →Resp     | Personnes et organisations responsables | → Responsibility[]                                                |
| `equipment`          | 0..* →Equip    | Équipements fixes installés à poste     | → Equipment[]                                                     |
| `identifier`         | 0..* →Ident    | Codes externes et PID                   | → Identifier[]                                                    |
| `memory`             | 0..* →Mem      | Notes et événements                     | → Memory[]                                                        |

---

## 4bis. DONNÉES BRUTES

### Datastream
Aligné avec : STA 2.0 Datastream
Utilisé par : TimeSerieDatastream (datastreamId), Observation (datastream)
Note : flux de données brutes pour un unique Thing + Sensor + ObservedProperty.
       Un changement de capteur crée un nouveau Datastream.
       Plusieurs Datastreams successifs sont agrégés en une TimeSerie
       via TimeSerieDatastream.

| Champ              | Cardinalité | Définition                                | Valeurs possibles                                                      |
|--------------------|-------------|-------------------------------------------|------------------------------------------------------------------------|
| `id`               | 1           | Identifiant technique, clé primaire       | uuid                                                                   |
| `name`             | 1           | Nom du flux                               | "Hauteur d'eau — Mercier D610 — OTT PLS 500"                           |
| `description`      | 0..1        | Description libre                         |                                                                        |
| `observationType`  | 1           | Type de résultat (URI OGC)                | "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement" |
| `unitOfMeasurement`| 1           | Unité de mesure                           | → Unit                                                                 |
| `station`          | 1 →Sta      | Station source (= Thing STA)              | → Station                                                              |
| `sensor`           | 1 →Sen      | Capteur source                            | → Sensor                                                               |
| `property`         | 1 →Prop     | Variable mesurée (= ObservedProperty STA) | → Property                                                             |
| `procedure`        | 0..1 →Proc  | Protocole de mesure                       | → Procedure                                                            |
| `featureOfInterest`| 0..1 →FOI   | Entité réelle observée par défaut         | → FeatureOfInterest                                                    |
| `startTime`        | 0..1        | Début de la période couverte              | "2024-01-01T00:00:00Z"                                                 |
| `endTime`          | 0..1        | Fin de la période couverte                | null si actif                                                          |
| `status`           | 1           | État du flux                              | `active` \| `inactive` \| `closed`                                     |

---

### Observation
Aligné avec : STA 2.0 Observation
Utilisé par : Datastream (observations)
Note : valeur brute horodatée — raw, sans qualityFlag, sans validation.
       La validation est dans ValidatedObservation du backend BDOH.
       Le lien se fait via phenomenonTime + datastream → TimeSerieDatastream.

| Champ               | Cardinalité | Définition                                           | Valeurs possibles                                          |
|---------------------|-------------|------------------------------------------------------|------------------------------------------------------------|
| `id`                | 1           | Identifiant technique, clé primaire                  | uuid                                                       |
| `phenomenonTime`    | 1           | Instant ou période du phénomène (STA standard)       | "2024-03-15T09:30:00Z" \| "2024-03-15T09:00:00Z/09:30:00Z" |
| `resultTime`        | 1           | Instant d'enregistrement du résultat                 | "2024-03-15T09:30:05Z"                                     |
| `result`            | 1           | Valeur brute mesurée                                 | 4.523                                                      |
| `datastream`        | 1 →DS       | Flux de données parent                               | → Datastream                                               |
| `featureOfInterest` | 0..1 →FOI   | Entité réelle observée (si différente du Datastream) | → FeatureOfInterest                                        |
| `samplingFeature`   | 0..1 →SF    | Prélèvement terrain associé                          | → SamplingFeature                                          |


## 5. PROJET

### Project
Aligné avec : schema.org/ResearchProject, STAplus Campaign, DataCite relatedIdentifier
Utilisé par : HistoricalProject (project), SamplingFeature (project)
Note : projet structurant de long terme ou campagne de mesure ponctuelle — même objet.
       La granularité est gérée par parent et les dates.
       Le lien vers Observatory/Site/Station/TimeSerie se fait via HistoricalProject
       (source de vérité unique, évite les incohérences).

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
| `status`         | 1            | État du projet                            | `planned` \| `active` \| `completed`    |
| `url`            | 0..1         | Site web du projet                        | "https://..."                           |
| `responsibility` | 0..* →Resp   | Personnes et organisations responsables   | → Responsibility[]                      |
| `identifier`     | 0..* →Ident  | PIDs externes (ANR, EU Grant...)          | → Identifier[]                          |
| `memory`         | 0..* →Mem    | Notes et événements                       | → Memory[]                              |

---

### HistoricalProject
Note : trace la succession des projets qui portent une ressource dans le temps.
       Source de vérité unique pour le lien Project → ressource.
       Même pattern que HistoricalLocation et HistoricalSensor.

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
Aligné avec : STAMPLATE Platform, SensorML DeploymentProperty
Utilisé par : Sensor (deployment), Station (deployment), TimeSerie (deployment)
Note : plateforme physique regroupant plusieurs capteurs comme entité cohérente.
       Le deploymentDepth sur chaque Sensor positionne le capteur sur la ligne
       et groupe implicitement les capteurs co-localisés (même profondeur = co-localisés).
       Exemples : ligne de capteurs verticale, bouée multi-paramètres, station météo multi-capteurs.

| Champ             | Cardinalité  | Définition                                    | Valeurs possibles                                                 |
|-------------------|--------------|-----------------------------------------------|-------------------------------------------------------------------|
| `id`              | 1            | Identifiant technique, clé primaire           | uuid                                                              |
| `code`            | 1            | Code court unique                             | "dep-ret-yzr-01"                                                  |
| `name`            | 1            | Nom du déploiement                            | "Ligne de capteurs retenue Yzeron"                                |
| `description`     | 0..1         | Description libre                             |                                                                   |
| `station`         | 1 →Sta       | Station de rattachement                       | → Station                                                         |
| `type`            | 1            | Type de plateforme                            | `verticalChain` \| `buoy` \| `weatherStation` \| `multiProbe` \| `other` |
| `deploymentDepth` | 0..1         | Profondeur de référence globale du déploiement | "-2.0"                                                           |
| `depthReference`  | 0..1         | Référence de profondeur                       | `surfaceRelative` \| `bottomRelative` \| `absoluteElevation`      |
| `installDate`     | 0..1         | Date d'installation                           | "2020-06-01"                                                      |
| `removeDate`      | 0..1         | Date de retrait, null si actif                | null                                                              |
| `status`          | 1            | État du déploiement                           | `active` \| `inactive` \| `removed`                               |
| `location`        | 0..1 →Loc    | Position si différente de la Station          | → Location                                                        |
| `equipment`       | 0..* →Equip  | Matériel associé au déploiement               | → Equipment[]                                                     |
| `identifier`      | 0..* →Ident  | Codes externes et PID                         | → Identifier[]                                                    |
| `memory`          | 0..* →Mem    | Notes et événements                           | → Memory[]                                                        |

---

### Sensor
Aligné avec : STA Sensor, STAMPLATE Sensor
Utilisé par : TimeSerie (sensor), ControlObservation (sensor), HistoricalSensor (sensor)
Note : instrument de mesure. HistoricalSensor trace les changements d'instrument sur une TimeSerie.
       Si le capteur appartient à un Deployment, deploymentDepth positionne ce capteur
       sur la ligne et groupe implicitement les capteurs co-localisés.

| Champ                    | Cardinalité  | Définition                                    | Valeurs possibles                                          |
|--------------------------|--------------|-----------------------------------------------|------------------------------------------------------------|
| `id`                     | 1            | Identifiant technique, clé primaire           | uuid                                                       |
| `code`                   | 0..1         | Code optionnel depuis serialNumber            | "sn-2023-00412"                                            |
| `name`                   | 1            | Nom de l'instrument                           | "ICP-MS Thermo iCAP RQ"                                    |
| `type`                   | 1            | Catégorie d'instrument                        | `icp_ms` \| `spectrophotometer` \| `hplc` \| `probe` \| `autoanalyzer` \| `datalogger` |
| `make`                   | 1            | Fabricant                                     | "Thermo Fisher"                                            |
| `model`                  | 1            | Modèle                                        | "iCAP RQ"                                                  |
| `serialNumber`           | 0..1         | Numéro de série                               | "SN-2023-00412"                                            |
| `laboratory`             | 0..1 →Org    | Laboratoire opérateur                         | → Organization                                             |
| `deployment`             | 0..1 →Dep    | Déploiement auquel appartient ce capteur      | → Deployment                                               |
| `deploymentDepth`        | 0..1         | Profondeur relative du capteur sur la ligne   | "-1.5"                                                     |
| `depthReference`         | 0..1         | Référence de profondeur                       | `surfaceRelative` \| `bottomRelative` \| `absoluteElevation` |
| `calibrationDate`        | 0..1         | Date de dernière calibration                  | "2024-01-15"                                               |
| `calibrationCertificate` | 0..1         | Référence ou URI du certificat                | "CERT-2024-ICP-001"                                        |
| `encodingType`           | 1            | Type d'encodage (conformité STA)              | "application/pdf" \| URI                                   |
| `metadata`               | 0..1         | URI vers la fiche technique                   | "https://..."                                              |
| `identifier`             | 0..* →Ident  | Codes externes et PID                         | → Identifier[]                                             |
| `memory`                 | 0..* →Mem    | Notes et événements                           | → Memory[]                                                 |

---

### Equipment
Utilisé par : SamplingFeature (equipment), Station (equipment), Deployment (equipment)
Note : matériel de collecte terrain ou équipement fixe installé à poste.
       Réutilisable entre plusieurs prélèvements et déploiements.

| Champ                | Cardinalité  | Définition                           | Valeurs possibles                                                       |
|----------------------|--------------|--------------------------------------|-------------------------------------------------------------------------|
| `id`                 | 1            | Identifiant technique, clé primaire  | uuid                                                                    |
| `code`               | 0..1         | Code optionnel                       | "flacon-hdpe-1l"                                                        |
| `name`               | 1            | Nom descriptif                       | "Flacon HDPE 1L bouchon bleu"                                           |
| `type`               | 1            | Type de matériel                     | `bottle` \| `pump` \| `autosampler` \| `corer` \| `syringe` \| `filterHolder` \| `datalogger` \| `sensor_probe` |
| `material`           | 0..1         | Matériau de construction             | "HDPE" \| "verre ambré" \| "inox"                                       |
| `volume`             | 0..1         | Contenance ou volume en litres       | "1.0"                                                                   |
| `preservationMethod` | 0..1         | Méthode de conservation              | "acidification HNO3" \| "congélation" \| "obscurité"                    |
| `manufacturer`       | 0..1         | Fabricant                            | "Nalgene"                                                               |
| `serialNumber`       | 0..1         | Numéro de série                      | "SN-EQ-00231"                                                           |
| `owner`              | 0..1 →Org    | Organisation propriétaire            | → Organization                                                          |
| `identifier`         | 0..* →Ident  | Codes externes et PID                | → Identifier[]                                                          |

---

## 7. OBSERVATION

### FeatureOfInterest
Aligné avec : STA FeatureOfInterest, OGC O&M domainFeature
Utilisé par : ValidatedObservation (featureOfInterest), ControlObservation (featureOfInterest)
Note : entité réelle du monde observée — cours d'eau, nappe, sol, atmosphère.
       Indépendante de la Station (Thing) qui l'observe.
       Une même Station peut observer plusieurs FeatureOfInterest différentes.
       Convention de code : {nom-court-entité}-{type-ou-milieu}
       ex: "mercier-eau-surf", "mercier-sed", "yzeron-bv", "p12-nappe-a"

| Champ          | Cardinalité  | Définition                              | Valeurs possibles                                                          |
|----------------|--------------|-----------------------------------------|----------------------------------------------------------------------------|
| `id`           | 1            | Identifiant technique, clé primaire     | uuid                                                                       |
| `code`         | 1            | Code court unique, saisi par curateur   | "mercier-eau-surf" \| "yzeron-bv"                                          |
| `name`         | 1            | Nom de l'entité observée                | "Eau de surface du Mercier" \| "Bassin versant de l'Yzeron"                |
| `description`  | 0..1         | Description libre                       |                                                                            |
| `type`         | 1            | Type d'entité                           | `river` \| `lake` \| `groundwater` \| `soil` \| `atmosphere` \| `wetland`  |
| `encodingType` | 1            | Type d'encodage (conformité STA)        | "application/geo+json"                                                     |
| `geometry`     | 1            | Emprise GeoJSON de l'entité             | `Point` \| `Polygon` \| `LineString`                                       |
| `identifier`   | 0..* →Ident  | Codes externes et PID                   | → Identifier[]                                                             |

---

### TimeSerieDatastream
Utilisé par : TimeSerie (timeserieDatastream)
Note : lie une TimeSerie à ses Datastreams sources successifs dans le temps.
       Permet de remonter aux données brutes IoT quelle que soit la source.
       La succession de ces enregistrements constitue l'historique complet
       de la série — y compris les changements de capteur, de système ou de réseau.

| Champ          | Cardinalité | Définition                                  | Valeurs possibles                                  |
|----------------|-------------|---------------------------------------------|----------------------------------------------------|
| `id`           | 1           | Identifiant technique, clé primaire         | uuid                                               |
| `timeSerie`    | 1 →TS       | Série parente                               | → TimeSerie                                        |
| `datastreamId` | 1           | Identifiant du Datastream dans la source    | uuid \| code externe                               |
| `sourceUrl`    | 1           | URL de base du STA source                   | "https://iot.bdoh.inrae.fr/v1.1"                   |
| `sourceType`   | 1           | Type de source                              | `sta_2.0` \| `sta_1.1` \| `csv_archive` \| `other` |
| `validFrom`    | 1           | Début de la période                         | "1997-01-14T00:00:00Z"                             |
| `validTo`      | 0..1        | Fin de la période, null si courant          | null                                               |


### TimeSerie
Aligné avec : STA Datastream
Utilisé par : Station (timeSeries), ValidatedObservation (timeSerie), ControlObservation (timeSerie), TransferFunction (inputSeries), Transformation (inputSeries)
Note : porte tout ce qui est fixe et commun à toute la série.
       Contrat analytique garantissant la comparabilité de tous les points.
       Code généré : {station.code}-{property.code} ex: "yzr-mer-d610-hea"

| Champ                   | Cardinalité    | Définition                                    | Valeurs possibles                                         |
|-------------------------|----------------|-----------------------------------------------|-----------------------------------------------------------|
| `id`                    | 1              | Identifiant technique, clé primaire           | uuid                                                      |
| `code`                  | 1              | Code généré depuis station + property.code    | "yzr-mer-d610-hea"                                        |
| `name`                  | 1              | Nom lisible de la série                       | "Hauteur d'eau — Mercier au pont D610"                    |
| `description`           | 0..1           | Description libre                             |                                                           |
| `station`               | 1 →Sta         | Station de rattachement                       | → Station                                                 |
| `sensor`                | 1 →Sen         | Instrument actif (snapshot courant)           | → Sensor                                                  |
| `deployment`            | 0..1 →Dep      | Déploiement auquel appartient cette série     | → Deployment                                              |
| `property`              | 1 →Prop        | Variable mesurée                              | → Property                                                |
| `unit`                  | 1 →Unit        | Unité de mesure                               | → Unit                                                    |
| `procedure.observation` | 1 →Proc        | Protocole analytique fixe pour toute la série | → Procedure (type=observation)                            |
| `procedure.validation`  | 0..1 →Proc     | Règles de validation des données              | → Procedure (type=validation)                             |
| `sampledMedium`         | 1              | Milieu échantillonné (CV ODM2)                | `surfaceWater` \| `groundwater` \| `soil` \| `sediment` \| `poreWater` \| `atmosphere` |
| `observationType`       | 1              | Mode d'acquisition                            | `sensor_continuous` \| `lab_sample`                       |
| `startDate`             | 1              | Date de début de la série                     | "1997-01-14T08:01:00Z"                                    |
| `endDate`               | 0..1           | Date de fin, null si active                   | null                                                      |
| `status`                | 1              | État de la série                              | `active` \| `inactive` \| `discontinued`                  |
| `license`               | 1              | Licence des données                           | `ODbL` \| `CC-BY` \| `CC-BY-SA`                           |
| `timeserieDatastream`   | 0..* →TSD      | Datastreams sources successifs                | → TimeSerieDatastream[]                                   |
| `historicalProject`     | 0..* →HistProj | Succession des projets porteurs               | → HistoricalProject[]                                     |
| `keyword`               | 0..* →Keyw     | Keywords thématiques pour catalogues          | → Keyword[]                                               |
| `identifier`            | 0..* →Ident    | Codes externes et PID                         | → Identifier[]                                            |
| `memory`                | 0..* →Mem      | Notes et événements                           | → Memory[]                                                |

---


## Vocabulaire qualityFlag

Quatre valeurs internes BDOH mappées vers les standards environnementaux.

| BDOH      | ODM2      | SANDRE                  | STA resultQuality OGC |
|-----------|-----------|-------------------------|-----------------------|
| `good`    | Good      | 1 — Bonne               | `good`                |
| `suspect` | Suspect   | 3 — Douteuse            | `suspect`             |
| `bad`     | Bad       | 4 — Mauvaise            | `invalid`             |
| `missing` | Missing   | — (lacune)              | `missing`             |

Ce tableau est à placer dans standards/index.md ou decisions/index.md.


### ValidatedObservation
Aligné avec : STA Observation, ODM2 Result + DataQuality, Helmholtz SMS
Utilisé par : TimeSerie (observations)
Note : un point de mesure validé par un opérateur humain.
       Optionnellement rattaché à un prélèvement terrain (lab_sample uniquement).
       Le lien vers les données brutes IoT se fait via TimeSerie → TimeSerieDatastream + phenomenonTime.

| Champ               | Cardinalité  | Définition                                          | Valeurs possibles                                        |
|---------------------|--------------|-----------------------------------------------------|----------------------------------------------------------|
| `id`                | 1            | Identifiant technique, clé primaire                 | uuid                                                     |
| `timeSerie`         | 1 →TS        | Série parente                                       | → TimeSerie                                              |
| `phenomenonTime`    | 1            | Instant ou période du phénomène observé (STA)       | "2024-03-15T09:30:00Z" \| "2024-03-15T09:00:00Z/2024-03-15T10:00:00Z" |
| `resultTime`        | 0..1         | Instant où le résultat a été produit (STA)          | "2024-03-15T09:35:00Z"                                   |
| `result`            | 1            | Valeur numérique mesurée                            | "2.4"                                                    |
| `qualityFlag`       | 1            | Indicateur qualité (mapping ODM2/SANDRE en annexe)  | `good` \| `suspect` \| `bad` \| `missing`                |
| `qualityComment`    | 0..1         | Justification libre du flag qualité                 | "pic de crue suspect"                                    |
| `validatedBy`       | 0..1 →Per    | Personne ayant validé                               | → Person                                                 |
| `validatedAt`       | 0..1         | Date de validation                                  | "2024-03-20T14:00:00Z"                                   |
| `validationLogUrl`  | 0..1         | URI vers le log de validation externe               | "https://wiski.inrae.fr/exports/log-2024.csv"            |
| `samplingFeature`   | 0..1 →SF     | Prélèvement terrain associé (lab_sample uniquement) | → SamplingFeature                                        |
| `featureOfInterest` | 0..1 →FOI    | Entité réelle observée                              | → FeatureOfInterest                                      |
---

### ControlObservation
Utilisé par : TimeSerie (controlObservations)
Note : observation de contrôle qualité (blanc terrain, duplicate, étalon).
       Structure parallèle à ValidatedObservation avec rôle QC explicite.

| Champ                | Cardinalité  | Définition                                      | Valeurs possibles                                      |
|----------------------|--------------|-------------------------------------------------|--------------------------------------------------------|
| `id`                 | 1            | Identifiant technique, clé primaire             | uuid                                                   |
| `timeSerie`          | 1 →TS        | Série parente                                   | → TimeSerie                                            |
| `datetime`           | 1            | Horodatage                                      | "2024-03-15T09:30:00Z"                                 |
| `type`               | 1            | Type de contrôle                                | `field_blank` \| `duplicate` \| `standard` \| `spike`  |
| `result`             | 1            | Valeur mesurée                                  | "0.02"                                                 |
| `expectedResult`     | 0..1         | Valeur théorique pour étalon                    | "0.00"                                                 |
| `qualityFlag`        | 1            | Résultat du contrôle                            | `pass` \| `warn` \| `fail`                             |
| `sensor`             | 0..1 →Sen    | Instrument si différent de la TimeSerie         | → Sensor                                               |
| `procedure.control`  | 1 →Proc      | Protocole QC appliqué                           | → Procedure (type=control)                             |
| `samplingFeature`    | 0..1 →SF     | Prélèvement terrain associé                     | → SamplingFeature                                      |
| `featureOfInterest`  | 0..1 →FOI    | Entité réelle observée                          | → FeatureOfInterest                                    |

---

### SamplingFeature
Aligné avec : STA FeatureOfInterest (specimen), ODM2 Specimen
Utilisé par : ValidatedObservation (samplingFeature), ControlObservation (samplingFeature)
Note : acte de prélèvement terrain. Présent uniquement pour les séries de type lab_sample.
       La chaîne analytique interne au laboratoire est hors modèle — lien via limsReference.

| Champ                 | Cardinalité  | Définition                                         | Valeurs possibles                                        |
|-----------------------|--------------|----------------------------------------------------|----------------------------------------------------------|
| `id`                  | 1            | Identifiant technique, clé primaire                | uuid                                                     |
| `datetime`            | 1            | Horodatage du prélèvement                          | "2024-03-15T09:30:00Z"                                   |
| `project`             | 0..1 →Proj   | Projet ou campagne dont dépend ce prélèvement      | → Project                                                |
| `specimenType`        | 1            | Type de matériau prélevé (CV ODM2)                 | `water` \| `soil` \| `sediment` \| `poreWater` \| `rock` \| `biological` |
| `medium`              | 1            | Milieu de prélèvement (CV ODM2)                    | `surfaceWater` \| `groundwater` \| `depth` \| `interstitial` |
| `depth`               | 0..1         | Profondeur de prélèvement en mètres                | "0.30"                                                   |
| `volume`              | 0..1         | Volume prélevé en litres                           | "1.0"                                                    |
| `filtrationOnSite`    | 0..1         | Filtration effectuée sur le terrain                | `true` \| `false`                                        |
| `filtrationThreshold` | 0..1         | Seuil de filtration en µm                          | "0.45"                                                   |
| `operator`            | 0..1 →Per    | Personne ayant effectué le prélèvement             | → Person                                                 |
| `equipment`           | 0..1 →Equip  | Matériel de collecte utilisé                       | → Equipment                                              |
| `location`            | 0..1 →Loc    | Position exacte si différente de la Station        | → Location                                               |
| `condition`           | 0..1         | Observations terrain libres                        | "turbidité élevée, eau brune"                            |
| `derivedFrom`         | 0..1 →SF     | Specimen parent si sous-échantillon                | → SamplingFeature                                        |
| `identifier`          | 0..* →Ident  | Codes externes et PID                              | → Identifier[]                                           |
| `limsReference`       | 0..1         | Identifiant du prélèvement dans le LIMS            | "LIMS-2024-03-001"                                       |

---

## 8. TRANSFORMATION

### TransferFunction
Utilisé par : Station (transferFunctions), Transformation (transferFunction)
Note : fonction de conversion d'une mesure brute en valeur physique.
       Exemple : hauteur d'eau → débit via courbe de tarage.
       HistoricalTransferFunction = plusieurs TransferFunction avec validFrom/validTo
       successifs sur la même Station+inputProperty+outputProperty.

| Champ            | Cardinalité  | Définition                              | Valeurs possibles                                                   |
|------------------|--------------|-----------------------------------------|---------------------------------------------------------------------|
| `id`             | 1            | Identifiant technique, clé primaire     | uuid                                                                |
| `name`           | 1            | Nom de la fonction                      | "Courbe de tarage Mercier D610 v3"                                  |
| `station`        | 1 →Sta       | Station associée                        | → Station                                                           |
| `inputProperty`  | 1 →Prop      | Variable en entrée                      | → Property (ex: hauteur)                                            |
| `outputProperty` | 1 →Prop      | Variable en sortie                      | → Property (ex: débit)                                              |
| `type`           | 1            | Type de fonction                        | `rating_curve` \| `linear` \| `polynomial` \| `lookup_table`        |
| `parameters`     | 1            | Coefficients ou table de valeurs (JSON) | {"a":2.1,"b":1.5}                                                   |
| `procedure`      | 0..1 →Proc   | Méthode de construction de la courbe    | → Procedure                                                         |
| `operator`       | 0..1 →Org    | Organisation responsable                | → Organization                                                      |
| `validFrom`      | 1            | Début de validité                       | "2020-01-01T00:00:00Z"                                              |
| `validTo`        | 0..1         | Fin de validité, null si courante       | null                                                                |

---

### Transformation
Utilisé par : TransformedTimeSerie (transformation)
Note : instance d'exécution d'une transformation.
       Lie les séries sources à la série produite via une TransferFunction.

| Champ              | Cardinalité  | Définition                                    | Valeurs possibles          |
|--------------------|--------------|-----------------------------------------------|----------------------------|
| `id`               | 1            | Identifiant technique, clé primaire           | uuid                       |
| `transferFunction` | 1 →TF        | Fonction appliquée                            | → TransferFunction         |
| `inputSeries`      | 1..* →TS     | Séries sources                                | → TimeSerie[]              |
| `outputSeries`     | 1 →TTS       | Série produite                                | → TransformedTimeSerie     |
| `appliedAt`        | 1            | Date d'exécution                              | "2024-04-01T08:00:00Z"     |
| `appliedBy`        | 0..1 →Per    | Personne ayant lancé la transformation        | → Person                   |
| `validFrom`        | 1            | Début de validité du résultat                 | "2024-01-01T00:00:00Z"     |
| `validTo`          | 0..1         | Fin de validité                               | null                       |

---

### TransformedTimeSerie
Utilisé par : Station (transformedSeries), TimeSeriesBundle (transformedSeries), Transformation (outputSeries)
Note : série dérivée d'une ou plusieurs TimeSerie via une Transformation.
       Exemple : débit calculé à partir de hauteur d'eau.
       Code généré : {station.code}-{property.code} ex: "yzr-mer-d610-debit"

| Champ                      | Cardinalité  | Définition                                    | Valeurs possibles                         |
|----------------------------|--------------|-----------------------------------------------|-------------------------------------------|
| `id`                       | 1            | Identifiant technique, clé primaire           | uuid                                      |
| `code`                     | 1            | Code généré depuis station + property.code    | "yzr-mer-d610-debit"                      |
| `name`                     | 1            | Nom de la série dérivée                       | "Débit Mercier au pont D610"              |
| `description`              | 0..1         | Description libre                             |                                           |
| `station`                  | 1 →Sta       | Station de rattachement                       | → Station                                 |
| `property`                 | 1 →Prop      | Variable produite                             | → Property                                |
| `unit`                     | 1 →Unit      | Unité de la série dérivée                     | → Unit                                    |
| `processingLevel`          | 1            | Niveau de traitement (toujours derived)       | `derived`                                 |
| `procedure.transformation` | 1 →Proc      | Algorithme appliqué                           | → Procedure (type=transformation)         |
| `transformation`           | 1 →Trans     | Instance de calcul                            | → Transformation                          |
| `sourceSeries`             | 1..* →TS     | Séries sources utilisées                      | → TimeSerie[]                             |
| `status`                   | 1            | État de la série                              | `active` \| `inactive`                    |
| `identifier`               | 0..* →Ident  | Codes externes et PID                         | → Identifier[]                            |
| `memory`                   | 0..* →Mem    | Notes et événements                           | → Memory[]                                |

---

## 9. ORGANISATION

### TimeSeriesBundle
Utilisé par : Observatory (bundles)
Note : regroupe des TimeSerie et TransformedTimeSerie pour la publication
       ou l'accès thématique groupé. Objet éditorial — pas un objet technique.

| Champ               | Cardinalité  | Définition                                     | Valeurs possibles                        |
|---------------------|--------------|------------------------------------------------|------------------------------------------|
| `id`                | 1            | Identifiant technique, clé primaire            | uuid                                     |
| `name`              | 1            | Nom du bundle                                  | "Qualité eau Saône 2024"                 |
| `description`       | 0..1         | Description libre                              |                                          |
| `observatory`       | 1 →Obs       | Observatoire parent                            | → Observatory                            |
| `series`            | 0..* →TS     | Séries brutes incluses                         | → TimeSerie[]                            |
| `transformedSeries` | 0..* →TTS    | Séries dérivées incluses                       | → TransformedTimeSerie[]                 |
| `theme`             | 0..1         | Thème du regroupement                          | "qualité eau" \| "hydrologie"            |
| `license`           | 0..1         | Licence si différente de l'Observatory         | "CC-BY"                                  |
| `keyword`           | 0..* →Keyw   | Keywords thématiques pour catalogues           | → Keyword[]                              |

---

### Memory
Utilisé par : Observatory, Site, Station, Sensor, Equipment, TimeSerie, TransformedTimeSerie, Deployment, Project (via resourceType + resourceId)
Note : note contextuelle ou événement daté rattaché à n'importe quelle ressource.
       Objet transversal — ne porte pas de données scientifiques, documente le cycle de vie.
       Les fichiers (photos, documents) sont stockés dans le S3 et référencés via mediaUrl.

| Champ          | Cardinalité | Définition                        | Valeurs possibles                                                                 |
|----------------|-------------|-----------------------------------|-----------------------------------------------------------------------------------|
| `id`           | 1           | Identifiant technique, clé primaire | uuid                                                                            |
| `resourceType` | 1           | Type de ressource ciblée          | `Observatory` \| `Site` \| `Station` \| `Sensor` \| `Equipment` \| `TimeSerie` \| `TransformedTimeSerie` \| `Deployment` \| `Project` |
| `resourceId`   | 1           | UUID de la ressource ciblée       | uuid                                                                              |
| `datetime`     | 1           | Date de la note ou de l'événement | "2014-04-17T00:00:00Z"                                                            |
| `type`         | 1           | Type de mémo                      | `note` \| `event` \| `document` \| `photo` \| `installation` \| `hydraulic_change` \| `maintenance` \| `incident` \| `calibration` |
| `title`        | 0..1        | Titre court                       | "Modification contrôle hydraulique"                                               |
| `content`      | 0..1        | Texte libre                       | "Installation d'une lame déversante"                                              |
| `mediaUrl`     | 0..*        | Photos ou documents associés (S3) | "https://storage.obs.fr/memories/2014-lame.jpg"                                   |
| `author`       | 0..1 →Per   | Auteur de la note                 | → Person                                                                          |



