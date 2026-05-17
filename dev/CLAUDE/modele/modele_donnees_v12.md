---
title:  Modèle de données BDOH
subtitle: Métadonnées des entités
author: Louis Héraut
date: mai 2026
affiliation: INRAE, UR RiverLy, Villeurbanne, France
---

# Convention de lecture

## Nature du fichier

Ce fichier est le **modèle de données BDD** de BDOH. Chaque tableau décrit
les colonnes réelles d'une table SQL. Les relations inverses (0..*)
n'apparaissent pas dans les tableaux : elles sont accessibles via requête
sur la table qui porte la FK, et documentées dans les notes de chaque entité.

## Cardinalités

- `1` = obligatoire
- `0..1` = optionnel
- `1..*` = un ou plus
- `0..*` = table de jointure explicite

## Conventions de nommage

Les règles suivantes s'appliquent uniformément dans tout le modèle.

**Tables** :
- `TitleCase` pour les entités principales : `Observatory`, `TimeSeries`,
  `TransferFunctionPoint`. Les composés gardent chaque mot capitalisé.
- `snake_case` pour les tables de jointure many-to-many qui n'ont pas
  d'identité propre : `person_organization`, `bundle_series`,
  `specimen_deployment`, `transformationbatch_inputseries`. Le contraste
  visuel signale qu'elles ne sont pas référencées comme entités.

**Colonnes** :
- `camelCase` partout : `anchorType`, `validFrom`, `phenomenonTimeStart`.
- Exception conventionnelle pour les suffixes de langue : `label_fr`,
  `label_en`, `term_fr`, `term_en`, `definition_fr`, `definition_en`.

**Valeurs d'enum** :
- Discriminants TPC pointant vers une entité (`resourceType`, `anchorType`,
  `seriesType`, `agentType` pour `Organization`) : **`TitleCase`** = nom
  exact de l'entité ciblée (`Observatory`, `Site`, `Station`,
  `TimeSeries`...). Cette règle rend le discriminant auto-explicite.
