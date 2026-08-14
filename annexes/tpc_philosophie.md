# Modélisation de l'entité Agent dans un système FAIR en hydrologie : du problème technique à ses fondements philosophiques

---

## Partie I : Le problème

### Contexte

Un système de gestion de données hydrologiques et environnementales conçu pour respecter les principes FAIR doit satisfaire quatre exigences : les données doivent être Findable, Accessible, Interoperable, Reusable. Ces exigences ne portent pas seulement sur les données elles-mêmes, mais sur le modèle qui les structure. Un export CSV doit être lisible sans documentation interne. Une métadonnée doit porter sa propre sémantique. Le schéma doit être compréhensible et exploitable indépendamment du système applicatif qui l'a produit.

### Le problème minimal

Plusieurs tables d'un tel modèle nécessitent de référencer un **agent producteur**, c'est-à-dire l'entité responsable d'une action sur la donnée. La difficulté tient à ce que cette entité peut être de nature fondamentalement différente selon le contexte.

Un champ `appliedBy` sur une table de batch de transformation peut désigner un chercheur qui lance manuellement un calcul, ou un pipeline automatisé qui l'exécute sans intervention humaine. Un champ de responsabilité fonctionnelle peut porter sur une personne physique ou sur une organisation. Dans les deux cas, le modèle doit choisir comment représenter cette dualité sans mentir sur la nature des entités impliquées et sans rendre les données illisibles à l'export.

C'est ce choix qui constitue le problème. Il est à la fois technique et philosophique, et la réponse technique correcte dépend d'une analyse honnête de ce que la structure des données est censée dire sur le monde.

### Les contraintes concrètes

Trois contraintes structurent le problème et bornent l'espace des solutions acceptables.

**La contrainte FAIR.** Les données doivent s'auto-décrire. Un export doit indiquer clairement si une action a été réalisée par un humain ou une machine, si une responsabilité porte sur une personne ou une organisation. En hydrologie, cette information est une métadonnée scientifique de premier rang : la provenance d'une donnée validée automatiquement n'a pas la même valeur épistémique qu'une validation humaine experte. La distinction doit être lisible dans les données, pas seulement dans la documentation du schéma.

**La contrainte d'intégrité.** Le modèle doit garantir qu'une référence vers un agent est cohérente : on ne peut pas référencer un agent humain avec l'identifiant d'une machine. Cette garantie doit survivre à l'export, à la réingestion, et à l'usage par des tiers qui ne connaissent pas le système d'origine.

**La contrainte de cohérence interne.** Un modèle de données complexe utilise généralement un nombre limité de patterns structurels. Si le pattern polymorphique `resourceType + resourceId` est déjà employé massivement pour d'autres relations (notes, identifiants externes, mots-clés, responsabilités), introduire une solution différente pour les agents crée une incohérence architecturale qui nuit à l'apprenabilité du modèle et à sa maintenance à long terme.

### Les trois stratégies classiques

En modélisation relationnelle, la généralisation d'un concept en plusieurs types concrets se résout selon trois stratégies canoniques.

**TPH (Table Per Hierarchy)** : une seule table contient tous les types possibles d'une famille conceptuelle. Un champ discriminant indique le type de chaque ligne. Les colonnes spécifiques à chaque type sont présentes pour toutes les lignes et laissées NULL pour les types auxquels elles ne s'appliquent pas. La FK depuis les tables clientes est unique et propre. La vérité sémantique est dans le schéma, pas dans les données.

**TPT (Table Per Type)** : une table parente contient les attributs communs à tous les types, et des tables filles liées par FK contiennent les attributs spécifiques à chaque type. Les jointures se multiplient, les exports sont illisibles sans reconstitution, et la hiérarchie postule une essence commune qui peut ne pas exister dans le domaine.

**TPC (Table Per Concrete type)** : pas de table parente. Chaque type concret a sa propre table indépendante avec tous ses attributs. La table cliente porte un discriminant de type et un identifiant, indiquant explicitement vers quelle entité concrète pointe la référence. La FK native est perdue, mais la sémantique est auto-portée par les données.

La question est de savoir lequel choisir, et pourquoi. La réponse technique seule ne suffit pas. Il faut comprendre ce que chaque choix dit sur la nature du problème lui-même.

---

## Partie II : Le fil philosophique

Les grandes ruptures de la logique et de la philosophie du langage au XXe siècle éclairent ce problème d'une façon qui n'est pas métaphorique. Elles décrivent structurellement pourquoi certaines solutions de modélisation sont condamnées à échouer, quelles que soient les contraintes techniques du moment.

---

### Frege (1848-1925) : Sens et référence

Gottlob Frege pose en 1892 une distinction fondamentale entre le **sens** (Sinn) et la **référence** (Bedeutung) d'un terme. La référence est l'objet pointé dans le monde. Le sens est le mode de présentation de cet objet, la façon dont on y accède conceptuellement. L'étoile du matin et l'étoile du soir ont la même référence (Vénus) mais des sens radicalement différents.

Appliqué à notre problème : un agent humain et un agent machine peuvent avoir la même référence fonctionnelle dans le système (ils produisent tous deux un batch, ils portent tous deux une responsabilité) mais leur sens est distinct. Une validation humaine et une validation automatisée ne sont pas deux modes d'accès au même concept ; ce sont deux concepts différents avec des implications épistémiques différentes.

TPH ignore cette distinction. En plaçant humain et machine dans la même table, il traite deux sens différents comme s'ils partageaient la même référence structurelle. PostgreSQL peut stocker les deux, mais la signification de chaque ligne dépend d'un discriminant implicite que la table ne rend pas visible à l'export.

La leçon de Frege pour la modélisation est directe : un bon modèle de données doit rendre explicite la distinction entre sens et référence. Le discriminant `agentType` porté dans la donnée elle-même, tel que TPC le propose, est précisément cette explicitation.

---

### Russell (1872-1970) et Whitehead : La théorie des types

Bertrand Russell, travaillant avec Alfred North Whitehead sur les Principia Mathematica (1910-1913), trébuche sur un paradoxe fondamental : l'ensemble de tous les ensembles qui ne se contiennent pas eux-mêmes. Si cet ensemble se contient lui-même, il ne devrait pas se contenir. S'il ne se contient pas, il devrait se contenir. Contradiction irréductible.

Pour résoudre ce paradoxe, Russell développe la **théorie des types** : on ne peut pas mélanger dans le même ensemble des objets de niveaux logiques différents sans créer des contradictions. Chaque objet appartient à un type, et les opérations sur ces objets doivent respecter cette stratification.

