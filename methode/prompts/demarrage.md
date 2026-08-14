# Prompt de démarrage

`CLAUDE.md`, à la racine, est lu automatiquement en début de session : il porte
déjà le contexte, la carte de propriété et l'ordre de lecture. Ce prompt ne les
répète pas, il demande ce que le routeur ne peut pas donner : une preuve que le
contexte a été compris et une posture explicite.

---

Lis les fichiers dans l'ordre donné par la section *Par où commencer* de
`CLAUDE.md`, puis vérifie en ligne l'état actuel des standards qui évoluent.
Leur état connu est dans `modele/sources.md` ; confirme-le, ne le suppose pas :
les standards avancent pendant que les connaissances d'entraînement
vieillissent. À vérifier en priorité :

- OGC API Connected Systems (successeur de STA, SOS et SPS)
- OGC SensorThings API 2.0
- STAMPLATE (Helmholtz)
- eLTER-RI et ENVRI-Hub NEXT (interopérabilité européenne)
- I-ADOPT (descriptions interopérables de variables observables)

Si tu trouves une divergence, signale-la : c'est `modele/sources.md` qu'il
faudra corriger, puisqu'il est le seul propriétaire de cette information.

Puis fais un résumé en trois parties.

1. **L'état du modèle** : ce qui est solide, ce qui reste ouvert, ce qui mérite
   d'être remis en question avant d'aller plus loin.
2. **Les tensions conceptuelles non résolues** : pas les points techniques, mais
   les questions de fond qui conditionnent plusieurs décisions en aval.
3. **Comment tu comptes travailler** : en montrant que tu sais quand questionner
   et quand exécuter (réflexes 2 et 3 de `methode/SOUL.md`), et que tu ne
   confonds pas les deux.

Le but est de vérifier que le contexte et la posture sont compris. La
conversation guidera ensuite le mode, conceptuel ou ingénieur, selon les besoins
du moment.
