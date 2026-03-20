# Modèle de données

## Convention de lecture

Chaque entité suit le même ordre de champs :

- **Identifiants** — qui c'est ? → `id`, `code`, `name`, `description`
- **Relations parents** — où ça s'accroche ? → liens vers d'autres entités
- **Métadonnées techniques** — comment c'est ? → champs typés, enums, dates
- **Objets liés** — ce qui en dépend → listes `0..*`

## Cardinalités

| Notation | Signification |
|---|---|
| `1` | Obligatoire, exactement un |
| `0..1` | Optionnel, zéro ou un |
| `1..*` | Un ou plusieurs |
| `0..*` | Zéro ou plusieurs |

## Identifiants

Chaque entité a deux identifiants distincts :

- **`id`** (UUID) — clé primaire technique, immuable, jamais affiché, utilisé pour toutes les relations en base
- **`code`** (string) — identifiant court lisible humainement, utilisé dans les URLs et l'affichage

Les codes suivent la convention hiérarchique `{parent.code}-{segment}` :

```
Observatory : yzr
Site        : yzr-mer
Station     : yzr-mer-d610
TimeSerie   : yzr-mer-d610-hea
```

## Entités du modèle

| Entité | Section | Description courte |
|---|---|---|
| [Person](actors.md#person) | Acteurs | Individu intervenant dans le cycle de vie des données |
| [Organization](actors.md#organization) | Acteurs | Organisme ou institution |
| [Responsibility](actors.md#responsibility) | Acteurs | Lien Person/Organization → ressource avec rôle ISO 19115 |
| [Property](references.md#property) | Référentiels | Variable observée, gérée par les curateurs |
| [Unit](references.md#unit) | Référentiels | Unité de mesure normalisée |
| [Procedure](references.md#procedure) | Référentiels | Protocole analytique, de validation ou de transformation |
| [Keyword](references.md#keyword) | Référentiels | Terme de classification thématique ISO 19115 |
| [Identifier](references.md#identifier) | Référentiels | Identifiant externe / PID vers un référentiel tiers |
| [Location](geography.md#location) | Géographie | Géométrie GeoJSON sans dimension temporelle |
| [HistoricalLocation](geography.md#historicallocation) | Géographie | Succession des positions dans le temps |
| [Observatory](network.md#observatory) | Réseau | Entité racine du réseau de surveillance |
| [Site](network.md#site) | Réseau | Subdivision géographique d'un Observatory |
| [Station](network.md#station) | Réseau | Point de mesure physique (Thing STA) |
| [Project](project.md#project) | Projet | Projet structurant ou campagne de mesure |
| [HistoricalProject](project.md#historicalproject) | Projet | Succession des projets sur une ressource |
| [Deployment](instrumentation.md#deployment) | Instrumentation | Plateforme regroupant plusieurs capteurs |
| [Sensor](instrumentation.md#sensor) | Instrumentation | Instrument de mesure |
| [HistoricalSensor](instrumentation.md#historicalsensor) | Instrumentation | Succession des instruments sur une TimeSerie |
| [Equipment](instrumentation.md#equipment) | Instrumentation | Matériel de collecte terrain |
| [FeatureOfInterest](observation.md#featureofinterest) | Observation | Entité réelle du monde observée |
| [TimeSerie](observation.md#timeserie) | Observation | Contrat analytique d'une série de mesures |
| [ValidatedObservation](observation.md#validatedobservation) | Observation | Point de mesure validé |
| [ControlObservation](observation.md#controlobservation) | Observation | Mesure de contrôle qualité |
| [SamplingFeature](observation.md#samplingfeature) | Observation | Acte de prélèvement terrain |
| [TransferFunction](transformation.md#transferfunction) | Transformation | Fonction de conversion mesure brute → valeur physique |
| [Transformation](transformation.md#transformation) | Transformation | Instance d'exécution d'une transformation |
| [TransformedTimeSerie](transformation.md#transformedtimeserie) | Transformation | Série dérivée via une Transformation |
| [TimeSeriesBundle](organisation.md#timeseriesbundle) | Organisation | Regroupement éditorial de séries |
| [Memory](organisation.md#memory) | Organisation | Note ou événement contextualisé sur une ressource |
