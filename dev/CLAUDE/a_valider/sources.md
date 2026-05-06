# Sources de référence BDOH

Ce fichier recense les sources consultées pour construire le modèle de données BDOH.
Il permet aux futures sessions de se reformer rapidement sur les standards et projets
de référence sans repartir de zéro.

---

## Standards OGC

### OGC SensorThings API Part 1: Sensing 1.1 (STA)
Standard de base du modèle BDOH pour la structure et l'interface.
- Spécification officielle : https://docs.ogc.org/is/18-088/18-088.html
- Page OGC : https://www.ogc.org/standards/sensorthings/
- Vue d'ensemble : https://ogcapi.ogc.org/senserthings/overview.html
- Version 1.0 (référence historique) : https://docs.ogc.org/is/15-078r6/15-078r6.html

**Etat en 2025-2026** : STA 1.1 reste la référence de production stable. STA 2.0 est
en appel à commentaires publics depuis janvier 2026 -- plus tout à fait un "draft" mais
pas encore ratifié. La principale évolution de STA 2.0 est le passage sur OMS (ISO
19156:2023), ce qui change la terminologie autour de FeatureOfInterest (introduction
des concepts Proximate/Ultimate FOI) et remplace `unitOfMeasurement` par `resultType`
(objet SWE-Common). BDOH a bien fait de ne pas adopter ces concepts instables --
HydroServer et FROST-Server font le même choix. STA 1.1 reste pleinement justifié
en production.

### OGC SensorThings API Extension: STAplus 1.0
Extension pour la science citoyenne et la propriété des observations.
Introduit les concepts de licence et de relations entre observations.
- Page OGC : https://www.ogc.org/standards/sensor-things-api-extension/

### OGC API - Connected Systems (CS API)
Successeur moderne de STA et SOS, basé sur OGC API Features.
Modélisé sur SOSA/SSN. A surveiller pour les évolutions futures de BDOH.
- Spécification Part 1 (Feature Resources) : https://docs.ogc.org/DRAFTS/23-001r0.html
- Spécification Part 2 (Dynamic Data) : https://docs.ogc.org/DRAFTS/23-002r0.html
- GitHub SWG : https://github.com/opengeospatial/ogcapi-connected-systems
- GitHub STA officiel : https://github.com/opengeospatial/sensorthings

**Etat en 2025-2026** : CS API v1.0 est maintenant publié (annonce OGC, février 2026).
C'est le successeur officiel de STA, SOS et SPS -- construit sur OGC API Features,
JSON-LD, SOSA/SSN, SensorML 3.0 (avec encodages JSON désormais standardisés). Il est
conçu pour coexister avec STA plutôt que le remplacer immédiatement : un endpoint CS API
peut lier vers un endpoint STA existant. Pour BDOH, c'est une cible à moyen terme mais
une migration prématurée serait hors de propos. A surveiller pour la v2.

**Ce que CS API apporte par rapport à STA** : une distinction plus propre entre systèmes
statiques (métadonnées de capteurs, plateformes, déploiements -- Part 1) et données
dynamiques (observations, commandes -- Part 2). L'entité `System` généralise le `Thing`
STA à tout type de système connecté (drone, satellite, humain...). L'architecture Part 1
/ Part 2 correspond grossièrement à la distinction couche IoT / couche métier de BDOH.

---

## Modèles de données environnementaux

### ODM2 - Observations Data Model 2
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
pour couvrir une gamme plus large d'observations -- pas seulement les séries temporelles
hydrologiques mais aussi les prélèvements d'échantillons, les profils, les données
multi-dimensionnelles. Il profil l'O&M OGC et structure les relations entre variables,
méthodes, sites et résultats. BDOH en reprend : la sémantique des variables (Property
aligné sur ODM2 Variable), la notion de SamplingFeature (acte de prélèvement terrain),
le concept d'Equipment, et les bonnes pratiques d'usage d'identifiants externes (ORCiD,
DOI, ROR). ODM2 reste une source de vérité sémantique même si son implémentation
technique (XML, WaterOneFlow) est dépassée.

---

## Implémentations de référence

