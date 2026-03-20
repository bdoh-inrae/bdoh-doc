# Instrumentation

---

## Deployment

Aligné avec : STAMPLATE Platform, SensorML DeploymentProperty

Utilisé par : [Sensor](#sensor) (deployment), [Station](network.md#station) (deployment), [TimeSerie](observation.md#timeserie) (deployment)

!!! note
    Plateforme physique regroupant plusieurs capteurs comme entité cohérente.
    Le `deploymentDepth` sur chaque [Sensor](#sensor) positionne le capteur sur la ligne
    et groupe implicitement les capteurs co-localisés : même profondeur = co-localisés.

    **Exemples** : ligne de capteurs verticale dans une retenue, bouée multi-paramètres, station météo multi-capteurs.

| Champ             | Cardinalité  | Définition                                     | Valeurs possibles                                                        |
|-------------------|--------------|------------------------------------------------|--------------------------------------------------------------------------|
| `id`              | 1            | Identifiant technique, clé primaire            | uuid                                                                     |
| `code`            | 1            | Code court unique                              | "dep-ret-yzr-01"                                                         |
| `name`            | 1            | Nom du déploiement                             | "Ligne de capteurs retenue Yzeron"                                       |
| `description`     | 0..1         | Description libre                              |                                                                          |
| `station`         | 1 →Sta       | Station de rattachement                        | → [Station](network.md#station)                                          |
| `type`            | 1            | Type de plateforme                             | `verticalChain` \| `buoy` \| `weatherStation` \| `multiProbe` \| `other` |
| `deploymentDepth` | 0..1         | Profondeur de référence globale du déploiement | "-2.0"                                                                   |
| `depthReference`  | 0..1         | Référence de profondeur                        | `surfaceRelative` \| `bottomRelative` \| `absoluteElevation`            |
| `installDate`     | 0..1         | Date d'installation                            | "2020-06-01"                                                             |
| `removeDate`      | 0..1         | Date de retrait, null si actif                 | null                                                                     |
| `status`          | 1            | État du déploiement                            | `active` \| `inactive` \| `removed`                                     |
| `location`        | 0..1 →Loc    | Position si différente de la Station           | → [Location](geography.md#location)                                      |
| `equipment`       | 0..* →Equip  | Matériel associé au déploiement                | → [Equipment](#equipment)[]                                              |
| `identifier`      | 0..* →Ident  | Codes externes et PID                          | → [Identifier](references.md#identifier)[]                               |
| `memory`          | 0..* →Mem    | Notes et événements                            | → [Memory](organisation.md#memory)[]                                     |

---

## Sensor

Aligné avec : STA Sensor, STAMPLATE Sensor

Utilisé par : [TimeSerie](observation.md#timeserie) (sensor), [ControlObservation](observation.md#controlobservation) (sensor), [HistoricalSensor](#historicalsensor) (sensor)

!!! note
    Instrument de mesure. [HistoricalSensor](#historicalsensor) trace les changements d'instrument sur une [TimeSerie](observation.md#timeserie).
    Si le capteur appartient à un [Deployment](#deployment), `deploymentDepth` positionne ce capteur sur la ligne et groupe implicitement les capteurs co-localisés.

| Champ                    | Cardinalité  | Définition                                    | Valeurs possibles                                                                        |
|--------------------------|--------------|-----------------------------------------------|------------------------------------------------------------------------------------------|
| `id`                     | 1            | Identifiant technique, clé primaire           | uuid                                                                                     |
| `code`                   | 0..1         | Code optionnel depuis serialNumber            | "sn-2023-00412"                                                                          |
| `name`                   | 1            | Nom de l'instrument                           | "ICP-MS Thermo iCAP RQ"                                                                  |
| `type`                   | 1            | Catégorie d'instrument                        | `icp_ms` \| `spectrophotometer` \| `hplc` \| `probe` \| `autoanalyzer` \| `datalogger` |
| `make`                   | 1            | Fabricant                                     | "Thermo Fisher"                                                                          |
| `model`                  | 1            | Modèle                                        | "iCAP RQ"                                                                                |
| `serialNumber`           | 0..1         | Numéro de série                               | "SN-2023-00412"                                                                          |
| `laboratory`             | 0..1 →Org    | Laboratoire opérateur                         | → [Organization](actors.md#organization)                                                 |
| `deployment`             | 0..1 →Dep    | Déploiement auquel appartient ce capteur      | → [Deployment](#deployment)                                                              |
| `deploymentDepth`        | 0..1         | Profondeur relative du capteur sur la ligne   | "-1.5"                                                                                   |
| `depthReference`         | 0..1         | Référence de profondeur                       | `surfaceRelative` \| `bottomRelative` \| `absoluteElevation`                            |
| `calibrationDate`        | 0..1         | Date de dernière calibration                  | "2024-01-15"                                                                             |
| `calibrationCertificate` | 0..1         | Référence ou URI du certificat                | "CERT-2024-ICP-001"                                                                      |
| `encodingType`           | 1            | Type d'encodage (conformité STA)              | "application/pdf" \| URI                                                                 |
| `metadata`               | 0..1         | URI vers la fiche technique                   | "https://..."                                                                            |
| `identifier`             | 0..* →Ident  | Codes externes et PID                         | → [Identifier](references.md#identifier)[]                                               |
| `memory`                 | 0..* →Mem    | Notes et événements                           | → [Memory](organisation.md#memory)[]                                                     |

---

## HistoricalSensor

!!! note
    Trace la succession des instruments sur une [TimeSerie](observation.md#timeserie) dans le temps.
    Même pattern que [HistoricalLocation](geography.md#historicallocation) et [HistoricalProject](project.md#historicalproject).

| Champ          | Cardinalité | Définition                          | Valeurs possibles |
|----------------|-------------|-------------------------------------|-------------------|
| `id`           | 1           | Identifiant technique, clé primaire | uuid              |
| `sensor`       | 1 →Sen      | Instrument actif sur cette période  | → [Sensor](#sensor) |
| `resourceType` | 1           | Type de ressource ciblée            | `TimeSerie`       |
| `resourceId`   | 1           | UUID de la ressource ciblée         | uuid              |
| `validFrom`    | 1           | Début d'utilisation                 | "2022-03-01"      |
| `validTo`      | 0..1        | Fin d'utilisation, null si actif    | null              |

---

## Equipment

Utilisé par : [SamplingFeature](observation.md#samplingfeature) (equipment), [Station](network.md#station) (equipment), [Deployment](#deployment) (equipment)

!!! note
    Matériel de collecte terrain ou équipement fixe installé à poste.
    Réutilisable entre plusieurs prélèvements et déploiements.

| Champ                | Cardinalité  | Définition                           | Valeurs possibles                                                                                    |
|----------------------|--------------|--------------------------------------|------------------------------------------------------------------------------------------------------|
| `id`                 | 1            | Identifiant technique, clé primaire  | uuid                                                                                                 |
| `code`               | 0..1         | Code optionnel                       | "flacon-hdpe-1l"                                                                                     |
| `name`               | 1            | Nom descriptif                       | "Flacon HDPE 1L bouchon bleu"                                                                        |
| `type`               | 1            | Type de matériel                     | `bottle` \| `pump` \| `autosampler` \| `corer` \| `syringe` \| `filterHolder` \| `datalogger` \| `sensor_probe` |
| `material`           | 0..1         | Matériau de construction             | "HDPE" \| "verre ambré" \| "inox"                                                                    |
| `volume`             | 0..1         | Contenance ou volume en litres       | "1.0"                                                                                                |
| `preservationMethod` | 0..1         | Méthode de conservation              | "acidification HNO3" \| "congélation" \| "obscurité"                                                 |
| `manufacturer`       | 0..1         | Fabricant                            | "Nalgene"                                                                                            |
| `serialNumber`       | 0..1         | Numéro de série                      | "SN-EQ-00231"                                                                                        |
| `owner`              | 0..1 →Org    | Organisation propriétaire            | → [Organization](actors.md#organization)                                                             |
| `identifier`         | 0..* →Ident  | Codes externes et PID                | → [Identifier](references.md#identifier)[]                                                           |
