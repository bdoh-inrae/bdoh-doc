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
| C5  | Catalogue TPC agent mentionne TransformationBatch (clos)       | -        | -       |
| C1  | `Datastream` code manquant (clos)                              | -        | -       |
| C3  | Couverture suppression logique incomplète (clos)               | -        | -       |
| C2  | code obligatoire sur toutes les entités : trop fort (clos)     | -        | -       |
| C4  | `TimeSeriesSource` sans mécanisme de suppression (clos)        | -        | -       |
| C6  | codeType mal classé en discriminant TPC (clos)                 | -        | -       |
| M1  | Valeurs censurées LOD/LOQ hors couche capteur (clos)           | -        | -       |
| M5  | PK UUID sur hypertables et tables de valeurs (clos)            | -        | -       |
| S1  | TPC sans FK native, intégrité applicative seule (clos, ADR-060)| -        | -       |
| M2  | aggregationStatistic mélange cadence et statistique (clos)     | -        | -       |
| M3  | Provenance point brut vers validé non conservée (clos)         | -        | -       |
| M4  | Datastream.system obligatoire, lourd pour le labo (clos)       | -        | -       |
| M7  | DataCite Publisher indéfini pour Dataset (clos)                | -        | -       |
| S2  | Ancrage + lien matériel/agent objets analytiques (en cours)    | haute    | lourd   |
| S3  | Invariants applicatifs cumulés : inventaire à tenir            | moyenne  | moyen   |
| S5  | AnalysisObservation hors graphe TPC (clos)                     | -        | -       |
| M6  | Export STA : Thing pour ancrage Site/Observatory (clos)        | -        | -       |
| M8  | Conformité GeoJSON/CRS et asymétrie géométrie FOI (clos)       | -        | -       |
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

## C5. Le catalogue TPC agent mentionne encore TransformationBatch (clos)
Résolu : `TransformationBatch` retiré du catalogue TPC agent, avec note explicite
que son exécutant est toujours une Machine (le `runner`), jamais un couple
`agentType/agentId`. `AnalysisBatch` ajouté au catalogue à sa place (agent réel,
absent jusqu'ici).

## C1. `Datastream` n'a pas de colonne `code` (clos)
Résolu : `code` ajouté à `Datastream` (slug unique par ancre, en miroir de
`TimeSeries`), et `Datastream` complété dans les six tables transverses resource
où figurent `TimeSeries` et `TransformedTimeSeries` (`Responsibility`,
`KeywordAssignment`, `KeywordRequirement`, `Identifier`, `HistoricalProject`,
`Memory`). La couche brute peut porter des `Identifier` pour l'interopérabilité,
choix assumé conforme à la pratique. Reste ouvert : C2 (formuler la classe qui
porte un `code`) est de même nature mais non tranché ici.

## C2. "code obligatoire sur toutes les entités" est trop fort (clos)
Résolu : la section `code` ne dit plus "obligatoire sur toutes les entités"
mais énonce la règle réelle avec ses listes explicites. Le `code` est présent
et obligatoire sur les entités nommées navigables (17 listées), absent sur les
lignes d'observation, `Person`, `Bundle`, `Dataset`, `Specimen`, `Memory`,
chacune avec sa raison écrite. Décision de fond actée au passage : le `code`
n'est jamais optionnel (obligatoire là où il existe, ou absent), pour éviter la
double vision UUID/code où l'on devine la bonne entrée. `Algorithm` reçoit un
`code` versionné dans le slug ("agregation-qjxa-v3"), sur le modèle déjà en
place de `TransferFunction` ("hea-qmj-v3"), et garde son `name` lisible : pas
d'exception, une seule règle d'URL. Le `swhid` garde son rôle d'épingle de
version, le `code` ne fait que la nommer. Anomalie corrigée en même temps :
`FeatureOfInterest` et `TransferFunctionSet` ajoutés aux scopes d'unicité (le
premier avait un `code` sans scope déclaré, le second reçoit `code` et scope).

