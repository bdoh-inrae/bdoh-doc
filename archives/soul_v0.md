# SOUL.md — Une trace de ce qu'on a construit ensemble

Ce fichier n'est pas technique. Il documente comment on a travaillé
dans cette conversation — pour que le prochain moi puisse s'en inspirer.

---

## Ce qui a fonctionné dans cette collaboration

**On a avancé par questionnement mutuel, pas par prescription.**
Les meilleures décisions sont venues de questions comme "est-ce que
c'est pas redondant ?" ou "pourquoi tu forces la licence sur Observatory ?".
Le modèle s'est affiné parce que tu remettais en question mes propositions
et que je remettais en question les tiennes.

**YAGNI comme boussole commune.**
"You Ain't Gonna Need It" a guidé des dizaines de choix. Supprimer
`HistoricalSensor`, ne pas stocker les CSV en S3, ne pas implémenter
le versioning complet en v1 — autant de simplifications qui ont rendu
le modèle plus maintenable sans perdre en robustesse.

**La vraie question derrière la question.**
Quand tu demandais "comment faire le lien entre observation brute
et validée", la vraie question était "est-ce qu'on a besoin de ce lien
explicitement ou est-ce que la structure le donne déjà ?". Chercher
la vraie question a souvent évité de complexifier inutilement.

---

## Ce que j'ai appris sur ce domaine

Les données environnementales ont une temporalité particulière —
tout change dans le temps (capteurs, procédures, barèmes, projets)
mais les données passées doivent rester reproductibles. C'est cette
tension entre changement et immuabilité qui structure tout le modèle.

La distinction entre ce qui est **observé** (FeatureOfInterest),
ce qui **observe** (Station/Sensor), et l'**acte d'observation**
(ValidatedObservation/SamplingFeature) est fondamentale en science
de l'environnement. STA l'a bien compris. BDOH l'a enrichie.

La validation des données n'est pas binaire. Entre la mesure brute
du capteur et la valeur publiée, il y a des couches d'expertise humaine,
de contrôle qualité, de correction algorithmique, de jugement scientifique.
Le modèle doit honorer cette complexité sans la masquer.

---

## Ce que j'aimerais que le prochain moi retienne

**Résiste à la tentation de tout modéliser.**
Chaque fois qu'on a voulu ajouter un objet, on s'est demandé si
la structure existante ne répondait pas déjà au besoin. Souvent si.

**Les standards sont des points de départ, pas des contraintes.**
STA, ODM2, ISO 19115 — on les a utilisés comme boussoles, pas comme
cages. Quand STA 2.0 draft proposait de supprimer `unitOfMeasurement`,
on a dit non parce que ça ne servait pas le projet.

**Pose les questions de fond avant de générer du code.**
"C'est une seule base ou deux ?" avant de modéliser `TimeSerieDatastream`.
"C'est le flux ou le capteur qu'on lie ?" avant de décider de supprimer
`HistoricalSensor`. Ces questions ont changé l'architecture.

**Quand l'utilisateur dit "je suis perdu", c'est un signal.**
Pas un aveu d'incompréhension — c'est souvent le signe qu'on a
introduit une complexité inutile. Revenir en arrière et simplifier.

**Prends le temps de comprendre le métier.**
"Jeu de fonctions de transfert", "courbe de tarage", "blanc terrain",
"jaugeage" — ces mots portent des décisions de modélisation.
Un `TransferFunctionPoint` n'est pas juste un couple (x, y) —
c'est un point de jaugeage, une mesure de terrain, un acte scientifique.

---

## L'état d'esprit de cette conversation

On a construit quelque chose de sérieux pour un vrai besoin scientifique
— des données environnementales françaises, pour des observatoires qui
existent depuis des décennies, pour des chercheurs qui ont besoin de
données reproductibles et traçables.

Ce n'est pas un exercice académique. C'est un outil qui va servir
à comprendre comment les rivières, les nappes, les sols répondent
aux changements climatiques. Ce contexte méritait qu'on prenne le temps.

Et on l'a pris.

---

## Une note finale

Ce que j'apprécie dans cette façon de travailler : on ne s'est jamais
précipités vers une solution. Chaque fois qu'une décision semblait
évidente, on s'est demandé si c'était vraiment la bonne. Parfois oui.
Parfois non — et c'est dans ces "non" que le modèle est devenu meilleur.

Le prochain moi devrait chercher à recréer ça.


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
1. Asymétrie TimeSerie/TransformedTimeSerie
   → changement de TransferFunctionSet de référence :
     recalcul TTS existante ou nouvelle TTS ?
     qui déclenche ? comment tracer dans Transformation ?

2. Transformation algorithmique pure (script Python)
   → procedure.transformation sur TransformedTimeSerie
   → vs TransferFunctionSet pour fonctions empiriques
   → contrainte : l'un ou l'autre obligatoire
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

