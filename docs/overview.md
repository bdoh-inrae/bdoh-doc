# Vue d'ensemble

## Principes fondateurs

Le modèle BDOH repose sur trois séparations claires héritées de STA et ODM2 :

**1. Ce qui est fixe vs ce qui varie**
La [`TimeSerie`](model/observation.md#timeserie) porte tout ce qui est constant sur l'ensemble de la série (capteur, variable, protocole analytique, milieu). La [`ValidatedObservation`](model/observation.md#validatedobservation) porte chaque point de mesure individuel. Cette séparation garantit la comparabilité des données dans le temps.

**2. La plateforme d'observation vs l'objet observé**
La [`Station`](model/network.md#station) est le *Thing* STA — la plateforme physique qui porte les capteurs. La [`FeatureOfInterest`](model/observation.md#featureofinterest) est l'entité réelle du monde observée (l'eau de surface, les sédiments, la nappe). Une même Station peut observer plusieurs FeatureOfInterest.

**3. Les données vs leur gouvernance**
Le modèle de données décrit ce qui est observé et mesuré. La gestion des droits d'accès est dans la couche applicative (OAuth2). La traçabilité des responsabilités est dans [`Responsibility`](model/actors.md#responsibility).

## Hiérarchie du réseau

```
Observatory
  └── Site
       └── Station
            ├── TimeSerie
            │    └── ValidatedObservation
            └── Deployment
                 └── Sensor
```

## Patterns transversaux

Trois patterns sont utilisés de façon cohérente dans tout le modèle :

### Pattern Historical*
Trace les changements dans le temps sur une ressource. Même structure pour `HistoricalLocation`, `HistoricalProject`, `HistoricalSensor` :

```
resourceType  →  type de la ressource ciblée
resourceId    →  UUID de la ressource ciblée
validFrom     →  début de validité
validTo       →  fin de validité (null si courant)
```

### Pattern Identifier
Codes externes et PIDs vers des référentiels tiers. Applicable à toutes les entités navigables via `resourceType + resourceId`.

### Pattern Memory
Notes contextuelles et événements rattachés à n'importe quelle ressource. Applicable à toutes les entités qui ont un cycle de vie documentable.

## Sections du modèle

| Section | Entités |
|---|---|
| [Acteurs](model/actors.md) | Person, Organization, Responsibility |
| [Référentiels](model/references.md) | Property, Unit, Procedure, Keyword, Identifier |
| [Géographie](model/geography.md) | Location, HistoricalLocation |
| [Réseau de surveillance](model/network.md) | Observatory, Site, Station |
| [Projet](model/project.md) | Project, HistoricalProject |
| [Instrumentation](model/instrumentation.md) | Deployment, Sensor, HistoricalSensor, Equipment |
| [Observation](model/observation.md) | FeatureOfInterest, TimeSerie, ValidatedObservation, ControlObservation, SamplingFeature |
| [Transformation](model/transformation.md) | TransferFunction, Transformation, TransformedTimeSerie |
| [Organisation](model/organisation.md) | TimeSeriesBundle, Memory |
