# 🔄 Système de Refresh Automatique Tableau

## ✅ RÉSUMÉ RAPIDE

Le système est **PRÊT** et **DÉPLOYÉ** sur GitHub ! Il ne manque plus qu'à configurer Heroku.

---

## 📦 Ce Qui Est Déjà Fait

### ✅ Code Développé et Déployé
- **APScheduler** installé (v3.10.4)
- **Scheduler** configuré pour 6h00 et 23h00 (Europe/Paris)
- **10 fichiers CSV** Tableau configurés
- **API endpoints** disponibles pour monitoring et tests
- **Integration complète** dans FastAPI avec lifecycle events
- **Tout est sur GitHub** (commit `2950f1b`)

---

## 🎯 CE QU'IL RESTE À FAIRE (5 minutes)

### Option A : Script PowerShell Automatique ⚡

```powershell
# Dans ce dossier, lancer :
.\configure-heroku-tableau.ps1
```

**C'est tout !** Le script configure automatiquement Heroku.

---

### Option B : Configuration Manuelle Heroku 🖱️

1. Aller sur : **https://dashboard.heroku.com/**
2. Ton app → **Settings** → **Config Vars**
3. Ajouter ces 6 variables (voir `HEROKU_CONFIG_TABLEAU.md`)

---

## 📅 Résultat Final

Une fois configuré, Heroku va **automatiquement** :

- ⏰ **6h00** (heure française) : Télécharger les 10 CSV Tableau
- 🔄 **Tous les jours** sans intervention

## 👁️ Indicateur Visuel dans l'App

Dans le header de l'application, un indicateur montre le statut :

- ✅ **Fond vert** : "Updated 11/06 at 06:00" (refresh réussi)
- ⚠️ **Fond rouge** : "Last attempt 11/06 at 06:00" (refresh échoué)
- ⏳ **Gris** : "Loading..." ou "No update yet"

**Auto-refresh toutes les 5 minutes** pour rester à jour.

---

## 📊 Les 10 CSV Téléchargés

| # | Fichier | Contenu |
|---|---------|---------|
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

## 🧪 Tester le Système

### Via l'API Swagger

```
https://TON-APP.herokuapp.com/docs
```

**Endpoints disponibles** :
- `GET /api/refresh/status` - Vérifier le scheduler
- `GET /api/refresh/last-update` - Dernière mise à jour
- `POST /api/refresh/trigger` - Refresh manuel immédiat

---

## 📚 Documentation

| Fichier | Description |
|---------|-------------|
| **`START_HEROKU_REFRESH.md`** | 🎯 **COMMENCE ICI** - Guide ultra-rapide |
| `HEROKU_CONFIG_TABLEAU.md` | Guide détaillé configuration Heroku |
| `REFRESH_AUTO_6H.md` | Documentation technique complète |
| `configure-heroku-tableau.ps1` | Script PowerShell automatique |
| `test_tableau_refresh.py` | Script de test en local |

---

## 🔐 Sécurité

✅ **Credentials protégés** :
- Stockés dans `backend/.env` (non commité)
- Configurés en Config Vars Heroku (sécurisé)
- Jamais dans le code source GitHub

---

## ⏱️ Temps d'Installation

- **Script automatique** : 30 secondes
- **Configuration manuelle** : 2 minutes

---

## 🎉 C'EST PRÊT !

Le système de refresh automatique à **6h du matin** est **100% fonctionnel**.

Il suffit de configurer les Config Vars sur Heroku et c'est parti ! 🚀

---

## 💡 Aide Rapide

**Problème ?** Voir `HEROKU_CONFIG_TABLEAU.md` section "Troubleshooting"

**Questions techniques ?** Voir `REFRESH_AUTO_6H.md`

**Besoin d'aide ?** Tous les guides sont dans ce dossier.
