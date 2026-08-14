#!/usr/bin/env python3
"""Verifie (et corrige) l'alignement visuel des tableaux Markdown.

Usage :
    mdtable.py check <fichier.md> [...]   liste les tableaux mal alignes
    mdtable.py fix   <fichier.md> [...]   reecrit les tableaux alignes

Options :
    --largeur N    largeur cible d'une ligne de tableau (defaut 153)

Regle appliquee, en deux temps.

1. Chaque colonne prend la largeur de sa cellule la plus large, et toutes les
   lignes sont paddees a cette largeur. Les barres verticales forment donc une
   grille.

2. Si le tableau depasse alors la largeur cible, seule la DERNIERE colonne est
   ramenee a la place restante. Les cellules de cette colonne qui depassent
   sortent de la grille et font deborder leur ligne, seules ; les autres restent
   paddees, donc la barre de droite reste alignee pour la majorite des lignes.

Ce compromis vient d'un constat d'usage : c'est presque toujours la derniere
colonne (les valeurs possibles) qui explose, sur une ou deux lignes. Elargir
toute la colonne pour ces deux lignes rendrait le tableau entier illisible ;
laisser ces deux lignes deborder seules reste lisible.

Aucun contenu n'est jamais tronque, reformule ni appauvri : la qualite du
contenu prime sur la mise en page.
"""

import sys
import unicodedata

FENCE = ("```", "~~~")

LARGEUR_CIBLE = 153   # largeur d'une ligne dans l'editeur, sans repli
PLANCHER = 20         # largeur minimale laissee a la derniere colonne


def width(s):
    """Largeur d'affichage en colonnes de terminal."""
    w = 0
    for ch in s:
        if unicodedata.combining(ch):
            continue
        w += 2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1
    return w


def split_row(line):
    """Decoupe une ligne de tableau en cellules, en respectant \\| echappe."""
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|") and not s.endswith("\\|"):
        s = s[:-1]
    cells, cur, i = [], [], 0
    while i < len(s):
        if s[i] == "\\" and i + 1 < len(s):
            cur.append(s[i:i + 2])
            i += 2
            continue
        if s[i] == "|":
            cells.append("".join(cur))
            cur = []
            i += 1
            continue
        cur.append(s[i])
        i += 1
    cells.append("".join(cur))
    return [c.strip() for c in cells]


def is_sep(cells):
    return bool(cells) and all(
        c and set(c) <= set(":- ") and "-" in c for c in cells
    )


def find_tables(lines):
    """Retourne [(debut, fin_exclue, [lignes])] pour chaque tableau, hors code."""
    tables, i, in_fence = [], 0, None
    while i < len(lines):
        stripped = lines[i].lstrip()
        if in_fence:
            if stripped.startswith(in_fence):
                in_fence = None
            i += 1
            continue
        if stripped.startswith(FENCE):
            in_fence = stripped[:3]
            i += 1
            continue
        if "|" in lines[i] and i + 1 < len(lines) and is_sep(split_row(lines[i + 1])):
            start = i
            i += 2
            while i < len(lines) and "|" in lines[i] and lines[i].strip():
                i += 1
            tables.append((start, i, lines[start:i]))
            continue
        i += 1
    return tables


def largeurs(rows, ncols, cible=LARGEUR_CIBLE):
    """Largeur de chaque colonne : maximum des cellules, la plus large rabotee.

    Voir la regle en tete de fichier. La ligne de separation ne contraint pas la
    largeur : c'est elle qui suit, pas l'inverse.

    Quand le tableau depasse la largeur cible, on rabote la colonne la PLUS
    LARGE, pas la derniere. C'est presque toujours la derniere en pratique (la
    colonne des valeurs possibles), mais pas toujours : dans une table d'index,
    c'est une colonne du milieu qui enfle. Raboter la derniere dans ce cas
    allongeait toutes les lignes au lieu de les raccourcir.
    """
    w = [0] * ncols
    for n, r in enumerate(rows):
        if n == 1:
            continue
        for c, cell in enumerate(r):
            if c < ncols:
                w[c] = max(w[c], width(cell))
    if ncols < 2:
        return w
    marge = 3 * ncols + 1           # "| " et " " par colonne, plus la barre finale
    while sum(w) + marge > cible:
        c = w.index(max(w))
        if w[c] <= PLANCHER:
            break                   # plus rien a raboter, le tableau debordera
        exces = sum(w) + marge - cible
        w[c] = max(PLANCHER, w[c] - exces)
    return w


