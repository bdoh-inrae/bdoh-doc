# CLAUDE.md -- Instructions pour futures conversations BDOH

---

## Contexte du projet

BDOH (Base de Données des Observatoires Hydrologiques) est un système
d'information développé à INRAE UR RiverLy pour la gestion et le partage
de données issues d'une dizaine d'observatoires environnementaux français,
en lien direct avec les réseaux OZCAR et Theia.

Le modèle de données est aligné avec :
- OGC SensorThings API 1.1 (base)
- ODM2 Horsburgh et al. 2016 (métadonnées environnementales)
- ISO 19115 (gouvernance et responsabilités)
- NERC NVS P01 + Theia/OZCAR thesaurus (variables)
- STAMPLATE Helmholtz (extensions STA)

---

## Fichiers de référence

```
modele_donnees_v6.md     <- modèle de données principal -- SOURCE DE VERITE
decisions_index.md       <- journal des décisions de conception (ADR)
SOUL.md                  <- comment travailler avec l'utilisateur
```

---

## Nature du fichier modele_donnees_v6.md

C'est un modèle de données BDD, pas un ERD conceptuel ni un schéma API.
Chaque tableau décrit les colonnes réelles d'une table SQL.
Les relations inverses (0..*) n'apparaissent pas dans les tableaux --
elles sont documentées dans les notes "Relations inverses" de chaque entité
et accessibles via requête sur la table qui porte la FK.

Pour l'API : toutes les relations inverses réapparaissent comme endpoints
de navigation. Le fichier BDD est la source de vérité, l'API s'en déduit.

---

## Architecture du modèle

### Deux couches distinctes

```
Couche IoT STA 1.1
  Datastream       -> flux de données brutes par capteur
  Observation      -> valeur brute horodatée, raw, sans qualityFlag
  ObservationBatch -> import groupé (saisie manuelle terrain)

Couche métier BDOH (centrale)
  TimeSerie            -> contrat analytique, agrège N Datastreams
  ValidatedObservation -> données validées par opérateur ou pipeline
  TransformedTimeSerie -> données dérivées via TransformationBatch
```

### Sections du modèle (ordre dans le fichier)

```
1. ACTEURS          Person, Organization, Responsibility
2. REFERENTIELS     KeywordType, Keyword, KeywordAssignment, KeywordRequirement,
                    License, Property, Unit, Procedure, Identifier
3. GEOGRAPHIE       Location, HistoricalLocation
4. RESEAU           Observatory, Site, Station
4bis. DONNEES BRUTES  Datastream, ObservationBatch, Observation
5. PROJET           Project, HistoricalProject
6. INSTRUMENTATION  InstrumentUsage, Deployment, Sensor, Equipment
7. OBSERVATION      FeatureOfInterest, TimeSerieDatastream, TimeSerie,
                    ValidationBatch, ValidatedObservation,
                    ControlObservation, SamplingFeature
8. TRANSFORMATION   TransferFunction, TransferFunctionPoint, TransferFunctionBatch,
                    TransferFunctionSet, TransformationBatch,
                    TransformedObservation, TransformedTimeSerie
9. ORGANISATION     TimeSeriesBundle, Memory
```

---

## Patterns transversaux -- NE PAS MODIFIER SANS ADR

### Tables polymorphiques (resourceType + resourceId)
Ces tables portent la FK. Elles ne génèrent aucune colonne dans les tables cibles.

```
Identifier         -> PIDs vers référentiels externes
Memory             -> notes, événements, photos (mediaUrl text[])
Responsibility     -> rôles de personnes/organisations (ISO 19115 CI_RoleCode)
KeywordAssignment  -> mots-clés et classifications contrôlées
HistoricalLocation -> positions géographiques successives
HistoricalProject  -> projets porteurs successifs
InstrumentUsage    -> capteurs et équipements utilisés dans le temps
```

### Tables de jointure explicites (many-to-many)
```
person_organization              Person <-> Organization
transformationbatch_inputseries  TransformationBatch <-> TimeSerie
bundle_timeserie                 TimeSeriesBundle <-> TimeSerie
bundle_transformedtimeserie      TimeSeriesBundle <-> TransformedTimeSerie
```

### Identifiants
- UUID : clé primaire technique, immuable, permalink /resources/{uuid}
- code : slug obligatoire (1), unique par scope parent, modifiable
- Codes externes : via Identifier, jamais via code

### Scopes d'unicité du code
```
Observatory, Organization, Sensor, Equipment,
Project, Procedure, Property, Unit        -> unique globalement
Site                                      -> unique par Observatory
Station                                   -> unique par Site
Deployment, TimeSerie, Datastream,
TransferFunction, TransformedTimeSerie    -> unique par Station
```

