---
title: Chantier BDOH
subtitle: Défauts documentaires, dette de formatage, hygiène de l'espace de travail
source: audit de l'espace de travail bdoh-doc, août 2026
---

# Comment lire ce fichier

Ce fichier possède **les défauts de l'espace de travail et de la documentation** :
divergences entre ce que le modèle dit à un endroit et à un autre, dette de
formatage, fichiers périmés, désordre des dossiers, état des standards à
rafraîchir.

Il ne possède aucune question de conception. Une question de fond non tranchée
(faut-il séparer état métier et cycle de vie ? faut-il dater
`person_organization` ?) appartient à `points_ouverts.md`, jamais ici. La
frontière est nette :

- `points_ouverts.md` : ce que le modèle **devrait dire** et qu'on ne sait pas
  encore. Résolu par une décision, puis par un ADR.
- `chantier.md` (ce fichier) : ce que le modèle **dit déjà mais mal, deux fois,
  ou plus du tout**. Résolu par une édition, sans décision de fond.

Un constat qui, en l'instruisant, se révèle être une question de conception
change de fichier. On le clôt ici avec la mention "déplacé vers
`points_ouverts.md` (identifiant)".

Chaque constat porte un identifiant stable `CH-nn` pour être cité ailleurs.
Les renvois au modèle se font par nom d'entité ou de section, jamais par numéro
de ligne : les numéros bougent, les noms non.

Convention de rédaction héritée du projet : pas de tiret cadratin ni
demi-cadratin. Deux-points, parenthèses, reformulation.


# Triage

