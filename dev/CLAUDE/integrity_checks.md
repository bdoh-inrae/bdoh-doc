# Contrôles d'intégrité BDOH

Ce fichier documente les vérifications d'intégrité à implémenter lors du
développement. Il existe parce que certaines relations polymorphiques du modèle
ne peuvent pas être garanties par des FK PostgreSQL standard -- la base accepte
des données incohérentes sans broncher si l'application ne vérifie pas.

Ce n'est pas un défaut de conception. C'est un compromis assumé et documenté
(voir ADR-004, ADR-029). Ces contrôles sont la contrepartie de ce choix.

---

## Pourquoi ce fichier existe

PostgreSQL ne supporte pas les FK conditionnelles. Une relation comme :

```
InstrumentUsage.instrumentId -> sensor(id)  SI instrumentType = 'sensor'
InstrumentUsage.instrumentId -> equipment(id)  SI instrumentType = 'equipment'
```

n'est pas exprimable en SQL. La colonne `instrumentId` est donc un uuid sans
contrainte FK déclarée. Si l'application insère une valeur incorrecte, la base
l'accepte silencieusement.

Le même problème existe pour toutes les tables polymorphiques du modèle :
`InstrumentUsage`, `Memory`, `Identifier`, `Responsibility`, `KeywordAssignment`,
`HistoricalLocation`, `HistoricalProject`.

---

## Niveau de risque par table

| Table               | Risque    | Pourquoi                                                        |
|---------------------|-----------|-----------------------------------------------------------------|
| `InstrumentUsage`   | Moyen     | Double polymorphisme : resourceType ET instrumentType           |
| `Memory`            | Faible    | resourceType stable, usage simple                               |
| `Identifier`        | Faible    | resourceType stable, usage simple                               |
| `Responsibility`    | Faible    | resourceType stable, usage simple                               |
| `KeywordAssignment` | Faible    | resourceType stable, usage simple                               |
| `HistoricalLocation`| Faible    | 3 valeurs possibles seulement (Observatory, Site, Station)      |
| `HistoricalProject` | Faible    | 4 valeurs possibles seulement                                   |

`InstrumentUsage` est prioritaire -- commencer par là.

---

## Contrôles à implémenter

### 1. InstrumentUsage -- intégrité des instruments

```sql
-- Sensors référencés qui n'existent pas
SELECT iu.id, iu.instrument_id
FROM instrument_usage iu
LEFT JOIN sensor s ON s.id = iu.instrument_id
WHERE iu.instrument_type = 'sensor'
  AND s.id IS NULL;

-- Equipments référencés qui n'existent pas
SELECT iu.id, iu.instrument_id
FROM instrument_usage iu
LEFT JOIN equipment e ON e.id = iu.instrument_id
WHERE iu.instrument_type = 'equipment'
  AND e.id IS NULL;
```

### 2. InstrumentUsage -- intégrité des ressources

```sql
-- Stations référencées qui n'existent pas
SELECT iu.id, iu.resource_id
FROM instrument_usage iu
LEFT JOIN station s ON s.id = iu.resource_id
WHERE iu.resource_type = 'Station'
  AND s.id IS NULL;

-- TimeSeries référencées qui n'existent pas
SELECT iu.id, iu.resource_id
FROM instrument_usage iu
LEFT JOIN time_serie ts ON ts.id = iu.resource_id
WHERE iu.resource_type = 'TimeSerie'
  AND ts.id IS NULL;

-- Deployments référencés qui n'existent pas
SELECT iu.id, iu.resource_id
FROM instrument_usage iu
LEFT JOIN deployment d ON d.id = iu.resource_id
WHERE iu.resource_type = 'Deployment'
  AND d.id IS NULL;

-- SamplingFeatures référencées qui n'existent pas
SELECT iu.id, iu.resource_id
FROM instrument_usage iu
LEFT JOIN sampling_feature sf ON sf.id = iu.resource_id
WHERE iu.resource_type = 'SamplingFeature'
  AND sf.id IS NULL;
```

### 3. Memory -- intégrité des ressources

```sql
-- Exemple pour Station -- répliquer pour chaque resourceType supporté
SELECT m.id, m.resource_id
FROM memory m
LEFT JOIN station s ON s.id = m.resource_id
WHERE m.resource_type = 'Station'
  AND s.id IS NULL;
```

### 4. Identifier -- intégrité des ressources

Même pattern que Memory -- une requête par resourceType supporté.

---

## Où implémenter ces contrôles

Trois endroits complémentaires, par ordre de priorité :

**1. Dans l'API (Django/FastAPI) -- obligatoire**

Avant chaque INSERT ou UPDATE sur une table polymorphique, vérifier que la
ressource cible existe. C'est la première ligne de défense.

```python
# Exemple Django avant insertion dans InstrumentUsage
def validate_instrument_usage(instrument_type, instrument_id):
    if instrument_type == 'sensor':
        if not Sensor.objects.filter(id=instrument_id).exists():
            raise ValidationError(f"Sensor {instrument_id} introuvable")
    elif instrument_type == 'equipment':
        if not Equipment.objects.filter(id=instrument_id).exists():
            raise ValidationError(f"Equipment {instrument_id} introuvable")
```

**2. En migration Django -- recommandé**

Ajouter une migration qui exécute les requêtes de contrôle au déploiement.
Si une incohérence est détectée, la migration échoue et alerte l'équipe.

**3. En tâche planifiée -- optionnel mais utile**

Une commande Django management (`manage.py check_integrity`) qui lance tous
les contrôles et logue les anomalies. À planifier hebdomadairement ou après
chaque import de données en masse.

---

## Règle générale pour les développeurs

Toute écriture sur une table polymorphique doit :

1. Vérifier que `resourceType` est dans la liste des valeurs autorisées.
2. Vérifier que `resourceId` pointe vers une entité existante du bon type.
3. Pour `InstrumentUsage` : vérifier aussi `instrumentType` + `instrumentId`.

Ces vérifications ne sont pas optionnelles -- elles remplacent les FK
PostgreSQL que la base ne peut pas déclarer.
