# Projet

---

## Project

Aligné avec : schema.org/ResearchProject, STAplus Campaign, DataCite relatedIdentifier

Utilisé par : [HistoricalProject](#historicalproject) (project), [SamplingFeature](observation.md#samplingfeature) (project)

!!! note
    Projet structurant de long terme ou campagne de mesure ponctuelle — même objet.
    La granularité est gérée par `parent` et les dates.
    Le lien vers Observatory/Site/Station/TimeSerie se fait **uniquement** via [HistoricalProject](#historicalproject) — source de vérité unique, évite les incohérences.

| Champ            | Cardinalité  | Définition                                | Valeurs possibles                       |
|------------------|--------------|-------------------------------------------|-----------------------------------------|
| `id`             | 1            | Identifiant technique, clé primaire       | uuid                                    |
| `code`           | 1            | Code court unique                         | "osr8" \| "camp-yzr-2023-metaux"        |
| `name`           | 1            | Nom du projet ou de la campagne           | "OSR8" \| "Campagne métaux Yzeron 2023" |
| `description`    | 0..1         | Description scientifique                  |                                         |
| `parent`         | 0..1 →Proj   | Projet parent si sous-projet ou campagne  | → [Project](#project)                   |
| `fundingAgency`  | 0..1 →Org    | Organisme financeur                       | → [Organization](actors.md#organization) |
| `startDate`      | 1            | Début du projet                           | "2020-01-01"                            |
| `endDate`        | 0..1         | Fin du projet, null si actif              | "2024-12-31"                            |
| `status`         | 1            | État du projet                            | `planned` \| `active` \| `completed`   |
| `url`            | 0..1         | Site web du projet                        | "https://..."                           |
| `responsibility` | 0..* →Resp   | Personnes et organisations responsables   | → [Responsibility](actors.md#responsibility)[] |
| `identifier`     | 0..* →Ident  | PIDs externes (ANR, EU Grant...)          | → [Identifier](references.md#identifier)[] |
| `memory`         | 0..* →Mem    | Notes et événements                       | → [Memory](organisation.md#memory)[]    |

---

## HistoricalProject

!!! note
    Trace la succession des projets qui portent une ressource dans le temps.
    Source de vérité unique pour le lien Project → ressource.
    Même pattern que [HistoricalLocation](geography.md#historicallocation) et [HistoricalSensor](instrumentation.md#historicalsensor).

| Champ          | Cardinalité | Définition                          | Valeurs possibles                                    |
|----------------|-------------|-------------------------------------|------------------------------------------------------|
| `id`           | 1           | Identifiant technique, clé primaire | uuid                                                 |
| `project`      | 1 →Proj     | Projet actif sur cette période      | → [Project](#project)                                |
| `resourceType` | 1           | Type de ressource ciblée            | `Observatory` \| `Site` \| `Station` \| `TimeSerie` |
| `resourceId`   | 1           | UUID de la ressource ciblée         | uuid                                                 |
| `validFrom`    | 1           | Début de la période                 | "2012-01-01"                                         |
| `validTo`      | 0..1        | Fin de la période, null si actif    | null                                                 |
