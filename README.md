# BDOH : documentation du modèle de données

Modèle de données de la Base de Données des Observatoires Hydrologiques (BDOH),
développé à INRAE UR RiverLy pour la gestion et le partage de données issues
d'une dizaine d'observatoires environnementaux français, en lien avec les
réseaux OZCAR et Theia.

**Statut : conception.** Rien n'est implémenté. Aucune base ne tourne, aucun
schéma SQL n'est appliqué. Le travail porte sur les fichiers du modèle
eux-mêmes.

## Où est quoi

| Fichier                            | Contient                                                      |
|------------------------------------|---------------------------------------------------------------|
| `dev/CLAUDE/modele_donnees_v12.md` | la structure : entités, colonnes, patterns, conventions       |
| `dev/CLAUDE/decisions_index.md`    | le pourquoi : ADR-001 à ADR-065, alternatives écartées        |
| `dev/CLAUDE/points_ouverts.md`     | ce qui n'est pas tranché                                      |
| `dev/CLAUDE/chantier.md`           | les défauts documentaires et l'hygiène de l'espace de travail |
| `dev/CLAUDE/sources.md`            | les standards externes et leur état daté                      |
| `plan.md`                          | le plan de travail courant                                    |
| `archives/`                        | les états anciens conservés sciemment                         |

Cette arborescence est en cours de réorganisation, voir `plan.md`.

## Documentation en ligne

> **Attention : la documentation publiée n'est pas à jour.**
> Le site [bdoh-inrae.github.io/bdoh-doc](https://bdoh-inrae.github.io/bdoh-doc)
> décrit un état du modèle antérieur à la version courante. Des entités qui n'y
> figurent plus y sont encore documentées. Pour l'état réel du modèle, lire le
> fichier source ci-dessus.
>
> La publication automatique a été désactivée le 14 août 2026 pour cette raison.
> Elle sera rétablie quand `docs/` aura été régénéré depuis le modèle.

## Contribuer à la documentation publique

Écrite en Markdown, générée avec
[MkDocs Material](https://squidfunk.github.io/mkdocs-material/).

```bash
pip install mkdocs-material
mkdocs serve          # puis ouvrir http://127.0.0.1:8000
```

Le déploiement se déclenche à la main : onglet Actions du dépôt, workflow
*Deploy documentation*, bouton *Run workflow*.

## Outils

```bash
python3 dev/outils/mdtable.py check <fichier.md>   # vérifie l'alignement des tableaux
python3 dev/outils/mdtable.py fix   <fichier.md>   # le corrige
```

## Licence

Voir `LICENSE`.
