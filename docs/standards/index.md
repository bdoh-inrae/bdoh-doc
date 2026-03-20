# Standards de référence

Le modèle BDOH s'appuie sur plusieurs standards environnementaux et géospatiaux. Cette page résume leur rôle et les points d'alignement.

---

## OGC SensorThings API (STA)

**Rôle** : standard de base pour l'interface et le modèle de données.

STA fournit les 8 entités fondamentales (`Thing`, `Sensor`, `Datastream`, `Observation`, `ObservedProperty`, `FeatureOfInterest`, `Location`, `HistoricalLocation`) et une API REST/JSON légère orientée IoT.

**Alignement BDOH** :

| STA | BDOH |
|---|---|
| Thing | Station |
| Sensor | Sensor |
| Datastream | TimeSerie |
| Observation | ValidatedObservation |
| ObservedProperty | Property |
| FeatureOfInterest | FeatureOfInterest + SamplingFeature |
| Location | Location |
| HistoricalLocation | HistoricalLocation |

**Références** : [OGC SensorThings API Part 1: Sensing 1.1](https://docs.ogc.org/is/18-088/18-088.html)

---

## ODM2 — Observations Data Model 2

**Rôle** : métadonnées environnementales, gestion des échantillons, vocabulaires contrôlés.

ODM2 (Horsburgh et al., 2016) est conçu pour les observatoires environnementaux. Il apporte les concepts de `Specimen`, `Action`, `ProcessingLevel`, `Method`, `Variable`, `Unit`, et les vocabulaires contrôlés pour les milieux (`SampledMedium`).

**Ce que BDOH reprend d'ODM2** :

- `sampledMedium` sur `TimeSerie` et `SamplingFeature`
- `specimenType` et `medium` sur `SamplingFeature`
- `processingLevel` sur `TimeSerie`
- Structure `Action → Result` traduite en `SamplingFeature → ValidatedObservation`

**Référence** : Horsburgh et al. (2016), *Environmental Modelling and Software*, doi:10.1016/j.envsoft.2016.01.010

---

## ISO 19115 — Métadonnées géographiques

**Rôle** : métadonnées de gouvernance et de responsabilité.

ISO 19115 définit `CI_Responsibility` et `CI_RoleCode` pour décrire qui est responsable de quoi sur une ressource géographique. BDOH utilise directement le vocabulaire `CI_RoleCode` dans l'entité [Responsibility](../model/actors.md#responsibility).

**Valeurs CI_RoleCode utilisées** : `pointOfContact`, `principalInvestigator`, `author`, `processor`, `publisher`, `custodian`, `owner`, `distributor`, `originator`, `resourceProvider`, `user`

**Alignement** : `MD_Keywords` → [Keyword](../model/references.md#keyword), `MD_KeywordTypeCode` → `keywordType`

---

## NERC NVS P01 — Vocabulaire des variables

**Rôle** : vocabulaire contrôlé pour les variables mesurées.

Le NERC P01 (Natural Environment Research Council Vocabulary Server) définit plus de 45 000 concepts de variables environnementales avec une structure composite : propriété mesurée + objet d'intérêt + milieu + méthode.

BDOH utilise P01 comme source externe via le champ `identifier` de [Property](../model/references.md#property).

---

## Theia/OZCAR Thesaurus

**Rôle** : classification thématique pour les observatoires français.

Le thésaurus Theia/OZCAR (`w3id.org/ozcar-theia`) est développé pour les observatoires des zones critiques français. Il propose des groupes thématiques (`Variable categories`) et des concepts de variables avec URIs stables.

BDOH l'utilise via `identifier` sur [Property](../model/references.md#property) pour l'interopérabilité avec les réseaux OZCAR.

---

## STAMPLATE (Helmholtz)

**Rôle** : extensions STA pour les sciences de l'environnement.

STAMPLATE (Brinckmann et al., 2025) standardise l'usage des champs `properties` de STA via des JSON Schemas. Il introduit notamment les concepts de `Platform` (déploiement), `Campaign` (projet/campagne), et les métadonnées de responsabilité via schema.org.

**Ce que BDOH reprend** :

- `Deployment` ← STAMPLATE Platform
- `Project` ← STAMPLATE Campaign + schema.org/ResearchProject
- Pattern `member` + `roleName` → [Responsibility](../model/actors.md#responsibility)

**Référence** : [github.com/HMC-STAMPLATE/JSONSchema](https://github.com/HMC-STAMPLATE/JSONSchema)

---

## Helmholtz SMS CV

**Rôle** : vocabulaire contrôlé pour les capteurs et variables mesurées.

Le Helmholtz Sensor Management System Controlled Vocabulary fournit des métadonnées enrichies pour les variables : `samplingMedium`, `aggregationType`, `status`, lien vers NERC NVS.

**Ce que BDOH reprend sur [Property](../model/references.md#property)** : `samplingMedium`, `aggregationType`, `status`, `definition`.
