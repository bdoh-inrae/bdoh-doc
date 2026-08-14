---
titre: Chantier BDOH
sous-titre: Ce qui reste ouvert, à trancher ou à corriger
mis_a_jour: 2026-08-14
---

# Comment lire ce fichier

Ce fichier possède **tout ce qui reste à faire** sur le modèle et sur l'espace
de travail. Il n'y a qu'un seul endroit à consulter pour savoir où on en est.

Il ne possède aucune vérité de structure (elle vit dans
`modele/modele_donnees.md`), aucun pourquoi déjà décidé (dans
`modele/decisions.md`), aucun état de standard (dans `modele/sources.md`).
`CLAUDE.md` est le routeur qui renvoie ici.

Chaque constat porte un identifiant stable, dont la lettre dit sa nature et
comment il se résout :

| Lettre | Nature                                      | Se résout par                      |
|--------|---------------------------------------------|------------------------------------|
| `C`    | constat concret et vérifiable sur le modèle | décision de fond, puis ADR         |
| `M`    | point de modélisation à clarifier           | décision de fond, puis ADR         |
| `S`    | risque structurel, coût assumé à nommer     | décision de fond, puis ADR         |
| `D`    | divergence documentaire                     | édition, sans décision de fond     |
| `V`    | veille standards                            | mise à jour de `modele/sources.md` |
| `T`    | travaux d'exécution                         | exécution                          |

La frontière qui compte est entre `D` et le reste. Un `D` est un endroit où le
modèle **dit déjà** ce qu'il veut dire, mais le dit mal, deux fois, ou plus du
tout : il se corrige sans rien décider. Tout le reste demande un arbitrage.
Un constat qui, en l'instruisant, change de nature change de lettre, avec une
ligne dans le journal pour dire pourquoi.

Les renvois au modèle se font par nom d'entité ou de section, jamais par numéro
de ligne : les numéros bougent, les noms non.

Convention de rédaction héritée du projet : pas de tiret cadratin ni
demi-cadratin. Deux-points, parenthèses, reformulation.

**Note de solde.** Les constats résolus ne sont pas supprimés : ils descendent
en fin de fichier, section *Constats soldés*, avec leur texte de résolution
intégral. Ils sont hors du fil de lecture mais restent citables, et surtout ils
évitent qu'une question tranchée soit rouverte par oubli. Même principe que la
section *Décisions remplacées* de `modele/decisions.md`.


# Triage

Sévérité : `élevée` (à traiter avant gel du schéma, ou risque de publication
fausse), `moyenne` (le modèle se contredit ou un cas réel n'est pas couvert),
`faible` (cosmétique ou confort). Effort : `faible` (édition ponctuelle),
`moyen` (refonte locale ou décision de fond), `élevé` (changement structurel ou
passe complète).

| ID  | Constat                                                                   | Sévérité | Effort |
|-----|---------------------------------------------------------------------------|----------|--------|
| C19 | Passage obligatoire par `Deployment` : jamais décidé, diverge de CS API   | moyenne  | moyen  |
| M9  | Données d'expérience de terrain : valeur issue d'un fit sur série courte  | élevée   | moyen  |
| T3  | La documentation publique décrit un modèle disparu                        | élevée   | élevé  |
| T1  | Dix-huit constats d'audit jamais relus                                    | moyenne  | moyen  |
| S3  | Invariants applicatifs cumulés : inventaire à tenir                       | moyenne  | moyen  |
| S4  | Historique des valeurs : propriété à écrire, pas à corriger               | moyenne  | faible |
| D9  | La version de DataCite est figée dans le modèle, et périmée               | moyenne  | faible |
| V3  | sources.md pointe les brouillons de CS API, désormais standards           | moyenne  | faible |
| S2  | Ancrage et lien au matériel : à confirmer soldé, ses cinq parties le sont | faible   | faible |
| D5  | Deux tables de jointure citées sans tableau de colonnes                   | faible   | faible |
| V1  | OGC API Connected Systems comme cible v2                                  | veille   | -      |
| V2  | Alignement STAMPLATE et écosystème européen                               | veille   | -      |
| V4  | Extension STA WebSub 1.0 absente de sources.md                            | faible   | faible |
| V5  | I-ADOPT absent de sources.md alors qu'il vise Property                    | faible   | moyen  |
| V6  | DataCite n'a pas d'entrée d'état daté dans sources.md                     | faible   | faible |
| T4  | Modèle d'endpoints API à construire par-dessus le modèle de données       | -        | élevé  |

Ordre suggéré : les `D*` d'abord, ils sont bon marché et le modèle ment tant
qu'ils tiennent. Puis `T2` (formatage), puis `T1` (relecture de l'audit, qui
peut faire naître de nouveaux `C*` et `M*`). `M9` est le seul sujet de fond
ouvert et mérite une session dédiée.