TPH commet exactement l'erreur que Russell cherche à éviter. Mettre un humain et une machine dans la même table `agent`, c'est construire un ensemble russellien : on y place des objets qui n'appartiennent pas au même type logique, et on espère que les colonnes NULL et les conventions applicatives suffiront à prévenir les contradictions. Ce n'est pas une garantie, c'est un pari sur la discipline des utilisateurs.

TPT tente de corriger cela avec une hiérarchie explicite, mais postule l'existence d'un type parent `agent` dont humain et machine seraient des instances. Il suppose qu'il existe une essence commune suffisamment riche pour mériter une table dédiée. Cette essence, comme on le verra avec Wittgenstein, est une construction qui ne correspond à rien dans le domaine.

TPC est russellien dans le bon sens : il sépare les types concrets et rend leur distinction explicite. Il ne prétend pas qu'il existe un universel `agent` dont humain et machine seraient des spécialisations. Il reconnaît deux types distincts qui jouent parfois le même rôle fonctionnel sans prétendre les unifier dans une hiérarchie artificielle.

---

### Hilbert (1862-1943) : Le programme formaliste

David Hilbert formule au début du XXe siècle un programme ambitieux : formaliser l'intégralité des mathématiques dans un système axiomatique complet, cohérent et décidable. Toute vérité mathématique doit être dérivable mécaniquement depuis un ensemble fini d'axiomes. Le système doit se suffire à lui-même.

C'est exactement l'ambition implicite de TPH et TPT lorsqu'ils tentent de mettre toute la vérité sémantique dans le schéma PostgreSQL. Le schéma joue le rôle du système axiomatique, les contraintes SQL sont les règles de dérivation, et on espère que toute donnée valide sera validable mécaniquement par le moteur sans intervention extérieure.

Ce programme échoue pour les bases de données pour la même raison qu'il échoue en mathématiques : Gödel.

---

### Gödel (1906-1978) : L'incomplétude

En 1931, Kurt Gödel publie ses théorèmes d'incomplétude. Dans tout système formel suffisamment expressif pour exprimer l'arithmétique, il existe des propositions vraies qui ne sont pas démontrables à l'intérieur de ce système. Un système formel ne peut pas être à la fois complet et cohérent. La vérité déborde toujours le système qui tente de la capturer.

La traduction pour notre problème est directe. Un schéma PostgreSQL suffisamment complexe contiendra toujours des vérités sémantiques qu'il ne peut pas capturer formellement. La distinction entre une validation humaine experte et une validation algorithmique automatique est une vérité sémantique réelle, avec des implications scientifiques concrètes en hydrologie. Cette vérité ne peut pas être entièrement garantie par des contraintes SQL. Elle déborde le schéma.

Gödel ne dit pas que les systèmes formels sont inutiles. Il dit qu'ils ont des limites intrinsèques dont il faut être conscient. La bonne réponse n'est pas de chercher un schéma encore plus contraignant, c'est de partitionner consciemment la vérité : ce que le schéma peut légitimement porter, ce que les données doivent porter elles-mêmes, et ce que la couche applicative doit valider.

TPC fait ce choix de façon explicite. Le schéma porte la structure. Le discriminant `agentType` porte le type dans la donnée elle-même. L'API porte les contraintes sémantiques fines que PostgreSQL ne peut pas exprimer. C'est une partition honnête de la vérité entre trois couches, chacune opérant dans son domaine de compétence.

---

### Turing (1912-1954) : La décidabilité et ses limites

Alan Turing répond à Hilbert différemment de Gödel. Son problème de l'arrêt (1936) démontre qu'il n'existe pas d'algorithme général capable de décider si un programme quelconque se terminera. La décidabilité complète est impossible : il n'existe pas de procédure mécanique universelle qui puisse répondre à toutes les questions bien formées sur le comportement d'un système.

Appliqué à notre problème, Turing nous dit qu'il n'existera jamais de schéma PostgreSQL capable de valider automatiquement toute la sémantique de métadonnées FAIR. La question n'est donc pas "comment mettre toute la vérité dans le schéma" mais "quelle partition de la vérité est raisonnable et soutenable entre le schéma, les données et l'application".

Turing contribue aussi directement à la notion de machine comme agent. Sa définition de la machine universelle pose qu'un processus computationnel peut être décrit comme un agent qui lit, transforme et écrit de l'information selon des règles. Un pipeline de calcul hydrologique est un agent turingien au sens plein du terme. Le traiter comme une `Person` avec des champs vides est une erreur conceptuelle, pas seulement une maladresse de modélisation.

---

### Liskov (1939-) : Le principe de substitution

Barbara Liskov formule en 1987 le principe qui porte son nom : dans un programme, un objet de type T peut être remplacé par un objet de sous-type S sans altérer les propriétés du programme. Un sous-type doit respecter le contrat de son type parent dans tous les contextes où ce type parent peut apparaître.

TPT viole ce principe de façon structurelle. La table parente `agent` définit un contrat implicite. Les tables filles `person` et `machine` sont censées en être des spécialisations substituables. Mais une machine ne peut pas se substituer à une personne dans tous les contextes : elle n'a pas d'ORCID, pas d'affiliation institutionnelle, elle ne peut pas signer un article. Et une personne ne peut pas se substituer à une machine : elle n'a pas de numéro de série, de version firmware, de fréquence d'échantillonnage.

La hiérarchie TPT crée une promesse de substituabilité que le domaine ne peut pas tenir. C'est un mensonge ontologique encodé dans le schéma.

TPC abandonne cette promesse. Il ne prétend pas que `Person` et `Machine` sont des sous-types d'un même `Agent`. Il reconnaît qu'ils jouent parfois le même rôle fonctionnel dans un contexte précis, sans postuler de relation d'héritage entre eux. C'est une position plus honnête, et elle respecte pleinement le principe de Liskov en refusant de promettre une substituabilité que le domaine ne peut pas garantir.

---

### Wittgenstein (1889-1951) : Le tournant décisif

Ludwig Wittgenstein est le philosophe le plus directement pertinent pour notre problème. Il faut distinguer ses deux périodes, car elles se contredisent sur l'essentiel, et cette contradiction est elle-même instructive.

#### Le Tractatus (1921) et ses limites

