---
title: Audit du modèle de données BDOH v12
subtitle: Vérification des standards, compléments aux points ouverts, nouveaux constats
source: lecture intégrale de modele_donnees_v12.md, decisions_index.md, points_ouverts.md, sources.md + vérification en ligne des standards
date: juillet 2026
---

# Comment lire ce fichier

Ce document est un rapport d'audit, pas un fichier du projet. Il ne possède
aucune vérité : chaque constat est destiné à être soit versé dans
`points_ouverts.md` (les identifiants C7 à C18, M9 à M14 et S6 prolongent la
numérotation existante pour faciliter le transfert), soit corrigé directement
dans le modèle s'il s'agit d'une simple divergence documentaire, soit écarté
après discussion. Rien ici n'est à recopier tel quel dans deux fichiers.

Verdict global d'abord, pour situer : le modèle est solide. La séparation des
couches, le contrat analytique, le pattern TPC unifié, la grille enum/Keyword,
les bornes calculées et le triptyque incertitude sont cohérents entre eux et
confirmés par les implémentations de référence (HydroServer, STAMPLATE,
WiSSkHy). L'essentiel de ce qui suit relève de trois familles : des
divergences internes entre l'index et les tables (bon marché, à corriger avant
gel), une zone encore floue (la chaîne laboratoire, seul endroit où deux
chemins coexistent sans règle écrite), et une tension doctrinale à nommer
(état métier contre cycle de vie de l'enregistrement, qui explique à elle
seule quatre anomalies apparentes).


# 1. État des standards vérifié en ligne (juillet 2026)

Vérifié comme demandé. `sources.md` reste le propriétaire de ces états ; les
lignes ci-dessous sont les mises à jour à y reporter.

**OGC API Connected Systems.** L'état de `sources.md` est confirmé : Parts 1
et 2 approuvées comme standards OGC (approbation 2 juin 2025, publication
v1.0 le 22 juillet 2025). Éléments nouveaux depuis la rédaction : une Part 3
(bindings pub/sub, MQTT) existe à l'état de draft, et l'OGC a organisé un
code sprint hybride les 27 au 29 janvier 2026 pour soutenir les
implémentations. Le standard est vivant côté implémentation, ce qui renforce
V1 (cible v2 actionnable).

**OGC SensorThings API 2.0.** L'état de `sources.md` est confirmé et reste
exact : l'appel à commentaires publics s'est clos le 18 janvier 2026 ; au
moment de cet audit (juillet 2026), aucune ratification n'est annoncée, le
standard est toujours en intégration des commentaires. STA 1.1 reste la
référence de production. Le choix BDOH de ne pas adopter `resultType`
SWE-Common ni la terminologie Proximate/Ultimate FOI reste justifié.

**STAMPLATE.** Le schéma Zenodo (10.5281/zenodo.17241283, 2025) est confirmé
comme référence citable. Élément nouveau et directement pertinent : l'équipe
STAMPLATE a publié en 2026 un schéma de qualité des séries temporelles fondé
sur le W3C DQV (Data Quality Vocabulary), intégré à son mécanisme JSON-LD, et
qui sérialise déjà des concepts STA 2.0 (ObservingProcedure,
RelatedDatastream, RelationRole) tout en restant rétro-compatible STA 1.1.
Deux conséquences pour BDOH : (a) c'est un modèle éprouvé pour exposer
`qualityFlag` et les métadonnées de validation dans les `properties` STA sans
attendre STA 2.0 ; (b) c'est la stratégie de transition 1.1 vers 2.0 la plus
documentée du domaine, à suivre pour V2. Le SMS Helmholtz a par ailleurs
publié son article de référence (arXiv 2512.17280, décembre 2025).

**eLTER-RI et ENVRI-Hub NEXT.** Le projet ENVRI-Hub NEXT (11 infrastructures
dont eLTER, financement Horizon Europe 101131141) a lancé la version
reconstruite de l'ENVRI-Hub en avril 2026 (webinaire officiel du 23 avril
2026), avec catalogue de services, base de connaissances à recherche
sémantique et AAI unifiée (ENVRI-ID, compatible EOSC). Pour BDOH, le point de
contact reste indirect (via Theia/OZCAR et la convergence DCAT-AP), mais la
plateforme est désormais opérationnelle : V2 passe de la veille passive à un
objet observable concrètement.


# 2. Compléments et pistes sur les points ouverts existants

## C6. `codeType` mal classé : proposition IdentifierScheme

D'accord avec le constat, et la piste "table de référence" est la bonne des
deux, pour une raison que le constat ne mentionne pas : `Identifier` porte
déjà une double vérité douce entre `codeType` et `codeSource`
(`codeType='ror'` implique `codeSource='ROR'` ; les deux colonnes disent
presque la même chose sous deux formes). Une table `IdentifierScheme`
absorbe les deux d'un coup :

