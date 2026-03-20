# Référentiels

Les référentiels sont des entités stables gérées par les curateurs. Elles définissent le vocabulaire commun du modèle — variables, unités, protocoles, classifications thématiques et identifiants externes.

---

## Property

Aligné avec : STA ObservedProperty, NERC NVS P01, Helmholtz SMS CV, ODM2 Variable

Utilisé par : [TimeSerie](observation.md#timeserie) (property), [TransformedTimeSerie](transformation.md#transformedtimeserie) (property), [TransferFunction](transformation.md#transferfunction) (inputProperty, outputProperty)

!!! note
    Chaque variable est unique et non dupliquée — gérée par les curateurs.
    Les URIs vers les thésaurus externes (NERC P01, Theia/OZCAR, SANDRE...) sont portées par `identifier`.
    `discipline` et `theme` suivent un vocabulaire contrôlé interne BDOH.

| Champ            | Cardinalité  | Définition                                  | Valeurs possibles                                                                                                                                                                                         |
|------------------|--------------|---------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `id`             | 1            | Identifiant technique, clé primaire         | uuid                                                                                                                                                                                                      |
| `code`           | 1            | Code court unique, saisi par curateur (2-8 cars) | "no3" \| "debit" \| "doc" \| "bact-div"                                                                                                                                                              |
| `symbol`         | 0..1         | Symbole scientifique universel              | "NO3" \| "Q" \| "DOC"                                                                                                                                                                                     |
| `name`           | 1            | Nom de la variable                          | "Nitrate" \| "Débit journalier maximal annuel"                                                                                                                                                            |
| `definition`     | 0..1         | Définition textuelle                        | "Maximum annuel du débit journalier"                                                                                                                                                                      |
| `defaultUnit`    | 0..1 →Unit   | Unité par défaut                            | → [Unit](#unit)                                                                                                                                                                                           |
| `sourceProperty` | 0..1 →Prop   | Variable source pour les variables dérivées | → Property (ex: "Q" pour "QJXA")                                                                                                                                                                         |
| `discipline`     | 1            | Famille majeure (vocabulaire contrôlé BDOH) | `hydrology` \| `chemistry` \| `meteorology` \| `sediment` \| `microbiology` \| `general`                                                                                                                 |
| `theme`          | 0..1         | Famille mineure (vocabulaire contrôlé BDOH) | `metals` \| `nutrients` \| `bacterialDiversity` \| `bacterialAbundance` \| `bacterialResistance` \| `radionuclides` \| `pesticides` \| `pharmaceuticals` \| `persistentOrganicPollutants` \| `organicMicropollutants` \| `general` |
| `samplingMedium` | 0..1         | Milieu intrinsèque à la variable (CV ODM2)  | `air` \| `surfaceWater` \| `groundwater` \| `soil` \| `sediment` \| `poreWater` \| `atmosphere`                                                                                                          |
| `aggregationType`| 0..1         | Type d'agrégation temporelle                | `average` \| `sum` \| `min` \| `max` \| `instantaneous` \| `cumulative`                                                                                                                                  |
| `samplingPeriod` | 0..1         | Début de la période de référence (MM-JJ)    | null \| "09-01" \| "01-01"                                                                                                                                                                                |
| `variableType`   | 0..1         | Nature physique — calcul de delta           | `intensive` \| `extensive`                                                                                                                                                                                |
| `valueType`      | 0..1         | Nature des valeurs                          | `continuous` \| `discrete` \| `categorical` \| `temporal`                                                                                                                                                |
| `origin`         | 0..1         | Mode de production                          | `observed` \| `derived` \| `simulated`                                                                                                                                                                   |
| `status`         | 1            | Statut du terme géré par les curateurs      | `accepted` \| `deprecated` \| `proposed`                                                                                                                                                                  |
| `identifier`     | 0..* →Ident  | URIs vers vocabulaires externes             | → [Identifier](#identifier)[]                                                                                                                                                                             |

---

## Unit

Utilisé par : [Property](#property) (defaultUnit), [TimeSerie](observation.md#timeserie) (unit), [TransformedTimeSerie](transformation.md#transformedtimeserie) (unit)

| Champ        | Cardinalité | Définition                          | Valeurs possibles                                  |
|--------------|-------------|-------------------------------------|----------------------------------------------------|
| `id`         | 1           | Identifiant technique, clé primaire | uuid                                               |
| `code`       | 1           | Code court pour URLs (kebab-case)   | "mg-l" \| "m3-s" \| "degc"                        |
| `symbol`     | 1           | Symbole textuel affiché             | "mg/L" \| "m³/s" \| "°C"                          |
| `name`       | 1           | Nom complet de l'unité              | "milligram per litre"                              |
| `definition` | 1           | URI QUDT ou UCUM                    | "http://qudt.org/vocab/unit/MilliGM-PER-L"         |

---

## Procedure

Utilisé par : [TimeSerie](observation.md#timeserie) (procedure.observation, procedure.validation), [ControlObservation](observation.md#controlobservation) (procedure.control), [TransferFunction](transformation.md#transferfunction) (procedure), [TransformedTimeSerie](transformation.md#transformedtimeserie) (procedure.transformation)

!!! note
    Entité générique pour tout protocole. Le champ `type` discrimine le rôle.

| Champ          | Cardinalité | Définition                              | Valeurs possibles                                                  |
|----------------|-------------|-----------------------------------------|--------------------------------------------------------------------|
| `id`           | 1           | Identifiant technique, clé primaire     | uuid                                                               |
| `code`         | 1           | Code court unique, saisi par curateur   | "iso-10304-1"                                                      |
| `name`         | 1           | Nom du protocole                        | "NF EN ISO 10304-1"                                                |
| `type`         | 1           | Rôle du protocole                       | `observation` \| `validation` \| `control` \| `transformation`    |
| `description`  | 0..1        | Description libre                       |                                                                    |
| `version`      | 0..1        | Version du protocole                    | "2021"                                                             |
| `reference`    | 0..1        | URI ou DOI du document normatif         | "https://www.iso.org/standard/..."                                 |
| `encodingType` | 1           | Type d'encodage (conformité STA)        | "application/pdf" \| URI                                           |

---

## Keyword

Aligné avec : ISO 19115 MD_Keywords, DataCite subject, DCAT keyword

Utilisé par : [Property](#property), [Observatory](network.md#observatory), [TimeSerie](observation.md#timeserie), [TimeSeriesBundle](organisation.md#timeseriesbundle)

!!! note
    `keywordType` suit le vocabulaire `MD_KeywordTypeCode` d'ISO 19115 :

    - `discipline` → domaine scientifique (Hydrologie, Chimie...)
    - `theme` → sujet thématique fin (Métaux, Nutrients...)
    - `place` → lieu géographique ("Bassin Rhône", "France")
    - `temporal` → période temporelle ("Holocène", "21e siècle")
    - `stratum` → couche géologique ou verticale ("Zone saturée")
    - `taxon` → taxon biologique ("Escherichia coli")
    - `instrument` → type d'instrument
    - `process` → processus observé

| Champ         | Cardinalité | Définition                                      | Valeurs possibles                                                                                      |
|---------------|-------------|-------------------------------------------------|--------------------------------------------------------------------------------------------------------|
| `id`          | 1           | Identifiant technique, clé primaire             | uuid                                                                                                   |
| `term`        | 1           | Terme de classification                         | "Hydrologie" \| "Métaux et métalloïdes"                                                                |
| `keywordType` | 1           | Type de keyword (MD_KeywordTypeCode ISO 19115)  | `discipline` \| `theme` \| `place` \| `temporal` \| `stratum` \| `taxon` \| `instrument` \| `process` |
| `thesaurus`   | 0..1        | Vocabulaire source                              | "BDOH" \| "TheiaOZCAR" \| "GCMD" \| "SANDRE" \| "free"                                                |
| `uri`         | 0..1        | URI du terme dans le thésaurus                  | "https://w3id.org/ozcar-theia/..."                                                                     |

---

## Identifier

Aligné avec : ODM2 ExternalIdentifiers, schema.org identifier

Utilisé par : Observatory, Site, Station, Sensor, Equipment, TimeSerie, Person, Organization, SamplingFeature, Property, Project (via resourceType + resourceId)

!!! note
    Permet autant de PIDs que nécessaire sur n'importe quelle ressource.
    Si `codeType = uri` alors `code` contient directement l'URI de résolution.

| Champ          | Cardinalité | Définition                              | Valeurs possibles                                                                                                      |
|----------------|-------------|-----------------------------------------|------------------------------------------------------------------------------------------------------------------------|
| `id`           | 1           | Identifiant technique, clé primaire     | uuid                                                                                                                   |
| `code`         | 1           | Valeur de l'identifiant ou URI complète | "V3015810" \| "https://w3id.org/ozcar-theia/c_xxx"                                                                    |
| `codeType`     | 1           | Type d'identifiant                      | `localCode` \| `uri` \| `doi` \| `orcid` \| `ror` \| `sandre` \| `wigos` \| `igsn` \| `other`                        |
| `codeSource`   | 1           | Système ou organisme émetteur           | "SANDRE" \| "TheiaOZCAR" \| "NERC" \| "DataCite" \| "ORCID" \| "ROR"                                                 |
| `resourceType` | 1           | Type de ressource ciblée                | `Observatory` \| `Site` \| `Station` \| `Sensor` \| `Equipment` \| `TimeSerie` \| `Person` \| `Organization` \| `SamplingFeature` \| `Property` \| `Project` |
| `resourceId`   | 1           | UUID de la ressource ciblée             | uuid                                                                                                                   |