def render(rows, aligns, cible=LARGEUR_CIBLE):
    widths = largeurs(rows, len(aligns), cible)
    out = []
    for n, r in enumerate(rows):
        if n == 1:
            parts = []
            for c, w in enumerate(widths):
                a = aligns[c]
                if a == "left":
                    parts.append(":" + "-" * (w + 1))
                elif a == "right":
                    parts.append("-" * (w + 1) + ":")
                elif a == "center":
                    parts.append(":" + "-" * w + ":")
                else:
                    parts.append("-" * (w + 2))
            out.append("|" + "|".join(parts) + "|")
            continue
        parts = []
        for c, w in enumerate(widths):
            cell = r[c] if c < len(r) else ""
            parts.append(" " + cell + " " * (w - width(cell)) + " ")
        ligne = "|" + "|".join(parts) + "|"
        # Une ligne qui deborde deja n'a rien a gagner a etre paddee jusqu'au
        # bout : la barre de droite ne s'alignera de toute facon pas. On retire
        # le remplissage de sa derniere cellule pour ne pas l'allonger en pure
        # perte. Les lignes qui tiennent gardent leur bord droit aligne.
        if width(ligne) > cible:
            ligne = ligne[:-1].rstrip() + " |"
        out.append(ligne)
    return out


def analyse(path, cible=LARGEUR_CIBLE):
    lines = open(path, encoding="utf-8").read().split("\n")
    problems, fixed, changed = [], list(lines), False
    for start, end, block in find_tables(lines):
        rows = [split_row(l) for l in block]
        ncols = len(rows[0])
        aligns = []
        for c in rows[1]:
            l, r = c.startswith(":"), c.endswith(":")
            aligns.append(
                "center" if l and r else "left" if l else "right" if r else "none"
            )
        ragged = [n for n, r in enumerate(rows) if len(r) != ncols]
        new = render(rows, aligns, cible)
        misaligned = new != [l.rstrip() for l in block]
        if ragged or misaligned:
            debords = [
                start + 1 + n
                for n, l in enumerate(new)
                if n != 1 and width(l) > cible
            ]
            problems.append(
                {
                    "line": start + 1,
                    "cols": ncols,
                    "rows": len(rows),
                    "ragged": [start + 1 + n for n in ragged],
                    "misaligned": misaligned,
                    "debords": debords,
                }
            )
        if new != [l.rstrip() for l in block]:
            fixed[start:end] = new
            changed = True
    return problems, fixed, changed


def main():
    args = [a for a in sys.argv[1:]]
    cible = LARGEUR_CIBLE
    if "--largeur" in args:
        i = args.index("--largeur")
        cible = int(args[i + 1])
        del args[i:i + 2]
    if len(args) < 2 or args[0] not in ("check", "fix"):
        print(__doc__)
        return 2
    mode, paths = args[0], args[1:]
    total_tables = total_bad = 0
    for p in paths:
        problems, fixed, changed = analyse(p, cible)
        lines = open(p, encoding="utf-8").read().split("\n")
        n = len(find_tables(lines))
        total_tables += n
        total_bad += len(problems)
        if problems:
            print(f"\n{p} : {len(problems)} tableau(x) a corriger sur {n}")
            for pr in problems:
                tag = []
                if pr["ragged"]:
                    tag.append(f"lignes a nombre de cellules different : {pr['ragged']}")
                if pr["misaligned"]:
                    tag.append("colonnes non alignees")
                print(f"  ligne {pr['line']:>5} ({pr['cols']} col.) : {' ; '.join(tag)}")
        if mode == "fix" and changed:
            open(p, "w", encoding="utf-8").write("\n".join(fixed))
            print(f"{p} : reecrit")
    print(f"\nTotal : {total_bad} tableau(x) a corriger sur {total_tables}")
    return 1 if total_bad else 0


if __name__ == "__main__":
    sys.exit(main())