Sévérité : `élevée` (risque de perte d'information ou de publication fausse),
`moyenne` (le modèle se contredit, un lecteur peut se tromper), `faible`
(cosmétique ou confort). Effort : `faible` (édition ponctuelle), `moyen` (passe
sur plusieurs fichiers), `élevé` (régénération complète).

| ID    | Constat                                                                | Catégorie   | Sévérité | Effort | État   |
|-------|------------------------------------------------------------------------|-------------|----------|--------|--------|
| CH-01 | 18 constats d'audit vivent seulement dans un dossier ignoré par git    | perte       | élevée   | faible | ouvert |
| CH-19 | Le site public publie un modèle de mars 2026, disparu depuis           | publication | élevée   | élevé  | ouvert |
| CH-03 | `dev/old/` ignoré par git, contient un backlog non repris ailleurs     | perte       | moyenne  | faible | ouvert |
| CH-05 | Patterns transversaux annonce quatre TPC, le modèle en porte cinq      | divergence  | moyenne  | faible | ouvert |
| CH-06 | Facility et SamplingBatch hors des domaines de référence, 6 tableaux   | divergence  | moyenne  | faible | ouvert |
| CH-07 | L'index anchor cite `Specimen`, la colonne est sur `SamplingBatch`     | divergence  | moyenne  | faible | ouvert |
| CH-10 | `Memory` cite `System`, entité supprimée par ADR-062                   | divergence  | moyenne  | faible | ouvert |
| CH-11 | Cinq mentions "(FK x)" désignent une colonne qui n'existe pas          | divergence  | moyenne  | faible | ouvert |
| CH-14 | `integrity_checks.md` entièrement écrit sur un modèle disparu          | périmé      | moyenne  | moyen  | ouvert |
| CH-16 | 26 tableaux sur 111 seulement forment une grille correcte              | formatage   | moyenne  | moyen  | ouvert |
| CH-17 | La règle d'alignement de `CLAUDE.md` se contredit elle-même            | formatage   | moyenne  | faible | ouvert |
| CH-25 | `sources.md` pointe les brouillons de CS API, désormais standards      | veille      | moyenne  | faible | ouvert |
| CH-13 | La version de DataCite est figée dans le modèle, et périmée            | propriété   | moyenne  | faible | ouvert |
| CH-08 | `bundle_series` absent de l'index des tables de jointure               | divergence  | faible   | faible | ouvert |
| CH-09 | Deux tables de jointure citées sans tableau de colonnes                | divergence  | faible   | faible | ouvert |
| CH-12 | Deux colonnes en TitleCase contre la convention camelCase              | divergence  | faible   | faible | ouvert |
| CH-15 | `points_ouverts.md` contient deux fois la section C3                   | doublon     | faible   | faible | ouvert |
| CH-18 | Trois conventions de tiret coexistent dans le projet                   | formatage   | faible   | faible | ouvert |
| CH-20 | `documentation_externe/` mélange sources externes et production        | rangement   | faible   | moyen  | ouvert |
| CH-21 | `dev/CLAUDE/` est nommé d'après l'outil, pas d'après son contenu       | rangement   | faible   | faible | ouvert |
| CH-22 | Trois versions du texte philosophique, aucune ne dit laquelle fait foi | doublon     | faible   | faible | ouvert |
| CH-23 | `note.md` est une boîte d'entrée non triée                             | rangement   | faible   | faible | ouvert |
| CH-24 | Le `.gitignore` masque `tmp` et `old` partout, sans exception          | perte       | faible   | faible | ouvert |
| CH-04 | Un fichier de verrou drawio est suivi par git                          | rangement   | faible   | faible | ouvert |
| CH-02 | Deux PDF dérivés non suivis par git                                    | rangement   | faible   | faible | ouvert |
| CH-26 | Extension STA WebSub 1.0 absente de `sources.md`                       | veille      | faible   | faible | ouvert |
| CH-27 | I-ADOPT absent de `sources.md` alors qu'il vise `Property`             | veille      | faible   | moyen  | ouvert |
| CH-28 | DataCite n'a pas d'entrée d'état daté dans `sources.md`                | propriété   | faible   | faible | ouvert |


# Risque de perte d'information

## CH-01. Dix-huit constats d'audit vivent seulement dans un dossier ignoré par git

`dev/CLAUDE/tmp/audit_modele_v12.md` (631 lignes, juillet 2026) porte les
constats C7 à C18, M10 à M14 et S6, avec leur triage sévérité et effort. Ce
fichier dit lui-même qu'il n'est pas un fichier du projet et que chaque constat
est destiné à être versé dans `points_ouverts.md`. Le versement n'a été fait que
partiellement : `points_ouverts.md` s'arrête à C6, M9, S5.

Or `.gitignore` contient la ligne `tmp`, qui ignore tout dossier de ce nom à
n'importe quelle profondeur. Ces 631 lignes ne sont donc dans aucun commit. Un
`git clean`, un changement de machine ou une suppression de dossier temporaire
les efface sans trace.

Constats concernés, dans l'ordre du triage de l'audit :

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

Trois de ces constats ont été retrouvés indépendamment lors du présent audit
(C13, C14, C17, repris ici en CH-12, CH-09, CH-11). Cette convergence sans
consultation préalable indique que l'audit de juillet est fiable et qu'il n'y a
pas de raison de le refaire : il y a raison de le verser.

**Action** : verser ces 18 constats dans `points_ouverts.md` (leur place, ce sont
des questions de conception), puis supprimer le fichier d'audit ou l'archiver
dans un dossier suivi par git. Ne pas les recopier ici : ce fichier ne possède
pas les questions de conception.

## CH-03. `dev/old/` ignoré par git

Même mécanisme que CH-01 : `.gitignore` contient `old`. Le dossier contient
`product_backlog.md`, backlog fonctionnel de la plateforme (monitoring, RGPD,
mentions légales, gestion des exports, traduction) dont rien n'est repris
ailleurs, et `chat_architecture_initiale.txt`, une conversation d'architecture initiale.

`product_backlog.md` n'est pas de la conception de modèle : c'est un besoin
fonctionnel de plateforme. Il n'a donc pas sa place dans `points_ouverts.md`. Il
en faut soit un fichier propre, soit une décision explicite de l'abandonner.

**Action** : décider si le backlog fonctionnel est vivant. S'il l'est, le sortir
de `old/` et le suivre. Sinon, l'archiver explicitement.

## CH-24. Le `.gitignore` masque `tmp` et `old` sans exception

Les motifs `tmp` et `old` du `.gitignore` sont sans barre oblique ni ancrage :
ils ignorent tout dossier portant ce nom à n'importe quelle profondeur. C'est ce
qui a rendu CH-01 et CH-03 possibles sans que rien ne le signale, puisque `git
status` reste propre.

**Action** : ancrer les motifs (`/tmp/`, `/old/`) pour qu'ils ne s'appliquent
qu'à la racine, ou renoncer à ces motifs et ranger les fichiers temporaires hors
du dépôt.

## CH-02. Deux PDF dérivés non suivis

`dev/CLAUDE/modele_donnees_v12.pdf` et
`dev/CLAUDE/philo/agent_TPC_philosophie_synthese_v2.pdf` sont dans l'arbre de
travail sans être suivis, alors que d'autres PDF du même type le sont. Ce sont
des dérivés d'un source Markdown : la question n'est pas de les sauver mais de
trancher une règle unique, suivre tous les PDF dérivés ou n'en suivre aucun.

## CH-04. Un fichier de verrou drawio est suivi par git

`dev/schema/.$conception.drawio.bkp` est un fichier de sauvegarde automatique de
drawio (452 ko), suivi par git. Il double `conception.drawio` et se réécrit tout
seul, ce qui produit du bruit dans chaque diff.

**Action** : le retirer du suivi et ajouter `.$*.bkp` au `.gitignore`.


# Divergences dans le modèle

Toutes les entrées de cette section décrivent une contradiction interne au
fichier qui fait autorité, `modele_donnees_v12.md`, ou entre lui et un fichier
qui le cite. Aucune ne demande de décision de conception : le modèle sait déjà
ce qu'il veut dire, il le dit à un endroit et pas à l'autre.

## CH-05. La section Patterns transversaux annonce quatre déclinaisons TPC, le modèle en porte cinq

La section *Patterns transversaux* écrit "Ce pattern TPC est décliné en quatre
usages" et documente resource, anchor, agent, series. Le TPC **system**
(`systemType` + `systemId`, porté par `Deployment` vers les cinq entités
d'instrumentation) n'a pas de section, pas de domaine de référence déclaré et
pas d'index de tables porteuses.

Il est pourtant listé comme invariant dans `CLAUDE.md` ("un seul pattern TPC,
cinq déclinaisons"), gravé par ADR-062, et utilisé dans la table `Deployment`.
Le lecteur qui découvre le modèle par la section des patterns ne le voit pas.

`note.md` porte déjà ce constat ("reprendre l'entete pattern transversaux manque
system").

## CH-06. `Deployment.anchorType` accepte `Facility`, absent du domaine de référence

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

## CH-07. L'index du pattern anchor cite `Specimen`, la colonne est sur `SamplingBatch`

L'index des tables porteuses de `anchorType` liste `Specimen` et renvoie à
"voir `Specimen.anchorType`". La table `Specimen` ne porte pas cette colonne :
son ancrage passe par `samplingBatch` ou `preparationBatch`. Inversement,
`SamplingBatch` porte bien `anchorType` mais ne figure pas dans l'index.

L'ancre a manifestement été déplacée du Specimen vers le batch lors d'ADR-064,
et l'index n'a pas suivi. Le renvoi "voir X.anchorType" pointe donc vers une
colonne inexistante, alors même que la section affirme que ce champ est "seule
source de vérité".

## CH-08. `bundle_series` absent de l'index des tables de jointure explicites

`bundle_series` a sa propre section, son tableau de colonnes, et figure dans
l'index du pattern TPC series. Il manque dans le tableau *Tables de jointure
explicites*, qui liste `person_organization`,
`transformationbatch_inputseries`, `specimen_parents`,
`transferfunctionset_function` et `dataset_resource`.

## CH-09. Deux tables de jointure citées sans tableau de colonnes

`person_organization` et `transformationbatch_inputseries` sont nommées dans
l'index des jointures, dans les *Utilisé par* de plusieurs entités et dans la
section *Relations inverses et API*, mais n'ont ni section ni tableau de
colonnes. Les quatre autres jointures en ont une. Un lecteur ne peut pas savoir
si `person_organization` porte des dates, un rôle, ou seulement deux clés.

Ce constat recoupe C14 de l'audit de juillet (CH-01), qui en comptait trois.

## CH-10. `Memory` cite `System`, entité supprimée par ADR-062

Le champ *Utilisé par* de `Memory` liste comme cibles possibles "Observatory,
Site, Station, System, TimeSeries, TransformedTimeSeries, Deployment, Project,
TransferFunction". `System` a été éclaté en cinq entités (Sensor, Actuator,
Sampler, Platform, Kit) par ADR-062, et le domaine de référence de
`resourceType` liste bien les cinq. C'est la seule occurrence résiduelle du nom
dans le modèle en dehors des passages qui racontent explicitement l'histoire de
la décision.

## CH-11. Cinq mentions "(FK nomColonne)" désignent une colonne qui n'existe pas

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

## CH-12. Deux colonnes en TitleCase contre la convention camelCase

`Site.Observatory` et `Station.Site` sont les deux seules colonnes du modèle en
TitleCase. La section *Conventions de nommage* dit "camelCase partout", avec
pour seule exception les suffixes de langue (`label_fr`, `term_en`). Le TitleCase
est réservé aux valeurs de discriminant TPC, où il porte un sens précis : le nom
exact de l'entité ciblée. L'utiliser aussi comme nom de colonne brouille ce
signal.

Ce constat est C13 de l'audit de juillet.

## CH-13. La version de DataCite est figée dans le modèle, et périmée

`modele_donnees_v12.md` écrit "Correspondance entre les propriétés DataCite 4.6
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

## CH-15. `points_ouverts.md` contient deux fois la section C3

Le fichier porte successivement "## C3. Couverture de la suppression logique
incomplète" puis "## C3. Couverture de la suppression logique incomplète
(clos)". La première version décrit le problème ouvert avec sa piste
d'instruction, la seconde le résout entité par entité. Le tableau de triage ne
compte qu'un C3, marqué clos. La version ouverte aurait dû disparaître lors de
la clôture.


# Fichiers périmés

## CH-14. `integrity_checks.md` est entièrement écrit sur un modèle disparu

`dev/CLAUDE/in_construction/integrity_checks.md` documente les vérifications
d'intégrité applicative à implémenter. Son contenu porte sur `InstrumentUsage`
(remplacé par ADR-037 puis ADR-062), `Equipment` (supprimé), `SamplingFeature`
(renommé `Specimen` par ADR-039) et `TimeSerie` (renommé `TimeSeries`). Les
requêtes SQL d'exemple portent sur des tables qui n'existeront jamais. Il cite
ADR-004 et ADR-029 comme justification, or ADR-029 figure dans les décisions
remplacées.

Le sujet, lui, est vivant et prioritaire : c'est S3 de `points_ouverts.md`
(inventaire des invariants applicatifs à tenir), et le nombre de patterns TPC est
passé de deux à cinq depuis l'écriture du fichier. Le danger est qu'un lecteur
pressé prenne ce fichier pour l'inventaire à jour.

**Action** : décider entre réécrire sur les cinq patterns actuels, ou supprimer
et laisser S3 porter le sujet jusqu'à l'implémentation. La deuxième option est
cohérente avec la règle de propriété unique : tant que rien n'est implémenté, un
fichier de contrôles séparé duplique S3.


# Publication

## CH-19. Le site public publie un modèle de mars 2026, disparu depuis

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


# Formatage

## CH-16. Vingt-six tableaux sur cent onze forment une grille correcte

Mesure faite sur les fichiers Markdown de `dev/CLAUDE/` et `docs/`, ce fichier
exclu, avec un vérificateur écrit pour l'occasion (`dev/outils/mdtable.py`, voir
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

## CH-17. La règle d'alignement de `CLAUDE.md` se contredit elle-même

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

## CH-18. Trois conventions de tiret coexistent

La règle est de n'utiliser ni cadratin (—) ni demi-cadratin (–), et de
reformuler. Elle est respectée dans les trois gros fichiers de fond
(`modele_donnees_v12.md`, `points_ouverts.md`, `sources.md`, zéro occurrence).
Ailleurs :

| Fichier                          | Cadratin | Demi-cadratin | ` -- ` |
|----------------------------------|----------|---------------|--------|
| `decisions_index.md`             | 0        | 0             | 90     |
| `integrity_checks.md`            | 0        | 0             | 19     |
| `philo/agent_TPC_philosophie.md` | 14       | 0             | 5      |
| `CLAUDE.md`                      | 1        | 1             | 0      |
| `docs/` (11 fichiers)            | 59       | 0             | 0      |
| `README.md`                      | 2        | 0             | 0      |

`decisions_index.md` a substitué ` -- ` au cadratin plutôt que de reformuler :
c'est une troisième convention, non écrite, qui produit un rendu HTML différent
selon le moteur Markdown. `CLAUDE.md` enfreint la règle qu'il énonce.


# Rangement de l'espace de travail

## CH-20. `documentation_externe/` mélange sources externes et production interne

Le dossier contient trois natures de fichiers que son nom ne distingue pas :

| Fichier                              | Nature réelle                                   |
|--------------------------------------|-------------------------------------------------|
| `DocumentationBDOH.pdf`              | source externe (documentation BDOH actuelle)    |
| `2026-02-WiSSkHy_GET_V2.pdf`         | source externe (présentation GET)               |
| `donnees_chimie_exemple.zip`         | jeu de données d'exemple                        |
| `PIZ_H_20240710_20241219_t_BDOH.txt` | jeu de données d'exemple                        |
| `revue_biblio.txt`                   | production interne (notes de lecture)           |
| `mail.txt`                           | correspondance (échange avec le BRGM)           |
| `BDOH_model.txt`                     | production interne (ancien brouillon de modèle) |

`revue_biblio.txt` recoupe partiellement `sources.md` sur WiSSkHy, ce qui crée
un début de double vérité sur un sujet dont `sources.md` est propriétaire.
`BDOH_model.txt` est un état ancien du modèle, à archiver comme tel ou à
supprimer.

## CH-21. `dev/CLAUDE/` est nommé d'après l'outil, pas d'après le contenu

Le dossier contient le modèle de données, les ADR, les points ouverts, la
bibliographie : le cœur intellectuel du projet, indépendant de l'outil qui a
servi à l'écrire. Le nom actuel désigne l'assistant, ce qui donne l'impression
que ces fichiers sont des artefacts d'outillage. Dans dix ans, un successeur
ouvrira ce dépôt sans savoir ce que le nom désigne.

Le sujet n'est pas cosmétique pour un travail dont l'exigence affichée est la
pérennité longue.

## CH-22. Trois versions du texte philosophique, aucune ne dit laquelle fait foi

`philo/` contient `agent_TPC_philosophie.md` (621 lignes, texte complet),
`agent_TPC_philosophie_synthese.md` (80 lignes) et
`agent_TPC_philosophie_synthese_v2.md` (82 lignes). Les deux synthèses partagent
leurs premiers paragraphes mot pour mot ; la v2 ajoute le passage sur les types
sommes et produits. Rien n'indique laquelle fait foi.

`CLAUDE.md` désigne `agent_TPC_philosophie_synthese.md` comme propriétaire de la
justification philosophique du pattern TPC, donc la v1, alors que la v2 est plus
récente et plus complète.

## CH-23. `note.md` est une boîte d'entrée non triée

Sept lignes brutes, sans date, sans statut, dont au moins deux relèvent du
chantier documentaire ("ascii des system / deployement pas bon", "reprendre
l'entete pattern transversaux manque system", qui est CH-05), au moins trois de
la conception ("deux mesures en même temps en chimie au même endroit", "TTS sans
TS", "l'objet machine est peut-être mal nommé"), et une de la veille
d'identifiants ("ajouter les identifiants RAID pour les projets").

Une boîte d'entrée est utile et il n'y a aucune raison de la supprimer. La
question est de la vider régulièrement vers les fichiers propriétaires plutôt
que de la laisser sédimenter, faute de quoi elle devient un huitième
propriétaire d'information non déclaré.


# Veille standards à répercuter dans `sources.md`

Ces constats appartiennent à `sources.md`, seul propriétaire de l'état daté des
standards. Ils sont listés ici comme travaux à faire, pas comme information : ne
pas lire ce tableau comme une source.

Vérifications faites en ligne le 14 août 2026.

## CH-25. `sources.md` pointe les brouillons de CS API, désormais standards

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

## Confirmation, sans action : STA 2.0 n'est toujours pas ratifié

`sources.md` écrit que l'appel à commentaires publics sur STA 2.0 s'est clos le
18 janvier 2026 et que le standard n'est pas encore ratifié. Vérification faite :
la page des standards SensorThings de l'OGC liste toujours 1.1 comme dernière
version approuvée de Part 1, et 2.0 n'y figure pas. La publication est annoncée
pour 2026 sans date. Le choix de rester sur STA 1.1 en production reste justifié,
et l'entrée de `sources.md` est exacte au 14 août 2026 : il suffit d'en dater la
vérification.

## CH-26. Extension STA WebSub 1.0 absente de `sources.md`

La page OGC liste une extension approuvée que `sources.md` ne mentionne pas :
SensorThings API Extension WebSub Asynchronous Messaging Standard 1.0
(24-032r1), à côté de STAplus 1.0 déjà présent. Elle standardise la notification
asynchrone de nouvelles observations.

Intérêt pour BDOH à évaluer, sans urgence : c'est un sujet d'interface, pas de
modèle de données, donc sans effet sur le schéma. À noter dans `sources.md` pour
que la liste des extensions STA soit complète.

## CH-27. I-ADOPT absent de `sources.md` alors qu'il vise exactement `Property`

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
`points_ouverts.md` (aggregationStatistic mélangeant cadence et statistique),
clos, dont I-ADOPT donne une lecture indépendante avec son StatisticalModifier.

**Action** : ajouter l'entrée dans `sources.md` avec son état daté, puis ouvrir
un point dans `points_ouverts.md` si la projection révèle un écart de fond. Ne
rien changer au modèle avant cette instruction.

## CH-28. DataCite n'a pas d'entrée d'état daté dans `sources.md`

Voir CH-13 pour le constat. L'action côté `sources.md` est de lui donner une
entrée propre, avec la version courante (4.7, publiée le 3 mars 2026), pour que
le modèle puisse cesser de la porter.


# Journal

| Date       | Événement                                                                 |
|------------|---------------------------------------------------------------------------|
| 2026-08-14 | Création du fichier, audit initial de l'espace de travail (CH-01 à CH-28) |
