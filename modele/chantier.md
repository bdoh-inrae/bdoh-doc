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


# Comment on instruit un constat

Un constat à la fois, dans l'ordre du triage sauf raison de faire autrement.
**Rien n'est écrit dans le modèle avant que Louis ait tranché.** Ce fichier
recense ; il ne se vide pas tout seul.

Chaque constat est présenté dans cet ordre, en quatre temps :

1. **Le constat**, tel qu'il est écrit ici. Pas reformulé en mieux : si sa
   rédaction est mauvaise, c'est un fait à signaler, pas à corriger en passant.
2. **Ce que dit le modèle aujourd'hui.** L'extrait exact concerné, tableau ou
   section, recopié. Pas un résumé : Louis doit pouvoir juger sur pièce sans
   ouvrir le fichier.
3. **Ce que j'en pense.** Le constat tient-il ? Si oui, quelles options, ce qui
   les distingue, et une recommandation assumée. Si non, l'argument qui l'écarte.
4. **Ce que ça changerait.** Les tableaux en avant et après, alignés, dès qu'une
   modification est en jeu.

Puis Louis tranche. Ensuite seulement, l'édition.

Trois situations arrêtent la marche plutôt que de la forcer :

- **Louis ne comprend pas.** Je réexplique autrement, par un exemple, un schéma,
  le besoin métier. Je ne change pas d'avis pour faire passer (réflexe 8 de
  `methode/SOUL.md`). Une proposition juste qu'il ne peut pas valider ne sert à
  rien, mais l'abandonner sous la friction ferait perdre une bonne solution.
- **Le constat cache une question plus large.** On le sort du fil, il ouvre son
  propre plan. Le forcer dans une session de passage en revue le traiterait mal.
- **On a changé de sujet.** Je le dis, et c'est le moment de vider le contexte
  plutôt que de traîner l'ancien (réflexe 9).

Fin d'un constat, toujours l'une de ces trois sorties :

| Sortie                | Ce qu'on écrit                                                                 |
|-----------------------|--------------------------------------------------------------------------------|
| Reste ouvert          | il rejoint sa lettre, avec ce que l'instruction a clarifié                     |
| Réglé, ou écarté      | il descend en *Constats soldés*, avec la raison écrite                         |
| Décision structurante | en plus, un ADR dans `modele/decisions.md`, qui devient le porteur du pourquoi |


# Triage

Sévérité : `élevée` (à traiter avant gel du schéma, ou risque de publication
fausse), `moyenne` (le modèle se contredit ou un cas réel n'est pas couvert),
`faible` (cosmétique ou confort). Effort : `faible` (édition ponctuelle),
`moyen` (refonte locale ou décision de fond), `élevé` (changement structurel ou
passe complète).

| ID    | Constat                                                                   | Sévérité | Effort |
|-------|---------------------------------------------------------------------------|----------|--------|
| C19   | Passage obligatoire par `Deployment` : jamais décidé, diverge de CS API   | moyenne  | moyen  |
| C20   | Convention de nommage : bonne pour l'API, pas celle de PostgreSQL         | moyenne  | faible |
| M9    | Données d'expérience de terrain : valeur issue d'un fit sur série courte  | élevée   | moyen  |
| T3    | La documentation publique décrit un modèle disparu                        | élevée   | élevé  |
| S3    | Invariants applicatifs cumulés : inventaire à tenir                       | moyenne  | moyen  |
| S4    | Historique des valeurs : propriété à écrire, pas à corriger               | moyenne  | faible |
| S2    | Ancrage et lien au matériel : à confirmer soldé, ses cinq parties le sont | faible   | faible |
| D5    | `person_organization` sans tableau de colonnes, bloqué par M11            | faible   | faible |
| V1    | OGC API Connected Systems comme cible v2                                  | veille   | -      |
| V2    | Alignement STAMPLATE et écosystème européen                               | veille   | -      |
| T4    | Modèle d'endpoints API à construire par-dessus le modèle de données       | -        | élevé  |
| audit | Vingt constats versés depuis l'audit de juillet, jamais lus ni instruits  | -        | -      |

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

## C20. La convention de nommage est cohérente, mais ce n'est pas celle de PostgreSQL

Question posée le 14 août 2026 : cette convention est-elle solide, compréhensible
de l'extérieur, conforme aux pratiques de base de données ? Réponse en deux
temps, parce qu'elle n'est pas la même selon la couche.

**Comme modèle conceptuel et comme API, elle est bonne.** `TitleCase` pour les
entités est la convention de la documentation STA, ODM2 et SensorML : un lecteur
venant de ces standards lit `Observatory` et `TimeSeries` sans effort.
`camelCase` pour les attributs est la convention JSON, donc celle de l'API, et
celle qu'emploie STA lui-même (`phenomenonTime`, `unitOfMeasurement`,
`resultTime`). De ce point de vue, la convention est non seulement défendable,
elle est meilleure que `snake_case` pour l'interopérabilité.