# Forces, état de référence à ne pas casser par mégarde

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

# C. Constats concrets

## C19. Le passage obligatoire par `Deployment` n'a jamais été décidé, et diverge de CS API

Dans BDOH, tout lien depuis une donnée vers du matériel passe par un
`Deployment` : `Datastream.deployment` est obligatoire, `ControlObservation` et
`AnalysisBatch` suivent le même chemin. Un objet d'instrumentation n'est jamais
référencé nu.

C'est une régularité réelle du modèle, mais elle n'est écrite dans aucun ADR.
Elle est apparue par accumulation, décision locale après décision locale
(ADR-037 puis ADR-062), sans que la règle générale soit énoncée ni son coût pesé.

Vérification faite le 14 août 2026 sur la spécification : **ce n'est pas ce que
fait OGC API Connected Systems**, contrairement à ce qu'on pourrait croire du
fait que la récursivité de `Deployment` en vient. Dans CS API, `System` est une
ressource de plein droit avec son propre endpoint, la hiérarchie normative est
System vers DataStream vers Observation, et `Deployment` n'est qu'un contexte
spatio-temporel optionnel.

| Question                     | CS API 1.0           | BDOH                                      |
|------------------------------|----------------------|-------------------------------------------|
| Le flux est rattaché à       | `System`             | `Deployment`                              |
| Le déploiement est           | optionnel, contexte  | obligatoire sur `Datastream`              |
| Un objet est adressable seul | oui, endpoint propre | oui comme entité, non comme cible de flux |

Ce que BDOH y gagne : un flux sait toujours où et quand il a été produit, sans
remontée de chaîne, ce qui est cohérent avec ADR-063 sur l'ancre comme propriété
d'identité. Ce que ça coûte : la question « quels flux ce capteur a-t-il
produits » demande de passer par les déploiements, et un export CS API devra
reconstituer le lien direct flux vers System.

**À instruire** : le choix est probablement bon, mais il doit être énoncé et
tranché explicitement, avec son coût d'export, plutôt que rester une régularité
implicite. Sujet lié à V1 (CS API comme cible v2).

# M. Points de modélisation à clarifier

## M9. Données d'expérience de terrain : une valeur issue d'un fit sur une série courte

