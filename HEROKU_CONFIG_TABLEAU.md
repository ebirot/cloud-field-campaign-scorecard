# 🚀 Configuration Heroku - Tableau Auto-Refresh

## ✅ Ce qui est Déjà Fait

Le code est **déjà poussé sur GitHub** avec :
- ✅ APScheduler dans `requirements.txt`
- ✅ Scheduler configuré pour 6h et 23h (Europe/Paris)
- ✅ Intégration dans `main.py` (démarrage automatique)

---

## ⚙️ Ce qu'il Faut Configurer sur Heroku

### 🔐 Ajouter les Config Vars Tableau

Heroku a besoin des credentials Tableau pour télécharger les CSV.

#### Option A : Via Heroku Dashboard (LE PLUS SIMPLE)

1. **Aller sur** : https://dashboard.heroku.com/

2. **Sélectionner ton app** (ex: `salesforce-scorecard-emea`)

3. **Onglet "Settings"** → Section **"Config Vars"** → Cliquer **"Reveal Config Vars"**

4. **Ajouter ces 3 variables** (une par une) :

| KEY | VALUE |
|-----|-------|
| `TABLEAU_SERVER_URL` | `https://prod-uswest-c.online.tableau.com` |
| `TABLEAU_SITE_ID` | `salesforce` |
| `TABLEAU_TOKEN_NAME` | `Token_Claude_CFM_Scorecard` |
| `TABLEAU_TOKEN_VALUE` | Voir ton fichier `.env` local |
| `TABLEAU_WORKBOOK_MDP_SCORECARD` | Voir ton fichier `.env` local |
| `TABLEAU_API_VERSION` | `3.19` |

**IMPORTANT** : Les valeurs `TABLEAU_TOKEN_VALUE` et `TABLEAU_WORKBOOK_MDP_SCORECARD` sont dans ton fichier :
```
C:\Users\ebirot\Desktop\Cloud Field Campaign Scorecard\backend\.env
```

5. **Cliquer "Add"** après chaque variable

---

#### Option B : Via Heroku CLI

```bash
# Se connecter à Heroku
heroku login

# Ajouter les Config Vars (remplace YOUR-APP-NAME)
heroku config:set TABLEAU_SERVER_URL="https://prod-uswest-c.online.tableau.com" --app YOUR-APP-NAME
heroku config:set TABLEAU_SITE_ID="salesforce" --app YOUR-APP-NAME
heroku config:set TABLEAU_TOKEN_NAME="Token_Claude_CFM_Scorecard" --app YOUR-APP-NAME
heroku config:set TABLEAU_API_VERSION="3.19" --app YOUR-APP-NAME

# Pour TABLEAU_TOKEN_VALUE et TABLEAU_WORKBOOK_MDP_SCORECARD
# Copie les valeurs depuis ton .env local
heroku config:set TABLEAU_TOKEN_VALUE="ta-valeur-ici" --app YOUR-APP-NAME
heroku config:set TABLEAU_WORKBOOK_MDP_SCORECARD="ta-valeur-ici" --app YOUR-APP-NAME
```

---

## 🔄 Déployer les Changements sur Heroku

### Si Auto-Deploy est Activé (Recommandé)

**C'est automatique !** Heroku va détecter le push sur GitHub et déployer.

Vérifie dans Heroku Dashboard :
- Onglet **"Deploy"**
- Section **"Automatic deploys"**
- Doit être ✅ **"Enable Automatic Deploys"**

### Si Auto-Deploy n'est PAS Activé

#### Option 1 : Activer Auto-Deploy

1. Dashboard → Ton app → **Deploy**
2. Section **"Automatic deploys"**
3. Cliquer **"Enable Automatic Deploys"**
4. Cliquer **"Deploy Branch"** (une seule fois pour maintenant)

#### Option 2 : Déployer Manuellement

1. Dashboard → Ton app → **Deploy**
2. Section **"Manual deploy"**
3. Sélectionner **"main"**
4. Cliquer **"Deploy Branch"**

---

## ✅ Vérifier que Tout Fonctionne

### 1. Vérifier le Déploiement

```bash
# Voir les logs en temps réel
heroku logs --tail --app YOUR-APP-NAME
```

Tu dois voir :
```
🚀 Starting Cloud Field Campaign Scorecard...
✅ Task scheduler started
📅 CSV refresh scheduled: 06:00 CET and 23:00 CET daily
✅ Application startup complete
```

### 2. Vérifier les Config Vars

```bash
heroku config --app YOUR-APP-NAME
```

Tu dois voir toutes les variables Tableau listées.

### 3. Tester le Scheduler via l'API

Ouvre dans ton navigateur :
```
https://YOUR-APP-NAME.herokuapp.com/api/refresh/status
```

Réponse attendue :
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

### 4. Déclencher un Refresh Manuel (Test)

