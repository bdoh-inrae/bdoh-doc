# Archives

Ce dossier garde les états anciens qu'on a décidé de conserver, par opposition à
ceux qu'on a décidé de supprimer. La distinction est volontaire dans les deux
sens : rien n'arrive ici par inertie, rien n'est supprimé sans qu'on l'ait
regardé.

Règle : **un fichier archivé ne fait plus autorité.** Il ne doit être cité par
aucun fichier vivant autrement que comme référence historique. S'il contient
encore une information vivante, cette information doit d'abord être versée dans
le fichier qui la possède, et l'archive ne sert plus qu'à la trace.

| Fichier                          | Ce que c'est                                                   | Statut                                         |
|----------------------------------|----------------------------------------------------------------|------------------------------------------------|
| `doutes_modele_ancien.txt`       | questions notées sur un état antérieur du modèle (InstrumentUsage, TimeSerie) | à relire, semblent résolues (voir ci-dessous) |
| `soul_v0.md`                     | ancêtre de `SOUL.md`, écrit comme un bilan de collaboration    | superseded, conservé pour la trace             |
| `product_backlog.md`             | backlog fonctionnel de la plateforme (monitoring, RGPD, exports, traduction) | archivé sans reprise, décision du 14 août 2026 |
| `chat_architecture_initiale.txt` | première conversation d'architecture, séparation stockage et traitement | conservé pour la trace |
| `plans/`                         | plans de travail clos, datés de leur ouverture                 | voir le cycle de vie décrit dans `plan.md`     |

Vérification faite le 14 août 2026 sur `doutes_modele_ancien.txt` : les trois
questions qu'il porte semblent réglées par le modèle v12. `observationType` a
disparu du modèle ; `procedureValidation` n'est plus porté que par `TimeSeries`,
plus par `ValidationBatch` ; la distinction entre observation ponctuelle et
observation sur plage est désormais explicite via le couple
`phenomenonTimeStart` et `phenomenonTimeEnd`. À confirmer lors de la relecture
groupée avec `audit_modele_v12.md`.

Un fichier `philo.txt~` de deux octets, vide de contenu, a été supprimé sans
archivage à la même date.

`audit_modele_v12.md` a été supprimé le 14 août 2026 : ses vingt constats ont
été versés tels quels dans `modele/chantier.md`, section *Constats versés depuis
l'audit de juillet 2026*. Ils y attendent d'être instruits un par un. Le texte
d'origine reste lisible dans l'historique git.
