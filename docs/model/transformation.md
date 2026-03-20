# Transformation

---

## TransferFunction

Utilisé par : [Station](network.md#station) (transferFunctions), [Transformation](#transformation) (transferFunction)

!!! note
    Fonction de conversion d'une mesure brute en valeur physique.
    Exemple : hauteur d'eau → débit via courbe de tarage.

    L'historique des courbes est géré par plusieurs `TransferFunction` avec `validFrom`/`validTo` successifs sur la même `Station + inputProperty + outputProperty`.

| Champ            | Cardinalité  | Définition                              | Valeurs possibles                                                   |
|------------------|--------------|-----------------------------------------|---------------------------------------------------------------------|
| `id`             | 1            | Identifiant technique, clé primaire     | uuid                                                                |
| `name`           | 1            | Nom de la fonction                      | "Courbe de tarage Mercier D610 v3"                                  |
| `station`        | 1 →Sta       | Station associée                        | → [Station](network.md#station)                                     |
| `inputProperty`  | 1 →Prop      | Variable en entrée                      | → [Property](references.md#property) (ex: hauteur)                  |
| `outputProperty` | 1 →Prop      | Variable en sortie                      | → [Property](references.md#property) (ex: débit)                    |
| `type`           | 1            | Type de fonction                        | `rating_curve` \| `linear` \| `polynomial` \| `lookup_table`       |
| `parameters`     | 1            | Coefficients ou table de valeurs (JSON) | {"a":2.1,"b":1.5}                                                   |
| `procedure`      | 0..1 →Proc   | Méthode de construction de la courbe    | → [Procedure](references.md#procedure)                              |
| `operator`       | 0..1 →Org    | Organisation responsable                | → [Organization](actors.md#organization)                            |
| `validFrom`      | 1            | Début de validité                       | "2020-01-01T00:00:00Z"                                              |
| `validTo`        | 0..1         | Fin de validité, null si courante       | null                                                                |

---

## Transformation

Utilisé par : [TransformedTimeSerie](#transformedtimeserie) (transformation)

!!! note
    Instance d'exécution d'une transformation.
    Lie les séries sources à la série produite via une [TransferFunction](#transferfunction).

| Champ              | Cardinalité  | Définition                                    | Valeurs possibles                                    |
|--------------------|--------------|-----------------------------------------------|------------------------------------------------------|
| `id`               | 1            | Identifiant technique, clé primaire           | uuid                                                 |
| `transferFunction` | 1 →TF        | Fonction appliquée                            | → [TransferFunction](#transferfunction)              |
| `inputSeries`      | 1..* →TS     | Séries sources                                | → [TimeSerie](observation.md#timeserie)[]            |
| `outputSeries`     | 1 →TTS       | Série produite                                | → [TransformedTimeSerie](#transformedtimeserie)      |
| `appliedAt`        | 1            | Date d'exécution                              | "2024-04-01T08:00:00Z"                               |
| `appliedBy`        | 0..1 →Per    | Personne ayant lancé la transformation        | → [Person](actors.md#person)                         |
| `validFrom`        | 1            | Début de validité du résultat                 | "2024-01-01T00:00:00Z"                               |
| `validTo`          | 0..1         | Fin de validité                               | null                                                 |

---

## TransformedTimeSerie

Utilisé par : [Station](network.md#station) (transformedSeries), [TimeSeriesBundle](organisation.md#timeseriesbundle) (transformedSeries), [Transformation](#transformation) (outputSeries)

!!! note
    Série dérivée d'une ou plusieurs [TimeSerie](observation.md#timeserie) via une [Transformation](#transformation).
    Exemple : débit calculé à partir de hauteur d'eau.

    Code généré : `{station.code}-{property.code}` ex: "yzr-mer-d610-debit"

| Champ                      | Cardinalité  | Définition                                    | Valeurs possibles                                         |
|----------------------------|--------------|-----------------------------------------------|-----------------------------------------------------------|
| `id`                       | 1            | Identifiant technique, clé primaire           | uuid                                                      |
| `code`                     | 1            | Code généré depuis station + property.code    | "yzr-mer-d610-debit"                                      |
| `name`                     | 1            | Nom de la série dérivée                       | "Débit Mercier au pont D610"                              |
| `description`              | 0..1         | Description libre                             |                                                           |
| `station`                  | 1 →Sta       | Station de rattachement                       | → [Station](network.md#station)                           |
| `property`                 | 1 →Prop      | Variable produite                             | → [Property](references.md#property)                      |
| `unit`                     | 1 →Unit      | Unité de la série dérivée                     | → [Unit](references.md#unit)                              |
| `processingLevel`          | 1            | Niveau de traitement (toujours derived)       | `derived`                                                 |
| `procedure.transformation` | 1 →Proc      | Algorithme appliqué                           | → [Procedure](references.md#procedure) (type=transformation) |
| `transformation`           | 1 →Trans     | Instance de calcul                            | → [Transformation](#transformation)                       |
| `sourceSeries`             | 1..* →TS     | Séries sources utilisées                      | → [TimeSerie](observation.md#timeserie)[]                 |
| `status`                   | 1            | État de la série                              | `active` \| `inactive`                                   |
| `identifier`               | 0..* →Ident  | Codes externes et PID                         | → [Identifier](references.md#identifier)[]                |
| `memory`                   | 0..* →Mem    | Notes et événements                           | → [Memory](organisation.md#memory)[]                      |
