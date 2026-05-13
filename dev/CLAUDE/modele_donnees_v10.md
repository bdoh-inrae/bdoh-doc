# Modèle de données BDOH v10 -- Métadonnées des entités

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
```
Les tables de jointure explicites (Person.organization, Bundle.series,
TransformationBatch.inputSeries) deviennent des endpoints bidirectionnels.

### Cardinalités
- `1` = obligatoire -- `0..1` = optionnel -- `1..*` = un ou plus -- `0..*` = table de jointure explicite

### Patterns transversaux -- tables polymorphiques

Ces tables portent la FK vers la ressource cible via `resourceType + resourceId`.
Elles ne génèrent aucune colonne dans les tables cibles.

| Table               | Ce qu'elle stocke                        | Ressources supportées                                                              |
|---------------------|------------------------------------------|------------------------------------------------------------------------------------|
| `Identifier`        | PIDs vers référentiels externes          | toutes les entités navigables                                                      |
| `Memory`            | Notes, événements, photos                | Observatory, Site, Station, System, TimeSerie, TransformedTimeSerie, Deployment, Project, TransferFunction |
| `Responsibility`    | Rôles d'acteurs sur des ressources       | Observatory, Site, Station, System, TimeSerie, Project, TransferFunction           |
| `KeywordAssignment` | Mots-clés et classifications contrôlées  | toutes les entités (voir KeywordAssignment.resourceType)                           |
| `KeywordRequirement`| Règles de complétion minimale            | défini par resourceType + keywordType                                              |
| `HistoricalLocation`| Positions géographiques successives      | Observatory, Site, Station, Deployment                                             |
| `HistoricalProject` | Projets porteurs successifs              | Observatory, Site, Station, TimeSerie                                              |
| `bundle_serie`      | Séries et fonctions regroupées en bundle | TimeSerie, TransformedTimeSerie, TransferFunction, ControlObservation              |

### Pattern TPC agent (agentType + agentId)

Plusieurs tables tracent l'acteur d'un acte ou d'une responsabilité.
Cet acteur peut être un humain (Person), un agent automatisé (Machine) ou une organisation (Organization).
Le pattern TPC est appliqué : `agentType` discrimine le type, `agentId` porte l'UUID.
Aucune FK native PostgreSQL -- intégrité garantie par trigger BEFORE INSERT/UPDATE.
Voir integrity_checks.md pour les requêtes de vérification périodique.

| Champ       | Type   | Valeurs                                   |
|-------------|--------|-------------------------------------------|
| `agentType` | enum   | `person` \| `machine` \| `organization`   |
| `agentId`   | uuid   | uuid de Person, Machine ou Organization   |

Tables portant ce pattern :
- `Responsibility` (agentType + agentId, obligatoires) : `person | organization | machine`
- `ValidationBatch` (validatedBy) : `person | machine`
- `TransformationBatch` (appliedBy) : `person | machine`
- `ObservationBatch` (importedBy) : `person | machine`
- `TransferFunctionBatch` (builtBy) : `person | machine`
- `Memory` (author) : `person | machine`
- `Specimen` (operator) : `person | machine`

### Tables de jointure explicites

Ces tables encodent des relations many-to-many portées par l'entité "propriétaire".

| Table                              | Entre                              |
|------------------------------------|------------------------------------|
| `person_organization`              | Person ↔ Organization              |
| `transformationbatch_inputseries`  | TransformationBatch ↔ TimeSerie    |
| `specimen_deployment`              | Specimen ↔ Deployment              |

### Identifiants : UUID, code slug et permalink

**UUID** : clé primaire technique sur toutes les entités. Immuable, jamais exposé
dans les URLs courantes. Sert de permalink stable pour les citations scientifiques.

```
Permalink : /resources/{uuid}
```

**code** : slug lisible, obligatoire (`1`) sur toutes les entités. Modifiable par
l'utilisateur. Une suggestion automatique est proposée à la création depuis le `name`
(ou le `serialNumber` pour System). Le code est unique dans son scope
parent -- deux entités de scopes différents peuvent avoir le même code.

Scopes d'unicité :
```
Observatory          unique globalement
Organization         unique globalement
System               unique globalement
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
Couche IoT (STA 1.1)             Couche métier BDOH
──────────────────────           ──────────────────────────────────────────
System (sensor)       ←→ Sensor  TimeSerie (contrat analytique continu)
Datastream            ←→         HistoricalDatastream (couture temporelle)
Observation (raw)     ←→         ValidatedObservation (qualifiée)
Station = Thing STA   ←→         Station (institutionnelle, code SANDRE)
System (platform)                Platform logique → hiérarchie Deployment
System (equipment)               Matériel de collecte → Deployment ponctuel
Property = ObservedProperty      Property (enrichie, discipline, thème...)
```

---

## 1. ACTEURS

### Person
> Individu humain impliqué dans la production ou la gestion des données.
Aligné avec : ODM2 People, STAMPLATE schema.org/Person, ISO 19115, ORCID
Utilisé par : pattern TPC agent (agentType='person') sur ValidationBatch, TransformationBatch,
             ObservationBatch, TransferFunctionBatch, Memory, Specimen.
             Responsibility (person). person_organization (affiliation).
Relations inverses : aucune (Person est référencée via agentId ou FK directe)
Note : organization est une table de jointure explicite `person_organization` --
       affiliation institutionnelle, distinct de Responsibility (rôle fonctionnel).
       Une personne peut appartenir à plusieurs organisations simultanément.
       Contrainte CHECK PostgreSQL : firstName et lastName et email sont obligatoires.

| Champ         | Cardinalité | Définition                          | Valeurs possibles                         |
|---------------|-------------|-------------------------------------|-------------------------------------------|
| `id`          | 1           | Identifiant technique, clé primaire | uuid                                      |
| `firstName`   | 1           | Prénom                              | "Julie"                                   |
| `lastName`    | 1           | Nom de famille                      | "Dupont"                                  |
| `email`       | 1           | Adresse email professionnelle       | "julie.dupont@inrae.fr"                   |
| `orcid`       | 0..1        | Identifiant chercheur ORCID         | "0000-0001-1234-1234"                     |
| `affiliation` | 0..1        | Affiliation textuelle libre         | "INRAE, UR RiverLy, Villeurbanne, France" |

---

### Machine
> Agent automatisé impliqué dans la production ou le traitement des données.
Aligné avec : CodeMeta schema.org/SoftwareApplication, W3C PROV-O Agent,
             ISO/IEC 18670 SWHID, Software Heritage
Utilisé par : pattern TPC agent (agentType='machine') sur ValidationBatch, TransformationBatch,
             ObservationBatch, TransferFunctionBatch, Memory, Specimen.
Relations inverses : aucune (Machine est référencée via agentId)
Note : représente un pipeline de calcul, un service d'import automatique, un agent IA.
       swhid identifie le code source exact utilisé -- identifiant cryptographique
       immuable (ISO/IEC 18670), garantit la reproductibilité scientifique.
       doi identifie la publication du logiciel (Zenodo, HAL...).
       codeRepository pointe vers le dépôt vivant (GitHub, GitLab...).
       Les trois sont complémentaires et alignés avec CodeMeta.

| Champ            | Cardinalité | Définition                                    | Valeurs possibles                                     |
|------------------|-------------|-----------------------------------------------|-------------------------------------------------------|
| `id`             | 1           | Identifiant technique, clé primaire           | uuid                                                  |
| `name`           | 1           | Nom du service ou pipeline                    | "pipeline-validation-bdoh"                            |
| `version`        | 0..1        | Version sémantique du logiciel                | "2.1.0"                                               |
| `codeRepository` | 0..1        | URL du dépôt source (CodeMeta codeRepository) | "https://github.com/inrae/bdoh-pipeline"              |
| `swhid`          | 0..1        | Identifiant Software Heritage (ISO/IEC 18670) | "swh:1:rel:22ece559cc7cc2364edc5e5593d63ae8bd229f9f"  |
| `doi`            | 0..1        | DOI du logiciel si publié                     | "10.5281/zenodo.1234567"                              |

---

### Organization
> Structure porteuse (laboratoire, observatoire, agence...).
Aligné avec : ODM2 Organizations, STAMPLATE schema.org/Organization, ROR
Utilisé par : Person via person_organization (table jointure),
             Responsibility (organization), Project (fundingAgency)
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
> Rôle d'un acteur (personne, organisation ou agent machine) sur une ressource à un instant T.
Aligné avec : ISO 19115 CI_Responsibility + CI_RoleCode, ODM2 Affiliations,
             STAMPLATE schema.org/Role, W3C PROV-O wasAssociatedWith
Utilisé par : Observatory, Site, Station, TimeSerie, Project, TransferFunction
             (via resourceType + resourceId)
Note : lie un acteur à une ressource avec un rôle fonctionnel et une période de validité.
       Distinct de Person.organization (appartenance institutionnelle).
       Pattern TPC agent : agentType discrimine Person, Organization ou Machine.
       agentType + agentId obligatoires (1) -- on sait toujours qui porte la responsabilité.
       Machine légitime pour certains rôles : custodian (pipeline IA de curation),
       processor (service de traitement automatique), originator (capteur autonome).
       Liste des rôles alignée sur ISO 19115-1 complète.

| Champ          | Cardinalité | Définition                                 | Valeurs possibles                                                         |
|----------------|-------------|--------------------------------------------|---------------------------------------------------------------------------|
| `id`           | 1           | Identifiant technique, clé primaire        | uuid                                                                      |
| `agentType`    | 1           | Type d'acteur responsable                  | `person` \| `organization` \| `machine`                                   |
| `agentId`      | 1           | UUID de la Person, Organization ou Machine | uuid                                                                      |
| `role`         | 1           | Rôle fonctionnel CI_RoleCode ISO 19115-1   | `resourceProvider` \| `custodian` \| `owner` \| `user` \| `distributor` \| `originator` \| `pointOfContact` \| `principalInvestigator` \| `processor` \| `publisher` \| `author` \| `sponsor` \| `coAuthor` \| `collaborator` \| `editor` \| `mediator` \| `rightsHolder` \| `contributor` \| `funder` \| `stakeholder` |
| `resourceType` | 1           | Type de ressource ciblée                   | `Observatory` \| `Site` \| `Station` \| `TimeSerie` \| `Project` \| `TransferFunction` |
| `resourceId`   | 1           | UUID de la ressource ciblée                | uuid                                                                      |
| `validFrom`    | 0..1        | Début de responsabilité                    | "2022-01-01"                                                              |
| `validTo`      | 0..1        | Fin, null si toujours actif                | "2024-12-31" \| null                                                      |

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

| Champ        | Cardinalité | Définition                          | Valeurs possibles                          |
|--------------|-------------|-------------------------------------|--------------------------------------------|
| `id`         | 1           | Identifiant technique, clé primaire | uuid                                       |
| `code`       | 1           | Code court pour URLs (kebab-case)   | "mg-l" \| "m3-s" \| "degc"                 |
| `symbol`     | 1           | Symbole textuel affiché             | "mg/L" \| "m³/s" \| "°C"                   |
| `name`       | 1           | Nom complet de l'unité              | "milligram per litre"                      |
| `definition` | 1           | URI QUDT ou UCUM                    | "http://qudt.org/vocab/unit/MilliGM-PER-L" |

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
             TimeSeriesBundle, Property, Organization, System,
             Deployment, FeatureOfInterest, Specimen, ControlObservation,
             TransferFunction, Datastream (via resourceType + resourceId)
Note : permet d'attacher autant de keywords que nécessaire à une ressource.
       Couvre les classifications multi-valeurs (discipline, theme, samplingMedium...)
       et les tags éditoriaux libres pour les catalogues.
       Les règles de complétion minimale sont dans KeywordRequirement.

| Champ          | Cardinalité | Définition                          | Valeurs possibles                                                                |
|----------------|-------------|-------------------------------------|----------------------------------------------------------------------------------|
| `id`           | 1           | Identifiant technique, clé primaire | uuid                                                                             |
| `keyword`      | 1 →Keyw     | Keyword assigné                     | → Keyword                                                                        |
| `resourceType` | 1           | Type de ressource ciblée            | `Observatory` \| `Site` \| `Station` \| `TimeSerie` \| `TransformedTimeSerie` \| `TimeSeriesBundle` \| `Property` \| `Organization` \| `System` \| `Deployment` \| `FeatureOfInterest` \| `Specimen` \| `ControlObservation` \| `TransferFunction` \| `Datastream` |
| `resourceId`   | 1           | UUID de la ressource ciblée         | uuid                                                                             |

---

### KeywordRequirement
> Règle de complétion minimale -- définit quels keywords sont obligatoires ou recommandés sur un type de ressource.
Utilisé par : validation applicative à la sauvegarde
Note : géré par les administrateurs BDOH sans migration de schéma.
       Permet de définir des standards de métadonnées sans contrainte SQL rigide.
       Exemples : Property doit avoir au moins un keyword de type 'discipline',
                  TimeSerie doit avoir au moins un keyword de type 'samplingMedium'.

| Champ          | Cardinalité | Définition                              | Valeurs possibles                                                  |
|----------------|-------------|-----------------------------------------|--------------------------------------------------------------------|
| `id`           | 1           | Identifiant technique, clé primaire     | uuid                                                               |
| `resourceType` | 1           | Type de ressource concerné              | `Property` \| `TimeSerie` \| `Station` \| `Specimen` \| ... |
| `keywordType`  | 1 →KWT      | Type de keyword requis                  | → KeywordType                                                      |
| `cardinality`  | 1           | Niveau d'obligation                     | `required` \| `recommended`                                        |

---

### License
> Licence de diffusion des données.
Utilisé par : Datastream (license), TimeSerie (license),
             TransformedTimeSerie (license), TimeSeriesBundle (license)
Note : toute licence implique un niveau d'accès -- une licence CC-BY est ouverte,
       une licence contractuelle est fermée ou restreinte.
       Obligatoire sur tous les flux de données.
       Gérée par les administrateurs BDOH.

| Champ  | Cardinalité | Définition                          | Valeurs possibles                                |
|--------|-------------|-------------------------------------|--------------------------------------------------|
| `id`   | 1           | Identifiant technique, clé primaire | uuid                                             |
| `code` | 1           | Code court unique                   | "cc-by-4.0" \| "odbl-1.0" \| "proprietary-inrae" |
| `name` | 1           | Nom complet de la licence           | "Creative Commons Attribution 4.0"               |
| `url`  | 0..1        | URL vers le texte officiel          | "https://creativecommons.org/licenses/by/4.0/"   |

---

### Identifier
> Code externe vers un référentiel tiers (SANDRE, TheiaOZCAR, WIGOS...).
Aligné avec : ODM2 ExternalIdentifiers, schema.org identifier,
             INSPIRE ExternalObjectIdentifier
Utilisé par : Observatory, Site, Station, System, TimeSerie,
             Person, Organization, Specimen, Property, Project
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
| `resourceType` | 1           | Type de ressource ciblée                | `Observatory` \| `Site` \| `Station` \| `System` \| `TimeSerie` \| `Person` \| `Organization` \| `Specimen` \| `Property` \| `Project` \| `TransferFunction` |
| `resourceId`   | 1           | UUID de la ressource ciblée             | uuid                                                                         |

---

## 3. GÉOGRAPHIE

### Location
> Géométrie pure d'un objet (point GPS, polygone...) sans dimension temporelle.
Aligné avec : STA Location, OGC GeoJSON, ISO 19107
Utilisé par : HistoricalLocation (location), Observatory (location courante),
             Site (location courante), Station (location courante),
             Deployment (location), Specimen (location)
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

---

### FeatureOfInterest
> Entité réelle du monde observée -- la rivière, la nappe, le sol, l'atmosphère.
Aligné avec : STA FeatureOfInterest, OGC OMS domainFeature, ISO 19156
Utilisé par : ValidatedObservation (featureOfInterest),
             ControlObservation (featureOfInterest),
             Station (featureOfInterest -- FOI ultime),
             TimeSerie (featureOfInterest -- FOI proximate optionnelle),
             Specimen (foi -- FOI proximate du prélèvement)
Relations inverses : Identifier
Note : entité réelle du monde observée -- cours d'eau, nappe, sol, atmosphère.
       Distincte de Specimen (acte de prélèvement) -- la distinction
       couvre les mêmes cas que Proximate/UltimateFOI de OMS sans l'adopter.
       Convention code : {nom-court-entité}-{type} ex: "mercier-eau-surf"
       Type via KeywordAssignment (keywordType='featureType') :
       valeurs courantes : river, lake, groundwater, soil, atmosphere, wetland

| Champ          | Cardinalité | Définition                          | Valeurs possibles                    |
|----------------|-------------|-------------------------------------|--------------------------------------|
| `id`           | 1           | Identifiant technique, clé primaire | uuid                                 |
| `code`         | 1           | Code court unique, curateur         | "mercier-eau-surf" \| "yzeron-bv"    |
| `name`         | 1           | Nom de l'entité observée            | "Eau de surface du Mercier"          |
| `description`  | 0..1        | Description libre                   |                                      |
| `encodingType` | 1           | Type d'encodage (conformité STA)    | "application/geo+json"               |
| `geometry`     | 1           | Emprise GeoJSON de l'entité         | `Point` \| `Polygon` \| `LineString` |

---

## 4. MONDE PHYSIQUE

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

| Champ                | Cardinalité    | Définition                          | Valeurs possibles           |
|----------------------|----------------|-------------------------------------|-----------------------------|
| `id`                 | 1              | Identifiant technique, clé primaire | uuid                        |
| `code`               | 1              | Code court unique                   | "yzr-mer"                   |
| `name`               | 1              | Nom du site                         | "Bassin versant du Mercier" |
| `description`        | 0..1           | Description libre                   |                             |
| `observatory`        | 1 →Obs         | Observatoire parent                 | → Observatory               |
| `location`           | 1 →Loc         | Géométrie courante                  | → Location                  |
| `area`               | 0..1           | Superficie en km²                   | "245.3"                     |

---

### Station
> Point de mesure institutionnel -- ancrage administratif et géographique permanent avec code SANDRE.
Aligné avec : STA Thing, STAMPLATE ThingProperties, ODM2 Specimens (Site),
             SANDRE station hydrométrique, WMO station hydrologique
Utilisé par : TimeSerie (station), TransferFunction (station),
             TransformedTimeSerie (station), Datastream (station)
Relations inverses (requêter par resourceType='Station') :
  HistoricalLocation, HistoricalProject, Responsibility,
  Identifier, Memory, KeywordAssignment
  Deployment (anchorType='station', anchorId)
Note : objet institutionnel et géographique -- le "Thing" STA.
       Existe indépendamment de tout équipement actif.
       A un code SANDRE, une continuité historique sur 50 ans, des responsabilités.
       Les Systems physiques sont déployés sur elle via Deployment (récursif).
       Distinct de Site (bassin versant, zone géographique large).
       code unique par Site.
       Type via KeywordAssignment (keywordType='stationType') :
       valeurs courantes : streamgage, weatherstation, well, soilpit, lakestation, tidegage

| Champ                | Cardinalité    | Définition                             | Valeurs possibles                        |
|----------------------|----------------|----------------------------------------|------------------------------------------|
| `id`                 | 1              | Identifiant technique, clé primaire    | uuid                                     |
| `code`               | 1              | Code court unique                      | "yzr-mer-d610"                           |
| `name`               | 1              | Nom de la station                      | "Mercier au pont D610"                   |
| `description`        | 0..1           | Description libre                      |                                          |
| `site`               | 1 →Site        | Site parent                            | → Site                                   |
| `location`           | 1 →Loc         | Position GPS courante                  | → Location                               |
| `elevation`          | 0..1           | Altitude en mètres (référentiel local) | "312.5"                                  |
| `featureOfInterest`  | 0..1 →FOI      | FOI ultime -- entité réelle observée   | → FeatureOfInterest                      |
| `installationDate`   | 0..1           | Date d'installation                    | "1997-01-14"                             |
| `status`             | 1              | État de la station                     | `active` \| `inactive` \| `discontinued` |

---

```
Architecture instrumentation BDOH v9 -- System + Deployment récursif