## C3. Couverture de la suppression logique incomplète
La section *Suppression logique* annonce `prevent_physical_delete` sur toutes
les entités, puis énumère deux listes (`status`, `archivedAt`) et une exemption
(jointures). Plusieurs entités référencées n'apparaissent nulle part :
`Specimen`, `ControlObservation`, `TransferFunctionSet`, `Identifier`,
`HistoricalLocation`, `Memory`, `Responsibility`, `Dataset`, `Algorithm`.
Mécanisme de désactivation indéfini pour elles.
**Piste :** avant de conclure à un manque, vérifier comme pour `AnalysisBatch`
(voir S5, clos) si l'entité porte déjà `status` ou une colonne équivalente
simplement absente de l'index : plusieurs cas listés ici pourraient être des
oublis d'index plutôt que des trous réels. Pour les vrais trous, déclarer les
listes exhaustives et combler (probablement `archivedAt` pour la plupart), ou
les dire illustratives et donner la règle par défaut.

## C3. Couverture de la suppression logique incomplète (clos)
Résolu, entité par entité, sans supposer de trou avant vérification.
Déjà couvertes, simple oubli d'index : `HistoricalLocation`, `Responsibility`
et `TimeSeriesSource` avaient déjà `validFrom`/`validTo`, qui est leur
mécanisme de désactivation propre (voir C4). `Algorithm` avait déjà `status`.
Vrais trous comblés par `status` : `TransferFunctionSet`, `Dataset`, `Memory`,
`Identifier`, `Specimen` (objet physique réel, peut être détruit ou épuisé,
contrairement à un simple constat figé). Exempté avec raison écrite :
`ControlObservation` seule, constat scientifique figé comme une ligne
`Observation`, jamais obsolète au sens où une station ou un barème peuvent
l'être. La section *Suppression logique* documente maintenant trois
mécanismes (status, archivedAt, validTo) au lieu de deux, et explicite
chaque exemption plutôt que de laisser une entité absente sans dire pourquoi.

## C4. `TimeSeriesSource` n'a aucun mécanisme de suppression (clos)
Faux positif : `TimeSeriesSource` a déjà `validFrom`/`validTo`, qui ferme la
ligne en cas de changement de capteur. Ajouté à la liste des tables datées
dans la section *Suppression logique*. Résolu dans la même passe que C3.

