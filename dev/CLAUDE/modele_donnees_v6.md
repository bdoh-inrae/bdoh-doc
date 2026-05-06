# Modèle de données BDOH v6 -- Métadonnées des entités

## Convention de lecture

Ce fichier est le **modèle de données BDD** de BDOH. Chaque tableau décrit
les colonnes réelles d'une table SQL. Les relations inverses (0..*) n'apparaissent
pas dans les tableaux -- elles sont accessibles via requête sur la table qui porte
la FK, et documentées dans les notes de chaque entité.

### Note pour l'API
Toutes les relations inverses supprimées ici réapparaissent comme endpoints
de navigation dans l'API :
```
GET /{resource}/{id}/identifiers    → Identifier WHERE resourceId={id}
GET /{resource}/{id}/memories       → Memory WHERE resourceId={id}
GET /{resource}/{id}/responsibilities → Responsibility WHERE resourceId={id}
GET /{resource}/{id}/keywords       → KeywordAssignment WHERE resourceId={id}
GET /{resource}/{id}/projects       → HistoricalProject WHERE resourceId={id}
GET /{resource}/{id}/locations      → HistoricalLocation WHERE resourceId={id}
GET /{resource}/{id}/instruments    → InstrumentUsage WHERE resourceId={id}
```
Les tables de jointure explicites (Person.organization, Bundle.series,
TransformationBatch.inputSeries) deviennent des endpoints bidirectionnels.

### Cardinalités
- `1` = obligatoire -- `0..1` = optionnel -- `1..*` = un ou plus -- `0..*` = table de jointure explicite

### Patterns transversaux -- tables polymorphiques

Ces tables portent la FK vers la ressource cible via `resourceType + resourceId`.
Elles ne génèrent aucune colonne dans les tables cibles.

| Table               | Ce qu'elle stocke                        | Ressources supportées                                                                 |
|---------------------|------------------------------------------|---------------------------------------------------------------------------------------|
| `Identifier`        | PIDs vers référentiels externes          | toutes les entités navigables                                                         |
| `Memory`            | Notes, événements, photos                | Observatory, Site, Station, Sensor, Equipment, TimeSerie, TransformedTimeSerie, Deployment, Project, TransferFunction |
| `Responsibility`    | Rôles de personnes/organisations         | Observatory, Site, Station, TimeSerie, Project, TransferFunction, Equipment, Sensor   |
| `KeywordAssignment` | Mots-clés et classifications contrôlées  | toutes les entités (voir KeywordAssignment.resourceType)                              |
| `KeywordRequirement`| Règles de complétion minimale            | défini par resourceType + keywordType                                                 |
| `HistoricalLocation`| Positions géographiques successives      | Observatory, Site, Station                                                            |
| `HistoricalProject` | Projets porteurs successifs              | Observatory, Site, Station, TimeSerie                                                 |
| `InstrumentUsage`   | Capteurs et équipements utilisés         | Station, TimeSerie, Deployment, SamplingFeature                                       |

### Tables de jointure explicites

Ces tables encodent des relations many-to-many portées par l'entité "propriétaire".

| Table                              | Entre                                   |
|------------------------------------|-----------------------------------------|
| `person_organization`              | Person ↔ Organization                   |
| `transformationbatch_inputseries`  | TransformationBatch ↔ TimeSerie         |
| `bundle_timeserie`                 | TimeSeriesBundle ↔ TimeSerie            |
| `bundle_transformedtimeserie`      | TimeSeriesBundle ↔ TransformedTimeSerie |

### Identifiants : UUID, code slug et permalink

**UUID** : clé primaire technique sur toutes les entités. Immuable, jamais exposé
dans les URLs courantes. Sert de permalink stable pour les citations scientifiques.

```
Permalink : /resources/{uuid}
```

**code** : slug lisible, obligatoire (`1`) sur toutes les entités. Modifiable par
l'utilisateur. Une suggestion automatique est proposée à la création depuis le `name`
(ou le `serialNumber` pour Sensor et Equipment). Le code est unique dans son scope
parent -- deux entités de scopes différents peuvent avoir le même code.

Scopes d'unicité :
```
Observatory          unique globalement
Organization         unique globalement
Sensor               unique globalement
Equipment            unique globalement
Project              unique globalement
Procedure            unique globalement
Property             unique globalement
Unit                 unique globalement
Site                 unique par Observatory
Station              unique par Site
Deployment           unique par Station
TimeSerie            unique par Station
Datastream           unique par Station
TransferFunction     unique par Station
TransformedTimeSerie unique par Station
```

Les codes externes (SANDRE, TheiaOZCAR, WIGOS...) sont portés par `identifier`,
pas par `code`. Le `code` est interne a BDOH.

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
> Individu impliqué dans la production ou la gestion des données.
Aligné avec : ODM2 People, STAMPLATE schema.org/Person, ISO 19115
Utilisé par : SamplingFeature (operator), ValidatedObservation (validatedBy),
             Responsibility (person), TransformationBatch (appliedBy), Memory (author)
