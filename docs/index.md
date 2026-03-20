# BDOH — Modèle de données

Bienvenue dans la documentation du modèle de données de la **Base de Données des Observatoires Hydrologiques (BDOH)**, développée à INRAE UR RiverLy.

## À propos

BDOH est un système d'information pour la gestion et le partage de données issues de réseaux de surveillance environnementale — stations hydrométriques, réseaux de qualité d'eau, observatoires de zones critiques.

Le modèle de données est conçu pour être interopérable avec les standards internationaux de l'environnement et de l'IoT.

## Comment naviguer

- [**Vue d'ensemble**](overview.md) — schéma global et principes du modèle
- [**Modèle de données**](model/index.md) — détail de chaque entité
- [**Standards**](standards/index.md) — alignement avec STA, ODM2, ISO 19115
- [**Décisions**](decisions/index.md) — journal des choix de conception

## Standards de référence

| Standard | Rôle dans BDOH |
|---|---|
| OGC SensorThings API (STA) | Interface et modèle de base |
| ODM2 (Horsburgh et al., 2016) | Métadonnées environnementales |
| ISO 19115 | Métadonnées géographiques et responsabilités |
| NERC NVS P01 | Vocabulaire contrôlé des variables |
| Theia/OZCAR thesaurus | Classification thématique |
| STAMPLATE (Helmholtz) | Extensions STA pour l'environnement |