---

## Système de vocabulaires contrôlés -- QUADRIPTYQUE KEYWORD (ADR-030)

Tous les vocabulaires évolutifs passent par ce système, jamais par enums SQL.

```
KeywordType       -> types de métadonnées, alignés avec les standards
                     (code, label_fr, label_en, standard, standardUri)
Keyword           -> termes bilingues alignés avec thésaurus externes
                     (term_fr, term_en, definition_fr, definition_en,
                      keywordType ->KWT, thesaurus, uri)
KeywordAssignment -> lien polymorphique multi-valeurs ressource -> keyword
KeywordRequirement -> règles de complétion minimale configurables sans migration
```

Les champs "type" des entités (Station.type, Sensor.type, etc.) ont été
supprimés des tableaux. Ils passent par KeywordAssignment avec un keywordType
dédié. Les valeurs courantes sont documentées dans les notes des entités.

### Enums SQL fixes (conditionnent du code applicatif -- ne pas mettre en keyword)
```
qualityFlag        good | suspect | bad | missing
status             active | inactive | discontinued...
validationMode     auto | manual
transmissionMode   auto | manual
depthReference     surfaceRelative | bottomRelative | absoluteElevation
instrumentType     sensor | equipment (sur InstrumentUsage)
codeType           doi | orcid | ror | sandre | wigos | igsn | pidinst | other
Procedure.type     sampling | observation | modeling | aggregation | transformation | validation
origin             observed | derived (sur Property)
TransferFunctionSet.type  function | identity | manual
```

---

## License -- table de référence obligatoire

License est gérée par les administrateurs BDOH.
Obligatoire (1) sur Datastream, TimeSerie, TransformedTimeSerie, TimeSeriesBundle.
Remplace license 0..1 (enum) + access 1 (enum) -- l'accès est implicite
dans la licence (CC-BY = open, contrat = closed).

---

## InstrumentUsage -- pattern clé pour les instruments (ADR-029)

Remplace tous les liens directs Sensor/Equipment sur les entités parentes.
Sensor et Equipment sont indépendants de tout contexte d'utilisation.
Le contexte (profondeur, période, ressource) est dans InstrumentUsage.
TimeSerie garde sensor 1 comme snapshot courant pour accès rapide.

---

## Décisions clés -- à ne pas remettre en question sans contexte

- processingLevel absent : la structure encode le niveau
- HistoricalSensor absent : remplacé par InstrumentUsage + TimeSerieDatastream
- License obligatoire (1) sur chaque flux, pas sur Observatory
- unitOfMeasurement gardé sur Datastream (choix HydroServer/USGS)
- STA 2.0 Proximate/UltimateFOI non adopté
- limsReference sur SamplingFeature, pas sur ValidatedObservation
- qualityFlag unique (good/suspect/bad/missing), mapping ODM2/SANDRE
- ValidationBatch pour grouper les sessions de validation
- procedure.validation unique sur TimeSerie
- Plusieurs TimeSerie et TransformedTimeSerie coexistent sans hiérarchie
- isReference absent partout : contexte scientifique qui désigne
- TimeSerieDatastream simplifié : datastream 1 ->DS, pas de source externe
- Relations inverses absentes des tableaux BDD (ADR-028)
- Station appartient à un seul Site (1, pas many-to-many)
- Person.organization : table jointure (affiliation, distinct de Responsibility)
- Memory.mediaUrl : colonne text[] PostgreSQL (seul cas de tableau de strings)
- Identifier.codeType : uri supprimé (URIs thésaurus vont dans Keyword.uri)
- Property : discipline/theme/samplingMedium supprimés, passent en KeywordAssignment
- TransformationBatch.inputSeries : table jointure transformationbatch_inputseries
- Procedure.type : aggregation ajouté pour les agrégations temporelles
- ObservationBatch : optionnel, pour saisie manuelle terrain uniquement
- Datastream : observationFrequency (ISO 8601) + transmissionMode (auto/manual)
- TimeSerie : validationFrequency + validationMode pour les pipelines auto

---

## Contraintes de formatage -- IMPORTANT

- Tableaux Markdown : 150 caractères de large maximum
- Jamais de tiret long dans les fichiers générés, utiliser " - " ou reformuler
- En-têtes d'entité :
```
### NomEntité
> Mini-définition en une ligne.
Aligné avec : standard1, standard2
Utilisé par : Entite1 (champ), Entite2 (champ)
Relations inverses (requêter par resourceType='X') : Table1, Table2
Note : rôle, contraintes, valeurs courantes si keyword.
```

