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

**Valeurs de vocabulaire (Keyword)** : à distinguer des enums SQL ci-dessus.
Un `Keyword` n'a pas de valeur d'enum figée ; il est désigné par ses libellés
bilingues `term_fr` / `term_en` (texte lisible normal, avec espaces et casse
naturelle : "surface water", "eau de surface") et porte une `notation`,
identifiant court en `kebab-case` destiné aux URIs ("surface-water"). Les
exemples de termes donnés dans les notes d'entité ("Keywords attendus") sont
des `term_en`, donc en texte lisible, pas des slugs.

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
- `Entité (via resourceType + resourceId)` : lien par le pattern TPC resource.
- `Entité (table jointure)` : lien many-to-many via une table de jointure.

Cette notation permet de distinguer une FK réelle d'un lien TPC
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

Slug lisible (kebab-case) présent sur les entités nommées navigables : celles
qu'un humain identifie et requête de mémoire dans une URL ou un script, sans
manipuler d'UUID. Là où il existe, il est obligatoire, jamais optionnel : un
code présent une fois sur deux obligerait, pour chaque objet, à deviner si
l'UUID ou le code est la bonne entrée. Modifiable par l'utilisateur, avec une
suggestion automatique à la création depuis le `name` (ou le `serialNumber`
pour System). Unique dans son scope parent (voir Scopes d'unicité) : deux
entités de scopes différents peuvent porter le même code.

Le `code` est un **confort de navigation**, pas un identifiant. Il permet de
lire et requêter les ressources de l'API sans manipuler d'UUID. Parce qu'il est
modifiable, il ne sert jamais de cible à un lien partagé, un export cité ou une
référence externe : ces usages passent exclusivement par l'UUID (identité
pérenne) ou par `Identifier` (identifiant externe cité). Le modifier est donc
sans conséquence sur l'intégrité, cela relève de la lisibilité, pas de
l'identification.

Portent un `code` : Observatory, Site, Station, System, Deployment, Datastream,
TimeSeries, TransformedTimeSeries, TransferFunction, TransferFunctionSet,
Algorithm, Project, Organization, Property, Unit, Procedure, FeatureOfInterest.
Pour `Algorithm` et `TransferFunction`, dont plusieurs lignes coexistent au fil
des versions, le slug inclut la version ("agregation-qjxa-v3", "hea-qmj-v3") et
reste unique ligne à ligne comme partout ; la version exacte reste épinglée par
le `swhid` pour `Algorithm`, le `code` ne fait que la nommer lisiblement.

N'en portent pas, chacune pour une raison précise :
- les lignes d'observation (`Observation`, `ValidatedObservation`,
  `AnalysisObservation`, `ControlObservation`) : on n'atteint jamais une mesure
  individuelle en la tapant, toujours via sa série ;
- `Person` : pas de slug fiable (homonymes, changements de nom) ; on la
  recherche par son nom et on la cite par un `Identifier` (ORCID) s'il existe ;
- `Bundle` et `Dataset` : cités par leur DOI, qui existe forcément ;
- `Specimen` : identifié par son code de laboratoire externe, porté par
  `limsReference` (ou un `Identifier`), pas par un slug BDOH ajouté en plus ;
- `Memory` : atteinte par navigation depuis la ressource qu'elle annote.

Les codes externes (SANDRE, TheiaOZCAR, WIGOS...) sont portés par `Identifier`,
pas par `code`. Le `code` est interne à BDOH.

## Scopes d'unicité du code

```
Observatory           unique globalement
Organization          unique globalement
System                unique globalement
Project               unique globalement
Procedure             unique globalement
Property              unique globalement
Unit                  unique globalement
Algorithm             unique globalement (version dans le slug)
FeatureOfInterest     unique globalement
Site                  unique par Observatory
Station               unique par Site
Deployment            unique par Station
TimeSeries            unique par ancre (Observatory, Site ou Station)
Datastream            unique par ancre (Observatory, Site ou Station)
TransferFunction      unique par ancre (Observatory, Site ou Station)
TransferFunctionSet   unique par ancre (Observatory, Site ou Station)
TransformedTimeSeries unique par ancre (Observatory, Site ou Station)
```

<div class="page-break"></div>

# Patterns transversaux

Le modèle utilise un même mécanisme, appelé **TPC**, pour les liens
polymorphiques, c'est-à-dire les liens qui peuvent pointer vers plusieurs
types d'entités selon le cas. Une table porte un couple `xxxType` + `xxxId` :
`xxxType` discrimine le type d'entité ciblée, `xxxId` porte son UUID. Aucune
FK native PostgreSQL n'est posée ; l'intégrité est garantie applicativement
(trigger, vérification périodique).

Ce pattern TPC est décliné en quatre usages, présentés ci-dessous :
- **TPC resource** (`resourceType + resourceId`) : rattacher une donnée
  transverse à n'importe quelle ressource (identifiants, mots-clés, notes...).
- **TPC anchor** (`anchorType + anchorId`) : ancrer une entité à un contexte
  géographique (Observatory, Site ou Station).
- **TPC agent** (`agentType + agentId`) : désigner l'acteur d'un acte
  (Person, Machine ou Organization).
- **TPC series** (`seriesType + seriesId`) : pointer vers une série ou une
  fonction, quel que soit son type (regroupements, exports, entrées de calcul,
  contrôles).

## Pattern TPC resource (resourceType + resourceId)

Rattache une donnée transverse (identifiant, mot-clé, note, responsable,
historique) à une ressource quelconque. `resourceType` discrimine le type de
ressource, `resourceId` porte son uuid.

Domaine de référence de `resourceType` : `Observatory`, `Site`, `Station`,
`System`, `Deployment`, `Datastream`, `TimeSeries`, `TransformedTimeSeries`,
`TransferFunction`, `TransferFunctionSet`, `Project`, `Bundle`, `Dataset`,
`Person`, `Organization`, `Property`, `Unit`, `Procedure`, `FeatureOfInterest`,
`Specimen`, `ControlObservation`, `Algorithm`, `Memory`.

Ne sont pas des ressources, et n'apparaissent dans aucune table ci-dessous : les
lignes de données (`Observation`, `ValidatedObservation`, `AnalysisObservation`),
les batches (qui portent leur acteur en propre, ce sont des événements), les
vocabulaires eux-mêmes (`Keyword`, `KeywordType`), les entités fermées et
autodéfinies (`License`, `Location`), les lignes de couture ou de calcul
(`TimeSeriesSource`, `Transformation`, `TransferFunctionPoint`,
`TransferFunctionParameter`).

