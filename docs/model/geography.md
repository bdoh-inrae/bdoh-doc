# Géographie

Les entités géographiques sont transversales — elles sont utilisées par Observatory, Site, Station et SamplingFeature.

---

## Location

Utilisé par : [HistoricalLocation](#historicallocation), [Observatory](network.md#observatory), [Site](network.md#site), [Station](network.md#station), [Deployment](instrumentation.md#deployment), [SamplingFeature](observation.md#samplingfeature)

!!! note
    Décrit uniquement la géométrie, sans dimension temporelle.
    La temporalité est portée par [HistoricalLocation](#historicallocation).
    Les ressources gardent un lien direct vers leur `location` courante pour les requêtes simples.

| Champ          | Cardinalité | Définition                          | Valeurs possibles                    |
|----------------|-------------|-------------------------------------|--------------------------------------|
| `id`           | 1           | Identifiant technique, clé primaire | uuid                                 |
| `encodingType` | 1           | Type d'encodage (conformité STA)    | "application/geo+json"               |
| `geometry`     | 1           | Géométrie GeoJSON                   | `Point` \| `Polygon` \| `LineString` |
| `crs`          | 1           | Système de référence de coordonnées | "EPSG:4326" \| "EPSG:2154"           |
| `description`  | 0..1        | Description libre                   |                                      |

---

## HistoricalLocation

Aligné avec : STA HistoricalLocation

Utilisé par : [Observatory](network.md#observatory), [Site](network.md#site), [Station](network.md#station) (via resourceType + resourceId)

!!! note
    Trace les changements de position géographique dans le temps.
    Source de vérité unique pour le lien ressource → localisation.
    Même pattern que [HistoricalProject](project.md#historicalproject) et [HistoricalSensor](instrumentation.md#historicalsensor).

| Champ          | Cardinalité | Définition                          | Valeurs possibles                    |
|----------------|-------------|-------------------------------------|--------------------------------------|
| `id`           | 1           | Identifiant technique, clé primaire | uuid                                 |
| `location`     | 1 →Loc      | Géométrie associée                  | → [Location](#location)              |
| `resourceType` | 1           | Type de ressource ciblée            | `Observatory` \| `Site` \| `Station` |
| `resourceId`   | 1           | UUID de la ressource ciblée         | uuid                                 |
| `validFrom`    | 1           | Début de validité                   | "2014-04-17T00:00:00Z"               |
| `validTo`      | 0..1        | Fin de validité, null si courant    | null                                 |
