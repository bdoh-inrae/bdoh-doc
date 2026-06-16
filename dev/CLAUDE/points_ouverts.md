---
title: Points ouverts BDOH
subtitle: Ce qui reste à trancher, creuser ou expliciter
source: audit de modele_donnees_v12.md + travail de session, juin 2026
---

# Comment lire ce fichier

Ce fichier possède **ce qui n'est pas tranché** : doutes valides, risques à
nommer, décisions de fond à acter. Il ne possède aucune vérité de structure
(elle vit dans `modele_donnees_v12.md`), aucun pourquoi déjà décidé (dans
`decisions_index.md`), aucun état de standard (dans `sources.md`).

Il remplace l'ancien fichier de points ouverts dont la partie A à D a été
soldée (voir la note ci-dessous). Son ossature vient d'un audit externe du
modèle ; les points déjà résolus par les décisions ADR-051 à ADR-059 en ont
été retirés ou ajustés.

Chaque constat porte un identifiant stable (`S*` structurel, `C*` concret,
`M*` modélisation, `V*` veille) pour être cité ailleurs. Les renvois au modèle
se font par nom d'entité ou de section, jamais par numéro de ligne. Sévérité et
effort servent au triage, pas à la décision.

Convention de rédaction héritée du projet : pas de tiret cadratin ni
demi-cadratin. Deux-points, parenthèses, reformulation.

**Note de solde.** Les points A1 à A7, B1, C1 à C4 de l'ancien fichier sont
tranchés et documentés en ADR-051 à ADR-059. Ne pas les rouvrir sans raison
neuve. Les identifiants `C*`/`S*`/`M*` ci-dessous sont ceux de l'audit et n'ont
aucun lien avec les anciens A/B/C/D.


# Triage

Sévérité : `élevée` (à traiter avant gel du schéma), `moyenne` (à trancher
bientôt), `faible` (cosmétique ou documentaire). Effort : `faible` (édition
ponctuelle), `moyen` (refonte locale ou décision de fond), `élevé` (changement
structurel ou dette de migration).

| ID  | Constat                                                        | Sévérité | Effort  |
|-----|----------------------------------------------------------------|----------|---------|
| C5  | Catalogue TPC agent mentionne encore TransformationBatch       | élevée   | faible  |
| C1  | `Datastream` n'a pas de colonne `code`                         | élevée   | faible  |
| C3  | Couverture de la suppression logique incomplète                | élevée   | faible  |
| C2  | "code obligatoire sur toutes les entités" est trop fort        | moyenne  | faible  |
| C4  | `TimeSeriesSource` sans mécanisme de suppression               | moyenne  | faible  |
| C6  | `codeType` mal classé en discriminant TPC                      | moyenne  | faible  |
| M1  | Valeurs censurées (<LOD, <LOQ) hors de la couche capteur       | élevée   | moyen   |
| M5  | PK UUID sur hypertables et UUID inutile sur tables de valeurs  | élevée   | moyen   |
| S1  | TPC sans FK : intégrité référentielle seulement applicative    | élevée   | élevé   |
| M2  | `aggregationStatistic` mélange cadence et statistique          | moyenne  | moyen   |
| M3  | Provenance point brut vers validé non conservée                | moyenne  | moyen   |
| M4  | `Datastream.system` obligatoire, lourd pour le labo            | moyenne  | moyen   |
| M7  | DataCite Publisher indéfini pour `Dataset`                     | moyenne  | faible  |
| S2  | Double vérité de l'ancrage flux / Deployment                   | moyenne  | moyen   |
| S3  | Invariants applicatifs cumulés : inventaire à tenir            | moyenne  | moyen   |
| S5  | AnalysisObservation hors du graphe TPC et des exports          | moyenne  | moyen   |
| M6  | Export STA : quel Thing pour un ancrage Site ou Observatory    | moyenne  | moyen   |
| M8  | Conformité GeoJSON / CRS et asymétrie géométrie FOI            | faible   | faible  |
| V1  | OGC API Connected Systems comme cible v2                       | veille   | -       |
| V2  | Alignement STAMPLATE et écosystème européen                    | veille   | -       |

