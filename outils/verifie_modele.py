#!/usr/bin/env python3
"""Verifie la coherence interne du modele de donnees BDOH.

Usage :
    verifie_modele.py [--racine DOSSIER] [--modele FICHIER]

Cinq controles. Aucun ne juge le fond : ils verifient seulement que le modele
dit la meme chose partout ou il se cite lui-meme.

  1. FK sans cible        une colonne "-> X" ou X n'est pas une entite du modele
  2. FK fantome           un "Entite (FK colonne)" ou l'entite citee n'a pas
                          cette colonne
  3. domaine TPC          une valeur de discriminant hors du domaine de
                          reference declare pour ce discriminant
  4. index de pattern     une entite porte un discriminant sans figurer dans
                          l'index de son pattern, ou l'inverse
  5. renvoi de fichier    un `fichier.md` cite entre accents graves qui n'existe
                          nulle part dans le depot

Les domaines de reference et les index de patterns ne sont PAS codes en dur :
ils sont lus dans le modele lui-meme, qui reste la seule source de verite. Le
jour ou un domaine change, l'outil suit sans etre modifie.

Sortie : 0 si tout est coherent, 1 sinon.
"""

import os
import re
import sys

IGNORE_DIRS = {".git", "archives", "__pycache__", "site", ".github"}


# ---------------------------------------------------------------- lecture

def trouve_modele(racine):
    """Le modele est le fichier qui porte la section des patterns transversaux."""
    for chemin in fichiers(racine, (".md",)):
        if "/docs/" in chemin.replace(os.sep, "/"):
            continue
        with open(chemin, encoding="utf-8", errors="replace") as f:
            tete = f.read(20000)
        if "# Patterns transversaux" in tete:
            return chemin
    return None


def fichiers(racine, suffixes):
    for base, dirs, noms in os.walk(racine):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for n in sorted(noms):
            if n.endswith(suffixes) and not n.endswith("~"):
                yield os.path.join(base, n)


def cellules(ligne):
    """Decoupe une ligne de tableau, en respectant les barres echappees."""
    s = ligne.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|") and not s.endswith("\\|"):
        s = s[:-1]
    out, cur, i = [], [], 0
    while i < len(s):
        if s[i] == "\\" and i + 1 < len(s):
            cur.append(s[i:i + 2])
            i += 2
        elif s[i] == "|":
            out.append("".join(cur))
            cur = []
            i += 1
        else:
            cur.append(s[i])
            i += 1
    out.append("".join(cur))
    return [c.strip() for c in out]


def analyse_modele(chemin):
    """Extrait entites, colonnes, FK, discriminants et sections du modele."""
    lignes = open(chemin, encoding="utf-8").read().split("\n")
    debut = next(
        (i for i, l in enumerate(lignes) if re.match(r"^# 1\. ", l)), 0
    )
    ents, courant = {}, None
    for i, l in enumerate(lignes):
        m = re.match(r"^#{2,3} ([A-Za-z_][A-Za-z0-9_]*)\s*$", l)
        if m and i >= debut:
            courant = m.group(1)
            ents[courant] = {"cols": {}, "ligne": i + 1, "utilise": ""}
            continue
        if courant and re.match(r"^\|\s*`", l):
            c = cellules(l)
            nom = c[0].strip("` ")
            ents[courant]["cols"][nom] = {"valeurs": c[-1], "ligne": i + 1}
    # champ "Utilise par", bloc de texte entre le titre et le tableau
    texte = "\n".join(lignes)
    for bloc in re.split(r"\n(?=#{2,3} [A-Za-z_])", texte):
        m = re.match(r"#{2,3} ([A-Za-z_][A-Za-z0-9_]*)\s*\n", bloc)
        if not m or m.group(1) not in ents:
            continue
        mu = re.search(r"\*Utilisé par\*.*?\n(.*?)(?=\n\*|\n\||\n---)", bloc, re.S)
        if mu:
            ents[m.group(1)]["utilise"] = mu.group(1)
    return ents, lignes


def domaines(lignes):
    """Domaines de reference declares, lus dans les sections de patterns."""
    texte = "\n".join(lignes)
    out = {}
    for m in re.finditer(
        r"Domaine de référence de `(\w+)`\s*:(.*?)(?=\n\n)", texte, re.S
    ):
        out[m.group(1)] = set(re.findall(r"`(\w+)`", m.group(2)))
    return out


def index_patterns(lignes):
    """Tables annoncees porteuses de chaque discriminant, lues dans les index."""
    out, disc = {}, None
    for l in lignes:
        m = re.match(r"^## Pattern TPC \w+ \((\w+) \+ \w+\)", l)
        if m:
            disc = m.group(1)
            out.setdefault(disc, set())
            continue
        if l.startswith("## ") and not l.startswith("## Pattern"):
            disc = None
        if disc and re.match(r"^\|\s*`", l):
            out[disc].add(cellules(l)[0].strip("` "))
    return out


# ---------------------------------------------------------------- controles