Critère `Identifier` contre `Keyword` (tranche les cas limites). `Identifier`
porte un identifiant de la ressource elle-même dans un registre (DOI, ORCID, ROR,
SWHID, code SANDRE) : il dit ce que la ressource est. `Keyword` porteur d'`uri`
aligne la ressource sur un terme de thésaurus (UCUM, QUDT, NERC P01, Theia/OZCAR) :
il dit dans quel vocabulaire elle se classe, et il est multi-valué (une même
ressource s'aligne sur plusieurs thésaurus). Un URI de vocabulaire n'est donc pas
un `Identifier`. Frontière assumée : un code de référentiel comme SANDRE est
traité en `Identifier`, ce choix relève du jugement, pas d'une propriété de l'URI.

Chaque table n'accepte qu'un sous-ensemble de ce domaine ; la liste exacte est
portée par le champ `resourceType` de son tableau, seule source de vérité. Le
tableau ci-dessous n'est qu'un index des tables porteuses, et le domaine de
référence est l'union maximale que ces sous-ensembles ne dépassent jamais.

| Table                | Ce qu'elle porte                          | Cibles autorisées                      |
|----------------------|-------------------------------------------|----------------------------------------|
| `Identifier`         | PID vers un référentiel externe           | voir `Identifier.resourceType`         |
| `Memory`             | Note, événement ou photo                  | voir `Memory.resourceType`             |
| `Responsibility`     | Rôle d'un acteur sur la ressource         | voir `Responsibility.resourceType`     |
| `KeywordAssignment`  | Mot-clé ou classification contrôlée       | voir `KeywordAssignment.resourceType`  |
| `KeywordRequirement` | Règle de complétion minimale en mots-clés | voir `KeywordRequirement.resourceType` |
| `HistoricalLocation` | Position géographique datée               | voir `HistoricalLocation.resourceType` |
| `HistoricalProject`  | Projet porteur daté                       | voir `HistoricalProject.resourceType`  |

## Pattern TPC anchor (anchorType + anchorId)

Ancre une entité à un contexte géographique. `anchorType` discrimine le type de
contexte, `anchorId` porte son uuid.

Domaine de référence de `anchorType` : `Observatory`, `Site`, `Station`.

Chaque table n'accepte qu'un sous-ensemble de ce domaine ; la liste exacte est
portée par le champ `anchorType` de son tableau, seule source de vérité. Le
tableau ci-dessous n'est qu'un index des tables porteuses. `Deployment` et
`Specimen` sont restreints à `Site` et `Station` (on déploie un instrument ou
prélève un échantillon en un lieu précis, pas sur un observatoire entier) ; les
autres acceptent les trois.

| Table                   | Entité ancrée                 | Cibles autorisées                        |
|-------------------------|-------------------------------|------------------------------------------|
| `Deployment`            | Déploiement d'instrument      | voir `Deployment.anchorType`             |
| `Datastream`            | Flux brut IoT                 | voir `Datastream.anchorType`             |
| `TimeSeries`            | Série validée                 | voir `TimeSeries.anchorType`             |
| `TransformedTimeSeries` | Série dérivée                 | voir `TransformedTimeSeries.anchorType`  |
| `Specimen`              | Échantillon prélevé           | voir `Specimen.anchorType`               |
| `TransferFunction`      | Barème (courbe de tarage...)  | voir `TransferFunction.anchorType`       |
| `TransferFunctionSet`   | Jeu de barèmes                | voir `TransferFunctionSet.anchorType`    |

Source de vérité de l'ancrage d'un flux : chaque flux (`Datastream`,
`TimeSeries`, `TransformedTimeSeries`) porte lui-même son ancrage, complet et
autoportant, sans avoir à le déduire d'une autre entité. C'est nécessaire pour
qu'il soit exportable de façon autonome vers une API externe (STA notamment). En
cas de divergence entre l'ancrage d'un flux et celui du Deployment du System
correspondant, l'ancrage du flux fait foi et le Deployment doit être corrigé :
l'ancrage d'un Deployment est une documentation de l'installation, ajoutée
souvent après coup. Ce choix évite de remonter la chaîne flux vers System vers
Deployment pour la question fréquente "quels flux sont rattachés à cette
station ?".

## Pattern TPC agent (agentType + agentId)

Trace l'acteur d'un acte ou d'une responsabilité : un humain (`Person`), un agent
automatisé (`Machine`) ou une organisation (`Organization`). `agentType`
discrimine le type, `agentId` porte son uuid.

Domaine de référence de `agentType` : `Person`, `Machine`, `Organization`.

Chaque table n'accepte qu'un sous-ensemble de ce domaine ; la liste exacte est
portée par le champ `agentType` de son tableau, seule source de vérité. Le
tableau ci-dessous n'est qu'un index des tables porteuses. Seule
`Responsibility` accepte les trois types ; les autres se limitent à `Person` et
`Machine`.

| Table                   | Acte tracé                        | Cibles autorisées                        |
|-------------------------|-----------------------------------|------------------------------------------|
| `Responsibility`        | Responsabilité sur une ressource  | voir `Responsibility.agentType`          |
| `ValidationBatch`       | Session de validation             | voir `ValidationBatch.agentType`         |
| `ObservationBatch`      | Import de données                 | voir `ObservationBatch.agentType`        |
| `AnalysisBatch`         | Campagne d'analyse labo           | voir `AnalysisBatch.agentType`           |
| `TransferFunctionBatch` | Construction d'un barème          | voir `TransferFunctionBatch.agentType`   |
| `Memory`                | Note (auteur)                     | voir `Memory.agentType`                  |
| `Specimen`              | Prélèvement (opérateur)           | voir `Specimen.agentType`                |

`TransformationBatch` n'est pas un porteur TPC agent : son exécutant est porté
par `runner`, une FK directe vers `Machine` (un calcul est toujours exécuté par
une machine, jamais par une personne).

## Pattern TPC series (seriesType + seriesId)

Pointe vers une série ou une fonction sans présumer de son type concret.
`seriesType` discrimine le type, `seriesId` porte son uuid.

Domaine de référence de `seriesType` : `TimeSeries`, `TransformedTimeSeries`,
`TransferFunction`, `ControlObservation`.

Chaque table n'accepte qu'un sous-ensemble de ce domaine ; la liste exacte est
portée par le champ `seriesType` de son tableau, seule source de vérité. Le
tableau ci-dessous n'est qu'un index des tables porteuses.

| Table                             | Ce qu'elle relie                 | Cibles autorisées                               |
|-----------------------------------|----------------------------------|-------------------------------------------------|
| `bundle_series`                   | Regroupement en Bundle           | voir `bundle_series.seriesType`                 |
| `dataset_resource`                | Référence d'export (Dataset)     | voir `dataset_resource.seriesType`              |
| `transformationbatch_inputseries` | Entrées d'un TransformationBatch | voir jointure `transformationbatch_inputseries` |
| `ControlObservation`              | Série contrôlée par une mesure   | voir `ControlObservation.seriesType`            |


## Tables de jointure explicites

Ces tables encodent des relations many-to-many portées par l'entité
"propriétaire".

| Table                              | Entre                              |
|------------------------------------|------------------------------------|
| `person_organization`              | Person ↔ Organization              |
| `transformationbatch_inputseries`  | TransformationBatch ↔ TimeSeries ou TransformedTimeSeries (seriesType + seriesId, pattern TPC series) |
| `specimen_deployment`              | Specimen ↔ Deployment              |
| `transferfunctionset_function`     | TransferFunctionSet ↔ TransferFunction |
| `dataset_resource`                 | Dataset ↔ TimeSeries, TransformedTimeSeries, TransferFunction ou ControlObservation (TPC series) |

TransferFunctionParameter et TransferFunctionPoint ne sont pas dans cette table car ce sont des relations 1..* directes (FK sur la table fille), non des jointures many-to-many.

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
via TPC. Un trigger `prevent_physical_delete` est posé sur toutes les entités
concernées. Trois mécanismes selon les tables, jamais deux à la fois sur la
même table :

- Tables avec `status` : utiliser `status` comme mécanisme de désactivation.
- Tables sans `status` ni cycle temporel propre : `archivedAt TIMESTAMPTZ NULL`
  (null = actif).
- Tables datées (`validFrom`/`validTo`, voir *Associations datées*) : `validTo`
  non-null ferme la ligne. C'est déjà un mécanisme de désactivation à part
  entière ; ces tables n'ont ni `status` ni `archivedAt` en plus, ce serait une
  double vérité sur le même fait.

Les tables de jointure (`person_organization`, `specimen_deployment`,
`transformationbatch_inputseries`, `bundle_series`) sont exemptées :
leurs lignes peuvent être supprimées physiquement car elles ne sont
pas elles-mêmes référencées par d'autres relations.

`ControlObservation` est exemptée, pour une raison différente de celle des
tables de jointure : c'est un constat scientifique figé une fois enregistré
(une mesure de contrôle a été faite), au même titre qu'une ligne `Observation`.
Rien ne la rend jamais obsolète au sens où une station ou un jeu de barème
peuvent l'être ; elle ne porte donc aucun des trois mécanismes ci-dessus.
`Specimen`, à l'inverse, est un objet physique réel (un flacon, un prélèvement)
qui peut être détruit ou épuisé : il porte `status`, malgré sa parenté avec les
constats figés.

Tables avec `status` (mécanisme natif) : Observatory, Site, Station, System,
Deployment, Datastream, ObservationBatch, ValidationBatch, AnalysisBatch,
TransferFunction, TransferFunctionBatch, TransformationBatch,
TransformedTimeSeries, TimeSeries, Project, Algorithm, TransferFunctionSet,
Dataset, Memory, Identifier, Specimen.

Tables avec `archivedAt` (ajout dédié) : Person, Machine, Organization, Unit,
Procedure, KeywordType, Keyword, License, Location, FeatureOfInterest, Bundle,
Property (qui a déjà `status=accepted|deprecated|proposed`).

Tables datées, `validTo` fait foi (pas d'`archivedAt` en plus) :
`HistoricalLocation`, `HistoricalProject`, `Responsibility`, `TimeSeriesSource`.


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
pattern TPC agent (agentType=`Person`) sur ValidationBatch, ObservationBatch, TransferFunctionBatch, Memory, Specimen. Responsibility (Person). person_organization (affiliation).

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
> Système ou service qui exécute des traitements automatisés - runner, pipeline, VM, HPC, agent IA.

*Aligné avec* :
- [W3C PROV-O Agent](https://www.w3.org/TR/prov-o/#Agent) - Machine est un agent
  PROV au sens de la traçabilité de production (`wasAssociatedWith`).

*Utilisé par* :<br>
pattern TPC agent (agentType=`Machine`) sur ValidationBatch, ObservationBatch, TransferFunctionBatch, Memory, Specimen.

*Relations inverses* :<br>
aucune (Machine est référencée via agentId)

*Note* :
- Représente le système qui a exécuté un traitement : serveur BDOH, HPC distant, pipeline local, agent IA.
- Ne porte pas les métadonnées du code exécuté : celles-ci vivent sur Algorithm.
- La reproductibilité scientifique est garantie par Algorithm (via son Identifier swhid), pas par Machine.
- serviceUrl est utile pour les runners distants (HPC, service cloud) afin de pointer vers le système.

| Champ         | Cardinalité | Définition                          | Valeurs possibles               |
|---------------|-------------|-------------------------------------|---------------------------------|
| `id`          | 1           | Identifiant technique, clé primaire | uuid                            |
| `name`        | 1           | Nom du système ou service           | "runner-bdoh-prod", "hpc-cines" |
| `description` | 0..1        | Description libre                   |                                 |
| `serviceUrl`  | 0..1        | URL du service si runner distant    | "https://..."                   |
| `archivedAt`  | 0..1        | Horodatage d'archivage logique      | null \| "2024-01-01T00:00:00Z"  |

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
- organizationType : laboratory, monitoring network, research, agency, university

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
| `resourceType` | 1           | Type de ressource ciblée                   | `Observatory` \| `Site` \| `Station` \| `System` \| `Datastream` \| `TimeSeries` \| `TransformedTimeSeries` \| `TransferFunction` \| `TransferFunctionSet` \| `Project` \| `Bundle` \| `Algorithm` |
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
- [Theia/OZCAR thesaurus](https://w3id.org/ozcar-theia) - thésaurus national
  français des variables observées dans les observatoires de zone critique.
  Référence privilégiée pour qualifier une Property et la rendre interopérable
  avec le portail in-situ.theia-land.fr ; le rattachement se fait via le
  mécanisme Keyword (`KeywordAssignment` vers un `Keyword` dont le `uri` est
  l'URI du terme du thésaurus).
- [NERC NVS P01 (Parameter Usage Vocabulary)](https://vocab.nerc.ac.uk/collection/P01/current/)
  - vocabulaire international de référence pour les variables environnementales,
  40 000+ termes avec URIs stables. Rattachement via Keyword, comme Theia/OZCAR.
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
- samplingMedium (recommended) : surface water, groundwater, soil

*Note* : 
- Géré par les curateurs, chaque variable est unique et non dupliquée.
- Rattachement aux thésaurus de variables (Theia/OZCAR, NERC P01, ODM2) via le mécanisme Keyword : un `KeywordAssignment` relie la Property à un `Keyword` dont le `uri` porte l'URI du terme, et un code de registre propre (SANDRE) passe lui par `Identifier`. Voir le critère `Identifier` contre `Keyword` dans la sous-section Pattern TPC resource.
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
  définitions ontologiques des unités. Rattachement via le mécanisme Keyword
  (`Keyword.uri`), pas via une colonne dédiée (symétrique de Property).
- [UCUM (Unified Code for Units of Measure)](https://ucum.org/) - alternative
  syntaxique compacte pour exprimer les unités (`mg/L`, `m3/s`). Rattachement
  également via Keyword, en complément de QUDT.

*Utilisé par* :<br>
Property (defaultUnit), TimeSeries (unit), TransformedTimeSeries (unit), Datastream (unitOfMeasurement)

*Relations inverses (requêter par resourceType='Unit')* :<br>
KeywordAssignment

*Note* : 
- HydroServer ajoute Unit comme entité séparée car STA standard n'a qu'un objet JSON inline pour unitOfMeasurement dans Datastream.
- Rattachement aux thésaurus d'unités (QUDT, UCUM) via le mécanisme Keyword,
  symétrique de Property : un `KeywordAssignment` relie la Unit à un `Keyword`
  dont le `uri` porte l'URI du terme. Une même Unit peut s'aligner sur plusieurs
  thésaurus (QUDT et UCUM à la fois). Voir le critère `Identifier` contre
  `Keyword` dans la sous-section Pattern TPC resource.

| Champ        | Cardinalité | Définition                          | Valeurs possibles                          |
|--------------|-------------|-------------------------------------|--------------------------------------------|
| `id`         | 1           | Identifiant technique, clé primaire | uuid                                       |
| `code`       | 1           | Code court pour URLs (kebab-case)   | "mg-l" \| "m3-s" \| "degc"                 |
| `symbol`     | 1           | Symbole textuel affiché             | "mg/L" \| "m³/s" \| "°C"                   |
| `name`       | 1           | Nom complet de l'unité              | "milligram per litre"                      |
| `definition` | 0..1        | Définition textuelle                | "Milligramme par litre d'eau"              |
| `archivedAt` | 0..1        | Horodatage d'archivage logique      | null \| "2024-01-01T00:00:00Z"             |

---

## Procedure
> Protocole appliqué - de prélèvement, mesure, analyse, modélisation, agrégation, transformation ou validation.

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
TimeSeries (procedureObservation, procedureValidation, procedureSampling), ControlObservation (procedureObservation), TransferFunction (procedureModeling), TransformedTimeSeries (procedureTransformation), Datastream (procedureObservation), Specimen (procedureSampling), AnalysisBatch (procedure)

*Note* :
- Entité réutilisable - une même Procedure peut être référencée par plusieurs objets. Le type discrimine le rôle et filtre les choix dans l'interface.
- Types et exemples :
  * **sampling** - prélever un échantillon terrain (ex : "Prélèvement eau de surface au seau", "Prélèvement automatique ISCO 3700")
  * **observation** - mesurer une valeur par capteur continu ou instrument de terrain (ex : "Mesure sonde multiparamètre YSI EXO2", "Jaugeage au micro-moulinet OTT C2")
  * **analysis** - analyser un Specimen en laboratoire (ex : "NF EN ISO 10304-1 chromatographie ionique nitrates", "ICP-MS métaux traces eau", "DOC par combustion catalytique Shimadzu")
  * **modeling** - construire un modèle depuis des mesures ("BaRatin v3 - courbe de tarage bayésienne", "Régression polynomiale turbidité/MES")
  * **aggregation** - agréger temporellement ou spatialement des valeurs (ex : "Moyenne journalière sur plage horaire", "Cumul pluviométrique mensuel")
  * **transformation** - appliquer un calcul pour produire de nouvelles valeurs (ex : "Application courbe de tarage par interpolation linéaire", "Correction offset dérive capteur")
  * **validation** - qualifier des données existantes (ex : "Validation visuelle Wiski par opérateur", "Pipeline automatique contrôle bornes SANDRE")

| Champ          | Cardinalité | Définition                          | Valeurs possibles                                                                              |
|----------------|-------------|-------------------------------------|------------------------------------------------------------------------------------------------|
| `id`           | 1           | Identifiant technique, clé primaire | uuid                                                                                           |
| `code`         | 1           | Slug unique globalement             | "iso-10304-1"                                                                                  |
| `name`         | 1           | Nom du protocole                    | "NF EN ISO 10304-1"                                                                            |
| `type`         | 1           | Rôle du protocole                   | `sampling` \| `observation` \| `analysis` \| `modeling` \| `aggregation` \| `transformation` \| `validation` |
| `description`  | 0..1        | Description libre                   |                                                                                                |
| `version`      | 0..1        | Version du protocole                | "2021"                                                                                         |
| `reference`    | 0..1        | URI ou DOI du document normatif     | "https://www.iso.org/standard/..."                                                             |
| `encodingType` | 1           | Type d'encodage (conformité STA)    | "application/pdf" \| URI                                                                       |
| `archivedAt`   | 0..1        | Horodatage d'archivage logique      | null \| "2024-01-01T00:00:00Z"                                                                 |

---

## Choix enum SQL ou vocabulaire Keyword

Deux mécanismes coexistent pour les valeurs contrôlées : les **enums SQL**,
figés dans le schéma, et le **quadriptyque Keyword** (KeywordType, Keyword,
KeywordAssignment, KeywordRequirement), évolutif sans migration. La règle de
choix, à appliquer champ par champ :

Un champ reste **enum SQL** si les trois conditions sont vraies. Sinon, c'est un
**Keyword**.

1. **Branchement de forme** : le code branche sur la valeur. La logique de calcul,
   une contrainte d'intégrité ou une résolution de FK polymorphe changent selon
   la valeur, pas seulement l'affichage.
2. **Ensemble fermé** : l'ensemble est petit et énumérable aujourd'hui, et ne
   grandit pas par l'usage métier.
3. **Évolution par le développement** : ajouter une valeur implique du code
   nouveau, c'est donc un acte de développement (migration légitime), pas un acte
   de curation.

Le critère discriminant est : *garde-fou de forme* (reste SQL) contre *étiquette
descriptive* (peut devenir Keyword). Une classification purement descriptive,
sans branchement et à liste ouverte par le métier, est un Keyword.

Application au modèle actuel (tous en SQL) :
- Discriminants TPC : `agentType`, `anchorType`, `resourceType`, `seriesType`,
  `systemType`, `codeType`. Une valeur de plus = une cible de FK polymorphe de
  plus = du code de résolution. Restent SQL.
- États et qualité : `status` (toutes entités), `qualityFlag`. Machines à états
  sur lesquelles reposent filtres et transitions. Restent SQL.
- Comportementaux fermés : `depthReference`, `origin`, `acquisitionType`,
  `transmissionMode`, `validationMode`. Petits, fermés, branchés. Restent SQL.
- Classifications portant un garde-fou : `aggregationStatistic` (le calcul et
  l'interprétation dépendent du type, ex. `sporadic` conditionne
  `observationFrequency`) et `Procedure.type` (garde-fou structurel : la bonne
  procédure au bon emplacement, ex. `procedureObservation` doit être de type
  observation sur TimeSeries). Restent SQL malgré leur apparence d'étiquette,
  parce qu'ils portent un branchement de forme.

Les vocabulaires métier sans branchement (disciplines, thèmes, types de station,
milieux...) passent par Keyword.

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

Chaque ligne montre, pour un type de keyword, des exemples de termes sous
leurs deux formes : `term_en` (le libellé lisible) et `notation` (l'identifiant
court qui servirait de segment d'URI).

| keywordType        | S'applique à                   | Exemples (`term_en` -> `notation`)                                              | Standard         |
|--------------------|--------------------------------|---------------------------------------------------------------------------------|------------------|
| `discipline`       | Property                       | hydrology -> `hydrology`, chemistry -> `chemistry`                              | ISO 19115        |
| `theme`            | Property                       | metals -> `metals`, nutrients -> `nutrients`, pesticides -> `pesticides`        | ISO 19115        |
| `samplingMedium`   | TimeSeries, Specimen, Property | surface water -> `surface-water`, groundwater -> `groundwater`                  | ODM2             |
| `featureType`      | FeatureOfInterest              | river -> `river`, lake -> `lake`, atmosphere -> `atmosphere`                    | ODM2 / OMS       |
| `siteType`         | Site                           | watershed -> `watershed`, wetland -> `wetland`, aquifer -> `aquifer`            | BDOH             |
| `stationType`      | Station                        | stream gage -> `stream-gage`, weather station -> `weather-station`              | SANDRE / WMO     |
| `sensorType`       | System (sensor)                | ICP-MS -> `icp-ms`, spectrophotometer -> `spectrophotometer`                    | Helmholtz SMS-CV |
| `platformType`     | System (platform)              | buoy -> `buoy`, vertical chain -> `vertical-chain`, drone -> `drone`            | Helmholtz SMS-CV |
| `equipmentType`    | System (equipment)             | bottle -> `bottle`, autosampler -> `autosampler`, filter holder -> `filter-holder` | Helmholtz SMS-CV |
| `organizationType` | Organization                   | laboratory -> `laboratory`, monitoring network -> `monitoring-network`          | ODM2             |
| `specimenType`     | Specimen                       | water -> `water`, soil -> `soil`, sediment -> `sediment`                        | ODM2             |
| `controlType`      | ControlObservation             | independent measure -> `independent-measure`, cross validation -> `cross-validation` | BDOH        |
| `memoryType`       | Memory                         | note -> `note`, event -> `event`, maintenance -> `maintenance`                  | BDOH             |

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
- `notation` : identifiant court du terme, destiné à servir de segment d'URI
  si BDOH publie son vocabulaire (équivalent de `skos:notation`). Suggéré
  automatiquement à la création depuis `term_en` (minuscules, accents et
  caractères spéciaux retirés, espaces remplacés par des tirets : "Surface
  water" donne "surface-water"), ajustable à la création, puis **immuable** :
  contrairement au `code` des autres entités, il ne doit plus changer une
  fois posé, car des URIs publiques peuvent en dépendre. Unique par
  `keywordType` : deux keywords d'un même type ne peuvent pas partager la
  même notation (l'URI publiée porte le type dans son chemin).
- Chaque terme doit idéalement pointer vers un thésaurus externe via uri.
- Les termes BDOH sans équivalent externe utilisent thesaurus='BDOH'.
- Utilisé de deux façons :
  1. Via KeywordAssignment - tags multi-valeurs sur une ressource
  2. Via FK directe - champ type sur Organization, Site, Station, etc.

| Champ          | Cardinalité | Définition                          | Valeurs possibles                                |
|----------------|-------------|-------------------------------------|--------------------------------------------------|
| `id`           | 1           | Identifiant technique, clé primaire | uuid                                             |
| `keywordType`  | 1 →KWT      | Type de ce keyword                  | → KeywordType                                    |
| `notation`     | 1           | Identifiant court du terme, unique par keywordType, immuable. Sert de segment d'URI (équivalent skos:notation) | "surface-water" \| "stream-gage" |
| `term_fr`      | 1           | Terme en français                   | "eau de surface" \| "hydrologie"                 |
| `term_en`      | 1           | Terme en anglais                    | "surface water" \| "hydrology"                   |
| `definition_fr`| 0..1        | Définition en français              |                                                  |
| `definition_en`| 0..1        | Définition en anglais               |                                                  |
| `thesaurus`    | 0..1        | Vocabulaire source                  | "ODM2" \| "TheiaOZCAR" \| "SANDRE" \| "BDOH"     |
| `uri`          | 0..1        | URI du terme dans le thésaurus      | "http://vocabulary.odm2.org/medium/surfaceWater" |
| `archivedAt`   | 0..1        | Horodatage d'archivage logique      | null \| "2024-01-01T00:00:00Z"                   |

---

## KeywordAssignment
> Lien entre un keyword et une ressource - pattern TPC resource, multi-valeurs.

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
| `resourceType` | 1           | Type de ressource ciblée            | `Observatory` \| `Site` \| `Station` \| `TimeSeries` \| `TransformedTimeSeries` \| `Bundle` \| `Property` \| `Unit` \| `Organization` \| `System` \| `Deployment` \| `FeatureOfInterest` \| `Specimen` \| `ControlObservation` \| `TransferFunction` \| `TransferFunctionSet` \| `Datastream` \| `Project` \| `Memory` \| `Algorithm` |
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
| `resourceType` | 1           | Type de ressource concerné          | `Organization` \| `Property` \| `FeatureOfInterest` \| `Site` \| `Station` \| `System` \| `TimeSeries` \| `TransformedTimeSeries` \| `ControlObservation` \| `Specimen` \| `Memory` \| `Datastream` |
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
| `isOpen`     | 1           | Licence ouverte (true) ou fermée/restreinte  | true \| false                                   |
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
Observatory, Site, Station, System, TimeSeries, Person, Organization, Specimen, Property, Project, Bundle, Dataset (via resourceType + resourceId) 

*Note* : 
- Permet autant d'identifiants externes que nécessaire sur n'importe quelle ressource.
- `Identifier` porte les identifiants qui désignent **la ressource BDOH elle-même dans un autre système** (relation d'identité : le code SANDRE d'une station, le DOI d'un Bundle, l'ORCID d'une Person). Les URIs de termes de thésaurus (TheiaOZCAR, ODM2, NERC...) ne désignent pas la ressource mais la **classent** dans un vocabulaire : elles passent par `Keyword.uri`, pas par `Identifier`. La distinction n'est pas une question de persistance (les deux types d'URI peuvent être des identifiants persistants), mais de nature du lien : identité d'un côté, classification de l'autre.

| Champ          | Cardinalité | Définition                          | Valeurs possibles                                                            |
|----------------|-------------|-------------------------------------|------------------------------------------------------------------------------|
| `id`           | 1           | Identifiant technique, clé primaire | uuid                                                                         |
| `code`         | 1           | Valeur de l'identifiant             | "V3015810" \| "0000-0001-1234-1234" \| "0-20000-0-06610"                     |
| `codeType`     | 1           | Type d'identifiant                  | `doi` \| `orcid` \| `ror` \| `sandre` \| `wigos` \| `igsn` \| `pidinst` \| `swhid` \| `other` |
| `codeSource`   | 1           | Système ou organisme émetteur       | "SANDRE" \| "TheiaOZCAR" \| "NERC" \| "DataCite" \| "ROR" \| "PIDINST"       |
| `resourceType` | 1           | Type de ressource ciblée            | `Observatory` \| `Site` \| `Station` \| `System` \| `TimeSeries` \| `TransformedTimeSeries` \| `Person` \| `Organization` \| `Specimen` \| `Property` \| `Procedure` \| `FeatureOfInterest` \| `Project` \| `TransferFunction` \| `TransferFunctionSet` \| `Bundle` \| `Dataset` \| `Datastream` \| `Algorithm` |
| `resourceId`   | 1           | UUID de la ressource ciblée         | uuid                                                                         |
| `status`       | 1           | État de l'identifiant                | `active` \| `archived`                                                       |


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

| Champ                | Cardinalité    | Définition                          | Valeurs possibles                        |
|----------------------|----------------|-------------------------------------|------------------------------------------|
| `id`                 | 1              | Identifiant technique, clé primaire | uuid                                     |
| `code`               | 1              | Code court unique, curateur         | "yzr"                                    |
| `name`               | 1              | Nom du réseau                       | "Observatoire de l'Yzeron"               |
| `description`        | 0..1           | Description scientifique            |                                          |
| `location`           | 1 →Loc         | Emprise géographique courante       | → Location                               |
| `startDate`          | 1              | Date de début                       | "2010-01-01"                             |
| `endDate`            | 0..1           | Date de fin, null si actif          | null                                     |
| `status`             | 1              | État de l'observatoire              | `active` \| `inactive` \| `discontinued` |
| `url`                | 0..1           | Site web du réseau                  | "https://..."                            |

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

| Champ         | Cardinalité    | Définition                          | Valeurs possibles              |
|---------------|----------------|-------------------------------------|--------------------------------|
| `id`          | 1              | Identifiant technique, clé primaire | uuid                           |
| `code`        | 1              | Code court unique                   | "yzr-mer"                      |
| `name`        | 1              | Nom du site                         | "Bassin versant du Mercier"    |
| `description` | 0..1           | Description libre                   |                                |
| `Observatory` | 1 →Obs         | Observatoire parent                 | → Observatory                  |
| `location`    | 1 →Loc         | Géométrie courante                  | → Location                     |
| `area`        | 0..1           | Superficie en km²                   | "245.3"                        |
| `archivedAt`  | 0..1           | Horodatage d'archivage logique      | null \| "2024-01-01T00:00:00Z" |

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
- stationType : stream gage, weather station, well, soil pit, lake station, tide gage
	   
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
- sensor : ICP-MS, spectrophotometer, HPLC, probe, autoanalyzer, datalogger
- platform : buoy, vertical chain, drone, multi-probe, weather station, mooring
- equipment : bottle, pump, autosampler, corer, syringe, filter holder

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

| Champ              | Cardinalité | Définition                                       | Valeurs possibles                                            |
|--------------------|-------------|--------------------------------------------------|--------------------------------------------------------------|
| `id`               | 1           | Identifiant technique, clé primaire              | uuid                                                         |
| `code`             | 1           | Slug unique globalement                          | "dep-lac-nord-bouee-2020"                                    |
| `name`             | 1           | Nom du déploiement                               | "Déploiement bouée lac nord 2020"                            |
| `system`           | 1 →Sys      | System déployé                                   | → System                                                     |
| `parentDeployment` | 0..1 →Dep   | Déploiement parent (récursif)                    | → Deployment                                                 |
| `anchorType`       | 0..1        | Type d'ancrage territorial (null si autonome)    | `Station` \| `Site`                                          |
| `anchorId`         | 0..1        | UUID de la Station ou du Site                    | uuid                                                         |
| `location`         | 0..1 →Loc   | Position propre si différente de l'ancre         | → Location                                                   |
| `deploymentDepth`  | 0..1        | Profondeur nominale du System dans ce Deployment | "-1.5"                                                       |
| `depthReference`   | 0..1        | Référence de profondeur                          | `surface_relative` \| `bottom_relative` \| `absolute_elevation` |
| `validFrom`        | 1           | Début du déploiement                             | "2020-06-01T00:00:00Z"                                       |
| `validTo`          | 0..1        | Fin, null si actif                               | null                                                         |
| `status`           | 1           | État du déploiement                              | `active` \| `inactive` \| `removed`                          |


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
- procedure optionnelle (0..1) ici, alors qu'elle est obligatoire (1) sur TimeSeries : volontaire. Un flux brut doit pouvoir être déposé dès l'installation du capteur, avant que le protocole de mesure ne soit formalisé ; il sera enrichi plus tard. La série métier validée, elle, exige un protocole défini.
- aggregationStatistic : nature métrologique de la valeur, aligné ODM2.
  * sporadic = pas de temps irrégulier (crue), observationFrequency null.
  * instantaneous = valeur ponctuelle, phenomenonTimeEnd null.
  * Autres = valeur intégrée sur intervalle, phenomenonTimeEnd renseigné.
- Plage temporelle couverte : non stockée. `phenomenonTimeStart` et `phenomenonTimeEnd` du flux sont calculés à la demande (MIN/MAX du phenomenonTime des Observations), exposés en lecture seule par l'API. Recomposés en l'intervalle `phenomenonTime` à l'export STA.

| Champ                    | Cardinalité | Définition                                | Valeurs possibles                                                |
|--------------------------|-------------|-------------------------------------------|------------------------------------------------------------------|
| `id`                     | 1           | Identifiant technique, clé primaire       | uuid                                                             |
| `code`                   | 1           | Slug unique par ancre (kebab-case)        | "hea-mercier-d610"                                               |
| `name`                   | 1           | Nom du flux                               | "Hauteur d'eau - Mercier D610 - OTT PLS 500"                     |
| `description`            | 0..1        | Description libre                         |                                                                  |
| `unitOfMeasurement`      | 1 →Unit     | Unité de mesure                           | → Unit                                                           |
| `anchorType`             | 1           | Type d'ancrage géographique               | `Observatory` \| `Site` \| `Station`                             |
| `anchorId`               | 1           | UUID de l'Observatory, Site ou Station    | uuid                                                             |
| `system`                 | 1 →Sys      | Capteur source (systemType=sensor)        | → System                                                         |
| `property`               | 1 →Prop     | Variable mesurée (= ObservedProperty STA) | → Property                                                       |
| `procedureObservation`   | 0..1 →Proc  | Protocole de mesure                       | → Procedure (type=observation)                                   |
| `acquisitionType`        | 1           | Mode d'acquisition des données            | `sensor_continuous` \| `lab_sample`                              |
| `aggregationStatistic`   | 1           | Nature métrologique de la valeur          | `instantaneous` \| `average` \| `cumulative` \| `maximum` \| `minimum` \| `variance` \| `standard_deviation` \| `sporadic` |
| `observationFrequency`   | 0..1        | Fréquence nominale (ISO 8601)             | "PT15M" \| "PT1H" - null si aggregationStatistic=sporadic        |
| `status`                 | 1           | État du flux                              | `active` \| `inactive` \| `closed`                               |
| `license`                | 1 →Lic      | Licence des données                       | → License                                                        |
| `transmissionMode`       | 0..1        | Modre d'arrivée des données dans BDOH      | `auto` \| `manual`                                               |

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
- Lie une TimeSeries à ses Datastreams sources dans le temps.
- Cas séquentiel (le plus courant) : un changement de capteur crée un nouveau Datastream et une nouvelle ligne ici, les périodes ne se chevauchent pas.
- Cas parallèle (plusieurs Datastreams simultanés) : explicitement autorisé. Deux capteurs mesurent la même variable en même temps (redondance physique, master/save). Plusieurs lignes coexistent sur la même période, sans contrainte d'unicité par (timeSeries, validFrom). Les métrologues documentent le contexte via `comment` ou `Memory`.
- Consolidation de plusieurs Datastreams vers une TimeSeries : deux voies valides et non exclusives.
  * Voie transformation : `TransformationBatch` multi-entrées, tracé, automatisable.
  * Voie validation manuelle : le validateur consolide à la main dans `ValidatedObservation`, jugement expert, moins tracé mais légitime.
- Couture entre le monde physique (System → Deployment → Datastream) et le monde analytique (TimeSeries → ValidatedObservation).
- La profondeur nominale du capteur est portée par le Deployment correspondant.
- Nommé d'après son rôle (la source d'une TimeSeries), et non avec le préfixe `Historical*` : cette table relie deux entités dans le temps, elle n'historise pas un attribut courant d'une ressource (voir Convention de lecture, pattern des associations datées). Anciens noms : TimeSeriesDatastream, puis HistoricalDatastream.

| Champ        | Cardinalité | Définition                          | Valeurs possibles      |
|--------------|-------------|-------------------------------------|------------------------|
| `id`         | 1           | Identifiant technique, clé primaire | uuid                   |
| `timeSeries`  | 1 →TS       | Série parente                       | → TimeSeries            |
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
- samplingMedium (required) : surface water, groundwater, atmosphere
		 
*Note* : 
- Porte tout ce qui est fixe et commun à toute la série.
- Contrat analytique garantissant la comparabilité de tous les points.
- anchorType + anchorId : pattern TPC - station dans le cas standard, site pour les séries de chimie sans station fixe ou campagnes mobiles.
- Le ou les capteurs courants se retrouvent via TimeSeriesSource WHERE validTo IS NULL (plusieurs résultats possibles en cas de Datastreams parallèles).
- FOI : featureOfInterest porte la FOI proximate si elle diffère de l'ancre.
- Règle de résolution API STA : TimeSeries.featureOfInterest si renseignée, sinon anchor.featureOfInterest.
- Une procédure de validation unique par série - plusieurs validations parallèles sur la même variable impliquent des TimeSeries distinctes.
- Plusieurs TimeSeries peuvent coexister sur la même station et la même variable sans hiérarchie - c'est le contexte scientifique qui désigne laquelle utiliser.
- OZCAR note que leur "Observation" pivot correspond à un Datastream STA.
- Plage temporelle couverte : non stockée. `phenomenonTimeStart` et `phenomenonTimeEnd` de la série sont calculés à la demande (MIN/MAX du phenomenonTime des ValidatedObservations), exposés en lecture seule par l'API. Recomposés en l'intervalle `phenomenonTime` à l'export STA.
- code unique par Station.

| Champ                   | Cardinalité | Définition                                    | Valeurs possibles                                            |
|-------------------------|-------------|-----------------------------------------------|--------------------------------------------------------------|
| `id`                    | 1           | Identifiant technique, clé primaire           | uuid                                                         |
| `code`                  | 1           | Slug unique par ancre                         | "hea-wiski"                                                  |
| `name`                  | 1           | Nom lisible de la série                       | "Hauteur d'eau - Mercier au pont D610"                       |
| `description`           | 0..1        | Description libre                             |                                                              |
| `anchorType`            | 1           | Type d'ancrage géographique                   | `Observatory` \| `Site` \| `Station`                         |
| `anchorId`              | 1           | UUID de l'Observatory, Site ou Station        | uuid                                                         |
| `featureOfInterest`     | 0..1 →FOI   | FOI proximate si différente de l'ancre        | → FeatureOfInterest                                          |
| `property`              | 1 →Prop     | Variable mesurée                              | → Property                                                   |
| `unit`                  | 1 →Unit     | Unité de mesure                               | → Unit                                                       |
| `procedureObservation` | 1 →Proc     | Protocole analytique fixe pour toute la série | → Procedure (type=observation)                               |
| `procedureValidation`  | 1 →Proc     | Procédure de validation de cette série        | → Procedure (type=validation)                                |
| `procedureSampling`    | 0..1 →Proc  | Protocole de prélèvement standard (lab_sample)| → Procedure (type=sampling) - null si sensor_continuous      |
| `acquisitionType`       | 1           | Mode d'acquisition des données                | `sensor_continuous` \| `lab_sample`                          |
| `aggregationStatistic`  | 1           | Nature métrologique de la valeur              | `instantaneous` \| `average` \| `cumulative` \| `maximum` \| `minimum` \| `variance` \| `standard_deviation` \| `sporadic` |
| `observationFrequency`  | 0..1        | Fréquence nominale (ISO 8601)                 | "PT15M" \| "PT1H" - null si aggregationStatistic=sporadic    |
| `status`                | 1           | État de la série                              | `active` \| `inactive` \| `discontinued`                     |
| `license`               | 1 →Lic      | Licence des données                           | → License                                                    |
| `validationFrequency`   | 0..1        | Fréquence de validation auto (ISO 8601)       | "PT15M" \| "P1D" \| "P1W"                                    |
| `validationMode`        | 0..1        | Mode de validation                            | `auto` \| `manual`                                           |

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
| `timeSeries`        | 1 →TS       | Série validée                       | → TimeSeries                              |
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
| `timeSeries`           | 1 →TS       | Série parente                                       | → TimeSeries                               |
| `phenomenonTimeStart` | 1           | Début de la période du phénomène                    | "2024-03-15T09:30:00Z"                    |
| `phenomenonTimeEnd`   | 0..1        | Fin de la période, null si instantané               | "2024-03-15T10:00:00Z" \| null            |
| `resultTime`          | 0..1        | Instant de production du résultat                   | "2024-03-15T09:35:00Z"                    |
| `result`              | 1           | Valeur numérique mesurée                            | "2.4"                                     |
| `qualityFlag`         | 1           | Indicateur qualité (mapping ODM2/SANDRE en annexe)  | `good` \| `suspect` \| `bad` \| `missing` |
| `qualityComment`      | 0..1        | Justification libre du flag qualité                 | "pic de crue suspect"                     |
| `uncertaintyLow`      | 0..1        | Borne basse de l'incertitude (asymétrique)          | -0.15                                     |
| `uncertaintyHigh`     | 0..1        | Borne haute de l'incertitude (asymétrique)          | 0.22                                      |
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
- controlType : independent measure, cross validation, reference gauge

*Note* : 
- Se greffe directement sur une TimeSeries ou TransformedTimeSeries sans Datastream dédié.
- Le System et la procédure diffèrent intentionnellement de ceux de la série parente - c'est une mesure indépendante pour vérifier la cohérence (ex : jaugeage de vérification sur une série de débit calculé, mesure avec un System étalonné de référence, comparaison avec une station voisine).
- seriesType + seriesId : pattern TPC - TimeSeries ou TransformedTimeSeries. C'est le lien obligatoire et porteur de sens.
- system : contrainte applicative systemType=sensor. Optionnel. Rattache la mesure à son instrument, exactement comme Datastream pointe vers System. La chaîne instrumentale complète se lit ControlObservation -> System -> Deployment -> Station/Site : l'instrument (règle à jauger, System étalon...) est déployé via un Deployment comme tout matériel, et ce déploiement lui donne son ancrage physique. Pas de lien direct vers Deployment. Si l'utilisateur ne renseigne pas l'instrument, le rattachement à la série (seriesType/seriesId) suffit.
- qualityFlag : optionnel. Qualifie la fiabilité de la mesure de contrôle elle-même (un jaugeage de vérification peut être douteux), avec le même vocabulaire que ValidatedObservation. Laissé vide si non évalué.

| Champ                   | Cardinalité | Définition                                          | Valeurs possibles                       |
|-------------------------|-------------|-----------------------------------------------------|-----------------------------------------|
| `id`                    | 1           | Identifiant technique, clé primaire                 | uuid                                    |
| `seriesType`             | 1           | Type de la série contrôlée                          | `TimeSeries` \| `TransformedTimeSeries`   |
| `seriesId`               | 1           | UUID de la TimeSeries ou TransformedTimeSeries        | uuid                                    |
| `phenomenonTimeStart`   | 1           | Début de la période du phénomène                    | "2024-03-15T09:30:00Z"                  |
| `phenomenonTimeEnd`     | 0..1        | Fin de la période, null si instantané               | "2024-03-15T10:00:00Z" \| null          |
| `resultTime`            | 0..1        | Instant de production du résultat                   | "2024-03-15T09:35:00Z"                  |
| `result`                | 1           | Valeur mesurée                                      | "0.02"                                  |
| `expectedResult`        | 0..1        | Valeur attendue selon la série                      | "0.021"                                 |
| `qualityFlag`           | 0..1        | Qualité de la mesure de contrôle elle-même          | `good` \| `suspect` \| `bad` \| `missing` |
| `qualityComment`        | 0..1        | Justification libre                                 | "écart de 5% - dérive capteur probable" |
| `system`                | 0..1 →Sys   | System utilisé pour le contrôle (systemType=sensor) | → System                                |
| `procedureObservation` | 1 →Proc     | Protocole de mesure appliqué                        | → Procedure (type=observation)          |
| `specimen`              | 0..1 →Spec  | Prélèvement terrain associé                         | → Specimen                              |
| `featureOfInterest`     | 0..1 →FOI   | Entité réelle observée                              | → FeatureOfInterest                     |

---

## AnalysisBatch
> Acte analytique en laboratoire sur un Specimen - qui a analysé quoi, avec quel appareil et quelle méthode.

*Aligné avec* :
- [ODM2 LabAnalyses](https://github.com/ODM2/ODM2/blob/master/doc/ODM2Docs/ext_labanalyses.md)
  - extension ODM2 dédiée aux analyses ex situ sur échantillons ; AnalysisBatch
  correspond à l'Action d'analyse ODM2 (type=laboratoryAnalysis) portant la
  méthode, l'équipement et l'opérateur.
- [CUAHSI ODM2 Specimen Actions](https://github.com/ODM2/ODM2/blob/master/doc/ODM2Docs/core_actions.md)
  - la chaîne CUAHSI (prélèvement, préparation, analyse) se modélise par
  filiation de Specimens (derivedFrom) et un AnalysisBatch par étape d'analyse.

*Utilisé par* :<br>
AnalysisObservation (analysisBatch)

*Note* :
- Frère des autres Batch (ValidationBatch, TransformationBatch...) : un acte daté,
  attribué à un agent, produisant des observations. Même famille, même pattern.
- Porte les métadonnées de la session analytique, communes à toutes les mesures
  de cette session. Les métadonnées propres à chaque mesure individuelle (LD, LQ,
  qualityFlag) vivent sur AnalysisObservation.
- system optionnel : l'appareil analytique (ICP-MS, spectromètre...) est un System
  de type sensor ou equipment. Même pattern que partout dans le modèle.
- Coexistence LIMS/interne : si la chimie est traitée dans un LIMS externe,
  Specimen.limsReference suffit et AnalysisBatch n'est pas créé. Si la chaîne
  analytique est interne, AnalysisBatch + AnalysisObservation la documentent
  complètement. Les deux voies sont non exclusives (ADR-007 amendé).
- Filiation des Specimens : prélèvement brut → Specimen enfant filtré (derivedFrom)
  → Specimen aliquote → AnalysisBatch. La chaîne CUAHSI (collecte, préparation,
  analyse) passe par la filiation des Specimens, pas par une hiérarchie de batchs.

| Champ             | Cardinalité | Définition                                    | Valeurs possibles               |
|-------------------|-------------|-----------------------------------------------|---------------------------------|
| `id`              | 1           | Identifiant technique, clé primaire           | uuid                            |
| `specimen`        | 1 →Spec     | Specimen analysé (brut ou aliquote préparé)   | → Specimen                      |
| `procedure`       | 1 →Proc     | Méthode analytique appliquée                  | → Procedure (type=analysis)     |
| `agentType`       | 1           | Type d'agent ayant réalisé l'analyse          | `Person` \| `Machine`           |
| `agentId`         | 1           | UUID de la Person ou Machine                  | uuid                            |
| `system`          | 0..1 →Sys   | Appareil analytique utilisé                   | → System                        |
| `analysisDateTime`| 1           | Date et heure de l'analyse                    | "2024-03-14T14:00:00Z"          |
| `comment`         | 0..1        | Commentaire libre sur la session              |                                 |
| `status`          | 1           | État du batch                                 | `active` \| `archived`          |

---

## AnalysisObservation
> Valeur mesurée sur un Specimen par un acte analytique - symétrique de ValidatedObservation pour la chimie.

*Aligné avec* :
- [ODM2 Measurement Result](https://github.com/ODM2/ODM2/blob/master/doc/ODM2Docs/results_measurement.md)
  - un Measurement Result ODM2 est une valeur unique pour une variable, mesurée
  sur un Specimen via une méthode analytique. AnalysisObservation en est la
  traduction directe dans BDOH.
- [OGC OMS (ISO 19156:2023)](https://docs.ogc.org/as/20-082r4/20-082r4.html)
  - observation au sens OMS : acte de mesure produisant un résultat, ici sur un
  Specimen (SamplingFeature de type SF_Specimen).

*Utilisé par* :<br>
TimeSeries (observations, acquisitionType=lab_sample)

*Note* :
- Symétrique de ValidatedObservation pour les séries issues de prélèvements. Même
  structure de base (phenomenonTime, result, qualityFlag, uncertainty), mêmes
  règles d'appartenance à une TimeSeries.
- La TimeSeries est le flux unifiant : elle porte la property, l'unité, la
  procédure nominale, la license. AnalysisObservation porte la valeur et ses
  métadonnées analytiques propres à la mesure individuelle.
- detectionLimit / quantificationLimit : valeurs de la session analytique de ce
  batch précis (pas de la méthode en général, qui peut varier selon la matrice
  et l'étalonnage du jour).
- phenomenonTimeStart : instant du prélèvement (porté par le Specimen parent),
  pas l'instant de l'analyse (qui est sur l'AnalysisBatch).
- uncertaintyLow/High : cohérent avec ADR-057 ; l'incertitude analytique est
  souvent asymétrique et dépend de la zone de la courbe d'étalonnage.

| Champ                 | Cardinalité | Définition                                              | Valeurs possibles                         |
|-----------------------|-------------|---------------------------------------------------------|-------------------------------------------|
| `id`                  | 1           | Identifiant technique, clé primaire                     | uuid                                      |
| `timeSeries`          | 1 →TS       | Série parente (acquisitionType=lab_sample)              | → TimeSeries                              |
| `analysisBatch`       | 1 →AB       | Batch analytique ayant produit cette valeur             | → AnalysisBatch                           |
| `phenomenonTimeStart` | 1           | Instant du prélèvement (date d'échantillonnage)         | "2024-03-12T09:00:00Z"                    |
| `phenomenonTimeEnd`   | 0..1        | Fin de la période, null si ponctuel                     | null                                      |
| `result`              | 1           | Valeur numérique mesurée                                | "2.3"                                     |
| `detectionLimit`      | 0..1        | Limite de détection de la session analytique            | 0.01                                      |
| `quantificationLimit` | 0..1        | Limite de quantification de la session analytique       | 0.05                                      |
| `qualityFlag`         | 0..1        | Indicateur qualité                                      | `good` \| `suspect` \| `bad` \| `missing` |
| `qualityComment`      | 0..1        | Justification libre du flag qualité                     | "valeur sous LD, résultat non quantifié"  |
| `uncertaintyLow`      | 0..1        | Borne basse de l'incertitude analytique                 | -0.1                                      |
| `uncertaintyHigh`     | 0..1        | Borne haute de l'incertitude analytique                 | 0.1                                       |

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
- samplingMedium (required) : surface water, groundwater, depth

*Note* : 
- Acte de prélèvement physique - un flacon rempli, un piège récolté.
- Distinct de Station (point de surveillance spatial permanent).
- anchorType + anchorId : pattern TPC, même pattern que Deployment - station dans le cas standard, site pour les campagnes sans station fixe.
- Cohérence applicative : anchorType/anchorId doit correspondre à l'ancrage des Deployments associés via specimen_deployment.
- Lien aux Deployments via la table de jointure `specimen_deployment` : un prélèvement peut mobiliser plusieurs équipements simultanément (pompe + flacon + filtre = trois Deployments pour un Specimen), et un Deployment peut produire plusieurs Specimens dans le temps (piège récolté chaque semaine pendant un mois). L'ancrage géographique du Specimen est hérité du Deployment.
- Deux voies non exclusives pour la chaîne analytique : LIMS externe référencé
  par limsReference seul, ou chaîne interne documentée par AnalysisBatch et
  AnalysisObservation. Voir la note d'AnalysisBatch (Coexistence LIMS/interne,
  ADR-007 amendé), qui est la source de vérité de cette articulation.
- status : l'échantillon physique existe-t-il encore ou a-t-il été détruit
  (épuisé par les analyses, contaminé, périmé). Distinct de la chaîne
  analytique (résultats, méthode, voir AnalysisBatch, souvent documentée dans
  BDOH) et de l'inventaire fin (aliquotage, quantité restante), qui reste au
  LIMS externe s'il est utilisé ; BDOH trace l'existence du Specimen, pas son
  inventaire physique détaillé.
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
| `status`              | 1           | État physique de l'échantillon                | `active` \| `discarded`       |

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
- [GUM - Guide to the Expression of Uncertainty in Measurement (JCGM 100:2008)](https://www.bipm.org/documents/20126/2071204/JCGM_100_2008_E.pdf)
  - cadre métrologique de référence pour l'expression et la propagation de
  l'incertitude ; les lois marginales de TransferFunctionParameter s'inscrivent
  dans ce cadre.

*Utilisé par* :<br>
transferfunctionset_function (transferFunction), TransferFunctionBatch (transferFunction),
TransferFunctionPoint (function), TransferFunctionParameter (function)

*Relations inverses (requêter par resourceType='TransferFunction')* :<br>
Responsibility, Identifier, Memory

*Note* :
- Fonction de conversion liée à une station - analogue à TimeSeries.
- Objet de réservoir : une TF existe indépendamment de tout TFSet et peut être référencée par plusieurs TFSet (via transferfunctionset_function).
- Dualité empirique / modèle : deux faces complémentaires d'une même réalité.
  * `TransferFunctionPoint` : la face empirique (les jaugeages, les couples x/y mesurés terrain).
  * `TransferFunctionParameter` : la face modèle (les coefficients de la courbe ajustée, avec leur distribution d'incertitude).
  * `TransferFunctionBatch` : l'acte de calage (qui a construit la courbe, quand, avec quel outil).
- inputProperty/outputProperty fixent la sémantique de la fonction (hauteur -> débit) : ils permettent de vérifier au moment du calcul qu'une série d'entrée et la TTS produite portent les bonnes variables.
- Pas de validFrom/validTo propres : la période d'application d'une TF est portée par la jointure transferfunctionset_function. La période d'acquisition des données de calibration est portée par acquisitionStart/acquisitionEnd, la date de construction par TransferFunctionBatch.builtAt.
- covariance : matrice de covariance entre coefficients (JSON), optionnelle. Nécessaire pour la propagation d'incertitude correcte (tirage multivarié) quand les coefficients ne sont pas indépendants. C'est le seul JSON résiduel justifié ici : une matrice dense ne se décompose pas naturellement en lignes sans artifice.
- anchorType + anchorId : pattern TPC - station dans le cas standard.

| Champ               | Cardinalité | Définition                              | Valeurs possibles                      |
|---------------------|-------------|-----------------------------------------|----------------------------------------|
| `id`                | 1           | Identifiant technique, clé primaire     | uuid                                   |
| `code`              | 1           | Slug unique par ancre                   | "hea-qmj-v3"                           |
| `name`              | 1           | Nom de la fonction                      | "Courbe de tarage Mercier D610 v3"     |
| `description`       | 0..1        | Description libre                       |                                        |
| `anchorType`        | 1           | Type d'ancrage géographique             | `Observatory` \| `Site` \| `Station`   |
| `anchorId`          | 1           | UUID de l'Observatory, Site ou Station  | uuid                                   |
| `inputProperty`     | 1 →Prop     | Variable en entrée                      | → Property (ex: hauteur)               |
| `outputProperty`    | 1 →Prop     | Variable en sortie                      | → Property (ex: débit)                 |
| `covariance`        | 0..1        | Matrice de covariance entre coefficients (JSON) | {"a_b": -0.3, "a_c": 0.1}      |
| `procedureModeling` | 0..1 →Proc  | Méthode de construction de la fonction  | → Procedure (type=modeling)            |
| `acquisitionStart`  | 0..1        | Début de la période d'acquisition       | "2023-06-01"                           |
| `acquisitionEnd`    | 0..1        | Fin de la période d'acquisition         | "2023-11-30"                           |
| `status`            | 1           | État de la fonction                     | `active` \| `inactive` \| `deprecated` |

---

## TransferFunctionPoint
> Couple (x, y) de calibration issu d'un jaugeage terrain - définit empiriquement la courbe.

*Utilisé par* :<br>
TransferFunction (via function FK - relation inverse)

*Note* :
- Face empirique de la TransferFunction : les données de terrain brutes (jaugeages, mesures de référence).
- Analogue à ValidatedObservation : c'est là que vivent les données (ex : hauteur=1.23m, débit=4.5m³/s pour une courbe de tarage).
- uncertaintyX/uncertaintyY : incertitude sur la mesure du jaugeage elle-même. L'incertitude sur la hauteur lue et sur le débit mesuré sont deux composantes distinctes, toutes deux nécessaires pour la propagation BaRatin (l'incertitude en basses eaux sur x peut dominer celle sur la courbe). Optionnelles mais recommandées pour les utilisateurs de BaRatin.

| Champ          | Cardinalité | Définition                               | Valeurs possibles       |
|----------------|-------------|------------------------------------------|-------------------------|
| `id`           | 1           | Identifiant technique, clé primaire      | uuid                    |
| `function`     | 1 →TF       | Fonction parente                         | → TransferFunction      |
| `batch`        | 0..1 →TFB   | Batch de construction parent             | → TransferFunctionBatch |
| `x`            | 1           | Valeur en entrée (ex: hauteur)           | 1.23                    |
| `y`            | 1           | Valeur en sortie (ex: débit)             | 4.5                     |
| `uncertaintyX` | 0..1        | Incertitude sur x (ex: erreur de hauteur) | 0.02                   |
| `uncertaintyY` | 0..1        | Incertitude sur y (ex: erreur de débit)  | 0.15                    |
| `datetime`     | 0..1        | Date du jaugeage ou de la mesure         | "2024-03-15T09:30:00Z"  |
| `comment`      | 0..1        | Commentaire libre                        | "jaugeage crue"         |

---

## TransferFunctionParameter
> Coefficient du modèle ajusté sur une TransferFunction, avec sa loi d'incertitude marginale.

*Aligné avec* :
- [GUM - Guide to the Expression of Uncertainty in Measurement (JCGM 100:2008)](https://www.bipm.org/documents/20126/2071204/JCGM_100_2008_E.pdf)
  - chaque paramètre est caractérisé par une loi de distribution (type, paramètres)
  conforme au cadre GUM pour l'expression de l'incertitude.
- [BaRatin / Le Coz et al. 2014](https://doi.org/10.1016/j.jhydrol.2013.11.016)
  - les coefficients hydrauliques d'une courbe de tarage BaRatin sont distribués
  (loi postérieure bayésienne) ; TransferFunctionParameter en est le réceptacle.

*Utilisé par* :<br>
TransferFunction (via function FK - relation inverse)

*Note* :
- Face modèle de la TransferFunction, frère de TransferFunctionPoint.
- Chaque ligne est un coefficient de la courbe ajustée (a, b, c pour une loi puissance Q = a(H-b)^c) avec sa distribution marginale.
- La valeur centrale (`value`) est la courbe maximale a posteriori (MAP), celle appliquée pour le calcul nominal.
- distributionType + distributionParam1/2 décrivent la loi marginale de ce coefficient : loi normale, log-normale, uniforme, etc. Ce résumé paramétrique permet de régénérer l'ensemble de courbes (spaghetti) pour la propagation d'incertitude sans stocker les milliers de tirages.
- Les corrélations entre coefficients (nécessaires pour un tirage multivarié correct) vivent dans TransferFunction.covariance. La combinaison lignes TransferFunctionParameter + matrice covariance est le générateur complet de l'ensemble spaghetti.
- La temporalité : une TF par période (via transferfunctionset_function), donc des paramètres par période, donc les "vecteurs de paramètres qui évoluent dans le temps" sont la succession des TF dans un TFSet. Pas de table temporelle supplémentaire.
- Objet voué à évoluer : si la méthode de caractérisation de la loi postérieure évolue (approche ensembliste plus riche, hyperparamètres supplémentaires), on enrichit les champs sans casser la structure. Le réceptacle est stable, son contenu peut grandir.

| Champ                | Cardinalité | Définition                                         | Valeurs possibles                                      |
|----------------------|-------------|----------------------------------------------------|--------------------------------------------------------|
| `id`                 | 1           | Identifiant technique, clé primaire                | uuid                                                   |
| `function`           | 1 →TF       | Fonction parente                                   | → TransferFunction                                     |
| `name`               | 1           | Nom du coefficient                                 | "a", "b", "c", "K", "alpha"                            |
| `value`              | 1           | Valeur centrale (max a posteriori)                 | 2.1                                                    |
| `distributionType`   | 0..1        | Forme de la loi marginale                          | `normal` \| `lognormal` \| `uniform` \| `gamma`        |
| `distributionParam1` | 0..1        | Premier paramètre de la loi                        | écart-type si normal, sigma si lognormal, min si uniform |
| `distributionParam2` | 0..1        | Second paramètre de la loi si nécessaire           | max si uniform, alpha si gamma                         |
| `unit`               | 0..1 →Unit  | Unité du coefficient                               | → Unit                                                 |
| `comment`            | 0..1        | Description du rôle du coefficient                 | "coefficient de débit section pleine"                  |

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

| Champ               | Cardinalité | Définition                             | Valeurs possibles               |
|---------------------|-------------|----------------------------------------|---------------------------------|
| `id`                | 1           | Identifiant technique, clé primaire    | uuid                            |
| `transferFunction`  | 1 →TF       | Fonction construite                    | → TransferFunction              |
| `builtAt`           | 1           | Date de construction                   | "2024-04-01T08:00:00Z"          |
| `agentType`         | 0..1        | Type d'agent ayant construit la courbe | `Person` \| `Machine`           |
| `agentId`           | 0..1        | UUID de la Person ou Machine           | uuid                            |
| `logUrl`            | 0..1        | Référence externe (export BaRatin..)   | "https://..."                   |
| `status`            | 1           | État du batch                          | `pending` \| `done` \| `failed` |
| `comment`           | 0..1        | Commentaire libre                      |                                 |

---

## TransferFunctionSet
> Jeu ordonné de TransferFunction qui se succèdent dans le temps - le barème appliqué à une série pour produire une TTS.

*Aligné avec* :
- [WMO - Manual on Stream Gauging, Vol. II](https://library.wmo.int/records/item/35841-manual-on-stream-gauging-vol-ii-computation-of-discharge)
  - un jeu de fonctions de transfert correspond à la succession temporelle des
  courbes de tarage d'une station (gestion des changements de tarage).
- [ODM2 Methods](https://github.com/ODM2/ODM2/blob/master/doc/ODM2Docs/core_methods.md)
  - le regroupement de méthodes appliquées dans le temps sur une même station.

*Utilisé par* :<br>
TransformationBatch (transferFunctionSet)

*Relations inverses* :<br>
transferfunctionset_function (les TF composant le jeu, avec leur période d'application)

*Note* : 
- Compose une ou plusieurs TransferFunction qui se succèdent dans le temps (via transferfunctionset_function, qui porte la période d'application de chaque TF dans ce jeu).
- Les TF sont piochées dans le réservoir de TransferFunction : une même TF peut servir dans plusieurs TFSet.
- Un seul TFSet est utilisé par TransformationBatch pour produire une TTS. La période sur laquelle ce TFSet s'applique à la TTS est portée par le batch.
- Plusieurs TFSet peuvent coexister sur une station sans hiérarchie imposée : c'est le contexte scientifique qui désigne lequel utiliser (même principe que TimeSeries/TransformedTimeSeries).
- Pas de validFrom/validTo propres : la composition temporelle interne est dans la jointure, la période d'application à une TTS est sur le batch.

| Champ              | Cardinalité | Définition                             | Valeurs possibles                    |
|--------------------|-------------|----------------------------------------|--------------------------------------|
| `id`               | 1           | Identifiant technique, clé primaire    | uuid                                 |
| `code`             | 1           | Slug unique par ancre                  | "bareme-mercier-d610-2024"           |
| `name`             | 1           | Nom du jeu                             | "Barème Mercier D610 2024"           |
| `description`      | 0..1        | Description libre                      |                                      |
| `anchorType`       | 1           | Type d'ancrage géographique            | `Observatory` \| `Site` \| `Station` |
| `anchorId`         | 1           | UUID de l'Observatory, Site ou Station | uuid                                 |
| `status`           | 1           | État du jeu                            | `active` \| `archived`               |
| `comment`          | 0..1        | Justification du choix                 | "nouveau jaugeage après crue"        |

---

## transferfunctionset_function
> Composition d'un TransferFunctionSet : quelles TransferFunction le composent, et sur quelle période chacune s'applique dans ce jeu - table de jointure.

*Note* :
- Relie un TFSet aux TransferFunction qu'il compose (many-to-many : une TF peut appartenir à plusieurs TFSet, un TFSet contient une ou plusieurs TF).
- validFrom/validTo donnent la plage temporelle d'application de cette TF dans ce TFSet précis : c'est ici que vit la succession des courbes (courbe A jusqu'en 2015, courbe B ensuite...).
- La même TF peut avoir des périodes d'application différentes dans deux TFSet distincts.

| Champ                | Cardinalité | Définition                                     | Valeurs possibles      |
|----------------------|-------------|------------------------------------------------|------------------------|
| `transferFunctionSet` | 1 →TFS      | Jeu parent                                     | → TransferFunctionSet  |
| `transferFunction`   | 1 →TF       | Fonction incluse dans le jeu                    | → TransferFunction     |
| `validFrom`          | 1           | Début d'application de cette TF dans ce jeu     | "2015-01-01T00:00:00Z" |
| `validTo`            | 0..1        | Fin d'application, null si courante             | null                   |

---

## Algorithm
> Code référencé et versionné sur une forge - script ou fonction utilisé par un TransformationBatch.

*Aligné avec* :
- [CodeMeta](https://codemeta.github.io/) - vocabulaire pour les métadonnées
  logicielles, basé sur [schema.org/SoftwareApplication](https://schema.org/SoftwareApplication).
  Inspire les champs `codeRepository`, `path`, `version`.
- [SWHID - ISO/IEC 18670:2025](https://www.swhid.org/swhid-specification/) -
  identifiant intrinsèque permanent du code source. Un même swhid identifie
  toujours le même état exact du code, indépendamment de sa localisation.
  Porté par `Identifier` (codeType=swhid).
- [Software Heritage](https://www.softwareheritage.org/) - archive universelle
  du code source publié, infrastructure de référence pour résoudre les SWHID.

*Utilisé par* :<br>
TransformationBatch (algorithm)

*Relations inverses (requêter par resourceType='Algorithm')* :<br>
Identifier, Responsibility, KeywordAssignment

*Note* :
- Objet global, non ancré géographiquement : un algorithme est réutilisable sur toutes les stations.
- codeRepository pointe vers le dépôt vivant (GitHub, GitLab, forge INRAE...).
- path précise le script ou la fonction dans ce dépôt.
- swhid épingle la version exacte du code exécuté. Porté par `Identifier`
  (codeType=swhid), pas par une colonne en dur, comme le DOI (même
  raisonnement, ADR-009/027, ADR-052 amendé). Unicité garantie par un index
  unique partiel sur `Identifier.code` restreint à `codeType='swhid'`.
  Caractère obligatoire (une ligne Algorithm n'existe qu'associée à un swhid)
  garanti applicativement, pas par une contrainte native : c'est le même
  niveau de garantie que le reste du pattern TPC resource (ADR-060), pas une
  exception.
- code, name, version, swhid, quatre rôles distincts : `code` est le slug d'URL lisible et versionné ("agregation-qjxa-v3"), confort de navigation modifiable comme partout ; `name` est le libellé lisible ("Agrégation QJXA") ; `version` est le tag git informatif, texte libre non contraint ; `swhid` (via Identifier) est l'épingle cryptographique immuable de la version exacte, seule à faire foi pour la reproductibilité. Le `code` nomme lisiblement la version, il ne l'épingle pas : ne pas confondre son suffixe "v3" avec la garantie portée par le swhid. Le suffixe de version du slug reprend `version` s'il est renseigné, sinon un incrément simple (v1, v2...).
- supersededBy chaîne les versions : quand une ligne passe status=superseded, elle pointe vers la ligne qui la remplace. Permet de reconstituer l'historique dans l'ordre (suivre la chaîne jusqu'à la ligne status=active) sans dépendre d'un horodatage ou du champ version, tous deux absents ou non fiables à cet usage. Null tant que la ligne est active ou simplement deprecated sans remplaçante connue.
- Épinglage applicatif, gating sur l'archivage : au moment d'un batch manuel, le runner déclenche (ou vérifie) l'archivage Software Heritage du script, attend la résolution du swhid (de l'ordre de quelques minutes), cherche un Identifier existant (resourceType=Algorithm, codeType=swhid, code=<swhid résolu>) et réutilise l'Algorithm associé, ou crée la ligne Algorithm et son Identifier si aucun ne correspond. Aucun batch ne s'exécute sur un code non archivé. Un batch auto réutilise la ligne déjà épinglée sans en créer une nouvelle. La notif "le dépôt git a changé" (via Software Heritage ou webhook) est hors modèle, à prévoir côté applicatif.
- Le DOI de la publication du logiciel, s'il existe (HAL, Zenodo...), est porté par `Identifier` (codeType=doi), même mécanisme que swhid, comme pour Bundle et Dataset.
- La configuration d'exécution (paramètres propres au batch) vit sur TransformationBatch.parameters, pas ici.
- Cas d'usage types (le dépôt et les conventions de nommage sont à spécifier, voir B2) :
  * Agrégation (QJXA) : codeRepository="https://github.com/inrae/bdoh-scripts",
    path="aggregation/qjxa.py", fichier de paramétrage externe sur le même dépôt
    (format à définir), input=TTS "Débit horaire".
  * Comblement de lacunes : path="gap-filling/stineman.py", deux séries en entrée
    (série principale + référence), rôles passés en parameters.
  * Ré-échantillonnage : path="resample/resample.py", fréquence cible et méthode
    en parameters.
  * Application de barème : path="rating/apply.py", transferFunctionSet renseigné,
    loi d'extrapolation et coefficient en parameters.
  * Combinaison master/save : path="merge/master-save.py", deux séries en entrée,
    rôles master/save passés en parameters.

| Champ            | Cardinalité | Définition                                    | Valeurs possibles                                    |
|------------------|-------------|-----------------------------------------------|------------------------------------------------------|
| `id`             | 1           | Identifiant technique, clé primaire           | uuid                                                 |
| `code`           | 1           | Slug unique globalement, version dans le slug | "agregation-qjxa-v3"                                 |
| `name`           | 1           | Libellé lisible de l'algorithme               | "Agrégation QJXA"                                    |
| `description`    | 0..1        | Description libre                             |                                                      |
| `codeRepository` | 1           | URL du dépôt source                           | "https://github.com/inrae/bdoh-scripts"              |
| `path`           | 0..1        | Chemin du script dans le dépôt                | "aggregation/qjxa.py"                                |
| `version`        | 0..1        | Tag de release git, informatif (texte libre)  | "v2.1.0"                                             |
| `status`         | 1           | État de la version                            | `active` \| `superseded` \| `deprecated`             |
| `supersededBy`   | 0..1 →Algo  | Version qui remplace cette ligne, si superseded | → Algorithm                                        |

---

## TransformationBatch
> Acte de calcul d'une série dérivée - quel algorithme sur quel runner, depuis quelles séries sources.

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
- Acte de calcul sur une ou plusieurs séries sources (TimeSeries ou TransformedTimeSeries).
- Analogue à ValidationBatch : factorisation des métadonnées de calcul.
- Les points calculés sont dans Transformation.
- runner : la Machine qui a exécuté (serveur BDOH, HPC, pipeline local).
- algorithm : le code qui a tourné (script versionné, swhid épinglé sur Algorithm).
- transferFunctionSet : optionnel, présent uniquement si le calcul applique un barème stocké (courbe de tarage...). Le runner applique la TF désignée par le TFSet pour chaque instant via les validFrom/validTo de la jointure transferfunctionset_function.
- parameters : JSON de configuration d'exécution propre à ce batch (loi d'extrapolation, pas d'agrégation, rôles des séries d'entrée si le script en a besoin...).
- inputSeries : table de jointure explicite `transformationbatch_inputseries` (seriesType, seriesId) - accepte TimeSeries et TransformedTimeSeries, un batch peut prendre plusieurs séries en entrée.

| Champ                   | Cardinalité  | Définition                              | Valeurs possibles               |
|-------------------------|--------------|-----------------------------------------|---------------------------------|
| `id`                    | 1            | Identifiant technique, clé primaire     | uuid                            |
| `transformedTimeSeries` | 1 →TTS       | Série produite                          | → TransformedTimeSeries         |
| `runner`                | 1 →Machine   | Système ayant exécuté le calcul         | → Machine                       |
| `algorithm`             | 1 →Algo      | Code exécuté                            | → Algorithm                     |
| `transferFunctionSet`   | 0..1 →TFS    | Jeu de fonctions appliqué si barème     | → TransferFunctionSet           |
| `parameters`            | 0..1         | Configuration d'exécution (JSON)        | {"method":"linear","gap_h":6}   |
| `appliedAt`             | 1            | Date d'exécution du calcul              | "2024-04-01T08:00:00Z"          |
| `validFrom`             | 1            | Début de la période calculée            | "2024-01-01T00:00:00Z"          |
| `validTo`               | 0..1         | Fin de la période calculée              | null                            |
| `status`                | 1            | État du batch                           | `pending` \| `done` \| `failed` |
| `comment`               | 0..1         | Commentaire libre                       |                                 |

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
- Analogue à ValidatedObservation : c'est là que vivent les données calculées.
- uncertaintyLow/High : bornes asymétriques de l'incertitude propagée sur la valeur calculée. Optionnelles. Produites par un TransformationBatch de propagation : un Algorithm de propagation (ex. BaRatin) prend en entrée la série de hauteur avec ses incertitudes (ValidatedObservation.uncertaintyLow/High) et la TransferFunction avec ses TransferFunctionParameter (lois marginales + covariance), et produit cette TTS avec les bornes sur chaque Transformation. C'est le niveau 3 de propagation d'incertitude : aucun objet nouveau, le mécanisme de transformation existant suffit.

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
| `uncertaintyLow`        | 0..1        | Borne basse de l'incertitude propagée     | -0.8                                      |
| `uncertaintyHigh`       | 0..1        | Borne haute de l'incertitude propagée     | 1.2                                       |

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
- recalculationMode : contrôle le déclenchement du recalcul quand une série source change. `auto` déclenche un nouveau TransformationBatch automatiquement (via trigger). `manual` laisse le curateur relancer le calcul explicitement. Dans les deux cas le recalcul écrase les valeurs précédentes dans `Transformation`.
- Fork curé : quand un état de calcul a une valeur scientifique durable (ancien barème à comparer, version ayant servi à une analyse publiée), il ne faut pas l'écraser silencieusement. Le geste est de créer une TTS coexistante ("Débit barème 2020") avant de recalculer la TTS courante avec le nouveau barème. Les deux coexistent sans hiérarchie, le contexte scientifique discrimine. C'est un acte de curation explicite, analogue au fork git : une lignée diverge volontairement et vit à côté. Aucun objet nouveau requis, ADR-026 l'autorise déjà.
- Pour les états publiés devant persister avec un DOI, utiliser Dataset (A7) plutôt que le fork.
- code unique par Station.

| Champ                      | Cardinalité | Définition                             | Valeurs possibles                                                |
|----------------------------|-------------|----------------------------------------|------------------------------------------------------------------|
| `id`                       | 1           | Identifiant technique, clé primaire    | uuid                                                             |
| `code`                     | 1           | Slug unique par ancre                  | "debit-tarage-bdoh"                                              |
| `name`                     | 1           | Nom de la série dérivée                | "Débit Mercier au pont D610"                                     |
| `description`              | 0..1        | Description libre                      |                                                                  |
| `anchorType`               | 1           | Type d'ancrage géographique            | `Observatory` \| `Site` \| `Station`                             |
| `anchorId`                 | 1           | UUID de l'Observatory, Site ou Station | uuid                                                             |
| `featureOfInterest`        | 0..1 →FOI   | FOI proximate si différente de l'ancre | → FeatureOfInterest                                              |
| `property`                 | 1 →Prop     | Variable produite                      | → Property                                                       |
| `unit`                     | 1 →Unit     | Unité de la série dérivée              | → Unit                                                           |
| `procedureTransformation`  | 1 →Proc     | Procédure de transformation            | → Procedure (type=transformation)                                |
| `acquisitionType`          | 1           | Mode d'acquisition des données         | `sensor_continuous` \| `lab_sample`                              |
| `aggregationStatistic`     | 1           | Nature métrologique de la valeur       | `instantaneous` \| `average` \| `cumulative` \| `maximum` \| `minimum` \| `variance` \| `standard_deviation` \| `sporadic` |
| `observationFrequency`     | 0..1        | Fréquence nominale (ISO 8601)          | "PT15M" \| "PT1H" - null si sporadic                             |
| `recalculationMode`        | 1           | Déclenchement du recalcul              | `auto` \| `manual`                                               |
| `status`                   | 1           | État de la série                       | `active` \| `inactive` \| `discontinued`                         |
| `license`                  | 1 →Lic      | Licence des données                    | → License                                                        |


<div class="page-break"></div>

# 9. ORGANISATION

## Mapping DataCite

Correspondance entre les propriétés DataCite 4.6 et les entités BDOH, commune à
`Bundle` (export éditorial vivant) et `Dataset` (export figé citable). Ce mapping
décrit le comportement d'export : un seul champ obligatoire DataCite est purement
éditorial (le Title) ; tout le reste se dérive de ce que le modèle porte déjà
(`Responsibility`, `Observatory`, `KeywordAssignment`, enveloppe spatio-temporelle
des séries). Aucune métadonnée n'est donc ressaisie : le mapping est une vue
dérivée, pas un stockage.

| Propriété DataCite     | Obligation  | Source dans BDOH                                       | Stocké / dérivé     |
|------------------------|-------------|--------------------------------------------------------|---------------------|
| Identifier (DOI)       | Mandatory   | `Identifier` (codeType=doi)                            | dérivé (dépôt)      |
| Creator                | Mandatory   | `Responsibility` (role=author / principalInvestigator) | dérivé              |
| Title                  | Mandatory   | `Bundle.name` ou `Dataset.title`                       | stocké              |
| Publisher              | Mandatory   | `Observatory` rattaché                                 | dérivé              |
| PublicationYear        | Mandatory   | année du dépôt (Bundle) ou `Dataset.exportedAt`        | calculé / stocké    |
| Subject                | Mandatory   | `KeywordAssignment` (type=theme / discipline)          | dérivé              |
| ResourceType           | Mandatory   | constante "Dataset"                                    | constante           |
| Description (Abstract) | Recommended | `Bundle.abstract`                                      | stocké              |
| Date (couverture)      | Recommended | min/max phenomenonTime des séries, ou fenêtre Dataset  | dérivé / stocké     |
| GeoLocation            | Recommended | enveloppe spatiale des stations incluses               | dérivé              |
| Contributor            | Recommended | `Responsibility` (autres rôles)                        | dérivé              |
| Language               | Recommended | constante "fr" ou "en" selon contexte                  | constante           |
| FundingReference       | Optional    | `Project` lié via Responsibility / KeywordAssignment   | dérivé              |
| RelatedIdentifier      | Optional    | `Identifier` (autres types) ; IsDerivedFrom à l'export | dérivé              |

---

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

| Champ          | Cardinalité | Définition                          | Valeurs possibles                                   |
|----------------|-------------|-------------------------------------|-----------------------------------------------------|
| `id`           | 1           | Identifiant technique, clé primaire | uuid                                                |
| `project`      | 1 →Proj     | Projet actif sur cette période      | → Project                                           |
| `resourceType` | 1           | Type de ressource ciblée            | `Observatory` \| `Site` \| `Station` \| `TimeSeries` \| `TransformedTimeSeries` \| `Datastream` |
| `resourceId`   | 1           | UUID de la ressource ciblée         | uuid                                                |
| `validFrom`    | 1           | Début de la période                 | "2012-01-01"                                        |
| `validTo`      | 0..1        | Fin de la période, null si actif    | null                                                |

---

## Bundle
> Regroupement éditorial de séries et fonctions pour la diffusion et le catalogage - objet de publication vivant.

*Aligné avec* :
- [DataCite Metadata Schema 4.6](https://datacite-metadata-schema.readthedocs.io/en/4.6/properties/)
  - schéma de référence pour la publication citable d'un jeu de données (DOI,
  Creator, Title, Publisher, Subject...). Bundle est exportable vers tout entrepôt
  compatible DataCite (Dataverse, Zenodo, RDG...). Voir le mapping ci-dessous dans
  la note.
- [DCAT Distribution](https://www.w3.org/TR/vocab-dcat-3/#Class:Distribution)
  - classe du vocabulaire de catalogue W3C ; un Bundle correspond à une
  distribution accessible d'un dataset, exportable vers les catalogues
  (Theia/OZCAR, ENVRI-Hub).
- [ODM2 Datasets](https://github.com/ODM2/ODM2/blob/master/doc/ODM2Docs/core_datasets.md)
  - mécanisme ODM2 de regroupement logique de résultats en jeu de données
  cohérent ; Bundle reprend ce principe pour la publication.

*Relations inverses* :<br>
KeywordAssignment

*Note* :
- Regroupe des TimeSeries, TransformedTimeSeries, TransferFunction et ControlObservation pour la publication. Objet éditorial, pas technique.
- Lien via la table bundle_series (seriesType + seriesId) - pattern TPC series.
- Extensible à tout nouveau type de série sans migration de schéma.
- Objet **vivant** : les séries incluses continuent d'évoluer après publication. Pour un snapshot figé citable avec DOI sur les valeurs, utiliser Dataset (A7).
- Le DOI est porté par `Identifier` (codeType=doi), pas par un champ en dur (ADR-009/027).
- `Subject` DataCite est fourni par `KeywordAssignment` : au moins un mot-clé thématique est attendu sur tout Bundle publié (type=theme ou type=discipline).
- Mapping DataCite complet : voir la section *Mapping DataCite* en tête de section 9, commune à Bundle et Dataset.

| Champ         | Cardinalité | Définition                                       | Valeurs possibles                      |
|---------------|-------------|--------------------------------------------------|----------------------------------------|
| `id`          | 1           | Identifiant technique, clé primaire              | uuid                                   |
| `name`        | 1           | Titre éditorial (= DataCite Title)               | "Qualité eau Saône 2024"               |
| `abstract`    | 0..1        | Description longue (= DataCite Abstract)         | texte libre                            |
| `coverImage`  | 0..1        | URL d'une illustration pour les portails         | "https://..."                          |
| `Observatory` | 1 →Obs      | Observatoire parent (= DataCite Publisher)       | → Observatory                          |
| `license`     | 1 →Lic      | Licence des données du bundle                    | → License                              |
| `status`      | 1           | État éditorial                                   | `draft` \| `published` \| `archived`   |

---

## bundle_series
> Lien entre un Bundle et une série ou fonction - table de jointure, pattern TPC series.

*Note* : Extensible sans migration : ajouter un type = ajouter une valeur à l'enum seriesType.
       Intégrité garantie par trigger BEFORE INSERT/UPDATE (pattern TPC agent).

| Champ       | Cardinalité | Définition                   | Valeurs possibles                                                                   |
|-------------|-------------|------------------------------|-------------------------------------------------------------------------------------|
| `bundleId`  | 1 →Bun      | Bundle parent                | → Bundle                                                                            |
| `seriesType` | 1           | Type de la série ou fonction | `TimeSeries` \| `TransformedTimeSeries` \| `TransferFunction` \| `ControlObservation` |
| `seriesId`   | 1           | UUID de la série ou fonction | uuid                                                                                |

---

## Dataset
> Reçu d'un export figé vers un entrepôt externe (Dataverse...) - objet de citation immuable.

*Aligné avec* :
- [DataCite Metadata Schema 4.6](https://datacite-metadata-schema.readthedocs.io/en/4.6/properties/)
  - le paquet de métadonnées envoyé à l'entrepôt est construit selon ce schéma
  (mapping commun à Bundle et Dataset, voir la section *Mapping DataCite* en tête
  de section 9). Le DOI obtenu identifie le dépôt externe.
- [DataCite RelatedIdentifier](https://datacite-metadata-schema.readthedocs.io/en/4.6/properties/relatedidentifier/)
  - le paquet exporté porte un relatedIdentifier (relationType=IsDerivedFrom)
  pointant vers les ressources BDOH d'origine, fermant la boucle entrepôt -> source.

*Utilisé par* :<br>
Identifier (resourceType='Dataset', codeType=doi)

*Relations inverses* :<br>
dataset_resource (les ressources BDOH incluses dans l'export)

*Note* :
- Reçu d'export, pas un conteneur de données. BDOH ne stocke jamais les valeurs figées : le snapshot est calculé au vol au moment de l'export, envoyé à l'entrepôt, et non conservé. L'archive et la garantie de reproductibilité vivent sur l'entrepôt (Dataverse), pas dans BDOH.
- Objet immuable une fois créé : il documente un acte d'export daté.
- Distinction avec Bundle : Bundle est un suivi éditorial vivant (pointe vers des ressources qui évoluent) ; Dataset est une citation figée (référence un dépôt externe à un instant T). Un Bundle peut engendrer un Dataset (sourceBundle), mais un export peut aussi se faire sans Bundle.
- Le DOI est celui attribué par l'entrepôt externe, porté par `Identifier` (codeType=doi), pas un champ en dur.
- Sert de compteur de réutilisation : compter les Dataset incluant une ressource donnée (via dataset_resource) donne le nombre d'exports/citations de cette ressource. Comptage partiel par construction (ne couvre que les exports passés par la passerelle BDOH), à documenter comme tel.
- temporalCoverageStart/End : fenêtre globale du panier exporté (= DataCite Date). Obligatoires sur l'objet stocké. Si l'utilisateur ne précise pas de fenêtre, BDOH calcule l'enveloppe réelle (min/max phenomenonTime des ressources) au moment de l'export et la fige ici.

| Champ                   | Cardinalité | Définition                                      | Valeurs possibles            |
|-------------------------|-------------|-------------------------------------------------|------------------------------|
| `id`                    | 1           | Identifiant technique, clé primaire             | uuid                         |
| `title`                 | 1           | Titre du dépôt exporté (= DataCite Title)       | "Débits Saône 2010-2015"     |
| `exportedAt`            | 1           | Date de l'export (= DataCite PublicationYear)   | "2024-06-01T00:00:00Z"       |
| `temporalCoverageStart` | 1           | Début de la fenêtre exportée                    | "2010-01-01T00:00:00Z"       |
| `temporalCoverageEnd`   | 1           | Fin de la fenêtre exportée                      | "2015-12-31T23:59:59Z"       |
| `repositoryUrl`         | 0..1        | URL du dépôt sur l'entrepôt externe             | "https://entrepot.../dataset/123" |
| `sourceBundle`          | 0..1 →Bun   | Bundle d'origine si l'export en provient         | → Bundle                     |
| `status`                | 1           | État du reçu d'export                            | `active` \| `superseded`     |

---

## dataset_resource
> Ressources BDOH incluses dans un export Dataset - table de jointure.

*Note* :
- Relie un Dataset aux ressources BDOH effectivement exportées (pattern TPC series).
- Pas de bornes temporelles par ressource : la fenêtre est globale au Dataset. Un panier sur des périodes hétérogènes se fait en plusieurs exports (plusieurs Dataset, plusieurs DOI).

| Champ        | Cardinalité | Définition                   | Valeurs possibles                                                                   |
|--------------|-------------|------------------------------|-------------------------------------------------------------------------------------|
| `dataset`    | 1 →Dat      | Dataset parent               | → Dataset                                                                           |
| `seriesType` | 1           | Type de la ressource exportée | `TimeSeries` \| `TransformedTimeSeries` \| `TransferFunction` \| `ControlObservation` |
| `seriesId`   | 1           | UUID de la ressource         | uuid                                                                                |

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
- memoryType : note, event, document, photo, installation, hydraulic change, maintenance, incident, calibration
	   
*Note* : 
- Note contextuelle ou événement daté attaché à n'importe quelle ressource.
- Objet transversal de documentation du cycle de vie.
- Fichiers stockés en S3, référencés via mediaUrl.
- agentType + agentId : pattern TPC - auteur humain (`Person`) pour une note
- manuelle, pipeline (`Machine`) pour une alerte automatique ou détection d'anomalie.

| Champ          | Cardinalité | Définition                          | Valeurs possibles                                                               |
|----------------|-------------|-------------------------------------|---------------------------------------------------------------------------------|
| `id`           | 1           | Identifiant technique, clé primaire | uuid                                                                            |
| `resourceType` | 1           | Type de ressource ciblée            | `Observatory` \| `Site` \| `Station` \| `System` \| `TimeSeries` \| `TransformedTimeSeries` \| `Deployment` \| `Project` \| `TransferFunction` \| `Specimen` \| `Datastream` |
| `resourceId`   | 1           | UUID de la ressource ciblée         | uuid                                                                            |
| `datetime`     | 1           | Date de la note ou de l'événement   | "2014-04-17T00:00:00Z"                                                          |
| `title`        | 0..1        | Titre court                         | "Modification contrôle hydraulique"                                             |
| `content`      | 0..1        | Texte libre                         | "Installation d'une lame déversante"                                            |
| `mediaUrl`     | 0..*        | Photos ou documents associés (S3)   | "https://storage.obs.fr/memories/2014-lame.jpg"                                 |
| `agentType`    | 0..1        | Type d'agent auteur de la note      | `Person` \| `Machine`                                                           |
| `agentId`      | 0..1        | UUID de la Person ou Machine        | uuid                                                                            |
| `status`       | 1           | État de la note                     | `active` \| `archived`                                                          |