Le Tractatus Logico-Philosophicus pose que le langage est une image du monde. Chaque proposition bien formée est une image d'un fait atomique. Le monde est la totalité des faits. Et la proposition la plus célèbre de l'ouvrage : ce dont on ne peut pas parler, il faut le taire.

C'est la fondation philosophique de TPH et de tout schéma relationnel qui tente de capturer toute la sémantique dans sa structure formelle. On définit un langage formel (le schéma), on pose que chaque donnée valide est une proposition bien formée dans ce langage, et on suppose que le monde peut être entièrement représenté dans ce cadre.

Mais le Tractatus lui-même reconnaît sa propre limite. La structure logique du langage ne peut pas être dite dans ce même langage ; elle se montre. Un schéma ne peut pas exprimer sa propre sémantique dans ses propres termes. La signification de la colonne `agent_type` dans TPH ne peut pas être garantie par le schéma lui-même : elle se montre dans la documentation externe, dans les conventions tacites, dans la culture de l'équipe. Le premier Wittgenstein pointe déjà vers la limite de TPH sans la surmonter.

#### Les jeux de langage

Dans les Recherches Philosophiques (1953, posthume), Wittgenstein abandonne complètement l'idée d'un langage idéal formel. Il introduit le concept de **jeu de langage** : le sens d'un mot n'est pas une essence abstraite, c'est son usage dans une pratique concrète. Les mots n'ont pas de signification fixe et universelle ; ils ont des significations contextuelles, déterminées par les règles du jeu dans lequel ils sont employés.

"Agent" dans le contexte d'un chercheur qui remplit des métadonnées après une campagne de terrain n'est pas le même concept que "agent" dans le contexte d'un script qui ingère automatiquement des données capteurs à 10 Hz. Ce ne sont pas deux variantes du même jeu de langage. Ce sont deux jeux distincts, avec des règles différentes, des participants différents, et des responsabilités épistémiques différentes.

TPH fait l'erreur fondamentale de traiter ces deux jeux de langage comme un seul. Il les fusionne dans une table unique avec des colonnes qui n'ont de sens que dans l'un ou l'autre jeu, et espère que le discriminant `agent_type` suffira à les séparer à l'usage. Mais cette séparation est applicative, pas structurelle. Elle ne voyage pas avec les données. Elle n'est pas visible dans un export CSV. Elle suppose que le lecteur connaît déjà le jeu.

TPT commet la même erreur à un niveau supérieur. Il postule qu'il existe un jeu de langage parent dont humain et machine seraient des sous-jeux. Mais il n'existe pas de jeu de langage `agent` en hydrologie qui soit neutre entre humain et machine. Ce méta-jeu est une abstraction sans usage réel dans la pratique scientifique.

TPC reconnaît qu'il y a deux jeux de langage distincts. La table `person` et ses conventions constituent le jeu humain. La table `machine` et ses conventions constituent le jeu machine. La table cliente porte le discriminant `agentType` qui indique explicitement dans quel jeu on joue. C'est la modélisation structurellement honnête du problème.

#### Les ressemblances de famille

Le concept de **ressemblance de famille** est peut-être la contribution la plus directement applicable de Wittgenstein à notre problème de modélisation.

Wittgenstein observe qu'on ne peut pas toujours définir un concept par une propriété commune à tous ses membres. Prenons le concept de "jeu" : les jeux de plateau, les jeux de cartes, les jeux de balle, les jeux olympiques. Qu'ont-ils tous en commun ? Rien d'universel. Certains ont des gagnants, d'autres non. Certains impliquent de la chance, d'autres non. Certains sont compétitifs, d'autres coopératifs. Ce qui les relie, c'est un réseau de ressemblances qui se croisent et se chevauchent, comme les membres d'une famille qui se ressemblent sans partager un seul trait universel.

Un agent humain et un agent machine en hydrologie partagent certaines propriétés fonctionnelles : ils produisent des données, ils portent une responsabilité sur un batch, ils ont un identifiant dans le système. Mais il n'existe pas de propriété que tout agent humain et toute machine partagent nécessairement et qui ne soit pas partagée par d'autres entités du modèle. Leur ressemblance est fonctionnelle et contextuelle, pas essentielle.

Vouloir les unifier dans une table TPH avec une essence commune, c'est chercher une définition là où il n'y a qu'une ressemblance de famille. C'est une erreur philosophique avant d'être une erreur technique. Elle produit un schéma qui postule une essence inexistante et qui laisse des colonnes NULL comme témoins silencieux de cette imposture.

TPC modélise précisément une ressemblance de famille. Les deux types jouent le même rôle dans certains contextes sans partager d'essence commune. La relation polymorphique est la représentation structurelle de cette ressemblance, pas d'une hiérarchie ontologique.

#### La règle et son application

Le troisième apport décisif du second Wittgenstein concerne la notion de **règle**. Suivre une règle n'est pas un acte mécanique et déductif. Aucune règle ne contient en elle-même les instructions pour sa propre application dans tous les cas futurs. Suivre une règle est une pratique sociale, apprise par l'exemple et maintenue par la communauté qui l'utilise.

La conséquence pour notre problème est radicale. Aucune contrainte SQL, aussi sophistiquée soit-elle, ne peut garantir que les métadonnées FAIR seront correctement remplies dans tous les cas futurs que le modèle n'a pas anticipés. La cohérence des données de recherche n'est pas une propriété formelle du schéma. C'est une pratique communautaire, maintenue par la documentation, la formation, la revue par les pairs, et les conventions de la discipline scientifique.

Cela ne signifie pas qu'il faut abandonner les contraintes formelles. Cela signifie qu'on ne doit pas leur faire porter une responsabilité qu'elles ne peuvent pas assumer. Le schéma doit être aussi expressif que possible, et le reste de la vérité doit être porté explicitement par d'autres couches : les données elles-mêmes via des discriminants clairs, l'API via des validations documentées et testées, la communauté scientifique via ses standards et ses pratiques.

C'est l'argument le plus fort contre TPH : en cachant la sémantique dans le schéma et dans des conventions non écrites, TPH fait reposer la cohérence sur une règle implicite que personne ne peut lire dans les données. Un chercheur tiers qui reçoit un export CSV ne sait pas quelle règle s'applique. TPC rend la règle visible dans les données. `agentType = 'machine'` est une règle lisible, exportable, interprétable sans documentation externe du système d'origine.

---

## Partie III : Analyse technique des stratégies et de leurs alternatives

