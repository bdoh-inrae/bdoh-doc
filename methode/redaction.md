# Règles de rédaction

Comment écrire dans ce dépôt : formalisme du modèle, mise en forme, et manière
de présenter une modification avant de l'appliquer.

Ce fichier ne dit pas quoi écrire (`modele/modele_donnees.md`), ni pourquoi
(`modele/decisions.md`), ni comment penser (`methode/SOUL.md`).


## Montrer avant d'écrire

Toute modification d'un tableau d'entité est présentée en avant et après, dans
la réponse, alignée, avant d'être appliquée. Louis valide sur ce qu'il voit, pas
sur la description de ce qui va être fait.

Corollaire pour les passes larges : quand une passe touche des dizaines de
tableaux, montrer un cas représentatif et le pire cas, plus une mesure de ce que
la passe change globalement. Et prouver, avant d'écrire, que le contenu des
cellules est inchangé.


## Une passe, un sujet

Une correction de mise en forme et une modification de fond ne sont jamais dans
la même passe ni dans le même commit. Sinon le diff devient illisible et il
n'est plus possible de voir ce qui a réellement changé.

Un déplacement de fichier et une modification de son contenu se séparent de la
même façon, à une exception près : la mise à jour des chemins qu'un déplacement
rend obligatoire fait partie du déplacement, sans quoi le dépôt reste incohérent
entre deux commits.


## Structure du modèle

Formalisme strict pour `modele/modele_donnees.md`.

Les tableaux de colonnes ne contiennent que des **colonnes réelles** de la table
SQL correspondante. Les relations portées par des tables de jointure séparées
(many-to-many, TPC series) ne figurent jamais dans le tableau de l'entité
parente : elles sont documentées dans la note de l'entité et dans la table des
jointures explicites.

Conventions de nommage (tables, colonnes, enums, valeurs de Keyword) : voir la
section *Conventions de nommage* de `modele/modele_donnees.md`, qui en est le
propriétaire. Ne pas les ressaisir ici.

En-tête d'entité, format standard à respecter :

```
### NomEntité
> Mini-définition en une ligne.

Aligné avec : standard1, standard2
Utilisé par : Entite1 (champ), Entite2 (champ)
Relations inverses (requêter par resourceType='X') : Table1, Table2
Note : rôle, contraintes, valeurs courantes si keyword.
```


## Tableaux Markdown

La règle est appliquée par `outils/mdtable.py`, pas par la vigilance. Sur 111
tableaux, la vigilance humaine ne tient pas : la mesure d'août 2026 en trouvait
26 corrects.

```bash
python3 outils/mdtable.py check <fichier.md>   # signale
python3 outils/mdtable.py fix   <fichier.md>   # corrige
```

La règle elle-même, en trois temps :

1. Chaque colonne prend la largeur de sa cellule la plus large, et toutes les
   lignes sont paddées à cette largeur. Les barres verticales forment une
   grille.
2. Si le tableau dépasse **150 caractères**, largeur utile d'une ligne dans
   l'éditeur, la colonne la plus large est ramenée à la place restante. C'est
   presque toujours la dernière (les valeurs possibles), mais pas toujours :
   dans une table d'index, c'est une colonne du milieu qui enfle.
3. Les cellules trop longues de cette colonne sortent de la grille et font
   déborder leur ligne, **seules**. Cette ligne se replie dans l'éditeur, les
   autres non.

Le point 3 est l'arbitrage qui compte, et il découle d'un constat d'usage :
c'est une ou deux lignes qui explosent, pas le tableau. Élargir toute la colonne
pour ces deux lignes rendrait le tableau entier illisible ; les laisser déborder
seules reste lisible.

**Le contenu ne se raccourcit jamais pour tenir dans la grille.** Ni troncature,
ni abréviation, ni valeur retirée d'une énumération. La qualité du contenu prime
sur la mise en page, sans exception. Si une ligne déborde parce que les valeurs
possibles sont nombreuses, elle déborde : c'est normal et attendu.

L'ancienne rédaction de cette règle se contredisait (elle demandait à la fois de
padder jusqu'à la ligne la plus large et de tolérer qu'une ligne dépasse, ce qui
est impossible en même temps). C'était D11 dans `modele/chantier.md`.


## Ponctuation

Pas de tiret cadratin (—) ni demi-cadratin (–). Utiliser les deux-points, des
parenthèses, ou reformuler. Le double tiret ` -- ` n'est pas une échappatoire :
c'est une troisième convention, elle a été retirée du projet en août 2026.

Titres portant un identifiant : le point, pas le tiret. `## ADR-001. Titre`,
`## D1. Titre`.


## Cohérence interne

Avant de clore une passe sur le modèle :

```bash
python3 outils/verifie_modele.py
```

Cinq contrôles : cible de FK inexistante, mention `(FK x)` dont la colonne
n'existe pas, valeur de discriminant hors du domaine déclaré, entité portant un
discriminant sans figurer dans l'index de son pattern, renvoi de fichier mort.
Aucun ne juge le fond : ils vérifient que le modèle dit la même chose partout où
il se cite lui-même.

Les domaines de référence et les index de patterns sont lus **dans** le modèle,
jamais codés en dur dans l'outil : le modèle reste la seule source de vérité.


## Toute modification du modèle cite ce qui l'autorise

Un ADR, un constat de `modele/chantier.md`, ou une demande explicite. Si rien ne
l'autorise, c'est qu'il faut d'abord ouvrir une décision. Une correction qui
n'est rattachable à rien est soit une divergence non identifiée (elle mérite un
`D`), soit un changement de fond déguisé.


## Mode d'édition

- Modification mineure (un champ, une ligne) : l'indiquer et laisser Louis
  éditer dans son propre éditeur.
- Modification large (plusieurs entités, passe transversale) : édition
  programmatique par script, avec vérification avant et après.