- Tous les autres enums : `lowercase` pour les mots simples (`active`,
  `good`, `sensor`), `snake_case` pour les composés (`sensor_continuous`,
  `surface_relative`, `standard_deviation`). Y compris pour les valeurs
  alignées sur un standard externe : la cohérence interne prime sur
  le mimétisme exact (les correspondances avec les vocabulaires
  externes - ODM2 par exemple - sont documentées dans les notes
  d'entité et les tableaux de mapping).

## Relations inverses et API

Toutes les relations inverses absentes des tableaux réapparaissent comme
endpoints de navigation dans l'API :

```
GET /{resource}/{id}/identifiers       → Identifier WHERE resourceId={id}
GET /{resource}/{id}/memories          → Memory WHERE resourceId={id}
GET /{resource}/{id}/responsibilities  → Responsibility WHERE resourceId={id}
GET /{resource}/{id}/keywords          → KeywordAssignment WHERE resourceId={id}
GET /{resource}/{id}/projects          → HistoricalProject WHERE resourceId={id}
GET /{resource}/{id}/locations         → HistoricalLocation WHERE resourceId={id}
```

Les tables de jointure explicites (`person_organization`, `bundle_series`,
`transformationbatch_inputseries`, `specimen_deployment`) deviennent
des endpoints bidirectionnels.

## Notation des champs « Utilisé par »

Chaque entité liste dans son champ *Utilisé par* les entités qui pointent
vers elle. La nature du lien est indiquée entre parenthèses :

- `Entité (FK nomColonne)` : lien par clé étrangère directe. La colonne
  `nomColonne` de l'entité citée pointe vers l'entité courante.
  Exemple : `Site (FK observatory)` - la colonne `observatory` de Site.
- `Entité (anchor)` ou `... (anchorType='X')` : lien par le pattern TPC anchor.
  L'entité citée porte `anchorType` + `anchorId` (voir Pattern TPC anchor).
- `Entité (via resourceType + resourceId)` : lien par table polymorphique.
- `Entité (table jointure)` : lien many-to-many via une table de jointure.

Cette notation permet de distinguer une FK réelle d'un lien polymorphique
sans avoir à ouvrir le tableau de l'entité citée.


<div class="page-break"></div>

# Identifiants

## UUID

Clé primaire technique sur toutes les entités. Immuable, jamais réutilisé.
L'UUID est l'**identifiant de référence** d'une ressource : tout partage,
toute citation scientifique, tout lien pérenne se fait par UUID, jamais
par `code`.

```
Permalink : /resources/{uuid}
```

## code

Slug lisible, obligatoire (`1`) sur toutes les entités. Modifiable par
l'utilisateur. Une suggestion automatique est proposée à la création
depuis le `name` (ou le `serialNumber` pour System). Le code est unique
dans son scope parent : deux entités de scopes différents peuvent avoir
le même code.

Le `code` est un **confort de navigation** : il permet aux techniciens
de lire et comprendre les ressources de l'API sans manipuler des UUID.
Il n'a aucune valeur d'identifiant pérenne - parce qu'il est modifiable,
il ne doit jamais servir de cible à un lien partagé, un export cité ou
une référence externe. Ces usages passent exclusivement par l'UUID.
La modification d'un `code` est donc sans conséquence sur l'intégrité :
elle relève de l'organisation et de la lisibilité, pas de l'identification.

Les codes externes (SANDRE, TheiaOZCAR, WIGOS...) sont portés par
`Identifier`, pas par `code`. Le `code` est interne à BDOH.

## Scopes d'unicité du code

```
Observatory           unique globalement
Organization          unique globalement
System                unique globalement
Project               unique globalement
Procedure             unique globalement
Property              unique globalement
Unit                  unique globalement
Site                  unique par Observatory
Station               unique par Site
Deployment            unique par Station
TimeSeries            unique par ancre (Observatory, Site ou Station)
Datastream            unique par ancre (Observatory, Site ou Station)
TransferFunction      unique par ancre (Observatory, Site ou Station)
TransformedTimeSeries unique par ancre (Observatory, Site ou Station)
```

<div class="page-break"></div>

# Patterns transversaux

## Tables polymorphiques (resourceType + resourceId)

Ces tables portent la FK vers la ressource cible via `resourceType + resourceId`.
Elles ne génèrent aucune colonne dans les tables cibles.

| Table                | Ce qu'elle stocke                        | Ressources supportées                                                               |
|----------------------|------------------------------------------|-------------------------------------------------------------------------------------|
| `Identifier`         | PIDs vers référentiels externes          | toutes les entités navigables                                                       |
| `Memory`             | Notes, événements, photos                | Observatory, Site, Station, System, TimeSeries, TransformedTimeSeries, Deployment, Project, TransferFunction |
| `Responsibility`     | Rôles d'acteurs sur des ressources       | Observatory, Site, Station, System, Datastream, TimeSeries, TransformedTimeSeries, TransferFunction, Project, Bundle |
| `KeywordAssignment`  | Mots-clés et classifications contrôlées  | toutes les entités (voir KeywordAssignment.resourceType)                            |
| `KeywordRequirement` | Règles de complétion minimale            | défini par resourceType + keywordType                                               |
| `HistoricalLocation` | Positions géographiques successives      | Observatory, Site, Station, Deployment                                              |
| `HistoricalProject`  | Projets porteurs successifs              | Observatory, Site, Station, TimeSeries                                              |
| `bundle_series`      | Séries et fonctions regroupées en bundle | TimeSeries, TransformedTimeSeries, TransferFunction, ControlObservation             |

## Pattern TPC anchor (anchorType + anchorId)

Plusieurs entités doivent se rattacher à un contexte géographique qui peut être
Observatory, Site ou Station selon la granularité. Le pattern TPC est appliqué
plutôt que trois FK optionnelles.

| Champ        | Type | Valeurs                                |
|--------------|------|----------------------------------------|
| `anchorType` | enum | `Observatory` \| `Site` \| `Station`   |
| `anchorId`   | uuid | uuid de l'Observatory, Site ou Station |

Tables portant ce pattern : `Deployment`, `Datastream`, `TimeSeries`,
`TransformedTimeSeries`, `Specimen`, `TransferFunction`, `TransferFunctionSet`.

Le domaine de `anchorType` est restreint pour certaines entités, lorsque
l'ancrage sur un Observatory entier n'a pas de sens physique :
- `Deployment` et `Specimen` : `Site` \| `Station` uniquement (on déploie un
  instrument ou prélève un échantillon en un lieu précis, pas sur tout un
  observatoire).
- Toutes les autres : `Observatory` \| `Site` \| `Station`.

La valeur exacte autorisée est indiquée dans le tableau de chaque entité.

Règle de cohérence et source de vérité : chaque flux de données
(`Datastream`, `TimeSeries`, `TransformedTimeSeries`) porte lui-même son
ancrage géographique via `anchorType/anchorId`. Cet ancrage est complet et
autoportant : il n'a pas à être déduit d'une autre entité. C'est une
condition nécessaire pour que chaque flux soit exportable de façon autonome
vers une API externe (STA notamment), où un Datastream doit exposer son
rattachement sans dépendre de la chaîne d'instrumentation.

L'ancrage d'un `Deployment` est une **documentation** de l'installation
physique, ajoutée souvent dans un second temps. En cas de divergence entre
l'ancrage d'un flux et celui du Deployment du System correspondant, c'est
l'ancrage porté par le flux qui fait foi ; le Deployment doit être corrigé
pour s'y conformer.

Ce choix est délibéré : il évite de remonter la chaîne
flux → System → Deployment (requête récursive coûteuse) pour répondre à une
question aussi fréquente que « quels flux sont rattachés à cette station ? ».
La cohérence entre l'ancrage d'un flux et celui de son Deployment est
vérifiée périodiquement au niveau applicatif (voir integrity_checks.md),
elle n'est pas garantie par une contrainte SQL.

## Pattern TPC agent (agentType + agentId)

Plusieurs tables tracent l'acteur d'un acte ou d'une responsabilité.
Cet acteur peut être un humain (Person), un agent automatisé (Machine)
ou une organisation (Organization). Le pattern TPC est appliqué :
`agentType` discrimine le type, `agentId` porte l'UUID. Aucune FK native
PostgreSQL - intégrité garantie par trigger BEFORE INSERT/UPDATE.
Voir integrity_checks.md pour les requêtes de vérification périodique.

| Champ       | Type | Valeurs                                 |
|-------------|------|-----------------------------------------|
| `agentType` | enum | `Person` \| `Machine` \| `Organization` |
| `agentId`   | uuid | uuid de Person, Machine ou Organization |

Tables portant ce pattern :

- `Responsibility` (agentType + agentId, obligatoires) : `Person | Organization | Machine`
- `ValidationBatch` (validatedBy) : `Person | Machine`
- `TransformationBatch` (appliedBy) : `Person | Machine`
- `ObservationBatch` (importedBy) : `Person | Machine`
- `TransferFunctionBatch` (builtBy) : `Person | Machine`
- `Memory` (author) : `Person | Machine`
- `Specimen` (operator) : `Person | Machine`

## Tables de jointure explicites

Ces tables encodent des relations many-to-many portées par l'entité
"propriétaire".

| Table                             | Entre                             |
|-----------------------------------|-----------------------------------|
| `person_organization`             | Person ↔ Organization             |
| `transformationbatch_inputseries` | TransformationBatch ↔ TimeSeries  |
| `specimen_deployment`             | Specimen ↔ Deployment             |

## Associations datées

Plusieurs tables encodent une relation valable sur une période, et portent
pour cela un couple `validFrom` / `validTo` (`validTo` null = relation
courante). Toutes suivent la même structure : (entité cible) + (valeur ou
entité liée) + (`validFrom`/`validTo`).

Leur nommage suit une règle de sens, et non de simple forme :

- Préfixe `Historical*` : la table historise un **attribut qui a une valeur
  courante** sur une ressource. La ressource « a » cet attribut à tout
  instant, et la table garde la trace des valeurs passées.
  `HistoricalLocation` (la localisation d'une ressource),
  `HistoricalProject` (le projet porteur d'une ressource).
- Nom décrivant le **rôle** : la table **relie deux entités dans le temps**
  sans qu'aucune ne soit « l'attribut courant » de l'autre. Le nom dit alors
  ce que la table fait. `TimeSeriesSource` (les Datastreams qui alimentent
  successivement une TimeSeries).

La structure est commune ; le nom doit refléter le jeu de rôle réel de la
table. Un préfixe `Historical*` sur une table qui n'historise pas un attribut
induirait en erreur sur son usage.

## Suppression logique

Aucune suppression physique sur les entités référencées directement ou
via TPC. Un trigger `prevent_physical_delete` est posé sur toutes les entités.
Deux mécanismes selon les tables :

- Tables avec `status` : utiliser `status` comme mécanisme de désactivation.
- Tables sans `status` : `archivedAt TIMESTAMPTZ NULL` (null = actif).

Les tables de jointure (`person_organization`, `specimen_deployment`,
`transformationbatch_inputseries`, `bundle_series`) sont exemptées :
leurs lignes peuvent être supprimées physiquement car elles ne sont
pas elles-mêmes référencées par d'autres relations.

Tables avec `status` (mécanisme natif) : Observatory, Site, Station, System,
Deployment, Datastream, ObservationBatch, ValidationBatch, TransferFunction,
TransferFunctionBatch, TransformationBatch, TransformedTimeSeries, TimeSeries,
Project.

Tables avec `archivedAt` (ajout dédié) : Person, Machine, Organization, Unit,
Procedure, KeywordType, Keyword, License, Location, FeatureOfInterest, Bundle,
Property (qui a déjà `status=accepted|deprecated|proposed`).


<div class="page-break"></div>

# 1. ACTEURS

## Person
> Individu humain impliqué dans la production ou la gestion des données.

*Aligné avec* :
- [ODM2 People](https://github.com/ODM2/ODM2/blob/master/doc/ODM2Docs/core_people.md)
  - structure conceptuelle d'une personne dans un système d'observation
  environnementale (PersonFirstName, PersonLastName, affiliation).
- [schema.org/Person](https://schema.org/Person) - vocabulaire web réutilisé
  par STAMPLATE pour la sérialisation JSON-LD des entités personnes.
- [ORCID](https://orcid.org/) - identifiant persistant chercheur, porté par
  `Person.orcid`.

*Utilisé par* :<br>
pattern TPC agent (agentType=`Person`) sur ValidationBatch, TransformationBatch, ObservationBatch, TransferFunctionBatch, Memory, Specimen. Responsibility (Person). person_organization (affiliation).

*Relations inverses* :<br>
aucune (Person est référencée via agentId ou FK directe)

*Note* :
- Organization est une table de jointure explicite `person_organization`.
- Affiliation institutionnelle, distinct de Responsibility (rôle fonctionnel).
- Une personne peut appartenir à plusieurs organisations simultanément.

| Champ         | Cardinalité | Définition                          | Valeurs possibles                         |
|---------------|-------------|-------------------------------------|-------------------------------------------|
| `id`          | 1           | Identifiant technique, clé primaire | uuid                                      |
| `firstName`   | 1           | Prénom                              | "Julie"                                   |
| `lastName`    | 1           | Nom de famille                      | "Dupont"                                  |
| `email`       | 1           | Adresse email professionnelle       | "julie.dupont@inrae.fr"                   |
| `orcid`       | 0..1        | Identifiant chercheur ORCID         | "0000-0001-1234-1234"                     |
| `affiliation` | 0..1        | Affiliation textuelle libre         | "INRAE, UR RiverLy, Villeurbanne, France" |
| `archivedAt`  | 0..1        | Horodatage d'archivage logique      | null \| "2024-01-01T00:00:00Z"            |

---

## Machine
> Agent automatisé impliqué dans la production ou le traitement des données.

*Aligné avec* :
- [CodeMeta](https://codemeta.github.io/) - vocabulaire pour les métadonnées
  logicielles, basé sur [schema.org/SoftwareApplication](https://schema.org/SoftwareApplication).
  Inspire les champs `codeRepository`, `version`, `doi`.
- [SWHID - ISO/IEC 18670:2025](https://www.swhid.org/swhid-specification/) -
  identifiant intrinsèque permanent du code source, porté par `Machine.swhid`.
  Garantit la reproductibilité scientifique : un même SWHID identifie toujours
  le même état exact du code, indépendamment de sa localisation.
- [Software Heritage](https://www.softwareheritage.org/) - archive universelle
  du code source publié, infrastructure de référence pour résoudre les SWHID.
- [W3C PROV-O Agent](https://www.w3.org/TR/prov-o/#Agent) - Machine est un agent
  PROV au sens de la traçabilité de production (`wasAssociatedWith`).

*Utilisé par* :<br>
pattern TPC agent (agentType=`Machine`) sur ValidationBatch, TransformationBatch, ObservationBatch, TransferFunctionBatch, Memory, Specimen.

*Relations inverses* :<br>
aucune (Machine est référencée via agentId)

*Note* : 
- Représente un pipeline de calcul, un service d'import automatique, un agent IA.
- swhid identifie le code source exact utilisé dans Software Heritage, immuable (ISO/IEC 18670), garantit la reproductibilité scientifique.
- doi identifie la publication HAL du logiciel.
- `codeRepository` pointe vers le dépôt vivant (GitHub, GitLab...).
- Les trois sont complémentaires et alignés avec le standard CodeMeta.

| Champ            | Cardinalité | Définition                                    | Valeurs possibles                                     |
|------------------|-------------|-----------------------------------------------|-------------------------------------------------------|
| `id`             | 1           | Identifiant technique, clé primaire           | uuid                                                  |
| `name`           | 1           | Nom du service ou pipeline                    | "pipeline-validation-bdoh"                            |
| `version`        | 0..1        | Version sémantique du logiciel                | "2.1.0"                                               |
| `codeRepository` | 0..1        | URL du dépôt source (CodeMeta codeRepository) | "https://github.com/inrae/bdoh-pipeline"              |
| `swhid`          | 0..1        | Identifiant Software Heritage (ISO/IEC 18670) | "swh:1:rel:22ece559cc7cc2364edc5e5593d63ae8bd229f9f"  |
| `doi`            | 0..1        | DOI du logiciel si publié                     | "10.5281/zenodo.1234567"                              |
| `archivedAt`     | 0..1        | Horodatage d'archivage logique                | null \| "2024-01-01T00:00:00Z"                        |

---

## Organization
> Structure porteuse (laboratoire, observatoire, agence...).

*Aligné avec* :
- [ODM2 Organizations](https://github.com/ODM2/ODM2/blob/master/doc/ODM2Docs/core_organizations.md)
  - structure conceptuelle d'une organisation porteuse (laboratoire, agence,
  réseau) avec hiérarchie parent.
- [schema.org/Organization](https://schema.org/Organization) - vocabulaire web
  réutilisé par STAMPLATE pour la sérialisation JSON-LD.
- [ROR (Research Organization Registry)](https://ror.org/) - identifiant
  persistant institutionnel, porté via `Identifier` (codeType=`ror`).

*Utilisé par* :<br>
Person via person_organization (table jointure), Responsibility (Organization)

*Keywords attendus (voir KeywordRequirement)* :<br>
- organizationType : laboratory, monitoring_network, research, agency, university

*Note* : 
- code slug unique globalement, suggestion depuis acronym ou name à la création.


| Champ        | Cardinalité | Définition                                  | Valeurs possibles                                      |
|--------------|-------------|---------------------------------------------|--------------------------------------------------------|
| `id`         | 1           | Identifiant technique, clé primaire         | uuid                                                   |
| `code`       | 1           | Slug unique globalement                     | "inrae"                                                |
| `name`       | 1           | Nom complet                                 | "Institut national de recherche pour l'agriculture..." |
| `acronym`    | 0..1        | Sigle                                       | "INRAE"                                                |
| `country`    | 1           | Pays (code ISO 3166-1 alpha-2)              | "FR"                                                   |
| `url`        | 0..1        | Site web                                    | "https://www.inrae.fr"                                 |
| `logoUrl`    | 0..1        | URL vers le logo (S3 ou hébergeur officiel) | "https://www.inrae.fr/logo.svg"                        |
| `archivedAt` | 0..1        | Horodatage d'archivage logique              | null \| "2024-01-01T00:00:00Z"                         |

---

## Responsibility
> Rôle d'un acteur (personne, organisation ou agent machine) sur une ressource à un instant T.

*Aligné avec* :
- [ISO 19115-1 CI_Responsibility](https://www.iso.org/standard/53798.html) -
  modèle de référence pour les responsabilités sur une ressource géographique.
  Sépare l'acteur (party) du rôle, ce qui permet la réutilisation d'un même
  acteur dans plusieurs rôles.
- [ISO 19115 CI_RoleCode](https://standards.iso.org/iso/19115/resources/Codelists/gml/CI_RoleCode.xml)
  - liste contrôlée des 20 rôles utilisés par BDOH (`resourceProvider`,
  `custodian`, `owner`, `funder`, `principalInvestigator`...). Reprise complète
  de ISO 19115-1 sans extension.
- [ODM2 Affiliations](https://github.com/ODM2/ODM2/blob/master/doc/ODM2Docs/core_people.md)
  - mécanisme analogue (Person × Organization × Role × période), qui a inspiré
  la temporalité `validFrom/validTo`.
- [schema.org/Role](https://schema.org/Role) - vocabulaire web utilisé par
  STAMPLATE pour la sérialisation JSON-LD des rôles.
- [W3C PROV-O wasAssociatedWith](https://www.w3.org/TR/prov-o/#wasAssociatedWith)
  - Responsibility encode des relations PROV de type "agent associé à une
  activité ou à une entité".

*Utilisé par* :<br>
Observatory, Site, Station, System, Datastream, TimeSeries, TransformedTimeSeries, TransferFunction, Project, Bundle (via resourceType + resourceId)

*Note* : 
- Lie un acteur à une ressource avec un rôle fonctionnel et une période de validité.
- Distinct de Person.organization (appartenance institutionnelle).
- Pattern TPC agent : agentType discrimine Person, Organization ou Machine.
- agentType + agentId obligatoires (1), on sait toujours qui porte la responsabilité.
- Machine légitime pour certains rôles : custodian (pipeline IA de curation), processor (service de traitement automatique), originator (capteur autonome).
- Liste des rôles alignée sur ISO 19115-1 complète.

| Champ          | Cardinalité | Définition                                 | Valeurs possibles                                                         |
|----------------|-------------|--------------------------------------------|---------------------------------------------------------------------------|
| `id`           | 1           | Identifiant technique, clé primaire        | uuid                                                                      |
| `agentType`    | 1           | Type d'acteur responsable                  | `Person` \| `Organization` \| `Machine`                                   |
| `agentId`      | 1           | UUID de la Person, Organization ou Machine | uuid                                                                      |
| `role`         | 1           | Rôle fonctionnel CI_RoleCode ISO 19115-1   | `resourceProvider` \| `custodian` \| `owner` \| `user` \| `distributor` \| `originator` \| `pointOfContact` \| `principalInvestigator` \| `processor` \| `publisher` \| `author` \| `sponsor` \| `coAuthor` \| `collaborator` \| `editor` \| `mediator` \| `rightsHolder` \| `contributor` \| `funder` \| `stakeholder` |
| `resourceType` | 1           | Type de ressource ciblée                   | `Observatory` \| `Site` \| `Station` \| `System` \| `Datastream` \| `TimeSeries` \| `TransformedTimeSeries` \| `TransferFunction` \| `Project` \| `Bundle` |
| `resourceId`   | 1           | UUID de la ressource ciblée                | uuid                                                                      |
| `validFrom`    | 0..1        | Début de responsabilité                    | "2022-01-01"                                                              |
| `validTo`      | 0..1        | Fin, null si toujours actif                | "2024-12-31" \| null                                                      |


<div class="page-break"></div>

# 2. RÉFÉRENTIELS

## Property
> Variable mesurée ou calculée (température, débit, nitrates...).

*Aligné avec* :
- [OGC STA 1.1 ObservedProperty](https://docs.ogc.org/is/18-088/18-088.html)
  - rôle dans l'API STA : Property est exposée comme ObservedProperty dans les
  réponses /Datastreams.
- [NERC NVS P01 (Parameter Usage Vocabulary)](https://vocab.nerc.ac.uk/collection/P01/current/)
  - vocabulaire de référence pour les variables environnementales, 40 000+ termes
  avec URIs stables. Lien établi via `Identifier` sur Property.
- [ODM2 Variables](https://github.com/ODM2/ODM2/blob/master/doc/ODM2Docs/core_variables.md)
  - structure conceptuelle (variable, definition, defaultUnit) reprise par BDOH.
- [HydroServer ObservedProperty](https://hydroserver2.github.io/hydroserver/)
  - implémentation de référence qui garde Property comme entité distincte
  (et non comme champ JSON inline de Datastream).

*Utilisé par* :<br>
TimeSeries (property), TransformedTimeSeries (property), TransferFunction (inputProperty, outputProperty), Datastream (property)

*Relations inverses* :<br>
Identifier, KeywordAssignment

*Keywords attendus (voir KeywordRequirement)* :<br>
- discipline (required) : hydrology, chemistry, meteorology
- theme (recommended) : metals, nutrients, pesticides
- samplingMedium (recommended) : surface_water, groundwater, soil

*Note* : 
- Géré par les curateurs, chaque variable est unique et non dupliquée.
- URIs vers thésaurus externes via identifier.
- Correspond à ObservedProperty dans l'API STA exposée.

| Champ           | Cardinalité | Définition                             | Valeurs possibles                              |
|-----------------|-------------|----------------------------------------|------------------------------------------------|
| `id`            | 1           | Identifiant technique, clé primaire    | uuid                                           |
| `code`          | 1           | Code court unique, curateur (2-8 cars) | "no3" \| "debit" \| "doc" \| "bact-div"        |
| `symbol`        | 0..1        | Symbole scientifique universel         | "NO3" \| "Q" \| "DOC"                          |
| `name`          | 1           | Nom de la variable                     | "Nitrate" \| "Débit journalier maximal annuel" |
| `definition`    | 0..1        | Définition textuelle                   | "Maximum annuel du débit journalier"           |
| `defaultUnit`   | 0..1 →Unit  | Unité par défaut                       | → Unit                                         |
| `sourceProperty`| 0..1 →Prop  | Variable source pour les dérivées      | → Property (ex: "Q" pour "QJXA")               |
| `origin`        | 0..1        | Mode de production                     | `observed` \| `derived`                        |
| `status`        | 1           | Statut géré par les curateurs          | `accepted` \| `deprecated` \| `proposed`       |

---

## Unit
> Unité de mesure associée à une Property.

*Aligné avec* :
- [ODM2 Units](https://github.com/ODM2/ODM2/blob/master/doc/ODM2Docs/core_units.md)
  - structure conceptuelle (code, symbol, name, definition).
- [HydroServer Unit](https://hydroserver2.github.io/hydroserver/) - implémentation
  de référence qui choisit, comme BDOH, de garder Unit comme entité séparée
  (FK depuis Datastream) plutôt que comme objet JSON inline (choix STA 1.1).
  Justification empirique de l'ADR-017.
- [QUDT vocab/unit](https://qudt.org/vocab/unit/) - URIs persistantes vers les
  définitions ontologiques des unités. Portées par `Unit.definition`.
- [UCUM (Unified Code for Units of Measure)](https://ucum.org/) - alternative
  syntaxique compacte pour exprimer les unités (`mg/L`, `m3/s`). Utilisable
  comme valeur de `Unit.definition` en complément de QUDT.

*Utilisé par* :<br>
Property (defaultUnit), TimeSeries (unit), TransformedTimeSeries (unit), Datastream (unitOfMeasurement)

*Note* : 
- HydroServer ajoute Unit comme entité séparée car STA standard n'a qu'un objet JSON inline pour unitOfMeasurement dans Datastream.

| Champ        | Cardinalité | Définition                          | Valeurs possibles                          |
|--------------|-------------|-------------------------------------|--------------------------------------------|
| `id`         | 1           | Identifiant technique, clé primaire | uuid                                       |
| `code`       | 1           | Code court pour URLs (kebab-case)   | "mg-l" \| "m3-s" \| "degc"                 |
| `symbol`     | 1           | Symbole textuel affiché             | "mg/L" \| "m³/s" \| "°C"                   |
| `name`       | 1           | Nom complet de l'unité              | "milligram per litre"                      |
| `definition` | 1           | URI QUDT ou UCUM                    | "http://qudt.org/vocab/unit/MilliGM-PER-L" |
| `archivedAt` | 0..1        | Horodatage d'archivage logique      | null \| "2024-01-01T00:00:00Z"             |

---

## Procedure
> Protocole appliqué - de prélèvement, mesure, modélisation, agrégation, transformation ou validation.

*Aligné avec* :
- [OGC STA 1.1 Sensor](https://docs.ogc.org/is/18-088/18-088.html) - dans STA,
  l'entité "Sensor" représente la procédure de mesure (la méthode), pas
  l'instrument physique. BDOH le sépare explicitement : Procedure = méthode,
  System = instrument.
- [ODM2 Methods](https://github.com/ODM2/ODM2/blob/master/doc/ODM2Docs/core_methods.md)
  - structure conceptuelle (name, description, version, reference) reprise.
- [OGC OMS (ISO 19156:2023)](https://docs.ogc.org/as/20-082r4/20-082r4.html)
  - concept central de OGC Observations, Measurements and Samples qui définit
  la procédure d'observation comme un acte typé (sampling, observation,
  validation...).
- [Helmholtz SMS](https://helmholtz.software/software/sensor-management-system)
  - apporte la notion de Method liée à un capteur, avec liens vers les
  protocoles publiés (DOI, normes ISO).

*Utilisé par* :<br>
TimeSeries (procedureObservation, procedureValidation, procedureSampling), ControlObservation (procedureObservation), TransferFunction (procedureModeling), TransformedTimeSeries (procedureTransformation), Datastream (procedureObservation), Specimen (procedureSampling)

*Note* :
- Entité réutilisable - une même Procedure peut être référencée par plusieurs objets. Le type discrimine le rôle et filtre les choix dans l'interface. 
- Types et exemples :
  * **sampling** - prélever un échantillon terrain (ex : "Prélèvement eau de surface au seau", "Prélèvement automatique ISCO 3700")
  * **observation** - mesurer une valeur (capteur continu, labo, jaugeage, contrôle) (ex : "NF EN ISO 10304-1 chromatographie ionique", "Jaugeage au micro-moulinet OTT C2", "Mesure sonde multiparamètre YSI EXO2")
  * **modeling** - construire un modèle depuis des mesures ("BaRatin v3 - courbe de tarage bayésienne", "Régression polynomiale turbidité/MES", "Courbe d'étalonnage spectrophotométrie")
  * **aggregation** - agréger temporellement ou spatialement des valeurs (ex : "Moyenne journalière sur plage horaire", "Agrégation annuelle QJXA depuis débits journaliers", "Cumul pluviométrique mensuel")
  * **transformation** - appliquer un calcul pour produire de nouvelles valeurs (ex : "Application courbe de tarage par interpolation linéaire", "Correction offset dérive capteur")
  * **validation** - qualifier des données existantes (ex : "Validation visuelle Wiski par opérateur", "Pipeline automatique contrôle bornes SANDRE")

| Champ          | Cardinalité | Définition                          | Valeurs possibles                                                               |
|----------------|-------------|-------------------------------------|---------------------------------------------------------------------------------|
| `id`           | 1           | Identifiant technique, clé primaire | uuid                                                                            |
| `code`         | 1           | Slug unique globalement             | "iso-10304-1"                                                                   |
| `name`         | 1           | Nom du protocole                    | "NF EN ISO 10304-1"                                                             |
| `type`         | 1           | Rôle du protocole                   | `sampling` \| `observation` \| `modeling` \| `aggregation` \| `transformation` \| `validation` |
| `description`  | 0..1        | Description libre                   |                                                                                 |
| `version`      | 0..1        | Version du protocole                | "2021"                                                                          |
| `reference`    | 0..1        | URI ou DOI du document normatif     | "https://www.iso.org/standard/..."                                              |
| `encodingType` | 1           | Type d'encodage (conformité STA)    | "application/pdf" \| URI                                                        |
| `archivedAt`   | 0..1        | Horodatage d'archivage logique      | null \| "2024-01-01T00:00:00Z"                                                  |

---

## KeywordType
> Type de métadonnée contrôlée - documente à quel standard ce type est aligné.

*Aligné avec* :
- [ISO 19115 MD_KeywordTypeCode](https://standards.iso.org/iso/19115/resources/Codelists/gml/MD_KeywordTypeCode.xml)
  - liste contrôlée des types de mots-clés en métadonnées géographiques
  (`discipline`, `theme`, `place`, `taxon`...). KeywordType s'aligne sur cette
  liste mais l'étend par les types BDOH spécifiques (samplingMedium, stationType,
  controlType...).
- [ODM2 Controlled Vocabularies](http://vocabulary.odm2.org/) - système de
  vocabulaires SKOS modérés (medium, methodType, organizationType, sampledMedium...).
  Chaque KeywordType BDOH peut pointer vers son équivalent ODM2 via `standardUri`.

*Utilisé par* :<br>
Keyword (keywordType), KeywordAssignment (keywordType), KeywordRequirement (keywordType)

*Note* :
- Chaque type de keyword est lui-même documenté et aligné avec un standard.
- Géré par les administrateurs BDOH.
- Le tableau ci-dessous donne des exemples représentatifs de types de keyword
  et de leur usage. Cette liste est un point de départ, non un domaine fermé :
  les administrateurs peuvent créer de nouveaux types sans migration de schéma
  (c'est l'intérêt du système Keyword par rapport à un enum SQL).

| keywordType        | S'applique à                   | Exemples de valeurs                                    | Standard d'alignement |
|--------------------|--------------------------------|--------------------------------------------------------|-----------------------|
| `discipline`       | Property                       | hydrology, chemistry, meteorology                      | ISO 19115             |
| `theme`            | Property                       | metals, nutrients, pesticides                          | ISO 19115             |
| `samplingMedium`   | TimeSeries, Specimen, Property | surface_water, groundwater, soil                       | ODM2                  |
| `featureType`      | FeatureOfInterest              | river, lake, groundwater, soil, atmosphere             | ODM2 / OMS            |
| `siteType`         | Site                           | watershed, lake, wetland, aquifer, estuary             | BDOH                  |
| `stationType`      | Station                        | stream_gage, weather_station, well, soil_pit           | SANDRE / WMO          |
| `sensorType`       | System (sensor)                | icp_ms, spectrophotometer, probe, datalogger           | Helmholtz SMS-CV      |
| `platformType`     | System (platform)              | buoy, vertical_chain, drone, mooring                   | Helmholtz SMS-CV      |
| `equipmentType`    | System (equipment)             | bottle, pump, autosampler, corer, filter_holder        | Helmholtz SMS-CV      |
| `organizationType` | Organization                   | laboratory, monitoring_network, agency, university     | ODM2                  |
| `specimenType`     | Specimen                       | water, soil, sediment, biological                      | ODM2                  |
| `controlType`      | ControlObservation             | independent_measure, cross_validation, reference_gauge | BDOH                  |
| `memoryType`       | Memory                         | note, event, document, photo, maintenance, incident    | BDOH                  |

- Exemples de codes de types : discipline, theme, samplingMedium, stationType,
  sensorType, equipmentType, siteType, deploymentType, featureType, memoryType,
  controlType, organizationType, specimenType.

| Champ         | Cardinalité | Définition                           | Valeurs possibles                             |
|---------------|-------------|--------------------------------------|-----------------------------------------------|
| `id`          | 1           | Identifiant technique, clé primaire  | uuid                                          |
| `code`        | 1           | Code interne unique                  | "discipline" \| "stationType" \| "sensorType" |
| `label_fr`    | 1           | Libellé français                     | "Discipline scientifique"                     |
| `label_en`    | 1           | Libellé anglais                      | "Scientific discipline"                       |
| `description` | 0..1        | Description du rôle de ce type       |                                               |
| `standard`    | 0..1        | Standard d'alignement                | "ISO 19115" \| "ODM2" \| "BDOH"               |
| `standardUri` | 0..1        | URI vers le concept dans le standard | "https://standards.iso.org/..."               |
| `archivedAt`  | 0..1        | Horodatage d'archivage logique       | null \| "2024-01-01T00:00:00Z"                |

---

## Keyword
> Terme de vocabulaire contrôlé - aligné avec un thésaurus externe autant que possible.

*Aligné avec* :
- [ISO 19115 MD_Keywords](https://www.iso.org/standard/53798.html) - élément
  structurant des métadonnées géographiques pour la classification thématique
  d'une ressource.
- [ODM2 Controlled Vocabularies](http://vocabulary.odm2.org/) - termes SKOS
  avec URIs persistantes pour les vocabulaires environnementaux. Source
  privilégiée pour `Keyword.uri` quand un terme existe (medium, methodType...).
- [Helmholtz SMS-CV](https://sms-cv.helmholtz.cloud/sms/cv/) - vocabulaire
  contrôlé des systèmes d'observation Earth & Environment. Fournit les listes
  de valeurs pour les KeywordType liés à l'instrumentation (`sensorType`,
  `equipmentType`, `platformType`, `actionType`...) : ce sont ces termes-là que
  les Keyword de ces types reprennent.
- [Theia/OZCAR thesaurus](https://w3id.org/ozcar-theia) - thésaurus national
  français des observatoires de zones critiques. Lien direct dans `Keyword.uri`
  permet l'interopérabilité avec le portail in-situ.theia-land.fr.
- [NERC Vocabulary Server (NVS)](https://vocab.nerc.ac.uk/) - infrastructure
  technique référence pour les vocabulaires SKOS environnementaux.

*Utilisé par* :<br>
KeywordAssignment (keyword) entités via KeywordAssignment (type, discipline, theme...)

*Note* : 
- Vocabulaire géré par les curateurs BDOH.
- Chaque terme doit idéalement pointer vers un thésaurus externe via uri.
- Les termes BDOH sans équivalent externe utilisent thesaurus='BDOH'.
- Utilisé de deux façons :
  1. Via KeywordAssignment - tags multi-valeurs sur une ressource
  2. Via FK directe - champ type sur Organization, Site, Station, etc.

| Champ          | Cardinalité | Définition                          | Valeurs possibles                                |
|----------------|-------------|-------------------------------------|--------------------------------------------------|
| `id`           | 1           | Identifiant technique, clé primaire | uuid                                             |
| `keywordType`  | 1 →KWT      | Type de ce keyword                  | → KeywordType                                    |
| `term_fr`      | 1           | Terme en français                   | "eau de surface" \| "hydrologie"                 |
| `term_en`      | 1           | Terme en anglais                    | "surface water" \| "hydrology"                   |
| `definition_fr`| 0..1        | Définition en français              |                                                  |
| `definition_en`| 0..1        | Définition en anglais               |                                                  |
| `thesaurus`    | 0..1        | Vocabulaire source                  | "ODM2" \| "TheiaOZCAR" \| "SANDRE" \| "BDOH"     |
| `uri`          | 0..1        | URI du terme dans le thésaurus      | "http://vocabulary.odm2.org/medium/surfaceWater" |
| `archivedAt`   | 0..1        | Horodatage d'archivage logique      | null \| "2024-01-01T00:00:00Z"                   |

---

## KeywordAssignment
> Lien entre un keyword et une ressource - pattern polymorphique multi-valeurs.

*Utilisé par* :<br>
Observatory, Site, Station, TimeSeries, TransformedTimeSeries, Bundle, Property, Organization, System, Deployment, FeatureOfInterest, Specimen, ControlObservation, TransferFunction, Datastream (via resourceType + resourceId)

*Note* : 
- Permet d'attacher autant de keywords que nécessaire à une ressource.
- Couvre les classifications multi-valeurs (discipline, theme, samplingMedium...) et les tags éditoriaux libres pour les catalogues.
- Les règles de complétion minimale sont dans KeywordRequirement.

| Champ          | Cardinalité | Définition                          | Valeurs possibles                                                                |
|----------------|-------------|-------------------------------------|----------------------------------------------------------------------------------|
| `id`           | 1           | Identifiant technique, clé primaire | uuid                                                                             |
| `keyword`      | 1 →Keyw     | Keyword assigné                     | → Keyword                                                                        |
| `resourceType` | 1           | Type de ressource ciblée            | `Observatory` \| `Site` \| `Station` \| `TimeSeries` \| `TransformedTimeSeries` \| `Bundle` \| `Property` \| `Organization` \| `System` \| `Deployment` \| `FeatureOfInterest` \| `Specimen` \| `ControlObservation` \| `TransferFunction` \| `Datastream` |
| `resourceId`   | 1           | UUID de la ressource ciblée         | uuid                                                                             |

---

## KeywordRequirement
> Règle de complétion minimale - définit quels keywords sont obligatoires ou recommandés sur un type de ressource.

*Utilisé par* :<br>
validation applicative à la sauvegarde

*Note* : 
- Géré par les administrateurs BDOH sans migration de schéma.
- Permet de définir des standards de métadonnées sans contrainte SQL rigide.
- Exemples :
  * Property doit avoir au moins un keyword de type 'discipline',
  * TimeSeries doit avoir au moins un keyword de type 'samplingMedium'.

| Champ          | Cardinalité | Définition                          | Valeurs possibles                                                  |
|----------------|-------------|-------------------------------------|--------------------------------------------------------------------|
| `id`           | 1           | Identifiant technique, clé primaire | uuid                                                               |
| `resourceType` | 1           | Type de ressource concerné          | `Organization` \| `Property` \| `FeatureOfInterest` \| `Site` \| `Station` \| `System` \| `TimeSeries` \| `TransformedTimeSeries` \| `ControlObservation` \| `Specimen` \| `Memory` |
| `keywordType`  | 1 →KWT      | Type de keyword requis              | → KeywordType                                                      |
| `cardinality`  | 1           | Niveau d'obligation                 | `required` \| `recommended`                                        |

---

## License
> Licence de diffusion des données.

*Aligné avec* :
- [SPDX License List](https://spdx.org/licenses/) - liste de référence des
  licences logicielles, matérielles, documentaires et de données. Fournit pour
  chaque licence un identifiant court canonique (`CC-BY-4.0`, `ODbL-1.0`), un
  nom complet et une URL permanente. Porté par `License.spdxId`.
- [Creative Commons](https://creativecommons.org/licenses/) - famille de
  licences ouvertes la plus courante pour les données environnementales
  publiées. Source des URLs de `License.url`.
- [Helmholtz SMS-CV Licenses](https://sms-cv.helmholtz.cloud/sms/cv/) -
  vocabulaire contrôlé de licences maintenu pour la gestion de métadonnées
  capteurs Earth & Environment ; référence utile pour cadrer le périmètre
  licences d'un système d'observation environnemental.
- [DCAT dct:license](https://www.w3.org/TR/vocab-dcat-3/#Property:resource_license)
  - propriété du vocabulaire de catalogue W3C pour exposer la licence d'une
  ressource ; cible d'export pour l'interopérabilité avec les catalogues
  (Theia/OZCAR, ENVRI-Hub).

*Utilisé par* :<br>
Datastream (license), TimeSeries (license), TransformedTimeSeries (license), Bundle (license)

*Note* :
- Table de référence peuplée et gérée par les administrateurs BDOH.
- `code` est le slug interne BDOH (kebab-case, pour les URLs) ; `spdxId` est
  l'identifiant standard SPDX (casse canonique, pour l'interopérabilité). Les
  deux coexistent : `code='cc-by-4.0'`, `spdxId='CC-BY-4.0'`.
- `spdxId` est null pour les licences sans équivalent SPDX (ex : licence
  contractuelle propriétaire spécifique).
- Toute licence porte un niveau d'ouverture : `isOpen=true` pour CC-BY, ODbL...,
  `isOpen=false` pour une licence contractuelle fermée ou restreinte. Le
  mécanisme d'accès restreint (liens temporaires, tokens...) sera défini
  ultérieurement et n'affecte pas cette table.
- Obligatoire sur tous les flux de données.

| Champ        | Cardinalité | Définition                                   | Valeurs possibles                                |
|--------------|-------------|----------------------------------------------|--------------------------------------------------|
| `id`         | 1           | Identifiant technique, clé primaire          | uuid                                             |
| `code`       | 1           | Slug interne BDOH (kebab-case, unique)       | "cc-by-4.0" \| "odbl-1.0" \| "proprietary-inrae" |
| `spdxId`     | 0..1        | Identifiant SPDX canonique (casse sensible)  | "CC-BY-4.0" \| "ODbL-1.0" \| null                |
| `name`       | 1           | Nom complet de la licence                    | "Creative Commons Attribution 4.0 International" |
| `url`        | 0..1        | URL vers le texte officiel de la licence     | "https://creativecommons.org/licenses/by/4.0/"   |
| `isOpen`     | 1           | Licence ouverte (true) ou fermée/restreinte  | true \| false                                    |
| `archivedAt` | 0..1        | Horodatage d'archivage logique               | null \| "2024-01-01T00:00:00Z"                   |

---

## Identifier
> Code externe vers un référentiel tiers (SANDRE, TheiaOZCAR, WIGOS...).

*Aligné avec* :
- [ODM2 ExternalIdentifiers](https://github.com/ODM2/ODM2/blob/master/doc/ODM2Docs/ext_externalidentifiers.md)
  - extension ODM2 dédiée aux identifiants externes (PIDs) attachés aux entités.
  Structure conceptuelle directement reprise (codeType, codeSource).
- [schema.org/identifier](https://schema.org/identifier) - propriété générique
  pour attacher un identifiant externe à toute entité web (PropertyValue).
- [INSPIRE ExternalObjectIdentifier](https://inspire.ec.europa.eu/data-model/approved/r4618-ir/html/index.htm?goto=2:1:5:1:7062)
  - type INSPIRE pour les identifiants persistants sur les objets spatiaux,
  pertinent pour l'interopérabilité avec les portails géographiques européens.

*Utilisé par* :<br>
Observatory, Site, Station, System, TimeSeries, Person, Organization, Specimen, Property, Project (via resourceType + resourceId) 

*Note* : 
- Permet autant de PIDs que nécessaire sur n'importe quelle ressource.
- Les URIs de thésaurus (TheiaOZCAR, ODM2...) vont dans Keyword.uri, pas ici - Identifier est réservé aux PIDs de ressources réelles.

| Champ          | Cardinalité | Définition                          | Valeurs possibles                                                                |
|----------------|-------------|-------------------------------------|----------------------------------------------------------------------------------|
| `id`           | 1           | Identifiant technique, clé primaire | uuid                                                                             |
| `code`         | 1           | Valeur de l'identifiant             | "V3015810" \| "0000-0001-1234-1234" \| "0-20000-0-06610"                         |
| `codeType`     | 1           | Type d'identifiant                  | `doi` \| `orcid` \| `ror` \| `sandre` \| `wigos` \| `igsn` \| `pidinst` \| `other` |
| `codeSource`   | 1           | Système ou organisme émetteur       | "SANDRE" \| "TheiaOZCAR" \| "NERC" \| "DataCite" \| "ROR" \| "PIDINST"           |
| `resourceType` | 1           | Type de ressource ciblée            | `Observatory` \| `Site` \| `Station` \| `System` \| `TimeSeries` \| `Person` \| `Organization` \| `Specimen` \| `Property` \| `Project` \| `TransferFunction` |
| `resourceId`   | 1           | UUID de la ressource ciblée         | uuid                                                                             |


<div class="page-break"></div>

# 3. GÉOGRAPHIE

## Location
> Géométrie pure d'un objet (point GPS, polygone...) sans dimension temporelle.

*Aligné avec* :
- [OGC STA 1.1 Location](https://docs.ogc.org/is/18-088/18-088.html) - entité STA
  qui localise un Thing ; BDOH reprend le principe d'une localisation comme
  entité distincte (et non comme champ de coordonnées inline).
- [GeoJSON (RFC 7946)](https://datatracker.ietf.org/doc/html/rfc7946) - format
  d'encodage de la géométrie (`geometry` Point, LineString, Polygon).
- [ISO 19107 Spatial Schema](https://www.iso.org/standard/66175.html) - modèle
  conceptuel de référence pour la représentation des géométries spatiales.

*Utilisé par* :<br>
HistoricalLocation (location), Observatory (location courante), Site (location courante), Station (location courante), Deployment (location), Specimen (location)

*Note* : 
- Décrit uniquement la géométrie, sans dimension temporelle.
- La temporalité est portée par HistoricalLocation.
- Partagée entre couche IoT STA et backend BDOH - même UUID.

| Champ          | Cardinalité | Définition                          | Valeurs possibles                    |
|----------------|-------------|-------------------------------------|--------------------------------------|
| `id`           | 1           | Identifiant technique, clé primaire | uuid                                 |
| `encodingType` | 1           | Type d'encodage (conformité STA)    | "application/geo+json"               |
| `geometry`     | 1           | Géométrie GeoJSON                   | `Point` \| `Polygon` \| `LineString` |
| `crs`          | 1           | Système de référence de coordonnées | "EPSG:4326" \| "EPSG:2154"           |
| `description`  | 0..1        | Description libre                   |                                      |
| `archivedAt`   | 0..1        | Horodatage d'archivage logique      | null \| "2024-01-01T00:00:00Z"       |

---

## HistoricalLocation
> Succession des positions géographiques d'une ressource dans le temps - une seule position active à la fois.

*Aligné avec* :
- [OGC STA 1.1 HistoricalLocation](https://docs.ogc.org/is/18-088/18-088.html)
  - entité STA qui trace les positions successives d'un Thing dans le temps.
  BDOH généralise le principe à plusieurs types de ressources (Observatory,
  Site, Station, Deployment) via le pattern resourceType + resourceId.

*Utilisé par* :<br>
Observatory, Site, Station, Deployment (via resourceType + resourceId)

*Note* :
- Trace les changements de position géographique événementiels dans le temps.
- Réservé aux changements discrets et rares (quelques fois dans la vie de la ressource) : station déplacée après une crue, bouée repositionnée, drone en position de départ.
- Pour une position qui varie en continu (trajectoire drone, profileur autonome), utiliser une TimeSeries dédiée (property=position, aggregationStatistic=instantaneous).
- Règle de décision : si la position change de façon événementielle → HistoricalLocation.
- Si la position change à chaque pas de temps → TimeSeries de position.
- Les ressources gardent un lien direct vers leur location courante pour les requêtes simples.

| Champ          | Cardinalité | Définition                          | Valeurs possibles                                    |
|----------------|-------------|-------------------------------------|------------------------------------------------------|
| `id`           | 1           | Identifiant technique, clé primaire | uuid                                                 |
| `location`     | 1 →Loc      | Géométrie associée                  | → Location                                           |
| `resourceType` | 1           | Type de ressource ciblée            | `Observatory` \| `Site` \| `Station` \| `Deployment` |
| `resourceId`   | 1           | UUID de la ressource ciblée         | uuid                                                 |
| `validFrom`    | 1           | Début de validité                   | "2014-04-17T00:00:00Z"                               |
| `validTo`      | 0..1        | Fin de validité, null si courant    | null                                                 |

---

## FeatureOfInterest
> Entité réelle du monde observée - la rivière, la nappe, le sol, l'atmosphère.

*Aligné avec* :
- [OGC STA 1.1 FeatureOfInterest](https://docs.ogc.org/is/18-088/18-088.html)
  - dans STA, ce qui est réellement observé par une Observation (souvent distinct
  du capteur qui observe).
- [OGC OMS / ISO 19156:2023](https://docs.ogc.org/as/20-082r4/20-082r4.html)
  - le concept de "ultimate feature of interest" (l'entité du monde réel dont
  on estime une propriété) structure la distinction BDOH entre ce qui observe
  et ce qui est observé.

*Utilisé par* :<br>
ValidatedObservation (featureOfInterest), ControlObservation (featureOfInterest), Station (featureOfInterest - FOI ultime), TimeSeries (featureOfInterest - FOI proximate optionnelle), TransformedTimeSeries (featureOfInterest - FOI proximate optionnelle), Specimen (foi - FOI proximate du prélèvement)

*Relations inverses* :<br>
Identifier

*Keywords attendus (voir KeywordRequirement)* :<br>
- featureType : river, lake, groundwater, soil, atmosphere, wetland
	   
*Note* : 
- Entité réelle du monde observée - cours d'eau, nappe, sol, atmosphère.
- Distincte de Specimen (acte de prélèvement) - la distinction couvre les mêmes cas que Proximate/UltimateFOI de OMS sans l'adopter.
- Convention code : {nom-court-entité}-{type} ex: "mercier-eau-surf"

| Champ          | Cardinalité | Définition                          | Valeurs possibles                    |
|----------------|-------------|-------------------------------------|--------------------------------------|
| `id`           | 1           | Identifiant technique, clé primaire | uuid                                 |
| `code`         | 1           | Code court unique, curateur         | "mercier-eau-surf" \| "yzeron-bv"    |
| `name`         | 1           | Nom de l'entité observée            | "Eau de surface du Mercier"          |
| `description`  | 0..1        | Description libre                   |                                      |
| `encodingType` | 1           | Type d'encodage (conformité STA)    | "application/geo+json"               |
| `geometry`     | 1           | Emprise GeoJSON de l'entité         | `Point` \| `Polygon` \| `LineString` |
| `archivedAt`   | 0..1        | Horodatage d'archivage logique      | null \| "2024-01-01T00:00:00Z"       |


<div class="page-break"></div>

# 4. MONDE PHYSIQUE

## Observatory
> Réseau d'observatoires environnementaux - entité racine du modèle.

*Aligné avec* :
- [OGC STA 1.1 Thing](https://docs.ogc.org/is/18-088/18-088.html) - Observatory
  correspond à un Thing STA enrichi ; les métadonnées spécifiques sont portées
  selon le profil STAMPLATE.
- [STAMPLATE Schema](https://zenodo.org/records/17241283) - profil de métadonnées
  STA pour l'environnement (Helmholtz). Standardise les champs `properties` d'un
  Thing, dont la notion d'appartenance à un programme/infrastructure.
- [schema.org/ResearchProject](https://schema.org/ResearchProject) - vocabulaire
  web pour la sérialisation JSON-LD d'un observatoire comme projet de recherche.
- [ISO 19115 MD_DataIdentification](https://www.iso.org/standard/53798.html)
  - section d'identification d'une ressource en métadonnées géographiques
  (titre, résumé, étendue), reprise pour décrire un observatoire.

*Utilisé par* :<br>
Site (FK observatory), Bundle (FK observatory). Cible d'ancrage possible (anchorType='Observatory') pour Datastream, TimeSeries, TransformedTimeSeries, TransferFunction, TransferFunctionSet.

*Relations inverses (requêter par resourceType='Observatory')* :<br>
HistoricalLocation, HistoricalProject, Responsibility, Identifier, Memory, KeywordAssignment

*Note* : 
- Entité racine du réseau.
- Correspond à un Thing STA avec properties enrichies (STAMPLATE).

| Champ                | Cardinalité | Définition                          | Valeurs possibles                        |
|----------------------|-------------|-------------------------------------|------------------------------------------|
| `id`                 | 1           | Identifiant technique, clé primaire | uuid                                     |
| `code`               | 1           | Code court unique, curateur         | "yzr"                                    |
| `name`               | 1           | Nom du réseau                       | "Observatoire de l'Yzeron"               |
| `description`        | 0..1        | Description scientifique            |                                          |
| `location`           | 1 →Loc      | Emprise géographique courante       | → Location                               |
| `startDate`          | 1           | Date de début                       | "2010-01-01"                             |
| `endDate`            | 0..1        | Date de fin, null si actif          | null                                     |
| `status`             | 1           | État de l'observatoire              | `active` \| `inactive` \| `discontinued` |
| `url`                | 0..1        | Site web du réseau                  | "https://..."                            |

---

## Site
> Subdivision géographique d'un observatoire (bassin versant, lac, aquifère...).

*Aligné avec* :
- [OGC STA 1.1 Thing](https://docs.ogc.org/is/18-088/18-088.html) - Site correspond
  à un regroupement géographique sous un Observatory, modélisé comme un Thing STA.
- [SANDRE Référentiel hydrométrique - Site hydrométrique](https://id.eaufrance.fr/ddd/hyd/2.4)
  - le SANDRE structure un "site hydrométrique" comme un lieu contenant plusieurs
  stations : exactement la relation Site → Station de BDOH.
- [INSPIRE EnvironmentalMonitoringFacility](https://inspire.ec.europa.eu/Themes/121/2892)
  - thème INSPIRE des installations de surveillance environnementale, pertinent
  pour l'interopérabilité géographique européenne.

*Utilisé par* :<br>
Station (FK site). Cible d'ancrage possible (anchorType='Site') pour Deployment, Datastream, TimeSeries, TransformedTimeSeries, TransferFunction, TransferFunctionSet, Specimen.

*Relations inverses (requêter par resourceType='Site')* :<br>
HistoricalLocation, HistoricalProject, Responsibility, Identifier, Memory, KeywordAssignment

*Keywords attendus (voir KeywordRequirement)* :<br>
- siteType : watershed, lake, wetland, aquifer, catchment, estuary
	   
*Note* : 
- Subdivision géographique d'un Observatory.
- code unique par Observatory.

| Champ         | Cardinalité | Définition                          | Valeurs possibles              |
|---------------|-------------|-------------------------------------|--------------------------------|
| `id`          | 1           | Identifiant technique, clé primaire | uuid                           |
| `code`        | 1           | Code court unique                   | "yzr-mer"                      |
| `name`        | 1           | Nom du site                         | "Bassin versant du Mercier"    |
| `description` | 0..1        | Description libre                   |                                |
| `Observatory` | 1 →Obs      | Observatoire parent                 | → Observatory                  |
| `location`    | 1 →Loc      | Géométrie courante                  | → Location                     |
| `area`        | 0..1        | Superficie en km²                   | "245.3"                        |
| `archivedAt`  | 0..1        | Horodatage d'archivage logique      | null \| "2024-01-01T00:00:00Z" |

---

## Station
> Point de mesure institutionnel - ancrage administratif et géographique permanent avec code SANDRE.

*Aligné avec* :
- [OGC STA 1.1 Thing](https://docs.ogc.org/is/18-088/18-088.html) - Station est
  le Thing STA au sens le plus strict : le point précis où l'instrumentation
  est déployée.
- [STAMPLATE Schema](https://zenodo.org/records/17241283) - profil qui standardise
  les `properties` d'un Thing (type de station, statut, métadonnées de site).
- [SANDRE Référentiel hydrométrique - Station hydrométrique](https://id.eaufrance.fr/ddd/hyd/2.4)
  - définit la "station hydrométrique" comme le lieu de mesure équipé sous un
  site. Référence pour les codes station français et la nomenclature des types.
- [WMO - station hydrologique](https://community.wmo.int/en/activity-areas/hydrology-and-water-resources)
  - cadre de l'Organisation météorologique mondiale pour les stations
  d'observation hydrologique, pertinent pour l'alignement international.

*Utilisé par* :<br>
Cible d'ancrage possible (anchorType='Station') pour Deployment, Datastream, TimeSeries, TransformedTimeSeries, TransferFunction, TransferFunctionSet, Specimen.

*Relations inverses (requêter par resourceType='Station')* :<br>
HistoricalLocation, HistoricalProject, Responsibility, Identifier, Memory, KeywordAssignment, Deployment (anchorType='Station', anchorId)

*Keywords attendus (voir KeywordRequirement)* :<br>
- stationType : stream_gage, weather_station, well, soil_pit, lake_station, tide_gage
	   
*Note* : 
- Objet institutionnel et géographique - le "Thing" STA.
- Existe indépendamment de tout équipement actif.
- A un code SANDRE, une continuité historique sur 50 ans, des responsabilités.
- Les Systems physiques sont déployés sur elle via Deployment (récursif).
- Distinct de Site (bassin versant, zone géographique large).
- code unique par Site.

| Champ                | Cardinalité    | Définition                             | Valeurs possibles                        |
|----------------------|----------------|----------------------------------------|------------------------------------------|
| `id`                 | 1              | Identifiant technique, clé primaire    | uuid                                     |
| `code`               | 1              | Code court unique                      | "yzr-mer-d610"                           |
| `name`               | 1              | Nom de la station                      | "Mercier au pont D610"                   |
| `description`        | 0..1           | Description libre                      |                                          |
| `Site`               | 1 →Site        | Site parent                            | → Site                                   |
| `location`           | 1 →Loc         | Position GPS courante                  | → Location                               |
| `elevation`          | 0..1           | Altitude en mètres (référentiel local) | "312.5"                                  |
| `featureOfInterest`  | 0..1 →FOI      | FOI ultime - entité réelle observée    | → FeatureOfInterest                      |
| `installationDate`   | 0..1           | Date d'installation                    | "1997-01-14"                             |
| `status`             | 1              | État de la station                     | `active` \| `inactive` \| `discontinued` |

---

```
Architecture instrumentation - System + Deployment récursif

Note API : l'API STA expose /Sensors comme vue filtrée
           System WHERE systemType='sensor'. Le client STA voit
           des Sensors conformes. BDOH stocke des Systems.

Cas station fixe avec capteur individuel :

  Station (ancrage institutionnel permanent, code SANDRE)
    └── Deployment [2020-...] anchorType='Station'
          └── System "Centrale YZR" (systemType=platform)
                └── Deployment [2020-2022]
                      └── System "Sonde hauteur OTT v1" (systemType=sensor)
                            └── Datastream A
                                  └── TimeSeriesSource [2020-2022] → TimeSeries "Hauteur D610"
                └── Deployment [2022-...]
                      └── System "Sonde hauteur OTT v2" (systemType=sensor)
                            └── Datastream B
                                  └── TimeSeriesSource [2022-...] → TimeSeries "Hauteur D610"

Cas bouée de lac (Platform multi-capteurs) :

  Station (bord du lac)
    └── Deployment [2020-...] anchorType='Station'
          └── System "Bouée lac nord" (systemType=platform)
                ├── Deployment [2020-...] deploymentDepth=-0.5m
                │     └── System "Sonde T YSI" (systemType=sensor)
                │           └── Datastream → TimeSeriesSource → TimeSeries "T lac 0.5m"
                └── Deployment [2020-...] deploymentDepth=-1.5m
                      └── System "Sonde O2 YSI" (systemType=sensor)
                            └── Datastream → TimeSeriesSource → TimeSeries "O2 lac 1.5m"

Cas drone (campagne mobile) :

  Site "Bassin versant Yzeron"
    └── Deployment [2024-05-10/12] anchorType='Site'
          location propre via HistoricalLocation (trajectoire)
          └── System "Bateau drone Yzeron" (systemType=platform)
                └── Deployment [2024-05-10/12]
                      └── System "Sonde conductivité" (systemType=sensor)
                            └── Datastream (anchorType='Site', anchorId=uuid_site)
                                  └── TimeSeriesSource → TimeSeries "Cond surface"
                                        (anchorType='Site', anchorId=uuid_site)
```

---

## System
> Objet physique traçable impliqué dans la production de données - capteur, plateforme ou équipement.

*Aligné avec* :
- [OGC API - Connected Systems](https://ogcapi.ogc.org/connectedsystems/) -
  standard OGC (Parts 1 & 2, approuvés 2026) dont la ressource "System" unifie
  capteurs, plateformes et équipements en une entité unique. C'est le modèle
  qui justifie la fusion BDOH de Sensor/Platform/Equipment en `System` (ADR-037).
- [W3C/OGC SSN - System](https://www.w3.org/TR/vocab-ssn-2023/)
  - ontologie sémantique sous-jacente : un System est une unité d'observation
  qui peut contenir des sous-systèmes.
- [OGC STA 1.1 Sensor](https://docs.ogc.org/is/18-088/18-088.html) - dans l'API
  STA exposée, un System de type `sensor` apparaît comme un Sensor.
- [ODM2 Equipment](https://github.com/ODM2/ODM2/blob/master/doc/ODM2Docs/ext_equipment.md)
  - extension ODM2 dont la notion d'équipement (modèle, numéro de série,
  fabricant) est reprise dans les champs de System.
- [Helmholtz SMS](https://helmholtz.software/software/sensor-management-system)
  - système de gestion de métadonnées capteurs : référence d'implémentation
  pour la gestion du cycle de vie d'un instrument.

*Utilisé par* :<br>
Deployment (system), Datastream (system), ControlObservation (system)

*Relations inverses (requêter par resourceType='System')* :<br>
Memory, Responsibility, Identifier, KeywordAssignment

*Keywords attendus (voir KeywordRequirement)* :<br>
- sensor : icp_ms, spectrophotometer, hplc, probe, autoanalyzer, datalogger
- platform : buoy, vertical_chain, drone, multi_probe, weather_station, mooring
- equipment : bottle, pump, autosampler, corer, syringe, filter_holder

*Note* : 
- Entité physique unique avec identité propre, indépendante de son contexte de déploiement.
- systemType discrimine le rôle - pattern TPC, même philosophie que agentType.
- Contraintes CHECK PostgreSQL par systemType :
  * sensor - encodingType obligatoire
  * equipment - calibrationDate, encodingType, metadata non pertinents (null)
  * platform - material, volume, preservationMethod non pertinents (null)
- API STA : /Sensors = vue System WHERE systemType='sensor'.
- code unique globalement.

| Champ                    | Cardinalité | Définition                             | Valeurs possibles                     |
|--------------------------|-------------|----------------------------------------|---------------------------------------|
| `id`                     | 1           | Identifiant technique, clé primaire    | uuid                                  |
| `code`                   | 1           | Slug unique globalement                | "ott-pls500-sn2023-00412"             |
| `name`                   | 1           | Nom descriptif                         | "Sonde OTT PLS 500"                   |
| `systemType`             | 1           | Discriminant TPC                       | `sensor` \| `platform` \| `equipment` |
| `make`                   | 0..1        | Fabricant                              | "OTT" \| "YSI" \| "Nalgene"           |
| `model`                  | 0..1        | Modèle                                 | "PLS 500"                             |
| `serialNumber`           | 0..1        | Numéro de série fabricant              | "SN-2023/00412 Rev.B"                 |
| `calibrationDate`        | 0..1        | Date dernière calibration (sensor)     | "2024-01-15"                          |
| `calibrationCertificate` | 0..1        | Référence certificat (sensor)          | "CERT-2024-ICP-001"                   |
| `encodingType`           | 0..1        | Type encodage STA (sensor obligatoire) | "application/pdf" \| URI              |
| `metadata`               | 0..1        | URI fiche technique (sensor)           | "https://..."                         |
| `material`               | 0..1        | Matériau de construction (equipment)   | "HDPE" \| "verre ambré" \| "inox"     |
| `volume`                 | 0..1        | Contenance en litres (equipment)       | "1.0"                                 |
| `preservationMethod`     | 0..1        | Méthode de conservation (equipment)    | "acidification HNO3" \| "congélation" |
| `status`                 | 1           | État de l'objet physique               | `active` \| `inactive` \| `retired`   |

---

## Deployment
> Acte de déployer un System dans un contexte spatial et temporel - récursif, universel.

*Aligné avec* :
- [OGC API - Connected Systems](https://ogcapi.ogc.org/connectedsystems/) -
  la ressource "Deployment" du CS API est récursive (un déploiement peut avoir
  des sous-déploiements). BDOH reprend ce modèle pour son Deployment universel
  (ADR-037).
- [W3C/OGC SSN - Deployment](https://www.w3.org/TR/vocab-ssn-2023/)
  - concept ontologique du déploiement d'un ou plusieurs Systems pour un objectif
  donné, à un lieu et une période donnés.
- [OGC SensorML 3.0](https://docs.ogc.org/DRAFTS/23-000.html) - encodage qui
  formalise les propriétés de déploiement d'un système d'observation.

*Utilisé par* :<br>
System (via deployment.system)

*Relations inverses (requêter par resourceType='Deployment')* :<br>
Memory, Identifier, HistoricalLocation

*Note* : 
- Trace toutes les relations physiques entre Systems, et entre Systems et leur ancrage.
- Récursif via parentDeployment - un capteur déployé sur une bouée déployée sur une station forme une hiérarchie de Deployments imbriqués.
- anchorType + anchorId : pattern TPC, ancrage sur Station ou Site.
- deploymentDepth : profondeur nominale du System dans ce Deployment.
- Si le System est déplacé sur un autre ancrage, c'est un nouveau Deployment.
- Position dans le temps - deux mécanismes selon la nature du changement :
  * HistoricalLocation : position événementielle (repositionnement ponctuel, dérive de bouée).
  * TimeSeries de position : position continue (trajectoire drone, profileur autonome) - même mécanisme qu'une série de mesure, property=position, aggregationStatistic=instantaneous.

| Champ              | Cardinalité | Définition                                       | Valeurs possibles                                              |
|--------------------|-------------|--------------------------------------------------|----------------------------------------------------------------|
| `id`               | 1           | Identifiant technique, clé primaire              | uuid                                                           |
| `code`             | 1           | Slug unique globalement                          | "dep-lac-nord-bouee-2020"                                      |
| `name`             | 1           | Nom du déploiement                               | "Déploiement bouée lac nord 2020"                              |
| `system`           | 1 →Sys      | System déployé                                   | → System                                                       |
| `parentDeployment` | 0..1 →Dep   | Déploiement parent (récursif)                    | → Deployment                                                   |
| `anchorType`       | 0..1        | Type d'ancrage territorial (null si autonome)    | `Station` \| `Site`                                            |
| `anchorId`         | 0..1        | UUID de la Station ou du Site                    | uuid                                                           |
| `location`         | 0..1 →Loc   | Position propre si différente de l'ancre         | → Location                                                     |
| `deploymentDepth`  | 0..1        | Profondeur nominale du System dans ce Deployment | "-1.5"                                                         |
| `depthReference`   | 0..1        | Référence de profondeur                          | `surface_relative` \| `bottom_relative` \| `absolute_elevation` |
| `validFrom`        | 1           | Début du déploiement                             | "2020-06-01T00:00:00Z"                                         |
| `validTo`          | 0..1        | Fin, null si actif                               | null                                                           |
| `status`           | 1           | État du déploiement                              | `active` \| `inactive` \| `removed`                            |


<div class="page-break"></div>

# 5. MONDE IoT

## Datastream
> Flux de données brutes issu d'un unique System de type sensor - couche IoT STA.

*Aligné avec* :
- [OGC STA 1.1 Datastream](https://docs.ogc.org/is/18-088/18-088.html) - entité
  STA qui regroupe les Observations partageant une même ObservedProperty et un
  même Sensor. Datastream BDOH correspond directement à ce concept.
- [FROST-Server](https://github.com/FraunhoferIOSB/FROST-Server) - implémentation
  de référence open-source de STA (Fraunhofer IOSB). Cible d'interopérabilité
  pour la couche IoT de BDOH.
- [HydroServer](https://hydroserver2.github.io/hydroserver/) - implémentation
  de référence côté données hydrologiques, qui informe le choix de garder
  Datastream comme couche d'acquisition distincte de la couche métier.

*Utilisé par* :<br>
TimeSeriesSource (datastream), Observation (datastream)

*Note* : 
- Flux de données brutes pour un unique System(sensor) + ObservedProperty.
- Un changement de capteur crée un nouveau Datastream (règle métrologique et STA).
- Plusieurs Datastreams successifs → une TimeSeries via TimeSeriesSource.
- BDOH garde unitOfMeasurement comme FK vers Unit (choix HydroServer/USGS).
- API STA : system → Sensor dans les réponses /Datastreams.
- FOI absente de la couche IoT - portée par Station et TimeSeries (couche métier).
- anchorType + anchorId : pattern TPC pour le rattachement géographique.
- Cas station fixe : anchorType='Station'. Cas drone : anchorType='Site'.
- Doit être cohérent avec l'ancrage du Deployment du System associé.
- acquisitionType : mode d'acquisition - sensor_continuous ou lab_sample.
- aggregationStatistic : nature métrologique de la valeur, aligné ODM2.
  * sporadic = pas de temps irrégulier (crue), observationFrequency null.
  * instantaneous = valeur ponctuelle, phenomenonTimeEnd null.
  * Autres = valeur intégrée sur intervalle, phenomenonTimeEnd renseigné.
- Plage temporelle couverte : non stockée. `phenomenonTimeStart` et `phenomenonTimeEnd` du flux sont calculés à la demande (MIN/MAX du phenomenonTime des Observations), exposés en lecture seule par l'API. Recomposés en l'intervalle `phenomenonTime` à l'export STA.

| Champ                    | Cardinalité | Définition                                | Valeurs possibles                                               |
|--------------------------|-------------|-------------------------------------------|-----------------------------------------------------------------|
| `id`                     | 1           | Identifiant technique, clé primaire       | uuid                                                            |
| `name`                   | 1           | Nom du flux                               | "Hauteur d'eau - Mercier D610 - OTT PLS 500"                    |
| `description`            | 0..1        | Description libre                         |                                                                 |
| `unitOfMeasurement`      | 1 →Unit     | Unité de mesure                           | → Unit                                                          |
| `anchorType`             | 1           | Type d'ancrage géographique               | `Observatory` \| `Site` \| `Station`                            |
| `anchorId`               | 1           | UUID de l'Observatory, Site ou Station    | uuid                                                            |
| `system`                 | 1 →Sys      | Capteur source (systemType=sensor)        | → System                                                        |
| `property`               | 1 →Prop     | Variable mesurée (= ObservedProperty STA) | → Property                                                      |
| `procedureObservation`   | 0..1 →Proc  | Protocole de mesure                       | → Procedure (type=observation)                                  |
| `acquisitionType`        | 1           | Mode d'acquisition des données            | `sensor_continuous` \| `lab_sample`                             |
| `aggregationStatistic`   | 1           | Nature métrologique de la valeur          | `instantaneous` \| `average` \| `cumulative` \| `maximum` \| `minimum` \| `variance` \| `standard_deviation` \| `sporadic` |
| `observationFrequency`   | 0..1        | Fréquence nominale (ISO 8601)             | "PT15M" \| "PT1H" - null si aggregationStatistic=sporadic       |
| `status`                 | 1           | État du flux                              | `active` \| `inactive` \| `closed`                              |
| `license`                | 1 →Lic      | Licence des données                       | → License                                                       |
| `transmissionMode`       | 0..1        | Mode d'arrivée des données dans BDOH      | `auto` \| `manual`                                              |

---

## ObservationBatch
> Import groupé de données brutes - trace qui a déposé quel lot, quand et depuis quelle source.

*Aligné avec* :
- [W3C PROV-O Activity](https://www.w3.org/TR/prov-o/#Activity) - un ObservationBatch
  est une activité PROV : un acte d'import daté, attribué à un agent, qui produit
  un ensemble d'Observations.
- [ODM2 Actions](https://github.com/ODM2/ODM2/blob/master/doc/ODM2Docs/core_actions.md)
  - dans ODM2, toute production de données passe par une Action ; ObservationBatch
  reprend ce principe pour tracer l'origine d'un lot d'observations.

*Utilisé par* :<br>
Observation (batch)

*Note* : 
- Optionnel - un capteur télétransmis en continu ne crée pas de batch.
- Nécessaire quand un technicien importe manuellement des données récupérées sur une centrale d'acquisition terrain non connectée.
- Analogue à ValidationBatch pour la couche IoT.
- agentType + agentId : pattern TPC - peut être un technicien (`Person`) ou un service d'import automatique (`Machine`).

| Champ         | Cardinalité | Définition                                 | Valeurs possibles                    |
|---------------|-------------|--------------------------------------------|--------------------------------------|
| `id`          | 1           | Identifiant technique, clé primaire        | uuid                                 |
| `datastream`  | 1 →DS       | Flux de données cible                      | → Datastream                         |
| `importedAt`  | 1           | Date et heure de l'import                  | "2024-04-01T08:00:00Z"               |
| `agentType`   | 0..1        | Type d'agent ayant réalisé l'import        | `Person` \| `Machine`                |
| `agentId`     | 0..1        | UUID de la Person ou Machine               | uuid                                 |
| `source`      | 0..1        | Origine des données (centrale, fichier...) | "centrale YZR-D610" \| "https://..." |
| `status`      | 1           | État de l'import                           | `pending` \| `done` \| `failed`      |
| `comment`     | 0..1        | Commentaire libre                          |                                      |

---

## Observation
> Valeur brute horodatée issue d'un Datastream - non validée, non corrigée.

*Aligné avec* :
- [OGC STA 1.1 Observation](https://docs.ogc.org/is/18-088/18-088.html) - dans
  STA, une Observation est l'acte de mesure produisant un résultat à un instant
  donné. Observation BDOH est la mesure brute issue du capteur.
- [OGC OMS / ISO 19156:2023](https://docs.ogc.org/as/20-082r4/20-082r4.html)
  - modèle conceptuel sous-jacent : l'observation comme estimation d'une
  propriété d'un feature of interest.
- [FROST-Server](https://github.com/FraunhoferIOSB/FROST-Server) - implémentation
  de référence pour le stockage et l'accès aux observations STA.

*Utilisé par* :<br>
Datastream (observations), ObservationBatch (datastream)

*Note* : 
- Valeur brute horodatée - raw, sans qualityFlag, sans validation.
- La validation est dans ValidatedObservation du backend BDOH.
- Le lien se fait via phenomenonTimeStart + datastream → TimeSeriesSource.
- FOI absente - portée par Station et TimeSeries (couche métier).
- phenomenonTimeEnd null si instantaneous ou sporadic.
- phenomenonTimeEnd obligatoire si average, cumulative, maximum, minimum, variance, standard_deviation (contrainte applicative).
- phenomenonTime vs resultTime : `phenomenonTime` est le moment du phénomène observé (prélèvement, mesure terrain) ; `resultTime` est le moment où la valeur a été produite. Pour un capteur, les deux coïncident. Pour une analyse de laboratoire, ils diffèrent : `phenomenonTime` = prélèvement, `resultTime` = analyse. `resultTime` est null si l'information n'est pas disponible.
- Colonne de partitionnement TimescaleDB : phenomenonTimeStart.

| Champ                 | Cardinalité | Définition                               | Valeurs possibles              |
|-----------------------|-------------|------------------------------------------|--------------------------------|
| `id`                  | 1           | Identifiant technique, clé primaire      | uuid                           |
| `batch`               | 0..1 →OB    | Batch d'import parent si saisie manuelle | → ObservationBatch             |
| `phenomenonTimeStart` | 1           | Début de la période du phénomène         | "2024-03-15T09:30:00Z"         |
| `phenomenonTimeEnd`   | 0..1        | Fin de la période, null si instantané    | "2024-03-15T10:00:00Z" \| null |
| `resultTime`          | 0..1        | Instant de production du résultat        | "2024-03-15T09:30:05Z" \| null |
| `result`              | 1           | Valeur brute mesurée                     | 4.523                          |
| `datastream`          | 1 →DS       | Flux de données parent                   | → Datastream                   |
| `specimen`            | 0..1 →Spec  | Prélèvement terrain associé              | → Specimen                     |


<div class="page-break"></div>

# 6. COUTURE

## TimeSeriesSource
> Lien temporel et spatial entre une TimeSeries et ses Datastreams successifs - trace les changements de capteur et de position nominale.

*Aligné avec* :
- [ODM2 Datasets](https://github.com/ODM2/ODM2/blob/master/doc/ODM2Docs/core_datasets.md)
  - mécanisme ODM2 de regroupement logique de résultats ; TimeSeriesSource
  joue un rôle analogue de liaison entre une couche d'acquisition et une couche
  métier.
- [HydroServer](https://hydroserver2.github.io/hydroserver/) - implémentation de
  référence dont l'articulation entre flux brut et série publiée a informé la
  conception de cette couture (ADR-036).
- [OGC API - Connected Systems](https://ogcapi.ogc.org/connectedsystems/) - le
  CS API distingue lui aussi données dynamiques brutes et features stables,
  séparation que TimeSeriesSource matérialise côté BDOH.

*Utilisé par* :<br>
TimeSeries (via timeSeries FK)

*Note* : 
- Lie une TimeSeries à ses Datastreams sources successifs dans le temps.
- Un changement de capteur = nouveau Datastream = nouvelle ligne ici.
- Couture entre le monde physique (System → Deployment → Datastream) et le monde analytique (TimeSeries → ValidatedObservation).
- La profondeur nominale du capteur est portée par le Deployment correspondant.
- Nommé d'après son rôle (la source d'une TimeSeries), et non avec le préfixe `Historical*` : cette table relie deux entités dans le temps, elle n'historise pas un attribut courant d'une ressource (voir Convention de lecture, pattern des associations datées). Anciens noms : TimeSeriesDatastream, puis HistoricalDatastream.

| Champ        | Cardinalité | Définition                          | Valeurs possibles      |
|--------------|-------------|-------------------------------------|------------------------|
| `id`         | 1           | Identifiant technique, clé primaire | uuid                   |
| `timeSeries` | 1 →TS       | Série parente                       | → TimeSeries           |
| `datastream` | 1 →DS       | Datastream source                   | → Datastream           |
| `validFrom`  | 1           | Début de la période                 | "1997-01-14T00:00:00Z" |
| `validTo`    | 0..1        | Fin de la période, null si courant  | null                   |


<div class="page-break"></div>

# 7. MONDE ANALYTIQUE

## TimeSeries
> Contrat analytique d'une série - variable et protocole fixes pour toute la durée.

*Utilisé par* :<br>
ValidatedObservation (timeSeries),
             TransformationBatch via transformationbatch_inputseries,
             TimeSeriesSource (timeSeries), HistoricalProject (resourceType=TimeSeries)
             ControlObservation (seriesType='TimeSeries', seriesId)

*Relations inverses (requêter par resourceType='TimeSeries')* :<br>
HistoricalProject, Responsibility, Identifier, Memory, KeywordAssignment

*Keywords attendus (voir KeywordRequirement)* :<br>
- samplingMedium (required) : surface_water, groundwater, atmosphere
		 
*Note* : 
- Porte tout ce qui est fixe et commun à toute la série.
- Contrat analytique garantissant la comparabilité de tous les points.
- anchorType + anchorId : pattern TPC - station dans le cas standard, site pour les séries de chimie sans station fixe ou campagnes mobiles.
- Le capteur courant se retrouve via TimeSeriesSource WHERE validTo IS NULL.
- FOI : featureOfInterest porte la FOI proximate si elle diffère de l'ancre.
- Règle de résolution API STA : TimeSeries.featureOfInterest si renseignée, sinon anchor.featureOfInterest.
- Une procédure de validation unique par série - plusieurs validations parallèles sur la même variable impliquent des TimeSeries distinctes.
- Plusieurs TimeSeries peuvent coexister sur la même station et la même variable sans hiérarchie - c'est le contexte scientifique qui désigne laquelle utiliser.
- OZCAR note que leur "Observation" pivot correspond à un Datastream STA.
- Plage temporelle couverte : non stockée. `phenomenonTimeStart` et `phenomenonTimeEnd` de la série sont calculés à la demande (MIN/MAX du phenomenonTime des ValidatedObservations), exposés en lecture seule par l'API. Recomposés en l'intervalle `phenomenonTime` à l'export STA.
- code unique par Station.

| Champ                  | Cardinalité | Définition                                    | Valeurs possibles                                            |
|------------------------|-------------|-----------------------------------------------|--------------------------------------------------------------|
| `id`                   | 1           | Identifiant technique, clé primaire           | uuid                                                         |
| `code`                 | 1           | Slug unique par ancre                         | "hea-wiski"                                                  |
| `name`                 | 1           | Nom lisible de la série                       | "Hauteur d'eau - Mercier au pont D610"                       |
| `description`          | 0..1        | Description libre                             |                                                              |
| `anchorType`           | 1           | Type d'ancrage géographique                   | `Observatory` \| `Site` \| `Station`                         |
| `anchorId`             | 1           | UUID de l'Observatory, Site ou Station        | uuid                                                         |
| `featureOfInterest`    | 0..1 →FOI   | FOI proximate si différente de l'ancre        | → FeatureOfInterest                                          |
| `property`             | 1 →Prop     | Variable mesurée                              | → Property                                                   |
| `unit`                 | 1 →Unit     | Unité de mesure                               | → Unit                                                       |
| `procedureObservation` | 1 →Proc     | Protocole analytique fixe pour toute la série | → Procedure (type=observation)                               |
| `procedureValidation`  | 1 →Proc     | Procédure de validation de cette série        | → Procedure (type=validation)                                |
| `procedureSampling`    | 0..1 →Proc  | Protocole de prélèvement standard (lab_sample)| → Procedure (type=sampling) - null si sensor_continuous      |
| `acquisitionType`      | 1           | Mode d'acquisition des données                | `sensor_continuous` \| `lab_sample`                          |
| `aggregationStatistic` | 1           | Nature métrologique de la valeur              | `instantaneous` \| `average` \| `cumulative` \| `maximum` \| `minimum` \| `variance` \| `standard_deviation` \| `sporadic` |
| `observationFrequency` | 0..1        | Fréquence nominale (ISO 8601)                 | "PT15M" \| "PT1H" - null si aggregationStatistic=sporadic    |
| `status`               | 1           | État de la série                              | `active` \| `inactive` \| `discontinued`                     |
| `license`              | 1 →Lic      | Licence des données                           | → License                                                    |
| `validationFrequency`  | 0..1        | Fréquence de validation auto (ISO 8601)       | "PT15M" \| "P1D" \| "P1W"                                    |
| `validationMode`       | 0..1        | Mode de validation                            | `auto` \| `manual`                                           |

---

## Vocabulaire qualityFlag
*Aligné avec* :
- [ODM2 controlled vocabulary](http://vocabulary.odm2.org/) - vocabulaires de
  qualification des résultats (ResultQualifier, qualityCode).
- [SANDRE - nomenclature qualité](https://www.sandre.eaufrance.fr/) - codes
  qualité du référentiel français (nomenclatures n°519 et suivantes).
- [OGC STA 1.1 - resultQuality](https://docs.ogc.org/is/18-088/18-088.html)
  - champ `resultQuality` d'une Observation STA.

Le tableau ci-dessous donne la correspondance exacte entre le vocabulaire
BDOH et chaque standard externe.

| BDOH      | ODM2    | SANDRE       | OGC resultQuality |
|-----------|---------|--------------|-------------------|
| `good`    | Good    | 1 - Bonne    | `good`            |
| `suspect` | Suspect | 3 - Douteuse | `suspect`         |
| `bad`     | Bad     | 4 - Mauvaise | `invalid`         |
| `missing` | Missing | - (lacune)   | `missing`         |

---

## ValidationBatch
> Session de validation groupée - qui a validé, quand, sur quelle période.

*Aligné avec* :
- [ODM2 Actions](https://github.com/ODM2/ODM2/blob/master/doc/ODM2Docs/core_actions.md)
  - une session de validation est une Action ODM2 de type validation, datée et
  attribuée à un acteur.
- [W3C PROV-O Activity](https://www.w3.org/TR/prov-o/#Activity) - ValidationBatch
  est une activité PROV qui transforme des observations brutes en observations
  validées (`used` / `wasGeneratedBy`).

*Utilisé par* :<br>
ValidatedObservation (validationBatch)

*Note* : 
- Groupe d'observations validées en une même session.
- Un batch couvre une fenêtre temporelle sur une TimeSeries.
- Alléger ValidatedObservation - les métadonnées de session sont ici, pas répétées sur chaque observation.
- agentType + agentId obligatoires (1) : pattern TPC - peut être un opérateur humain (`Person`) ou un pipeline de validation automatique (`Machine`).

| Champ              | Cardinalité | Définition                          | Valeurs possibles                        |
|--------------------|-------------|-------------------------------------|------------------------------------------|
| `id`               | 1           | Identifiant technique, clé primaire | uuid                                     |
| `timeSeries`       | 1 →TS       | Série validée                       | → TimeSeries                             |
| `periodStart`      | 1           | Début de la fenêtre validée         | "2024-01-01T00:00:00Z"                   |
| `periodEnd`        | 1           | Fin de la fenêtre validée           | "2024-03-31T23:59:59Z"                   |
| `agentType`        | 1           | Type d'agent ayant validé           | `Person` \| `Machine`                    |
| `agentId`          | 1           | UUID de la Person ou Machine        | uuid                                     |
| `validatedAt`      | 1           | Date d'exécution du batch           | "2024-04-01T08:00:00Z"                   |
| `validationLogUrl` | 0..1        | URI vers le log externe (Wiski...)  | "https://wiski.inrae.fr/log-2024-q1.csv" |
| `status`           | 1           | État du batch                       | `pending` \| `validated` \| `rejected`   |
| `comment`          | 0..1        | Commentaire libre sur la session    | "Validation Q1 2024 après crue janvier"  |

---

## ValidatedObservation
> Valeur validée par un opérateur ou un pipeline qualité - avec indicateur qualité.

*Aligné avec* :
- [OGC STA 1.1 Observation](https://docs.ogc.org/is/18-088/18-088.html) - une
  ValidatedObservation reprend la structure d'une Observation STA, enrichie des
  métadonnées de qualité et de validation.
- [ODM2 Result + DataQuality](https://github.com/ODM2/ODM2/blob/master/doc/ODM2Docs/ext_dataquality.md)
  - l'extension DataQuality d'ODM2 modélise la qualité attachée à un résultat ;
  ValidatedObservation porte cette information via `qualityFlag`.
- [Helmholtz SMS](https://helmholtz.software/software/sensor-management-system)
  - métadonnées d'observation enrichies (qualité, provenance) dans un système
  d'observation environnemental.
- [HydroServer ProcessingLevel](https://hydroserver2.github.io/hydroserver/)
  - notion de niveau de traitement des données ; la couche métier de BDOH
  correspond aux niveaux validés/publiés de HydroServer.

*Utilisé par* :<br>
TimeSeries (observations)

*Note* :
- Point de mesure validé par opérateur humain ou pipeline automatique.
- Lien vers données brutes : TimeSeries → TimeSeriesSource + phenomenonTimeStart.
- Métadonnées de session (validatedBy, validatedAt, log) portées par ValidationBatch.
- La procédure de validation est portée par la TimeSeries parente.
- validationBatch 0..1 - une observation peut être validée hors batch.
- phenomenonTimeEnd null si instantaneous ou sporadic.

| Champ                 | Cardinalité | Définition                                          | Valeurs possibles                         |
|-----------------------|-------------|-----------------------------------------------------|-------------------------------------------|
| `id`                  | 1           | Identifiant technique, clé primaire                 | uuid                                      |
| `timeSeries`          | 1 →TS       | Série parente                                       | → TimeSeries                              |
| `phenomenonTimeStart` | 1           | Début de la période du phénomène                    | "2024-03-15T09:30:00Z"                    |
| `phenomenonTimeEnd`   | 0..1        | Fin de la période, null si instantané               | "2024-03-15T10:00:00Z" \| null            |
| `resultTime`          | 0..1        | Instant de production du résultat                   | "2024-03-15T09:35:00Z"                    |
| `result`              | 1           | Valeur numérique mesurée                            | "2.4"                                     |
| `qualityFlag`         | 1           | Indicateur qualité (mapping ODM2/SANDRE en annexe)  | `good` \| `suspect` \| `bad` \| `missing` |
| `qualityComment`      | 0..1        | Justification libre du flag qualité                 | "pic de crue suspect"                     |
| `validationBatch`     | 0..1 →VB    | Batch de validation parent                          | → ValidationBatch                         |
| `specimen`            | 0..1 →Spec  | Prélèvement terrain associé (lab_sample uniquement) | → Specimen                                |
| `featureOfInterest`   | 0..1 →FOI   | Entité réelle observée                              | → FeatureOfInterest                       |

---

## ControlObservation
> Mesure ponctuelle de vérification - valeur obtenue par une méthode indépendante et comparée à une série pour détecter une dérive ou une erreur.

*Aligné avec* :
- [ODM2 controlled vocabulary](http://vocabulary.odm2.org/) - vocabulaires de
  qualification ; une ControlObservation est une mesure de contrôle qualité
  (blanc, étalon, duplicat) servant à qualifier les données.
- [OGC OMS / ISO 19156:2023](https://docs.ogc.org/as/20-082r4/20-082r4.html)
  - une observation de contrôle reste une observation au sens OMS : un acte de
  mesure produisant un résultat, mais à finalité de vérification.

*Utilisé par* :<br>
TimeSeries (controlObservations), TransformedTimeSeries (controlObservations)

*Keywords attendus (voir KeywordRequirement)* :<br>
- controlType : independent_measure, cross_validation, reference_gauge

*Note* : 
- Se greffe directement sur une TimeSeries ou TransformedTimeSeries sans Datastream dédié.
- Le System et la procédure diffèrent intentionnellement de ceux de la série parente - c'est une mesure indépendante pour vérifier la cohérence (ex : jaugeage de vérification sur une série de débit calculé, mesure avec un System étalonné de référence, comparaison avec une station voisine).
- seriesType + seriesId : pattern TPC - TimeSeries ou TransformedTimeSeries.
- system : contrainte applicative systemType=sensor.

| Champ                  | Cardinalité | Définition                                          | Valeurs possibles                       |
|------------------------|-------------|-----------------------------------------------------|-----------------------------------------|
| `id`                   | 1           | Identifiant technique, clé primaire                 | uuid                                    |
| `seriesType`           | 1           | Type de la série contrôlée                          | `TimeSeries` \| `TransformedTimeSeries` |
| `seriesId`             | 1           | UUID de la TimeSeries ou TransformedTimeSeries      | uuid                                    |
| `phenomenonTimeStart`  | 1           | Début de la période du phénomène                    | "2024-03-15T09:30:00Z"                  |
| `phenomenonTimeEnd`    | 0..1        | Fin de la période, null si instantané               | "2024-03-15T10:00:00Z" \| null          |
| `resultTime`           | 0..1        | Instant de production du résultat                   | "2024-03-15T09:35:00Z"                  |
| `result`               | 1           | Valeur mesurée                                      | "0.02"                                  |
| `expectedResult`       | 0..1        | Valeur attendue selon la série                      | "0.021"                                 |
| `qualityFlag`          | 1           | Résultat du contrôle                                | `pass` \| `warn` \| `fail`              |
| `qualityComment`       | 0..1        | Justification libre                                 | "écart de 5% - dérive capteur probable" |
| `system`               | 0..1 →Sys   | System utilisé pour le contrôle (systemType=sensor) | → System                                |
| `procedureObservation` | 1 →Proc     | Protocole de mesure appliqué                        | → Procedure (type=observation)          |
| `specimen`             | 0..1 →Spec  | Prélèvement terrain associé                         | → Specimen                              |
| `featureOfInterest`    | 0..1 →FOI   | Entité réelle observée                              | → FeatureOfInterest                     |

---

## Specimen
> Acte de prélèvement terrain daté - résultat de l'activation d'un ou plusieurs équipements via Deployment.

*Aligné avec* :
- [OGC OMS - SF_Specimen / ISO 19156:2023](https://docs.ogc.org/as/20-082r4/20-082r4.html)
  - le concept de Specimen (échantillon prélevé pour analyse ex situ) est défini
  par OMS comme un type de sampling feature. Specimen BDOH en reprend la sémantique.
- [ODM2 Specimen](https://github.com/ODM2/ODM2/blob/master/doc/ODM2Docs/core_samplingfeatures.md)
  - dans ODM2, Specimen est un SamplingFeature ; structure conceptuelle reprise
  (prélèvement, opérateur, méthode).
- [OGC STA 1.1 FeatureOfInterest](https://docs.ogc.org/is/18-088/18-088.html)
  - dans l'API STA exposée, un Specimen apparaît comme le FeatureOfInterest des
  observations qui en sont issues.

*Utilisé par* :<br>
ValidatedObservation (specimen), ControlObservation (specimen), Observation (specimen), specimen_deployment (specimenId)

*Keywords attendus (voir KeywordRequirement)* :<br>
- specimenType (required) : water, soil, sediment, biological
- samplingMedium (required) : surface_water, groundwater, depth

*Note* : 
- Acte de prélèvement physique - un flacon rempli, un piège récolté.
- Distinct de Station (point de surveillance spatial permanent).
- anchorType + anchorId : pattern TPC, même pattern que Deployment - station dans le cas standard, site pour les campagnes sans station fixe.
- Cohérence applicative : anchorType/anchorId doit correspondre à l'ancrage des Deployments associés via specimen_deployment.
- La chaîne analytique interne au laboratoire est hors modèle - lien via limsReference.
- agentType + agentId : pattern TPC - technicien terrain (`Person`) ou préleveur automatique (`Machine`).
- procedureSampling : protocole de prélèvement appliqué pour ce Specimen précis. Null si le Specimen est issu d'un Deployment automatique et que le protocole est porté par TimeSeries.procedureSampling.
- foi : FOI proximate - ce qui a été échantillonné précisément (eau de surface à 30cm), distincte de la FOI de Station (la rivière en général).
- derivedFrom : sous-échantillon issu d'un Specimen parent (aliquote, dilution).


| Champ                 | Cardinalité | Définition                                    | Valeurs possibles             |
|-----------------------|-------------|-----------------------------------------------|-------------------------------|
| `id`                  | 1           | Identifiant technique, clé primaire           | uuid                          |
| `datetime`            | 1           | Horodatage de la récolte                      | "2024-03-15T09:30:00Z"        |
| `anchorType`          | 1           | Type d'ancrage géographique                   | `Station` \| `Site`           |
| `anchorId`            | 1           | UUID de la Station ou du Site                 | uuid                          |
| `foi`                 | 0..1 →FOI   | FOI proximate - ce qui a été échantillonné    | → FeatureOfInterest           |
| `project`             | 0..1 →Proj  | Projet ou campagne dont dépend ce prélèvement | → Project                     |
| `procedureSampling`   | 0..1 →Proc  | Protocole de prélèvement appliqué             | → Procedure (type=sampling)   |
| `depth`               | 0..1        | Profondeur de prélèvement en mètres           | "0.30"                        |
| `volume`              | 0..1        | Volume prélevé en litres                      | "1.0"                         |
| `filtrationOnSite`    | 0..1        | Filtration effectuée sur le terrain           | `true` \| `false`             |
| `filtrationThreshold` | 0..1        | Seuil de filtration en µm                     | "0.45"                        |
| `agentType`           | 0..1        | Type d'agent ayant réalisé la récolte         | `Person` \| `Machine`         |
| `agentId`             | 0..1        | UUID de la Person ou Machine                  | uuid                          |
| `location`            | 0..1 →Loc   | Position exacte si différente de l'ancre      | → Location                    |
| `condition`           | 0..1        | Observations terrain libres                   | "turbidité élevée, eau brune" |
| `derivedFrom`         | 0..1 →Spec  | Specimen parent si sous-échantillon           | → Specimen                    |
| `limsReference`       | 0..1        | Identifiant du prélèvement dans le LIMS       | "LIMS-2024-03-001"            |

---

## specimen_deployment
> Lien many-to-many entre un Specimen et les Deployments qui l'ont produit.

*Note* : 
- Un prélèvement peut mobiliser plusieurs équipements simultanément (pompe + flacon + filtre = trois Deployments → un Specimen).
- Un Deployment peut produire plusieurs Specimens dans le temps (piège récolté chaque semaine pendant un mois).
- L'ancrage géographique du Specimen est hérité du Deployment (Station ou Site).

| Champ          | Cardinalité | Définition               |
|----------------|-------------|--------------------------|
| `specimenId`   | 1 →Spec     | Specimen produit         |
| `deploymentId` | 1 →Dep      | Deployment ayant produit |


<div class="page-break"></div>

# 8. TRANSFORMATION

## TransferFunction
> Fonction de conversion liée à une station - courbe de tarage, relation turbidité/MES...

*Aligné avec* :
- [ODM2 Methods](https://github.com/ODM2/ODM2/blob/master/doc/ODM2Docs/core_methods.md)
  - une fonction de transfert est construite par une méthode (procédure de
  modélisation) ; TransferFunction porte cette méthode via sa colonne
  `procedureModeling`.
- [WMO - Manual on Stream Gauging, Vol. II](https://library.wmo.int/records/item/35841-manual-on-stream-gauging-vol-ii-computation-of-discharge)
  - référence internationale pour les courbes de tarage hauteur-débit (discharge
  ratings) : le cas d'usage hydrométrique central des fonctions de transfert.

*Utilisé par* :<br>
TransferFunctionSet (transferFunction), TransferFunctionBatch (transferFunction),
             TransferFunctionPoint (function)

*Relations inverses (requêter par resourceType='TransferFunction')* :<br>
Responsibility, Identifier, Memory

*Note* : 
- Fonction de conversion liée à une station - analogue à TimeSeries.
- Les points de calibration (couples x/y) définissent la fonction empiriquement.
- anchorType + anchorId : pattern TPC - station dans le cas standard.

| Champ               | Cardinalité | Définition                             | Valeurs possibles                      |
|---------------------|-------------|----------------------------------------|----------------------------------------|
| `id`                | 1           | Identifiant technique, clé primaire    | uuid                                   |
| `code`              | 1           | Slug unique par ancre                  | "hea-qmj-v3"                           |
| `name`              | 1           | Nom de la fonction                     | "Courbe de tarage Mercier D610 v3"     |
| `description`       | 0..1        | Description libre                      |                                        |
| `anchorType`        | 1           | Type d'ancrage géographique            | `Observatory` \| `Site` \| `Station`   |
| `anchorId`          | 1           | UUID de l'Observatory, Site ou Station | uuid                                   |
| `inputProperty`     | 1 →Prop     | Variable en entrée                     | → Property (ex: hauteur)               |
| `outputProperty`    | 1 →Prop     | Variable en sortie                     | → Property (ex: débit)                 |
| `parameters`        | 0..1        | Coefficients analytiques (JSON)        | {"a":2.1,"b":1.5}                      |
| `procedureModeling` | 0..1 →Proc  | Méthode de construction de la fonction | → Procedure (type=modeling)            |
| `validFrom`         | 1           | Début de la période de validité        | "2024-01-01T00:00:00Z"                 |
| `validTo`           | 0..1        | Fin de validité, null si active        | null                                   |
| `status`            | 1           | État de la fonction                    | `active` \| `inactive` \| `deprecated` |

---

## TransferFunctionPoint
> Couple (x, y) de calibration issu d'un jaugeage terrain - définit empiriquement la courbe.

*Utilisé par* :<br>
TransferFunction (via function FK - relation inverse)

*Note* : 
- Couple de valeurs (x/y) définissant empiriquement la fonction.
- Analogue à ValidatedObservation - c'est là que vivent les données (ex : (hauteur=1.23m, débit=4.5m³/s) pour une courbe de tarage ou (turbidité=120NTU, MES=245mg/L) pour une relation turbidité/MES)

| Champ         | Cardinalité | Définition                          | Valeurs possibles       |
|---------------|-------------|-------------------------------------|-------------------------|
| `id`          | 1           | Identifiant technique, clé primaire | uuid                    |
| `function`    | 1 →TF       | Fonction parente                    | → TransferFunction      |
| `batch`       | 0..1 →TFB   | Batch de construction parent        | → TransferFunctionBatch |
| `x`           | 1           | Valeur en entrée                    | 1.23                    |
| `y`           | 1           | Valeur en sortie                    | 4.5                     |
| `uncertainty` | 0..1        | Incertitude sur la mesure           | 0.05                    |
| `datetime`    | 0..1        | Date du jaugeage ou de la mesure    | "2024-03-15T09:30:00Z"  |
| `comment`     | 0..1        | Commentaire libre                   | "jaugeage crue"         |

---

## TransferFunctionBatch
> Acte de construction d'une TransferFunction - qui a construit la courbe, quand, avec quel outil.

*Aligné avec* :
- [ODM2 Actions](https://github.com/ODM2/ODM2/blob/master/doc/ODM2Docs/core_actions.md)
  - la construction d'une fonction de transfert est une Action ODM2 datée et
  attribuée à un acteur.
- [W3C PROV-O wasGeneratedBy](https://www.w3.org/TR/prov-o/#wasGeneratedBy) -
  un TransferFunctionBatch est l'activité PROV qui génère une TransferFunction
  à partir de points de jaugeage.

*Utilisé par* :<br>
TransferFunctionPoint (batch)

*Note* :
- Acte de construction d'une TransferFunction - qui, quand, depuis quel outil.
- Analogue à ValidationBatch et TransformationBatch.
- La procédure est portée par TransferFunction parente, pas répétée ici.
- agentType + agentId : pattern TPC - expert humain (`Person`) pour une courbe de tarage manuelle, ou algorithme automatique (`Machine`) pour BaRatin en mode batch.

| Champ              | Cardinalité | Définition                             | Valeurs possibles               |
|--------------------|-------------|----------------------------------------|---------------------------------|
| `id`               | 1           | Identifiant technique, clé primaire    | uuid                            |
| `transferFunction` | 1 →TF       | Fonction construite                    | → TransferFunction              |
| `builtAt`          | 1           | Date de construction                   | "2024-04-01T08:00:00Z"          |
| `agentType`        | 0..1        | Type d'agent ayant construit la courbe | `Person` \| `Machine`           |
| `agentId`          | 0..1        | UUID de la Person ou Machine           | uuid                            |
| `logUrl`           | 0..1        | Référence externe (export BaRatin..)   | "https://..."                   |
| `status`           | 1           | État du batch                          | `pending` \| `done` \| `failed` |
| `comment`          | 0..1        | Commentaire libre                      |                                 |

---

## TransferFunctionSet
> Jeu de transformation applicable sur une période - référence une TransferFunction et son type.

*Aligné avec* :
- [WMO - Manual on Stream Gauging, Vol. II](https://library.wmo.int/records/item/35841-manual-on-stream-gauging-vol-ii-computation-of-discharge)
  - un jeu de fonctions de transfert correspond à la succession temporelle des
  courbes de tarage d'une station (gestion des changements de tarage).
- [ODM2 Methods](https://github.com/ODM2/ODM2/blob/master/doc/ODM2Docs/core_methods.md)
  - le regroupement de méthodes appliquées dans le temps sur une même station.

*Utilisé par* :<br>
TransformationBatch (transferFunctionSet)

*Note* : 
- Conteneur obligatoire pour une ou plusieurs TransferFunction sur une station.
- Même avec une seule TF on passe toujours par un TFSet.
- Plusieurs TFSet peuvent coexister sur une station sans hiérarchie imposée.
- type=identity ou manual -> transferFunction null, pas de calcul via TF.

| Champ              | Cardinalité | Définition                             | Valeurs possibles                    |
|--------------------|-------------|----------------------------------------|--------------------------------------|
| `id`               | 1           | Identifiant technique, clé primaire    | uuid                                 |
| `name`             | 1           | Nom du jeu                             | "Barème Mercier D610 2024"           |
| `description`      | 0..1        | Description libre                      |                                      |
| `anchorType`       | 1           | Type d'ancrage géographique            | `Observatory` \| `Site` \| `Station` |
| `anchorId`         | 1           | UUID de l'Observatory, Site ou Station | uuid                                 |
| `transferFunction` | 0..1 →TF    | Fonction appliquée si type=function    | → TransferFunction                   |
| `type`             | 1           | Type de transformation                 | `function` \| `identity` \| `manual` |
| `validFrom`        | 1           | Début de validité                      | "2024-01-01T00:00:00Z"               |
| `validTo`          | 0..1        | Fin de validité, null si courant       | null                                 |
| `comment`          | 0..1        | Justification du choix                 | "nouveau jaugeage après crue"        |

Contrainte : si type=function -> transferFunction obligatoire.
            si type=identity ou manual -> transferFunction null.

---

## TransformationBatch
> Acte de calcul d'une série dérivée - qui a lancé le calcul, quand, depuis quelles séries sources.

*Aligné avec* :
- [ODM2 Actions](https://github.com/ODM2/ODM2/blob/master/doc/ODM2Docs/core_actions.md)
  - la dérivation de nouvelles séries est une Action ODM2 ; TransformationBatch
  trace ce calcul (entrées, méthode, acteur, date).
- [W3C PROV-O wasGeneratedBy](https://www.w3.org/TR/prov-o/#wasGeneratedBy) -
  un TransformationBatch est l'activité PROV qui génère une TransformedTimeSeries
  à partir d'une ou plusieurs séries d'entrée.

*Utilisé par* :<br>
Transformation (transformationBatch)

*Note* : 
- Acte de calcul sur une ou plusieurs TimeSeries sources.
- Analogue à ValidationBatch - factorisation des métadonnées de calcul.
- Les points calculés sont dans Transformation.
- inputSeries est une table de jointure explicite `transformationbatch_inputseries` (batch_id, timeseries_id) - un batch peut prendre plusieurs séries en entrée.
- agentType + agentId : pattern TPC - opérateur humain (`Person`) pour un calcul manuel, pipeline automatique (`Machine`) pour un recalcul planifié.
- Point ouvert :
  * cas sans TransferFunctionSet (transformation algorithmique pure)
  * transferFunctionSet est actuellement obligatoire (1), à trancher en v2.

| Champ                   | Cardinalité | Définition                          | Valeurs possibles               |
|-------------------------|-------------|-------------------------------------|---------------------------------|
| `id`                    | 1           | Identifiant technique, clé primaire | uuid                            |
| `transformedTimeSeries` | 1 →TTS      | Série produite                      | → TransformedTimeSeries         |
| `transferFunctionSet`   | 1 →TFS      | Jeu de fonctions appliqué           | → TransferFunctionSet           |
| `inputSeries`           | 1..* →TS    | Séries sources (table jointure)     | → TimeSeries[]                  |
| `appliedAt`             | 1           | Date d'exécution du calcul          | "2024-04-01T08:00:00Z"          |
| `agentType`             | 0..1        | Type d'agent ayant lancé le calcul  | `Person` \| `Machine`           |
| `agentId`               | 0..1        | UUID de la Person ou Machine        | uuid                            |
| `validFrom`             | 1           | Début de la période calculée        | "2024-01-01T00:00:00Z"          |
| `validTo`               | 0..1        | Fin de la période calculée          | null                            |
| `status`                | 1           | État du batch                       | `pending` \| `done` \| `failed` |
| `comment`               | 0..1        | Commentaire libre                   |                                 |

---

## Transformation
> Valeur calculée par un TransformationBatch - analogue à ValidatedObservation.

*Aligné avec* :
- [OGC STA 1.1 Observation](https://docs.ogc.org/is/18-088/18-088.html) - une
  Transformation reprend la structure d'une Observation STA : une valeur datée
  rattachée à une série. Ici la valeur est calculée, non mesurée.
- [ODM2 Provenance](https://github.com/ODM2/ODM2/blob/master/doc/ODM2Docs/ext_provenance.md)
  - l'extension Provenance d'ODM2 modélise les résultats dérivés et leur filiation ;
  une Transformation est un résultat dérivé traçable jusqu'à ses séries sources.

*Utilisé par* :<br>
TransformedTimeSeries (observations)

*Note* : 
- Point calculé par un TransformationBatch.
- Analogue à ValidatedObservation - c'est là que vivent les données calculées.

| Champ                   | Cardinalité | Définition                                | Valeurs possibles                         |
|-------------------------|-------------|-------------------------------------------|-------------------------------------------|
| `id`                    | 1           | Identifiant technique, clé primaire       | uuid                                      |
| `transformedTimeSeries` | 1 →TTS      | Série parente                             | → TransformedTimeSeries                   |
| `transformationBatch`   | 0..1 →TB    | Batch de calcul parent                    | → TransformationBatch                     |
| `phenomenonTimeStart`   | 1           | Début de la période du phénomène          | "2024-03-15T09:30:00Z"                    |
| `phenomenonTimeEnd`     | 0..1        | Fin de la période, null si instantané     | "2024-03-15T10:00:00Z" \| null            |
| `resultTime`            | 0..1        | Instant de production du résultat calculé | "2024-03-16T02:00:00Z" \| null            |
| `result`                | 1           | Valeur calculée                           | "4.5"                                     |
| `qualityFlag`           | 0..1        | Indicateur qualité                        | `good` \| `suspect` \| `bad` \| `missing` |

---

## TransformedTimeSeries
> Série dérivée d'une ou plusieurs TimeSeries via des fonctions de transfert - analogue à TimeSeries.

*Aligné avec* :
- [OGC STA 1.1 Datastream](https://docs.ogc.org/is/18-088/18-088.html) - une
  TransformedTimeSeries reprend la structure d'un Datastream STA, appliquée à
  une série calculée plutôt que mesurée.
- [ODM2 Provenance](https://github.com/ODM2/ODM2/blob/master/doc/ODM2Docs/ext_provenance.md)
  - l'extension Provenance d'ODM2 trace la filiation des résultats dérivés.
- [HydroServer ProcessingLevel](https://hydroserver2.github.io/hydroserver/)
  - notion de niveau de traitement : une TransformedTimeSeries correspond à un
  niveau dérivé/calculé dans la hiérarchie de traitement des données.

*Utilisé par* :<br>
TransformationBatch (transformedTimeSeries),
             Bundle via bundle_series (seriesType='TransformedTimeSeries'),
             ControlObservation (seriesType='TransformedTimeSeries', seriesId)

*Relations inverses (requêter par resourceType='TransformedTimeSeries')* :<br>
Identifier, Memory, KeywordAssignment

*Note* : 
- Série dérivée d'une ou plusieurs TimeSeries via des TransformationBatch.
- Analogue à TimeSeries - même structure de métadonnées.
- Plusieurs TransformedTimeSeries peuvent coexister sur la même station et la même variable sans hiérarchie - c'est le contexte scientifique qui désigne laquelle utiliser (même principe que TimeSeries).
- Plage temporelle couverte : non stockée. `phenomenonTimeStart` et `phenomenonTimeEnd` de la série sont calculés à la demande (MIN/MAX du phenomenonTime des Transformations), exposés en lecture seule par l'API. Recomposés en l'intervalle `phenomenonTime` à l'export STA.
- code unique par Station.

| Champ                     | Cardinalité | Définition                             | Valeurs possibles                                                |
|---------------------------|-------------|----------------------------------------|------------------------------------------------------------------|
| `id`                      | 1           | Identifiant technique, clé primaire    | uuid                                                             |
| `code`                    | 1           | Slug unique par ancre                  | "debit-tarage-bdoh"                                              |
| `name`                    | 1           | Nom de la série dérivée                | "Débit Mercier au pont D610"                                     |
| `description`             | 0..1        | Description libre                      |                                                                  |
| `anchorType`              | 1           | Type d'ancrage géographique            | `Observatory` \| `Site` \| `Station`                             |
| `anchorId`                | 1           | UUID de l'Observatory, Site ou Station | uuid                                                             |
| `featureOfInterest`       | 0..1 →FOI   | FOI proximate si différente de l'ancre | → FeatureOfInterest                                              |
| `property`                | 1 →Prop     | Variable produite                      | → Property                                                       |
| `unit`                    | 1 →Unit     | Unité de la série dérivée              | → Unit                                                           |
| `procedureTransformation` | 1 →Proc     | Procédure de transformation            | → Procedure (type=transformation)                                |
| `acquisitionType`         | 1           | Mode d'acquisition des données         | `sensor_continuous` \| `lab_sample`                              |
| `aggregationStatistic`    | 1           | Nature métrologique de la valeur       | `instantaneous` \| `average` \| `cumulative` \| `maximum` \| `minimum` \| `variance` \| `standard_deviation` \| `sporadic` |
| `observationFrequency`    | 0..1        | Fréquence nominale (ISO 8601)          | "PT15M" \| "PT1H" - null si aggregationStatistic=sporadic        |
| `status`                  | 1           | État de la série                       | `active` \| `inactive` \| `discontinued`                         |
| `license`                 | 1 →Lic      | Licence des données                    | → License                                                        |


<div class="page-break"></div>

# 9. ORGANISATION

## Project
> Projet ou campagne ayant financé ou porté une ressource.

*Aligné avec* :
- [OGC STAplus - Project](https://docs.ogc.org/is/22-022r1/22-022r1.html) -
  extension STA (22-022r1) dont l'entité Project organise les observations en
  campagnes/projets. Modèle direct du Project BDOH.
- [schema.org/ResearchProject](https://schema.org/ResearchProject) - vocabulaire
  web pour la sérialisation JSON-LD d'un projet de recherche.
- [DataCite Metadata Schema](https://schema.datacite.org/) - schéma de métadonnées
  pour la citation des données ; `relatedIdentifier` permet de lier un Project
  à ses publications et jeux de données associés.

*Utilisé par* :<br>
HistoricalProject (project), Specimen (project)

*Relations inverses (requêter par resourceType='Project')* :<br>
Responsibility, Identifier, Memory

*Note* : 
- Projet structurant ou campagne de mesure - même objet.
- Lien vers Observatory/Site/Station/TimeSeries via HistoricalProject.
- Organisations et rôles (financeur, coordinateur, partenaire...) via Responsibility (resourceType='Project', role=funder|principalInvestigator|collaborator...).
- Pas de FK directe fundingAgency - Responsibility couvre tous les rôles avec temporalité et multiplicité, sans double vérité.

| Champ         | Cardinalité | Définition                               | Valeurs possibles                       |
|---------------|-------------|------------------------------------------|-----------------------------------------|
| `id`          | 1           | Identifiant technique, clé primaire      | uuid                                    |
| `code`        | 1           | Code court unique                        | "osr8" \| "camp-yzr-2023-metaux"        |
| `name`        | 1           | Nom du projet ou de la campagne          | "OSR8" \| "Campagne métaux Yzeron 2023" |
| `description` | 0..1        | Description scientifique                 |                                         |
| `parent`      | 0..1 →Proj  | Projet parent si sous-projet ou campagne | → Project                               |
| `startDate`   | 1           | Début du projet                          | "2020-01-01"                            |
| `endDate`     | 0..1        | Fin du projet, null si actif             | "2024-12-31"                            |
| `status`      | 1           | État du projet                           | `planned` \| `active` \| `completed`    |
| `url`         | 0..1        | Site web du projet                       | "https://..."                           |

---

## HistoricalProject
> Lien temporalisé entre un projet et une ressource - plusieurs projets actifs simultanément possibles.

*Note* : 
- Trace la succession des projets qui portent une ressource.
- Source de vérité unique pour le lien Project → ressource.
- Même pattern que HistoricalLocation.

| Champ          | Cardinalité | Définition                          | Valeurs possibles                                    |
|----------------|-------------|-------------------------------------|------------------------------------------------------|
| `id`           | 1           | Identifiant technique, clé primaire | uuid                                                 |
| `project`      | 1 →Proj     | Projet actif sur cette période      | → Project                                            |
| `resourceType` | 1           | Type de ressource ciblée            | `Observatory` \| `Site` \| `Station` \| `TimeSeries` |
| `resourceId`   | 1           | UUID de la ressource ciblée         | uuid                                                 |
| `validFrom`    | 1           | Début de la période                 | "2012-01-01"                                         |
| `validTo`      | 0..1        | Fin de la période, null si actif    | null                                                 |

---

## Bundle
> Regroupement éditorial de séries et fonctions pour la diffusion et le catalogage - objet de publication.

*Aligné avec* :
- [ODM2 Datasets](https://github.com/ODM2/ODM2/blob/master/doc/ODM2Docs/core_datasets.md)
  - mécanisme ODM2 de regroupement logique de résultats en jeu de données
  cohérent ; Bundle reprend ce principe pour la publication.
- [DataCite Metadata Schema](https://schema.datacite.org/) - schéma de référence
  pour la publication citable d'un jeu de données (DOI, publisher, version,
  relatedIdentifier). Cible d'export d'un Bundle vers un entrepôt à DOI.
- [DCAT Distribution](https://www.w3.org/TR/vocab-dcat-3/#Class:Distribution)
  - classe du vocabulaire de catalogue W3C ; un Bundle correspond à une
  distribution accessible d'un dataset, exportable vers les catalogues
  (Theia/OZCAR, ENVRI-Hub).

*Relations inverses* :<br>
KeywordAssignment

*Note* : 
- Regroupe des TimeSeries, TransformedTimeSeries, TransferFunction et ControlObservation pour la publication. Objet éditorial - pas technique.
- Lien via table polymorphique bundle_series (seriesType + seriesId) - pattern TPC.
- Extensible à tout nouveau type de série sans migration de schéma.

| Champ         | Cardinalité | Définition                          | Valeurs possibles              |
|---------------|-------------|-------------------------------------|--------------------------------|
| `id`          | 1           | Identifiant technique, clé primaire | uuid                           |
| `name`        | 1           | Nom du bundle                       | "Qualité eau Saône 2024"       |
| `description` | 0..1        | Description libre                   |                                |
| `Observatory` | 1 →Obs      | Observatoire parent                 | → Observatory                  |
| `license`     | 1 →Lic      | Licence des données du bundle       | → License                      |
| `archivedAt`  | 0..1        | Horodatage d'archivage logique      | null \| "2024-01-01T00:00:00Z" |

---

## BundleSeries
> Lien polymorphique entre un Bundle et une série ou fonction - table de jointure TPC.

*Note* : Extensible sans migration : ajouter un type = ajouter une valeur à l'enum seriesType.
       Intégrité garantie par trigger BEFORE INSERT/UPDATE (pattern TPC agent).

| Champ        | Cardinalité | Définition                   | Valeurs possibles                                                                     |
|--------------|-------------|------------------------------|---------------------------------------------------------------------------------------|
| `bundleId`   | 1 →Bun      | Bundle parent                | → Bundle                                                                              |
| `seriesType` | 1           | Type de la série ou fonction | `TimeSeries` \| `TransformedTimeSeries` \| `TransferFunction` \| `ControlObservation` |
| `seriesId`   | 1           | UUID de la série ou fonction | uuid                                                                                  |

---

## Memory
> Note ou événement attaché à n'importe quelle ressource du modèle - journal de bord.

*Aligné avec* :
- [ODM2 Annotations](https://github.com/ODM2/ODM2/blob/master/doc/ODM2Docs/ext_annotations.md)
  - extension ODM2 permettant d'attacher des notes et commentaires qualifiants
  à n'importe quelle entité. Memory généralise ce principe via le pattern
  resourceType + resourceId.
- [schema.org/CreativeWork](https://schema.org/CreativeWork) - vocabulaire web
  réutilisé par STAMPLATE pour la sérialisation JSON-LD des notes et contenus
  éditoriaux (texte, photos, événements).

*Utilisé par* :<br>
Observatory, Site, Station, System, TimeSeries, TransformedTimeSeries, Deployment, Project, TransferFunction (via resourceType + resourceId)

*Keywords attendus (voir KeywordRequirement)* :<br>
- memoryType : note, event, document, photo, installation, hydraulic_change, maintenance, incident, calibration
	   
*Note* : 
- Note contextuelle ou événement daté attaché à n'importe quelle ressource.
- Objet transversal de documentation du cycle de vie.
- Fichiers stockés en S3, référencés via mediaUrl.
- agentType + agentId : pattern TPC - auteur humain (`Person`) pour une note
- manuelle, pipeline (`Machine`) pour une alerte automatique ou détection d'anomalie.

| Champ          | Cardinalité | Définition                          | Valeurs possibles                                                               |
|----------------|-------------|-------------------------------------|---------------------------------------------------------------------------------|
| `id`           | 1           | Identifiant technique, clé primaire | uuid                                                                            |
| `resourceType` | 1           | Type de ressource ciblée            | `Observatory` \| `Site` \| `Station` \| `System` \| `TimeSeries` \| `TransformedTimeSeries` \| `Deployment` \| `Project` \| `TransferFunction` |
| `resourceId`   | 1           | UUID de la ressource ciblée         | uuid                                                                            |
| `datetime`     | 1           | Date de la note ou de l'événement   | "2014-04-17T00:00:00Z"                                                          |
| `title`        | 0..1        | Titre court                         | "Modification contrôle hydraulique"                                             |
| `content`      | 0..1        | Texte libre                         | "Installation d'une lame déversante"                                            |
| `mediaUrl`     | 0..*        | Photos ou documents associés (S3)   | "https://storage.obs.fr/memories/2014-lame.jpg"                                 |
| `agentType`    | 0..1        | Type d'agent auteur de la note      | `Person` \| `Machine`                                                           |
| `agentId`      | 0..1        | UUID de la Person ou Machine        | uuid                                                                            |
