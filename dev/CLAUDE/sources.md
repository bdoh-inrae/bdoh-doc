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
- Vue d'ensemble : https://ogcapi.ogc.org/sensorthings/overview.html
- Version 1.0 (référence historique) : https://docs.ogc.org/is/15-078r6/15-078r6.html

### OGC SensorThings API Extension: STAplus 1.0
Extension pour la science citoyenne et la propriété des observations.
Introduit les concepts de licence et de relations entre observations.
- Page OGC : https://www.ogc.org/standards/sensor-things-api-extension/

### OGC API - Connected Systems (CS API)
Successeur moderne de STA et SOS, basé sur OGC API Features.
Modélisé sur SOSA/SSN. A surveiller pour les évolutions futures de BDOH.
- Spécification draft : https://docs.ogc.org/DRAFTS/23-001r0.html

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

---

## Implémentations de référence

### HydroServer (CUAHSI / Utah State University)
Implémentation de référence STA pour les observatoires environnementaux.
Architecture la plus proche de BDOH : une base, deux API (STA + métier).
Garde `unitOfMeasurement` comme FK vers `Unit` — choix repris dans BDOH.

- Dépôt GitHub : https://github.com/hydroserver2/hydroserver
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

### STAMPLATE (Helmholtz Earth & Environment)
7 centres de recherche allemands (TERENO, PANGAEA, GEOMAR, UFZ, GFZ...).
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
- Infrastructure STA en cours (guidelines) :
  https://github.com/theia-ozcar-is/sensorthings-guidelines

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
