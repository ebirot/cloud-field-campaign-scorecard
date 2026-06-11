# 🚀 Quick Start - Déploiement Heroku

## En 5 Minutes !

### 1️⃣ Installer Heroku CLI
```bash
winget install Heroku.HerokuCLI
```

### 2️⃣ Se connecter
```bash
heroku login
```

### 3️⃣ Initialiser Git
```bash
cd "C:\Users\ebirot\Desktop\Cloud Field Campaign Scorecard"
git init
git add .
git commit -m "Ready for Heroku"
```

### 4️⃣ Créer l'app Heroku
```bash
heroku create salesforce-scorecard
```

### 5️⃣ Déployer !
```bash
git push heroku main
```

### 6️⃣ Ouvrir l'app
```bash
heroku open
```

---

## ✅ Fichiers Créés pour Heroku

- ✅ `Procfile` - Commande de démarrage
- ✅ `runtime.txt` - Version Python
- ✅ `requirements.txt` - Dépendances Python
- ✅ `.gitignore` - Fichiers à ignorer
- ✅ `.env.example` - Template variables d'environnement

---

## 🌐 Votre App Sera Accessible Sur

**https://salesforce-scorecard.herokuapp.com/**

- Dashboard : `/`
- API Docs : `/docs`
- Health Check : `/health`
- Admin : `/admin`

---

## ⚠️ Important

### Données CSV
Les fichiers CSV ne sont **PAS** uploadés sur Heroku (trop volumineux).

**Solutions** :
1. **Recommandé** : Stocker sur Google Cloud Storage / AWS S3
2. Utiliser l'API Tableau directement
3. Uploader manuellement via `heroku run bash`

### Variables d'Environnement
Configurer après le déploiement :
```bash
heroku config:set CORS_ORIGINS="*"
```

---

## 📖 Documentation Complète

Voir **`HEROKU_DEPLOYMENT.md`** pour le guide détaillé.

---

## 🐛 Problème ?

**Voir les logs** :
```bash
heroku logs --tail
```

**Redémarrer** :
```bash
heroku restart
```

**Vérifier le status** :
```bash
heroku ps
```