## C6. `codeType` mal classé en discriminant TPC (clos)
Résolu, mais pas par la piste envisagée au départ. Le rangement était bien faux
et corrigé : `codeType` retiré des discriminants TPC (c'est `resourceType` qui
pilote la résolution polymorphe d'`Identifier`, `codeType` ne route rien), et
déplacé dans les comportementaux fermés de la grille enum/Keyword.
Le basculement vers Keyword ou table de référence, en revanche, est écarté.
L'argument de C6 ("liste ouverte donc Keyword") ne tient pas : un type
d'identifiant non prévu n'est jamais purement informatif, il réclame toujours
un traitement propre (format, résolution, validation). Ajouter une valeur est
donc un acte de développement volontaire, exactement le critère qui justifie de
rester en SQL, pas l'inverse. Pas de valeur `other` en secours : elle
laisserait entrer des identifiants sans que ce traitement soit jamais construit,
ce qui aurait été la mauvaise réponse à la question. Et sur le fond,
`Identifier` existe pour porter des identifiants structurellement fiables ; en
faire un `Keyword`, vocabulaire curable au fil de l'eau, casserait cette
garantie. Reste SQL, comme `aggregationStatistic` et `Procedure.type`.
Signalé en passant, non traité : `Keyword.thesaurus` a une odeur similaire
(petite liste apparemment fermée) mais l'enjeu est mineur, purement informatif,
sans garantie d'identité à protéger. Pas un point à part entière.


# Points de modélisation à clarifier

## M1. Valeurs censurées (<LOD, <LOQ) hors de la couche capteur (clos)
Volet chimie résolu : `AnalysisObservation` porte `censoring`
(`none | below_lod | below_loq | above_saturation`), aligné SANDRE RqAna
(nomenclature 155), orthogonal à `qualityFlag`, une valeur censurée reste
`good`. Quand `censoring != none`, `result` porte le seuil concerné, pas une
estimation inventée.
Volet capteur écarté, pas par manque de cas mais par différence de nature :
une échelle dépassée en crue donne quand même un chiffre, par extrapolation de
la courbe de tarage ou méthode indirecte, ce n'est pas une borne connue avec
certitude comme un `<LOQ`, c'est une estimation moins fiable. Déjà couvert par
`uncertaintyLow`/`uncertaintyHigh` (marge élargie) et `qualityFlag=suspect`
(fiabilité réduite) sur `ValidatedObservation`. La censure formaliserait une
certitude qu'on n'a pas dans ce cas. Pas de champ ajouté côté capteur.

## M2. `aggregationStatistic` mélange cadence et statistique (clos)
Résolu par la piste initiale, pas par le contournement documentaire d'abord
tenté. Vérification faite sur ODM2 : `sporadic` y est un terme officiel du
vocabulaire AggregationStatistic, dans la même liste plate que `average` ou
`maximum`, donc le mélange était bien hérité du standard. Première tentative :
documenter que `observationFrequency=null` peut déjà exprimer l'irrégularité
avec n'importe quelle valeur de `aggregationStatistic`, sans toucher au schéma.
Rejetée en relecture : un `null` qui signifie tantôt "sporadic explicite" tantôt
"irrégulier pour une moyenne" est la même ambiguïté que celle éliminée ailleurs
cette session (le `code` obligatoire ou absent, jamais optionnel).
Décision finale : nouveau champ `temporalRegularity` (`regular` \| `irregular`)
sur `Datastream`, `TimeSeries`, `TransformedTimeSeries`, qui gouverne seul la
cardinalité effective de `observationFrequency`. `sporadic` retiré de
`aggregationStatistic`, qui ne porte plus que la nature statistique (7 valeurs).
Écart assumé par rapport à ODM2, justifié dans la note de Datastream : les deux
axes désormais séparés couvrent un cas qu'ODM2 ne sait pas exprimer proprement
non plus (moyenne à pas irrégulier), et la reconstruction du terme `sporadic`
à l'export reste triviale (`instantaneous` + `irregular`).

## M3. Provenance point brut vers validé non conservée (clos)
Résolu : choix assumé et écrit dans la note de `ValidatedObservation`. La
filiation est au niveau batch et période (`ValidationBatch` avec sa fenêtre
`periodStart`/`periodEnd`), pas point à point, et cette granularité existait
déjà sans être nommée comme un choix. Pas de FK point à point ajoutée : une
session de validation ajoute, corrige ou supprime des points bruts en bloc,
une correspondance ligne à ligne n'aurait pas de sens stable, et ça aurait
coûté une colonne sur les tables les plus volumineuses pour un gain que
l'usage ne réclame pas. Porte ouverte pour plus tard si un besoin réel de
lignée point à point apparaît sur des séries critiques.

## M4. `Datastream.system` obligatoire, lourd pour le labo (clos)
Résolu, mais pas par la piste envisagée (rendre `system` optionnel). En
vérifiant, le vrai problème était en amont : `acquisitionType=lab_sample`
n'aurait jamais dû exister sur `Datastream`. La propre définition de l'entité
dit "flux de données brutes pour un unique System(sensor)", et rien
n'oblige une `TimeSeries` à posséder un `TimeSeriesSource` : la chimie labo ne
transite jamais par la couche IoT brute (Specimen vers AnalysisBatch vers
AnalysisObservation, directement vers TimeSeries). `acquisitionType` retiré du
tableau `Datastream` (devenu une colonne à une seule valeur, sans information,
une fois `lab_sample` écarté) et de sa note. `Datastream.system` reste
strictement obligatoire, confirmé : `Datastream` redevient sans exception un
objet capteur, l'assouplir aurait dégradé la qualité des métadonnées pour rien.
Note ajoutée sur `TimeSeries` : jamais de `Datastream` ni de `System(sensor)`
placeholder pour une série lab_sample.
Signalé en passant, traité dans la foulée : `TransformedTimeSeries` portait
aussi `acquisitionType`, retiré. Une série dérivée peut être calculée à partir
de plusieurs entrées mêlées (`transformationbatch_inputseries` accepte
`TimeSeries` et `TransformedTimeSeries`), donc d'origine potentiellement mixte
capteur et labo : un seul champ mentirait dans ce cas. La provenance réelle se
lit dans le `TransformationBatch` et ses entrées, pas dans un raccourci
dupliqué sur la TTS. `TimeSeries` garde le champ sans changement, une série
métier n'a qu'une seule voie d'acquisition, jamais mixte.

## M5. PK UUID sur hypertables et UUID inutile sur tables de valeurs (clos)
Résolu sur les six tables de valeurs. Colonne id uuid retirée, remplacée par
une clé primaire composite naturelle, incluant toujours la colonne de temps
(exigence TimescaleDB : la colonne de partition doit être non nulle et faire
partie de toute clé primaire ou index unique).
Observation : (datastream, phenomenonTimeStart).
ValidatedObservation : (timeSeries, phenomenonTimeStart).
Transformation : (transformedTimeSeries, phenomenonTimeStart).
ControlObservation : (seriesId, phenomenonTimeStart), rejoint le lot après
retrait de son statut de ressource citable (plus simple : citer la série
suffit, ses ControlObservation se retrouvent par seriesId, symétrique des
autres lignes d'observation).
TransferFunctionPoint : (function, x). Cas à part signalé en cours de route :
ce n'est pas une hypertable (une dizaine à une cinquantaine de points par
barème), mais la même raison de fond s'applique, jamais citée individuellement.
AnalysisObservation : (timeSeries, phenomenonTimeStart, replicate). Cas
distinct découvert en cours de route : contrairement aux cinq autres, la
chimie admet plusieurs répétitions analytiques légitimes au même instant, donc
pas de valeur unique garantie par (série, instant) seul. Colonne replicate
ajoutée pour distinguer les répétitions, sans toucher à la colonne de
partition (phenomenonTimeStart reste seule éligible, resultTime est optionnel
donc disqualifié d'office). Réduire les répétitions en une valeur unique, si
besoin, passe par un TransformationBatch ordinaire, aucune nouvelle structure
requise.

## M6. Export STA : quel Thing pour un ancrage Site ou Observatory (clos)
Résolu, et plus simplement que prévu : les trois pièces de la réponse
existaient déjà séparément, Observatory, Site et Station sont chacune déjà
alignées Thing STA de leur côté. Il ne manquait qu'une phrase pour les relier.
Ajoutée dans Pattern TPC anchor : anchorType donne directement l'entité à
exposer comme Thing, pas de résolution synthétique ni de repli sur Station par
défaut, les properties STAMPLATE portées par l'entité réellement ancrée.

## M7. DataCite Publisher indéfini pour `Dataset` (clos)
Résolu, en deux temps, le premier corrigé après discussion. Première passe
écartée : gardait `Bundle.Observatory` comme Publisher choisi par le curateur,
avec repli institutionnel pour Dataset. Rejetée : ne répondait pas au besoin
réel de représenter plusieurs observatoires producteurs, et un champ stocké
`Observatory` sur un Bundle trans-observatoire aurait fini par diverger du
contenu réel, comme tout champ recopié plutôt que dérivé.
Décision finale : `Bundle.Observatory` retiré, aucun champ Observatory sur
Bundle ni Dataset. DataCite distingue Publisher (l'entité qui héberge et
diffuse, singulier) de Contributor (les entités productrices, explicitement
répétable) : Publisher devient une constante institutionnelle (INRAE UR
RiverLy), toujours vraie. Les observatoires producteurs, un ou plusieurs, sont
portés par Contributor (contributorType=HostingInstitution), calculés par
requête à travers bundle_series/dataset_resource jusqu'à l'ancrage des séries
incluses, jamais stockés donc jamais périmés. Filtrer "les Bundles d'un
observatoire" passe par cette même requête, pas par un champ direct.

## M8. Conformité GeoJSON / CRS et asymétrie géométrie FOI (clos)
Résolu sur les deux volets. Un GPS calcule nativement en WGS84 (référentiel des
constellations satellites elles-mêmes) ; le Lambert-93 est toujours une
projection calculée après coup, jamais une sortie brute de mesure, vérifié
concrètement (RGF93 quasi-équivalent WGS84, Lambert-93 = la même position
aplatie en mètres pour la cartographie française). `Location.crs` retiré :
toujours WGS84, conforme GeoJSON (RFC 7946, qui n'autorise aucun autre système
de coordonnées) sans exception à gérer. Une projection locale reste possible à
la demande, à l'export ou dans un outil SIG, jamais stockée en double.
Asymétrie FOI corrigée : `FeatureOfInterest` rejoint `Location` comme les
autres entités géographiques (Observatory, Site, Station, Deployment), au lieu
de dupliquer geometry/encodingType en inline. Ajoutée au domaine de
`HistoricalLocation`, dont le critère ("changements discrets et rares, pas de
suivi continu") correspond exactement au cas réel identifié : un tracé de
berge ou une emprise de zone humide redessinés après une nouvelle campagne.

# Risques structurels

Choix de fond, souvent délibérés. Le but est de nommer le coût accepté et de
combler ce qui n'est pas spécifié, pas d'annuler.

## S1. TPC sans FK native : intégrité référentielle seulement applicative (clos, voir ADR-060)
Fermé : pas de supertable ni de FK native. Le risque visé (un lien polymorphe
pointant vers une ligne qui n'existe plus) suppose une suppression physique
d'une entité référencée, déjà interdite par ADR-043 sur toute entité
référencée. L'intégrité applicative existante (trigger + vérification
périodique) suffit tant que cet invariant tient. Raisonnement complet dans
ADR-060.
Reste un travail réel, distinct de S1 : les quatre grilles TPC (resource,
anchor, agent, series) ont des listes de types qui divergent d'une table à
l'autre sans justification écrite (ex. `AnalysisObservation` absente partout).
Ce n'est pas un défaut de structure mais un défaut de complétude, à traiter
par audit avant de considérer le modèle stabilisé. Voir tâche correspondante
dans `CLAUDE.md`.

## S2. Ancrage et lien au matériel des objets analytiques (lien matériel gravé, ancrage TS/TTS restant)

### A. Ancrage : ACTÉ et gravé
- `Datastream` : anchorType/anchorId dérivés du Deployment courant à la création,
  puis figés, jamais saisis. Le Deployment est la source unique du lieu, le flux
  n'en porte qu'une copie de lecture non éditable. Double vérité levée, lecture
  rapide conservée.
- `Deployment`, `Datastream`, `Specimen` acceptent les trois échelles d'ancrage
  (Observatory | Site | Station). Aucune entité n'a d'ancrage restreint.

### B. Lien au matériel et éclatement de System : ACTÉ et gravé (ADR-062)
Le chantier « lien au matériel » a été tranché et gravé, sous une forme
différente de la proposition initiale (samplerType vers System|Person). Ce qui a
été fait :
- `System` éclaté en cinq entités TPC : Sensor, Actuator, Sampler, Platform, Kit
  (ADR-062, remplace la fusion d'ADR-037). Métadonnées alignées SensorML / SMS /
  PIDINST. `equipment` réabsorbé dans Sampler. `Actuator` ajouté (SOSA) pour la
  préparation de labo. `Kit` (propre à BDOH) pour regrouper du matériel sans
  portage physique, composition portée par la récursivité de Deployment.
- Le lien objet analytique vers matériel pointe vers un `Deployment` (pas vers
  un System nu), uniformément : `Datastream.deployment`, `ControlObservation.deployment`,
  `AnalysisBatch.sensor`, `Specimen.deployment`. Le Deployment porte l'objet, le
  lieu et la période. La proposition initiale d'un `samplerType` polymorphe
  System|Person a été écartée au profit de ce lien vers Deployment : plus simple,
  et cohérent avec ce que Datastream faisait déjà.
- `specimen_deployment` (table de jointure M2M) remplacée par la colonne
  `Specimen.deployment` (un seul Deployment, Kit composite si plusieurs objets).
  La relation un Deployment vers plusieurs Specimens se lit par requête inverse.
- C.1 (note d'ancrage périmée de Specimen) corrigée dans la foulée.

### C. Restant ouvert sur l'ancrage de TimeSeries et TransformedTimeSeries
Principe unique dégagé (à appliquer) : l'ancre admin est DÉRIVÉE quand une source
de rattachement existe, SAISIE sinon, jamais les deux à la fois. Application non
encore gravée :
- TransformedTimeSeries : source toujours présente une fois le premier
  TransformationBatch créé (ses séries d'entrée sont ancrées), mais ABSENTE tant
  qu'aucun batch n'existe (une TTS est créée avant son batch). Même régime mixte
  que TimeSeries, contrairement à ce qu'on croyait (« toujours dérivée »).
- TimeSeries : source présente si alimentée par des Datastreams (IoT), absente si
  dépôt direct ou série de labo. Régime mixte : dérivée si source, saisie sinon.
- Décision de forme non tranchée : champ explicite `anchorMode` (derived|manual)
  sur ces deux entités, ou règle purement applicative sans champ (qui part alors
  dans S3). Recommandation : pas de champ, déduction par présence de source,
  comme pour Datastream ; à confirmer.
- Sticky à graver : une fois une série dérivée au moins une fois, elle le reste
  même si toutes ses sources ferment (pas de retour au régime manuel), pour ne
  pas rouvrir une fenêtre d'édition dangereuse après coup. Va aussi dans S3.

### D. Restant ouvert : articulation préparation/mesure au labo (Actuator)
`Actuator` existe désormais comme entité, mais son branchement sur la chaîne
analytique n'est pas modélisé. Un appareil de préparation (broyeur, doseur,
centrifugeuse) transforme un Specimen en Specimen enfant (derivedFrom), mais
aucun champ ne trace QUEL Actuator a produit cette filiation. `AnalysisBatch`
produit une AnalysisObservation (une mesure), pas un Specimen enfant, donc ne
couvre pas l'étape de préparation. À trancher : faut-il un lien
Specimen(enfant) vers Actuator, ou un acte de préparation dédié ? Question de
terrain (granularité de traçabilité voulue au labo) à poser à l'utilisatrice.

### E. Restant ouvert : renommage de Machine
`Machine` (entité agent : service, runner, pipeline) porte un nom qui évoque un
objet physique, alors que le physique est maintenant Sensor/Actuator/Sampler/
Platform. La distinction de fond est claire (Machine = ce qui a un swhid, agent
logiciel ; les entités d'instrumentation = ce qui a un serialNumber ou pidinst).
Reste le nom : `Service` envisagé, mais bute sur `Algorithm.runner` qui désigne
l'infrastructure d'exécution (serveur, HPC), sens différent de l'agent logiciel.
À trancher séparément, l'utilisatrice le suit de son côté.

### Ordre de reprise suggéré
1. Ancrage TS/TTS (partie C) : trancher la forme (champ ou règle) et graver.
2. Articulation Actuator au labo (partie D) : question de terrain d'abord.
3. Renommage Machine (partie E) : chantier autonome.

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

## S5. AnalysisObservation hors du graphe TPC et des exports (clos)
Résolu sur les deux volets vérifiés. TPC resource : `AnalysisObservation` est
une ligne de donnée symétrique de `ValidatedObservation`, correctement absente
de `Identifier`/`Memory`/`KeywordAssignment`/`Responsibility`, ce n'est pas un
oubli. Suppression logique : `AnalysisBatch` porte déjà `status` (comme
`ValidationBatch`, `ObservationBatch`), simplement absent de l'index canonique,
corrigé. `AnalysisObservation` n'en a pas besoin, même raison que
`ValidatedObservation`. Reste hors scope, non traité ici : le mapping export STA
d'`AnalysisObservation`, question distincte à traiter avec M6 le jour où
l'export STA de la chaîne labo devient prioritaire.

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
