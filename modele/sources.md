---
title:  Modèle de données BDOH
subtitle: Sources de référence
author: Louis Héraut
date: mai 2026
affiliation: INRAE, UR RiverLy, Villeurbanne, France
---

# À quoi sert ce fichier

Ce fichier est la bibliographie annotée des standards et implémentations de
référence de BDOH, et le **propriétaire unique de leur état daté** (version,
ratification, publication). Pour chaque source : ce qu'elle est, ce qu'elle
apporte à BDOH, et où elle en est. Quand un autre fichier a besoin de l'état
d'un standard, il pointe ici plutôt que de le recopier.

Il ne décrit pas le modèle (`modele_donnees.md`) ni les décisions
(`decisions.md`). Les questions de veille propres à BDOH, c'est-à-dire ce
qu'il faudra décider quand un standard bouge, sont dans `chantier.md`
(partie D), pas ici.

# Standards OGC

## OGC SensorThings API Part 1: Sensing 1.1 (STA)
Standard de base du modèle BDOH pour la structure et l'interface.
- Spécification officielle : https://docs.ogc.org/is/18-088/18-088.html
- Page OGC : https://www.ogc.org/standards/sensorthings/
- Vue d'ensemble : https://ogcapi.ogc.org/sensorthings/overview.html
- Version 1.0 (référence historique) : https://docs.ogc.org/is/15-078r6/15-078r6.html

**Etat en 2025-2026** : STA 1.1 reste la référence de production stable. STA 2.0
a fait l'objet d'un appel à commentaires publics OGC clos le 18 janvier 2026 ;
les commentaires sont en cours d'intégration et le standard n'est pas encore
ratifié. La principale évolution de STA 2.0 est le passage sur OMS (ISO
19156:2023), ce qui change la terminologie autour de FeatureOfInterest (introduction
des concepts Proximate/Ultimate FOI) et remplace `unitOfMeasurement` par `resultType`
(objet SWE-Common). BDOH a bien fait de ne pas adopter ces concepts instables :
HydroServer et FROST-Server font le même choix. STA 1.1 reste pleinement justifié
en production.

## OGC SensorThings API Extension: STAplus 1.0
Extension pour la science citoyenne et la propriété des observations.
Introduit les concepts de licence et de relations entre observations.
- Page OGC : https://www.ogc.org/standards/sensor-things-api-extension/

## OGC API - Connected Systems (CS API)
Successeur moderne de STA et SOS, basé sur OGC API Features.
Modélisé sur SOSA/SSN. A surveiller pour les évolutions futures de BDOH.
- Portail officiel (URL stable) : https://ogcapi.ogc.org/connectedsystems/
- Page OGC : https://www.ogc.org/standards/ogc-api-connected-systems/
- Spécification Part 1 (Feature Resources, draft) : https://docs.ogc.org/DRAFTS/23-001r0.html
- Spécification Part 2 (Dynamic Data, draft) : https://docs.ogc.org/DRAFTS/23-002r0.html
- GitHub SWG : https://github.com/opengeospatial/ogcapi-connected-systems

**Etat en 2025-2026** : les Parts 1 et 2 de CS API ont été approuvées comme
standards OGC officiels le 2 juin 2025, la version 1.0 ayant été publiée le
22 juillet 2025. C'est le successeur officiel
de STA, SOS et SPS, construit sur OGC API Features, JSON-LD, SOSA/SSN,
SensorML 3.0 (avec encodages JSON désormais standardisés). Il est conçu pour
coexister avec STA plutôt que le remplacer immédiatement : un endpoint CS API
peut lier vers un endpoint STA existant. Pour BDOH, c'est une cible à moyen
terme mais une migration prématurée serait hors de propos. A surveiller pour
la v2. Note : les URLs de spécification ci-dessus restent en `/DRAFTS/` au
moment de la rédaction ; l'URL canonique stable est le portail ogcapi.ogc.org.

**Ce que CS API apporte par rapport à STA** : une distinction plus propre entre systèmes
statiques (métadonnées de capteurs, plateformes, déploiements, dans la Part 1)
et données dynamiques (observations, commandes, dans la Part 2). L'entité `System` généralise le `Thing`
STA à tout type de système connecté (drone, satellite, humain...). L'architecture Part 1
/ Part 2 correspond grossièrement à la distinction couche IoT / couche métier de BDOH.


