# CLAUDE.md — Instructions pour futures conversations BDOH

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

## Fichiers de référence

```
modele_donnees_v3.md     ← modèle de données principal — SOURCE DE VÉRITÉ
bdoh-doc/                ← dépôt MkDocs Material (documentation web)
  mkdocs.yml
  docs/
    index.md
    overview.md
    model/               ← une page par section du modèle
    standards/index.md
    decisions/index.md
```

## Architecture du modèle

### Deux couches distinctes

```
Couche IoT STA 1.1 (optionnelle)
  Datastream → données brutes par capteur
  Observation → valeur brute horodatée, raw, sans qualityFlag

Couche métier BDOH (centrale, obligatoire)
  TimeSerie → agrège N Datastreams via TimeSerieDatastream
  ValidatedObservation → données validées par opérateur ou pipeline
  TransformedTimeSerie → données dérivées via TransferFunctionSet
```

### Hiérarchie principale

```
Observatory → Site → Station → TimeSerie → ValidatedObservation
                             → Datastream → Observation
                             → TransformedTimeSerie
```

### Patterns transversaux — NE PAS MODIFIER SANS ADR

- `resourceType + resourceId` : lien polymorphique (Memory, Identifier,
  HistoricalLocation, HistoricalProject)
- `Historical*` : même structure partout (resourceType, resourceId,
  validFrom, validTo)
- `id` UUID immuable + `code` kebab-case lisible sur toutes les entités
- `license 0..1` + `access 1` sur TimeSerie, Datastream, TransformedTimeSerie
  (pas sur Observatory)

## Sections du modèle (ordre dans le fichier)

```
1. ACTEURS          Person, Organization, Responsibility
2. RÉFÉRENTIELS     Property, Unit, Procedure, Keyword, Identifier
3. GÉOGRAPHIE       Location, HistoricalLocation
4. RÉSEAU           Observatory, Site, Station
4bis. DONNÉES BRUTES  Datastream, Observation  ← couche IoT
5. PROJET           Project, HistoricalProject
6. INSTRUMENTATION  Deployment, Sensor, Equipment
7. OBSERVATION      FeatureOfInterest, TimeSerieDatastream, TimeSerie,
                    ValidationBatch, ValidatedObservation,
                    ControlObservation, SamplingFeature
8. TRANSFORMATION   TransferFunction, TransferFunctionPoint,
                    TransferFunctionSet, HistoricalTransferFunction,
                    Transformation, TransformedTimeSerie
9. ORGANISATION     TimeSeriesBundle, Memory
```

## Décisions clés — à ne pas remettre en question sans contexte

- `processingLevel` absent : la structure encode le niveau
  (Observation=raw, ValidatedObservation=validated, TransformedTimeSerie=derived)
- `HistoricalSensor` absent : remplacé par TimeSerieDatastream
- `license` absent sur Observatory : chaque flux porte sa propre licence
- `unitOfMeasurement` gardé sur Datastream (choix HydroServer/USGS,
  pas le resultType SWE-Common de STA 2.0 draft)
- STA 2.0 Proximate/UltimateFOI non adopté : SamplingFeature +
  FeatureOfInterest couvrent déjà ces cas
- `limsReference` sur SamplingFeature, pas sur ValidatedObservation
- `qualityFlag` unique (good/suspect/bad/missing), mapping ODM2/SANDRE
  documenté dans standards/index.md
- `ValidationBatch` pour grouper les sessions de validation
- `referenceValidationProcedure` sur TimeSerie pour dire quelle
  procédure fait foi parmi plusieurs validations parallèles
- `TransferFunctionSet` + `HistoricalTransferFunction` pour gérer
  l'historique et la coexistence de barèmes différents
- `TransferFunctionPoint` pour les couples x/y de calibration

## Contraintes de formatage — IMPORTANT

Les tableaux Markdown du modèle de données doivent faire **150 caractères
de large maximum**. Quelques lignes peuvent dépasser si vraiment nécessaire
(valeurs possibles très longues) mais cest lexception.

Ne jamais utiliser le tiret long dans les fichiers générés.
Utiliser " - " ou reformuler.

