
# Product Backlog


## Global
- traduction  anglais français
- Licence Ouverte Etalab même les données privées qui sont sous embargo (18 mois max)
- 
[1] intégration continue pour faire des releases
- service de job parallélisés que si c'est trop long  
[1] mentions légales
[1] RGPD
[3] gallery photo

## Monitoring
Pour les adminstrateurs et gestionnaires d'observatoire, suivi du nombre de :

- visite de chaque chronique
- export
- inscrit
- connection
- nouvelle chronique
- import
- recherche
- variable

Suivi des jobs et de leur unicité.
Message d'information sur l'actualisation des données en cours.


## Histrorique
Historique de suivi des modifications global sur la base selon le niveau de privilèges des utilisateurs.

Suivi par :

- date
- auteur
- type d'action

Selon la thématique :

- Tout
- Privilèges
- Observatoires : modification sur les objets des observatoires
- Imports
- Traitement (suppression, gestion des barèmes, calcul)
- Exports






## Rôles et gestion des rôles
### Les rôles
Les rôles membre de confiance, gestionnaires de chroniques libre et non libres ne sont propres qu'à une sélection de chroniques.<br>
Les rôles des gestionnaire de stations ne sont propres qu'à une sélection de stations.<br>
Les rôles des gestionnaire de sites ne sont propres qu'à une sélection de sites.<br>
Les rôles des gestionnaire d'observatoires ne sont propres qu'à une sélection d'observatoires.<br>
Le rôle d'administrateur s'applique à toutes les chroniques, stations, sites et observatoires.

- **anonyme** : *chercher, visualiser, exporter des chroniques*

- **membre** : *enregistrement de sélections de chroniques* / chercher, visualiser, exporter des chroniques / *chercher* des chroniques non libres

- **membre de confiance** : enregistrement de sélections de chroniques / chercher, visualiser, exporter des chroniques / chercher, *visualiser*, *exporter* des chroniques non libres

- **gestionnaire de chroniques** : enregistrement de sélections de chroniques / chercher, visualiser, exporter, *importer*, *calculer*, *modifier* des chroniques / chercher des chroniques non libres

- **gestionnaire de chroniques non libres** : gestionnaire de rôles de *membre de confiance* / enregistrement de sélections de chroniques / chercher, visualiser, exporter, des chroniques / chercher, *visualiser*, *exporter*, *importer*, *calculer* et *modifier* des chroniques non libres

- **gestionnaire de stations** : gestionnaire de rôles membre de confiance, de *gestionnaire de chroniques libres et non libres* / enregistrement de sélections de chroniques / chercher, visualiser, exporter, importer, calculer, *créer*, modifier, *altérer* des chroniques libre et non libres / *modifier* des stations

- **gestionnaire de sites** : gestionnaire de rôles membre de confiance, de gestionnaire de chroniques libres et non libres et de *gestionnaire de stations* / enregistrement de sélections de chroniques / chercher, visualiser, exporter, importer, calculer, créer, modifier, altérer des chroniques libre et non libres / *créer*, modifier, *altérer* des stations / *modifier* des sites 

- **gestionnaire d'observatoires** : gestionnaire de rôles de *membre de confiance*, gestionnaire de chroniques libres et non libres, gestionnaire de stations, *gestionnaire de sites* et *gestionnaire d'observatoires* / enregistrement de sélections de chroniques / chercher, visualiser, exporter, importer, calculer, créer, modifier altérer des chroniques libre et non libres / créer, modifier, altérer des stations / *créer*, modifier, *altérer* des sites / *modifier* des observatoires / *céer*, *modifier*, *altérer* des jeux de données

- **administrateur** : gestionnaire de rôles de *membre*, membre de confiance, gestionnaire de chroniques libres et non libres, gestionnaire de stations, gestionnaire de sites, gestionnaire d'observatoires et *administrateur* / enregistrement de sélections de chroniques / chercher, visualiser, exporter, importer, calculer, créer, modifier, altérer des chroniques libre et non libres / créer, modifier, altérer des stations / créer, modifier, altérer des sites / *créer*, modifier, *altérer* des observatoires / céer, modifier, altérer des jeux de données

Tous les utilisateurs peuvent : demander de l'aide / proposer des améliorations