<div class="page-break"></div>

# Modèles de données environnementaux

## ODM2 - Observations Data Model 2
Modèle de référence pour les métadonnées environnementales.
Apporte : Specimen, Method, Variable, Unit, SampledMedium, ProcessingLevel.

- Site officiel : https://www.odm2.org
- Dépôt GitHub : https://github.com/ODM2/ODM2
- Article de référence (open access) :
  Horsburgh J.S. et al. (2016). Observations Data Model 2: A community
  information model for spatially discrete Earth observations.
  Environmental Modelling & Software, 79, 55-74.
  https://doi.org/10.1016/j.envsoft.2016.01.010
- Extension interopérabilité :
  Hsu L. et al. (2017). Enhancing Interoperability and Capabilities of
  Earth Science Data using ODM2. Data Science Journal, 16(4), 1-16.
  https://doi.org/10.5334/dsj-2017-004

**Ce que ODM2 apporte à BDOH** : ODM2 est né de l'ODM 1.1 (CUAHSI HIS, 2008), étendu
pour couvrir une gamme plus large d'observations : pas seulement les séries
temporelles hydrologiques, mais aussi les prélèvements d'échantillons, les profils
et les données multi-dimensionnelles. Il profil l'O&M OGC et structure les relations entre variables,
méthodes, sites et résultats. BDOH en reprend : la sémantique des variables (Property
aligné sur ODM2 Variable), la notion de SamplingFeature (acte de prélèvement terrain),
le concept d'Equipment, et les bonnes pratiques d'usage d'identifiants externes (ORCiD,
DOI, ROR). ODM2 reste une source de vérité sémantique même si son implémentation
technique (XML, WaterOneFlow) est dépassée.


<div class="page-break"></div>

# Implémentations de référence

## HydroServer (CUAHSI / Utah State University)
Implémentation de référence STA pour les observatoires environnementaux.
Architecture la plus proche de BDOH : une base, deux API (STA + métier).
Garde `unitOfMeasurement` comme FK vers `Unit`, choix repris dans BDOH.

- Dépôt GitHub : https://github.com/hydroserver2/hydroserver
- Documentation : https://hydroserver2.github.io/hydroserver/
- Instance de démo : https://playground.hydroserver.org
- Article stack complet :
  Horsburgh J.S., Lippold K., Slaugh D.L., Ramirez M. (2025).
  HydroServer: A software stack supporting collection, communication,
  storage, management, and sharing of data from in situ environmental sensors.
  Environmental Modelling & Software, 193.
  https://doi.org/10.1016/j.envsoft.2025.106637
- Article alignement STA/ODM2 :
  Horsburgh J.S., Lippold K., Slaugh D.L. (2025).
  Adapting OGC's SensorThings API and data model to support data
  management and sharing for environmental sensors.
  Environmental Modelling & Software, 183.
  https://doi.org/10.1016/j.envsoft.2024.106241

**Ce que HydroServer apporte à BDOH** : HydroServer est le miroir américain le plus
proche de BDOH dans sa philosophie. Stack technique : Django/Python pour l'API STA,
PostgreSQL/TimescaleDB pour la base, Vue.js pour le front. Le data model étend STA
avec des métadonnées ODM2 : Variable, Unit, Method deviennent des entités séparées
(exactement comme Property, Unit, Procedure dans BDOH). Ils gardent `unitOfMeasurement`
comme FK vers Unit plutôt que d'adopter le `resultType` SWE-Common de STA 2.0.
C'est la justification empirique de l'ADR-017 de BDOH.