**Comme schéma SQL, ce n'est pas la pratique courante, et le coût n'a jamais été
nommé.** La convention PostgreSQL est `snake_case` minuscule partout. La raison
est mécanique, pas esthétique : PostgreSQL replie tout identifiant non protégé en
minuscules.

```sql
CREATE TABLE Observatory (anchorType text);   -- cree "observatory"."anchortype"
SELECT anchorType FROM Observatory;           -- fonctionne, mais lit anchortype
CREATE TABLE "Observatory" ("anchorType" text);  -- respecte la casse
SELECT "anchorType" FROM "Observatory";          -- il faut citer, partout, toujours
```

Conserver la casse impose donc de mettre des guillemets doubles autour de
**chaque** identifiant, dans chaque requête, chaque vue, chaque migration, chaque
script d'administration. Un oubli ne lève pas toujours d'erreur : il peut viser
silencieusement un identifiant replié différent. Les outils (`psql \d`,
`pg_dump`, un client graphique) affichent les noms cités. Les ORM demandent une
correspondance explicite champ par champ.

**Ce que le modèle affirme aujourd'hui**, dans sa section *Nature du fichier* :
« Chaque tableau décrit les colonnes réelles d'une table SQL. » Si le schéma
physique finit en `snake_case`, cette phrase devient fausse.

**Trois issues possibles, aucune tranchée ici.**

| Issue                                              | Ce qu'elle implique                                                                           |
|----------------------------------------------------|-----------------------------------------------------------------------------------------------|
| Garder la casse en base, avec guillemets partout   | cohérence parfaite doc / base / API, au prix d'une discipline de citation permanente et de pièges connus |
| Schéma physique en `snake_case`, mapping par l'ORM | pratique standard, aucun piège SQL ; le modèle devient un modèle **logique** et doit le dire  |
| Statu quo sans décision                            | le plus coûteux : la question se posera au premier `CREATE TABLE`, sans arbitrage écrit       |

La deuxième est la plus courante dans les projets qui rencontrent ce cas, et
elle ne coûte presque rien tant que rien n'est implémenté : il suffit d'écrire
une phrase dans la convention et une règle de dérivation (`anchorType` devient
`anchor_type`). Mais c'est un choix, pas une évidence, et il touche l'affirmation
la plus fondamentale du fichier modèle.

**Point secondaire**, à trancher avec le reste : la distinction `TitleCase` pour
les entités contre `snake_case` pour les jointures sans identité propre est
inhabituelle. Elle porte une vraie information (ces tables ne sont pas des
entités référençables) et c'est un argument valable, mais un lecteur extérieur
n'a aucune raison de la deviner. Elle est documentée, ce qui suffit peut-être.

**À instruire avant le premier `CREATE TABLE`**, pas avant. Rien n'est implémenté,
donc rien ne presse ; mais l'arbitrage devient coûteux dès la première migration.

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

# T. Travaux

## T1. Verser les constats de l'audit archivé (clos)

archives/audit_modele_v12.md (631 lignes, juillet 2026, depuis supprimé) est un audit du modèle
produit sur claude.ai, jamais relu. Il porte les constats C7 à C18, M10 à M14 et
S6, avec leur triage sévérité et effort, et dit lui-même que chacun est destiné à
être versé ici. Le versement n'a jamais été fait.

**Ce que fait T1, et ce qu'il ne fait pas.** T1 est une tâche de rangement, pas
d'instruction. Il verse les constats dans ce fichier avec leur lettre, pour qu'ils
cessent de vivre dans un fichier d'archive que rien ne consulte. Il ne les
tranche pas : chacun sera pris un par un, plus tard, comme n'importe quel autre
constat ouvert.