La philosophie a posé le cadre. Il faut maintenant vérifier que le choix philosophiquement fondé tient face aux contraintes réelles de PostgreSQL, des outils applicatifs, et des exigences FAIR opérationnelles. Cette section examine chaque stratégie et chaque alternative moderne sans concession sur leurs limites respectives.

---

### TPH : Table Per Hierarchy

#### Ce qu'elle fait

TPH crée une table unique qui contient tous les types possibles d'une famille conceptuelle. Un seul champ discriminant indique le type de chaque ligne. Les colonnes spécifiques à chaque type sont présentes pour toutes les lignes, remplies pour le type concerné et laissées NULL pour les autres.

```sql
CREATE TABLE agent (
    id             UUID PRIMARY KEY,
    agent_type     TEXT NOT NULL CHECK (agent_type IN ('person', 'machine')),
    name           TEXT NOT NULL,
    -- colonnes person
    first_name     TEXT,
    last_name      TEXT,
    orcid          TEXT,
    email          TEXT,
    -- colonnes machine
    serial_number  TEXT,
    model          TEXT,
    firmware       TEXT,
    manufacturer   TEXT
);
```

La FK depuis la table cliente est propre et native : `agent_id UUID REFERENCES agent(id)`.

#### Ce qu'elle fait philosophiquement

TPH est le programme de Hilbert appliqué à la modélisation : il suppose qu'un système formel unique peut capturer tous les types d'agents. Il cherche l'universel là où Wittgenstein a montré qu'il n'y a que des ressemblances de famille. Il fusionne deux jeux de langage distincts dans une même table en espérant que le discriminant suffira à les séparer à l'usage.

#### Pourquoi elle est écartée dans un contexte FAIR

Le problème n'est pas les NULL en eux-mêmes. PostgreSQL les stocke de façon compacte et leur impact en lecture est négligeable sur des tables de métadonnées de taille raisonnable. Le problème est sémantique.

Un export CSV d'une table TPH contient des colonnes dont la signification dépend du discriminant. Un chercheur tiers qui reçoit ce fichier voit une colonne `orcid` et une colonne `serial_number` côte à côte sur les mêmes lignes. Sans la documentation du schéma, il ne peut pas savoir que ces deux colonnes ne sont jamais remplies simultanément, ni comprendre pourquoi. La règle est implicite, non lisible dans les données : c'est la violation directe du principe wittgensteinien de la règle visible.

La contrainte FAIR la plus explicitement violée est Reusable : des données réutilisables doivent être compréhensibles sans système intermédiaire. Une table TPH ne satisfait pas cette exigence.

Par ailleurs, les contraintes d'intégrité interne à chaque type ne peuvent pas être exprimées proprement dans le schéma. Une contrainte `CHECK` peut vérifier qu'un `first_name` est rempli si `agent_type = 'person'`, mais ces contraintes croisées s'accumulent, deviennent fragiles à la maintenance, et ne sont pas documentées dans le schéma lui-même de façon lisible. Elles constituent une autre forme de règle implicite.

---

### TPT : Table Per Type

#### Ce qu'elle fait

TPT crée une table parente qui contient les attributs communs à tous les types, et des tables filles liées par FK qui contiennent les attributs spécifiques à chaque type. La table parente porte généralement le discriminant.

```sql
CREATE TABLE agent (
    id          UUID PRIMARY KEY,
    agent_type  TEXT NOT NULL CHECK (agent_type IN ('person', 'machine')),
    name        TEXT NOT NULL
);

CREATE TABLE agent_person (
    id         UUID PRIMARY KEY REFERENCES agent(id),
    first_name TEXT NOT NULL,
    last_name  TEXT NOT NULL,
    orcid      TEXT,
    email      TEXT
);

CREATE TABLE agent_machine (
    id            UUID PRIMARY KEY REFERENCES agent(id),
    serial_number TEXT,
    model         TEXT,
    firmware      TEXT,
    manufacturer  TEXT
);
```

La FK depuis la table cliente pointe vers `agent(id)`. Pour accéder aux attributs complets d'un agent, une jointure avec la table fille correspondante est nécessaire.

#### Ce qu'elle fait philosophiquement

TPT est la stratégie qui ressemble le plus à une solution correcte en surface. Elle reconnaît que les types ont des attributs distincts, les sépare dans des tables différentes, et conserve une FK propre depuis les tables clientes. Mais elle postule quelque chose que le domaine ne peut pas justifier : l'existence d'un universel `agent` suffisamment riche pour mériter une table dédiée avec ses propres attributs.

C'est l'erreur que Liskov pointe directement. La table `agent` définit un contrat implicite de substituabilité. Les tables filles sont censées être des sous-types qui respectent ce contrat. Mais une machine ne peut pas se substituer à une personne dans tous les contextes, et vice versa. La hiérarchie promet ce que le domaine ne peut pas tenir.

#### Pourquoi elle est écartée dans un contexte FAIR

TPT est la pire des trois stratégies pour l'export et la lisibilité externe, précisément parce qu'elle répartit les attributs d'une entité sur plusieurs tables. Un export de la table parente ne donne qu'un squelette : `id`, `agent_type`, `name`. Les attributs réels sont dans les tables filles, invisibles sans jointure.

Un export complet nécessite soit une vue matérialisée, soit une jointure explicite, soit deux fichiers distincts avec une clé de correspondance. Dans tous les cas, la compréhension de l'export requiert une connaissance préalable du schéma interne. C'est exactement ce que l'exigence Reusable de FAIR interdit.

Du point de vue des performances, TPT impose une jointure systématique à chaque lecture d'un agent complet. Sur des tables de métadonnées peu volumineuses, ce coût unitaire est négligeable, mais le pattern se répète à chaque endpoint de l'API, à chaque export, à chaque requête de diagnostic. Le coût cumulé est réel, et les bénéfices sont inexistants dans ce contexte.

Du point de vue des migrations, ajouter un troisième type d'agent impose de créer une table fille et de mettre à jour le discriminant de la table parente simultanément. La table parente devient un point de couplage entre tous les types, ce qui rigidifie l'évolution du modèle.

---

### TPC : Table Per Concrete type

#### Ce qu'elle fait

TPC supprime toute table parente. Chaque type concret a sa propre table indépendante avec l'intégralité de ses attributs. La table cliente référence un agent via deux colonnes : un discriminant de type et un identifiant. Il n'y a pas de FK native au sens PostgreSQL du terme.