Différences clés avec BDOH : HydroServer cible les groupes de recherche américains
gérant leurs propres stations (déploiement cloud individuel par groupe). BDOH est plus
centralisé (une dizaine d'observatoires dans une même base). HydroServer n'a pas de
couche de validation multi-étapes ni de système de fonctions de transfert. Ces
besoins sont propres au contexte hydrologique français : référentiel SANDRE,
courbes de tarage, calcul de débits journaliers (QJXA).
HydroServer s'intègre à HydroShare pour l'archivage long terme, équivalent
potentiel du Bundle BDOH pour la publication.

La séparation entre ingestion (Streaming Data Loader, un outil externe) et gestion
(Data Management App) dans HydroServer confirme que la couche de transformation est
traitée comme externe au core. Argument en faveur de "BDOH documente plutôt qu'exécute"
pour les transformations (point ouvert ADR sur TransformationBatch).

## STAMPLATE (Helmholtz Earth & Environment)
7 centres de recherche allemands (TERENO, KIT, HEREON, GFZ, AWI, GEOMAR, UFZ, FZJ).
Standardise l'usage des champs `properties` de STA via JSON Schemas.
Introduit : Platform (Deployment), Campaign (Project), data quality,
provenance, responsible persons. Construit sur JSON-LD et schema.org.

- Site projet : https://helmholtz-metadaten.de/inf-projects/stamplate
- Communauté : https://community.helmholtz-metadaten.de/projects/stamplate/
- Schema (Zenodo, open access) :
  Brinckmann N. et al. (2025). STAMPLATE Schema: An extended SensorThings
  API data model for environmental monitoring systems.
  Zenodo. https://doi.org/10.5281/zenodo.17241283
- Ecosystem complet :
  Bumberger J. et al. (2025). Digital ecosystem for FAIR time series data
  management in environmental system science.
  SoftwareX, 29. https://doi.org/10.1016/j.softx.2025.102038
- Codebase JSON Schemas :
  https://codebase.helmholtz.cloud/stamplate/jsonschemas

**Ce que STAMPLATE apporte à BDOH** : STAMPLATE est le cas d'usage à plus grande échelle
de l'extension STA pour les sciences environnementales : 7 centres, des milliers
de capteurs, des infrastructures allant des observatoires terrestres (TERENO) aux
systèmes embarqués (IAGOS). Leur approche technique diffère de BDOH : ils étendent STA via les
champs `properties` en JSON-LD standardisé (pas de tables SQL supplémentaires), une
instance FROST-Server par centre, fédérées dans un Earth Data Portal commun.

L'écosystème DataHub Helmholtz couple : SMS (Sensor Management System) pour les
métadonnées capteurs et déploiements, FROST-Server (STA) comme interface données,
TSM (Time Series Management System) pour la gestion des séries, EDP (Earth Data Portal)
pour la découverte et visualisation. C'est une architecture plus distribuée que BDOH
mais les problèmes résolus sont les mêmes : traçabilité des déploiements, data quality,
provenance, responsible persons, campagnes (= projets).

Le fait que STAMPLATE ait livré son schéma formel en 2025 (Zenodo) est important :
c'est maintenant une référence citable pour la standardisation des métadonnées STA
dans les sciences de l'environnement. Les alignements avec ce schéma pourraient
renforcer l'interopérabilité de BDOH avec les infrastructures européennes.

Ressources complémentaires de l'écosystème TERENO/Helmholtz, utiles pour
enrichir les métadonnées BDOH :
- Profil STA augmenté, présentation des `properties` :
  https://hmc-stamplate.github.io/JSONSchema/properties.html
- Notes de travail DESY sur un STA augmenté (variante de profil, à examiner
  pour l'enrichissement de nos métadonnées) :
  https://notes.desy.de/hKhtD-0jRfilON3TasH6Eg
- Framework pour la qualification automatique des données :
  Schmidt L. et al. (2023). Environmental Modelling & Software, 168.
  https://doi.org/10.1016/j.envsoft.2023.105809
  Note : approche très aboutie de qualification et pré-traitement automatique du
  signal, mais potentiellement trop rigide. Point de comparaison pour le système
  de validation de BDOH, qui garde une place à l'expertise humaine.

## FROST-Server (Fraunhofer)
Implémentation open source de STA. Base PostgreSQL avec séparation
données statiques / dynamiques. Utilisé par Helmholtz comme serveur STA.
- GitHub : https://github.com/FraunhoferIOSB/FROST-Server

## WiSSkHy (SO HYBAM / GET)
Outil de gestion et de bancarisation de données du Service d'Observation
HYBAM, qui suit les grands fleuves tropicaux (Amazone, Congo, Orénoque).
Développé au laboratoire GET (Géosciences Environnement Toulouse).
- Démonstrateur : https://sno-hybam.shinyapps.io/WiSSkHy/
- Dépôt GitHub : https://github.com/william-santini/WiSSkHy

**Ce que WiSSkHy apporte à BDOH** : c'est une confirmation externe directe de
deux choix d'architecture de BDOH. D'abord, WiSSkHy n'utilise pas le Datastream
de la norme OGC mais un objet propre nommé TimeSerie, au motif que les données
de capteurs sont dérivées, critiquées, qualifiées et validées : c'est exactement
le raisonnement qui sépare la couche IoT et la couche métier dans BDOH. Ensuite,
WiSSkHy vise à bancariser les pipelines de traitement de données, ce qui rejoint
la logique de workflow de BDOH (validation et transformation tracées).

WiSSkHy traite la qualité comme un objet scientifique à part entière, avec un
jeu de codes plus fin que les quatre valeurs de `qualityFlag` BDOH : Raw,
Screened, Provisional, Partial, Good, Estimated, Suspect, Bad, Missing. Cette
granularité est intéressante à comparer avec le choix BDOH d'un vocabulaire
minimal (good, suspect, bad, missing) aligné ODM2/SANDRE/OGC. Les états
intermédiaires de WiSSkHy (Screened, Provisional) relèvent dans BDOH du
processus de validation par lots plutôt que d'un code de qualité figé.


<div class="page-break"></div>

# Réseaux d'observatoires français

## Theia/OZCAR
Réseau des observatoires des zones critiques français.
Thésaurus de référence pour les variables environnementales.
BDOH s'aligne sur Theia/OZCAR pour l'interopérabilité nationale.

- Thésaurus : https://w3id.org/ozcar-theia
- Portail de données : https://in-situ.theia-land.fr/
- Documentation producteurs :
  https://theia-ozcar.gricad-pages.univ-grenoble-alpes.fr/doc-producer/producer-documentation.html
- Infrastructure STA en cours (guidelines) :
  https://github.com/theia-ozcar-is/sensorthings-guidelines
- IR OZCAR : https://www.ozcar-ri.org/fr/donnees/

**Ce que Theia/OZCAR est réellement** : 22 observatoires labellisés, ~60 sites en
France et à l'étranger (Afrique, Asie, Amérique du Sud, Arctique), séries démarrant
dès 1960, plus de 300 variables mesurées (physiques et chimiques). L'IR OZCAR est
l'infrastructure de recherche nationale dédiée à la Zone Critique, la fine
pellicule entre roche non altérée et basse atmosphère où se produisent les
transferts d'eau, d'énergie et de matière.

Le SI Theia/OZCAR a construit un "modèle de données pivot" basé sur ISO 19115/INSPIRE,
O&M et DataCite. Il expose les données via SensorThings (séries temporelles) et CSW
(catalogue). La recherche par variable est identifiée comme le besoin premier des
utilisateurs. C'est la justification centrale du quadriptyque Keyword de BDOH
(ADR-030) et de l'alignement de Keyword.uri sur le thésaurus Theia/OZCAR.

**Interopérabilité BDOH - Theia/OZCAR** : les URIs du thésaurus Theia/OZCAR dans
`Keyword.uri` ne sont pas des métadonnées de confort : c'est le lien qui rend
les données de BDOH découvrables depuis le portail national in-situ.theia-land.fr.
Les `Identifier` portant les codes SANDRE, les `Keyword` alignés sur le thésaurus
OZCAR, et le `Bundle` comme objet de publication sont les trois points
de contact critiques pour cette interopérabilité.

Projet ANR FairTOIS (2020-2022) : a consolidé l'implémentation FAIR du SI Theia/OZCAR.
Au démarrage du projet, 7 observatoires sur 22 étaient visibles sur le portail,
contre 16 sur 22 à la fin. BDOH opère dans ce contexte d'hétérogénéité et de transition vers la FAIRisation.

## UMR SAS - GeoSAS (SOFAIR)
Ressource pédagogique de l'UMR Sol Agro et hydrosystème Spatialisation
(INRAE / Institut Agro Rennes-Angers) sur la mise en pratique de STA pour
les observatoires.
- Guide SOFAIR : https://geosas.fr/sofair-book/intro.html

**Ce que cette ressource apporte à BDOH** : c'est un support à destination des
gestionnaires d'observatoire et du personnel de terrain pour choisir les
métadonnées STA. Elle est surtout utile par les questions qu'elle soulève sur
l'interprétation de l'entité Thing : selon le grain de précision retenu, une
Thing peut désigner un point de mesure, une zone, une centrale d'acquisition
ou un capteur. Cette ambiguïté est exactement celle que BDOH tranche en
distinguant explicitement Observatory, Site, Station et les entités
d'instrumentation (Sensor, Actuator, Sampler, Platform, Kit) plutôt que de
tout réunir dans une Thing polymorphe. Le guide propose par ailleurs une
définition de FeatureOfInterest qui mérite discussion au regard du choix BDOH
(FeatureOfInterest = entité réelle observée, distincte du point de mesure).


<div class="page-break"></div>

# Vocabulaires contrôlés

## NERC NVS P01 - Vocabulaire des variables
40 000+ concepts de variables environnementales avec URIs stables.
Structure composite : propriété + objet d'intérêt + milieu + méthode.
Utilisé dans BDOH via `Identifier` sur `Property`.
- Vocabulaire en ligne : https://vocab.nerc.ac.uk/collection/P01/current/

## Helmholtz SMS CV - Sensor Management System
Vocabulaire contrôlé des systèmes d'observation Earth & Environment.
Apporte les listes de valeurs pour les KeywordType liés à l'instrumentation
(`sensorType`, `equipmentType`, `platformType`, `actionType`) et un
vocabulaire de licences. Utilisé dans BDOH côté `Keyword` (termes des
types capteur/équipement) et comme référence pour la table `License`.
- Interface CV : https://sms-cv.helmholtz.cloud/sms/cv/
- SMS open source :
  Lorenz C. et al. (2025). Sensor Management System (SMS): Open-source
  software for FAIR sensor metadata management in Earth system sciences.
  arXiv. https://doi.org/10.48550/arXiv.2512.17280

## SANDRE - Service d'Administration Nationale des Données et Référentiels sur l'Eau
Référentiel français pour les codes de qualité des données hydrométriques. Le
mapping des quatre valeurs `qualityFlag` de BDOH vers les codes SANDRE est défini
dans `decisions.md` (ADR-024), qui en est le propriétaire.
- Site : https://www.sandre.eaufrance.fr

## QUDT - Quantities, Units, Dimensions and Types
URIs pour les unités de mesure. Utilisé dans `Unit.definition`.
- Site : https://qudt.org
- Vocabulaire des unités : https://qudt.org/vocab/unit/

## UCUM - Unified Code for Units of Measure
Syntaxe compacte pour exprimer les unités (`mg/L`, `m3/s`). Alternative
à QUDT utilisable dans `Unit.definition`.
- Site : https://ucum.org

## SPDX License List - Identifiants de licences
Liste de référence des licences (logiciel, données, documentation) avec
identifiant court canonique, nom complet et URL permanente. Utilisé dans
BDOH via `License.spdxId`.
- Liste officielle : https://spdx.org/licenses/

## SWHID - Software Hash Identifier (ISO/IEC 18670:2025)
Identifiant intrinsèque permanent du code source. Utilisé dans BDOH via
`Algorithm.swhid` pour la reproductibilité scientifique des pipelines.
- Spécification : https://www.swhid.org/swhid-specification/
- Archive Software Heritage : https://www.softwareheritage.org/

## PIDINST - Persistent Identification of Instruments (RDA)
Schéma de métadonnées de la Research Data Alliance pour l'identification pérenne
des instruments (schéma 1.0, 2022 ; mapping DataCite). Utilisé dans BDOH comme
référence des métadonnées des cinq entités d'instrumentation (Sensor, Actuator,
Sampler, Platform, Kit) : Manufacturer (make), Model (model), AlternateIdentifier
de type serialNumber et inventoryNumber, Owner, InstrumentType, MeasuredVariable.
Complète SensorML (encodage riche) et le SMS (implémentation) pour ancrer make /
model / serialNumber / inventoryNumber sur un standard d'identification dédié.
Implémenté côté handle via des services comme B2INST.
- Spécification : https://docs.pidinst.org/
- Schéma 1.0 : https://www.rd-alliance.org/wp-content/uploads/2022/01/pidinst-schema-1.0_Final.pdf


<div class="page-break"></div>

# Correspondance source → entités du modèle

Cette table récapitule, pour chaque source, les entités du modèle de données
qui la citent dans leur section *Aligné avec*. Elle sert de point d'entrée
pour vérifier la cohérence des alignements et pour les enrichir.

| Source | Entités BDOH alignées | Nature de l'apport |
|--------|------------------------|---------------------|
| OGC STA 1.1 | Property, Unit, Procedure, Location, HistoricalLocation, FeatureOfInterest, Observatory, Site, Station, Sensor, Datastream, Observation, ValidatedObservation, Specimen, Transformation, TransformedTimeSeries, qualityFlag | Structure de base et interface ; vocabulaire des entités IoT (le Sensor STA = entité Sensor BDOH) |
| OGC API - Connected Systems | Sensor, Actuator, Sampler, Platform, Kit, Deployment, TimeSeriesSource | Deployment récursif ; ressource System unifiée reconstituée en vue (BDOH éclate en cinq entités, ADR-062) |
| OGC OMS / ISO 19156:2023 | FeatureOfInterest, Procedure, Observation, ControlObservation, Specimen | Concept d'observation et de feature of interest |
| OGC STAplus | Project | Entité Project (campagnes) et License |
| OGC SensorML 3.0 | Deployment, Sensor, Actuator, Sampler, Platform, Kit | Encodage des propriétés de déploiement, d'instrument et d'actionneur |
| W3C SSN/SOSA | Sensor, Actuator, Sampler, Platform, Kit, Deployment | Ontologie sémantique : rôles Sensor, Actuator, Sampler, Platform (Kit propre à BDOH) |
| W3C PROV-O | Service (SoftwareAgent), Machine, Responsibility, SamplingBatch, PreparationBatch, AnalysisBatch, CalibrationBatch, ObservationBatch, ValidationBatch, TransferFunctionBatch, TransformationBatch | Traçabilité : agents (Person/Service/Organization), activités, génération |
| ODM2 | Person, Organization, Responsibility, Property, Unit, Procedure, KeywordType, Keyword, Identifier, ObservationBatch, Observation, TimeSeriesSource, ValidationBatch, ValidatedObservation, ControlObservation, Specimen, TransferFunction, TransferFunctionBatch, TransferFunctionSet, TransformationBatch, Transformation, TransformedTimeSeries, Bundle, Memory | Sémantique environnementale de référence (variables, méthodes, actions, provenance, annotations) |
| HydroServer | Property, Unit, Datastream, TimeSeriesSource, ValidatedObservation, TransformedTimeSeries | Implémentation de référence ; justification empirique de plusieurs ADR |
| STAMPLATE Schema | Observatory, Station | Profil de métadonnées STA pour l'environnement |
| FROST-Server | Datastream, Observation | Implémentation de référence STA |
| Helmholtz SMS | Sensor, Actuator, Sampler, Platform, Kit, Procedure ; SMS-CV : Keyword, License | Cycle de vie des instruments, Basic Data ; Configuration inspire Kit ; vocabulaires |
| ISO 19115 | Responsibility (CI_RoleCode), KeywordType (MD_KeywordTypeCode), Keyword (MD_Keywords), Observatory (MD_DataIdentification) | Métadonnées géographiques et gouvernance |
| ISO 19107 | Location | Schéma spatial des géométries |
| schema.org | Person, Organization, Responsibility, Observatory, Project, Machine, Identifier, Memory | Sérialisation JSON-LD (souvent via STAMPLATE) |
| NERC NVS P01 | Property | Vocabulaire des variables environnementales |
| ODM2 Controlled Vocabularies | KeywordType, Keyword, ControlObservation, qualityFlag | Vocabulaires SKOS modérés |
| Theia/OZCAR thesaurus | Property, Keyword | Thésaurus national français des variables (interopérabilité in-situ.theia-land.fr) |
| SANDRE | Site, Station, qualityFlag | Référentiel hydrométrique français |
| WMO | Station, TransferFunction, TransferFunctionSet | Stations hydrologiques et courbes de tarage |
| QUDT / UCUM | Unit | URIs et syntaxe des unités |
| SPDX | License | Identifiants de licences canoniques |
| SWHID / Software Heritage | Algorithm | Identifiant permanent du code source |
| PIDINST (RDA) | Sensor, Actuator, Sampler, Platform, Kit | Métadonnées d'identification pérenne d'instrument (make, model, serialNumber, inventoryNumber) |
| CodeMeta | Algorithm | Métadonnées logicielles |
| ORCID / ROR | Person / Organization | Identifiants persistants (via Identifier) |
| GeoJSON (RFC 7946) | Location | Encodage de la géométrie |
| INSPIRE | Site, Identifier | Interopérabilité géographique européenne |
| DataCite | Project, Bundle | Publication citable (DOI) |
| DCAT | License, Bundle | Vocabulaire de catalogue (export Theia/OZCAR, ENVRI-Hub) |

**Note sur la lecture de cette table** : une source citée sur de nombreuses
entités (ODM2, STA) est une boussole structurante ; une source citée sur une
ou deux entités (GeoJSON, SWHID) apporte une brique précise. Les deux types
sont légitimes - ce qui compte est que chaque citation corresponde à un concept
réellement repris, pas à un alignement de façade.


<div class="page-break"></div>

# Standards de gouvernance et métadonnées

## ISO 19115 - Métadonnées géographiques
Définit `CI_Responsibility` et `CI_RoleCode` pour la gouvernance.
`MD_Keywords` et `MD_KeywordTypeCode` pour la classification thématique.
Utilisé dans BDOH pour `Responsibility` et `Keyword`.
- Norme : https://www.iso.org/standard/53798.html

## ISO 19156 - Observations and Measurements (O&M)
Définit les concepts fondamentaux d'observation, feature of interest,
sampling feature. Base conceptuelle de STA et ODM2.
- Norme : https://www.iso.org/standard/32574.html

**Note 2025** : la version 2023 (ISO 19156:2023, aussi publiée comme OGC OMS) introduit
les SamplingFeature plus riches et formalise la distinction Proximate/Ultimate
FeatureOfInterest que STA 2.0 adopte. BDOH couvre ce besoin via sa propre distinction
SamplingFeature (acte de prélèvement terrain) / FeatureOfInterest (entité stable du
monde), comme acté dans l'ADR-011. Cette approche est plus opérationnelle et
moins abstraite que la terminologie OMS 2023.

## W3C PROV-O - Provenance Ontology
Standard de traçabilité des données. Concepts `wasGeneratedBy`,
`wasAssociatedWith`, `used`. Inspiré le design de `Transformation` et
`ValidationBatch` dans BDOH.
- Spécification : https://www.w3.org/TR/prov-o/

## schema.org
Vocabulaire sémantique pour les métadonnées web. Utilisé par STAMPLATE
pour `Person`, `Organization`, `ResearchProject`. Repris dans BDOH
via `Responsibility` et `Project`.
- Site : https://schema.org


<div class="page-break"></div>

# Références à explorer

## Science ouverte et FAIR
- DataCite Metadata Schema (DOI sur Bundle) :
  https://schema.datacite.org
- DCAT - Data Catalog Vocabulary (catalogue et découverte) :
  https://www.w3.org/TR/vocab-dcat/
- OGC API Records (catalogue géospatial) :
  https://ogcapi.ogc.org/records/
- i-Adopt Framework (interopérabilité des variables, utilisé par Theia/OZCAR FairTOIS) :
  https://i-adopt.github.io/
  Note : FairTOIS a utilisé i-Adopt pour standardiser les noms de variables entre
  observatoires OZCAR. Pertinent pour l'alignement Property <-> thésaurus externes.

## Incertitude de mesure
- ISO GUM - Guide to the Expression of Uncertainty in Measurement :
  https://www.bipm.org/en/committees/jc/jcgm/publications
- ODM2 DataQuality extension :
  https://github.com/ODM2/ODM2/blob/master/doc/ODM2Docs/ext_dataquality.md

## Hydrologie et courbes de tarage
- WMO Guide to Hydrological Practices (Vol. 1, Ch. 5 - Rating curves) :
  https://library.wmo.int/index.php?lvl=notice_display&id=540
- ISO 1100-2 - Measurement of liquid flow in open channels (rating curves) :
  https://www.iso.org/standard/57249.html

## Ecosystème européen à surveiller
- eLTER-RI (European Long Term Ecological Research), infrastructure européenne
  dont OZCAR est le miroir français. Interopérabilité future potentielle avec BDOH :
  https://elter-ri.eu/
- ENVRI-Hub NEXT, harmonisation des métadonnées et vocabulaires à l'échelle européenne
  (réseau des infrastructures de recherche environnementales ESFRI) :
  https://envri-hub.envri-fair.eu/
  Note : Helmholtz contribue à ENVRI-Hub NEXT via STAMPLATE (Claudio et al. 2025,
  Zenodo 10.5281/zenodo.15555563). Surveiller pour l'alignement vocabulaires BDOH.
