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
| M9  | Données d'expérience de terrain : valeur issue d'un fit sur série courte  | élevée   | moyen  |
| T3  | La documentation publique décrit un modèle disparu                        | élevée   | élevé  |
| T1  | Dix-huit constats d'audit jamais relus                                    | moyenne  | moyen  |
| S3  | Invariants applicatifs cumulés : inventaire à tenir                       | moyenne  | moyen  |
| S4  | Historique des valeurs : propriété à écrire, pas à corriger               | moyenne  | faible |
| D1  | Patterns transversaux annonce quatre TPC, le modèle en porte cinq         | moyenne  | faible |
| D2  | Facility et SamplingBatch hors des domaines de référence, six tableaux    | moyenne  | faible |
| D3  | L'index anchor cite Specimen, la colonne est sur SamplingBatch            | moyenne  | faible |
| D6  | Memory cite System, entité supprimée par ADR-062                          | moyenne  | faible |
| D7  | Cinq mentions "(FK x)" désignent une colonne qui n'existe pas             | moyenne  | faible |
| D9  | La version de DataCite est figée dans le modèle, et périmée               | moyenne  | faible |
| D11 | La règle d'alignement des tableaux se contredit elle-même                 | moyenne  | faible |
| T2  | Passer tous les tableaux au format arrêté                                 | moyenne  | moyen  |
| V3  | sources.md pointe les brouillons de CS API, désormais standards           | moyenne  | faible |
| S2  | Ancrage et lien au matériel : à confirmer soldé, ses cinq parties le sont | faible   | faible |
| D4  | bundle_series absent de l'index des tables de jointure                    | faible   | faible |
| D5  | Deux tables de jointure citées sans tableau de colonnes                   | faible   | faible |
| D8  | Deux colonnes en TitleCase contre la convention camelCase                 | faible   | faible |
| D10 | La section C3 figurait deux fois, ouverte et close                        | faible   | faible |
| D12 | Trois conventions de tiret coexistent dans le projet                      | faible   | faible |
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

## D1. La section Patterns transversaux annonce quatre déclinaisons TPC, le modèle en porte cinq