```sql
CREATE TABLE person (
    id         UUID PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name  TEXT NOT NULL,
    orcid      TEXT,
    email      TEXT
);

CREATE TABLE machine (
    id            UUID PRIMARY KEY,
    name          TEXT NOT NULL,
    serial_number TEXT,
    model         TEXT,
    firmware      TEXT,
    manufacturer  TEXT
);

-- Dans la table cliente :
CREATE TABLE transformation_batch (
    id          UUID PRIMARY KEY,
    agent_type  TEXT NOT NULL CHECK (agent_type IN ('person', 'machine')),
    agent_id    UUID NOT NULL
    -- autres champs...
);
```

La résolution de l'agent se fait en deux temps : lire `agent_type` pour savoir quelle table interroger, puis requêter la bonne table avec `agent_id`.

#### Ce qu'elle fait philosophiquement

TPC est la traduction structurelle des ressemblances de famille wittgensteiniennes. Il reconnaît que `person` et `machine` sont deux entités distinctes qui jouent parfois le même rôle fonctionnel sans partager d'essence commune. Il ne promet pas de substituabilité (Liskov est respecté), ne fusionne pas des jeux de langage distincts (Wittgenstein est respecté), et ne postule pas d'universel inexistant (Russell est respecté).

Le discriminant `agent_type` porté dans la table cliente est la règle rendue visible dans la donnée elle-même. Un export CSV contient explicitement, sur chaque ligne, l'information du type de l'agent. La règle n'est plus implicite : elle est lisible sans documentation externe du système d'origine.

#### Les coûts réels et comment les gérer

TPC a un coût technique concret qu'il serait malhonnête de minimiser.

**La perte de l'intégrité référentielle native.** C'est le coût principal. PostgreSQL ne peut pas poser une contrainte `FOREIGN KEY` conditionnelle sur `agent_id` en fonction de `agent_type`. Une suppression de ligne dans `person` ne provoque pas d'erreur automatique si des `transformation_batch` y font référence. Ce trou doit être comblé explicitement.

La réponse appropriée dans un contexte de données de recherche est double. Les suppressions physiques ne devraient jamais se produire sur des données de recherche : on archive, on marque comme inactif, on déprécie. Un agent qui a produit des données ne peut pas disparaître sans laisser de trace ; c'est une exigence de traçabilité scientifique qui dépasse la simple intégrité référentielle SQL. Par ailleurs, des triggers de validation posés sur les tables clientes vérifient la cohérence du couple `(agent_type, agent_id)` à chaque insertion et mise à jour. Cette logique vit dans la base, pas seulement dans l'application.

**La complexité des requêtes transversales.** Lister tous les agents qui ont produit des batches sur une période donnée nécessite un `UNION ALL` entre les résultats pour chaque type. C'est verbeux et moins optimisable par le planificateur de requêtes PostgreSQL qu'une jointure classique.

```sql
SELECT 'person' AS agent_type, p.id,
       p.first_name || ' ' || p.last_name AS name
FROM transformation_batch tb
JOIN person p ON p.id = tb.agent_id AND tb.agent_type = 'person'
WHERE tb.applied_at > '2024-01-01'

UNION ALL

SELECT 'machine' AS agent_type, m.id, m.name
FROM transformation_batch tb
JOIN machine m ON m.id = tb.agent_id AND tb.agent_type = 'machine'
WHERE tb.applied_at > '2024-01-01';
```

Ce coût est réel mais circonscrit. Ces requêtes transversales portent sur des métadonnées, pas sur des données de mesure massives. Leur fréquence est faible et leur volume limité. Des vues encapsulent le `UNION ALL` pour simplifier l'interface applicative sans modifier la structure sous-jacente.

**La cohérence des identifiants.** Rien dans le schéma n'empêche qu'un `agent_id` soit un UUID valide dans `person` alors que `agent_type` vaut `machine`. Cette incohérence ne peut être détectée qu'à la résolution. Elle est peu probable en pratique si l'API est le seul point d'écriture, mais elle existe comme risque théorique et doit être couverte par les mesures de mitigation décrites dans la conclusion.

---

### Les alternatives modernes

Au-delà des trois stratégies classiques, plusieurs approches modernes ont été examinées. Aucune ne résout le problème de fond sans introduire d'autres compromis significatifs.

#### JSONB comme champ de débordement

L'approche consiste à créer une table `agent` légère avec les attributs communs et un discriminant, et à stocker les attributs spécifiques à chaque type dans un champ `JSONB`.

```sql
CREATE TABLE agent (
    id          UUID PRIMARY KEY,
    agent_type  TEXT NOT NULL CHECK (agent_type IN ('person', 'machine')),
    name        TEXT NOT NULL,
    attributes  JSONB
);
```

Un agent humain aurait dans `attributes` son ORCID et son email. Une machine y aurait son numéro de série et son firmware. La FK depuis les tables clientes est propre et native. Les index GIN permettent d'indexer les champs JSONB fréquemment interrogés.

Le problème est précisément wittgensteinien : JSONB déplace le schéma hors du schéma. Un `\d agent` dans psql ne dit plus ce qu'est un agent humain ou une machine. La structure des `attributes` est un jeu de langage privé que seule l'application connaît. Pour un DBA qui reprend le projet, pour un outil de documentation automatique, pour un chercheur qui interroge directement la base, la structure est opaque.

Dans un contexte FAIR où la compréhensibilité du modèle est une exigence de premier rang, JSONB aggrave le problème plutôt qu'il ne le résout. Il cache la sémantique dans un blob au lieu de la rendre visible dans le schéma ou dans les données. On perd la rigueur du schéma sans gagner la lisibilité des données. Des contraintes `CHECK` avec des fonctions de validation peuvent partiellement compenser cette opacité, mais elles ne sont pas lisibles dans le schéma standard et ne voyagent pas avec les exports.

#### Héritage PostgreSQL natif (`INHERITS`)

PostgreSQL propose un mécanisme d'héritage de tables via la clause `INHERITS`. Une table fille hérite de toutes les colonnes de la table parente et peut en ajouter de nouvelles.

```sql
CREATE TABLE agent (
    id    UUID PRIMARY KEY,
    name  TEXT NOT NULL
);

CREATE TABLE person (
    first_name TEXT NOT NULL,
    orcid      TEXT
) INHERITS (agent);

CREATE TABLE machine (
    serial_number TEXT,
    model         TEXT
) INHERITS (agent);
```

