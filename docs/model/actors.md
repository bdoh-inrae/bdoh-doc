# Acteurs

Les entités acteurs décrivent les personnes et organisations impliquées dans le cycle de vie des données. Elles sont référencées partout dans le modèle.

---

## Person

Utilisé par : [SamplingFeature](observation.md#samplingfeature) (operator), [ValidatedObservation](observation.md#validatedobservation) (validatedBy), [Responsibility](#responsibility) (person), [Transformation](transformation.md#transformation) (appliedBy), [Memory](organisation.md#memory) (author)

| Champ          | Cardinalité   | Définition                          | Valeurs possibles                         |
|----------------|---------------|-------------------------------------|-------------------------------------------|
| `id`           | 1             | Identifiant technique, clé primaire | uuid                                      |
| `firstName`    | 1             | Prénom                              | "Julie"                                   |
| `lastName`     | 1             | Nom de famille                      | "Dupont"                                  |
| `email`        | 0..1          | Adresse email                       | "julie.dupont@inrae.fr"                   |
| `orcid`        | 0..1          | Identifiant chercheur ORCID         | "0000-0001-1234-1234"                     |
| `organization` | 0..* →Org     | Employeur / labo de rattachement    | → Organization[]                          |
| `affiliation`  | 0..1          | Affiliation textuelle libre         | "INRAE, UR RiverLy, Villeurbanne, France" |

---

## Organization

Utilisé par : [Person](#person) (organization), [Sensor](instrumentation.md#sensor) (laboratory), [Station](network.md#station) (operator), [Equipment](instrumentation.md#equipment) (owner), [Observatory](network.md#observatory) (operator), [Responsibility](#responsibility) (organization), [Project](project.md#project) (fundingAgency)

| Champ        | Cardinalité  | Définition                                       | Valeurs possibles                                                                       |
|--------------|--------------|--------------------------------------------------|-----------------------------------------------------------------------------------------|
| `id`         | 1            | Identifiant technique, clé primaire              | uuid                                                                                    |
| `code`       | 0..1         | Code depuis acronym, optionnel                   | "inrae"                                                                                 |
| `name`       | 1            | Nom complet                                      | "Institut national de recherche pour l'agriculture, l'alimentation et l'environnement"  |
| `acronym`    | 0..1         | Sigle                                            | "INRAE"                                                                                 |
| `type`       | 1            | Catégorie d'organisation                         | `laboratory` \| `monitoring_network` \| `research` \| `agency` \| `university`         |
| `country`    | 1            | Pays (code ISO)                                  | "FR"                                                                                    |
| `url`        | 0..1         | Site web                                         | "https://www.inrae.fr"                                                                  |
| `logoUrl`    | 0..1         | URL vers le logo (S3 ou hébergeur officiel)      | "https://www.inrae.fr/logo.svg"                                                         |
| `identifier` | 0..* →Ident  | Codes externes et PID (ROR, ISNI...)             | → [Identifier](references.md#identifier)[]                                              |

---

## Responsibility

Aligné avec : ISO 19115 CI_Responsibility, CI_RoleCode

Utilisé par : [Observatory](network.md#observatory), [Site](network.md#site), [Station](network.md#station), [TimeSerie](observation.md#timeserie), [Project](project.md#project) (via resourceType + resourceId)

!!! note
    Lie une Person ou une Organization à une ressource avec un rôle fonctionnel.
    Distinct de `Person.organization` qui décrit l'appartenance institutionnelle.
    Contrainte : `person` et `organization` ne peuvent pas être tous les deux null simultanément.

| Champ          | Cardinalité  | Définition                               | Valeurs possibles                                                                                                                                                            |
|----------------|--------------|------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `id`           | 1            | Identifiant technique, clé primaire      | uuid                                                                                                                                                                         |
| `person`       | 0..1 →Per    | Personne responsable                     | → [Person](#person)                                                                                                                                                          |
| `organization` | 0..1 →Org    | Organisation responsable                 | → [Organization](#organization)                                                                                                                                              |
| `role`         | 1            | Rôle fonctionnel (CI_RoleCode ISO 19115) | `pointOfContact` \| `principalInvestigator` \| `author` \| `processor` \| `publisher` \| `custodian` \| `owner` \| `distributor` \| `originator` \| `resourceProvider` \| `user` |
| `resourceType` | 1            | Type de ressource ciblée                 | `Observatory` \| `Site` \| `Station` \| `TimeSerie` \| `Project`                                                                                                            |
| `resourceId`   | 1            | UUID de la ressource ciblée              | uuid                                                                                                                                                                         |
| `validFrom`    | 0..1         | Début de responsabilité                  | "2022-01-01"                                                                                                                                                                 |
| `validTo`      | 0..1         | Fin, null si toujours actif              | "2024-12-31" \| null                                                                                                                                                         |