### Devenir membre
Pour devenir membre il faut s'inscrire à BDOH.
L'inscription demande obligatoirement une adresse mail, un nom, un prénom et un mot de passe. La connection avec la fédération est possible.
Lors de l'inscription il est possible d'ajouter son ORCID ainsi que sont affiliation lié à une structure de recherche (API structure de recherche : https://data.enseignementsup-recherche.gouv.fr/explore/dataset/fr-esr-structures-recherche-publiques-actives/api/?disjunctive.numero_national_de_structure&disjunctive.tutelles&q=inrae&disjunctive.type_de_structure)

Un administrateur peut créer un membre.

### Gestion des rôles
La page global de gestion des rôles contient :
- Un résumé des rôles du membre.
- Un résumé des droits des rôles possibles.
- Si le membre est gestionnaire de rôle, cette page permet d'attribuer ou retirer des rôles à d'autres utilisateurs grâce à une barre de recherche. 

Sur chaque page d'objet, si un membre est gestionnaire de rôle, il peut voir une page de gestion de rôle spécifique à l'objet visualiser pour permettre de gérer les rôles des membres sur l'objet en question.
Si un membre veut faire une demande de rôle, il peut contacter les gestionnaires sur les pages de chaque objet.

Rappel, les rôles sont spécifiques à un objet (chroniques, stations, sites, observatoires).



## Visualisation
- Affichage des lacunes par mois pour les chroniques continues et le nombre de mesures pour les chroniques discontinue
- Gestion de l'affichage de l'entiereté de la chronique ou d'une seule partie avec un aperçu de l'ensemble de la chronique en dessous de la courbe.
- Renvoie depuis les infos de lacunes par pédiode de temps vers le graphique.
- Affichage des points de contrôle
- Code qualité affiché par la couleur de la courbe
- Afficher plusieurs chronique en même temps de même unité ou nom avec un contrôle sur les axes (inversé, log, sqrt)
- Faire la conversion des chronique à la volé L/s -> m3/s


## Chercher



## Exporter
Privilegier l'export par le navigateur mais si l'export est trop long : envoie de mails qui contiennent des URL temporaires.  

Lors de l'export l'utilisateur peut choisir :

- la période d'export
- le fuseau horaire
- format de fichier (csv, json)

Si l'utilisateur est connecté et est donc membre, il peut réalisé un pannier de chronique qu'il peut enregistrer et exporter par paquet.
L'export de pannier permet de selectionner et enregistrer pour chaque chronique le type d'export voulu.
Par défaut, la période d'export est la période visualisée.

Le format d'export suit les principes FAIR.

### Dossier zippé d'export
*titre*

BDOH-export_VAR_TYPE_OBS_SIT_STA_DEB-FIN

*format du titre*

- VAR = identifiant de la variable
  - *DEB* : débit
  - *HT* : hauteur d'eau
- TYPE = type d'export
  - *raw* : pas de modification
  - *interp-linear* : interpolation lineaire (1 min à 24 h)
  - *agg-FUN-timestep* : aggregation temporel par la fonction *FUN* (sum, avg, movavg, max, min, qXX) sur le pas de temps *timestep* (year, month, season) avec gestion des lacunes
- OBS = observatoire id
  - *YZE* : Yzeron
  - *DRA* : Draix
- SITE = site id
  - *BV-YZE* : Bassin versant de l'Yzeron
  - *EXP-CHA* : Experimentations Chaudanne
  - *EXP-MER* : Experimentation Mercier
  - *RET-COL* : Retenues Collinaires
- STA = code station
- DEB-FIN = période d'export
  - DEB = date de début de l'export
  - FIN = date de fin de l'export

*fichiers en plus*

- Licence Ouverte anglais/français
- README : récapitulatif de ces infos avec la citation des données et le lien vers les resources importantes (type de chronique,
nombre de mesures, généalogie...)


### Format CSV
*titre*

data.csv

*info*

Fichier de donnée de l'export

*colonne*

- id_chronique : Identifiant de la chronique
- id_variable : Identifiant de la variable
- date : Date 
- value : Valeur
- value_min : Borne basse de l'incertitude
- value_max : Borne haute de l'incertitude
- quality : Code qualité


** fichier de métadonnées de variable **

*titre*

meta_variable.csv

*info*

*colonne*
- id_variable : Identifiant de la variable
- variable : Nom long de la variable
- definition : Definition de la variable
- export_type : type d'export
- lien avec d'autres métadonnées

** fichier de métadonnées de station **

*titre*

meta_chronique.csv

*info*

*colonne*
- id_chronique : Identifiant de la chronique
- id_observatory : Identifiant de l'observatoire
- observatory : Nom de l'observatoire
- id_site : Identifiant du site
- site ; Nom du site
- id_sation : Identifiant de la station
- station : Nom de la station

### Format JSON
```
{
  "observatories": [
    {
      "id_observatory": "<id_observatory>",
      "observatory_name": "<observatory_name>",
      "sites": [
        {
          "id_site": "<id_site>",
          "site_name": "<site_name>",
          "stations": [
            {
              "id_station": "<id_station>",
              "station_name": "<station_name>",
              "chroniques": [
                {
                  "id_chronique": "<id_chronique>",
                  "variable": {
                    "id_variable": "<id_variable>",
                    "variable_name": "<variable_name>",
                    "definition": "<definition>",
                    "export_type": "<export_type>"
                  },
                  "measures": [
                    {
                      "date": "<date>",
                      "value": "<value>",
                      "value_min": "<value_min>",
                      "value_max": "<value_max>",
                      "quality": "<quality>"
                    }
                  ]
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

[?] Eclairicir le niveau de précision de la date
[?] Les shapefile 


## Interoperabilité et transfert
- Les chroniques de BDOH peuvent être transférer directement à l'HydroPortail.
- Les DOI des jeux de données sont obtenues lors du transfert des métadonnées sur Recherche Data Gouv.
- Les jeux de données peuvent être transférer directment au SI Theia/OZCAR.


## Importer
[1] vérification lors de l'import (uncité des dates, tri, pas de chevauchement des plages d'import de données, ...)
[1] import de sig
[1] convertir chronique discontinue en chronique continue
[2] gestion des incertitudes + gestion des chiffres significatif
[1] taille limite des fichiers d'import -> API règle le problème ?

## Calculer




## Objets

### Membre
#### Attributs
- photo / id ascii art
- email*
- nom*
- prénom*
- mot de passe*
- ORCID
- affiliation (auto rempli par l'ORCID)
- rôle

#### Méthodes
- générer un jeton API
- gérer ses rôles


### Partenaire
#### Attributs

#### Méthodes


### Incerittude
#### Attributs
- type d'incertitudes (Confidence Interval, Standard Deviation, Absolute Error)

#### Méthodes


### Barème
#### Attributs
- identifiant de barèmes
- nom
- commentaire
- X
- X min
- X max
- unité X
- type d'inceritude X
- code qualité X
- Y
- Y min
- Y max
- unité Y
- type d'inceritude Y
- code qualité Y

#### Méthodes


### Jeu de barèmes
#### Attributs
- identifiant de jeux de barèmes
- début
- fin
- id chronique entrée 

#### Méthodes


### Généalogie de barèmes
#### Attributs
- identifiant de jeux de barèmes
- date

#### Méthodes


### Variables
#### Attributs

#### Méthodes


### Point de contrôle
#### Attributs

#### Méthodes


### Mesure
#### Attributs
- id chronique
- date
- valeur
- borne min
- borne max
- code qualité

#### Méthodes


### Chronique
#### Attributs
- type (continue, discontinue)
- est elle libre
- identifiant de jeux de barèmes
- variable
- type d'incertitudes
- id chronique

#### Méthodes
*Modification*

- changer les métadonnées
- application de code de validation
- supprimer des données
- calculer des chroniques transformer

*Altération*

- transformer une chronique non libre en chronique libre et vice-versa
- supprimer l'objet


### Station
#### Attributs

#### Méthodes


### Site
#### Attributs

#### Méthodes


### Jeu de données
#### Attributs

#### Méthodes


### Observatoire
#### Attributs

#### Méthodes




## Données
[1] recherche par filtre par objet
[?] gestion des millisecondes
[1] recherche des stations et chroniques par filtre avance : station / activité / commune / sites expérimentaux / producteur / famille de paramètre / paramètre / type de chronique / bassin / cours d'eau / jeux de données

### Observatoires
[1] gestion de logo et de personnalisation
[1] code qualité propre à un observatoire / stations et quel code ?

### Stations

### Chroniques mères
[1] producteur pour les chroniques
[1] autorisé les doublons de nom
[1] chronique caché, donnée privé
[1] duplication de chronique
[1] gestion des lacunes lors de la suppression : https://gitlab.irstea.fr/pole-is/bdoh/-/issues/115
[2] chronique discontinue (pb de vocabulaire)
[2] supprimer des données en ligne, transformer en donnée invalide depuis BDOH
[?] conversion de chroniques

### Chroniques filles
[1] actualisation des chroniques filles si la chronique mere a changé
[1] interdir la supression de donnée sur les chroniques calculées
[3] estimation des chroniques de contaminants https://gitlab.irstea.fr/pole-is/bdoh/-/issues/77 

### Barèmes
[1] supprimer les baremes
[1] pour le calcul d'une chronique faire une recherche par station
[2] gestion graphique de l'application des barèmes par date et heure seconde
[1] voir l'historique des barèmes sur une chronique calculé : versionning
[1] gestion des unités dans les barèmes
[?] champs min max des barèmes

### Variables
[1] unité associé au variable
[?] notiton de famille de paramètre (comme theia)

### Jeux de données
[1] gestion des doi avec RDG

### Point de contrôle


### SIG
[?] db geojson pour gérer les shp ou base de donnée mixte avec les infos des objets (station, site, observatoire)


## Dette technique à éclaircir
Nom de station en doublon
Librairie de graph
Manque de test, perte de suivi
le cache ?