Note API : l'API STA expose /Sensors comme vue filtrée
           System WHERE systemType='sensor'. Le client STA voit
           des Sensors conformes. BDOH stocke des Systems.

Cas station fixe avec capteur individuel :

  Station (ancrage institutionnel permanent, code SANDRE)
    └── Deployment [2020-...] anchorType='station'
          └── System "Centrale YZR" (systemType=platform)
                └── Deployment [2020-2022]
                      └── System "Sonde hauteur OTT v1" (systemType=sensor)
                            └── Datastream A
                                  └── HistoricalDatastream [2020-2022] → TimeSerie "Hauteur D610"
                └── Deployment [2022-...]
                      └── System "Sonde hauteur OTT v2" (systemType=sensor)
                            └── Datastream B
                                  └── HistoricalDatastream [2022-...] → TimeSerie "Hauteur D610"

Cas bouée de lac (Platform multi-capteurs) :

  Station (bord du lac)
    └── Deployment [2020-...] anchorType='station'
          └── System "Bouée lac nord" (systemType=platform)
                ├── Deployment [2020-...] deploymentDepth=-0.5m
                │     └── System "Sonde T YSI" (systemType=sensor)
                │           └── Datastream → HistoricalDatastream → TimeSerie "T lac 0.5m"
                └── Deployment [2020-...] deploymentDepth=-1.5m
                      └── System "Sonde O2 YSI" (systemType=sensor)
                            └── Datastream → HistoricalDatastream → TimeSerie "O2 lac 1.5m"