La section *Patterns transversaux* écrit "Ce pattern TPC est décliné en quatre
usages" et documente resource, anchor, agent, series. Le TPC **system**
(`systemType` + `systemId`, porté par `Deployment` vers les cinq entités
d'instrumentation) n'a pas de section, pas de domaine de référence déclaré et
pas d'index de tables porteuses.

Il est pourtant listé comme invariant dans `CLAUDE.md` ("un seul pattern TPC,
cinq déclinaisons"), gravé par ADR-062, et utilisé dans la table `Deployment`.
Le lecteur qui découvre le modèle par la section des patterns ne le voit pas.

`methode/notes.md` porte déjà ce constat ("reprendre l'entete pattern transversaux manque
system").

## D2. `Facility` et `SamplingBatch` hors des domaines de référence, dans six tableaux

Trois affirmations du même fichier ne s'accordent pas :

| Endroit                                  | Ce qui est dit                                                      |
|------------------------------------------|---------------------------------------------------------------------|
| Section *Pattern TPC anchor*, domaine    | "Domaine de référence de `anchorType` : Observatory, Site, Station" |
| Section *Pattern TPC anchor*, index      | "Toutes acceptent les trois échelles (Observatory, Site, Station)"  |
| Table `Deployment`, colonne `anchorType` | `Observatory` \| `Site` \| `Station` \| `Facility`                  |

`Facility` vient d'ADR-064 (chaîne d'actes de laboratoire). L'ajout a été fait
dans la table sans remonter au domaine, et la phrase "toutes acceptent les trois
échelles" est devenue fausse.

Le passage à l'outil (`outils/verifie_modele.py`) montre que ce n'est pas un cas
isolé mais un oubli systématique : les deux entités introduites par ADR-064,
`Facility` et `SamplingBatch`, ont été ajoutées comme cibles dans six tableaux
sans jamais remonter aux deux domaines de référence qui les gouvernent.

| Discriminant   | Table portant la valeur hors domaine                           | Valeur ajoutée              |
|----------------|----------------------------------------------------------------|-----------------------------|
| `anchorType`   | `Deployment`                                                   | `Facility`                  |
| `resourceType` | `Responsibility`, `Identifier`, `HistoricalLocation`, `Memory` | `Facility`                  |
| `resourceType` | `KeywordAssignment`                                            | `Facility`, `SamplingBatch` |

La correction est en un seul endroit : ajouter `Facility` aux deux domaines de
référence, `SamplingBatch` à celui de `resourceType`, et refaire la phrase sur
les trois échelles. Aucune table individuelle n'est à toucher, ce sont elles qui
avaient raison. Mais le fait que six tableaux aient dérivé du domaine sans que
rien ne le signale est l'argument le plus net en faveur du contrôle outillé :
c'est exactement le genre d'écart qu'une relecture humaine ne voit pas.

## D3. L'index du pattern anchor cite `Specimen`, la colonne est sur `SamplingBatch`

L'index des tables porteuses de `anchorType` liste `Specimen` et renvoie à
"voir `Specimen.anchorType`". La table `Specimen` ne porte pas cette colonne :
son ancrage passe par `samplingBatch` ou `preparationBatch`. Inversement,
`SamplingBatch` porte bien `anchorType` mais ne figure pas dans l'index.

L'ancre a manifestement été déplacée du Specimen vers le batch lors d'ADR-064,
et l'index n'a pas suivi. Le renvoi "voir X.anchorType" pointe donc vers une
colonne inexistante, alors même que la section affirme que ce champ est "seule
source de vérité".

## D4. `bundle_series` absent de l'index des tables de jointure explicites

`bundle_series` a sa propre section, son tableau de colonnes, et figure dans
l'index du pattern TPC series. Il manque dans le tableau *Tables de jointure
explicites*, qui liste `person_organization`,
`transformationbatch_inputseries`, `specimen_parents`,
`transferfunctionset_function` et `dataset_resource`.

## D5. Deux tables de jointure citées sans tableau de colonnes

`person_organization` et `transformationbatch_inputseries` sont nommées dans
l'index des jointures, dans les *Utilisé par* de plusieurs entités et dans la
section *Relations inverses et API*, mais n'ont ni section ni tableau de
colonnes. Les quatre autres jointures en ont une. Un lecteur ne peut pas savoir
si `person_organization` porte des dates, un rôle, ou seulement deux clés.

Ce constat recoupe C14 de l'audit de juillet (CH-01), qui en comptait trois.

## D6. `Memory` cite `System`, entité supprimée par ADR-062

Le champ *Utilisé par* de `Memory` liste comme cibles possibles "Observatory,
Site, Station, System, TimeSeries, TransformedTimeSeries, Deployment, Project,
TransferFunction". `System` a été éclaté en cinq entités (Sensor, Actuator,
Sampler, Platform, Kit) par ADR-062, et le domaine de référence de
`resourceType` liste bien les cinq. C'est la seule occurrence résiduelle du nom
dans le modèle en dehors des passages qui racontent explicitement l'histoire de
la décision.

## D7. Cinq mentions "(FK nomColonne)" désignent une colonne qui n'existe pas

La section *Notation des champs « Utilisé par »* définit `Entité (FK nomColonne)`
comme "la colonne nomColonne de l'entité citée pointe vers l'entité courante".
Cinq mentions ne vérifient pas cette définition :

| Écrit dans le champ *Utilisé par* de | Mention                        | Réalité de la table citée                                         |
|--------------------------------------|--------------------------------|-------------------------------------------------------------------|
| `Observatory`                        | Site (FK observatory)          | la colonne s'appelle `Observatory`, pas `observatory`             |
| `Site`                               | Station (FK site)              | la colonne s'appelle `Site`, pas `site`                           |
| `Sensor`                             | Datastream (FK sensor)         | `Datastream` n'a pas de colonne `sensor` : il pointe `deployment` |
| `Sensor`                             | ControlObservation (FK sensor) | idem, la colonne est `deployment`                                 |
| `Deployment`                         | Specimen (FK deployment)       | `Specimen` n'a pas de colonne `deployment`                        |

Les deux premières se corrigent avec CH-12 (renommer la colonne suffit). Les
trois autres sont des liens qui n'existent pas sous cette forme : le lien
`Sensor` vers `Datastream` passe par `Deployment` (`systemType='Sensor'`), et
`Specimen` se rattache à un `SamplingBatch`, pas à un `Deployment`. La notation
correcte serait "(via Deployment)".

Le point mérite attention parce que ce champ est le seul index de navigation
inverse du modèle : c'est lui qu'on lit pour savoir qui pointe vers quoi sans
ouvrir toutes les tables. S'il ment, il ment à l'endroit exact où on lui fait
confiance.

## D8. Deux colonnes en TitleCase contre la convention camelCase

`Site.Observatory` et `Station.Site` sont les deux seules colonnes du modèle en
TitleCase. La section *Conventions de nommage* dit "camelCase partout", avec
pour seule exception les suffixes de langue (`label_fr`, `term_en`). Le TitleCase
est réservé aux valeurs de discriminant TPC, où il porte un sens précis : le nom
exact de l'entité ciblée. L'utiliser aussi comme nom de colonne brouille ce
signal.

Ce constat est C13 de l'audit de juillet.

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

## D10. La section C3 figurait deux fois, ouverte et close

Le fichier porte successivement "## C3. Couverture de la suppression logique
incomplète" puis "## C3. Couverture de la suppression logique incomplète
(clos)". La première version décrit le problème ouvert avec sa piste
d'instruction, la seconde le résout entité par entité. Le tableau de triage ne
compte qu'un C3, marqué clos. La version ouverte aurait dû disparaître lors de
la clôture.

## D11. La règle d'alignement des tableaux se contredit elle-même

La règle écrite dit deux choses incompatibles dans la même phrase :

> les barres verticales de chaque colonne sont alignées sur la ligne la plus
> large de cette colonne, les lignes courtes sont paddées d'espaces jusqu'à cette
> largeur. Le contenu ne doit jamais être tronqué ni appauvri pour des raisons de
> largeur : si une ligne dépasse parce que les valeurs possibles sont nombreuses,
> elle dépasse, c'est normal et attendu.

Si on padde jusqu'à la ligne la plus large, aucune ligne ne dépasse jamais : la
notion de dépassement n'a plus de sens. La deuxième moitié de la règle décrit en
réalité une autre politique, tolérer qu'une cellule exceptionnellement longue
sorte de la colonne sans élargir tout le tableau.

Les deux politiques sont défendables et le fichier applique les deux selon les
endroits, ce qui explique les 47 tableaux à dépassement de CH-16. C'est un
arbitrage à trancher, pas un défaut à corriger en silence : la question est
posée dans la synthèse remise avec ce fichier.

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

## T1. Relire l'audit archivé, constat par constat

`archives/audit_modele_v12.md` (631 lignes, juillet 2026) est un audit du modèle
produit sur claude.ai, jamais relu. Il porte les constats C7 à C18, M10 à M14 et
S6, avec leur triage sévérité et effort, et dit lui-même que chacun est destiné
à être versé ici. Le versement n'a jamais été fait : les identifiants de ce
fichier s'arrêtent à C6, M9, S5.

Le travail n'est pas de verser en bloc mais de **relire** : ces constats ont été
écrits sur l'état du modèle en juillet, avant plusieurs corrections. Chacun est à
classer contre le modèle courant.

| Verdict   | Ce qu'on en fait                                                         |
|-----------|--------------------------------------------------------------------------|
| valide    | entre ici avec sa lettre (`C`, `M`, `S` ou `D` selon sa nature réelle)   |
| caduc     | déjà résolu depuis, part directement en *Constats soldés* avec la raison |
| à écarter | ne tient pas à l'examen, part en soldés avec l'argument qui l'écarte     |

Constats à relire, dans l'ordre du triage de l'audit :

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

Trois de ces constats ont été retrouvés indépendamment lors de l'audit d'août
2026, sans que celui de juillet ait été consulté : C13 est devenu D8, C14 est
devenu D5, C17 est devenu D7. Cette convergence indique que l'audit de juillet
est fiable, et qu'il n'y a pas lieu de le refaire, seulement de le relire.

Trois constats à instruire en priorité, parce qu'ils touchent le fond et non la
documentation : S6 (état métier et cycle de vie confondus dans `status`), C7
(`Person.orcid` en double vérité avec `Identifier`) et M11
(`person_organization` sans temporalité).

**Action** : relecture groupée, avec restitution du classement avant intégration.
Puis suppression de `archives/audit_modele_v12.md`, dont le contenu vivant aura
rejoint ce fichier et dont le reste sera soldé.

## T3. Régénérer la documentation publique

`docs/` n'a pas été touché depuis le premier commit du 20 mars 2026, alors que
`dev/` a évolué jusqu'au 20 juillet. Le workflow `.github/workflows/deploy.yml`
publie `docs/` sur GitHub Pages à chaque push sur `main`, sans condition. Le site
en ligne décrit donc un modèle antérieur à la v12, avec des entités qui n'existent
plus :

| Nom publié en ligne    | Réalité v12                                                                      |
|------------------------|----------------------------------------------------------------------------------|
| `TimeSerie`            | renommé `TimeSeries`                                                             |
| `SamplingFeature`      | renommé `Specimen` (ADR-039)                                                     |
| `HistoricalSensor`     | supprimé, remplacé par `TimeSeriesSource`                                        |
| `Equipment`            | supprimé, éclaté dans les cinq entités instrumentales                            |
| `TimeSeriesBundle`     | renommé `Bundle` (ADR-042)                                                       |
| `TransformedTimeSerie` | renommé `TransformedTimeSeries`                                                  |
| `Deployment`           | décrit comme "plateforme regroupant plusieurs capteurs", devenu un acte récursif |

`docs/model/index.md` liste 29 entités, le modèle v12 en compte 60. Aucune des
sections 5 à 8 du modèle actuel (monde IoT, couture, chaîne analytique labo,
transformation refondue) n'y figure. `docs/decisions/index.md` s'arrête aux
premiers ADR, dans une rédaction antérieure : ADR-002 y explique encore le
changement de capteur par `HistoricalSensor`.

La procédure de régénération est décrite dans `CLAUDE.md`, section *Régénérer
bdoh-doc*, et n'a jamais été exécutée depuis. Elle mentionne d'ailleurs une page
rawdata.md qui n'existe ni dans `docs/` ni dans `mkdocs.yml`.

**Action, deux temps.** À court terme, décider si le site doit rester en ligne
dans cet état : le plus simple est de désactiver la publication automatique tant
que la régénération n'est pas faite, plutôt que de laisser une documentation
fausse accessible et citable. À moyen terme, régénérer selon la procédure de
`CLAUDE.md`, et poser la règle qui manque : la régénération est une étape du
travail sur le modèle, pas une tâche séparée qu'on repousse.

## T4. Modèle d'endpoints API

Les champs *Utilisé par* et *Relations inverses* du modèle décrivent de la
navigation, pas de la structure SQL. ADR-028 le dit déjà : les relations
inverses sont absentes des tables et réapparaissent comme endpoints. La
conséquence n'en a pas été tirée, et c'est précisément cette partie qui a dérivé
(voir D7).

Deux temps :

- **Maintenant** : ces champs restent dans le modèle comme index de lecture,
  mais leur cohérence est vérifiée par `outils/verifie_modele.py` plutôt que par
  la vigilance. Ils sont dérivables du reste du modèle, donc contrôlables.
- **Après stabilisation du schéma** : un fichier propre, modele/api.md,
  construit par-dessus le modèle de données. Il possédera les endpoints, leur
  pagination, leurs filtres, leur format de réponse, et les exports (STA,
  DataCite, CS API). Le modèle de données reste sa seule source.

Ne pas commencer avant que les `D*` soient soldés : un modèle d'API construit
sur un index de navigation qui ment hériterait de ses erreurs.


# Constats soldés

Tranchés, avec leur raisonnement de résolution. Conservés pour éviter qu'une
question réglée soit rouverte par oubli, et pour que le renvoi depuis un ADR ou
depuis un autre constat reste résolvable. Ne pas rouvrir sans raison neuve.

Les identifiants C1 à C6, M1 à M8, S1 et S5 viennent de l'audit de juin 2026.
Les points A1 à A7, B1 et C1 à C4 d'un fichier de points ouverts encore
antérieur sont tranchés et documentés en ADR-051 à ADR-059 ; ils n'ont aucun
lien avec les identifiants ci-dessous.

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

## C5. Le catalogue TPC agent mentionne encore TransformationBatch (clos)
Résolu : `TransformationBatch` retiré du catalogue TPC agent, avec note explicite
que son exécutant est toujours une Machine (le `runner`), jamais un couple
`agentType/agentId`. `AnalysisBatch` ajouté au catalogue à sa place (agent réel,
absent jusqu'ici).

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


 (clos)
## T2. Passer tous les tableaux au format (clos)

Mesure faite sur les fichiers Markdown de `dev/CLAUDE/` et `docs/`, ce fichier
exclu, avec un vérificateur écrit pour l'occasion (`outils/mdtable.py`, voir
CH-17 pour la règle appliquée) :

| Constat                                                             | Nombre |
|---------------------------------------------------------------------|--------|
| Tableaux dont toutes les barres verticales sont alignées            | 26     |
| Tableaux dont au moins une cellule dépasse la largeur de sa colonne | 47     |
| Tableaux dont le padding est simplement absent ou incomplet         | 38     |
| Tableaux dont le nombre de cellules varie d'une ligne à l'autre     | 0      |

Répartition par périmètre : 24 tableaux corrects sur 77 dans `dev/CLAUDE/`,
2 sur 34 dans `docs/`.

Le défaut le plus fréquent est systématique et invisible à la relecture rapide :
la ligne de séparation est plus courte d'un caractère par colonne que les lignes
de contenu. Dans `Person` par exemple, la première colonne fait quinze tirets
alors que les cellules occupent seize caractères. Toutes les barres de la ligne
de séparation sont donc décalées vers la gauche, d'autant plus qu'on avance dans
le tableau. En lecture Markdown brute, le tableau ne forme pas de grille.

Aucun tableau n'a un nombre de cellules incohérent, ce qui est une bonne
nouvelle : le contenu est structurellement sain, seul le rendu ne l'est pas.

**Résolution.** Passe faite le 14 août 2026 sur les huit fichiers vivants (`CLAUDE.md`,
`README.md`, `plan.md`, `modele/`, `methode/`, `annexes/`) : 90 tableaux, tous
conformes. La politique retenue est celle décrite dans `outils/mdtable.py` :
grille à 150 caractères (largeur utile de l'éditeur), colonne la plus large
rabotée si le tableau dépasse, cellules trop longues débordant ligne par ligne.
Les lignes qui débordent passent de 248 à 37 sur l'ensemble du dépôt, dont 203
à 21 pour le seul modèle.

Vérification faite avant écriture : le contenu de chaque cellule est identique
caractère par caractère avant et après, sur les 90 tableaux. Le rendu seul a
changé.

`docs/` n'est pas passé au format : il sera régénéré (T3), le formater
maintenant serait du travail perdu.

Reste connu, non bloquant : la table *Correspondance source vers entités* de
`modele/sources.md` a une colonne du milieu si large qu'aucune politique de
formatage ne la rend confortable. C'est un problème éditorial (trop d'entités
par ligne), pas un problème de format.

 (clos)
## D12. Trois conventions de tiret coexistent (clos)

La règle est de n'utiliser ni cadratin (—) ni demi-cadratin (–), et de
reformuler. Elle est respectée dans les trois gros fichiers de fond
(`modele/modele_donnees.md`, `chantier.md`, `sources.md`, zéro occurrence).
Ailleurs :

| Fichier                        | Cadratin | Demi-cadratin | ` -- ` |
|--------------------------------|----------|---------------|--------|
| `modele/decisions.md`          | 0        | 0             | 90     |
| `archives/integrity_checks.md` | 0        | 0             | 19     |
| `annexes/tpc_philosophie.md`   | 14       | 0             | 5      |
| `CLAUDE.md`                    | 1        | 1             | 0      |
| `docs/` (11 fichiers)          | 59       | 0             | 0      |
| `README.md`                    | 2        | 0             | 0      |

`modele/decisions.md` a substitué ` -- ` au cadratin plutôt que de reformuler :
c'est une troisième convention, non écrite, qui produit un rendu HTML différent
selon le moteur Markdown. `CLAUDE.md` enfreint la règle qu'il énonce.

**Résolution.** Résolu le 14 août 2026. `modele/decisions.md` ne contient plus aucun ` -- ` :
58 titres d'ADR sont passés au point (`## ADR-001. Titre`, aligné sur le style
des identifiants de ce fichier), 9 items de liste au deux-points, et les 23
occurrences en prose ont été reformulées une par une plutôt que substituées.
`annexes/tpc_philosophie.md` : ses 14 titres passent du cadratin au deux-points.
Les ` -- ` restants dans cette annexe sont des commentaires SQL dans des blocs
de code, ils restent.

Les occurrences résiduelles de `—` et `–` dans `CLAUDE.md` et dans ce fichier
sont les énoncés de la règle elle-même, qui cite les caractères.

`docs/` porte encore 59 cadratins : ils partiront avec la régénération (T3).

# Journal

| Date       | Événement                                                                                              |
|------------|--------------------------------------------------------------------------------------------------------|
| 2026-08-14 | Unification de `chantier.md` et de l'ancien `chantier.md` en un fichier unique                         |
| 2026-08-14 | Renumérotation : les `CH-*` deviennent `D*`, `V*` et `T*` selon leur nature                            |
| 2026-08-14 | Clos par la remise en ordre de l'espace de travail : anciens CH-02, CH-03, CH-04, CH-14, CH-20 à CH-24 |
| 2026-08-14 | D10 : la section C3 en double est résolue, la version ouverte était superseded par la close            |
