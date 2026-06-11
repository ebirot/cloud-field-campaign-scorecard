# 🚀 DÉMARRAGE RAPIDE - Heroku Tableau Refresh

## ⚡ Pour activer le refresh automatique à 6h sur Heroku

### Méthode 1 : Script Automatique (LE PLUS SIMPLE)

```powershell
# Ouvrir PowerShell dans ce dossier
.\configure-heroku-tableau.ps1
```

Le script va :
1. ✅ Lire les credentials depuis `backend\.env`
2. ✅ Les configurer automatiquement sur Heroku
3. ✅ Vérifier que tout est OK

**Temps** : 30 secondes ⏱️

---

### Méthode 2 : Heroku Dashboard (Interface Web)

1. **Aller sur** : https://dashboard.heroku.com/

2. **Cliquer sur ton app** (ex: `salesforce-scorecard-emea`)

3. **Settings** → **Config Vars** → **Reveal Config Vars**

4. **Ajouter ces 6 variables** :

| Variable | Valeur (depuis `backend\.env`) |
|----------|--------------------------------|
| `TABLEAU_SERVER_URL` | `https://prod-uswest-c.online.tableau.com` |
| `TABLEAU_SITE_ID` | `salesforce` |
| `TABLEAU_TOKEN_NAME` | Copier depuis `.env` |
| `TABLEAU_TOKEN_VALUE` | Copier depuis `.env` |
| `TABLEAU_WORKBOOK_MDP_SCORECARD` | Copier depuis `.env` |
| `TABLEAU_API_VERSION` | `3.19` |

**Temps** : 2 minutes ⏱️

---

## ✅ Vérifier que Ça Marche

### 1. Ouvrir l'API Swagger de ton app Heroku

```
https://TON-APP.herokuapp.com/docs
```

### 2. Tester l'endpoint de status

Chercher : **GET /api/refresh/status**

Cliquer : **Try it out** → **Execute**

Tu dois voir :
```json
{
  "scheduler_running": true,
  "jobs": [
    {
      "id": "morning_csv_refresh",
      "next_run": "2026-06-12T06:00:00+02:00"
    }
  ]
}
```

### 3. Tester un refresh manuel

Chercher : **POST /api/refresh/trigger**

Cliquer : **Try it out** → **Execute**

Ça va télécharger les 10 CSV immédiatement !

---

## 📅 Horaires de Refresh

Une fois configuré :

- 🌅 **6h00** tous les matins (heure française)
- 🌙 **23h00** tous les soirs (heure française)

**Automatique, pas besoin d'intervention !** 🎉

---

## 🐛 Si Ça Ne Marche Pas

### Voir les logs Heroku

```bash
heroku logs --tail --app TON-APP
```

Chercher :
```
✅ Task scheduler started
📅 CSV refresh scheduled: 06:00 CET and 23:00 CET daily
```

### Problème courant : Config Vars manquantes

Vérifier :
```bash
heroku config --app TON-APP | grep TABLEAU
```

Tu dois voir les 6 variables `TABLEAU_*`.

---

## 📚 Documentation Complète

- **Guide détaillé** : `HEROKU_CONFIG_TABLEAU.md`
- **Guide technique** : `REFRESH_AUTO_6H.md`
- **Test local** : `test_tableau_refresh.py`

---

## 🎯 C'est Tout !

Après configuration, Heroku va **automatiquement télécharger les CSV Tableau à 6h et 23h** ! 🚀

Le code est déjà déployé, il suffit d'ajouter les Config Vars.
