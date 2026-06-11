# 🔄 CSV Auto-Refresh System

## Vue d'ensemble

Le système télécharge automatiquement les CSV depuis Tableau Server **tous les jours à 06:00 et 23:00 CET**.

---

## 🎯 Fonctionnalités

### 1. Refresh Automatique
- **06:00 CET**: Données du matin (pour commencer la journée avec des chiffres frais)
- **23:00 CET**: Données de fin de journée (tous les deals fermés inclus)

### 2. Refresh Manuel
- API endpoint pour déclencher manuellement: `POST /api/refresh/trigger`
- Utilisable depuis le frontend (bouton à ajouter dans Admin)

### 3. Monitoring
- Status du scheduler: `GET /api/refresh/status`
- Dernière mise à jour: `GET /api/refresh/last-update`

---

## 📋 CSV Téléchargés

Les 10 fichiers CSV suivants sont automatiquement mis à jour:

| # | View Tableau | Fichier Local |
|---|--------------|---------------|
| 1 | Regional Sales L2 | `1_regional_sales_l2.csv` |
| 2 | Regional Sales L2 Cloud | `2_regional_sales_l2_cloud.csv` |
| 3 | Regional Sales L3 | `3_regional_sales_l3.csv` |
| 4 | Cloud View L1 | `4_cloud_view_l1.csv` |
| 5 | Cloud View L2 | `5_cloud_view_l2.csv` |
| 6 | Horseman | `6_horseman.csv` |
| 7 | Traffic Source | `7_traffic_source.csv` |
| 8 | Offer L1 L2 | `8_offer_l1_l2.csv` |
| 9 | Webinar | `9_webinar.csv` |
| 10 | Data Freshness | `10_data_freshness.csv` |

---

## 🔐 Configuration

### Variables d'Environnement (.env)

Déjà configurées dans `backend/.env`:

```env
# Tableau Server
TABLEAU_SERVER_URL=https://prod-uswest-c.online.tableau.com
TABLEAU_SITE_ID=salesforce
TABLEAU_TOKEN_NAME=your_token_name
TABLEAU_TOKEN_VALUE=your_token_value
TABLEAU_API_VERSION=3.19

# Workbook
TABLEAU_WORKBOOK_MDP_SCORECARD=your_workbook_id
```

### Personal Access Token

**Nom**: Configure in `.env` file  
**Valeur**: Configure in `.env` file (never commit secrets!)  
**Permissions requises**:
- View workbook
- Download views as CSV

---

## 🚀 Démarrage

### Automatique au lancement du backend

Le scheduler démarre automatiquement quand tu lances:

```bash
cd backend
uvicorn app.main:app --reload
```

Logs au démarrage:
```
🚀 Starting Cloud Field Campaign Scorecard...
✅ Task scheduler started
📅 CSV refresh scheduled: 06:00 CET and 23:00 CET daily
✅ Application startup complete
```

---

## 🧪 Test Manuel

### 1. Via Python Direct

```bash
cd backend
python -m app.services.tableau_refresh
```

Cela télécharge immédiatement tous les CSV.

### 2. Via API

```bash
# Déclencher refresh
curl -X POST http://localhost:8000/api/refresh/trigger

# Vérifier status
curl http://localhost:8000/api/refresh/status

# Dernière mise à jour
curl http://localhost:8000/api/refresh/last-update
```

### 3. Via Frontend (TODO)

Ajouter un bouton dans l'onglet Admin:
```
[🔄 Refresh Data Now]
```

---

## 📊 Monitoring

### Status du Scheduler

**GET** `/api/refresh/status`

Réponse:
```json
{
  "scheduler_running": true,
  "jobs": [
    {
      "id": "daily_csv_refresh",
      "name": "Daily CSV Refresh from Tableau",
      "next_run": "2026-05-29T23:00:00+02:00",
      "trigger": "cron[hour='23', minute='0']"
    },
    {
      "id": "morning_csv_refresh",
      "name": "Morning CSV Refresh",
      "next_run": "2026-05-30T06:00:00+02:00",
      "trigger": "cron[hour='6', minute='0']"
    }
  ],
  "next_daily_refresh": "2026-05-29T23:00:00+02:00",
  "next_morning_refresh": "2026-05-30T06:00:00+02:00",
  "current_time": "2026-05-29T14:30:00"
}
```

### Dernière Mise à Jour

**GET** `/api/refresh/last-update`

Réponse:
```json
{
  "last_updated": "2026-05-29 23:00:00",
  "file_exists": true
}
```