Cas drone (campagne mobile) :

  Site "Bassin versant Yzeron"
    └── Deployment [2024-05-10/12] anchorType='site'
          location propre via HistoricalLocation (trajectoire)
          └── System "Bateau drone Yzeron" (systemType=platform)
                └── Deployment [2024-05-10/12]
                      └── System "Sonde conductivité" (systemType=sensor)
                            └── Datastream → HistoricalDatastream → TimeSerie "Cond surface"
```

---

### System
> Objet physique traçable impliqué dans la production de données -- capteur, plateforme ou équipement.
Aligné avec : OGC CS API System, SOSA/SSN sosa:System, STA Sensor (vue filtrée),
             ODM2 Equipment, STAMPLATE SensorProperties, Helmholtz SMS
Utilisé par : Deployment (system), Datastream (system), ControlObservation (system)
Relations inverses (requêter par resourceType='System') :
  Memory, Responsibility, Identifier, KeywordAssignment
Note : entité physique unique avec identité propre, indépendante de son contexte de déploiement.
       systemType discrimine le rôle -- pattern TPC, même philosophie que agentType.
       Contraintes CHECK PostgreSQL par systemType :
         sensor    -- encodingType obligatoire
         equipment -- calibrationDate, encodingType, metadata non pertinents (null)
         platform  -- material, volume, preservationMethod non pertinents (null)
       API STA : /Sensors = vue System WHERE systemType='sensor'.
       Type fin via KeywordAssignment (keywordType='systemSubType') :
         sensor    : icp_ms, spectrophotometer, hplc, probe, autoanalyzer, datalogger
         platform  : buoy, verticalChain, drone, multiProbe, weatherStation, mooring
         equipment : bottle, pump, autosampler, corer, syringe, filterHolder
       code unique globalement.

| Champ                    | Cardinalité | Définition                               | Valeurs possibles                      |
|--------------------------|-------------|------------------------------------------|----------------------------------------|
| `id`                     | 1           | Identifiant technique, clé primaire      | uuid                                   |
| `code`                   | 1           | Slug unique globalement                  | "ott-pls500-sn2023-00412"              |
| `name`                   | 1           | Nom descriptif                           | "Sonde OTT PLS 500"                    |
| `systemType`             | 1           | Discriminant TPC                         | `sensor` \| `platform` \| `equipment`  |
| `make`                   | 0..1        | Fabricant                                | "OTT" \| "YSI" \| "Nalgene"           |
| `model`                  | 0..1        | Modèle                                   | "PLS 500"                              |
| `serialNumber`           | 0..1        | Numéro de série fabricant                | "SN-2023/00412 Rev.B"                  |
| `calibrationDate`        | 0..1        | Date dernière calibration (sensor)       | "2024-01-15"                           |
| `calibrationCertificate` | 0..1        | Référence certificat (sensor)            | "CERT-2024-ICP-001"                    |
| `encodingType`           | 0..1        | Type encodage STA (sensor obligatoire)   | "application/pdf" \| URI               |
| `metadata`               | 0..1        | URI fiche technique (sensor)             | "https://..."                          |
| `material`               | 0..1        | Matériau de construction (equipment)     | "HDPE" \| "verre ambré" \| "inox"      |
| `volume`                 | 0..1        | Contenance en litres (equipment)         | "1.0"                                  |
| `preservationMethod`     | 0..1        | Méthode de conservation (equipment)      | "acidification HNO3" \| "congélation"  |
| `status`                 | 1           | État de l'objet physique                 | `active` \| `inactive` \| `retired`    |

---

### Deployment
> Acte de déployer un System dans un contexte spatial et temporel -- récursif, universel.
Aligné avec : OGC CS API Deployment, SOSA/SSN, SensorML DeploymentProperty
Utilisé par : System (via deployment.system)
Relations inverses (requêter par resourceType='Deployment') :
  Memory, Identifier, HistoricalLocation
Note : trace toutes les relations physiques entre Systems, et entre Systems et leur ancrage.
       Récursif via parentDeployment -- un capteur déployé sur une bouée déployée sur une station
       forme une hiérarchie de Deployments imbriqués.
       anchorType + anchorId : pattern TPC, ancrage sur Station ou Site.
       Un Deployment sans anchorType est autonome (drone en mission libre) -- position
       propre via HistoricalLocation.
       deploymentDepth : profondeur nominale du System dans ce Deployment.
       La position réelle mesurée en continu est une TimeSerie dédiée (capteur de pression).
       Si le System est déplacé sur un autre ancrage, c'est un nouveau Deployment.

| Champ              | Cardinalité | Définition                                       | Valeurs possibles                                            |
|--------------------|-------------|--------------------------------------------------|--------------------------------------------------------------|
| `id`               | 1           | Identifiant technique, clé primaire              | uuid                                                         |
| `code`             | 1           | Slug unique globalement                          | "dep-lac-nord-bouee-2020"                                    |
| `name`             | 1           | Nom du déploiement                               | "Déploiement bouée lac nord 2020"                            |
| `system`           | 1 →Sys      | System déployé                                   | → System                                                     |
| `parentDeployment` | 0..1 →Dep   | Déploiement parent (récursif)                    | → Deployment                                                 |
| `anchorType`       | 0..1        | Type d'ancrage territorial (null si autonome)    | `station` \| `site`                                          |
| `anchorId`         | 0..1        | UUID de la Station ou du Site                    | uuid                                                         |
| `location`         | 0..1 →Loc   | Position propre si différente de l'ancre         | → Location                                                   |
| `deploymentDepth`  | 0..1        | Profondeur nominale du System dans ce Deployment | "-1.5"                                                       |
| `depthReference`   | 0..1        | Référence de profondeur                          | `surfaceRelative` \| `bottomRelative` \| `absoluteElevation` |
| `validFrom`        | 1           | Début du déploiement                             | "2020-06-01T00:00:00Z"                                       |
| `validTo`          | 0..1        | Fin, null si actif                               | null                                                         |
| `status`           | 1           | État du déploiement                              | `active` \| `inactive` \| `removed`                          |

---
## 5. MONDE IoT

### Datastream
> Flux de données brutes issu d'un unique System de type sensor sur une station -- couche IoT STA.
Aligné avec : STA 1.1 Datastream, FROST-Server, HydroServer Datastream
Utilisé par : HistoricalDatastream (datastream), Observation (datastream)
Note : flux de données brutes pour un unique Thing + System(sensor) + ObservedProperty.
       Un changement de capteur crée un nouveau Datastream (règle métrologique et STA).
       Plusieurs Datastreams successifs → une TimeSerie via HistoricalDatastream.
       BDOH garde unitOfMeasurement comme FK vers Unit (choix HydroServer/USGS).
       API STA : system → Sensor dans les réponses /Datastreams.
       FOI absente de la couche IoT -- portée par Station et TimeSerie (couche métier).
       L'API STA résout la FOI à la demande : TimeSerie.featureOfInterest
       si renseignée, sinon Station.featureOfInterest.

| Champ                  | Cardinalité | Définition                                | Valeurs possibles                                                      |
|------------------------|-------------|-------------------------------------------|------------------------------------------------------------------------|
| `id`                   | 1           | Identifiant technique, clé primaire       | uuid                                                                   |
| `name`                 | 1           | Nom du flux                               | "Hauteur d'eau -- Mercier D610 -- OTT PLS 500"                         |
| `description`          | 0..1        | Description libre                         |                                                                        |
| `observationType`      | 1           | Type de résultat (URI OGC OM 2.0)         | "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement" |
| `unitOfMeasurement`    | 1 →Unit     | Unité de mesure                           | → Unit                                                                 |
| `station`              | 1 →Sta      | Station source (= Thing STA)              | → Station                                                              |
| `system`               | 1 →Sys      | Capteur source (systemType=sensor)        | → System                                                               |
| `property`             | 1 →Prop     | Variable mesurée (= ObservedProperty STA) | → Property                                                             |
| `procedure`            | 0..1 →Proc  | Protocole de mesure                       | → Procedure                                                            |
| `startTime`            | 0..1        | Début de la période couverte              | "2024-01-01T00:00:00Z"                                                 |
| `endTime`              | 0..1        | Fin de la période couverte, null si actif | null                                                                   |
| `status`               | 1           | État du flux                              | `active` \| `inactive` \| `closed`                                     |
| `license`              | 1 →Lic      | Licence des données                       | → License                                                              |
| `observationFrequency` | 0..1        | Fréquence de mesure (ISO 8601 duration)   | "PT15M" \| "PT1S" \| "P1D"                                             |
| `transmissionMode`     | 0..1        | Mode d'arrivée des données dans BDOH      | `auto` \| `manual`                                                     |

---

### ObservationBatch
> Import groupé de données brutes -- trace qui a déposé quel lot, quand et depuis quelle source.
Aligné avec : W3C PROV-O Activity, ODM2 Actions
Utilisé par : Observation (batch)
Note : optionnel -- un capteur télétransmis en continu ne crée pas de batch.
       Nécessaire quand un technicien importe manuellement des données
       récupérées sur une centrale d'acquisition terrain non connectée.
       Analogue à ValidationBatch pour la couche IoT.
       agentType + agentId : pattern TPC -- peut être un technicien (person)
       ou un service d'import automatique (machine).

| Champ         | Cardinalité | Définition                                 | Valeurs possibles                    |
|---------------|-------------|--------------------------------------------|--------------------------------------|
| `id`          | 1           | Identifiant technique, clé primaire        | uuid                                 |
| `datastream`  | 1 →DS       | Flux de données cible                      | → Datastream                         |
| `importedAt`  | 1           | Date et heure de l'import                  | "2024-04-01T08:00:00Z"               |
| `agentType`   | 0..1        | Type d'agent ayant réalisé l'import        | `person` \| `machine`                |
| `agentId`     | 0..1        | UUID de la Person ou Machine               | uuid                                 |
| `source`      | 0..1        | Origine des données (centrale, fichier...) | "centrale YZR-D610" \| "https://..." |
| `status`      | 1           | État de l'import                           | `pending` \| `done` \| `failed`      |
| `comment`     | 0..1        | Commentaire libre                          |                                      |

---

### Observation
> Valeur brute horodatée issue d'un Datastream -- non validée, non corrigée.
Aligné avec : STA 1.1 Observation, OGC OMS, FROST-Server
Utilisé par : Datastream (observations), ObservationBatch (datastream)
Note : valeur brute horodatée -- raw, sans qualityFlag, sans validation.
       La validation est dans ValidatedObservation du backend BDOH.
       Le lien se fait via phenomenonTime + datastream → HistoricalDatastream.
       FOI absente -- portée par Station et TimeSerie (couche métier).
       L'API STA résout la FOI à la demande depuis la couche métier.

| Champ             | Cardinalité | Définition                                     | Valeurs possibles                                           |
|-------------------|-------------|------------------------------------------------|-------------------------------------------------------------|
| `id`              | 1           | Identifiant technique, clé primaire            | uuid                                                        |
| `batch`           | 0..1 →OB    | Batch d'import parent si saisie manuelle       | → ObservationBatch                                          |
| `phenomenonTime`  | 1           | Instant ou période du phénomène (STA standard) | "2024-03-15T09:30:00Z" \| "2024-03-15T09:00:00Z/09:30:00Z" |
| `resultTime`      | 1           | Instant d'enregistrement du résultat           | "2024-03-15T09:30:05Z"                                      |
| `result`          | 1           | Valeur brute mesurée                           | 4.523                                                       |
| `datastream`      | 1 →DS       | Flux de données parent                         | → Datastream                                                |
| `specimen` | 0..1 →Spec  | Prélèvement terrain associé                    | → Specimen                                           |

---

## 6. COUTURE

### HistoricalDatastream
> Lien temporel et spatial entre une TimeSerie et ses Datastreams successifs -- trace les changements de capteur et de position nominale.
Aligné avec : ODM2 Datasets, HydroServer (liaison Datastream→TimeSerie), OGC CS API
Utilisé par : TimeSerie (via timeSerie FK)
Note : lie une TimeSerie à ses Datastreams sources successifs dans le temps.
       Un changement de capteur = nouveau Datastream = nouvelle ligne ici.
       Couture entre le monde physique (System → Deployment → Datastream)
       et le monde analytique (TimeSerie → ValidatedObservation).
       La profondeur nominale du capteur est portée par le Deployment correspondant.
       Renommé depuis TimeSerieDatastream pour refléter son rôle réel.

| Champ        | Cardinalité | Définition                          | Valeurs possibles      |
|--------------|-------------|-------------------------------------|------------------------|
| `id`         | 1           | Identifiant technique, clé primaire | uuid                   |
| `timeSerie`  | 1 →TS       | Série parente                       | → TimeSerie            |
| `datastream` | 1 →DS       | Datastream source                   | → Datastream           |
| `validFrom`  | 1           | Début de la période                 | "1997-01-14T00:00:00Z" |
| `validTo`    | 0..1        | Fin de la période, null si courant  | null                   |

---

## 7. MONDE ANALYTIQUE

### TimeSerie
> Contrat analytique d'une série -- variable et protocole fixes pour toute la durée.
Utilisé par : ValidatedObservation (timeSerie), ControlObservation (timeSerie),
             TransformationBatch via transformationbatch_inputseries,
             HistoricalDatastream (timeSerie), HistoricalProject (resourceType=TimeSerie)
Relations inverses (requêter par resourceType='TimeSerie') :
  HistoricalProject, Responsibility, Identifier, Memory, KeywordAssignment
Note : porte tout ce qui est fixe et commun à toute la série.
       Contrat analytique garantissant la comparabilité de tous les points.
       Le capteur courant se retrouve via HistoricalDatastream WHERE validTo IS NULL.
       Le regroupement spatial avec d'autres séries co-localisées est via la hiérarchie
       Deployment -- un Deployment de platform regroupe les capteurs co-localisés.
       FOI : featureOfInterest porte la FOI proximate si elle diffère de celle de Station.
       Règle de résolution API STA : TimeSerie.featureOfInterest si renseignée,
       sinon Station.featureOfInterest.
       Une procédure de validation unique par série -- plusieurs validations
       parallèles sur la même variable impliquent des TimeSerie distinctes.
       Plusieurs TimeSerie peuvent coexister sur la même station et la même
       variable sans hiérarchie -- c'est le contexte scientifique qui désigne laquelle utiliser.
       OZCAR note que leur "Observation" pivot correspond à un Datastream STA.
       code unique par Station.
       Keywords attendus via KeywordAssignment (voir KeywordRequirement) :
         samplingMedium (required) -- ex: surfaceWater, groundwater, atmosphere

| Champ                   | Cardinalité | Définition                                    | Valeurs possibles                        |
|-------------------------|-------------|-----------------------------------------------|------------------------------------------|
| `id`                    | 1           | Identifiant technique, clé primaire           | uuid                                     |
| `code`                  | 1           | Slug unique par Station                       | "hea-wiski"                              |
| `name`                  | 1           | Nom lisible de la série                       | "Hauteur d'eau -- Mercier au pont D610"  |
| `description`           | 0..1        | Description libre                             |                                          |
| `station`               | 1 →Sta      | Station de rattachement                       | → Station                                |
| `featureOfInterest`     | 0..1 →FOI   | FOI proximate si différente de Station        | → FeatureOfInterest                      |
| `property`              | 1 →Prop     | Variable mesurée                              | → Property                               |
| `unit`                  | 1 →Unit     | Unité de mesure                               | → Unit                                   |
| `procedure.observation` | 1 →Proc     | Protocole analytique fixe pour toute la série | → Procedure (type=observation)           |
| `procedure.validation`  | 1 →Proc     | Procédure de validation de cette série        | → Procedure (type=validation)            |
| `observationType`       | 1           | Mode d'acquisition                            | `sensor_continuous` \| `lab_sample`      |
| `startDate`             | 1           | Date de début de la série                     | "1997-01-14T08:01:00Z"                   |
| `endDate`               | 0..1        | Date de fin, null si active                   | null                                     |
| `status`                | 1           | État de la série                              | `active` \| `inactive` \| `discontinued` |
| `license`               | 1 →Lic      | Licence des données                           | → License                                |
| `validationFrequency`   | 0..1        | Fréquence de validation auto (ISO 8601)       | "PT15M" \| "P1D" \| "P1W"               |
| `validationMode`        | 0..1        | Mode de validation                            | `auto` \| `manual`                       |

---

### Vocabulaire qualityFlag
Aligné avec : ODM2 ResultQualifiers, SANDRE codes qualité, STA resultQuality OGC

| BDOH      | ODM2    | SANDRE            | OGC resultQuality |
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
       agentType + agentId obligatoires (1) : pattern TPC -- peut être un
       opérateur humain (person) ou un pipeline de validation automatique (machine).

| Champ              | Cardinalité | Définition                          | Valeurs possibles                        |
|--------------------|-------------|-------------------------------------|------------------------------------------|
| `id`               | 1           | Identifiant technique, clé primaire | uuid                                     |
| `timeSerie`        | 1 →TS       | Série validée                       | → TimeSerie                              |
| `periodStart`      | 1           | Début de la fenêtre validée         | "2024-01-01T00:00:00Z"                   |
| `periodEnd`        | 1           | Fin de la fenêtre validée           | "2024-03-31T23:59:59Z"                   |
| `agentType`        | 1           | Type d'agent ayant validé           | `person` \| `machine`                    |
| `agentId`          | 1           | UUID de la Person ou Machine        | uuid                                     |
| `validatedAt`      | 1           | Date d'exécution du batch           | "2024-04-01T08:00:00Z"                   |
| `validationLogUrl` | 0..1        | URI vers le log externe (Wiski...)  | "https://wiski.inrae.fr/log-2024-q1.csv" |
| `status`           | 1           | État du batch                       | `pending` \| `validated` \| `rejected`   |
| `comment`          | 0..1        | Commentaire libre sur la session    | "Validation Q1 2024 après crue janvier"  |

---

### ValidatedObservation
> Valeur validée par un opérateur ou un pipeline qualité -- avec indicateur qualité.
Aligné avec : STA Observation (enrichie), ODM2 Result + DataQuality,
             Helmholtz SMS observation metadata, HydroServer ProcessingLevel
Utilisé par : TimeSerie (observations)
Note : point de mesure validé par opérateur humain ou pipeline automatique.
       Lien vers données brutes : TimeSerie → HistoricalDatastream + phenomenonTime.
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
| `specimen`   | 0..1 →Spec  | Prélèvement terrain associé (lab_sample uniquement) | → Specimen                                          |
| `featureOfInterest` | 0..1 →FOI   | Entité réelle observée                              | → FeatureOfInterest                                        |

---

### ControlObservation
> Mesure ponctuelle de vérification -- valeur obtenue par une méthode indépendante et comparée à la série continue pour détecter une dérive ou une erreur.
Aligné avec : ODM2 ResultQualifier, OGC OMS
Utilisé par : TimeSerie (controlObservations)
Note : se greffe directement sur une TimeSerie sans Datastream dédié.
       Le System et la procédure diffèrent intentionnellement de ceux de la
       TimeSerie parente -- c'est une mesure indépendante pour vérifier la cohérence.
       Ex : jaugeage de vérification sur une série de hauteur d'eau,
            mesure avec un System étalonné de référence,
            comparaison avec une station voisine.
       system : contrainte applicative systemType=sensor.
       Type via KeywordAssignment (keywordType='controlType') :
       valeurs courantes : independent_measure, cross_validation, reference_gauge

| Champ                   | Cardinalité | Définition                            | Valeurs possibles                        |
|-------------------------|-------------|---------------------------------------|------------------------------------------|
| `id`                    | 1           | Identifiant technique, clé primaire   | uuid                                     |
| `timeSerie`             | 1 →TS       | Série parente                         | → TimeSerie                              |
| `phenomenonTime`        | 1           | Instant ou période du phénomène (STA) | "2024-03-15T09:30:00Z"                   |
| `resultTime`            | 0..1        | Instant où le résultat a été produit  | "2024-03-15T09:35:00Z"                   |
| `result`                | 1           | Valeur mesurée                        | "0.02"                                   |
| `expectedResult`        | 0..1        | Valeur attendue selon la série        | "0.021"                                  |
| `qualityFlag`           | 1           | Résultat du contrôle                  | `pass` \| `warn` \| `fail`               |
| `qualityComment`        | 0..1        | Justification libre du flag qualité   | "écart de 5% -- dérive capteur probable" |
| `system`                | 0..1 →Sys   | System utilisé pour le contrôle (systemType=sensor) | → System                                 |
| `procedure.observation` | 1 →Proc     | Protocole de mesure appliqué          | → Procedure (type=observation)           |
| `specimen`       | 0..1 →Spec  | Prélèvement terrain associé           | → Specimen                        |
| `featureOfInterest`     | 0..1 →FOI   | Entité réelle observée                | → FeatureOfInterest                      |

---

### Specimen
> Acte de prélèvement terrain daté -- résultat de l'activation d'un ou plusieurs équipements via Deployment.
Aligné avec : OGC OMS SF_Specimen, ODM2 Specimen, ISO 19156, STA FeatureOfInterest (specimen)
Utilisé par : ValidatedObservation (specimen), ControlObservation (specimen),
             Observation (specimen), specimen_deployment (specimenId)
Note : acte de prélèvement physique -- un flacon rempli, un piège récolté.
       Distinct de Station (point de surveillance spatial permanent).
       L'ancrage géographique est hérité du ou des Deployments via specimen_deployment.
       La chaîne analytique interne au laboratoire est hors modèle -- lien via limsReference.
       agentType + agentId : pattern TPC -- technicien terrain (person) ou
       préleveur automatique (machine).
       foi : FOI proximate -- ce qui a été échantillonné précisément (eau de surface
       à 30cm), distincte de la FOI de Station (la rivière en général).
       derivedFrom : sous-échantillon issu d'un Specimen parent (aliquote, dilution).
       Keywords attendus via KeywordAssignment (voir KeywordRequirement) :
         specimenType (required) -- ex: water, soil, sediment, biological
         samplingMedium (required) -- ex: surfaceWater, groundwater, depth

| Champ                 | Cardinalité | Définition                                    | Valeurs possibles             |
|-----------------------|-------------|-----------------------------------------------|-------------------------------|
| `id`                  | 1           | Identifiant technique, clé primaire           | uuid                          |
| `datetime`            | 1           | Horodatage de la récolte                      | "2024-03-15T09:30:00Z"        |
| `foi`                 | 0..1 →FOI   | FOI proximate -- ce qui a été échantillonné   | → FeatureOfInterest           |
| `project`             | 0..1 →Proj  | Projet ou campagne dont dépend ce prélèvement | → Project                     |
| `depth`               | 0..1        | Profondeur de prélèvement en mètres           | "0.30"                        |
| `volume`              | 0..1        | Volume prélevé en litres                      | "1.0"                         |
| `filtrationOnSite`    | 0..1        | Filtration effectuée sur le terrain           | `true` \| `false`             |
| `filtrationThreshold` | 0..1        | Seuil de filtration en µm                     | "0.45"                        |
| `agentType`           | 0..1        | Type d'agent ayant réalisé la récolte         | `person` \| `machine`         |
| `agentId`             | 0..1        | UUID de la Person ou Machine                  | uuid                          |
| `location`            | 0..1 →Loc   | Position exacte si différente du Deployment   | → Location                    |
| `condition`           | 0..1        | Observations terrain libres                   | "turbidité élevée, eau brune" |
| `derivedFrom`         | 0..1 →Spec  | Specimen parent si sous-échantillon           | → Specimen                    |
| `limsReference`       | 0..1        | Identifiant du prélèvement dans le LIMS       | "LIMS-2024-03-001"            |

---

### specimen_deployment
> Lien many-to-many entre un Specimen et les Deployments qui l'ont produit.
Note : un prélèvement peut mobiliser plusieurs équipements simultanément
       (pompe + flacon + filtre = trois Deployments → un Specimen).
       Un Deployment peut produire plusieurs Specimens dans le temps
       (piège récolté chaque semaine pendant un mois).
       L'ancrage géographique du Specimen est hérité du Deployment (Station ou Site).

| Champ          | Cardinalité | Définition               |
|----------------|-------------|--------------------------|
| `specimenId`   | 1 →Spec     | Specimen produit         |
| `deploymentId` | 1 →Dep      | Deployment ayant produit |

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

| Champ            | Cardinalité    | Définition                             | Valeurs possibles                      |
|------------------|----------------|----------------------------------------|----------------------------------------|
| `id`             | 1              | Identifiant technique, clé primaire    | uuid                                   |
| `code`           | 1              | Slug unique par Station                | "hea-qmj-v3"                           |
| `name`           | 1              | Nom de la fonction                     | "Courbe de tarage Mercier D610 v3"     |
| `description`    | 0..1           | Description libre                      |                                        |
| `station`        | 1 →Sta         | Station associée                       | → Station                              |
| `inputProperty`  | 1 →Prop        | Variable en entrée                     | → Property (ex: hauteur)               |
| `outputProperty` | 1 →Prop        | Variable en sortie                     | → Property (ex: débit)                 |
| `parameters`     | 0..1           | Coefficients analytiques (JSON)        | {"a":2.1,"b":1.5}                      |
| `procedure`      | 0..1 →Proc     | Méthode de construction de la fonction | → Procedure (type=modeling)            |
| `startDate`      | 1              | Date de début de validité              | "2024-01-01T00:00:00Z"                 |
| `endDate`        | 0..1           | Date de fin, null si active            | null                                   |
| `status`         | 1              | État de la fonction                    | `active` \| `inactive` \| `deprecated` |

---

### TransferFunctionPoint
> Couple (x, y) de calibration issu d'un jaugeage terrain -- définit empiriquement la courbe.
Utilisé par : TransferFunction (via function FK -- relation inverse)
Note : couple de valeurs (x/y) définissant empiriquement la fonction.
       Analogue à ValidatedObservation -- c'est là que vivent les données.
       Ex : (hauteur=1.23m, débit=4.5m³/s) pour une courbe de tarage.
       Ex : (turbidité=120NTU, MES=245mg/L) pour une relation turbidité/MES.

| Champ      | Cardinalité | Définition                          | Valeurs possibles       |
|------------|-------------|-------------------------------------|-------------------------|
| `id`       | 1           | Identifiant technique, clé primaire | uuid                    |
| `function` | 1 →TF       | Fonction parente                    | → TransferFunction      |
| `batch`    | 0..1 →TFB   | Batch de construction parent        | → TransferFunctionBatch |
| `x`        | 1           | Valeur en entrée                    | 1.23                    |
| `y`        | 1           | Valeur en sortie                    | 4.5                     |
| `uncertainty` | 0..1     | Incertitude sur la mesure           | 0.05                    |
| `datetime` | 0..1        | Date du jaugeage ou de la mesure    | "2024-03-15T09:30:00Z"  |
| `comment`  | 0..1        | Commentaire libre                   | "jaugeage crue"         |

---

### TransferFunctionBatch
> Acte de construction d'une TransferFunction -- qui a construit la courbe, quand, avec quel outil.
Aligné avec : ODM2 Actions, W3C PROV-O wasGeneratedBy
Utilisé par : TransferFunctionPoint (batch)
Note : acte de construction d'une TransferFunction -- qui, quand, depuis quel outil.
       Analogue à ValidationBatch et TransformationBatch.
       La procédure est portée par TransferFunction parente, pas répétée ici.
       agentType + agentId : pattern TPC -- expert humain (person) pour une courbe
       de tarage manuelle, ou algorithme automatique (machine) pour BaRatin en mode batch.

| Champ               | Cardinalité | Définition                             | Valeurs possibles               |
|---------------------|-------------|----------------------------------------|---------------------------------|
| `id`                | 1           | Identifiant technique, clé primaire    | uuid                            |
| `transferFunction`  | 1 →TF       | Fonction construite                    | → TransferFunction              |
| `builtAt`           | 1           | Date de construction                   | "2024-04-01T08:00:00Z"          |
| `agentType`         | 0..1        | Type d'agent ayant construit la courbe | `person` \| `machine`           |
| `agentId`           | 0..1        | UUID de la Person ou Machine           | uuid                            |
| `logUrl`            | 0..1        | Référence externe (export BaRatin..)   | "https://..."                   |
| `status`            | 1           | État du batch                          | `pending` \| `done` \| `failed` |
| `comment`           | 0..1        | Commentaire libre                      |                                 |

---

### TransferFunctionSet
> Jeu de transformation applicable sur une période -- référence une TransferFunction et son type.
Aligné avec : WMO hydrological standards, ODM2 Methods
Utilisé par : TransformationBatch (transferFunctionSet)
Note : conteneur obligatoire pour une ou plusieurs TransferFunction sur une station.
       Même avec une seule TF on passe toujours par un TFSet.
       Plusieurs TFSet peuvent coexister sur une station sans hiérarchie imposée.
       type=identity ou manual -> transferFunction null, pas de calcul via TF.

| Champ              | Cardinalité | Définition                          | Valeurs possibles                    |
|--------------------|-------------|-------------------------------------|--------------------------------------|
| `id`               | 1           | Identifiant technique, clé primaire | uuid                                 |
| `name`             | 1           | Nom du jeu                          | "Barème Mercier D610 2024"           |
| `description`      | 0..1        | Description libre                   |                                      |
| `station`          | 1 →Sta      | Station associée                    | → Station                            |
| `transferFunction` | 0..1 →TF    | Fonction appliquée si type=function | → TransferFunction                   |
| `type`             | 1           | Type de transformation              | `function` \| `identity` \| `manual` |
| `validFrom`        | 1           | Début de validité                   | "2024-01-01T00:00:00Z"               |
| `validTo`          | 0..1        | Fin de validité, null si courant    | null                                 |
| `comment`          | 0..1        | Justification du choix              | "nouveau jaugeage après crue"        |

Contrainte : si type=function -> transferFunction obligatoire.
             si type=identity ou manual -> transferFunction null.

---

### TransformationBatch
> Acte de calcul d'une série dérivée -- qui a lancé le calcul, quand, depuis quelles séries sources.
Aligné avec : ODM2 Actions (dérivation), W3C PROV-O wasGeneratedBy
Utilisé par : Transformation (transformationBatch)
Note : acte de calcul sur une ou plusieurs TimeSerie sources.
       Analogue à ValidationBatch -- factorisation des métadonnées de calcul.
       Les points calculés sont dans Transformation.
       inputSeries est une table de jointure explicite `transformationbatch_inputseries`
       (batch_id, timeserie_id) -- un batch peut prendre plusieurs séries en entrée.
       agentType + agentId : pattern TPC -- opérateur humain (person) pour un calcul
       manuel, pipeline automatique (machine) pour un recalcul planifié.
       Point ouvert : cas sans TransferFunctionSet (transformation algorithmique pure)
       -- transferFunctionSet est actuellement obligatoire (1), à trancher en v2.

| Champ                  | Cardinalité | Définition                          | Valeurs possibles               |
|------------------------|-------------|-------------------------------------|---------------------------------|
| `id`                   | 1           | Identifiant technique, clé primaire | uuid                            |
| `transformedTimeSerie` | 1 →TTS      | Série produite                      | → TransformedTimeSerie          |
| `transferFunctionSet`  | 1 →TFS      | Jeu de fonctions appliqué           | → TransferFunctionSet           |
| `inputSeries`          | 1..* →TS    | Séries sources (table jointure)     | → TimeSerie[]                   |
| `appliedAt`            | 1           | Date d'exécution du calcul          | "2024-04-01T08:00:00Z"          |
| `agentType`            | 0..1        | Type d'agent ayant lancé le calcul  | `person` \| `machine`           |
| `agentId`              | 0..1        | UUID de la Person ou Machine        | uuid                            |
| `validFrom`            | 1           | Début de la période calculée        | "2024-01-01T00:00:00Z"          |
| `validTo`              | 0..1        | Fin de la période calculée          | null                            |
| `status`               | 1           | État du batch                       | `pending` \| `done` \| `failed` |
| `comment`              | 0..1        | Commentaire libre                   |                                 |

---

### Transformation
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
             TimeSeriesBundle via bundle_serie (serieType='TransformedTimeSerie')
Relations inverses (requêter par resourceType='TransformedTimeSerie') :
  Identifier, Memory, KeywordAssignment
Note : série dérivée d'une ou plusieurs TimeSerie via des TransformationBatch.
       Analogue à TimeSerie -- même structure de métadonnées.
       Plusieurs TransformedTimeSerie peuvent coexister sur la même station
       et la même variable sans hiérarchie -- c'est le contexte scientifique
       qui désigne laquelle utiliser (même principe que TimeSerie).
       code unique par Station.

| Champ                      | Cardinalité    | Définition                          | Valeurs possibles                        |
|----------------------------|----------------|-------------------------------------|------------------------------------------|
| `id`                       | 1              | Identifiant technique, clé primaire | uuid                                     |
| `code`                     | 1              | Slug unique par Station             | "debit-tarage-bdoh"                      |
| `name`                     | 1              | Nom de la série dérivée             | "Débit Mercier au pont D610"             |
| `description`              | 0..1           | Description libre                   |                                          |
| `station`                  | 1 →Sta         | Station de rattachement             | → Station                                |
| `property`                 | 1 →Prop        | Variable produite                   | → Property                               |
| `unit`                     | 1 →Unit        | Unité de la série dérivée           | → Unit                                   |
| `procedure.transformation` | 1 →Proc        | Procédure de transformation         | → Procedure (type=transformation)        |
| `startDate`                | 1              | Date de début de la série           | "2024-01-01T00:00:00Z"                   |
| `endDate`                  | 0..1           | Date de fin, null si active         | null                                     |
| `status`                   | 1              | État de la série                    | `active` \| `inactive` \| `discontinued` |
| `license`                  | 1 →Lic         | Licence des données                 | → License                                |


---

## 9. ORGANISATION

### Project
> Projet ou campagne ayant financé ou porté une ressource.
Aligné avec : schema.org/ResearchProject, STAplus Campaign,
             DataCite relatedIdentifier, STAMPLATE memberOf
Utilisé par : HistoricalProject (project), Specimen (project)
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

| Champ          | Cardinalité | Définition                          | Valeurs possibles                                   |
|----------------|-------------|-------------------------------------|-----------------------------------------------------|
| `id`           | 1           | Identifiant technique, clé primaire | uuid                                                |
| `project`      | 1 →Proj     | Projet actif sur cette période      | → Project                                           |
| `resourceType` | 1           | Type de ressource ciblée            | `Observatory` \| `Site` \| `Station` \| `TimeSerie` |
| `resourceId`   | 1           | UUID de la ressource ciblée         | uuid                                                |
| `validFrom`    | 1           | Début de la période                 | "2012-01-01"                                        |
| `validTo`      | 0..1        | Fin de la période, null si actif    | null                                                |

---

### TimeSeriesBundle
> Regroupement éditorial de séries et fonctions pour la diffusion et le catalogage -- objet de publication.
Aligné avec : ODM2 Datasets, DataCite Dataset, DCAT Distribution
Relations inverses : KeywordAssignment
Note : regroupe des TimeSerie, TransformedTimeSerie, TransferFunction et ControlObservation
       pour la publication. Objet éditorial -- pas technique.
       Lien via table polymorphique bundle_serie (serieType + serieId) -- pattern TPC.
       Extensible à tout nouveau type de série sans migration de schéma.

| Champ               | Cardinalité | Définition                          | Valeurs possibles        |
|---------------------|-------------|-------------------------------------|--------------------------|
| `id`                | 1           | Identifiant technique, clé primaire | uuid                     |
| `name`              | 1           | Nom du bundle                       | "Qualité eau Saône 2024" |
| `description`       | 0..1        | Description libre                   |                          |
| `observatory`       | 1 →Obs      | Observatoire parent                 | → Observatory            |
| `license`           | 1 →Lic      | Licence des données du bundle       | → License                |

---

### BundleSerie
> Lien polymorphique entre un TimeSeriesBundle et une série ou fonction -- table de jointure TPC.
Note : Extensible sans migration : ajouter un type = ajouter une valeur à l'enum serieType.
       Intégrité garantie par trigger BEFORE INSERT/UPDATE (pattern TPC agent).

| Champ       | Cardinalité | Définition                   | Valeurs possibles                                                                   |
|-------------|-------------|------------------------------|-------------------------------------------------------------------------------------|
| `bundleId`  | 1 →Bun      | Bundle parent                | → TimeSeriesBundle                                                                  |
| `serieType` | 1           | Type de la série ou fonction | `TimeSerie` \| `TransformedTimeSerie` \| `TransferFunction` \| `ControlObservation` |
| `serieId`   | 1           | UUID de la série ou fonction | uuid                                                                                |

---

### Memory
> Note ou événement attaché à n'importe quelle ressource du modèle -- journal de bord.
Aligné avec : ODM2 Annotations, STAMPLATE schema.org/CreativeWork
Utilisé par : Observatory, Site, Station, System, TimeSerie,
             TransformedTimeSerie, Deployment, Project
             (via resourceType + resourceId)
Note : note contextuelle ou événement daté attaché à n'importe quelle ressource.
       Objet transversal de documentation du cycle de vie.
       Fichiers stockés en S3, référencés via mediaUrl.
       agentType + agentId : pattern TPC -- auteur humain (person) pour une note
       manuelle, pipeline (machine) pour une alerte automatique ou détection d'anomalie.
       Type via KeywordAssignment (keywordType='memoryType') :
       valeurs courantes : note, event, document, photo, installation,
       hydraulic_change, maintenance, incident, calibration

| Champ          | Cardinalité | Définition                          | Valeurs possibles                                                               |
|----------------|-------------|-------------------------------------|---------------------------------------------------------------------------------|
| `id`           | 1           | Identifiant technique, clé primaire | uuid                                                                            |
| `resourceType` | 1           | Type de ressource ciblée            | `Observatory` \| `Site` \| `Station` \| `System` \| `TimeSerie` \| `TransformedTimeSerie` \| `Deployment` \| `Project` \| `TransferFunction` |
| `resourceId`   | 1           | UUID de la ressource ciblée         | uuid                                                                            |
| `datetime`     | 1           | Date de la note ou de l'événement   | "2014-04-17T00:00:00Z"                                                          |
| `title`        | 0..1        | Titre court                         | "Modification contrôle hydraulique"                                             |
| `content`      | 0..1        | Texte libre                         | "Installation d'une lame déversante"                                            |
| `mediaUrl`     | 0..*        | Photos ou documents associés (S3)   | "https://storage.obs.fr/memories/2014-lame.jpg"                                 |
| `agentType`    | 0..1        | Type d'agent auteur de la note      | `person` \| `machine`                                                           |
| `agentId`      | 0..1        | UUID de la Person ou Machine        | uuid                                                                            |