def controle(racine, chemin_modele):
    ents, lignes = analyse_modele(chemin_modele)
    doms = domaines(lignes)
    idx = index_patterns(lignes)
    noms = set(ents)
    # abreviations de cible tolerees dans la colonne cardinalite
    alias = {"Dep", "Loc", "Obs", "Prop", "Proc", "Unit", "Lic", "FOI",
             "Spec", "SBat", "PBat", "TS", "TTS", "TF"}
    ecarts = []

    # 1. FK sans cible
    for e, d in ents.items():
        for col, info in d["cols"].items():
            for cible in re.findall(r"→\s*([A-Za-z_][A-Za-z0-9_]*)", info["valeurs"]):
                if cible not in noms and cible not in alias:
                    ecarts.append(("FK sans cible", chemin_modele, info["ligne"],
                                   f"{e}.{col} pointe vers {cible}, entité inconnue"))

    # 2. FK fantome
    for e, d in ents.items():
        for cite, col in re.findall(
            r"([A-Z][A-Za-z0-9_]*)\s*\(FK\s+([a-zA-Z_][a-zA-Z0-9_]*)\)", d["utilise"]
        ):
            if cite not in ents:
                ecarts.append(("FK fantôme", chemin_modele, d["ligne"],
                               f"{e} cite l'entité inconnue {cite}"))
            elif col not in ents[cite]["cols"]:
                ecarts.append(("FK fantôme", chemin_modele, d["ligne"],
                               f"{e} annonce {cite} (FK {col}) mais {cite} "
                               f"n'a pas de colonne {col}"))

    # 3. valeur de discriminant hors domaine
    for e, d in ents.items():
        for col, info in d["cols"].items():
            if col in doms:
                vals = set(re.findall(r"`(\w+)`", info["valeurs"]))
                hors = sorted(vals - doms[col])
                if hors:
                    ecarts.append(("domaine TPC", chemin_modele, info["ligne"],
                                   f"{e}.{col} accepte {hors}, hors du domaine "
                                   f"de référence déclaré"))

    # 4. index de pattern
    for disc, tables in idx.items():
        for t in sorted(tables):
            if t in ents and disc not in ents[t]["cols"]:
                ecarts.append(("index de pattern", chemin_modele, ents[t]["ligne"],
                               f"l'index du pattern annonce {t} porteur de "
                               f"{disc}, mais sa table n'a pas cette colonne"))
    for e, d in ents.items():
        for disc in idx:
            if disc in d["cols"] and e not in idx[disc]:
                ecarts.append(("index de pattern", chemin_modele, d["ligne"],
                               f"{e} porte {disc} mais ne figure pas dans "
                               f"l'index de son pattern"))

    # 5. renvoi de fichier
    #
    # plan.md est exempte : nommer des fichiers qui n'existent pas encore est
    # exactement son role. Ailleurs, pour parler d'un fichier absent sans
    # declencher le controle, l'ecrire sans accents graves.
    #
    # Un renvoi peut etre un simple nom (`sources.md`) ou un chemin relatif au
    # depot (`modele/sources.md`). Le chemin est prefere : il leve l'ambiguite
    # quand deux dossiers portent un fichier de meme nom.
    noms, chemins = set(), set()
    for base, dirs, ns in os.walk(racine):
        # .git seul est exclu du relevé de présence : un fichier de .github ou
        # d'archives existe bel et bien et doit pouvoir être cité.
        dirs[:] = [d for d in dirs if d not in {".git", "__pycache__"}]
        for n in ns:
            noms.add(n)
            chemins.add(
                os.path.relpath(os.path.join(base, n), racine).replace(os.sep, "/")
            )
    for chemin in fichiers(racine, (".md", ".txt")):
        if os.path.basename(chemin) == "plan.md":
            continue
        for i, l in enumerate(open(chemin, encoding="utf-8", errors="replace")):
            for ref in re.findall(r"`([A-Za-z0-9_./-]+\.(?:md|txt|py|yml))`", l):
                if "/" in ref:
                    if ref not in chemins:
                        ecarts.append(("renvoi de fichier", chemin, i + 1,
                                       f"cite {ref}, chemin qui n'existe pas"))
                elif ref not in noms:
                    ecarts.append(("renvoi de fichier", chemin, i + 1,
                                   f"cite {ref}, qui n'existe nulle part"))
    return ecarts


def main():
    args = sys.argv[1:]
    racine = "."
    modele = None
    if "--racine" in args:
        racine = args[args.index("--racine") + 1]
    if "--modele" in args:
        modele = args[args.index("--modele") + 1]
    if modele is None:
        modele = trouve_modele(racine)
    if modele is None:
        print("modèle introuvable : aucun fichier ne porte "
              "la section « Patterns transversaux »")
        return 2

    ecarts = controle(racine, modele)
    print(f"modèle analysé : {modele}\n")
    if not ecarts:
        print("aucun écart.")
        return 0

    par_type = {}
    for t, f, l, msg in ecarts:
        par_type.setdefault(t, []).append((f, l, msg))
    for t in ("FK sans cible", "FK fantôme", "domaine TPC",
              "index de pattern", "renvoi de fichier"):
        if t not in par_type:
            continue
        print(f"{t} ({len(par_type[t])})")
        for f, l, msg in par_type[t]:
            print(f"  {f}:{l}  {msg}")
        print()
    print(f"total : {len(ecarts)} écart(s)")
    return 1


if __name__ == "__main__":
    sys.exit(main())