Relations inverses : aucune (Person est référencée par d'autres entités)
Note : organization est une table de jointure explicite `person_organization` --
       affiliation institutionnelle, distinct de Responsibility (rôle fonctionnel).
       Une personne peut appartenir à plusieurs organisations simultanément.

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
> Structure porteuse (laboratoire, observatoire, agence...).
Aligné avec : ODM2 Organizations, STAMPLATE schema.org/Organization, ROR
Utilisé par : Person via person_organization (table jointure),
             Responsibility (organization), Project (fundingAgency),
             Equipment (owner)
Relations inverses : aucune
Note : code slug unique globalement -- suggestion depuis acronym ou name à la création.
       Type via KeywordAssignment (keywordType='organizationType') :
       valeurs courantes : laboratory, monitoring_network, research, agency, university

| Champ        | Cardinalité | Définition                                  | Valeurs possibles                                                          |
|--------------|-------------|---------------------------------------------|----------------------------------------------------------------------------|
| `id`         | 1           | Identifiant technique, clé primaire         | uuid                                                                       |
| `code`       | 1           | Slug unique globalement                     | "inrae"                                                                    |
| `name`       | 1           | Nom complet                                 | "Institut national de recherche pour l'agriculture..."                     |
| `acronym`    | 0..1        | Sigle                                       | "INRAE"                                                                    |
| `country`    | 1           | Pays (code ISO 3166-1 alpha-2)              | "FR"                                                                       |
| `url`        | 0..1        | Site web                                    | "https://www.inrae.fr"                                                     |
| `logoUrl`    | 0..1        | URL vers le logo (S3 ou hébergeur officiel) | "https://www.inrae.fr/logo.svg"                                            |

---

### Responsibility
> Rôle d'une personne ou organisation sur une ressource à un instant T.
Aligné avec : ISO 19115 CI_Responsibility + CI_RoleCode, ODM2 Affiliations,
             STAMPLATE schema.org/Role
Utilisé par : Observatory, Site, Station, TimeSerie, Project, TransferFunction
             (via resourceType + resourceId)
Note : lie une Person ou une Organization à une ressource avec un rôle fonctionnel.
       Distinct de Person.organization (appartenance institutionnelle).
       Contrainte : person et organization ne peuvent pas être tous les deux null.

| Champ          | Cardinalité | Définition                               | Valeurs possibles                                                           |
|----------------|-------------|------------------------------------------|-----------------------------------------------------------------------------|
| `id`           | 1           | Identifiant technique, clé primaire      | uuid                                                                        |
| `person`       | 0..1 →Per   | Personne responsable                     | → Person                                                                    |
| `organization` | 0..1 →Org   | Organisation responsable                 | → Organization                                                              |
| `role`         | 1           | Rôle fonctionnel CI_RoleCode ISO 19115   | `pointOfContact` \| `principalInvestigator` \| `author` \| `processor` \| `publisher` \| `custodian` \| `owner` \| `distributor` \| `originator` \| `resourceProvider` \| `user` |
| `resourceType` | 1           | Type de ressource ciblée                 | `Observatory` \| `Site` \| `Station` \| `TimeSerie` \| `Project` \| `TransferFunction` |
| `resourceId`   | 1           | UUID de la ressource ciblée              | uuid                                                                        |
| `validFrom`    | 0..1        | Début de responsabilité                  | "2022-01-01"                                                                |
| `validTo`      | 0..1        | Fin, null si toujours actif              | "2024-12-31" \| null                                                        |

---

## 2. RÉFÉRENTIELS

### Property
> Variable mesurée ou calculée (température, débit, nitrates...).
Aligné avec : STA ObservedProperty, NERC NVS P01, Helmholtz SMS CV,
             ODM2 Variables, HydroServer ObservedProperty
Utilisé par : TimeSerie (property), TransformedTimeSerie (property),
             TransferFunction (inputProperty, outputProperty), Datastream (property)
Relations inverses : Identifier, KeywordAssignment
Note : géré par les curateurs -- chaque variable est unique et non dupliquée.
       URIs vers thésaurus externes via identifier.
       Correspond à ObservedProperty dans l'API STA exposée.
       Keywords attendus via KeywordAssignment (voir KeywordRequirement) :
         discipline (required)  -- ex: hydrology, chemistry, meteorology
         theme (recommended)    -- ex: metals, nutrients, pesticides
         samplingMedium (recommended) -- ex: surfaceWater, groundwater, soil

| Champ           | Cardinalité | Définition                             | Valeurs possibles                                                            |
|-----------------|-------------|----------------------------------------|------------------------------------------------------------------------------|
| `id`            | 1           | Identifiant technique, clé primaire    | uuid                                                                         |
| `code`          | 1           | Code court unique, curateur (2-8 cars) | "no3" \| "debit" \| "doc" \| "bact-div"                                      |
| `symbol`        | 0..1        | Symbole scientifique universel         | "NO3" \| "Q" \| "DOC"                                                        |
| `name`          | 1           | Nom de la variable                     | "Nitrate" \| "Débit journalier maximal annuel"                               |
| `definition`    | 0..1        | Définition textuelle                   | "Maximum annuel du débit journalier"                                         |
| `defaultUnit`   | 0..1 →Unit  | Unité par défaut                       | → Unit                                                                       |
| `sourceProperty`| 0..1 →Prop  | Variable source pour les dérivées      | → Property (ex: "Q" pour "QJXA")                                             |
| `origin`        | 0..1        | Mode de production                     | `observed` \| `derived`                                                      |
| `status`        | 1           | Statut géré par les curateurs          | `accepted` \| `deprecated` \| `proposed`                                     |

---

### Unit
> Unité de mesure associée à une Property.
Aligné avec : ODM2 Units, HydroServer Unit, QUDT, UCUM
Utilisé par : Property (defaultUnit), TimeSerie (unit),
             TransformedTimeSerie (unit), Datastream (unitOfMeasurement)
Note : HydroServer ajoute Unit comme entité séparée car STA standard
       n'a qu'un objet JSON inline pour unitOfMeasurement dans Datastream.

| Champ        | Cardinalité | Définition                          | Valeurs possibles                                  |
|--------------|-------------|-------------------------------------|----------------------------------------------------|
| `id`         | 1           | Identifiant technique, clé primaire | uuid                                               |
| `code`       | 1           | Code court pour URLs (kebab-case)   | "mg-l" \| "m3-s" \| "degc"                         |
| `symbol`     | 1           | Symbole textuel affiché             | "mg/L" \| "m³/s" \| "°C"                           |
| `name`       | 1           | Nom complet de l'unité              | "milligram per litre"                              |
| `definition` | 1           | URI QUDT ou UCUM                    | "http://qudt.org/vocab/unit/MilliGM-PER-L"         |

---

### Procedure
> Protocole appliqué -- de prélèvement, mesure, modélisation, agrégation, transformation ou validation.
Aligné avec : STA Sensor (procédure de mesure), ODM2 Methods,
             OGC OMS ObservingProcedure, Helmholtz SMS
Utilisé par : TimeSerie (procedure.observation, procedure.validation),
             ControlObservation (procedure.observation),
             TransferFunction (procedure.modeling),
             TransformedTimeSerie (procedure.transformation),
             Datastream (procedure)
Note : entité réutilisable -- une même Procedure peut être référencée par
       plusieurs objets. Le type discrimine le rôle et filtre les choix
       dans l'interface.
       Dans STA, Procedure correspond à l'entité Sensor quand elle décrit
       une méthode de mesure (encodingType + metadata).

       Types et exemples :
       sampling      -- prélever un échantillon terrain
                        ex: "Prélèvement eau de surface au seau"
                        ex: "Prélèvement automatique ISCO 3700"
       observation   -- mesurer une valeur (capteur continu, labo, jaugeage, contrôle)
                        ex: "NF EN ISO 10304-1 chromatographie ionique"
                        ex: "Jaugeage au micro-moulinet OTT C2"
                        ex: "Mesure sonde multiparamètre YSI EXO2"
       modeling      -- construire un modèle depuis des mesures
                        ex: "BaRatin v3 -- courbe de tarage bayésienne"
                        ex: "Régression polynomiale turbidité/MES"
                        ex: "Courbe d'étalonnage spectrophotométrie"
       aggregation   -- agréger temporellement ou spatialement des valeurs
                        ex: "Moyenne journalière sur plage horaire"
                        ex: "Agrégation annuelle QJXA depuis débits journaliers"
                        ex: "Cumul pluviométrique mensuel"
       transformation -- appliquer un calcul pour produire de nouvelles valeurs
                        ex: "Application courbe de tarage par interpolation linéaire"
                        ex: "Correction offset dérive capteur"
       validation    -- qualifier des données existantes
                        ex: "Validation visuelle Wiski par opérateur"
                        ex: "Pipeline automatique contrôle bornes SANDRE"

| Champ          | Cardinalité | Définition                           | Valeurs possibles                                                               |
|----------------|-------------|--------------------------------------|---------------------------------------------------------------------------------|
| `id`           | 1           | Identifiant technique, clé primaire  | uuid                                                                            |
| `code`         | 1           | Slug unique globalement              | "iso-10304-1"                                                                   |
| `name`         | 1           | Nom du protocole                     | "NF EN ISO 10304-1"                                                             |
| `type`         | 1           | Rôle du protocole                    | `sampling` \| `observation` \| `modeling` \| `aggregation` \| `transformation` \| `validation` |
| `description`  | 0..1        | Description libre                    |                                                                                 |
| `version`      | 0..1        | Version du protocole                 | "2021"                                                                          |
| `reference`    | 0..1        | URI ou DOI du document normatif      | "https://www.iso.org/standard/..."                                              |
| `encodingType` | 1           | Type d'encodage (conformité STA)     | "application/pdf" \| URI                                                        |

---

### KeywordType
> Type de métadonnée contrôlée -- documente à quel standard ce type est aligné.
Aligné avec : ISO 19115 MD_KeywordTypeCode, ODM2 CV types
Utilisé par : Keyword (keywordType), KeywordAssignment (keywordType), KeywordRequirement (keywordType)
Note : chaque type de keyword est lui-même documenté et aligné avec un standard.
       Géré par les administrateurs BDOH.
       Exemples de types : discipline, theme, samplingMedium, stationType,
       sensorType, equipmentType, siteType, deploymentType, featureType,
       memoryType, controlType, organizationType, specimenType.

| Champ         | Cardinalité | Définition                                  | Valeurs possibles                             |
|---------------|-------------|---------------------------------------------|-----------------------------------------------|
| `id`          | 1           | Identifiant technique, clé primaire         | uuid                                          |
| `code`        | 1           | Code interne unique                         | "discipline" \| "stationType" \| "sensorType" |
| `label_fr`    | 1           | Libellé français                            | "Discipline scientifique"                     |
| `label_en`    | 1           | Libellé anglais                             | "Scientific discipline"                       |
| `description` | 0..1        | Description du rôle de ce type              |                                               |
| `standard`    | 0..1        | Standard d'alignement                       | "ISO 19115" \| "ODM2" \| "BDOH"               |
| `standardUri` | 0..1        | URI vers le concept dans le standard        | "https://standards.iso.org/..."               |

---

### Keyword
> Terme de vocabulaire contrôlé -- aligné avec un thésaurus externe autant que possible.
Aligné avec : ISO 19115 MD_Keywords, ODM2 CV, TheiaOZCAR thesaurus, NERC NVS
Utilisé par : KeywordAssignment (keyword)
             entités via KeywordAssignment (type, discipline, theme...)
Note : vocabulaire géré par les curateurs BDOH.
       Chaque terme doit idéalement pointer vers un thésaurus externe via uri.
       Les termes BDOH sans équivalent externe utilisent thesaurus='BDOH'.
       Utilisé de deux façons :
         1. Via KeywordAssignment -- tags multi-valeurs sur une ressource
         2. Via FK directe -- champ type sur Organization, Site, Station, etc.

| Champ          | Cardinalité | Définition                              | Valeurs possibles                                |
|----------------|-------------|-----------------------------------------|--------------------------------------------------|
| `id`           | 1           | Identifiant technique, clé primaire     | uuid                                             |
| `keywordType`  | 1 →KWT      | Type de ce keyword                      | → KeywordType                                    |
| `term_fr`      | 1           | Terme en français                       | "eau de surface" \| "hydrologie"                 |
| `term_en`      | 1           | Terme en anglais                        | "surface water" \| "hydrology"                   |
| `definition_fr`| 0..1        | Définition en français                  |                                                  |
| `definition_en`| 0..1        | Définition en anglais                   |                                                  |
| `thesaurus`    | 0..1        | Vocabulaire source                      | "ODM2" \| "TheiaOZCAR" \| "SANDRE" \| "BDOH"     |
| `uri`          | 0..1        | URI du terme dans le thésaurus          | "http://vocabulary.odm2.org/medium/surfaceWater" |

---

### KeywordAssignment
> Lien entre un keyword et une ressource -- pattern polymorphique multi-valeurs.
Utilisé par : Observatory, Site, Station, TimeSerie, TransformedTimeSerie,
             TimeSeriesBundle, Property, Organization, Sensor, Equipment,
             Deployment, FeatureOfInterest, SamplingFeature, ControlObservation,
             TransferFunction, Datastream (via resourceType + resourceId)
Note : permet d'attacher autant de keywords que nécessaire à une ressource.
       Couvre les classifications multi-valeurs (discipline, theme, samplingMedium...)
       et les tags éditoriaux libres pour les catalogues.
       Les règles de complétion minimale sont dans KeywordRequirement.

| Champ          | Cardinalité | Définition                          | Valeurs possibles                                                                |
|----------------|-------------|-------------------------------------|----------------------------------------------------------------------------------|
| `id`           | 1           | Identifiant technique, clé primaire | uuid                                                                             |
| `keyword`      | 1 →Keyw     | Keyword assigné                     | → Keyword                                                                        |
| `resourceType` | 1           | Type de ressource ciblée            | `Observatory` \| `Site` \| `Station` \| `TimeSerie` \| `TransformedTimeSerie` \| `TimeSeriesBundle` \| `Property` \| `Organization` \| `Sensor` \| `Equipment` \| `Deployment` \| `FeatureOfInterest` \| `SamplingFeature` \| `ControlObservation` \| `TransferFunction` \| `Datastream` |
| `resourceId`   | 1           | UUID de la ressource ciblée         | uuid                                                                             |

---

### KeywordRequirement
> Règle de complétion minimale -- définit quels keywords sont obligatoires ou recommandés sur un type de ressource.
Utilisé par : validation applicative à la sauvegarde
Note : géré par les administrateurs BDOH sans migration de schéma.
       Permet de définir des standards de métadonnées sans contrainte SQL rigide.
       Exemples : Property doit avoir au moins un keyword de type 'discipline',
                  TimeSerie doit avoir au moins un keyword de type 'samplingMedium'.

| Champ          | Cardinalité | Définition                              | Valeurs possibles                                                            |
|----------------|-------------|-----------------------------------------|------------------------------------------------------------------------------|
| `id`           | 1           | Identifiant technique, clé primaire     | uuid                                                                         |
| `resourceType` | 1           | Type de ressource concerné              | `Property` \| `TimeSerie` \| `Station` \| `SamplingFeature` \| ...           |
| `keywordType`  | 1 →KWT      | Type de keyword requis                  | → KeywordType                                                                |
| `cardinality`  | 1           | Niveau d'obligation                     | `required` \| `recommended`                                                  |

---

### License
> Licence de diffusion des données.
Utilisé par : Datastream (license), TimeSerie (license),
             TransformedTimeSerie (license), TimeSeriesBundle (license)
Note : toute licence implique un niveau d'accès -- une licence CC-BY est ouverte,
       une licence contractuelle est fermée ou restreinte.
       Obligatoire sur tous les flux de données.
       Gérée par les administrateurs BDOH.

| Champ  | Cardinalité | Définition                          | Valeurs possibles                                    |
|--------|-------------|-------------------------------------|------------------------------------------------------|
| `id`   | 1           | Identifiant technique, clé primaire | uuid                                                 |
| `code` | 1           | Code court unique                   | "cc-by-4.0" \| "odbl-1.0" \| "proprietary-inrae"     |
| `name` | 1           | Nom complet de la licence           | "Creative Commons Attribution 4.0"                   |
| `url`  | 0..1        | URL vers le texte officiel          | "https://creativecommons.org/licenses/by/4.0/"       |

---

### Identifier
> Code externe vers un référentiel tiers (SANDRE, TheiaOZCAR, WIGOS...).
Aligné avec : ODM2 ExternalIdentifiers, schema.org identifier,
             INSPIRE ExternalObjectIdentifier
Utilisé par : Observatory, Site, Station, Sensor, Equipment, TimeSerie,
             Person, Organization, SamplingFeature, Property, Project
             (via resourceType + resourceId)
Note : permet autant de PIDs que nécessaire sur n'importe quelle ressource.
       Les URIs de thésaurus (TheiaOZCAR, ODM2...) vont dans Keyword.uri,
       pas ici -- Identifier est réservé aux PIDs de ressources réelles.

| Champ          | Cardinalité | Définition                              | Valeurs possibles                                                            |
|----------------|-------------|-----------------------------------------|------------------------------------------------------------------------------|
| `id`           | 1           | Identifiant technique, clé primaire     | uuid                                                                         |
| `code`         | 1           | Valeur de l'identifiant                 | "V3015810" \| "0000-0001-1234-1234" \| "0-20000-0-06610"                     |
| `codeType`     | 1           | Type d'identifiant                      | `doi` \| `orcid` \| `ror` \| `sandre` \| `wigos` \| `igsn` \| `pidinst` \| `other` |
| `codeSource`   | 1           | Système ou organisme émetteur           | "SANDRE" \| "TheiaOZCAR" \| "NERC" \| "DataCite" \| "ROR" \| "PIDINST"       |
| `resourceType` | 1           | Type de ressource ciblée                | `Observatory` \| `Site` \| `Station` \| `Sensor` \| `Equipment` \| `TimeSerie` \| `Person` \| `Organization` \| `SamplingFeature` \| `Property` \| `Project` \| `TransferFunction` |
| `resourceId`   | 1           | UUID de la ressource ciblée             | uuid                                                                         |

---

## 3. GÉOGRAPHIE

### Location
> Géométrie pure d'un objet (point GPS, polygone...) sans dimension temporelle.
Aligné avec : STA Location, OGC GeoJSON, ISO 19107
Utilisé par : HistoricalLocation (location), Observatory (location courante),
             Site (location courante), Station (location courante),
             Deployment (location), SamplingFeature (location)
Note : décrit uniquement la géométrie, sans dimension temporelle.
       La temporalité est portée par HistoricalLocation.
       Partagée entre couche IoT STA et backend BDOH -- même UUID.

| Champ          | Cardinalité | Définition                          | Valeurs possibles                    |
|----------------|-------------|-------------------------------------|--------------------------------------|
| `id`           | 1           | Identifiant technique, clé primaire | uuid                                 |
| `encodingType` | 1           | Type d'encodage (conformité STA)    | "application/geo+json"               |
| `geometry`     | 1           | Géométrie GeoJSON                   | `Point` \| `Polygon` \| `LineString` |
| `crs`          | 1           | Système de référence de coordonnées | "EPSG:4326" \| "EPSG:2154"           |
| `description`  | 0..1        | Description libre                   |                                      |

---

### HistoricalLocation
> Succession des positions géographiques d'une ressource dans le temps -- une seule position active à la fois.
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
> Réseau d'observatoires environnementaux -- entité racine du modèle.
Aligné avec : STA Thing (properties), schema.org/ResearchProject,
             ISO 19115 MD_DataIdentification, INSPIRE, STAMPLATE memberOf
Utilisé par : Site (observatory), TimeSeriesBundle (observatory)
Relations inverses (requêter par resourceType='Observatory') :
  HistoricalLocation, HistoricalProject, Responsibility,
  Identifier, Memory, KeywordAssignment
Note : entité racine du réseau.
       Correspond à un Thing STA avec properties enrichies (STAMPLATE).

| Champ                | Cardinalité    | Définition                              | Valeurs possibles                        |
|----------------------|----------------|-----------------------------------------|------------------------------------------|
| `id`                 | 1              | Identifiant technique, clé primaire     | uuid                                     |
| `code`               | 1              | Code court unique, curateur             | "yzr"                                    |
| `name`               | 1              | Nom du réseau                           | "Observatoire de l'Yzeron"               |
| `description`        | 0..1           | Description scientifique                |                                          |
| `location`           | 1 →Loc         | Emprise géographique courante           | → Location                               |
| `startDate`          | 1              | Date de début                           | "2010-01-01"                             |
| `endDate`            | 0..1           | Date de fin, null si actif              | null                                     |
| `status`             | 1              | État de l'observatoire                  | `active` \| `inactive` \| `discontinued` |
| `url`                | 0..1           | Site web du réseau                      | "https://..."                            |

---

### Site
> Subdivision géographique d'un observatoire (bassin versant, lac, aquifère...).
Aligné avec : STA Thing (properties), ISO 19115, INSPIRE
Utilisé par : Station (site)
Relations inverses (requêter par resourceType='Site') :
  HistoricalLocation, HistoricalProject, Responsibility,
  Identifier, Memory, KeywordAssignment
Note : subdivision géographique d'un Observatory.
       code unique par Observatory.
       Type via KeywordAssignment (keywordType='siteType') :
       valeurs courantes : watershed, lake, wetland, aquifer, catchment, estuary

| Champ                | Cardinalité    | Définition                                | Valeurs possibles                                                 |
|----------------------|----------------|-------------------------------------------|-------------------------------------------------------------------|
| `id`                 | 1              | Identifiant technique, clé primaire       | uuid                                                              |
| `code`               | 1              | Code court unique                         | "yzr-mer"                                                         |
| `name`               | 1              | Nom du site                               | "Bassin versant du Mercier"                                       |
| `description`        | 0..1           | Description libre                         |                                                                   |
| `observatory`        | 1 →Obs         | Observatoire parent                       | → Observatory                                                     |
| `location`           | 1 →Loc         | Géométrie courante                        | → Location                                                        |
| `area`               | 0..1           | Superficie en km²                         | "245.3"                                                           |

---

### Station
> Point de mesure physique sur le terrain -- le Thing STA.
Aligné avec : STA Thing, STAMPLATE ThingProperties, ODM2 SamplingFeatures (Site)
Utilisé par : TimeSerie (station), TransferFunction (station),
             TransformedTimeSerie (station), Deployment (station), Datastream (station)
Relations inverses (requêter par resourceType='Station') :
  HistoricalLocation, HistoricalProject, Responsibility,
  Identifier, Memory, KeywordAssignment, InstrumentUsage
Note : point de mesure physique -- le "Thing" STA.
       code unique par Site.
       Type via KeywordAssignment (keywordType='stationType') :
       valeurs courantes : streamgage, weatherstation, well, soilpit, lakestation, tidegage

| Champ                | Cardinalité    | Définition                              | Valeurs possibles                                                   |
|----------------------|----------------|-----------------------------------------|---------------------------------------------------------------------|
| `id`                 | 1              | Identifiant technique, clé primaire     | uuid                                                                |
| `code`               | 1              | Code court unique                       | "yzr-mer-d610"                                                      |
| `name`               | 1              | Nom de la station                       | "Mercier au pont D610"                                              |
| `description`        | 0..1           | Description libre                       |                                                                     |
| `site`               | 1 →Site        | Site parent                             | → Site                                                              |
| `location`           | 1 →Loc         | Position GPS courante                   | → Location                                                          |
| `elevation`          | 0..1           | Altitude en mètres (référentiel local)  | "312.5"                                                             |
| `installationDate`   | 0..1           | Date d'installation                     | "1997-01-14"                                                        |
| `status`             | 1              | État de la station                      | `active` \| `inactive` \| `discontinued`                            |

---

## 4bis. DONNÉES BRUTES (couche IoT STA 2.0)

### Datastream
> Flux de données brutes issu d'un capteur sur une station -- couche IoT STA.
Aligné avec : STA 1.1 Datastream, FROST-Server, HydroServer Datastream
Utilisé par : TimeSerieDatastream (datastream), Observation (datastream)
Note : flux de données brutes pour un unique Thing + Sensor + ObservedProperty.
       Un changement de capteur crée un nouveau Datastream (STA standard).
       Plusieurs Datastreams successifs → une TimeSerie via TimeSerieDatastream.
       BDOH garde unitOfMeasurement comme FK vers Unit (choix HydroServer/USGS)
       plutôt que le resultType SWE-Common de STA 2.0 draft -- plus simple
       et suffisant pour les données environnementales.

| Champ                  | Cardinalité | Définition                                | Valeurs possibles                                                  |
|------------------------|-------------|-------------------------------------------|--------------------------------------------------------------------|
| `id`                   | 1           | Identifiant technique, clé primaire       | uuid                                                               |
| `name`                 | 1           | Nom du flux                               | "Hauteur d'eau -- Mercier D610 -- OTT PLS 500"                     |
| `description`          | 0..1        | Description libre                         |                                                                    |
| `observationType`      | 1           | Type de résultat (URI OGC OM 2.0)         | "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement" |
| `unitOfMeasurement`    | 1 →Unit     | Unité de mesure                           | → Unit                                                             |
| `station`              | 1 →Sta      | Station source (= Thing STA)              | → Station                                                          |
| `sensor`               | 1 →Sen      | Capteur source                            | → Sensor                                                           |
| `property`             | 1 →Prop     | Variable mesurée (= ObservedProperty STA) | → Property                                                         |
| `procedure`            | 0..1 →Proc  | Protocole de mesure                       | → Procedure                                                        |
| `featureOfInterest`    | 0..1 →FOI   | Entité réelle observée par défaut         | → FeatureOfInterest                                                |
| `startTime`            | 0..1        | Début de la période couverte              | "2024-01-01T00:00:00Z"                                             |
| `endTime`              | 0..1        | Fin de la période couverte, null si actif | null                                                               |
| `status`               | 1           | État du flux                              | `active` \| `inactive` \| `closed`                                 |
| `license`              | 1 →Lic      | Licence des données                       | → License                                                          |
| `observationFrequency` | 0..1        | Fréquence de mesure (ISO 8601 duration)   | "PT15M" \| "PT1S" \| "P1D"                                         |
| `transmissionMode`     | 0..1        | Mode d'arrivée des données dans BDOH      | `auto` \| `manual`                                                 |

---

### ObservationBatch
> Import groupé de données brutes -- trace qui a déposé quel lot, quand et depuis quelle source.
Aligné avec : W3C PROV-O Activity, ODM2 Actions
Utilisé par : Observation (batch)
Note : optionnel -- un capteur télétransmis en continu ne crée pas de batch.
       Nécessaire quand un technicien importe manuellement des données
       récupérées sur une centrale d'acquisition terrain non connectée.
       Analogue à ValidationBatch pour la couche IoT.

| Champ         | Cardinalité | Définition                                 | Valeurs possibles                    |
|---------------|-------------|--------------------------------------------|--------------------------------------|
| `id`          | 1           | Identifiant technique, clé primaire        | uuid                                 |
| `datastream`  | 1 →DS       | Flux de données cible                      | → Datastream                         |
| `importedAt`  | 1           | Date et heure de l'import                  | "2024-04-01T08:00:00Z"               |
| `importedBy`  | 0..1 →Per   | Technicien ayant réalisé l'import          | → Person                             |
| `source`      | 0..1        | Origine des données (centrale, fichier...) | "centrale YZR-D610" \| "https://..." |
| `status`      | 1           | État de l'import                           | `pending` \| `done` \| `failed`      |
| `comment`     | 0..1        | Commentaire libre                          |                                      |

---

### Observation
> Valeur brute horodatée issue d'un Datastream -- non validée, non corrigée.
Aligné avec : STA 2.0 Observation, OGC OMS, FROST-Server
Utilisé par : Datastream (observations), ObservationBatch (datastream)
Note : valeur brute horodatée -- raw, sans qualityFlag, sans validation.
       La validation est dans ValidatedObservation du backend BDOH.
       Le lien se fait via phenomenonTime + datastream → TimeSerieDatastream.
       STA 2.0 : FeatureOfInterest devient ProximateFeatureOfInterest.
       BDOH garde featureOfInterest pour compatibilité STA 1.1/2.0.

| Champ               | Cardinalité | Définition                                       | Valeurs possibles                                          |
|---------------------|-------------|--------------------------------------------------|------------------------------------------------------------|
| `id`                | 1           | Identifiant technique, clé primaire              | uuid                                                       |
| `batch`             | 0..1 →OB    | Batch d'import parent si saisie manuelle         | → ObservationBatch                                         |
| `phenomenonTime`    | 1           | Instant ou période du phénomène (STA standard)   | "2024-03-15T09:30:00Z" \| "2024-03-15T09:00:00Z/09:30:00Z" |
| `resultTime`        | 1           | Instant d'enregistrement du résultat             | "2024-03-15T09:30:05Z"                                     |
| `result`            | 1           | Valeur brute mesurée                             | 4.523                                                      |
| `datastream`        | 1 →DS       | Flux de données parent                           | → Datastream                                               |
| `featureOfInterest` | 0..1 →FOI   | Entité observée si différente du Datastream      | → FeatureOfInterest                                        |
| `samplingFeature`   | 0..1 →SF    | Prélèvement terrain associé                      | → SamplingFeature                                          |

---

## 5. PROJET

### Project
> Projet ou campagne ayant financé ou porté une ressource.
Aligné avec : schema.org/ResearchProject, STAplus Campaign,
             DataCite relatedIdentifier, STAMPLATE memberOf
Utilisé par : HistoricalProject (project), SamplingFeature (project)
Relations inverses (requêter par resourceType='Project') :
  Responsibility, Identifier, Memory
Note : projet structurant ou campagne de mesure -- même objet.
       Lien vers Observatory/Site/Station/TimeSerie via HistoricalProject.

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

---

### HistoricalProject
> Lien temporalisé entre un projet et une ressource -- plusieurs projets actifs simultanément possibles.
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

### InstrumentUsage
> Lien temporalisé entre une ressource et un instrument -- trace l'utilisation des capteurs et équipements dans le temps.
Aligné avec : ODM2 Equipment (usage), W3C PROV-O wasAssociatedWith
Utilisé par : Station, TimeSerie, Deployment, SamplingFeature
             (via resourceType + resourceId)
Note : table polymorphique temporalisée -- analogue à HistoricalProject pour les instruments.
       Remplace tous les liens directs Sensor/Equipment sur les entités parentes.
       Porte le contexte d'utilisation (profondeur, période) qui n'appartient pas
       à l'instrument lui-même mais à son usage sur une ressource donnée.
       TimeSerie garde sensor 1 comme snapshot courant pour accès rapide --
       l'historique complet des capteurs est ici.

| Champ            | Cardinalité | Définition                                  | Valeurs possibles                                              |
|------------------|-------------|---------------------------------------------|----------------------------------------------------------------|
| `id`             | 1           | Identifiant technique, clé primaire         | uuid                                                           |
| `resourceType`   | 1           | Type de ressource ciblée                    | `Station` \| `TimeSerie` \| `Deployment` \| `SamplingFeature`  |
| `resourceId`     | 1           | UUID de la ressource ciblée                 | uuid                                                           |
| `instrumentType` | 1           | Type d'instrument                           | `sensor` \| `equipment`                                        |
| `instrumentId`   | 1           | UUID du Sensor ou Equipment                 | uuid                                                           |
| `deploymentDepth`| 0..1        | Profondeur de l'instrument sur la ressource | "-1.5"                                                         |
| `depthReference` | 0..1        | Référence de profondeur                     | `surfaceRelative` \| `bottomRelative` \| `absoluteElevation`   |
| `validFrom`      | 0..1        | Début de la période d'utilisation           | "2020-06-01T00:00:00Z"                                         |
| `validTo`        | 0..1        | Fin de la période, null si actif            | null                                                           |

---

### Deployment
> Plateforme multi-capteurs co-localisés (ligne de sondes, bouée, sonde multi-paramètres...).
Aligné avec : STAMPLATE Platform, STA 2.0 Deployment (draft), SensorML DeploymentProperty
Utilisé par : InstrumentUsage (resourceType=Deployment)
Relations inverses (requêter par resourceType='Deployment') :
  InstrumentUsage, Memory, Identifier
Note : plateforme physique regroupant plusieurs capteurs et équipements.
       Instruments et profondeurs tracés via InstrumentUsage.
       STA 2.0 introduit une entité Deployment dans son draft (issue #167).
       Type via KeywordAssignment (keywordType='deploymentType') :
       valeurs courantes : verticalChain, buoy, weatherStation, multiProbe

| Champ             | Cardinalité | Définition                                     | Valeurs possibles                                                  |
|-------------------|-------------|------------------------------------------------|--------------------------------------------------------------------|
| `id`              | 1           | Identifiant technique, clé primaire            | uuid                                                               |
| `code`            | 1           | Code court unique                              | "dep-ret-yzr-01"                                                   |
| `name`            | 1           | Nom du déploiement                             | "Ligne de capteurs retenue Yzeron"                                 |
| `description`     | 0..1        | Description libre                              |                                                                    |
| `station`         | 1 →Sta      | Station de rattachement                        | → Station                                                          |
| `deploymentDepth` | 0..1        | Profondeur de référence globale                | "-2.0"                                                             |
| `depthReference`  | 0..1        | Référence de profondeur                        | `surfaceRelative` \| `bottomRelative` \| `absoluteElevation`       |
| `installDate`     | 0..1        | Date d'installation                            | "2020-06-01"                                                       |
| `removeDate`      | 0..1        | Date de retrait, null si actif                 | null                                                               |
| `status`          | 1           | État du déploiement                            | `active` \| `inactive` \| `removed`                                |
| `location`        | 0..1 →Loc   | Position si différente de la Station           | → Location                                                         |

---

### Sensor
> Instrument de mesure physique (ICP-MS, sonde de température, débitmètre...).
Aligné avec : STA Sensor, STAMPLATE SensorProperties, ODM2 Equipment,
             Helmholtz SMS instrument metadata
Utilisé par : TimeSerie (sensor -- snapshot courant), ControlObservation (sensor),
             Datastream (sensor), InstrumentUsage (instrumentType=sensor)
Relations inverses (requêter par resourceType='Sensor') :
  Responsibility, Identifier, Memory
Note : instrument de mesure indépendant de tout contexte d'utilisation.
       Type via KeywordAssignment (keywordType='sensorType') :
       valeurs courantes : icp_ms, spectrophotometer, hplc, probe, autoanalyzer, datalogger
       Le labo, le déploiement, la profondeur sont portés par InstrumentUsage
       qui trace l'utilisation de ce capteur sur une ressource dans le temps.
       TimeSerie.sensor est un snapshot courant pour accès rapide -- l'historique
       complet est dans InstrumentUsage.
       code unique globalement -- suggestion depuis serialNumber à la création,
       ou depuis make + model si serialNumber absent.

| Champ                    | Cardinalité | Définition                                  | Valeurs possibles                                             |
|--------------------------|-------------|---------------------------------------------|---------------------------------------------------------------|
| `id`                     | 1           | Identifiant technique, clé primaire         | uuid                                                          |
| `code`                   | 1           | Slug unique globalement                     | "thermo-icap-rq-sn2023-00412"                                 |
| `name`                   | 1           | Nom de l'instrument                         | "ICP-MS Thermo iCAP RQ"                                       |
| `make`                   | 1           | Fabricant                                   | "Thermo Fisher"                                               |
| `model`                  | 1           | Modèle                                      | "iCAP RQ"                                                     |
| `serialNumber`           | 0..1        | Numéro de série fabricant (valeur brute)    | "SN-2023/00412 Rev.B"                                         |
| `calibrationDate`        | 0..1        | Date de dernière calibration                | "2024-01-15"                                                  |
| `calibrationCertificate` | 0..1        | Référence ou URI du certificat              | "CERT-2024-ICP-001"                                           |
| `encodingType`           | 1           | Type d'encodage (conformité STA)            | "application/pdf" \| URI                                      |
| `metadata`               | 0..1        | URI vers la fiche technique                 | "https://..."                                                 |

---

### Equipment
> Matériel terrain non électronique (flacon, pompe, préleveur automatique...).
Aligné avec : ODM2 Equipment, STAMPLATE Platform (matériel terrain)
Utilisé par : SamplingFeature (equipment),
             InstrumentUsage (instrumentType=equipment)
Relations inverses (requêter par resourceType='Equipment') :
  Responsibility, Identifier
Note : matériel de collecte terrain ou équipement fixe installé à poste.
       Distinct de Sensor (instrument de mesure électronique).
       Type via KeywordAssignment (keywordType='equipmentType') :
       valeurs courantes : bottle, pump, autosampler, corer, syringe, filterHolder, datalogger, sensor_probe
       code unique globalement -- suggestion depuis serialNumber à la création,
       ou depuis name si serialNumber absent.

| Champ                | Cardinalité | Définition                           | Valeurs possibles                                               |
|----------------------|-------------|--------------------------------------|-----------------------------------------------------------------|
| `id`                 | 1           | Identifiant technique, clé primaire  | uuid                                                            |
| `code`               | 1           | Slug unique globalement              | "flacon-hdpe-1l-sn-eq-00231"                                    |
| `name`               | 1           | Nom descriptif                       | "Flacon HDPE 1L bouchon bleu"                                   |
| `material`           | 0..1        | Matériau de construction             | "HDPE" \| "verre ambré" \| "inox"                               |
| `volume`             | 0..1        | Contenance ou volume en litres       | "1.0"                                                           |
| `preservationMethod` | 0..1        | Méthode de conservation              | "acidification HNO3" \| "congélation" \| "obscurité"            |
| `manufacturer`       | 0..1        | Fabricant                            | "Nalgene"                                                       |
| `serialNumber`       | 0..1        | Numéro de série fabricant (brut)     | "SN-EQ-00231"                                                   |

---

## 7. OBSERVATION

### FeatureOfInterest
> Entité réelle du monde observée -- la rivière, la nappe, le sol, l'atmosphère.
Aligné avec : STA FeatureOfInterest, OGC OMS domainFeature, ISO 19156
Utilisé par : ValidatedObservation (featureOfInterest),
             ControlObservation (featureOfInterest), Datastream (featureOfInterest),
             Observation (featureOfInterest)
Relations inverses : Identifier
Note : entité réelle du monde observée -- cours d'eau, nappe, sol, atmosphère.
       Distincte de SamplingFeature (acte de prélèvement) -- la distinction
       couvre les mêmes cas que Proximate/UltimateFOI de OMS sans l'adopter.
       Convention code : {nom-court-entité}-{type} ex: "mercier-eau-surf"
       Type via KeywordAssignment (keywordType='featureType') :
       valeurs courantes : river, lake, groundwater, soil, atmosphere, wetland

| Champ          | Cardinalité | Définition                           | Valeurs possibles                                                         |
|----------------|-------------|--------------------------------------|---------------------------------------------------------------------------|
| `id`           | 1           | Identifiant technique, clé primaire  | uuid                                                                      |
| `code`         | 1           | Code court unique, curateur          | "mercier-eau-surf" \| "yzeron-bv"                                         |
| `name`         | 1           | Nom de l'entité observée             | "Eau de surface du Mercier"                                               |
| `description`  | 0..1        | Description libre                    |                                                                           |
| `encodingType` | 1           | Type d'encodage (conformité STA)     | "application/geo+json"                                                    |
| `geometry`     | 1           | Emprise GeoJSON de l'entité          | `Point` \| `Polygon` \| `LineString`                                      |

---

### TimeSerieDatastream
> Lien temporalisé entre une TimeSerie et ses Datastream sources successifs -- trace les changements de capteur.
Aligné avec : ODM2 Datasets, HydroServer (liaison Datastream→TimeSerie)
Utilisé par : TimeSerie via timeSerie FK (relation directe)
Note : lie une TimeSerie à ses Datastreams sources successifs dans le temps.
       Constitue l'historique complet des changements de capteur et de flux.
       Un changement de capteur = nouveau Datastream = nouvelle ligne ici.

| Champ       | Cardinalité | Définition                          | Valeurs possibles      |
|-------------|-------------|-------------------------------------|------------------------|
| `id`        | 1           | Identifiant technique, clé primaire | uuid                   |
| `timeSerie` | 1 →TS       | Série parente                       | → TimeSerie            |
| `datastream`| 1 →DS       | Datastream source                   | → Datastream           |
| `validFrom` | 1           | Début de la période                 | "1997-01-14T00:00:00Z" |
| `validTo`   | 0..1        | Fin de la période, null si courant  | null                   |

---

### TimeSerie
> Contrat analytique d'une série -- variable, capteur et protocole fixes pour toute la durée.
Utilisé par : ValidatedObservation (timeSerie), ControlObservation (timeSerie),
             TransformationBatch via transformationbatch_inputseries,
             TimeSerieDatastream (timeSerie), HistoricalProject (resourceType=TimeSerie)
Relations inverses (requêter par resourceType='TimeSerie') :
  HistoricalProject, Responsibility, Identifier, Memory, KeywordAssignment, InstrumentUsage
Note : porte tout ce qui est fixe et commun à toute la série.
       Contrat analytique garantissant la comparabilité de tous les points.
       Une procédure de validation unique par série -- plusieurs validations
       parallèles sur la même variable impliquent des TimeSerie distinctes.
       Plusieurs TimeSerie peuvent coexister sur la même station et la même
       variable sans hiérarchie -- c'est le contexte scientifique qui désigne
       laquelle utiliser.
       OZCAR note que leur "Observation" pivot correspond à un Datastream STA.
       code unique par Station.
       Keywords attendus via KeywordAssignment (voir KeywordRequirement) :
         samplingMedium (required) -- ex: surfaceWater, groundwater, atmosphere

| Champ                   | Cardinalité    | Définition                                    | Valeurs possibles                                          |
|-------------------------|----------------|-----------------------------------------------|------------------------------------------------------------|
| `id`                    | 1              | Identifiant technique, clé primaire           | uuid                                                       |
| `code`                  | 1              | Slug unique par Station                       | "hea-wiski"                                                |
| `name`                  | 1              | Nom lisible de la série                       | "Hauteur d'eau -- Mercier au pont D610"                    |
| `description`           | 0..1           | Description libre                             |                                                            |
| `station`               | 1 →Sta         | Station de rattachement                       | → Station                                                  |
| `sensor`                | 1 →Sen         | Instrument actif (snapshot courant)           | → Sensor                                                   |
| `property`              | 1 →Prop        | Variable mesurée                              | → Property                                                 |
| `unit`                  | 1 →Unit        | Unité de mesure                               | → Unit                                                     |
| `procedure.observation` | 1 →Proc        | Protocole analytique fixe pour toute la série | → Procedure (type=observation)                             |
| `procedure.validation`  | 1 →Proc        | Procédure de validation de cette série        | → Procedure (type=validation)                              |
| `observationType`       | 1              | Mode d'acquisition                            | `sensor_continuous` \| `lab_sample`                        |
| `startDate`             | 1              | Date de début de la série                     | "1997-01-14T08:01:00Z"                                     |
| `endDate`               | 0..1           | Date de fin, null si active                   | null                                                       |
| `status`                | 1              | État de la série                              | `active` \| `inactive` \| `discontinued`                   |
| `license`               | 1 →Lic         | Licence des données                           | → License                                                  |
| `validationFrequency`   | 0..1           | Fréquence de validation auto (ISO 8601)       | "PT15M" \| "P1D" \| "P1W"                                  |
| `validationMode`        | 0..1           | Mode de validation                            | `auto` \| `manual`                                         |

---

### Vocabulaire qualityFlag
Aligné avec : ODM2 ResultQualifiers, SANDRE codes qualité, STA resultQuality OGC

| BDOH      | ODM2    | SANDRE           | OGC resultQuality |
|-----------|---------|-------------------|-------------------|
| `good`    | Good    | 1 -- Bonne        | `good`            |
| `suspect` | Suspect | 3 -- Douteuse     | `suspect`         |
| `bad`     | Bad     | 4 -- Mauvaise     | `invalid`         |
| `missing` | Missing | -- (lacune)       | `missing`         |

---

### ValidationBatch
> Session de validation groupée -- qui a validé, quand, sur quelle période.
Aligné avec : ODM2 Actions (validation), W3C PROV-O Activity
Utilisé par : ValidatedObservation (validationBatch)
Note : groupe d'observations validées en une même session.
       Un batch couvre une fenêtre temporelle sur une TimeSerie.
       Alléger ValidatedObservation -- les métadonnées de session
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
| `status`           | 1           | État du batch                           | `pending` \| `validated` \| `rejected`   |
| `comment`          | 0..1        | Commentaire libre sur la session        | "Validation Q1 2024 après crue janvier"  |

---

### ValidatedObservation
> Valeur validée par un opérateur ou un pipeline qualité -- avec indicateur qualité.
Aligné avec : STA Observation (enrichie), ODM2 Result + DataQuality,
             Helmholtz SMS observation metadata, HydroServer ProcessingLevel
Utilisé par : TimeSerie (observations)
Note : point de mesure validé par opérateur humain ou pipeline automatique.
       Lien vers données brutes : TimeSerie → TimeSerieDatastream + phenomenonTime.
       Métadonnées de session (validatedBy, validatedAt, log) portées par ValidationBatch.
       La procédure de validation est portée par la TimeSerie parente.
       validationBatch 0..1 -- une observation peut être validée hors batch.

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
> Mesure ponctuelle de vérification -- valeur obtenue par une méthode indépendante et comparée à la série continue pour détecter une dérive ou une erreur.
Aligné avec : ODM2 ResultQualifier, OGC OMS
Utilisé par : TimeSerie (controlObservations)
Note : se greffe directement sur une TimeSerie sans Datastream dédié.
       Le capteur et la procédure diffèrent intentionnellement de ceux de la
       TimeSerie parente -- c'est une mesure indépendante pour vérifier la cohérence.
       Ex : jaugeage de vérification sur une série de hauteur d'eau,
            mesure avec un capteur étalonné de référence,
            comparaison avec une station voisine.
       Type via KeywordAssignment (keywordType='controlType') :
       valeurs courantes : independent_measure, cross_validation, reference_gauge

| Champ                   | Cardinalité | Définition                                | Valeurs possibles                                               |
|-------------------------|-------------|-------------------------------------------|-----------------------------------------------------------------|
| `id`                    | 1           | Identifiant technique, clé primaire       | uuid                                                            |
| `timeSerie`             | 1 →TS       | Série parente                             | → TimeSerie                                                     |
| `phenomenonTime`        | 1           | Instant ou période du phénomène (STA)     | "2024-03-15T09:30:00Z"                                          |
| `resultTime`            | 0..1        | Instant où le résultat a été produit      | "2024-03-15T09:35:00Z"                                          |
| `result`                | 1           | Valeur mesurée                            | "0.02"                                                          |
| `expectedResult`        | 0..1        | Valeur attendue selon la série            | "0.021"                                                         |
| `qualityFlag`           | 1           | Résultat du contrôle                      | `pass` \| `warn` \| `fail`                                      |
| `qualityComment`        | 0..1        | Justification libre du flag qualité       | "écart de 5% -- dérive capteur probable"                        |
| `sensor`                | 0..1 →Sen   | Capteur utilisé pour le contrôle          | → Sensor                                                        |
| `procedure.observation` | 1 →Proc     | Protocole de mesure appliqué              | → Procedure (type=observation)                                  |
| `samplingFeature`       | 0..1 →SF    | Prélèvement terrain associé               | → SamplingFeature                                               |
| `featureOfInterest`     | 0..1 →FOI   | Entité réelle observée                    | → FeatureOfInterest                                             |

---

### SamplingFeature
> Acte de prélèvement terrain daté et localisé -- distinct de la FeatureOfInterest observée.
Aligné avec : STA FeatureOfInterest (specimen), ODM2 Specimen,
             OGC OMS SF_Specimen, ISO 19156
Utilisé par : ValidatedObservation (samplingFeature),
             ControlObservation (samplingFeature), Observation (samplingFeature)
Note : acte de prélèvement terrain. Présent pour les séries de type lab_sample.
       La chaîne analytique interne au laboratoire est hors modèle -- lien via limsReference.
       Présent aussi dans la couche IoT pour l'enregistrement terrain immédiat.
       Keywords attendus via KeywordAssignment (voir KeywordRequirement) :
         specimenType (required) -- ex: water, soil, sediment, biological
         samplingMedium (required) -- ex: surfaceWater, groundwater, depth

| Champ                 | Cardinalité | Définition                                         | Valeurs possibles                                         |
|-----------------------|-------------|----------------------------------------------------|-----------------------------------------------------------|
| `id`                  | 1           | Identifiant technique, clé primaire                | uuid                                                      |
| `datetime`            | 1           | Horodatage du prélèvement                          | "2024-03-15T09:30:00Z"                                    |
| `project`             | 0..1 →Proj  | Projet ou campagne dont dépend ce prélèvement      | → Project                                                 |
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

---

## 8. TRANSFORMATION

### TransferFunction
> Fonction de conversion liée à une station -- courbe de tarage, relation turbidité/MES...
Aligné avec : ODM2 Methods, WMO rating curve standards
Utilisé par : TransferFunctionSet (transferFunction), TransferFunctionBatch (transferFunction),
             TransferFunctionPoint (function)
Relations inverses (requêter par resourceType='TransferFunction') :
  Responsibility, Identifier, Memory
Note : fonction de conversion liée à une station -- analogue à TimeSerie.
       Les points de calibration (couples x/y) définissent la fonction empiriquement.
       code unique par Station.

| Champ            | Cardinalité    | Définition                             | Valeurs possibles                                            |
|------------------|----------------|----------------------------------------|--------------------------------------------------------------|
| `id`             | 1              | Identifiant technique, clé primaire    | uuid                                                         |
| `code`           | 1              | Slug unique par Station                | "hea-qmj-v3"                                                 |
| `name`           | 1              | Nom de la fonction                     | "Courbe de tarage Mercier D610 v3"                           |
| `description`    | 0..1           | Description libre                      |                                                              |
| `station`        | 1 →Sta         | Station associée                       | → Station                                                    |
| `inputProperty`  | 1 →Prop        | Variable en entrée                     | → Property (ex: hauteur)                                     |
| `outputProperty` | 1 →Prop        | Variable en sortie                     | → Property (ex: débit)                                       |
| `parameters`     | 0..1           | Coefficients analytiques (JSON)        | {"a":2.1,"b":1.5}                                            |
| `procedure`      | 0..1 →Proc     | Méthode de construction de la fonction | → Procedure (type=modeling)                                  |
| `startDate`      | 1              | Date de début de validité              | "2024-01-01T00:00:00Z"                                       |
| `endDate`        | 0..1           | Date de fin, null si active            | null                                                         |
| `status`         | 1              | État de la fonction                    | `active` \| `inactive` \| `deprecated`                       |

---

### TransferFunctionPoint
> Couple (x, y) de calibration issu d'un jaugeage terrain -- définit empiriquement la courbe.
Utilisé par : TransferFunction (via function FK -- relation inverse)
Note : couple de valeurs (x/y) définissant empiriquement la fonction.
       Analogue à ValidatedObservation -- c'est là que vivent les données.
       Ex : (hauteur=1.23m, débit=4.5m³/s) pour une courbe de tarage.
       Ex : (turbidité=120NTU, MES=245mg/L) pour une relation turbidité/MES.

| Champ      | Cardinalité | Définition                          | Valeurs possibles      |
|------------|-------------|-------------------------------------|------------------------|
| `id`       | 1           | Identifiant technique, clé primaire | uuid                   |
| `function` | 1 →TF       | Fonction parente                    | → TransferFunction     |
| `batch`    | 0..1 →TFB   | Batch de construction parent        | → TransferFunctionBatch|
| `x`        | 1           | Valeur en entrée                    | 1.23                   |
| `y`        | 1           | Valeur en sortie                    | 4.5                    |
| `uncertainty` | 0..1     | Incertitude sur la mesure           | 0.05                   |
| `datetime` | 0..1        | Date du jaugeage ou de la mesure    | "2024-03-15T09:30:00Z" |
| `comment`  | 0..1        | Commentaire libre                   | "jaugeage crue"        |

---

### TransferFunctionBatch
> Acte de construction d'une TransferFunction -- qui a construit la courbe, quand, avec quel outil.
Aligné avec : ODM2 Actions, W3C PROV-O wasGeneratedBy
Utilisé par : TransferFunctionPoint (batch)
Note : acte de construction d'une TransferFunction -- qui, quand, depuis quel outil.
       Analogue à ValidationBatch et TransformationBatch.
       La procédure est portée par TransferFunction parente, pas répétée ici.

| Champ               | Cardinalité | Définition                          | Valeurs possibles               |
|---------------------|-------------|-------------------------------------|---------------------------------|
| `id`                | 1           | Identifiant technique, clé primaire | uuid                            |
| `transferFunction`  | 1 →TF       | Fonction construite                 | → TransferFunction              |
| `builtAt`           | 1           | Date de construction                | "2024-04-01T08:00:00Z"          |
| `builtBy`           | 0..1 →Per   | Personne ayant construit la courbe  | → Person                        |
| `logUrl`            | 0..1        | Référence externe (export BaRatin..)| "https://..."                   |
| `status`            | 1           | État du batch                       | `pending` \| `done` \| `failed` |
| `comment`           | 0..1        | Commentaire libre                   |                                 |

---

### TransferFunctionSet
> Jeu de transformation applicable sur une période -- référence une TransferFunction et son type.
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
| `type`             | 1           | Type de transformation              | `function` \| `identity` \| `manual`   |
| `validFrom`        | 1           | Début de validité                   | "2024-01-01T00:00:00Z"                 |
| `validTo`          | 0..1        | Fin de validité, null si courant    | null                                   |
| `comment`          | 0..1        | Justification du choix              | "nouveau jaugeage après crue"          |

Contrainte : si type=function -> transferFunction obligatoire.
             si type=identity ou manual -> transferFunction null.

---

### TransformationBatch
> Acte de calcul d'une série dérivée -- qui a lancé le calcul, quand, depuis quelles séries sources.
Aligné avec : ODM2 Actions (dérivation), W3C PROV-O wasGeneratedBy
Utilisé par : TransformedObservation (transformationBatch)
Note : acte de calcul sur une ou plusieurs TimeSerie sources.
       Analogue à ValidationBatch -- factorisation des métadonnées de calcul.
       Les points calculés sont dans TransformedObservation.
       inputSeries est une table de jointure explicite `transformationbatch_inputseries`
       (batch_id, timeserie_id) -- un batch peut prendre plusieurs séries en entrée.
       Point ouvert : cas sans TransferFunctionSet (transformation algorithmique pure)
       -- transferFunctionSet est actuellement obligatoire (1), à trancher en v2.

| Champ                  | Cardinalité | Définition                          | Valeurs possibles               |
|------------------------|-------------|-------------------------------------|---------------------------------|
| `id`                   | 1           | Identifiant technique, clé primaire | uuid                            |
| `transformedTimeSerie` | 1 →TTS      | Série produite                      | → TransformedTimeSerie          |
| `transferFunctionSet`  | 1 →TFS      | Jeu de fonctions appliqué           | → TransferFunctionSet           |
| `inputSeries`          | 1..* →TS    | Séries sources (table jointure)     | → TimeSerie[]                   |
| `appliedAt`            | 1           | Date d'exécution du calcul          | "2024-04-01T08:00:00Z"          |
| `appliedBy`            | 0..1 →Per   | Personne ayant lancé le calcul      | → Person                        |
| `validFrom`            | 1           | Début de la période calculée        | "2024-01-01T00:00:00Z"          |
| `validTo`              | 0..1        | Fin de la période calculée          | null                            |
| `status`               | 1           | État du batch                       | `pending` \| `done` \| `failed` |
| `comment`              | 0..1        | Commentaire libre                   |                                 |

---

### TransformedObservation
> Valeur calculée par un TransformationBatch -- analogue à ValidatedObservation.
Aligné avec : STA Observation (enrichie), ODM2 DerivedResults
Utilisé par : TransformedTimeSerie (observations)
Note : point calculé par un TransformationBatch.
       Analogue à ValidatedObservation -- c'est là que vivent les données calculées.

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
> Série dérivée d'une ou plusieurs TimeSerie via des fonctions de transfert -- analogue à TimeSerie.
Aligné avec : STA Datastream (enrichi), ODM2 DerivedResults,
             HydroServer Datastream (processingLevel=derived)
Utilisé par : TransformationBatch (transformedTimeSerie),
             TimeSeriesBundle via bundle_transformedtimeserie
Relations inverses (requêter par resourceType='TransformedTimeSerie') :
  Identifier, Memory, KeywordAssignment
Note : série dérivée d'une ou plusieurs TimeSerie via des TransformationBatch.
       Analogue à TimeSerie -- même structure de métadonnées.
       Plusieurs TransformedTimeSerie peuvent coexister sur la même station
       et la même variable sans hiérarchie -- c'est le contexte scientifique
       qui désigne laquelle utiliser (même principe que TimeSerie).
       code unique par Station.

| Champ                      | Cardinalité    | Définition                          | Valeurs possibles                               |
|----------------------------|----------------|-------------------------------------|-------------------------------------------------|
| `id`                       | 1              | Identifiant technique, clé primaire | uuid                                            |
| `code`                     | 1              | Slug unique par Station             | "debit-tarage-bdoh"                             |
| `name`                     | 1              | Nom de la série dérivée             | "Débit Mercier au pont D610"                    |
| `description`              | 0..1           | Description libre                   |                                                 |
| `station`                  | 1 →Sta         | Station de rattachement             | → Station                                       |
| `property`                 | 1 →Prop        | Variable produite                   | → Property                                      |
| `unit`                     | 1 →Unit        | Unité de la série dérivée           | → Unit                                          |
| `procedure.transformation` | 1 →Proc        | Procédure de transformation         | → Procedure (type=transformation)               |
| `startDate`                | 1              | Date de début de la série           | "2024-01-01T00:00:00Z"                          |
| `endDate`                  | 0..1           | Date de fin, null si active         | null                                            |
| `status`                   | 1              | État de la série                    | `active` \| `inactive` \| `discontinued`        |
| `license`                  | 1 →Lic         | Licence des données                 | → License                                       |


---

## 9. ORGANISATION

### TimeSeriesBundle
> Regroupement éditorial de séries pour la diffusion et le catalogage -- objet de publication.
Aligné avec : ODM2 Datasets, DataCite Dataset, DCAT Distribution
Utilisé par : bundle_timeserie (table jointure → TimeSerie),
             bundle_transformedtimeserie (table jointure → TransformedTimeSerie)
Relations inverses : KeywordAssignment
Note : regroupe des TimeSerie et TransformedTimeSerie pour la publication.
       Objet éditorial -- pas technique.
       Deux tables de jointure explicites (types fixes et fermés) :
         bundle_timeserie (bundle_id, timeserie_id)
         bundle_transformedtimeserie (bundle_id, transformedtimeserie_id)

| Champ               | Cardinalité | Définition                               | Valeurs possibles                 |
|---------------------|-------------|------------------------------------------|-----------------------------------|
| `id`                | 1           | Identifiant technique, clé primaire      | uuid                              |
| `name`              | 1           | Nom du bundle                            | "Qualité eau Saône 2024"          |
| `description`       | 0..1        | Description libre                        |                                   |
| `observatory`       | 1 →Obs      | Observatoire parent                      | → Observatory                     |
| `license`           | 1 →Lic      | Licence des données du bundle            | → License                         |

---

### Memory
> Note ou événement attaché à n'importe quelle ressource du modèle -- journal de bord.
Aligné avec : ODM2 Annotations, STAMPLATE schema.org/CreativeWork
Utilisé par : Observatory, Site, Station, Sensor, Equipment, TimeSerie,
             TransformedTimeSerie, Deployment, Project
             (via resourceType + resourceId)
Note : note contextuelle ou événement daté attaché à n'importe quelle ressource.
       Objet transversal de documentation du cycle de vie.
       Fichiers stockés en S3, référencés via mediaUrl.
       Type via KeywordAssignment (keywordType='memoryType') :
       valeurs courantes : note, event, document, photo, installation,
       hydraulic_change, maintenance, incident, calibration

| Champ          | Cardinalité | Définition                          | Valeurs possibles                                               |
|----------------|-------------|-------------------------------------|-----------------------------------------------------------------|
| `id`           | 1           | Identifiant technique, clé primaire | uuid                                                            |
| `resourceType` | 1           | Type de ressource ciblée            | `Observatory` \| `Site` \| `Station` \| `Sensor` \| `Equipment` \| `TimeSerie` \| `TransformedTimeSerie` \| `Deployment` \| `Project` \| `TransferFunction` |
| `resourceId`   | 1           | UUID de la ressource ciblée         | uuid                                                            |
| `datetime`     | 1           | Date de la note ou de l'événement   | "2014-04-17T00:00:00Z"                                          |
| `title`        | 0..1        | Titre court                         | "Modification contrôle hydraulique"                             |
| `content`      | 0..1        | Texte libre                         | "Installation d'une lame déversante"                            |
| `mediaUrl`     | 0..*        | Photos ou documents associés (S3)   | "https://storage.obs.fr/memories/2014-lame.jpg"                 |
| `author`       | 0..1 →Per   | Auteur de la note                   | → Person                                                        |