# Décisions de conception

Ce journal documente les choix structurants du modèle — pourquoi telle option a été retenue, quelles alternatives ont été écartées et pour quelle raison. L'objectif est de rendre le modèle maintenable dans le temps sans avoir à reconstruire le raisonnement depuis zéro.

---

## ADR-001 — STA comme base, étendu par ODM2

**Décision** : utiliser OGC SensorThings API comme modèle de base et l'enrichir avec les métadonnées d'ODM2.

**Contexte** : STA est léger, REST/JSON, orienté IoT — mais trop générique pour les observatoires environnementaux. ODM2 est riche sémantiquement mais daté technologiquement (XML, WaterOneFlow).

**Choix retenu** : STA pour la structure et l'interface, ODM2 pour la sémantique des métadonnées environnementales. C'est exactement l'approche de Horsburgh et al. (2024) avec HydroServer.

**Références** : Horsburgh et al. (2024), *Environmental Modelling and Software* doi:10.1016/j.envsoft.2024.106241

---

## ADR-002 — TimeSerie comme contrat analytique

**Décision** : la `TimeSerie` porte tout ce qui est fixe pour toute la série — capteur, variable, protocole analytique, milieu. Elle ne porte pas les observations individuelles.

**Contexte** : dans STA, le `Datastream` est déjà ce concept. BDOH le renforce en y attachant explicitement `procedure.observation` comme contrat immuable.

**Conséquence** : si un paramètre analytique change (nouveau protocole, nouvel instrument avec impact sur la mesure), c'est une nouvelle `TimeSerie`. Le changement de capteur sans impact sur la comparabilité est tracé via `HistoricalSensor`.

---

## ADR-003 — Station vs FeatureOfInterest

**Décision** : distinguer explicitement la `Station` (plateforme physique qui porte les capteurs) de la `FeatureOfInterest` (entité réelle du monde observée).

**Contexte** : certaines implémentations STA confondent les deux en faisant pointer `FeatureOfInterest` vers la position de la station. C'est une simplification pratique mais sémantiquement incorrecte selon OGC O&M.

**Choix retenu** : la `Station` est le *Thing* STA — elle porte les capteurs. La `FeatureOfInterest` est l'eau de surface, les sédiments, la nappe — ce qu'on observe réellement. Une même station peut avoir plusieurs `FeatureOfInterest`.

---

## ADR-004 — Pattern resourceType + resourceId

**Décision** : utiliser un pattern polymorphique `resourceType + resourceId` pour les entités transversales (`Memory`, `Identifier`, `HistoricalLocation`, `HistoricalProject`, `HistoricalSensor`).

**Contexte** : deux alternatives ont été étudiées :
- colonnes séparées (`observatory_id`, `site_id`, `station_id`...) → intégrité référentielle automatique en base mais schéma verbeux
- `resourceType + resourceId` → perd la FK constraint mais schéma uniforme et extensible

**Choix retenu** : `resourceType + resourceId` pour trois raisons :
1. cohérence : une seule convention pour toutes les entités transversales
2. extensibilité : ajouter un nouveau type de ressource = ajouter une valeur dans l'enum, pas modifier le schéma
3. alignement avec les standards récents : STAplus, STAMPLATE utilisent ce pattern

**Contrainte** : l'intégrité référentielle est garantie par l'application, pas par la base.

---

## ADR-005 — Historical* : pattern uniforme

**Décision** : toutes les entités `Historical*` (`HistoricalLocation`, `HistoricalProject`, `HistoricalSensor`) partagent la même structure : `resourceType + resourceId + validFrom + validTo`.

**Contexte** : `HistoricalSensor` aurait pu pointer directement vers `TimeSerie` avec une FK directe. C'est plus simple techniquement et garantit l'intégrité référentielle.

**Choix retenu** : pattern uniforme pour la cohérence des requêtes — un développeur qui connaît `HistoricalLocation` comprend immédiatement `HistoricalSensor`. La légère perte d'intégrité automatique est acceptable.

---

## ADR-006 — Project et HistoricalProject : source de vérité unique

**Décision** : le lien entre un `Project` et les ressources qu'il porte (Observatory, Site, Station, TimeSerie) passe **uniquement** par `HistoricalProject`.

**Contexte** : une première approche ajoutait `Project.observatory` pour un accès direct. Le risque était d'avoir deux sources d'information contradictoires si l'une était modifiée sans l'autre.

**Choix retenu** : `HistoricalProject` est la source de vérité unique. `Project` n'a pas de lien direct vers les ressources. Cela évite toute incohérence et force à passer par l'historique — ce qui est de toute façon nécessaire puisqu'un même observatoire peut être porté successivement par OSR6, OSR7, OSR8.

---

## ADR-007 — LIMS hors modèle

**Décision** : la chaîne analytique interne au laboratoire (réception, préparation, analyse) est hors modèle. Le lien se fait via `ValidatedObservation.limsReference`.

**Contexte** : ODM2 modélise des `Action` chaînées pour tracer toute la chaîne de préparation d'un échantillon. C'est très riche mais très complexe, et cette complexité appartient au LIMS (Laboratory Information Management System) — un SI distinct avec ses propres contraintes réglementaires (COFRAC, ISO 17025).

**Choix retenu** : BDOH décrit **ce qui est observé sur le terrain** (SamplingFeature) et **le résultat certifié** (ValidatedObservation). La boîte noire du labo est documentée par `limsReference` — un pointeur opaque vers le LIMS.

---