```bash
curl -X POST https://YOUR-APP-NAME.herokuapp.com/api/refresh/trigger
```

Ou via l'interface Swagger :
```
https://YOUR-APP-NAME.herokuapp.com/docs
```

---

## 📂 Où Vont les CSV sur Heroku ?

Les CSV sont sauvegardés dans le système de fichiers **éphémère** de Heroku dans :
```
/app/data/csv/
```

⚠️ **IMPORTANT** : Le système de fichiers Heroku est **éphémère** :
- Les fichiers sont recréés à chaque redémarrage du dyno
- Les fichiers persistent pendant l'exécution
- Le scheduler les recharge automatiquement à 6h et 23h

**C'est OK** car les CSV sont rafraîchis automatiquement 2x par jour !

---

## 🎯 Checklist Configuration Heroku

- [ ] Code poussé sur GitHub (commit `b4f49d1`)
- [ ] Config Vars Tableau ajoutées sur Heroku
  - [ ] `TABLEAU_SERVER_URL`
  - [ ] `TABLEAU_SITE_ID`
  - [ ] `TABLEAU_TOKEN_NAME`
  - [ ] `TABLEAU_TOKEN_VALUE`
  - [ ] `TABLEAU_WORKBOOK_MDP_SCORECARD`
  - [ ] `TABLEAU_API_VERSION`
- [ ] Auto-deploy activé (ou déployé manuellement)
- [ ] Logs vérifiés : scheduler démarré ✅
- [ ] API `/api/refresh/status` fonctionne
- [ ] Test refresh manuel réussi

---

## 🐛 Troubleshooting Heroku

### Problème : "No module named 'apscheduler'"

**Cause** : Le déploiement n'a pas détecté le nouveau `requirements.txt`

**Solution** :
```bash
# Force un nouveau build
heroku builds:create --app YOUR-APP-NAME
```

### Problème : "401 Unauthorized" dans les logs Tableau

**Cause** : Config Vars Tableau mal configurées

**Solution** :
1. Vérifie les Config Vars :
```bash
heroku config --app YOUR-APP-NAME | grep TABLEAU
```

2. Compare avec ton `.env` local

3. Remets la bonne valeur :
```bash
heroku config:set TABLEAU_TOKEN_VALUE="bonne-valeur" --app YOUR-APP-NAME
```

### Problème : Scheduler ne démarre pas

**Cause** : Erreur au démarrage de l'app

**Solution** :
```bash
# Voir les logs détaillés
heroku logs --tail --app YOUR-APP-NAME

# Redémarrer l'app
heroku restart --app YOUR-APP-NAME
```

### Problème : CSV ne se téléchargent pas

**Cause** : Dossier `data/csv/` n'existe pas

**Vérification** :
```bash
heroku run bash --app YOUR-APP-NAME
ls -la data/csv/
```

**Solution** : Le code crée automatiquement le dossier. Si absent, c'est un problème de déploiement.

---

## 📅 Prochains Refreshes

Une fois configuré, Heroku téléchargera automatiquement les CSV :

- 🌅 **Chaque matin à 6h00** (heure française)
- 🌙 **Chaque soir à 23h00** (heure française)

---

## 💰 Impact sur les Coûts Heroku

Le scheduler utilise **0 dyno supplémentaire** :
- Il tourne dans le même dyno que le backend
- Pas de coût additionnel
- Les refreshes prennent ~10-30 secondes

---

## ✅ Résumé des Commandes

```bash
# 1. Vérifier le nom de ton app Heroku
heroku apps

# 2. Ajouter les Config Vars (remplace YOUR-APP-NAME et les valeurs)
heroku config:set TABLEAU_SERVER_URL="https://prod-uswest-c.online.tableau.com" --app YOUR-APP-NAME
heroku config:set TABLEAU_SITE_ID="salesforce" --app YOUR-APP-NAME
heroku config:set TABLEAU_TOKEN_NAME="Token_Claude_CFM_Scorecard" --app YOUR-APP-NAME
heroku config:set TABLEAU_TOKEN_VALUE="ta-valeur" --app YOUR-APP-NAME
heroku config:set TABLEAU_WORKBOOK_MDP_SCORECARD="ta-valeur" --app YOUR-APP-NAME
heroku config:set TABLEAU_API_VERSION="3.19" --app YOUR-APP-NAME

# 3. Vérifier
heroku config --app YOUR-APP-NAME

# 4. Voir les logs
heroku logs --tail --app YOUR-APP-NAME

# 5. Tester l'API
curl https://YOUR-APP-NAME.herokuapp.com/api/refresh/status
```

---

## 🎉 C'est Prêt !

Une fois les Config Vars ajoutées, **Heroku va automatiquement refresher les CSV à 6h et 23h** ! 🚀

Le système est **100% automatique**, pas besoin d'intervention manuelle.