---

## 🔍 Logs

Le système log toutes les opérations:

```
🔐 Authenticating with Tableau Server...
✅ Tableau authentication successful
📋 Fetching workbook views...
📊 Found 10 views in workbook
📥 Downloading 10 CSV files...
✅ Downloaded Regional Sales L2 -> 1_regional_sales_l2.csv (125.3 KB)
✅ Downloaded Regional Sales L2 Cloud -> 2_regional_sales_l2_cloud.csv (98.7 KB)
...
✅ CSV refresh completed: 10/10 files in 8.3s
📅 Updated data freshness: 2026-05-29 23:00:00
🔓 Signed out from Tableau Server
```

---

## 🛠️ Troubleshooting

### Problème: Token expiré

**Symptôme**: `401 Unauthorized` dans les logs

**Solution**:
1. Générer un nouveau token sur Tableau Server
2. Mettre à jour `TABLEAU_TOKEN_VALUE` dans `.env`
3. Redémarrer le backend

### Problème: View introuvable

**Symptôme**: `View 'XYZ' not in mapping, skipping`

**Solution**:
1. Vérifier le nom exact de la view sur Tableau Server
2. Ajouter le mapping dans `tableau_refresh.py`:
```python
self.view_mappings = {
    'Nom Exact View': 'numero_fichier.csv',
    ...
}
```

### Problème: Scheduler ne démarre pas

**Symptôme**: Pas de logs de scheduler au démarrage

**Solution**:
```bash
# Vérifier les imports
python -c "from app.services.scheduler import scheduler; print('OK')"

# Vérifier APScheduler installé
pip list | grep apscheduler
```

---

## 📝 Architecture

### Composants

1. **tableau_refresh.py**: Service de téléchargement Tableau
   - Authentification via Personal Access Token
   - Download CSV via Tableau REST API
   - Gestion des erreurs et retry

2. **scheduler.py**: Gestionnaire de tâches planifiées
   - APScheduler pour le scheduling
   - Démarrage automatique avec le backend
   - Gestion des jobs (ajout, suppression, monitoring)

3. **refresh.py**: API endpoints
   - Trigger manuel
   - Status du scheduler
   - Dernière mise à jour

4. **main.py**: Intégration
   - Lifecycle hooks (startup/shutdown)
   - Démarrage automatique du scheduler

---

## 🔒 Sécurité

### Token Storage

✅ **Actuellement**: Token stocké dans `.env` (OK pour dev/internal)  
⚠️ **Production**: Utiliser Azure Key Vault ou AWS Secrets Manager

### Logs

- Les tokens ne sont JAMAIS loggés
- Seulement le nom du token est visible
- Les erreurs d'auth sont génériques

---

## 🎛️ Configuration Avancée

### Changer les heures de refresh

Dans `backend/app/services/scheduler.py`:

```python
# Daily refresh at 23:00 CET
self.scheduler.add_job(
    self._run_csv_refresh,
    CronTrigger(hour=23, minute=0, timezone='Europe/Paris'),
    ...
)

# Morning refresh at 06:00 CET
self.scheduler.add_job(
    self._run_csv_refresh,
    CronTrigger(hour=6, minute=0, timezone='Europe/Paris'),
    ...
)
```

### Ajouter un refresh supplémentaire

```python
# Lunch refresh at 12:00
self.scheduler.add_job(
    self._run_csv_refresh,
    CronTrigger(hour=12, minute=0, timezone='Europe/Paris'),
    id='lunch_csv_refresh',
    name='Lunch CSV Refresh',
    replace_existing=True
)
```

### Refresh toutes les 4 heures

```python
self.scheduler.add_job(
    self._run_csv_refresh,
    CronTrigger(hour='*/4', timezone='Europe/Paris'),  # Every 4 hours
    id='frequent_refresh',
    name='Frequent CSV Refresh',
    replace_existing=True
)
```

---

## ✅ Résumé

**Status**: ✅ Implémenté et prêt à utiliser  
**Horaires**: 06:00 CET et 23:00 CET  
**Fichiers**: 10 CSV automatiquement mis à jour  
**API**: Trigger manuel + monitoring disponibles  
**Logs**: Complets et détaillés  

**Prochaine étape**: Redémarrer le backend pour activer le scheduler!

```bash
# Arrêter le backend actuel (Ctrl+C)
# Relancer
cd backend
uvicorn app.main:app --reload
```

**Le scheduler sera actif et les CSV seront mis à jour automatiquement! 🚀**
