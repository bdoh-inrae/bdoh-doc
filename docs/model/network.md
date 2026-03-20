# Réseau de surveillance

La hiérarchie spatiale du réseau : `Observatory → Site → Station`.

---

## Observatory

Aligné avec : STA Thing, schema.org/ResearchProject, ISO 19115, INSPIRE

Utilisé par : [Site](#site) (observatory), [TimeSeriesBundle](organisation.md#timeseriesbundle) (observatory)

!!! note
    Entité racine du réseau de surveillance. Agrège des Sites.
    La licence définie ici s'applique par défaut à toutes les données du réseau.

| Champ                | Cardinalité    | Définition                                  | Valeurs possibles                         |
|----------------------|----------------|---------------------------------------------|-------------------------------------------|
| `id`                 | 1              | Identifiant technique, clé primaire         | uuid                                      |
| `code`               | 1              | Code court unique, saisi par curateur       | "yzr"                                     |
| `name`               | 1              | Nom du réseau                               | "Observatoire de l'Yzeron"                |
| `description`        | 0..1           | Description scientifique                    |                                           |
| `operator`           | 1 →Org         | Organisme gestionnaire principal            | → [Organization](actors.md#organization)  |
| `location`           | 1 →Loc         | Emprise géographique courante               | → [Location](geography.md#location)       |
| `startDate`          | 1              | Date de début                               | "2010-01-01"                              |
| `endDate`            | 0..1           | Date de fin, null si actif                  | null                                      |
| `status`             | 1              | État de l'observatoire                      | `active` \| `inactive` \| `discontinued` |
| `url`                | 0..1           | Site web du réseau                          | "https://..."                             |
| `license`            | 1              | Licence des données par défaut              | `ODbL` \| `CC-BY` \| `CC-BY-SA`          |
| `historicalLocation` | 0..* →HistLoc  | Succession des emprises géographiques       | → [HistoricalLocation](geography.md#historicallocation)[] |
| `historicalProject`  | 0..* →HistProj | Succession des projets structurants         | → [HistoricalProject](project.md#historicalproject)[]     |
| `responsibility`     | 0..* →Resp     | Personnes et organisations responsables     | → [Responsibility](actors.md#responsibility)[]            |
| `keyword`            | 0..* →Keyw     | Keywords thématiques pour catalogues        | → [Keyword](references.md#keyword)[]      |
| `identifier`         | 0..* →Ident    | Codes externes et PID                       | → [Identifier](references.md#identifier)[] |
| `memory`             | 0..* →Mem      | Notes et événements                         | → [Memory](organisation.md#memory)[]      |

---

## Site

Utilisé par : [Observatory](#observatory) (sites), [Station](#station) (site)

!!! note
    Subdivision géographique d'un Observatory.
    Regroupe des Stations sur une entité physique cohérente (bassin versant, lac...).
    Code généré : `{observatory.code}-{segment court}` ex: "yzr-mer"

| Champ                | Cardinalité    | Définition                                       | Valeurs possibles                                                            |
|----------------------|----------------|--------------------------------------------------|------------------------------------------------------------------------------|
| `id`                 | 1              | Identifiant technique, clé primaire              | uuid                                                                         |
| `code`               | 1              | Code court unique                                | "yzr-mer"                                                                    |
| `name`               | 1              | Nom du site                                      | "Bassin versant du Mercier"                                                  |
| `description`        | 0..1           | Description libre                                |                                                                              |
| `observatory`        | 1 →Obs         | Observatoire parent                              | → [Observatory](#observatory)                                                |
| `type`               | 1              | Type d'entité physique                           | `watershed` \| `lake` \| `wetland` \| `aquifer` \| `catchment` \| `estuary` |
| `location`           | 1 →Loc         | Géométrie courante (polygone ou point)           | → [Location](geography.md#location)                                          |
| `area`               | 0..1           | Superficie en km²                                | "245.3"                                                                      |
| `operator`           | 0..1 →Org      | Opérateur si différent de l'Observatory          | → [Organization](actors.md#organization)                                     |
| `historicalLocation` | 0..* →HistLoc  | Succession des périmètres géographiques          | → [HistoricalLocation](geography.md#historicallocation)[]                    |
| `historicalProject`  | 0..* →HistProj | Succession des projets porteurs                  | → [HistoricalProject](project.md#historicalproject)[]                        |
| `responsibility`     | 0..* →Resp     | Personnes et organisations responsables          | → [Responsibility](actors.md#responsibility)[]                               |
| `identifier`         | 0..* →Ident    | Codes externes et PID                            | → [Identifier](references.md#identifier)[]                                   |
| `memory`             | 0..* →Mem      | Notes et événements                              | → [Memory](organisation.md#memory)[]                                         |

---

## Station

Aligné avec : STA Thing

Utilisé par : [Site](#site) (stations), [TimeSerie](observation.md#timeserie) (station), [TransferFunction](transformation.md#transferfunction) (station), [TransformedTimeSerie](transformation.md#transformedtimeserie) (station), [Deployment](instrumentation.md#deployment) (station)

!!! note
    Point de mesure physique — le "Thing" STA.
    Peut appartenir à plusieurs Sites (relation many-to-many).
    Code généré : `{site.code}-{segment court}` ex: "yzr-mer-d610"

| Champ                | Cardinalité    | Définition                              | Valeurs possibles                                                                        |
|----------------------|----------------|-----------------------------------------|------------------------------------------------------------------------------------------|
| `id`                 | 1              | Identifiant technique, clé primaire     | uuid                                                                                     |
| `code`               | 1              | Code court unique                       | "yzr-mer-d610"                                                                           |
| `name`               | 1              | Nom de la station                       | "Mercier au pont D610"                                                                   |
| `description`        | 0..1           | Description libre                       |                                                                                          |
| `site`               | 0..* →Site     | Sites parents (many-to-many)            | → [Site](#site)[]                                                                        |
| `type`               | 1              | Type de station                         | `streamgage` \| `weatherstation` \| `well` \| `soilpit` \| `lakestation` \| `tidegage` |
| `location`           | 1 →Loc         | Position GPS courante                   | → [Location](geography.md#location)                                                      |
| `elevation`          | 0..1           | Altitude en mètres (référentiel local)  | "312.5"                                                                                  |
| `operator`           | 0..1 →Org      | Organisme opérateur                     | → [Organization](actors.md#organization)                                                 |
| `installationDate`   | 0..1           | Date d'installation                     | "1997-01-14"                                                                             |
| `status`             | 1              | État de la station                      | `active` \| `inactive` \| `discontinued`                                                |
| `historicalLocation` | 0..* →HistLoc  | Succession des positions                | → [HistoricalLocation](geography.md#historicallocation)[]                                |
| `historicalProject`  | 0..* →HistProj | Succession des projets porteurs         | → [HistoricalProject](project.md#historicalproject)[]                                    |
| `responsibility`     | 0..* →Resp     | Personnes et organisations responsables | → [Responsibility](actors.md#responsibility)[]                                           |
| `equipment`          | 0..* →Equip    | Équipements fixes installés à poste     | → [Equipment](instrumentation.md#equipment)[]                                            |
| `identifier`         | 0..* →Ident    | Codes externes et PID                   | → [Identifier](references.md#identifier)[]                                               |
| `memory`             | 0..* →Mem      | Notes et événements                     | → [Memory](organisation.md#memory)[]                                                     |