Les en-têtes dentité suivent toujours ce format :
```
### NomEntité
Aligné avec : standard1, standard2
Utilisé par : Entite1 (champ), Entite2 (champ)
Note : explication courte du rôle et des contraintes importantes.
```

---

## Comment régénérer bdoh-doc

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

1. Lire `modele_donnees_v3.md` en entier
2. Découper en pages selon la structure ci-dessus
3. Ajouter les liens internes entre entités (ex: `→ [Station](network.md#station)`)
4. Mettre à jour `decisions/index.md` avec les nouveaux ADR
5. Mettre à jour `standards/index.md` avec les alignements vérifiés
6. Tester avec `mkdocs serve` avant de pousser

### Points de vigilance pour la régénération

- Chaque entité doit avoir son en-tête `Aligné avec` vérifié
- Les liens internes utilisent des ancres depuis les titres `###`
- `rawdata.md` est une nouvelle page à créer (section 4bis)
- `transformation.md` a été profondément remanié — ne pas partir
  de l'ancienne version
- Le vocabulaire `qualityFlag` et son mapping doit apparaître dans
  `standards/index.md`

## Points ouverts pour prochaines sessions

### TRANSFORMATION — priorité haute
```
1. Asymétrie TimeSerie / TransformedTimeSerie

Sur une `TimeSerie`, plusieurs `ValidatedObservation` parallèles peuvent coexister pour le même instant — la `referenceValidationProcedure` dit laquelle fait foi. Sur une `TransformedTimeSerie`, la question est différente : quand on change de `TransferFunctionSet` de référence (nouveau barème, nouvelle courbe de tarage), que se passe-t-il sur les valeurs déjà calculées ?

Trois sous-questions non tranchées :
- Est-ce qu'on recalcule la `TransformedTimeSerie` existante avec le nouveau `TransferFunctionSet` ? Si oui, qui déclenche ce recalcul et comment le tracer dans `Transformation` ?
- Ou est-ce qu'on crée une nouvelle `TransformedTimeSerie` parallèle, et l'ancienne devient inactive ?
- Si recalcul, comment distinguer dans l'historique des `Transformation` le calcul initial du recalcul ?

2. Coexistence de plusieurs TransformedTimeSerie parallèles

Plusieurs `TransformedTimeSerie` peuvent produire la même variable sur la même station — par exemple deux séries de débit issues de deux barèmes différents. `TransferFunctionSet.isReference` dit lequel fait foi à un instant T. Mais la contrainte d'unicité n'est pas encore formalisée :

- Un seul `isReference=true` par `(station, property)` à un instant T ?
- Ou un seul par `TransformedTimeSerie` ?
- Comment on gère le basculement de référence dans le temps — est-ce que `isReference` a lui aussi un `validFrom/validTo` ?

3. Transformation algorithmique pure

Une `TransformedTimeSerie` peut être produite sans `TransferFunctionSet` — via un script Python, un filtre, une agrégation temporelle. Dans ce cas `procedure.transformation` sur `TransformedTimeSerie` porte l'algorithme. La contrainte est : `procedure.transformation` ou au moins une `Transformation` avec `transferFunctionSet` doit être renseignée — pas les deux null. Cette contrainte est documentée mais pas encore formalisée comme ADR.
```

### SCIENCE OUVERTE — priorité moyenne
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

### DOCUMENTATION — priorité haute
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

### INGESTION — priorité basse (v2)
```
7. Format CSV d'import
   → spécification du format attendu par l'API
   → pas de modèle de données supplémentaire nécessaire
   → ValidationBatch couvre déjà la traçabilité

8. Pipeline de validation automatique
   → workflow Wiski/Hydrolab → ValidationBatch
   → validationLogUrl suffit pour l'instant
```

### QUESTIONS NON TRANCHÉES
```
9. Plateforme mobile (bateau, drone)
   → HistoricalLocation sur Sensor ? (YAGNI pour l'instant)

10. samplingPeriod sur Property
    → contrainte documentée mais pas testée sur cas réels
    → samplingPeriodStart ou samplingPeriodMode obligatoire
```