C'est séduisant en apparence, mais l'héritage PostgreSQL a des limitations documentées qui le rendent impraticable en production sérieuse. Les contraintes d'unicité sur la table parente ne s'appliquent pas aux lignes des tables filles. Les FK qui référencent la table parente ne voient pas les lignes insérées dans les tables filles. Les index sur la table parente ne couvrent pas les tables filles. Le support par les ORM, notamment Django ORM, est inexistant ou marginal.

En pratique, l'héritage PostgreSQL a été conçu pour le partitionnement physique de grandes tables, pas pour exprimer des hiérarchies de types sémantiques. L'utiliser comme substitut à TPT reviendrait à superposer un outil de partitionnement sur un problème ontologique. Les garanties d'intégrité que TPT offre théoriquement disparaissent, sans que les avantages de TPC soient obtenus.

#### Tables de liaison polymorphiques intermédiaires

Une variante parfois proposée consiste à créer une table de liaison explicite entre la table cliente et les types concrets, plutôt que de porter le discriminant directement dans la table cliente.

```sql
CREATE TABLE batch_agent (
    batch_id    UUID NOT NULL REFERENCES transformation_batch(id),
    agent_type  TEXT NOT NULL CHECK (agent_type IN ('person', 'machine')),
    agent_id    UUID NOT NULL
);
```

Cette approche n'apporte rien de fondamental par rapport à TPC direct. Elle ajoute une table et une jointure supplémentaires sans résoudre le problème de l'intégrité référentielle native, sans rendre les données plus lisibles, et sans simplifier les requêtes. Elle fragmente l'information de provenance sur deux tables là où elle pourrait tenir sur deux colonnes de la table cliente. Elle pourrait avoir un intérêt si une ressource devait référencer plusieurs agents simultanément de types différents, mais dans le cas standard d'un agent unique par action, c'est une complexité sans bénéfice.

#### Bases de données alternatives : DuckDB et triplestores

DuckDB, qui supporte nativement les types union discriminés dans le format Parquet, serait philosophiquement proche de la solution idéale. Un type `Agent = Person | Machine` y serait un type de première classe, visible dans le schéma du fichier, sans discriminant implicite. Mais DuckDB est une base analytique OLAP mono-writer. Il n'a pas de driver Django stable, ne supporte pas l'écriture concurrente, et son écosystème ORM est embryonnaire. Il est pertinent comme format de diffusion des données (export Parquet auto-descriptif), pas comme moteur de stockage transactionnel pour une API en production.

Les triplestores RDF éliminent le problème différemment : il n'y a pas de table `agent`, seulement des noeuds typés par `foaf:Person` ou `prov:SoftwareAgent` dans un graphe de triplets. Le polymorphisme disparaît comme question parce que la notion de "table dans laquelle ranger une entité" n'existe plus. Mais les performances analytiques sur des volumes importants sont très inférieures à PostgreSQL, l'écosystème applicatif est immature, et le coût opérationnel est significatif. Ils restent pertinents comme couche d'exposition sémantique des métadonnées, pas comme moteur de stockage principal.

---

### Tableau de synthèse

| Critère                                       | TPH    | TPT      | TPC       | JSONB  | `INHERITS` PG |
|-----------------------------------------------|--------|----------|-----------|--------|---------------|
| FK native propre                              | oui    | oui      | non       | oui    | non fiable    |
| Intégrité référentielle garantie              | oui    | oui      | triggers  | oui    | non           |
| Export CSV auto-descriptif                    | non    | non      | oui       | non    | partiel       |
| Schéma lisible sans documentation externe     | non    | partiel  | oui       | non    | non           |
| Requêtes transversales simples                | oui    | jointure | UNION ALL | oui    | non fiable    |
| Alignement Liskov                             | non    | non      | oui       | non    | non           |
| Alignement FAIR (Reusable)                    | faible | faible   | fort      | faible | faible        |
| Cohérence avec pattern polymorphique existant | non    | non      | oui       | non    | non           |
| Support ORM Django                            | natif  | natif    | manuel    | natif  | inexistant    |

---

## Conclusion : Pour une adoption massive et raisonnée de TPC

### 1. Le lien entre résolution philosophique et choix technique

Le fil conducteur de ce document n'est pas une succession de références philosophiques venant habiller a posteriori un choix technique déjà arrêté. C'est le mouvement inverse : la philosophie révèle pourquoi certaines solutions de modélisation sont structurellement condamnées, indépendamment de leur confort d'implémentation à court terme.

Frege a montré que sens et référence sont deux choses distinctes. Un bon modèle de données doit rendre visible ce que les données signifient, pas seulement ce à quoi elles réfèrent. Une table TPH avec un discriminant implicite stocke des références sans en porter le sens. Un export de cette table est sémantiquement muet.

Russell a montré qu'on ne peut pas mélanger impunément des objets de types logiques différents dans le même ensemble. TPH construit exactement cet ensemble dangereux. TPT le corrige en apparence, mais postule une hiérarchie dont la table parente n'a pas d'usage réel dans le domaine.

Gödel a montré qu'aucun système formel ne peut capturer toute la vérité sémantique d'un domaine suffisamment expressif. Chercher à tout mettre dans le schéma PostgreSQL est le programme de Hilbert appliqué aux bases de données, et il échoue pour les mêmes raisons. La bonne réponse n'est pas un schéma plus contraignant, c'est une partition consciente de la vérité entre les couches du système.

Liskov a montré que la substituabilité est un contrat, pas une décoration. TPT promet ce contrat sans pouvoir le tenir. TPC renonce à cette promesse et dit la vérité : deux types distincts jouent parfois le même rôle fonctionnel. Ce n'est pas une hiérarchie, c'est une ressemblance de famille au sens de Wittgenstein.

Wittgenstein a fourni les outils conceptuels les plus précis pour nommer le problème. Les jeux de langage montrent que "agent humain" et "agent machine" ne sont pas deux variantes d'un même concept, mais deux pratiques distinctes avec des règles, des participants et des responsabilités épistémiques différentes. Les ressemblances de famille montrent qu'ils partagent un rôle fonctionnel sans partager d'essence. La règle et son application montrent que la cohérence sémantique ne peut pas être entièrement formalisée dans un schéma : elle doit être rendue visible dans les données elles-mêmes pour être praticable par des tiers.

