# BDOH — Documentation du modèle de données

Documentation du modèle de données de la Base de Données des Observatoires Hydrologiques (BDOH), développée à INRAE UR RiverLy.

## Lire la documentation

La documentation est disponible en ligne : [https://votre-org.github.io/bdoh-doc](https://votre-org.github.io/bdoh-doc)

## Contribuer

La documentation est écrite en Markdown et générée avec [MkDocs Material](https://squidfunk.github.io/mkdocs-material/).

### Prérequis

```bash
pip install mkdocs-material
```

### Prévisualisation locale

```bash
mkdocs serve
# puis ouvrir http://127.0.0.1:8000 dans Firefox
```

### Déploiement

Le déploiement est automatique via GitHub Actions à chaque push sur `main`.

## Structure

```
docs/
├── index.md          # Page d'accueil
├── overview.md       # Vue d'ensemble du modèle
├── model/            # Modèle de données — une page par section
├── standards/        # Alignement avec les standards (STA, ODM2, ISO 19115...)
└── decisions/        # Journal des décisions de conception (ADR)
```