**Aucun tri au versement.** Trois constats de l'audit (C13, C14, C17) ressemblent
à des divergences traitées en août 2026 (D8, D5, D7), mais le rapprochement est
fait de l'extérieur, sur les titres, sans que le texte de l'audit ait été lu par
Louis. Décider qu'ils sont clos serait trancher à sa place. Ils sont donc versés
comme les autres, avec une note signalant le recoupement possible, et le
rapprochement se vérifiera au moment de leur instruction.

Ce que cette ressemblance indique en revanche, c'est que l'audit de juillet est
fiable : ces trois constats ont été retrouvés indépendamment en août sans qu'il
ait été consulté. Raison de plus pour le verser tel quel plutôt que le réécrire.

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

**Fait le 14 août 2026.** Les vingt constats sont versés dans la section
*Constats versés depuis l'audit de juillet 2026*, ci-dessous, texte d'origine
intact, sans tri ni jugement. archives/audit_modele_v12.md (supprimé, lisible dans l'historique git) est supprimé : son
contenu vit désormais ici, et l'archive n'aurait plus qu'à diverger.

Reste à faire, hors de ce plan : instruire chaque constat, un par un.

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

**Procédure de régénération**, déplacée depuis `CLAUDE.md` dont elle n'était pas
la propriété. Prérequis : `pip install mkdocs-material`.

Structure cible :

```
docs/
  index.md  overview.md
  model/
    index.md  actors.md  references.md  geography.md  network.md
    rawdata.md  instrumentation.md  observation.md  transformation.md
    organisation.md  project.md
  standards/index.md
  decisions/index.md
```

1. Lire `modele/modele_donnees.md` en entier.
2. Découper en pages selon la structure ci-dessus, ajouter les liens internes.
3. Mettre à jour `docs/decisions/index.md` depuis `modele/decisions.md`.
4. Mettre à jour `docs/standards/index.md` depuis `modele/sources.md`, sans
   ressaisir l'état des standards à la main : il vit dans `modele/sources.md`.
5. Tester avec `mkdocs serve` avant de pousser.
6. Réactiver le déclenchement automatique de `.github/workflows/deploy.yml`,
   mais seulement après avoir posé la garantie que la régénération fait partie
   du travail sur le modèle, et non d'une tâche séparée qu'on repousse. C'est
   cette absence de garantie, pas l'oubli, qui a laissé le site geler cinq mois.

Points de vigilance hérités :
- `instrumentation.md` (cinq entités d'instrumentation plus Deployment récursif)
  est à créer, il n'existe pas dans la version en ligne.
- `transformation.md` a été profondément remanié : ne pas repartir de l'ancienne
  version.
- Le mapping `qualityFlag` ODM2 / SANDRE et l'état de STA 2.0 viennent de
  `modele/decisions.md` (ADR-024) et de `modele/sources.md`.
- La page rawdata.md est citée par cette procédure mais n'existe ni dans
  `docs/` ni dans `mkdocs.yml` : à créer ou à retirer de la structure cible.

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


## T5. Dépôt de scripts BDOH

Conventions de nommage, format des fichiers de paramétrage, processus de
versionnement des scripts référencés par `Algorithm`. À traiter avant
l'implémentation des `TransformationBatch` algorithmiques, sinon les `swhid`
épinglent du code dont l'organisation n'a pas été pensée.

Déplacé depuis `CLAUDE.md`, section *Chantiers techniques en cours*, qui
dupliquait ce fichier.

## T6. Ingestion : format CSV et pipeline de validation

Spécifier le format CSV attendu par l'API et le pipeline de validation
automatique. Priorité basse, cible v2.

Aucun modèle de données supplémentaire n'est requis : `ObservationBatch` et
`ValidationBatch` couvrent déjà la traçabilité. C'est un travail de
spécification d'interface, pas de modélisation.

Déplacé depuis `CLAUDE.md`.


# Constats versés depuis l'audit de juillet 2026

Vingt constats issus de archives/audit_modele_v12.md (supprimé, lisible dans l'historique git), versés ici **tels quels**
le 14 août 2026, sans avoir été lus ni instruits. Leur texte est celui de
l'audit, mot pour mot ; leurs identifiants sont ceux de l'audit.

Ils sont dans une section à part, et pas rangés sous leur lettre, pour une
raison : les ranger supposerait de juger de quelle nature ils sont, donc de les
avoir instruits. Ce n'était pas l'objet de la remise en ordre. Ils vivaient dans
un fichier d'archive que rien ne consulte ; ils vivent maintenant là où on les
verra.

**Comment les traiter.** Un par un, dans une session dédiée. Chaque constat
instruit quitte cette section : il rejoint sa lettre s'il reste ouvert, ou les
*Constats soldés* s'il est réglé ou écarté, avec la raison écrite. La section
disparaît quand elle est vide.

Deux avertissements de lecture, vérifiables sans rien instruire :

- **Recoupements possibles.** C13, C14 et C17 ressemblent, par leur titre, à des
  divergences traitées en août (D8, D5, D7). Le rapprochement est fait de
  l'extérieur, sur les titres, et n'a pas été vérifié dans le texte : à
  confirmer au moment de leur instruction, pas avant.
- **Collision d'identifiants.** M4 et V1 ci-dessous ne sont pas des constats mais
  des notes de renvoi de l'audit, et leurs identifiants sont déjà pris dans ce
  fichier par des constats différents (M4 soldé, V1 ouvert). Ils sont versés
  quand même, sans renumérotation : renuméroter casserait le lien avec le texte
  d'origine. À démêler à l'instruction.

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

## M4 et la chaîne labo : voir M9 (nouveau constat, regroupe et élargit)

M4 est un symptôme d'une question plus large traitée en M9 ci-dessous : le
modèle offre aujourd'hui deux chemins pour la donnée de laboratoire sans dire
lequel est canonique. Trancher M9 résout M4 par ricochet (si la chimie
n'entre plus par la couche IoT, la contrainte `Datastream.system` obligatoire
cesse d'être un problème labo).

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

## V1 et V2 : mise à jour

Voir section 1. V1 gagne un élément (Part 3 pub/sub en draft : la cible v2
inclura potentiellement du streaming temps réel standardisé). V2 gagne deux
éléments concrets : le schéma qualité DQV de STAMPLATE comme modèle
d'exposition de `qualityFlag` en STA 1.1, et l'ENVRI-Hub opérationnel depuis
avril 2026 comme point d'observation de la convergence des vocabulaires.


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
`README.md`, le plan de travail, `modele/`, `methode/`, `annexes/`) : 90 tableaux, tous
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


## D11. La règle d'alignement des tableaux se contredit elle-même (clos)

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

**Résolution.** Résolu le 14 août 2026 par l'écriture de `methode/redaction.md`,
qui devient le propriétaire des règles d'écriture. La règle y est énoncée en
trois temps sans contradiction : padder à la cellule la plus large ; raboter la
colonne la plus large si le tableau dépasse 150 caractères ; laisser les
cellules trop longues de cette colonne déborder ligne par ligne. La phrase
« le contenu ne se raccourcit jamais pour tenir dans la grille » est conservée
telle quelle, elle n'a jamais été le problème.


## D1. La section Patterns transversaux annonce quatre déclinaisons TPC, le modèle en porte cinq (clos)

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

**Résolution.** Résolu le 14 août 2026. La section *Pattern TPC system* est écrite, avec son
domaine de référence (`Sensor`, `Actuator`, `Sampler`, `Platform`, `Kit`), son
index (`Deployment`, seul porteur) et la conséquence structurante qui n'était
écrite nulle part : aucun objet d'instrumentation n'est jamais référencé nu,
tout lien vers du matériel passe par un `Deployment`. L'introduction annonce
maintenant cinq déclinaisons.


## D2. `Facility` et `SamplingBatch` hors des domaines de référence, dans six tableaux (clos)

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

**Résolution.** Résolu le 14 août 2026. `Facility` et `SamplingBatch` rejoignent le domaine de
référence de `resourceType` ; `Facility` rejoint celui de `anchorType`, avec la
phrase qui manquait : les trois premières échelles sont celles du terrain,
`Facility` est celle du laboratoire, et une entité qui n'a de sens que sur le
terrain n'accepte que les trois premières. La phrase « toutes acceptent les
trois échelles », devenue fausse, est corrigée. Aucun tableau d'entité n'a
changé : c'étaient eux qui avaient raison.


## D3. L'index du pattern anchor cite `Specimen`, la colonne est sur `SamplingBatch` (clos)

L'index des tables porteuses de `anchorType` liste `Specimen` et renvoie à
"voir `Specimen.anchorType`". La table `Specimen` ne porte pas cette colonne :
son ancrage passe par `samplingBatch` ou `preparationBatch`. Inversement,
`SamplingBatch` porte bien `anchorType` mais ne figure pas dans l'index.

L'ancre a manifestement été déplacée du Specimen vers le batch lors d'ADR-064,
et l'index n'a pas suivi. Le renvoi "voir X.anchorType" pointe donc vers une
colonne inexistante, alors même que la section affirme que ce champ est "seule
source de vérité".

**Résolution.** Résolu le 14 août 2026. L'index du pattern anchor cite `SamplingBatch` à la
place de `Specimen`, conformément à ADR-064 qui a déplacé l'ancre du support
physique vers l'acte de prélèvement.


## D4. `bundle_series` absent de l'index des tables de jointure explicites (clos)

`bundle_series` a sa propre section, son tableau de colonnes, et figure dans
l'index du pattern TPC series. Il manque dans le tableau *Tables de jointure
explicites*, qui liste `person_organization`,
`transformationbatch_inputseries`, `specimen_parents`,
`transferfunctionset_function` et `dataset_resource`.

**Résolution.** Résolu le 14 août 2026. `bundle_series` figure dans l'index des tables de
jointure explicites.


## D6. `Memory` cite `System`, entité supprimée par ADR-062 (clos)

Le champ *Utilisé par* de `Memory` liste comme cibles possibles "Observatory,
Site, Station, System, TimeSeries, TransformedTimeSeries, Deployment, Project,
TransferFunction". `System` a été éclaté en cinq entités (Sensor, Actuator,
Sampler, Platform, Kit) par ADR-062, et le domaine de référence de
`resourceType` liste bien les cinq. C'est la seule occurrence résiduelle du nom
dans le modèle en dehors des passages qui racontent explicitement l'histoire de
la décision.

**Résolution.** Résolu le 14 août 2026. Le champ *Utilisé par* de `Memory` liste les cinq
entités d'instrumentation, `Facility` et `Datastream` à la place de `System`,
conformément au domaine de référence de `resourceType`.


## D7. Cinq mentions "(FK nomColonne)" désignent une colonne qui n'existe pas (clos)

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

**Résolution.** Résolu le 14 août 2026 pour trois des cinq mentions. `Datastream` et
`ControlObservation` sont notés « (via Deployment) » et non « (FK sensor) » : le
lien vers un capteur passe toujours par un déploiement, jamais en direct.
`Specimen` est noté « (via SamplingBatch) ». Les deux mentions restantes,
`Site (FK observatory)` et `Station (FK site)`, dépendent de D8 : renommer la
colonne suffit à les rendre vraies.


## D10. La section C3 figurait deux fois, ouverte et close (clos)

Le fichier porte successivement "## C3. Couverture de la suppression logique
incomplète" puis "## C3. Couverture de la suppression logique incomplète
(clos)". La première version décrit le problème ouvert avec sa piste
d'instruction, la seconde le résout entité par entité. Le tableau de triage ne
compte qu'un C3, marqué clos. La version ouverte aurait dû disparaître lors de
la clôture.

**Résolution.** Résolu le 14 août 2026 lors de l'unification : seule la version
close a été reprise, la version ouverte était superseded par elle.

## D8. Deux colonnes en TitleCase contre la convention camelCase (clos)

`Site.Observatory` et `Station.Site` sont les deux seules colonnes du modèle en
TitleCase. La section *Conventions de nommage* dit "camelCase partout", avec
pour seule exception les suffixes de langue (`label_fr`, `term_en`). Le TitleCase
est réservé aux valeurs de discriminant TPC, où il porte un sens précis : le nom
exact de l'entité ciblée. L'utiliser aussi comme nom de colonne brouille ce
signal.

Ce constat est C13 de l'audit de juillet.

**Résolution.** Résolu le 14 août 2026. `Site.Observatory` devient
`Site.observatory`, `Station.Site` devient `Station.site`. La convention a été
relue avant d'agir et elle est sans ambiguïté : `camelCase` pour toute colonne,
la seule exception étant les suffixes de langue, et le `TitleCase` réservé d'une
part aux noms de tables d'entités, d'autre part aux valeurs de discriminant TPC
où il désigne le nom exact de l'entité ciblée. Une colonne en TitleCase
brouillait donc deux signaux à la fois.

Le renommage rend vraies du même coup les deux dernières mentions de D7, et le
vérificateur sort désormais zéro.

Note : le fait que cette convention soit cohérente en interne ne dit rien de sa
conformité aux pratiques PostgreSQL. Cette question, distincte, est C20.


## D9. La version de DataCite est figée dans le modèle, et périmée (clos)

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

**Résolution.** Résolu le 14 août 2026. Le numéro de version sort du fichier modèle : la section
*Mapping DataCite* ne dit plus « propriétés DataCite 4.6 » et ses liens pointent
la documentation courante, pas une version figée. `modele/sources.md` reçoit une
entrée DataCite en propre, avec son état daté (4.7, publiée le 3 mars 2026), et
en devient le seul propriétaire, comme pour tout autre standard.

Le mapping lui-même n'est pas touché : il s'appuie sur des propriétés stables
depuis 4.x. C'était le numéro de version, pas la correspondance, qui avait
vieilli.


## V3. `sources.md` pointe les brouillons de CS API, désormais standards (clos)

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

**Résolution.** Résolu le 14 août 2026. Les liens des deux parties passent de `/DRAFTS/` aux
URLs canoniques `docs.ogc.org/is/23-001` et `/is/23-002`, vérifiées sur la page
OGC qui les liste en version 1.0 avec le statut IS.

L'entrée gagne au passage un point de vigilance relevé en lisant la Part 2 :
dans CS API, un `DataStream` est rattaché à un `System`, pas à un `Deployment`.
BDOH fait l'inverse, c'est C19.


## V4. Extension STA WebSub 1.0 absente de `sources.md` (clos)

La page OGC liste une extension approuvée que `sources.md` ne mentionne pas :
SensorThings API Extension WebSub Asynchronous Messaging Standard 1.0
(24-032r1), à côté de STAplus 1.0 déjà présent. Elle standardise la notification
asynchrone de nouvelles observations.

Intérêt pour BDOH à évaluer, sans urgence : c'est un sujet d'interface, pas de
modèle de données, donc sans effet sur le schéma. À noter dans `sources.md` pour
que la liste des extensions STA soit complète.

**Résolution.** Résolu le 14 août 2026. `modele/sources.md` porte une entrée pour l'extension
WebSub 1.0 (OGC 24-032r1), à côté de STAplus. Sujet d'interface, sans effet sur
le modèle de données : à évaluer si BDOH expose un jour un flux temps réel.


## V5. I-ADOPT absent de `sources.md` alors qu'il vise exactement `Property` (clos)

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

**Résolution.** Résolu le 14 août 2026 pour ce que ce constat demandait : `modele/sources.md`
porte une entrée I-ADOPT avec son état daté et ce que le cadre apporte à BDOH.

La projection elle-même n'est pas faite, et c'est volontaire : vérifier si la
décomposition `Property` / `Unit` / `aggregationStatistic` / milieu se projette
proprement sur les composants I-ADOPT est un travail de fond, pas de veille. À
ouvrir comme un `M` le jour où on s'y met.


## V6. DataCite n'a pas d'entrée d'état daté dans `sources.md` (clos)

Voir CH-13 pour le constat. L'action côté `sources.md` est de lui donner une
entrée propre, avec la version courante (4.7, publiée le 3 mars 2026), pour que
le modèle puisse cesser de la porter.

**Résolution.** Résolu le 14 août 2026, dans la même passe que D9 : `modele/sources.md` a son
entrée DataCite et en devient le propriétaire unique.

# Journal

| Date       | Événement                                                                                              |
|------------|--------------------------------------------------------------------------------------------------------|
| 2026-08-14 | Unification de `chantier.md` et de l'ancien `chantier.md` en un fichier unique                         |
| 2026-08-14 | Renumérotation : les `CH-*` deviennent `D*`, `V*` et `T*` selon leur nature                            |
| 2026-08-14 | Clos par la remise en ordre de l'espace de travail : anciens CH-02, CH-03, CH-04, CH-14, CH-20 à CH-24 |
| 2026-08-14 | D10 : la section C3 en double est résolue, la version ouverte était superseded par la close            |