TPC est la traduction directe de ces leçons en décision de modélisation. Il ne prétend pas capturer toute la vérité dans le schéma. Il porte le discriminant dans la donnée pour que la sémantique soit auto-portée. Il partitionne la vérité entre trois couches dont chacune opère dans son domaine de compétence : le schéma exprime la structure, les données portent le type, l'API valide les contraintes sémantiques que PostgreSQL ne peut pas exprimer formellement. Cette partition n'est pas un aveu de faiblesse. C'est la seule réponse honnête à l'incomplétude de Gödel appliquée aux systèmes d'information.

Dans un modèle de données FAIR destiné à la recherche, adopter TPC massivement n'est donc pas un choix pragmatique par défaut. C'est un choix architectural cohérent avec ce que FAIR exige réellement : que les données soient compréhensibles, réutilisables et interprétables indépendamment du système qui les a produites.

---

### 2. Règles de décision : quand appliquer TPC, quand ne pas l'appliquer

TPC n'est pas universel. Son adoption doit être guidée par des critères précis, pas par une conviction idéologique.

**Appliquer TPC quand :**

Les types cibles sont ontologiquement distincts, c'est-à-dire qu'ils ne partagent pas d'essence commune justifiant une table parente, seulement un rôle fonctionnel dans un contexte précis. La question à se poser est : si on retire le contexte dans lequel ils jouent le même rôle, ont-ils encore quoi que ce soit en commun ? Si la réponse est non, TPC est indiqué.

Les attributs spécifiques à chaque type sont nombreux et structurellement différents. Si les colonnes NULL dans une table TPH représenteraient plus de 30 à 40 % des données pour certains types, l'incohérence structurelle est trop visible pour être ignorée.

La sémantique doit voyager avec les données. Chaque fois qu'un export CSV, un fichier Parquet ou une réponse API doit être interprétable sans documentation externe du schéma, TPC est indiqué. C'est le critère FAIR Reusable appliqué au modèle lui-même.

Les types constituent un ensemble fermé ou lentement évolutif. TPC supporte bien un ensemble de types stable et contrôlé par des enums explicites. Si de nouveaux types doivent pouvoir être ajoutés fréquemment sans migration, d'autres approches méritent d'être considérées.

Le modèle utilise déjà le pattern polymorphique ailleurs. La cohérence architecturale est un critère à part entière. Un modèle où TPC est appliqué uniformément est un modèle dont les conventions s'apprennent une fois et s'appliquent partout. Une incohérence locale coûte plus cher à long terme que la complexité d'une migration ponctuelle.

**Ne pas appliquer TPC quand :**

Les types partagent une essence commune riche et stable, avec de nombreux attributs partagés et peu d'attributs spécifiques. Si les colonnes communes représentent 80 % du schéma et que les spécialisations sont marginales, TPH avec un discriminant explicite et des contraintes CHECK est suffisant et plus simple à maintenir.

L'intégrité référentielle native est une contrainte non négociable et aucune politique de suppression logique n'est en place. Dans un système transactionnel généraliste où des suppressions physiques sont courantes et où les triggers de validation ne peuvent pas être garantis, la perte de la FK native de TPC représente un risque inacceptable.

Les requêtes transversales sur tous les types sont fréquentes, massives et critiques pour les performances. Si l'application doit régulièrement agréger ou filtrer sur l'ensemble des types sans distinction, le coût des `UNION ALL` peut devenir prohibitif. Ce cas est rare dans un modèle de métadonnées, mais courant dans un modèle de données opérationnelles à fort volume.

**Le cas intermédiaire : TPH localisé dans un contexte TPC global.**

Il existe une situation où TPH reste défendable même dans un modèle globalement TPC : lorsque deux types partagent un rôle fonctionnel identique, que leurs attributs spécifiques sont peu nombreux, et que la distinction entre eux n'a pas de valeur épistémique propre dans les exports. Une table de responsabilité fonctionnelle qui accepte une personne ou une organisation, avec deux FK optionnelles dont l'une est obligatoirement remplie, en est un exemple typique. Les attributs communs (rôle, ressource cible, dates de validité) dominent largement les attributs spécifiques. Dans ce cas, TPH localisé avec une contrainte applicative explicitement documentée est un compromis défendable, à condition que la règle soit visible et que la documentation soit maintenue activement.

---

### 3. Mesures techniques pour mitiger les risques de TPC en PostgreSQL

Adopter TPC massivement impose de compenser explicitement ce que PostgreSQL ne peut plus garantir nativement. Ces mesures ne sont pas optionnelles : sans elles, TPC crée des trous d'intégrité réels.

**Valider le discriminant à l'écriture par contrainte CHECK.**

La première ligne de défense est une contrainte `CHECK` sur le discriminant pour qu'il ne puisse prendre que des valeurs connues et contrôlées.

```sql
ALTER TABLE transformation_batch
ADD CONSTRAINT chk_agent_type
CHECK (agent_type IN ('person', 'machine'));
```

Cette contrainte est insuffisante à elle seule (elle ne vérifie pas que `agent_id` est cohérent avec `agent_type`) mais elle empêche l'introduction de valeurs arbitraires dans le discriminant.

**Valider la cohérence du couple `(agent_type, agent_id)` par trigger.**

Un trigger `BEFORE INSERT OR UPDATE` vérifie que l'identifiant référencé existe bien dans la table correspondant au type déclaré. C'est le substitut direct de la FK native.

```sql
CREATE OR REPLACE FUNCTION check_agent_reference()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.agent_type = 'person' THEN
        IF NOT EXISTS (SELECT 1 FROM person WHERE id = NEW.agent_id) THEN
            RAISE EXCEPTION 'agent_id % ne correspond à aucune person', NEW.agent_id;
        END IF;
    ELSIF NEW.agent_type = 'machine' THEN
        IF NOT EXISTS (SELECT 1 FROM machine WHERE id = NEW.agent_id) THEN
            RAISE EXCEPTION 'agent_id % ne correspond à aucune machine', NEW.agent_id;
        END IF;
    ELSE
        RAISE EXCEPTION 'agent_type inconnu : %', NEW.agent_type;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_check_agent_reference
BEFORE INSERT OR UPDATE ON transformation_batch
FOR EACH ROW EXECUTE FUNCTION check_agent_reference();
```

Ce trigger doit être posé sur chaque table cliente portant un couple `(agent_type, agent_id)`. Il est la seule garantie d'intégrité référentielle en l'absence de FK native.

**Interdire les suppressions physiques sur les tables référencées.**

La suppression physique d'une `Person` ou d'une `Machine` référencée ne peut pas être interceptée par une FK absente. La réponse architecturale est d'interdire les suppressions physiques par convention et par contrainte dans la base elle-même.