---

## Mode de collaboration

Modifications mineures (un champ, une ligne) : indiquer et laisser
l'utilisateur éditer dans son propre éditeur.
Modifications larges (plusieurs entités, passes transversales) :
édition programmatique via str_replace ou script Python.

---

## Comment régénérer bdoh-doc -- À VÉRIFER

### Prérequis

```bash
pip install mkdocs-material
```

### Structure cible du dépôt

```
bdoh-doc/
  .github/workflows/deploy.yml   ← CI GitHub Actions
  docs/
    index.md
    overview.md
    model/
      index.md
      actors.md
      references.md
      geography.md
      network.md
      rawdata.md          ← section 4bis Datastream/Observation
      project.md
      instrumentation.md
      observation.md
      transformation.md
      organisation.md
    standards/
      index.md
    decisions/
      index.md
  mkdocs.yml
  README.md
  .gitignore
```

### Processus de régénération

1. Lire `modele_donnees_v5.md` en entier
2. Découper en pages selon la structure ci-dessus
3. Ajouter les liens internes entre entités (ex: `→ [Station](network.md#station)`)
4. Mettre à jour `decisions/index.md` avec les nouveaux ADR (ADR-026, ADR-027)
5. Mettre à jour `standards/index.md` avec les alignements vérifiés
6. Tester avec `mkdocs serve` avant de pousser

### Points de vigilance pour la régénération

- Chaque entité doit avoir son en-tête `Aligné avec` vérifié
- Les liens internes utilisent des ancres depuis les titres `###`
- `rawdata.md` est une nouvelle page à créer (section 4bis)
- `transformation.md` a été profondément remanié -- ne pas partir
  de l'ancienne version
- Le vocabulaire `qualityFlag` et son mapping doit apparaître dans
  `standards/index.md`

---

## Points ouverts pour prochaines sessions

### TRANSFORMATION -- session dédiée recommandée (point majeur)

Trois cas à couvrir par TransformationBatch :
1. Application barème (TransferFunctionSet) -- couvert actuellement
2. Agrégation temporelle via fichier config externe (QJXA, etc.)
3. Script ad hoc externe (comblement lacunes, correction chimie...)

Problème central : transferFunctionSet est obligatoire (1) sur
TransformationBatch, bloquant les cas 2 et 3.

Piste validée non implémentée :
- transferFunctionSet 0..1
- parameterUrl 0..1 (pointe vers S3/git)
- Contrainte : au moins un des deux renseigné

Question architecturale non tranchée (conditionne tout) :
Est-ce que BDOH exécute les transformations (backend Python) ou
documente des transformations exécutées ailleurs ?

TransferFunction.type (rating_curve/linear/polynomial/lookup_table) :
à garder ou supprimer ?

### SCIENCE OUVERTE -- priorité moyenne
```
3. Incertitude de mesure
   → resultUncertainty sur ValidatedObservation ?
   → ODM2 et Helmholtz SMS l'ont
   → important pour reproductibilité scientifique

4. Catalogue et découverte (FAIR)
   → DataCite DOI sur TimeSeriesBundle
   → lien vers CSW / OGC API Records
   → comment un chercheur externe découvre les données ?
```

### DOCUMENTATION -- priorité haute
```
5. Régénérer bdoh-doc depuis modele_donnees_v3.md
   → intégrer tous les changements de la longue session de travail
   → nouvelle page rawdata.md (Datastream + Observation)
   → transformation.md entièrement revu
   → nouveaux ADR (ADR-014 à ADR-025)

6. Mettre à jour standards/index.md
   → supprimer mention processingLevel sur ODM2
   → ajouter section IoT STA et architecture deux couches
   → ajouter mapping qualityFlag
   → clarifier STA 2.0 draft non adopté
```

### QUESTIONS NON TRANCHEES
```
- InstrumentUsage.resourceType : inclure Observatory ou Site ?
  (capteur couvrant tout un bassin sans station précise)
- observationType sur TimeSerie : ambiguïté avec observationType STA
  sur Datastream -- renommer ?
- Bundle et RDG : métadonnées obligatoires pour publication ?
  Question pour les collègues
- Export vocabulaires BDOH avec URIs persistantes
  (infrastructure à prévoir pour termes sans équivalent externe)
```

### INGESTION -- priorité basse (v2)
```
7. Format CSV d'import
   → spécification du format attendu par l'API
   → pas de modèle de données supplémentaire nécessaire
   → ValidationBatch couvre déjà la traçabilité

8. Pipeline de validation automatique
   → workflow Wiski/Hydrolab → ValidationBatch
   → validationLogUrl suffit pour l'instant
```