**Statut : ouvert, diagnostic posé, forme du chaînon à trancher. Sévérité moyenne
(cas réel non couvert, aujourd'hui traité dans Excel hors traçabilité), effort
moyen (un patron existant à décliner, pas une refonte).**

### Le cas
Certaines grandeurs d'observatoire ne sont ni des mesures de capteur en continu
ni des analyses d'échantillon : elles résultent d'un calcul sur une série courte
de points mesurés pendant une expérience de terrain. Exemple type : la
perméabilité du sol par essai piézométrique (slug test). On perturbe le niveau,
un piézo enregistre la décrue pendant quelques minutes, on ajuste une loi
(exponentielle décroissante) sur ces points, et le paramètre du fit (la
perméabilité) est la valeur qu'on veut dans une série. Chaque expérience produit
UN point ; la série de perméabilité en accumule au fil des campagnes.
Aujourd'hui ce calcul est fait à la main (tableur), sans traçabilité : ni les
points bruts, ni la loi, ni l'expérimentateur ne sont conservés nulle part.

### Le diagnostic : provenance par série contre provenance par point
La distinction structurelle qui tranche, implicite dans le modèle mais jamais
énoncée avant cette réflexion :
- Une **TransformedTimeSeries** a une provenance PAR SÉRIE : le
  TransformationBatch dérive la série entière d'autres séries identifiées. Son
  contrat est « je suis dérivée de ces séries par cette procédure ».
- Une **TimeSeries lab_sample** a une provenance PAR POINT : chaque valeur a sa
  propre chaîne d'actes (Specimen, AnalysisBatch, AnalysisObservation),
  indépendante du point voisin. La série n'est dérivée de rien : elle accumule
  des résultats d'actes distincts.

La perméabilité a une provenance par point (douze expériences par an, chacune
avec son propre mini-flux et son propre fit). C'est donc structurellement une
donnée de type chimie, pas une donnée de transformation.

### Piste écartée : le trou Datastream vers TTS (à ne pas rouvrir)
Une première réflexion avait envisagé d'autoriser un Datastream comme entrée de
transformationbatch_inputseries, pour produire la série de perméabilité comme
une TTS. Écarté après examen : une TTS alimentée point par point par des batchs
successifs pointant chacun vers un Datastream d'entrée différent n'a plus de
contrat de dérivation lisible (l'inventaire de ses sources devient hétérogène et
croissant). Ce serait forcer une provenance par point dans un mécanisme de
provenance par série. Percerait en outre un second pont IoT vers métier à côté
de TimeSeriesSource, pour un gain nul une fois le bon patron identifié.
L'argument « la perméabilité est dérivée, donc TTS » ne tient pas non plus : une
concentration ICP-MS est tout autant le produit d'une chaîne de calcul interne,
et vit en TimeSeries. Le critère TS contre TTS n'est pas brut contre calculé,
c'est : dérivée d'autres séries métier (TTS) contre alimentée par des actes (TS).

### Direction envisagée : décliner le patron chimie
Parallèle terme à terme avec la chaîne d'échantillonnage :

| Chimie                           | Expérience de terrain                    |
|----------------------------------|------------------------------------------|
| SamplingBatch (prélèvement)      | l'acte expérimental (manip piézo)        |
| Specimen (support physique)      | mini-Datastream (points bruts de décrue) |
| AnalysisBatch (mesure, appareil) | le fit (Algorithm, loi d'ajustement)     |
| AnalysisObservation (valeur)     | la valeur de perméabilité                |
| TimeSeries lab_sample            | TimeSeries de perméabilité               |

Éléments déjà en place, aucun changement requis :
- Le mini-Datastream (série courte de plein droit, points bruts conservés :
  sans eux la valeur fittée est invérifiable, contraire à la mission de
  reproductibilité). Ses Observations arrivent par un ObservationBatch qui porte
  déjà l'expérimentateur (agentType=Person) et la date.
- L'Algorithm pour la loi de fit (swhid, reproductibilité, exécutable par un
  runner BDOH ou une app terrain : remplace le tableur artisanal).

Ce qui manque, le chaînon de provenance par point :
1. Un troisième type d'acquisition sur TimeSeries, à côté de sensor_continuous
   et lab_sample (nom candidat : field_experiment), pour la série qui accumule
   les valeurs d'expériences.
2. L'acte qui relie chaque valeur à son expérience : l'équivalent
   d'AnalysisBatch, prenant un Datastream (les points bruts) là où AnalysisBatch
   prend un Specimen, portant l'Algorithm du fit, le deployment de l'instrument,
   l'agent, la date, et produisant la valeur versée dans la série. Deux formes
   possibles, à trancher :
   - un nouvel objet frère (ExperimentBatch), symétrique d'AnalysisBatch,
     cohérent avec « chaque acte est un batch » (ADR-064) ;
   - un élargissement d'AnalysisBatch (entrée Specimen OU Datastream), écarté
     a priori : tord la sémantique de labo d'un objet existant, travers déjà
     rencontré et refusé ailleurs.

### Questions à instruire à la reprise
- La forme du chaînon (ExperimentBatch dédié, forme pressentie) et l'objet
  valeur produit : réutiliser AnalysisObservation ou créer un équivalent ?
  Inventorier ce qu'AnalysisObservation porte (LOD, LOQ, qualityFlag...) et ce
  qui a un sens pour un paramètre fitté (incertitude du fit, R², résidus ?
  parallèle possible avec CalibrationParameter et TransferFunctionParameter,
  qui portent déjà des lois d'incertitude).
- Le mini-Datastream expérimental : Datastream ordinaire (rien à changer) ou
  besoin d'un marqueur (son deployment et sa courte durée suffisent-ils à le
  distinguer d'un flux pérenne ?).
- L'ancrage de la série d'expériences : par point (chaque expérience a son
  lieu) ou par série (une série par station, comme lab_sample) ? Le patron
  chimie suggère par série, avec le lieu fin porté par l'acte.
- Lien avec la calibration : une calibration est aussi un fit sur une série
  courte contre étalon (même motif « points + loi = paramètres »). Une fois
  ExperimentBatch conçu, vérifier si CalibrationBatch devrait stocker ses
  points bruts de la même façon (aujourd'hui il ne garde que les paramètres),
  sans forcer l'unification si les besoins divergent.

# S. Risques structurels

Choix de fond, souvent délibérés. Le but est de nommer le coût accepté et de
combler ce qui n'est pas spécifié, pas d'annuler.

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

### C. Ancrage de TimeSeries et TransformedTimeSeries (clos, gravé ADR-063)
Tranché et gravé. L'ancre est une propriété d'identité (pas un cache, pas de
champ de mode), fixée à la création : dérivée de l'amont s'il existe, saisie
sinon, et cohérente par construction sur toute la chaîne Datastream vers
TimeSeries vers TimeSeriesSource. Relier des objets d'ancres différentes est
refusé (condition de jonction). Une TimeSeriesSource ne coud que des flux de
la même ancre, une TransformedTimeSeries n'agrège que des entrées de
la même ancre : pas d'agrégation multi-stations (non-besoin BDOH confirmé).
Lecture directe de anchorId, jamais de remontée de chaîne. L'idée d'un champ
`anchorMode` est explicitement abandonnée (après création, un seul régime figé).
Le comportement « sticky » est absorbé par ce cadrage : l'ancre ne change jamais
sauf correction d'erreur. Invariants applicatifs (garde de cohérence à la
jonction, propagation d'une correction) portés dans S3. Voir ADR-063 et la
section Pattern TPC anchor du modèle.

### D. Articulation préparation/mesure au labo (clos, gravé ADR-064)
Tranché et gravé. La chaîne de laboratoire est complète et alignée ODM2 :
SamplingBatch (prélèvement), PreparationBatch (préparation : filtration, broyage,
dilution, produisant un Specimen enfant via l'Actuator ou le Sampler pointé par
son deployment), AnalysisBatch (mesure). Le FK derivedFrom est remplacé par la
jointure specimen_parents rattachée au PreparationBatch (filiation, y compris
composite). CalibrationBatch historise les calibrations. Facility ancre les
instruments de labo. Voir ADR-064.

Reste secondaire, non gravé : l'application effective des corrections de
calibration aux données brutes, qui serait une transformation entre Datastream
et TimeSeries (pas au niveau TransformedTimeSeries). À modéliser si le besoin de
rejouer les corrections dans BDOH se confirme.

### E. Machine / Service / Algorithm (clos, gravé ADR-065)
Tranché et gravé. Trois rôles séparés : Algorithm (code intriqué, reproductibilité),
Service (agent logiciel responsable, documentaire, prov:SoftwareAgent), Machine
(hardware d'exécution, documentaire, jamais agent). agentType devient Person,
Service, Organization ; Machine en sort. Le hardware automatique (préleveur,
capteur) est un outil, pas un agent. Voir ADR-065.

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
**Piste :** tenir un inventaire unique et exhaustif des invariants applicatifs,
avec pour chacun déclencheur, requête de détection, action, fréquence. Ajouter
des tests qui injectent des violations et vérifient leur détection.

Invariants déjà identifiés à porter (liste vivante, non exhaustive) :
- Suppression physique interdite sur toute entité référencée (prevent_physical_delete).
- Intégrité de chaque lien TPC (resourceType/Id, anchorType/Id, agentType/Id,
  seriesType/Id, systemType/Id) : la cible existe et est du bon type.
- Cohérence d'ancre sur la chaîne Datastream vers TimeSeries vers
  TimeSeriesSource (ADR-063) : à l'ajout d'une
  TimeSeriesSource, le Datastream cousu a la même ancre que la TimeSeries ; à la
  création d'une TTS, ses TimeSeries d'entrée partagent une ancre. Jonction
  refusée sinon.
- Propagation d'une correction d'ancre (ADR-063) : une correction d'ancre sur un
  objet amont, acte explicite et rare, doit se répercuter sur les ancres figées
  des objets en aval. Pas de synchronisation permanente : ne se déclenche qu'à la
  correction.
- Ordre d'écriture : un Datastream est créé et ancré avant d'être cousu à une
  TimeSeries via TimeSeriesSource (l'invariant de cohérence lit son ancre figée).
- Sur un Deployment en cascade, seul le Deployment racine porte anchorType/anchorId ;
  les enfants les laissent vides et héritent par remontée de parentDeployment.

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

# D. Divergences documentaires

Des endroits où le modèle, ou un fichier qui le cite, se contredit lui-même.
Aucune ne demande de décision de fond : la bonne réponse est déjà quelque part
dans le projet, elle n'est simplement pas partout.

Les divergences D1 à D8 sont détectées automatiquement par
`outils/verifie_modele.py`. Le critère de clôture de cette section est que
l'outil sorte zéro.

## D5. `person_organization` citée sans tableau de colonnes

`person_organization` est nommée dans l'index des jointures, dans les *Utilisé
par* de `Person` et d'`Organization`, et dans la section *Relations inverses et
API*, mais n'a ni section ni tableau de colonnes. Un lecteur ne peut pas savoir
si elle porte des dates, un rôle, ou seulement deux clés.

`transformationbatch_inputseries`, qui souffrait du même manque, a été écrite le
14 août 2026 : ses colonnes se déduisaient sans rien décider.

`person_organization`, non. Lui donner des colonnes revient à trancher si
l'affiliation est datée, ce qui est **M11** de l'audit archivé, jamais relu.
L'écrire dans une passe censée ne rien décider serait trancher en douce. Louis
penche pour la datation, qui permettrait de conserver des personnes clairement
définies avec des affiliations clairement valides dans le temps ; c'est un
argument de fond, à instruire comme tel.

**Bloqué par M11.** Se referme avec lui, pas avant.

## D9. La version de DataCite est figée dans le modèle, et périmée

`modele/modele_donnees.md` écrit "Correspondance entre les propriétés DataCite 4.6
et les entités BDOH" et pointe six fois la documentation de la version 4.6.
`sources.md` est le propriétaire déclaré de l'état daté des standards, mais il
n'a pas d'entrée DataCite : la version vit donc uniquement dans le modèle, à
l'endroit où la règle de propriété dit qu'elle ne devrait pas être.

Vérification en ligne du 14 août 2026 : DataCite Metadata Schema **4.7** est
publié depuis le 3 mars 2026 (nouveaux types de ressource, nouveaux types
d'identifiants liés, nouveau type de relation). Le mapping BDOH lui-même n'est
pas invalidé, les propriétés utilisées sont stables ; c'est le numéro de version
qui est faux.

C'est l'illustration exacte du risque que la règle de propriété unique cherche à
éviter, et le premier cas mesuré où elle n'a pas été appliquée.

# V. Veille standards

Questions d'évolution, pas de défauts. L'état daté des standards vit dans
`modele/sources.md`, propriétaire unique ; seules les questions d'alignement non
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

## V3. `sources.md` pointe les brouillons de CS API, désormais standards

`sources.md` note lui-même que "les URLs de spécification ci-dessus restent en
`/DRAFTS/` au moment de la rédaction". La page OGC liste maintenant les deux
parties d'OGC API Connected Systems en version 1.0 avec le statut IS
(International Standard) : Part 1 Feature Resources (23-001) et Part 2 Dynamic
Data (23-002). Les liens `/DRAFTS/23-001r0.html` et `/DRAFTS/23-002r0.html`
peuvent être remplacés par les URLs canoniques `docs.ogc.org/is/`.

L'état daté écrit dans `sources.md` (approbation le 2 juin 2025, publication le
22 juillet 2025) reste conforme à ce que publie l'OGC. Seuls les liens sont à
mettre à jour, ce qui confirme au passage que la veille de juillet était bien
faite.

## V4. Extension STA WebSub 1.0 absente de `sources.md`

La page OGC liste une extension approuvée que `sources.md` ne mentionne pas :
SensorThings API Extension WebSub Asynchronous Messaging Standard 1.0
(24-032r1), à côté de STAplus 1.0 déjà présent. Elle standardise la notification
asynchrone de nouvelles observations.

Intérêt pour BDOH à évaluer, sans urgence : c'est un sujet d'interface, pas de
modèle de données, donc sans effet sur le schéma. À noter dans `sources.md` pour
que la liste des extensions STA soit complète.

## V5. I-ADOPT absent de `sources.md` alors qu'il vise exactement `Property`

Le framework I-ADOPT (InteroperAble Descriptions of Observable Property
Terminologies) est une recommandation de la Research Data Alliance, finalisée en
janvier 2022 et adoptée par la RDA en avril 2022, dotée d'une ontologie publiée
et maintenue. Il décompose une variable observable en composants
(ObjectOfInterest, Property, Matrix, ContextObject, StatisticalModifier) pour
rendre les descriptions de variables interopérables entre vocabulaires.

C'est le problème que BDOH résout à sa manière avec `Property`, `Unit`,
`aggregationStatistic`, le milieu, et l'alignement NERC P01. NERC P01 est
d'ailleurs l'un des vocabulaires que I-ADOPT prend en exemple, et le NERC
publie des décompositions I-ADOPT de ses termes P01.

L'enjeu n'est pas d'adopter le framework : c'est de vérifier si la décomposition
BDOH s'y projette proprement, ce qui est un bon test de robustesse du découpage
actuel, et de savoir si l'écart est délibéré. Le sujet touche aussi M2 de
`chantier.md` (aggregationStatistic mélangeant cadence et statistique),
clos, dont I-ADOPT donne une lecture indépendante avec son StatisticalModifier.

**Action** : ajouter l'entrée dans `sources.md` avec son état daté, puis ouvrir
un point dans `chantier.md` si la projection révèle un écart de fond. Ne
rien changer au modèle avant cette instruction.

## V6. DataCite n'a pas d'entrée d'état daté dans `sources.md`

Voir CH-13 pour le constat. L'action côté `sources.md` est de lui donner une
entrée propre, avec la version courante (4.7, publiée le 3 mars 2026), pour que
le modèle puisse cesser de la porter.

# T. Travaux

## T1. Verser les constats de l'audit archivé

`archives/audit_modele_v12.md` (631 lignes, juillet 2026) est un audit du modèle
produit sur claude.ai, jamais relu. Il porte les constats C7 à C18, M10 à M14 et
S6, avec leur triage sévérité et effort, et dit lui-même que chacun est destiné à
être versé ici. Le versement n'a jamais été fait.

**Ce que fait T1, et ce qu'il ne fait pas.** T1 est une tâche de rangement, pas
d'instruction. Il verse les constats dans ce fichier avec leur lettre, pour qu'ils
cessent de vivre dans un fichier d'archive que rien ne consulte. Il ne les
tranche pas : chacun sera pris un par un, plus tard, comme n'importe quel autre
constat ouvert.

Un seul filtrage est fait au versement, et il est mécanique : trois constats ont
déjà été traités par la passe d'août 2026 et seraient versés en double.

| Constat de l'audit                               | Devenu | État               |
|--------------------------------------------------|--------|--------------------|
| C13, colonnes en TitleCase                       | D8     | clos le 14/08/2026 |
| C14, tables de jointure sans tableau de colonnes | D5     | partiellement clos |
| C17, index "Utilisé par" divergents des domaines | D7     | clos le 14/08/2026 |

Ces trois-là ont été retrouvés indépendamment en août sans que l'audit de
juillet ait été consulté. La convergence indique qu'il est fiable : raison de
plus pour le verser tel quel plutôt que de le réécrire.

Constats à verser, dans l'ordre du triage de l'audit :
| ID  | Constat                                                                 | Sévérité | Effort |
|-----|-------------------------------------------------------------------------|----------|--------|
| S6  | État métier et cycle de vie de l'enregistrement confondus dans `status` | élevée   | moyen  |
| C7  | `Person.orcid` en colonne : double vérité avec `Identifier`             | moyenne  | faible |
| C8  | Index de suppression logique divergent des tables                       | moyenne  | faible |
| C9  | `Deployment` cumule `status` et `validFrom`/`validTo`                   | moyenne  | faible |
| C10 | Scope d'unicité de `Deployment.code` incompatible avec son ancrage      | moyenne  | faible |
| C11 | ADR-013 et ADR-023 sans trace dans le modèle ni statut "remplacée"      | moyenne  | faible |
| M10 | `ControlObservation` : ni corrigeable ni supprimable                    | moyenne  | faible |
| M11 | `person_organization` sans temporalité                                  | moyenne  | faible |
| M13 | Acyclicité et ancrage racine : invariants manquants sur les récursifs   | moyenne  | faible |
| C12 | `Memory.mediaUrl` en cardinalité 0..* dans un tableau de colonnes       | faible   | faible |
| C13 | Colonnes en TitleCase contre la convention camelCase                    | faible   | faible |
| C14 | Trois tables de jointure sans tableau de colonnes                       | faible   | faible |
| C15 | Vocabulaire `status` hétérogène dans la famille Batch                   | faible   | faible |
| C16 | Notes "code unique par Station" contre scope "unique par ancre"         | faible   | faible |
| C17 | Index "Utilisé par" et "Relations inverses" divergents des domaines     | faible   | faible |
| C18 | Obligation de l'agent variable selon les batchs, sans règle             | faible   | faible |
| M12 | `Person.email` obligatoire : intenable pour les personnes historiques   | faible   | faible |
| M14 | `transferfunctionset_function` supprimable, mais porteuse d'histoire    | faible   | faible |

Trois d'entre eux touchent le fond et non la documentation, et mériteront d'être
pris en premier quand l'instruction commencera : S6 (état métier et cycle de vie
confondus dans `status`), C7 (`Person.orcid` en double vérité avec `Identifier`)
et M11 (`person_organization` sans temporalité, dont dépend D5).

**Action.** Verser les quinze constats restants dans ce fichier, chacun avec son
texte d'origine, sous la lettre que sa nature commande. Puis supprimer
`archives/audit_modele_v12.md` : son contenu vivra ici, et l'archive n'aurait
plus qu'à diverger.

À faire dans cette phase de remise en ordre. L'instruction de chaque constat
vient après, hors de ce plan.