### HydroServer (CUAHSI / Utah State University)
Implémentation de référence STA pour les observatoires environnementaux.
Architecture la plus proche de BDOH : une base, deux API (STA + métier).
Garde `unitOfMeasurement` comme FK vers `Unit` -- choix repris dans BDOH.

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
comme FK vers Unit plutôt que d'adopter le `resultType` SWE-Common de STA 2.0 --
c'est la justification empirique de l'ADR-017 de BDOH.

Différences clés avec BDOH : HydroServer cible les groupes de recherche américains
gérant leurs propres stations (déploiement cloud individuel par groupe). BDOH est plus
centralisé (une dizaine d'observatoires dans une même base). HydroServer n'a pas de
couche de validation multi-étapes ni de système de fonctions de transfert -- ces besoins
sont propres au contexte hydrologique français (SANDRE, courbes de tarage, QJXA).
HydroServer s'intègre à HydroShare pour l'archivage long terme -- équivalent
potentiel du TimeSeriesBundle BDOH pour la publication.

La séparation entre ingestion (Streaming Data Loader -- outil externe) et gestion
(Data Management App) dans HydroServer confirme que la couche de transformation est
traitée comme externe au core. Argument en faveur de "BDOH documente plutôt qu'exécute"
pour les transformations (point ouvert ADR sur TransformationBatch).

### STAMPLATE (Helmholtz Earth & Environment)
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
de l'extension STA pour les sciences environnementales -- 7 centres, des milliers de
capteurs, des infrastructures allant des observatoires terrestres (TERENO) aux systèmes
embarqués (IAGOS). Leur approche technique diffère de BDOH : ils étendent STA via les
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

### FROST-Server (Fraunhofer)
Implémentation open source de STA. Base PostgreSQL avec séparation
données statiques / dynamiques. Utilisé par Helmholtz comme serveur STA.
- GitHub : https://github.com/FraunhoferIOSB/FROST-Server

---

## Réseaux d'observatoires français

### Theia/OZCAR
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
l'infrastructure de recherche nationale dédiée à la Zone Critique -- la fine pellicule
entre roche non altérée et basse atmosphère, là où se produisent les transferts d'eau,
d'énergie et de matière.

Le SI Theia/OZCAR a construit un "modèle de données pivot" basé sur ISO 19115/INSPIRE,
O&M et DataCite. Il expose les données via SensorThings (séries temporelles) et CSW
(catalogue). La recherche par variable est identifiée comme le besoin premier des
utilisateurs -- c'est la justification centrale du quadriptyque Keyword de BDOH
(ADR-030) et de l'alignement de Keyword.uri sur le thésaurus Theia/OZCAR.

**Interopérabilité BDOH - Theia/OZCAR** : les URIs du thésaurus Theia/OZCAR dans
`Keyword.uri` ne sont pas des métadonnées de confort -- c'est le lien qui rend les
données de BDOH découvrables depuis le portail national in-situ.theia-land.fr.
Les `Identifier` portant les codes SANDRE, les `Keyword` alignés sur le thésaurus
OZCAR, et le `TimeSeriesBundle` comme objet de publication sont les trois points
de contact critiques pour cette interopérabilité.

Projet ANR FairTOIS (2020-2022) : a consolidé l'implémentation FAIR du SI Theia/OZCAR.
Au démarrage du projet, 7 observatoires sur 22 étaient visibles sur le portail -- 16/22
à la fin. BDOH opère dans ce contexte d'hétérogénéité et de transition vers la FAIRisation.

---

## Vocabulaires contrôlés

### NERC NVS P01 - Vocabulaire des variables
45 000+ concepts de variables environnementales avec URIs stables.
Structure composite : propriété + objet d'intérêt + milieu + méthode.
Utilisé dans BDOH via `identifier` sur `Property`.
- Vocabulaire en ligne : https://vocab.nerc.ac.uk/collection/P01/current/

### Helmholtz SMS CV - Sensor Management System
Vocabulaire pour les capteurs et variables. Apporte : `samplingMedium`,
`aggregationType`, `status`, `definition`.
Utilisé dans BDOH pour les champs de `Property`.
- SMS open source :
  Lorenz C. et al. (2025). Sensor Management System (SMS): Open-source
  software for FAIR sensor metadata management in Earth system sciences.
  arXiv. https://doi.org/10.48550/arXiv.2512.17280

### SANDRE - Service d'Administration Nationale des Données et Référentiels sur l'Eau
Référentiel français pour les codes de qualité des données hydrométriques.
Mapping qualityFlag BDOH : good=1, suspect=3, bad=4, missing=lacune.
- Site : https://www.sandre.eaufrance.fr

### QUDT - Quantities, Units, Dimensions and Types
URIs pour les unités de mesure. Utilisé dans `Unit.definition`.
- Site : https://qudt.org

---

## Standards de gouvernance et métadonnées

### ISO 19115 - Métadonnées géographiques
Définit `CI_Responsibility` et `CI_RoleCode` pour la gouvernance.
`MD_Keywords` et `MD_KeywordTypeCode` pour la classification thématique.
Utilisé dans BDOH pour `Responsibility` et `Keyword`.
- Norme : https://www.iso.org/standard/53798.html

### ISO 19156 - Observations and Measurements (O&M)
Définit les concepts fondamentaux d'observation, feature of interest,
sampling feature. Base conceptuelle de STA et ODM2.
- Norme : https://www.iso.org/standard/32574.html

**Note 2025** : la version 2023 (ISO 19156:2023, aussi publiée comme OGC OMS) introduit
les SamplingFeature plus riches et formalise la distinction Proximate/Ultimate
FeatureOfInterest que STA 2.0 adopte. BDOH couvre ce besoin via sa propre distinction
SamplingFeature (acte de prélèvement terrain) / FeatureOfInterest (entité stable du
monde) -- ADR-011. Cette approche est plus opérationnelle et moins abstraite que la
terminologie OMS 2023.

### W3C PROV-O - Provenance Ontology
Standard de traçabilité des données. Concepts `wasGeneratedBy`,
`wasAssociatedWith`, `used`. Inspiré le design de `Transformation` et
`ValidationBatch` dans BDOH.
- Spécification : https://www.w3.org/TR/prov-o/

### schema.org
Vocabulaire sémantique pour les métadonnées web. Utilisé par STAMPLATE
pour `Person`, `Organization`, `ResearchProject`. Repris dans BDOH
via `Responsibility` et `Project`.
- Site : https://schema.org

---

## Références à explorer pour les prochaines sessions

### Science ouverte et FAIR
- DataCite Metadata Schema (DOI sur TimeSeriesBundle) :
  https://schema.datacite.org
- DCAT - Data Catalog Vocabulary (catalogue et découverte) :
  https://www.w3.org/TR/vocab-dcat/
- OGC API Records (catalogue géospatial) :
  https://ogcapi.ogc.org/records/
- i-Adopt Framework (interopérabilité des variables -- utilisé par Theia/OZCAR FairTOIS) :
  https://i-adopt.github.io/
  Note : FairTOIS a utilisé i-Adopt pour standardiser les noms de variables entre
  observatoires OZCAR. Pertinent pour l'alignement Property <-> thésaurus externes.

### Incertitude de mesure
- ISO GUM - Guide to the Expression of Uncertainty in Measurement :
  https://www.bipm.org/en/committees/jc/jcgm/publications
- ODM2 DataQuality extension :
  https://github.com/ODM2/ODM2/blob/master/doc/ODM2Docs/ext_dataquality.md

### Hydrologie et courbes de tarage
- WMO Guide to Hydrological Practices (Vol. 1, Ch. 5 - Rating curves) :
  https://library.wmo.int/index.php?lvl=notice_display&id=540
- ISO 1100-2 - Measurement of liquid flow in open channels (rating curves) :
  https://www.iso.org/standard/57249.html

### Ecosystème européen à surveiller
- eLTER-RI (European Long Term Ecological Research) -- infrastructure européenne
  dont OZCAR est le miroir français. Interopérabilité future potentielle avec BDOH :
  https://elter-ri.eu/
- ENVRI-Hub NEXT -- harmonisation métadonnées et vocabulaires à l'échelle européenne
  (réseau des infrastructures de recherche environnementales ESFRI) :
  https://envri-hub.envri-fair.eu/
  Note : Helmholtz contribue à ENVRI-Hub NEXT via STAMPLATE (Claudio et al. 2025,
  Zenodo 10.5281/zenodo.15555563). Surveiller pour l'alignement vocabulaires BDOH.