## ADR-008 — Property : champs directs vs Keyword

**Décision** : `discipline` et `theme` sont des champs directs dans `Property`, pas des `Keyword`.

**Contexte** : l'approche générique aurait tout mis dans `Keyword` avec des `keywordType` différents. Cela aurait été cohérent avec ISO 19115 mais peu pratique pour filtrer et gérer les variables.

**Choix retenu** : `discipline` et `theme` sont des enums fixes gérés par les curateurs — au même titre que `samplingMedium` ou `aggregationType`. Ils ne varient pas selon le contexte et ne pointent pas vers des thésaurus externes. Les liens vers les thésaurus (Theia/OZCAR, NERC...) passent par `identifier`. `Keyword` reste réservé à la classification éditoriale pour les catalogues (Observatory, TimeSerie, TimeSeriesBundle).

---

## ADR-009 — Identifiants : UUID + code lisible

**Décision** : chaque entité a deux identifiants distincts — un `id` UUID (clé primaire technique) et un `code` lisible humainement (utilisé dans les URLs).

**Contexte** : un entier auto-incrémenté est plus simple mais prévisible (fuite d'information sur le volume) et difficile à fusionner entre bases. Un UUID seul est illisible dans les URLs et les logs.

**Choix retenu** : UUID immuable pour toutes les relations en base, `code` kebab-case pour les URLs et l'affichage. Le `code` peut être modifié sans casser les relations. Convention hiérarchique : `{parent.code}-{segment}`.

---

## ADR-010 — Deployment : grouper les capteurs co-localisés

**Décision** : introduire une entité `Deployment` pour regrouper des capteurs sur une même plateforme physique (ligne verticale, bouée, station multi-capteurs).

**Contexte** : pour reconstruire un profil vertical dans une retenue (température + salinité + position à plusieurs profondeurs), il faut lier les séries entre elles. Plusieurs approches ont été étudiées :
- `pairedTimeSerie` sur `TimeSerie` → couplage au niveau des séries, mais fragile si les capteurs sont séparables
- `pairedSensor` sur `Sensor` → couplage physique, mais incorrect si un capteur peut être déployé seul dans un autre contexte
- `Deployment` + `deploymentDepth` sur `Sensor` → regroupement physique + position relative

**Choix retenu** : `Deployment` comme entité à part entière. Le `deploymentDepth` sur chaque `Sensor` positionne le capteur sur la ligne et groupe implicitement les co-localisés (même profondeur = co-localisés). La requête "donne-moi toutes les séries de la ligne à l'instant T" se fait simplement par `deployment_id`.

---

## ADR-011 — SamplingFeature : frontière avec FeatureOfInterest

**Décision** : `SamplingFeature` représente l'**acte de prélèvement** (événement daté, unique), pas l'entité géographique observée.

**Contexte** : dans STA standard, `FeatureOfInterest` joue les deux rôles selon le contexte — c'est soit le lieu de mesure, soit l'échantillon prélevé. ODM2 distingue proprement `SamplingFeature` (station, point de prélèvement) de `Specimen` (échantillon physique).

**Choix retenu** :
- `FeatureOfInterest` = entité réelle du monde (tronçon de rivière, nappe, sol) — stable, avec un `code` et une géométrie
- `SamplingFeature` = acte de prélèvement terrain — événement daté, lié à une `ValidatedObservation`

---

## ADR-012 — Codes pour les Property : symbol + code

**Décision** : `Property` a deux champs distincts — `code` (kebab-case, utilisé dans les URLs de TimeSerie) et `symbol` (symbole scientifique universel, optionnel).

**Contexte** : "Q" est le symbole universel du débit mais trop court et ambigu dans une URL. "debit" est lisible dans une URL mais n'est pas un symbole scientifique. Les deux ont leur utilité.

**Choix retenu** :
- `code` obligatoire, 2-8 caractères kebab-case, saisi par les curateurs : "debit", "no3", "bact-div"
- `symbol` optionnel, notation scientifique standard : "Q", "NO3", "DOC"

Les codes de `TimeSerie` sont générés par concaténation : `{station.code}-{property.code}` → "yzr-mer-d610-no3"

---

## ADR-013 — variableType : intensive vs extensive

**Décision** : ajouter `variableType` (`intensive` / `extensive`) sur `Property` pour guider les calculs de delta.

**Contexte** : pour calculer un écart entre deux valeurs, la méthode dépend de la nature physique de la variable. Un delta de température = T2 - T1 (variable intensive). Un delta de débit = (Q2 - Q1) / Q1 (variable extensive). Cette information ne peut pas être déduite du nom ou de l'unité.

**Choix retenu** : champ `variableType` explicite sur `Property`, géré par les curateurs. Évite d'encoder une règle de calcul dans le code applicatif qui ne connaît pas la physique de chaque variable.

---

## Points ouverts

Les questions suivantes n'ont pas encore été tranchées et feront l'objet de décisions ultérieures :

- **Plateforme mobile** : si des capteurs embarqués sur des bateaux ou drones sont intégrés, `HistoricalLocation` devra inclure `Sensor` dans son `resourceType` (YAGNI pour l'instant).
- **samplingPeriod** : le format MM-JJ est une simplification. Une année hydrologique peut commencer à des dates différentes selon le contexte géographique — à préciser.
- **TransformedTimeSerie et processingLevel** : la valeur `derived` est toujours fixe — à confirmer qu'aucun cas ne nécessite `raw` ou `validated` sur une série dérivée.
