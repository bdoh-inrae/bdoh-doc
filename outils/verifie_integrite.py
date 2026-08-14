#!/usr/bin/env python3
"""Signale les fichiers qui ont perdu beaucoup de lignes, avant de committer.

Usage :
    verifie_integrite.py [--seuil N]     compare l'arbre de travail a HEAD
    verifie_integrite.py --commit REF    controle un commit deja fait

Pourquoi cet outil existe. Le 14 aout 2026, un script de reecriture a tronque
modele/chantier.md de 628 lignes, et la troncature a ete commitee sans etre vue.
Les deux autres verificateurs du projet etaient passes au vert : un fichier
ampute reste bien forme, ses tableaux restent alignes, ses renvois restent
valides. Ils controlent la COHERENCE, pas l'INTEGRITE.

Ce que fait celui-ci, et rien d'autre : il compte les lignes perdues et le dit
fort. Il ne juge pas si la perte est legitime. Une suppression voulue (un
fichier fusionne dans un autre, une archive versee) sera signalee comme le
reste : c'est normal, le but est de forcer un regard, pas de bloquer.

Sortie : 0 si rien ne depasse le seuil, 1 sinon.
"""

import subprocess
import sys

SEUIL = 60          # lignes perdues nettes a partir desquelles on alerte
SEUIL_RATIO = 0.25  # ou perte superieure a ce ratio du fichier d'origine


def git(*args):
    r = subprocess.run(["git", *args], capture_output=True, text=True)
    return r.stdout


def taille(ref, chemin):
    out = git("show", f"{ref}:{chemin}")
    return out.count("\n") if out else 0


def main():
    args = sys.argv[1:]
    seuil = SEUIL
    if "--seuil" in args:
        seuil = int(args[args.index("--seuil") + 1])

    if "--commit" in args:
        ref = args[args.index("--commit") + 1]
        brut = git("show", "--numstat", "--format=", ref)
        base = f"{ref}^"
    else:
        brut = git("diff", "--numstat", "HEAD")
        base = "HEAD"

    alertes = []
    for ligne in brut.strip().split("\n"):
        if not ligne.strip():
            continue
        champs = ligne.split("\t")
        if len(champs) < 3 or champs[0] == "-":
            continue           # binaire, ignore
        ajout, retrait, chemin = int(champs[0]), int(champs[1]), champs[2]
        if "=>" in chemin:     # renommage : git donne "ancien => nouveau"
            continue
        net = ajout - retrait
        if net >= 0:
            continue
        avant = taille(base, chemin)
        ratio = (-net / avant) if avant else 0
        if -net >= seuil or ratio >= SEUIL_RATIO:
            alertes.append((chemin, avant, net, ratio))

    if not alertes:
        print("integrite : aucun fichier ne perd de volume au-dela du seuil.")
        return 0

    print(f"{'fichier':44s} {'avant':>7} {'net':>7} {'perte':>7}")
    print("-" * 70)
    for chemin, avant, net, ratio in sorted(alertes, key=lambda a: a[2]):
        print(f"{chemin:44s} {avant:7d} {net:7d} {ratio:6.0%}")
    print()
    print("Regarder chaque ligne avant de committer. Une perte voulue (fichier")
    print("fusionne, archive versee) est normale ; une perte non voulue ne se")
    print("verra nulle part ailleurs, les autres verificateurs ne la voient pas.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