```sql
CREATE OR REPLACE FUNCTION prevent_physical_delete()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION
        'Suppression physique interdite sur %. Utiliser archived_at pour archiver.',
        TG_TABLE_NAME;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_prevent_person_delete
BEFORE DELETE ON person
FOR EACH ROW EXECUTE FUNCTION prevent_physical_delete();

CREATE TRIGGER trg_prevent_machine_delete
BEFORE DELETE ON machine
FOR EACH ROW EXECUTE FUNCTION prevent_physical_delete();
```

Le même trigger doit être posé sur toutes les tables concrètes référencées par des relations TPC. La désactivation d'une entité passe par un champ `archived_at` ou `status`, jamais par une suppression physique.

**Encapsuler les requêtes transversales dans des vues.**

Les `UNION ALL` nécessaires pour naviguer sur l'ensemble des agents ne doivent pas être répétés dans chaque endpoint de l'API. Des vues encapsulent cette logique une fois pour toutes.

```sql
CREATE VIEW agent_view AS
    SELECT id, 'person' AS agent_type,
           first_name || ' ' || last_name AS display_name,
           email, orcid,
           NULL AS serial_number, NULL AS model
    FROM person
    WHERE archived_at IS NULL

    UNION ALL

    SELECT id, 'machine' AS agent_type,
           name AS display_name,
           NULL AS email, NULL AS orcid,
           serial_number, model
    FROM machine
    WHERE archived_at IS NULL;
```

Cette vue est un outil de lecture, pas une table d'écriture. Elle simplifie les requêtes analytiques et les endpoints de navigation sans modifier la structure sous-jacente.

**Documenter le contrat polymorphique dans le schéma lui-même.**

Les commentaires PostgreSQL sur les colonnes `agent_type` et `agent_id` doivent être traités comme une contrainte de projet, pas comme une option éditoriale.

```sql
COMMENT ON COLUMN transformation_batch.agent_type IS
    'Type de l''agent producteur. Valeurs valides : person, machine.
     Détermine la table cible de agent_id.
     Intégrité garantie par le trigger trg_check_agent_reference.';

COMMENT ON COLUMN transformation_batch.agent_id IS
    'UUID de l''agent producteur dans la table désignée par agent_type.
     Pas de FK native : voir trigger trg_check_agent_reference.';
```

Ces commentaires sont lisibles par `\d+` dans psql, par les outils de documentation automatique, et par tout outil d'inspection du schéma. Ils rendent le contrat implicite de TPC explicite au niveau du schéma lui-même, ce qui est cohérent avec l'exigence de lisibilité FAIR appliquée au modèle.

**Centraliser toute écriture sur l'API.**

Les mesures précédentes réduisent le risque mais ne l'éliminent pas entièrement. La dernière ligne de défense est architecturale : aucune écriture directe en base ne doit être possible en dehors de l'API. Les accès directs à PostgreSQL sont restreints aux rôles de lecture pour les utilisateurs applicatifs, et aux rôles d'administration pour les opérations de maintenance. La couverture de tests de l'API doit inclure explicitement les cas d'incohérence du couple `(agent_type, agent_id)`.

**Vérifier l'intégrité périodiquement par des requêtes de cohérence.**

Même avec les mesures précédentes, une requête de vérification doit être exécutée périodiquement pour détecter toute incohérence qui aurait pu passer entre les mailles des triggers.

```sql
-- Détecter les références orphelines dans transformation_batch
SELECT tb.id, tb.agent_type, tb.agent_id, 'orphelin' AS statut
FROM transformation_batch tb
WHERE
    (tb.agent_type = 'person'
        AND NOT EXISTS (SELECT 1 FROM person  WHERE id = tb.agent_id))
 OR (tb.agent_type = 'machine'
        AND NOT EXISTS (SELECT 1 FROM machine WHERE id = tb.agent_id));
```

Ce type de requête doit exister pour chaque table cliente portant une relation TPC. Son résultat doit être loggué et déclencher une alerte si des lignes sont retournées.

---

### Synthèse

Adopter TPC massivement dans un modèle de données FAIR pour la recherche hydrologique n'est pas une dérive vers la complexité. C'est une décision architecturale fondée sur une analyse rigoureuse de ce que le domaine exige et de ce qu'un schéma relationnel peut honnêtement garantir.

Le problème philosophique posé par Gödel et Wittgenstein ne disparaît pas en choisissant une autre stratégie. Il est simplement déplacé : vers des colonnes NULL silencieuses avec TPH, vers des jointures qui cachent la structure réelle avec TPT, vers des blobs opaques avec JSONB. TPC est la seule stratégie qui le traite explicitement, en rendant la vérité lisible dans les données elles-mêmes.

Les risques techniques introduits par la perte de la FK native sont réels mais circonscrits. Ils se mitigent par une combinaison de triggers de validation, d'interdiction des suppressions physiques, de vues d'encapsulation, de commentaires de schéma, de centralisation des écritures sur l'API et de vérifications périodiques d'intégrité. Aucune de ces mesures n'est conceptuellement difficile. Leur mise en place est un investissement initial qui se rembourse à chaque export, à chaque réingestion de données par un tiers, et à chaque chercheur qui lit un CSV sans avoir à consulter la documentation du schéma pour comprendre ce qu'il lit.

C'est précisément ce que FAIR demande.

Des moteurs alternatifs comme TypeDB résoudraient le problème polymorphique nativement : leur système de types somme permet de déclarer qu'un agent est soit une personne soit une machine comme une propriété du schéma lui-même, avec une garantie d'intégrité moteur que PostgreSQL ne peut pas offrir sur une FK en deux colonnes. Sur le plan philosophique, c'est la réponse correcte. Sur le plan opérationnel, ces moteurs n'ont pas aujourd'hui la maturité nécessaire pour des données scientifiques à long terme : pas d'ORM stable, pas d'écosystème Django ou FastAPI, pas d'équivalent à TimescaleDB pour les séries temporelles, et une communauté trop restreinte pour garantir la pérennité sur 20 ou 30 ans. Le choix de rester sur PostgreSQL n'est donc pas un renoncement philosophique. C'est une décision d'ingénierie lucide : accepter une limite structurelle connue du modèle relationnel, la compenser par des mesures explicites et auditables, et attendre que des moteurs philosophiquement plus corrects atteignent la maturité opérationnelle que des données de recherche exigent.
