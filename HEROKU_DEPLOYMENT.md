# 🚀 Guide de Déploiement Heroku

## Cloud Field Campaign Scorecard Platform

Ce guide vous aidera à déployer l'application complète (Backend FastAPI + Frontend) sur Heroku.

---

## 📋 Prérequis

### 1. Créer un compte Heroku
- Aller sur https://signup.heroku.com/
- Créer un compte gratuit ou utiliser un compte existant

### 2. Installer Heroku CLI
- **Windows** : Télécharger depuis https://devcenter.heroku.com/articles/heroku-cli
- Ou via Command Prompt :
```bash
winget install Heroku.HerokuCLI
```

### 3. Vérifier l'installation
```bash
heroku --version
```

---

## 🔧 Étape 1 : Préparer le Projet

### 1.1 Initialiser Git (si pas déjà fait)
```bash
cd "C:\Users\ebirot\Desktop\Cloud Field Campaign Scorecard"
git init
```

### 1.2 Ajouter les fichiers
```bash
git add .
git commit -m "Initial commit for Heroku deployment"
```

---

## 🏗️ Étape 2 : Créer l'Application Heroku

### 2.1 Se connecter à Heroku
```bash
heroku login
```
Cela ouvrira votre navigateur pour vous authentifier.

### 2.2 Créer une nouvelle app
```bash
heroku create salesforce-scorecard-emea
```
**Note** : Remplacez `salesforce-scorecard-emea` par le nom que vous voulez (doit être unique).

---

## ⚙️ Étape 3 : Configuration des Variables d'Environnement

### 3.1 Variables obligatoires
```bash
# Database (Heroku Postgres - sera ajouté automatiquement)
# Pas besoin de le faire manuellement

# API Keys (si vous en avez)
heroku config:set TABLEAU_SERVER_URL="https://prod-uswest-c.online.tableau.com"
heroku config:set TABLEAU_SITE_ID="salesforce"
heroku config:set TABLEAU_TOKEN_NAME="your_token_name"
heroku config:set TABLEAU_TOKEN_VALUE="your_token_value"

# Slack (si vous utilisez Slack)
heroku config:set SLACK_BOT_TOKEN="xoxb-your-token"
heroku config:set SLACK_CHANNEL_ID="C123456789"

# CORS (important!)
heroku config:set CORS_ORIGINS="*"
```

### 3.2 Vérifier les variables
```bash
heroku config
```

---

## 📦 Étape 4 : Ajouter Heroku Postgres (Optionnel)

Si votre app utilise une base de données PostgreSQL :

```bash
heroku addons:create heroku-postgresql:mini
```

**Note** : Le plan "mini" est gratuit mais limité. Pour plus de capacité, utilisez `hobby-basic` ($7/mois).

---

## 🚀 Étape 5 : Déployer l'Application

### 5.1 Pousser vers Heroku
```bash
git push heroku main
```

**Si votre branche s'appelle "master"** :
```bash
git push heroku master
```

### 5.2 Vérifier le déploiement
```bash
heroku logs --tail
```

Vous devriez voir :
```
INFO:     Uvicorn running on http://0.0.0.0:xxxxx
INFO:     Application startup complete
```

---

## 🌐 Étape 6 : Accéder à l'Application

### 6.1 Ouvrir l'app
```bash
heroku open
```

Ou visitez directement : `https://salesforce-scorecard-emea.herokuapp.com/`

### 6.2 URLs disponibles
- **Dashboard principal** : https://votre-app.herokuapp.com/
- **API Documentation** : https://votre-app.herokuapp.com/docs
- **Health Check** : https://votre-app.herokuapp.com/health
- **Admin** : https://votre-app.herokuapp.com/admin

---

## 📊 Étape 7 : Uploader les Données CSV

Les fichiers CSV ne sont PAS dans Git (exclus par .gitignore). Vous devez les uploader manuellement.

### Option A : Via Heroku Dashboard
1. Aller sur https://dashboard.heroku.com/
2. Sélectionner votre app
3. Onglet "Settings" → "Config Vars"
4. Ajouter les chemins des fichiers CSV

### Option B : Via Heroku CLI
```bash
heroku run bash
cd data/Email\ Datas/
# Uploader vos CSV ici
```

### Option C : Utiliser un service externe (Recommandé)
- **Google Cloud Storage** : Stocker les CSV sur GCS
- **AWS S3** : Stocker les CSV sur S3
- **Dropbox** : Lien direct vers les fichiers

