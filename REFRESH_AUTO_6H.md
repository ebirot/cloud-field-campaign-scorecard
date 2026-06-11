# 🔄 Refresh Automatique CSV Tableau - 6h du Matin

## ✅ Configuration Actuelle

Le système est **DÉJÀ CONFIGURÉ** pour télécharger automatiquement les CSV Tableau :

- **⏰ Horaire** : Tous les matins à **6h00** (heure française - Europe/Paris)
- **⏰ Horaire bonus** : Tous les soirs à **23h00** (heure française)
- **📊 Fichiers** : 10 fichiers CSV depuis Tableau Server
- **🤖 Automatique** : Pas besoin d'intervention manuelle

---

## 🚀 Comment Activer le Système

### Étape 1 : Installer la dépendance manquante

```bash
cd "C:\Users\ebirot\Desktop\Cloud Field Campaign Scorecard\backend"
pip install apscheduler==3.10.4
```

### Étape 2 : Lancer le backend

```bash
cd "C:\Users\ebirot\Desktop\Cloud Field Campaign Scorecard\backend"
uvicorn app.main:app --reload
```

Au démarrage, tu verras :

```
🚀 Starting Cloud Field Campaign Scorecard...
✅ Task scheduler started
📅 CSV refresh scheduled: 06:00 CET and 23:00 CET daily
✅ Application startup complete
```

**C'est tout !** Le système est actif ✅

---

## 🧪 Tester Maintenant (Sans Attendre 6h)

### Option A : Script de Test Direct

```bash
cd "C:\Users\ebirot\Desktop\Cloud Field Campaign Scorecard"
python test_tableau_refresh.py
```

Cela télécharge immédiatement tous les CSV.

### Option B : Via l'API (Backend en cours d'exécution)

```bash
# Dans un autre terminal
curl -X POST http://localhost:8000/api/refresh/trigger
```

Ou ouvre dans ton navigateur :
```
http://localhost:8000/docs
```

Puis cherche l'endpoint `POST /api/refresh/trigger` et clique sur "Try it out".

---

## 📊 Fichiers Téléchargés

Les CSV seront sauvegardés dans :
```
C:\Users\ebirot\Desktop\Cloud Field Campaign Scorecard\data\csv\
```

**Liste des 10 fichiers** :

| # | Fichier | View Tableau |
|---|---------|--------------|
| 1 | `1_regional_sales_l2.csv` | Regional Sales L2 |
| 2 | `2_regional_sales_l2_cloud.csv` | Regional Sales L2 & Cloud |
| 3 | `3_regional_sales_l3.csv` | Regional Sales L3 |
| 4 | `4_cloud_view_l1.csv` | Cloud View APM L1 |
| 5 | `5_cloud_view_l2.csv` | Cloud View APM L2 |
| 6 | `6_horseman.csv` | Horseman |
| 7 | `7_traffic_source.csv` | Traffic Source |
| 8 | `8_offer_l1_l2.csv` | Offer L1/L2 |
| 9 | `9_webinar.csv` | Webinar |
| 10 | `10_data_freshness.csv` | Data Freshness |

---

## 🔐 Credentials Tableau

Les credentials sont configurés dans `backend/.env` :

```env
TABLEAU_SERVER_URL=https://prod-uswest-c.online.tableau.com
TABLEAU_SITE_ID=salesforce
TABLEAU_TOKEN_NAME=your_token_name
TABLEAU_TOKEN_VALUE=your_token_value
TABLEAU_WORKBOOK_MDP_SCORECARD=your_workbook_id
```

**Note** : Les vraies valeurs sont dans ton fichier `.env` local (non commité sur GitHub).

✅ **Token expire le** : 28 Mai 2027 (encore 11 mois de validité)

---

## 📈 Monitoring du Système

### Vérifier le Status du Scheduler

**GET** `http://localhost:8000/api/refresh/status`