```
IdentifierScheme : id, code ("doi", "orcid", "sandre"...), name,
                   authority ("DataCite", "SANDRE"...),
                   uriTemplate 0..1 ("https://doi.org/{code}"),
                   validationPattern 0..1 (regex),
                   archivedAt 0..1
Identifier : scheme 1 -> IdentifierScheme (remplace codeType + codeSource)
```

Avantages sur le Keyword : intégrité par FK native (contrairement au TPC,
rien n'empêche ici une vraie FK), et surtout des colonnes structurées que le
code peut exploiter (résolution d'URI, validation de format à la saisie),
ce qu'un Keyword ne porte pas. Ajouter Handle ou ARK devient un INSERT.
L'index unique partiel du swhid devient un index sur
`(scheme, code) WHERE scheme = <uuid du scheme swhid>` ou, plus lisible, la
contrainte reste applicative comme aujourd'hui. Le critère de la grille
enum/Keyword est respecté dans son esprit : `codeType` ne branchait pas de
résolution polymorphe, il n'avait donc rien d'un discriminant TPC ; il
devient une donnée. Même traitement recommandé pour `Keyword.thesaurus`
(texte libre aujourd'hui) : soit le supprimer (dérivable de `uri`), soit le
normaliser, mais ne pas le laisser en étiquette libre divergente de l'URI.

## M1. Valeurs censurées : censorCode aligné ODM2

Proposition concrète : un champ `censorCode 0..1` sur `AnalysisObservation`,
`ValidatedObservation` et `Transformation`, aligné sur le CV ODM2 CensorCode :

```
censorCode : none | below_detection | below_quantification | above_range
(mapping ODM2 : nc | lt | lt | gt ; SANDRE : codes remarque 1/2/7/10)
```

Il reste enum SQL par la grille ADR-058 : le code branche dessus (les
statistiques sur valeurs censurées exigent un traitement spécial, type
substitution ou Kaplan-Meier ; l'export ODM2/SANDRE mappe dessus), l'ensemble
est fermé, l'ajout est un acte de développement. Point sémantique à écrire
noir sur blanc dans la note : quand `censorCode` est renseigné, `result`
porte la valeur du seuil, pas une mesure ; c'est ce que font ODM2 et SANDRE,
et c'est ce qui évite un `result` null. La censure capteur (saturation,
sous-gamme) est un vrai cas : `above_range` sur `ValidatedObservation` couvre
un limnigraphe saturé en crue. Recommandation : symétrie complète sur les
trois tables de valeurs métier, optionnel partout, absent de `Observation`
(couche brute, on n'y interprète rien).

## M2. Séparer statistique et régularité : l'option zéro champ

La piste du point ouvert propose deux champs. Il existe une option plus
sobre : supprimer `sporadic` de `aggregationStatistic` et faire porter la
régularité par la nullabilité de `observationFrequency` (null = cadence
irrégulière, renseigné = cadence nominale). Une crue échantillonnée à pas
variable devient `instantaneous` + `observationFrequency` null ; une moyenne
sur fenêtres irrégulières devient exprimable (`average` + null), ce qui
était le cas bloquant. Coût : on ne peut plus dire "régulier mais fréquence
inconnue", cas marginal à documenter comme assumé. Si ce cas s'avérait réel
sur les données historiques, retomber sur la piste à deux champs. La
contrainte conditionnelle actuelle ("observationFrequency null si sporadic")
disparaît, remplacée par aucune contrainte : un invariant de moins.

## M3. Provenance point à point : écrire la propriété, ne pas ajouter de lien

Recommandation : la piste 1 seule (écrire que la lignée est au niveau
série/période, pas au point), sans `sourceObservation`. Arguments : la
jointure temporelle couvre le cas séquentiel, qui est l'écrasante majorité ;
le cas parallèle est précisément celui où le validateur exerce un jugement
(consolidation master/save), et ce jugement est déjà tracé au bon grain par
`ValidationBatch` + `comment`/`Memory` ; enfin un lien par point sur une
hypertable de milliards de lignes a un coût réel (une colonne UUID de plus,
voir M5) pour un bénéfice qui n'a pas de demandeur identifié. YAGNI, mais en
écrivant la limite pour qu'elle soit un choix et non un oubli. Si un jour un
observatoire l'exige, l'ajout d'une colonne nullable est une migration
bénigne.

## M4 et la chaîne labo : voir M9 (nouveau constat, regroupe et élargit)

M4 est un symptôme d'une question plus large traitée en M9 ci-dessous : le
modèle offre aujourd'hui deux chemins pour la donnée de laboratoire sans dire
lequel est canonique. Trancher M9 résout M4 par ricochet (si la chimie
n'entre plus par la couche IoT, la contrainte `Datastream.system` obligatoire
cesse d'être un problème labo).

## M5. Clés des hypertables : proposition concrète

Quatre tables de valeurs sont des hypertables de fait : `Observation`,
`ValidatedObservation`, `AnalysisObservation`, `Transformation`
(`ControlObservation` et `TransferFunctionPoint` sont volumétriquement
négligeables et cibles TPC pour la première : elles gardent leur UUID).
Proposition :

- Supprimer la PK UUID des quatre hypertables. Aucune n'est cible TPC ni
  d'aucune FK entrante : leur UUID ne sert ni l'identité citable ni la
  navigation.
- Clé primaire composite naturelle là où l'unicité est aussi une règle
  scientifique : `(timeSeries, phenomenonTimeStart)` sur
  `ValidatedObservation` (une série validée a une valeur par instant, c'est
  un invariant métier autant qu'une clé) et `(transformedTimeSeries,
  phenomenonTimeStart)` sur `Transformation`. La colonne de partition est
  dans la clé : TimescaleDB est satisfait, et l'index unique sert les
  requêtes de lecture dominantes (série + plage temporelle).
- Attention sur `Observation` : le cas parallèle vit au niveau TimeSeries
  (deux Datastreams), pas dans un Datastream ; `(datastream,
  phenomenonTimeStart)` est donc une clé naturelle valide, sauf si un même
  capteur peut émettre deux valeurs au même horodatage (doublons de
  télétransmission) : dans ce cas l'ingestion doit dédupliquer avant insert,
  ce qui est de toute façon souhaitable. À confirmer sur données réelles.
- Attention sur `AnalysisObservation` : les réplicats d'analyse (deux
  aliquotes du même Specimen dosés séparément) peuvent produire deux valeurs
  au même `phenomenonTimeStart` pour la même série. Soit la clé inclut
  `analysisBatch` (`(timeSeries, phenomenonTimeStart, analysisBatch)`), soit
  la règle métier impose une valeur retenue par instant et par série et les
  réplicats passent en `ControlObservation`. À trancher avec les chimistes ;
  la seconde option est plus propre conceptuellement (la série reste un
  contrat "une valeur par instant").

## M6. Thing STA : exposer les trois ancres comme Things

Proposition : `/Things` est peuplé par l'union des trois tables d'ancrage
(Observatory, Site, Station), chacune avec un `properties.bdohType`
discriminant (c'est exactement le style STAMPLATE : le typage fin vit dans
les properties JSON-LD). Le Thing d'un Datastream est son ancre, quelle
qu'elle soit. Avantages : règle unique sans Thing synthétique, aucune entité
nouvelle, les trois objets ont déjà nom, description, Location. Coût : des
Things de granularités hétérogènes dans le même endpoint, ce que STA tolère
explicitement (le guide SOFAIR documente cette latitude d'interprétation).
La règle vit dans la couche d'export, à documenter au même endroit que la
résolution FOI (ADR-038).

## M7. Publisher DataCite du Dataset : autoriser le multi-observatoire

Deux sous-décisions à séparer. (a) Pour `Bundle` : écrire l'invariant "toutes
les séries d'un bundle_series sont ancrées dans l'Observatory du Bundle"
(vérification à l'insert, l'ancre de la série remonte à un Observatory
unique par construction de la hiérarchie). Il est voulu par la structure
actuelle (FK obligatoire), autant le rendre explicite. (b) Pour `Dataset` :
recommandation de ne pas interdire les exports multi-observatoires (les
études comparatives inter-sites sont un cas d'usage réel d'une base
centralisée nationale, c'est même un argument de l'ADR-025). Dérivation :
si toutes les ressources exportées remontent à un Observatory unique, il est
Publisher ; sinon Publisher = l'infrastructure (constante "BDOH / INRAE", à
fixer) et chaque Observatory devient Contributor
(contributorType=hostingInstitution), ce que DataCite 4.6 prévoit
exactement pour ce cas. Le mapping de la section 9 gagne une ligne, pas une
colonne.

## M8. GeoJSON/CRS : stocker PostGIS, réserver geo+json à la sortie

Recommandation alignée sur la piste : le stockage est une géométrie PostGIS
avec SRID (2154 légitime en interne pour les calculs métriques français),
`encodingType='application/geo+json'` décrit le format de sérialisation API,
et l'API reprojette systématiquement en 4326 à la sortie pour être conforme
RFC 7946. Le champ `crs` devient la métadonnée du CRS de stockage et
d'acquisition (ce que le topographe a réellement mesuré), pas une promesse
sur le format d'échange. Trois phrases dans la note de `Location` suffisent.
Sur l'asymétrie FOI : recommandation d'aligner `FeatureOfInterest` sur le
mécanisme commun (FK `location 1 -> Location` remplaçant
`geometry`/`encodingType` inline). L'argument "FOI conceptuelle sans
historique" justifie de ne pas lui donner de `HistoricalLocation`, pas de
dupliquer le mécanisme de géométrie ; en phase de conception l'alignement
est gratuit, et il centralise la question CRS en un seul endroit.

## S2. Double vérité d'ancrage : nommer, puis définir l'inclusion

D'accord avec les deux pistes. Formulation proposée pour la règle
d'inclusion, à porter dans `integrity_checks.md` : soit A(f) l'ancre d'un
flux et A(d) l'ancre du Deployment actif du System qui l'alimente ; la
cohérence exige que A(d) soit égale à A(f) ou descende de A(f) dans la
hiérarchie Observatory > Site > Station (le flux peut être plus général que
l'installation, jamais plus précis). Cas limites couverts : drone (flux
Site, deployment Site : égalité), capteur fixe (flux Station, deployment
Station : égalité), série d'observatoire agrégeant des installations de
plusieurs stations (flux Observatory, deployments Station : inclusion),
et le cas suspect (flux Station, deployment Site) est détecté. Le terme à
employer dans le modèle : dénormalisation contrôlée, arbitrée flux, motivée
par l'export STA autoportant et la requête fréquente "quels flux sur cette
station". La sortir du vocabulaire "propriétaire unique" comme le suggère le
constat.

## S3. Inventaire des invariants : registre numéroté

Proposition de forme : chaque invariant applicatif reçoit un identifiant
stable `INV-xxx` dans `integrity_checks.md` (qui en devient le propriétaire
unique), avec quatre colonnes : énoncé, mécanisme de garde (trigger, check à
l'insert, job périodique), requête de détection, action en cas de violation.
Les notes d'entité du modèle citent l'identifiant au lieu de reformuler la
règle (fin des paraphrases divergentes). Inventaire de départ relevé pendant
cet audit, en plus de ceux déjà cités par S3 :

- existence des cibles TPC (quatre déclinaisons) ;
- inclusion d'ancrage flux/Deployment (S2) et Specimen/Deployment ;
- une seule HistoricalLocation courante (validTo null) par ressource ;
- `phenomenonTimeEnd` obligatoire ou interdit selon `aggregationStatistic` ;
- `Procedure.type` conforme à l'emplacement (procedureObservation de type
  observation, etc.) ;
- contraintes CHECK par `systemType` sur System ;
- `procedureSampling` null si `acquisitionType=sensor_continuous` ;
- `ControlObservation.system` de systemType sensor ;
- complétion minimale KeywordRequirement à la sauvegarde ;
- immuabilité de `Keyword.notation` après création ;
- swhid obligatoire sur Algorithm, unicité du swhid ;
- unicité du `code` par scope, y compris les scopes par ancre
  (index `(anchorType, anchorId, code)`) ;
- non-chevauchement des périodes dans `transferfunctionset_function` au sein
  d'un même TFSet ;
- acyclicité des quatre FK auto-référentes (voir M13) ;
- Deployment racine (sans parentDeployment) doit porter un ancrage
  (voir M13) ;
- imbrication temporelle d'un Deployment enfant dans la période de son
  parent ;
- Bundle mono-observatoire (M7a) ;
- garde d'écrasement d'une TTS référencée par un Dataset (S4).

Ajouter, comme le suggère S3, des tests d'injection : chaque INV-xxx a un
test qui viole la règle et vérifie la détection. C'est le seul moyen de
savoir que l'inventaire est vivant.

## S4. Écrire la propriété, et poser la garde minimale

D'accord avec les deux pistes, avec une recommandation d'aller jusqu'à la
garde : le recalcul d'une TTS référencée par au moins un `Dataset` (via
`dataset_resource`) devrait exiger une confirmation explicite ou déclencher
la proposition de fork. C'est trois lignes d'applicatif (un EXISTS avant
l'écrasement) qui transforment "le curateur doit penser à forker" en "le
système le lui rappelle au seul moment où ça compte". La propriété générale
("BDOH conserve l'état courant, la trajectoire vit sur l'entrepôt externe")
mérite une phrase en tête de la section 8 du modèle, pas seulement dans les
notes. Connexe : voir M14 sur `transferfunctionset_function`.

## V1 et V2 : mise à jour

Voir section 1. V1 gagne un élément (Part 3 pub/sub en draft : la cible v2
inclura potentiellement du streaming temps réel standardisé). V2 gagne deux
éléments concrets : le schéma qualité DQV de STAMPLATE comme modèle
d'exposition de `qualityFlag` en STA 1.1, et l'ENVRI-Hub opérationnel depuis
avril 2026 comme point d'observation de la convergence des vocabulaires.


# 3. Nouveaux constats concrets (C7 à C18)

Locaux, vérifiables, probablement des défauts. Triage en fin de section.

## C7. `Person.orcid` en colonne : double vérité avec Identifier

`Person` porte une colonne `orcid 0..1`, alors que `Identifier` accepte
`codeType='orcid'` avec `resourceType='Person'`, et que la section `code` du
modèle dit elle-même qu'une Person se cite "par un Identifier (ORCID) s'il
existe". Deux emplacements pour le même fait : c'est exactement l'erreur
corrigée sur Algorithm (ADR-052 amendé : doi et swhid retirés des colonnes)
et évitée sur Bundle et Dataset. Piste : supprimer la colonne, l'ORCID passe
par `Identifier`, la note de Person renvoie au critère Identifier/Keyword.
Même logique déjà appliquée partout ailleurs, aucune raison écrite de
l'exception.

## C8. Index de suppression logique divergent des tables

Deux divergences vérifiées entre la section *Suppression logique* et les
tableaux d'entités : `Site` est listé dans les tables à `status` mais son
tableau ne porte que `archivedAt` ; `Bundle` est listé dans les tables à
`archivedAt` mais son tableau ne porte que `status` (draft, published,
archived). L'un des deux se trompe dans chaque cas. Noter que la valeur
`archived` du status de Bundle fait doublon conceptuel avec un éventuel
`archivedAt` : voir S6 pour le fond. Piste : corriger l'index (probablement
Site vers la liste archivedAt, Bundle vers la liste status), et profiter de
la passe pour regénérer l'index depuis les tableaux plutôt que l'inverse.

## C9. `Deployment` cumule status et validFrom/validTo

La règle de la section *Suppression logique* dit "jamais deux mécanismes à
la fois sur la même table", et classe les tables datées comme fermées par
`validTo`. Or `Deployment` porte à la fois `validFrom`/`validTo` (fin du
déploiement) et `status` (active, inactive, removed), listé dans les tables
à status. Les sémantiques se recouvrent : un déploiement terminé a-t-il
validTo non-null, status=removed, ou les deux, et que signifie leur
désaccord ? Piste : soit supprimer `status` (validTo ferme, comme
Responsibility), soit le garder avec une sémantique disjointe écrite
(par exemple status=inactive pour une interruption temporaire sans fin de
déploiement), auquel cas la doctrine "jamais deux" doit être amendée (voir
S6, dont c'est un cas).

## C10. Scope d'unicité de `Deployment.code` incompatible avec son ancrage

Les scopes déclarent "Deployment unique par Station", mais `Deployment` peut
être ancré sur un Site, ou n'avoir aucun ancrage (`anchorType 0..1`, null si
autonome, cas des sous-déploiements sur plateforme). Le scope est indéfini
pour ces deux cas. Piste : "unique par ancre, unique globalement si sans
ancre", ou plus simple : "unique par ancre du déploiement racine de sa
hiérarchie" ; à trancher, puis corriger la table des scopes.

## C11. ADR-013 et ADR-023 sans trace dans le modèle ni statut "remplacée"

`variableType` (ADR-013, intensive/extensive) et `samplingPeriodStart/End/
Mode` (ADR-023) n'existent nulle part dans le modèle v12 (vérifié par
recherche exhaustive), et aucune entrée de la section *Décisions remplacées*
ne les couvre. Soit ces champs ont été retirés délibérément (alors il manque
la décision qui remplace, même en une ligne), soit ils ont été perdus dans
une refonte (alors il faut décider s'ils reviennent : `variableType` guide
les calculs de delta, la question de fond reste posée). Le point n'est pas
le champ, c'est la gouvernance : un ADR vivant dont la décision n'est plus
dans le modèle est une divergence entre les deux fichiers propriétaires.

## C12. `Memory.mediaUrl` en cardinalité 0..* dans un tableau de colonnes

La convention de lecture dit que les tableaux ne contiennent que des colonnes
réelles, et les relations 0..* n'y figurent jamais. `mediaUrl 0..*` viole la
règle : soit c'est un tableau PostgreSQL (TEXT[] ou JSONB) et il faut
l'écrire (cardinalité 0..1, type array documenté), soit c'est une table
fille `MemoryMedia` à créer. Le type array est probablement suffisant
(les URLs ne sont référencées par rien), mais il faut le dire.

## C13. Colonnes en TitleCase contre la convention camelCase

`Station.Site`, `Site.Observatory`, `Bundle.Observatory` sont écrites avec
majuscule initiale dans les tableaux, contre la convention camelCase des
colonnes. Correction cosmétique (`site`, `observatory`), à faire avant que
le SQL ne soit généré depuis ces tableaux.

## C14. Trois tables de jointure sans tableau de colonnes

`transferfunctionset_function`, `bundle_series` et `dataset_resource` ont
leur tableau ; `person_organization`, `specimen_deployment` et
`transformationbatch_inputseries` n'en ont pas (elles ne sont décrites que
par mention). Le modèle étant la source de vérité de la structure, leurs
colonnes exactes n'existent nulle part. À documenter au même format, ce qui
forcera au passage la question M11 (temporalité de person_organization).

## C15. Vocabulaire `status` hétérogène dans la famille Batch

Les batchs revendiquent "même famille, même pattern", mais leurs status
divergent sans raison écrite : `pending|done|failed` (ObservationBatch,
TransformationBatch, TransferFunctionBatch), `pending|validated|rejected`
(ValidationBatch), `active|archived` (AnalysisBatch). Le cas AnalysisBatch
est le plus étrange : son status est un mécanisme d'archivage, pas un état
d'exécution, alors que ses frères portent un état d'exécution. Piste :
harmoniser sur `pending|done|failed` partout où le batch est un acte qui
s'exécute, et traiter l'archivage par le mécanisme de suppression logique
prévu pour la table (ce qui rejoint S6 : deux axes distincts).

## C16. Notes "code unique par Station" contre scope "unique par ancre"

Les notes de `TimeSeries` et `TransformedTimeSeries` disent "code unique par
Station" alors que la table des scopes dit "unique par ancre (Observatory,
Site ou Station)". La table des scopes fait foi ; corriger les deux notes.

## C17. Index "Utilisé par" et "Relations inverses" divergents des domaines

Instances relevées, à verser dans l'audit des grilles TPC déjà prévu
(résidu de S1) : le champ `resourceType` de `Responsibility` inclut
TransferFunctionSet et Algorithm, absents de son "Utilisé par" ; celui
d'`Identifier` inclut TransformedTimeSeries, Procedure, FeatureOfInterest,
TransferFunction, TransferFunctionSet, Datastream et Algorithm, absents de
son "Utilisé par" ; le domaine de référence TPC resource inclut `Memory`
comme cible (une note sur une note) mais le `resourceType` de Memory ne
l'inclut pas, sans justification écrite. Aucun de ces écarts n'est
nécessairement une erreur (les sous-ensembles sont légitimes), mais chacun
doit être soit aligné soit justifié, sinon l'audit des grilles ne pourra
jamais conclure.

## C18. Obligation de l'agent variable selon les batchs, sans règle

`agentType/agentId` sont obligatoires (1) sur ValidationBatch et
AnalysisBatch, optionnels (0..1) sur ObservationBatch, TransferFunctionBatch,
Specimen et Memory. Une activité PROV sans agent est une provenance faible ;
si l'optionnalité couvre un vrai cas (import legacy dont l'auteur est
inconnu ?), l'écrire ; sinon harmoniser sur obligatoire. Constat de
cohérence, pas de structure.


# 4. Nouveaux points de modélisation (M9 à M14)

## M9. Chaîne laboratoire : deux chemins, aucun canonique (regroupe M4)

Le constat central de cet audit. Depuis ADR-059, une valeur de chimie peut
emprunter deux chemins :

1. Chemin IoT : `Datastream` (acquisitionType=lab_sample, system obligatoire)
   vers `Observation` (qui porte `specimen 0..1`) vers validation vers
   `ValidatedObservation` (qui porte aussi `specimen 0..1`).
2. Chemin labo : `Specimen` vers `AnalysisBatch` vers `AnalysisObservation`,
   rattachée directement à la TimeSeries, sans passer par la couche IoT.

Rien n'écrit lequel est canonique ni quand utiliser l'un ou l'autre, et les
frictions s'accumulent aux coutures :

- `Observation.specimen` et `ValidatedObservation.specimen` sont des vestiges
  probables d'avant ADR-059 : si le chemin labo est le chemin 2, ces colonnes
  n'ont plus de cas d'usage, et si c'est le chemin 1, alors
  `AnalysisObservation` fait doublon.
- `AnalysisObservation` n'a aucun lien vers `ValidationBatch`, alors que
  `TimeSeries.procedureValidation` est obligatoire (1) pour toute série,
  lab_sample compris : le workflow de validation ne peut pas atteindre la
  branche labo. Soit `validationBatch 0..1` s'ajoute à AnalysisObservation,
  soit la note écrit que la validation labo est portée par le qualityFlag
  posé pendant l'AnalysisBatch, et `procedureValidation` devient
  conditionnel.
- `TimeSeries.procedureObservation` (type=observation) est obligatoire même
  pour une série lab_sample, dont le protocole de mesure réel est la
  Procedure de type analysis sur AnalysisBatch. Que met-on dans
  procedureObservation pour une série de nitrates dosés en labo ?
- M4 (Datastream.system obligatoire, System placeholder pour l'analyseur)
  ne se pose que sur le chemin 1.

Piste recommandée : déclarer le chemin 2 canonique pour tout ce qui vient
d'un Specimen (la donnée labo n'a pas de couche brute IoT, son "brut" est le
rapport d'analyse, tracé par AnalysisBatch) ; supprimer `specimen` de
`Observation` et `ValidatedObservation` ; statuer sur la validation de la
branche labo (l'option validationBatch 0..1 sur AnalysisObservation préserve
la symétrie de la famille) ; rendre `procedureObservation` conditionnel sur
TimeSeries (obligatoire si sensor_continuous, null si lab_sample, le
protocole analytique vivant sur AnalysisBatch). Vérifier auprès des
gestionnaires qu'aucun flux labo réel n'arrive aujourd'hui en pseudo-continu
qui justifierait le chemin 1 (préleveur automatique couplé à un analyseur en
ligne : cas réel, mais c'est alors un capteur au sens plein, chemin 1
légitime avec un vrai System).

## M10. `ControlObservation` : ni corrigeable ni supprimable

`ControlObservation` est exemptée de tout mécanisme de suppression logique
(constat scientifique figé) mais elle est cible du pattern TPC resource
(KeywordAssignment) et du TPC series (bundle_series, dataset_resource), donc
protégée par `prevent_physical_delete`. Une ligne saisie par erreur (doublon,
mauvaise série) est immortelle. Le `qualityFlag=bad` qualifie une mesure de
contrôle douteuse, pas une erreur de saisie. Piste : soit assumer et écrire
que l'erreur de saisie se corrige par `qualityFlag=bad` + `qualityComment`
(en acceptant la confusion des deux sens), soit lui donner un `status`
minimal (active, retracted) qui préserve l'esprit "constat figé" tout en
permettant la rétractation, geste connu de l'édition scientifique.

## M11. `person_organization` sans temporalité

ODM2 Affiliations, cité comme source de la temporalité de Responsibility,
porte des périodes sur l'affiliation elle-même. `person_organization` n'a ni
validFrom/validTo ni tableau de colonnes (voir C14). Sur un horizon de 50
ans, "qui était à INRAE quand cette donnée a été produite" est une question
d'attribution réelle. Piste : ajouter validFrom/validTo, ce qui en fait une
association datée au sens du modèle ; sa suppression physique (aujourd'hui
permise en tant que jointure) devrait alors être remplacée par la fermeture
via validTo, comme les autres tables datées.

## M12. `Person.email` obligatoire : intenable pour les personnes historiques

Des séries remontant aux années 1960 impliquent des opérateurs et auteurs
sans adresse électronique connue, voire décédés. Un champ obligatoire force
des valeurs bidon. Piste : passer à 0..1. Trivial mais à faire avant le gel.

## M13. Acyclicité et ancrage racine : invariants manquants sur les récursifs

Quatre FK auto-référentes n'ont aucune garde écrite contre les cycles :
`Deployment.parentDeployment`, `Project.parent`, `Specimen.derivedFrom`,
`Algorithm.supersededBy`. Un cycle rend les remontées récursives (ancrage
d'un déploiement, chaîne de versions d'un algorithme) non terminantes.
S'ajoutent deux règles propres à Deployment : un Deployment racine (sans
parent) doit porter un ancrage (sinon la hiérarchie flotte sans lieu), et la
période d'un Deployment enfant devrait être incluse dans celle de son parent
(un capteur ne peut pas être déployé sur une bouée avant que la bouée le
soit). À verser au registre INV-xxx (S3).

## M14. `transferfunctionset_function` supprimable, mais porteuse d'histoire

En tant que table de jointure, ses lignes sont physiquement supprimables. Or
elles encodent quelle courbe s'appliquait quand dans un TFSet, information
que les TransformationBatch passés référencent implicitement (le batch pointe
le TFSet et une période ; le sens de ce pointeur dépend de l'état de la
jointure au moment du calcul). Supprimer ou modifier une ligne réécrit
silencieusement le sens d'un calcul passé. Les valeurs produites restent
justes (stockées), mais le journal de méthode (ADR-054) devient mensonger.
Piste : traiter cette jointure comme une association datée à part entière
(fermeture par validTo, pas de suppression physique), exception écrite à
l'exemption des jointures. Cohérent avec l'esprit de S4.


# 5. Nouveau risque structurel (S6)

## S6. État métier et cycle de vie de l'enregistrement : deux axes confondus

Quatre anomalies de cet audit (C8, C9, C15, et le cas Property déjà signalé
en creux par la parenthèse de la section *Suppression logique*) ont la même
racine : la doctrine actuelle traite `status` comme un mécanisme unique
alors qu'il porte, selon les tables, deux choses différentes :

- un **état métier**, fait scientifique ou éditorial sur l'objet : Property
  proposed/accepted/deprecated, Project planned/active/completed, Observatory
  active/discontinued, Bundle draft/published, System active/retired ;
- un **cycle de vie de l'enregistrement**, fait administratif sur la ligne :
  cette ligne est-elle encore une donnée vivante de la base, ou une erreur de
  saisie, un doublon, un objet retiré de la circulation.

La règle "un seul mécanisme par table" est juste quand status porte le
second sens. Elle produit des impasses quand status porte le premier : un
Project `completed` est un état métier normal, pas un archivage, et un
Project créé par erreur n'a aucune sortie ; même chose pour une Property
`accepted` saisie en doublon. Les tables où les deux besoins coexistent
finissent par cumuler les deux mécanismes en contrebande (Property annoncée
avec status et archivedAt, Deployment avec status et validTo, Bundle avec un
status qui contient `archived`).

Piste : un ADR court qui pose la distinction et la règle en trois lignes :
(1) toute entité référencée porte un et un seul mécanisme de cycle de vie
(archivedAt, ou validTo pour les datées) ; (2) `status` est réservé aux
états métier et ses valeurs ne doivent plus contenir de valeur d'archivage
(retirer `archived` de Bundle et Dataset, `deprecated` reste métier sur
Property et Algorithm car c'est un fait de curation, pas un retrait) ; (3)
les deux colonnes peuvent coexister sans double vérité puisqu'elles ne
parlent pas du même fait. Cela résout C8, C9 et C15 par le fond plutôt que
cas par cas, au prix d'une passe d'harmonisation sur une dizaine de tables.
L'alternative (conserver la doctrine actuelle et traiter chaque collision
comme une exception documentée) est défendable mais accumulera les notes
d'exception.


# 6. Triage des nouveaux constats

| ID  | Constat                                                          | Sévérité | Effort |
|-----|------------------------------------------------------------------|----------|--------|
| M9  | Chaîne labo : deux chemins, aucun canonique                      | élevée   | moyen  |
| S6  | État métier et cycle de vie confondus dans status                | élevée   | moyen  |
| C7  | Person.orcid double vérité avec Identifier                       | moyenne  | faible |
| C8  | Index suppression logique divergent des tables (Site, Bundle)    | moyenne  | faible |
| C9  | Deployment cumule status et validFrom/validTo                    | moyenne  | faible |
| C10 | Scope du code Deployment incompatible avec anchorType Site/null  | moyenne  | faible |
| C11 | ADR-013 / ADR-023 sans trace ni statut remplacée                 | moyenne  | faible |
| M10 | ControlObservation ni corrigeable ni supprimable                 | moyenne  | faible |
| M11 | person_organization sans temporalité                             | moyenne  | faible |
| M13 | Acyclicité et ancrage racine des FK récursives non spécifiés     | moyenne  | faible |
| M14 | transferfunctionset_function supprimable malgré les batchs passés | faible  | faible |
| C12 | Memory.mediaUrl en 0..* dans un tableau de colonnes              | faible   | faible |
| C13 | Colonnes TitleCase (Site, Observatory) contre camelCase          | faible   | faible |
| C14 | Trois tables de jointure sans tableau de colonnes                | faible   | faible |
| C15 | Vocabulaire status hétérogène dans la famille Batch              | faible   | faible |
| C16 | Notes "unique par Station" contre scope "unique par ancre"       | faible   | faible |
| C17 | Index Utilisé par divergents des domaines resourceType           | faible   | faible |
| C18 | Obligation de l'agent variable selon les batchs                  | faible   | faible |
| M12 | Person.email obligatoire                                         | faible   | faible |

Ordre suggéré : trancher S6 d'abord (il détermine la correction de C8, C9,
C15 et évite de les corriger deux fois), puis M9 (seule vraie zone floue du
modèle, et elle conditionne M4 et une partie de M5), puis la rafale des C à
effort faible en une seule passe d'édition, puis M5/M1/M2 déjà au triage.


# 7. Ce que cet audit ne remet pas en cause

Pour mémoire, et parce que la consigne du projet est de challenger sans
rouvrir sans raison : les invariants 1 à 9 de CLAUDE.md sortent renforcés de
cette lecture. En particulier, la vérification en ligne confirme que le pari
System + Deployment récursif (ADR-037) est aligné sur un standard désormais
publié et implémenté (CS API v1.0), que le refus des concepts STA 2.0
instables (ADR-011, ADR-017) reste le choix des implémentations de référence,
et que la stratégie Keyword/uri vers les thésaurus externes est exactement
celle que l'écosystème européen (STAMPLATE, ENVRI-Hub) est en train de
généraliser. Aucun constat de ce rapport ne touche à la structure des deux
couches, au contrat analytique, ni au pattern TPC lui-même : tout se joue
dans les coutures et la doctrine, au bon moment pour le faire.