Modifier le code pour lire depuis l'URL au lieu du filesystem local.

---

## 🔄 Étape 8 : Mises à Jour

### Après chaque modification du code :

```bash
# 1. Commiter les changements
git add .
git commit -m "Description des changements"

# 2. Pousser vers Heroku
git push heroku main

# 3. Vérifier les logs
heroku logs --tail
```

---

## 🐛 Dépannage

### Problème : Application crashe au démarrage
```bash
heroku logs --tail
```
Cherchez les erreurs dans les logs.

### Problème : "No web dyno running"
```bash
heroku ps:scale web=1
```

### Problème : Timeout au démarrage
Augmenter le timeout dans `Procfile` :
```
web: cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT --timeout-keep-alive 120
```

### Problème : Données CSV manquantes
Les CSV ne sont pas sur Heroku. Solutions :
1. Utiliser Heroku S3 / GCS pour stocker les fichiers
2. Modifier le code pour lire depuis une URL externe
3. Utiliser l'API Tableau directement sans CSV

### Problème : Port déjà utilisé
Heroku définit le port automatiquement via `$PORT`. Ne jamais hardcoder le port 8000.

---

## 💰 Coûts Heroku

### Plan Gratuit (Eco Dynos)
- **Prix** : Gratuit
- **Limites** : 
  - 1000 heures/mois (environ 42 jours)
  - L'app s'endort après 30 min d'inactivité
  - Réveil automatique au prochain accès (peut prendre 10-20 secondes)

### Plan Hobby ($7/mois)
- **Prix** : $7/mois par dyno
- **Avantages** :
  - Pas de sleep
  - Metrics inclus
  - Custom domain SSL

### Plan Professional ($25-50/mois)
- **Prix** : $25-50/mois
- **Avantages** :
  - Plusieurs dynos (load balancing)
  - Auto-scaling
  - Support prioritaire

---

## 🔐 Sécurité

### 1. Protéger le mot de passe admin
Dans le code, changer le mot de passe admin :
```javascript
// frontend/js/health_of_cloud.js
const ADMIN_PASSWORD = 'VotreMotDePasseSecurise123!';
```

### 2. Activer HTTPS
Heroku fournit HTTPS automatiquement via `*.herokuapp.com`.

### 3. Limiter les CORS
Au lieu de `CORS_ORIGINS="*"`, spécifier votre domaine :
```bash
heroku config:set CORS_ORIGINS="https://salesforce-scorecard-emea.herokuapp.com"
```

---

## 📈 Monitoring

### Voir les logs en temps réel
```bash
heroku logs --tail
```

### Voir les métriques
```bash
heroku open metrics
```

### Redémarrer l'app
```bash
heroku restart
```

---

## 🎯 Checklist de Déploiement

- [ ] Heroku CLI installé
- [ ] Compte Heroku créé
- [ ] Git initialisé
- [ ] Fichiers committed
- [ ] App Heroku créée
- [ ] Variables d'environnement configurées
- [ ] Code poussé vers Heroku
- [ ] Logs vérifiés (pas d'erreurs)
- [ ] Application accessible via l'URL
- [ ] Données CSV uploadées ou accessible via URL
- [ ] Mot de passe admin changé
- [ ] CORS configuré correctement

---

## 📞 Support

### Documentation Heroku
- Getting Started : https://devcenter.heroku.com/articles/getting-started-with-python
- Deploying Python : https://devcenter.heroku.com/articles/deploying-python
- Logs & Monitoring : https://devcenter.heroku.com/articles/logging

### Commandes Utiles
```bash
# Voir l'état de l'app
heroku ps

# Redémarrer
heroku restart

# Ouvrir dans le navigateur
heroku open

# Accéder au terminal
heroku run bash

# Voir les variables d'environnement
heroku config

# Ajouter une variable
heroku config:set KEY=VALUE

# Supprimer une variable
heroku config:unset KEY
```

---

## ✅ Résumé des Commandes

```bash
# 1. Préparation
cd "C:\Users\ebirot\Desktop\Cloud Field Campaign Scorecard"
git init
git add .
git commit -m "Initial commit"

# 2. Heroku
heroku login
heroku create salesforce-scorecard-emea
heroku config:set CORS_ORIGINS="*"

# 3. Déploiement
git push heroku main

# 4. Vérification
heroku logs --tail
heroku open
```

**Votre application est maintenant déployée ! 🎉**

URL: https://salesforce-scorecard-emea.herokuapp.com/