Exemple réponse :
```json
{
  "scheduler_running": true,
  "jobs": [
    {
      "id": "morning_csv_refresh",
      "name": "Morning CSV Refresh",
      "next_run": "2026-06-12T06:00:00+02:00"
    },
    {
      "id": "daily_csv_refresh",
      "name": "Daily CSV Refresh from Tableau",
      "next_run": "2026-06-11T23:00:00+02:00"
    }
  ]
}
```

### Voir la Dernière Mise à Jour

**GET** `http://localhost:8000/api/refresh/last-update`

---

## 🎯 Sur Heroku (Production)

Le système fonctionne **aussi sur Heroku automatiquement** :

1. ✅ APScheduler ajouté dans `requirements.txt`
2. ✅ Scheduler démarre avec `lifespan` dans `main.py`
3. ✅ Variables d'environnement configurées dans Heroku Config Vars

**IMPORTANT** : Sur Heroku, assure-toi d'ajouter les Config Vars :
```
TABLEAU_TOKEN_NAME=your_token_name
TABLEAU_TOKEN_VALUE=your_token_value
TABLEAU_WORKBOOK_MDP_SCORECARD=your_workbook_id
```

Ces valeurs doivent correspondre à celles de ton fichier `.env` local.

---

## 🐛 Troubleshooting

### Problème : "No module named 'apscheduler'"

**Solution** :
```bash
cd backend
pip install apscheduler==3.10.4
```

### Problème : "401 Unauthorized" depuis Tableau

**Solution** :
1. Vérifie que le token est correct dans `.env`
2. Vérifie que le token n'a pas expiré (expire le 28 Mai 2027)
3. Regénère un nouveau token si nécessaire

### Problème : Les fichiers ne se téléchargent pas

**Solution** :
1. Vérifie que le dossier `data/csv/` existe :
```bash
mkdir -p "C:\Users\ebirot\Desktop\Cloud Field Campaign Scorecard\data\csv"
```

2. Lance le test manuel :
```bash
python test_tableau_refresh.py
```

### Problème : Scheduler ne démarre pas

**Solution** :
Vérifie les logs au démarrage du backend. Tu dois voir :
```
✅ Task scheduler started
📅 CSV refresh scheduled: 06:00 CET and 23:00 CET daily
```

Si absent, vérifie que `init_scheduler()` est appelé dans `main.py` (ligne 29).

---

## ⚙️ Modifier l'Horaire

Pour changer l'heure, édite `backend/app/services/scheduler.py` :

```python
# Ligne 42 : Changer l'horaire du refresh matinal
CronTrigger(hour=6, minute=0, timezone='Europe/Paris')
           # ↑ Change cette valeur (0-23)

# Ligne 33 : Changer l'horaire du refresh nocturne
CronTrigger(hour=23, minute=0, timezone='Europe/Paris')
           # ↑ Change cette valeur (0-23)
```

---

## 📅 Prochains Refreshes

Basé sur l'heure actuelle (11 Juin 2026, ~18h) :

- **Prochain refresh** : Ce soir à **23h00**
- **Refresh suivant** : Demain matin à **6h00**

---

## ✅ Checklist

- [x] APScheduler ajouté dans `requirements.txt`
- [x] Scheduler configuré pour 6h + 23h (timezone Europe/Paris)
- [x] Token Tableau valide jusqu'en Mai 2027
- [x] Scheduler s'active automatiquement au démarrage
- [x] API endpoints disponibles pour tests manuels
- [x] Script de test `test_tableau_refresh.py` créé

---

## 🎉 Résumé

**Le système de refresh automatique à 6h du matin est PRÊT !**

Pour l'activer maintenant :
```bash
cd "C:\Users\ebirot\Desktop\Cloud Field Campaign Scorecard\backend"
pip install apscheduler==3.10.4
uvicorn app.main:app --reload
```

**Demain matin à 6h, les CSV seront automatiquement téléchargés !** 🚀