Ordre suggéré : les `C*` d'abord (contradictions internes bon marché, dont C5
est un reliquat direct de la dernière session), puis M1 et M5 (robustesse
scientifique et tenue à l'échelle), puis S1 et le reste.


# Forces (état de référence, ne pas casser par mégarde)

- Séparation couche IoT (`Datastream`, `Observation`) et couche métier
  (`TimeSeries`, `ValidatedObservation`, `TransformedTimeSeries`), cousue par
  `TimeSeriesSource`.
- `TimeSeries` comme contrat analytique stable.
- Traçabilité par Batch (PROV-O) cohérente, désormais étendue à la chimie
  (`AnalysisBatch`).
- Séparation UUID (identité) et `code` (confort).
- Règle enum SQL contre Keyword fondée sur un critère de fond (ADR-058).
- Bornes temporelles calculées plutôt que stockées.
- Incertitude modélisée par un générateur (TransferFunctionParameter +
  covariance) plutôt que par des tirages stockés (ADR-056, ADR-057).
- Dataset comme reçu d'export, BDOH n'archive pas (ADR-055).


# Constats concrets et vérifiables

Locaux, actionnables. Probablement des défauts à corriger, pas des choix.

## C5. Le catalogue TPC agent mentionne encore TransformationBatch
**Reliquat de la session A1.** La section *Pattern TPC agent* liste toujours
`TransformationBatch (appliedBy : Person | Machine)`, alors qu'ADR-051 a remplacé
le couple `agentType/agentId` par `runner 1 →Machine` + `algorithm`. La ligne du
catalogue est donc fausse. Question de fond restée non écrite : l'utilisatrice a
posé que toute transformation passe par une machine ou un service (manuel ou auto,
c'est pareil, un humain paramétrise mais ne calcule pas à la main).
**Piste :** retirer `TransformationBatch` du catalogue TPC agent, et acter
explicitement dans la note de `TransformationBatch` ou un ADR que l'exécutant est
toujours une Machine (le `runner`), l'agent humain étant tracé via la
`Responsibility` sur la TTS si besoin. Décision déjà prise oralement, à graver.

## C1. `Datastream` n'a pas de colonne `code`
La table `Datastream` ne liste aucun `code`, alors que la section *Scopes
d'unicité du code* déclare "Datastream unique par ancre" et que le modèle pose
"code obligatoire sur toutes les entités". Incohérence entre trois endroits.
**Piste :** ajouter `code` (slug unique par ancre, comme `TimeSeries`), ou
retirer `Datastream` des scopes si un flux brut n'a pas à être adressable par
slug. À trancher selon que les techniciens naviguent les Datastreams par code.

## C2. "code obligatoire sur toutes les entités" est trop fort
`Bundle`, `Dataset`, `TransferFunctionSet`, `Memory`, `Responsibility`,
`Identifier`, les Batch, les tables de valeurs n'ont pas de `code`. La règle
réelle est : `code` sur les ressources nommées navigables, pas sur tout.
**Piste :** reformuler la section `code` en listant la classe concernée (ou en
la dérivant d'une propriété, par exemple "entités exposées en
`/resources/{uuid}`"). Empêche l'ajout de `code` partout par excès de zèle.

## C3. Couverture de la suppression logique incomplète
La section *Suppression logique* annonce `prevent_physical_delete` sur toutes
les entités, puis énumère deux listes (`status`, `archivedAt`) et une exemption
(jointures). Plusieurs entités référencées n'apparaissent nulle part :
`Specimen`, `ControlObservation`, `TransferFunctionSet`, `Identifier`,
`HistoricalLocation`, `Memory`, `Responsibility`, `Dataset`, et les nouveaux
`AnalysisBatch`, `AnalysisObservation`, `Algorithm`. Mécanisme de désactivation
indéfini pour elles.
**Piste :** déclarer les listes exhaustives et combler (probablement `archivedAt`
pour la plupart), ou les dire illustratives et donner la règle par défaut.
Vérifier chaque entité une à une, y compris celles créées en dernière session.

## C4. `TimeSeriesSource` n'a aucun mécanisme de suppression
Entité centrale de la couture, absente des listes `status`/`archivedAt` et de
l'exemption jointures. Aucune sémantique de désactivation définie pour une table
qui porte l'historique des changements de capteur.
**Piste :** lui ajouter `archivedAt`, ou l'exempter explicitement en justifiant
(une ligne de couture ne se désactive peut-être pas, elle se borne par `validTo`).

## C6. `codeType` mal classé en discriminant TPC
La section enum/Keyword range `codeType` parmi les discriminants TPC. Or
`codeType` (`doi | orcid | ror | sandre | wigos | igsn | pidinst | other`) ne
sélectionne aucune entité cible : c'est `resourceType` qui pilote la résolution
polymorphe d'`Identifier`. `codeType` est une étiquette à liste ouverte par
curation (ajouter Handle ou ARK impose aujourd'hui une migration), donc par le
critère du modèle lui-même il penche vers Keyword ou table de référence. Même
odeur, plus légère, pour `thesaurus` sur `Keyword`.
**Piste :** reclasser `codeType` hors des discriminants TPC, puis choisir : table
de référence `IdentifierScheme` (intégrité base, ajout par donnée) ou Keyword.
Mettre à jour la justification de la grille enum/Keyword en conséquence.


# Points de modélisation à clarifier

## M1. Valeurs censurées (<LOD, <LOQ) hors de la couche capteur
**Partiellement traité en session, à compléter.** `AnalysisObservation` porte
`detectionLimit` et `quantificationLimit`, donc la chimie labo a de quoi situer
une valeur par rapport à ses seuils. Mais il manque toujours : un **code de
censure** explicite (la valeur est-elle un `<LOD`, un `<LOQ`, ou une mesure
réelle ?), absent même sur `AnalysisObservation` ; et toute notion d'incertitude
ou de censure sur `ValidatedObservation` et `Transformation` côté capteur, alors
qu'on y a ajouté `uncertaintyLow/High` mais pas de censure. `qualityFlag`
(good/suspect/bad/missing) ne capte pas la censure.
**Pistes :**
- Ajouter un qualificateur `censoring` (`none | below | above`) sur
  `AnalysisObservation` au minimum, alignable ODM2 (ResultQualifier) ou SANDRE.
- Décider si la censure peut concerner aussi des séries capteur (saturation,
  sous-gamme) et donc remonter sur `ValidatedObservation`/`Transformation`.

## M2. `aggregationStatistic` mélange cadence et statistique
L'enum mêle deux axes orthogonaux : `sporadic` décrit une cadence (pas de temps
irrégulier), les autres décrivent la nature statistique (`instantaneous`,
`average`, `cumulative`, `maximum`...). Une série sporadique en moyenne ne peut
pas être exprimée : `sporadic` avale la dimension statistique. Point distinct de
la décision enum/Keyword (ADR-058) qui a gardé le champ en SQL sans voir ce
mélange d'axes.
**Piste :** séparer deux champs, un pour la statistique (toujours rempli), un
pour la régularité (régulier avec `observationFrequency`, ou irrégulier).
`sporadic` cesse d'être une valeur de `aggregationStatistic`.

## M3. Provenance point brut vers validé non conservée
Le lien `Observation` vers `ValidatedObservation` se reconstruit par jointure
temporelle, sans FK directe. Dans le cas parallèle désormais autorisé (ADR
TimeSeriesSource), une `ValidatedObservation` à l'instant T ne peut plus être
rattachée au point brut exact dont elle dérive. La filiation est au niveau
série/période, pas au point.
**Pistes :**
- Écrire que la lignée point à point n'est pas préservée, seulement la lignée
  série/période. Confirmer que c'est acceptable scientifiquement.
- Si la filiation au point est nécessaire pour les séries critiques : lien
  optionnel `sourceObservation` sur `ValidatedObservation`.

## M4. `Datastream.system` obligatoire, lourd pour le labo
`Datastream.system` est obligatoire et `systemType=sensor`. Pour un `lab_sample`,
cela force un System(sensor) représentant l'analyseur. Avec `AnalysisBatch` qui
porte déjà le `system` analyseur (en option), cette contrainte sur Datastream
devient possiblement redondante pour le labo, ou source de System placeholder.
**Piste :** vérifier sur cas réels si `system` obligatoire est tenable côté labo,
et articuler avec `AnalysisBatch.system` pour éviter de déclarer l'instrument à
deux endroits. Rendre `system` optionnel quand `acquisitionType=lab_sample` est
une option.

## M5. PK UUID sur hypertables et UUID inutile sur tables de valeurs
Les tables de valeurs (`Observation`, `ValidatedObservation`, `Transformation`,
`TransferFunctionPoint`, et maintenant `AnalysisObservation`) ont une PK `id`
uuid mais ne sont cibles d'aucun TPC : leur UUID ne sert pas l'identité citable
qui le justifie ailleurs. Si `Observation` est partitionnée sur
`phenomenonTimeStart` (hypertable TimescaleDB), un index unique doit inclure la
colonne de partition : une PK sur `id` seul est refusée ou impose
`(id, phenomenonTimeStart)`. À l'échelle de milliards de lignes, UUID superflu =
index perdu et localité d'insertion dégradée.
**Pistes :**
- Clarifier quelles tables de valeurs sont des hypertables et comment leur PK
  inclut la colonne de partition.
- Se demander si ces tables ont besoin d'un surrogate UUID, ou si une clé
  naturelle `(série, phenomenonTimeStart)` suffit. `ControlObservation`, cible
  TPC, garde son UUID.

## M6. Export STA : quel Thing pour un ancrage Site ou Observatory
Le mapping STA pose Station égale Thing, mais un `Datastream` peut être ancré
`Site` ou `Observatory`. STA exige `Datastream` vers `Thing`. Comment `/Things`
est-il peuplé pour les flux sans Station ?
**Piste :** définir la règle de résolution du Thing pour les ancrages non-Station
(exposer Site et Observatory comme Things, ou Thing synthétique), dans la couche
d'export.

## M7. DataCite Publisher indéfini pour `Dataset`
Le mapping DataCite dérive Publisher de l'Observatory rattaché, mais `Dataset`
n'a aucun lien Observatory : seulement `dataset_resource` vers des séries qui
peuvent couvrir plusieurs Observatories. La dérivation est indéfinie. Question
voisine : `Bundle.Observatory` est unique, ce qui suppose qu'un Bundle ne mélange
pas plusieurs Observatories, sans que l'invariant soit écrit.
**Pistes :**
- Spécifier la dérivation du Publisher pour Dataset (Observatory commun aux
  ressources, erreur si divergence).
- Écrire l'invariant "un Bundle appartient à un seul Observatory" s'il est voulu,
  et le vérifier à l'ajout dans `bundle_series`.

## M8. Conformité GeoJSON / CRS et asymétrie géométrie FOI
`Location.geometry` est annoncée "application/geo+json" avec un `crs` pouvant
valoir EPSG:2154. GeoJSON (RFC 7946) impose WGS84 : la combinaison n'est pas du
GeoJSON conforme. Connexe : `FeatureOfInterest` embarque sa géométrie inline
alors que tout le reste passe par `Location` (donc pas d'historique de position).
**Pistes :**
- Si le stockage est PostGIS avec sérialisation à la volée, le dire et réserver
  l'étiquette geo+json à la sortie 4326. Sinon distinguer stockage et export.
- Décider si l'asymétrie FOI est assumée (FOI conceptuelle sans historique) ou à
  aligner sur `Location`.


# Risques structurels

Choix de fond, souvent délibérés. Le but est de nommer le coût accepté et de
combler ce qui n'est pas spécifié, pas d'annuler.

## S1. TPC sans FK native : intégrité référentielle seulement applicative
Tous les liens polymorphes (`resourceType+resourceId`, `anchorType+anchorId`,
`agentType+agentId`, `seriesType+seriesId`) n'ont aucune FK PostgreSQL. Les
triggers valident à l'écriture mais ne couvrent pas le sens inverse : rien
n'empêche un `resourceId` de pointer vers une entité archivée, la cascade n'est
définie nulle part (que devient un `KeywordAssignment` vers une `Property`
deprecated), et la base ne garantit pas que `(resourceType, resourceId)` soit
cohérent.
Cas particulier : `anchor` (Observatory|Site|Station) et `agent`
(Person|Machine|Organization) ont un ensemble cible petit et figé. Ce sont
exactement les cas où "une FK nullable par type + CHECK d'exclusion" donnerait
une vraie intégrité base à coût quasi nul. En les passant en TPC pour
l'uniformité, on abandonne l'intégrité là où elle était la plus facile à garder.
**Pistes (par ambition croissante) :**
- Documenter les garanties réelles : intégrité immédiate à l'écriture, cohérence
  seulement éventuelle pour le reste (job périodique). Nommer la fenêtre tolérée.
- Pour `anchor` et `agent` : FK nullables + CHECK d'exclusion mutuelle, intégrité
  base sans changer l'API.
- Supertable `Resource` (PK partagée par les entités navigables, FK réelle vers
  elle pour `Identifier`, `Memory`, `KeywordAssignment`, `Responsibility`).
  Restaure l'intégrité polymorphe et colle au modèle `/resources/{uuid}`. Coût :
  une jointure de plus.

## S2. Double vérité de l'ancrage flux / Deployment
Le modèle dit que chaque flux porte son `anchorType/anchorId` autoportant, que le
`Deployment` porte aussi le sien, et qu'en cas de divergence le flux fait foi.
C'est une redondance avec arbitrage, donc une double vérité, alors que le projet
défend "un seul propriétaire". La raison (éviter la remontée récursive flux vers
System vers Deployment) est une performance légitime, mais ce n'est pas un cas de
propriétaire unique. Sous-problème : la cohérence est mal définie quand un flux
est ancré `Observatory` et le Deployment `Station` ou `Site`.
**Pistes :**
- Nommer la chose : dénormalisation contrôlée motivée par la performance, arbitrée
  en faveur du flux. La sortir du discours "un seul propriétaire".
- Définir la cohérence par inclusion géographique (l'ancre du flux doit être
  l'ancre du Deployment ou un de ses ancêtres) et la porter dans le check.

## S3. Invariants applicatifs cumulés : inventaire à tenir
Beaucoup de contraintes vivent uniquement en applicatif plus job périodique :
ancrage flux/Deployment, ancrage Specimen/Deployment, unicité "une seule location
courante", chaîne ControlObservation vers System vers Deployment, exclusion
runner/algorithme, etc. La correction du modèle dépend de la complétude de ces
règles et de l'exécution des jobs. La base seule ne décrit plus un état valide.
**Piste :** tenir un inventaire unique et exhaustif des invariants applicatifs
(le projet pointe `integrity_checks.md`, vérifier qu'il les couvre tous), avec
pour chacun déclencheur, requête de détection, action, fréquence. Ajouter des
tests qui injectent des violations et vérifient leur détection.

## S5. AnalysisObservation hors du graphe TPC et des exports
**Ajout de cette session.** `AnalysisObservation` et `AnalysisBatch` ont été
créés (ADR-059) mais leur intégration transversale n'a pas été passée en revue :
ils n'apparaissent pas dans les listes de `resourceType` (Identifier, Memory,
KeywordAssignment, Responsibility), ni dans le mapping STA/export, ni dans les
scopes de suppression logique (voir C3). Une mesure chimique citable ou
annotable, ou exportable en STA comme une Observation, n'est pour l'instant pas
raccordée.
**Pistes :**
- Décider si `AnalysisObservation` doit être cible TPC (annotable par Memory,
  citable par Identifier). Probablement non au point de mesure, comme
  ValidatedObservation, mais à acter.
- Vérifier l'export STA d'une `AnalysisObservation` (elle se rattache à une
  TimeSeries lab_sample, donc devrait suivre le même mapping que
  ValidatedObservation, à confirmer).
- Intégrer `AnalysisBatch`/`AnalysisObservation`/`Algorithm` dans la passe C3.

## S4. Historique des valeurs : propriété à écrire, pas à corriger
Le recalcul d'une `TransformedTimeSeries` écrase les valeurs dans
`Transformation`. C'est un choix assumé (ADR-054, fork curé manuel, archive sur
Dataverse). L'audit le confirme comme cohérent, mais souligne deux choses non
écrites : la propriété "BDOH conserve l'état courant, pas la trajectoire" n'est
pas formulée noir sur blanc dans le modèle, et le fork curé dépend du curateur
qui pense à forker avant de recalculer une série déjà exportée dans un Dataset.
**Pistes :**
- Écrire explicitement la propriété dans le modèle (note sur `Transformation` ou
  `TransformedTimeSeries`) : état courant seulement, reproductibilité d'un état
  passé via l'archive externe.
- Optionnel, si l'audit interne devient un besoin : marquer comme immuables les
  valeurs déjà exportées dans un `Dataset`, ou déclencher le fork automatiquement
  avant recalcul d'une série référencée par un export.


# Veille standards

Questions d'évolution, pas de défauts. L'état daté des standards vit dans
`sources.md` (propriétaire unique) ; seules les questions d'alignement non
tranchées sont ici.

## V1. OGC API Connected Systems comme cible v2
CS API est désormais un standard publié et figé (v1.0, voir `sources.md`), donc
la question d'en faire la cible d'une v2 de l'API BDOH devient actionnable sans
risque de cible mouvante. Le pari System + Deployment récursif (ADR-037) s'aligne
déjà dessus.
**Piste :** évaluer le coût d'un export CS API en complément ou remplacement de
STA 1.1, quand la v1 sera stabilisée.

## V2. Alignement STAMPLATE et écosystème européen
Aligner les `properties` exposées en STA sur le schéma formel STAMPLATE
(Helmholtz) pour renforcer l'interopérabilité avec les portails. Surveiller
eLTER-RI et ENVRI-Hub NEXT pour l'alignement des vocabulaires (convergence
DCAT-AP, ISO 19115). Détails et DOI dans `sources.md`.
