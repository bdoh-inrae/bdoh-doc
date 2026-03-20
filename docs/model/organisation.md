# Organisation

---

## TimeSeriesBundle

Utilisé par : [Observatory](network.md#observatory) (bundles)

!!! note
    Regroupe des [TimeSerie](observation.md#timeserie) et [TransformedTimeSerie](transformation.md#transformedtimeserie) pour la publication ou l'accès thématique groupé.
    **Objet éditorial** — pas un objet technique. Ne sert pas à encoder des relations entre séries.

| Champ               | Cardinalité  | Définition                                     | Valeurs possibles                        |
|---------------------|--------------|------------------------------------------------|------------------------------------------|
| `id`                | 1            | Identifiant technique, clé primaire            | uuid                                     |
| `name`              | 1            | Nom du bundle                                  | "Qualité eau Saône 2024"                 |
| `description`       | 0..1         | Description libre                              |                                          |
| `observatory`       | 1 →Obs       | Observatoire parent                            | → [Observatory](network.md#observatory)  |
| `series`            | 0..* →TS     | Séries brutes incluses                         | → [TimeSerie](observation.md#timeserie)[] |
| `transformedSeries` | 0..* →TTS    | Séries dérivées incluses                       | → [TransformedTimeSerie](transformation.md#transformedtimeserie)[] |
| `theme`             | 0..1         | Thème du regroupement                          | "qualité eau" \| "hydrologie"            |
| `license`           | 0..1         | Licence si différente de l'Observatory         | "CC-BY"                                  |
| `keyword`           | 0..* →Keyw   | Keywords thématiques pour catalogues           | → [Keyword](references.md#keyword)[]     |

---

## Memory

Utilisé par : Observatory, Site, Station, Sensor, Equipment, TimeSerie, TransformedTimeSerie, Deployment, Project (via resourceType + resourceId)

!!! note
    Note contextuelle ou événement daté rattaché à n'importe quelle ressource du modèle.
    **Objet transversal** — ne porte pas de données scientifiques, documente le cycle de vie.
    Les fichiers (photos, documents) sont stockés dans le S3 et référencés via `mediaUrl`.

| Champ          | Cardinalité | Définition                          | Valeurs possibles                                                                                                                    |
|----------------|-------------|-------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------|
| `id`           | 1           | Identifiant technique, clé primaire | uuid                                                                                                                                 |
| `resourceType` | 1           | Type de ressource ciblée            | `Observatory` \| `Site` \| `Station` \| `Sensor` \| `Equipment` \| `TimeSerie` \| `TransformedTimeSerie` \| `Deployment` \| `Project` |
| `resourceId`   | 1           | UUID de la ressource ciblée         | uuid                                                                                                                                 |
| `datetime`     | 1           | Date de la note ou de l'événement   | "2014-04-17T00:00:00Z"                                                                                                               |
| `type`         | 1           | Type de mémo                        | `note` \| `event` \| `document` \| `photo` \| `installation` \| `hydraulic_change` \| `maintenance` \| `incident` \| `calibration`  |
| `title`        | 0..1        | Titre court                         | "Modification contrôle hydraulique"                                                                                                  |
| `content`      | 0..1        | Texte libre                         | "Installation d'une lame déversante"                                                                                                 |
| `mediaUrl`     | 0..*        | Photos ou documents associés (S3)   | "https://storage.obs.fr/memories/2014-lame.jpg"                                                                                      |
| `author`       | 0..1 →Per   | Auteur de la note                   | → [Person](actors.md#person)                                                                                                         |
