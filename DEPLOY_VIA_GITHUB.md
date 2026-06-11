# 🚀 Déploiement via GitHub → Heroku

## Méthode la plus simple ! (GitHub déjà connecté)

---

## 📋 Étapes Rapides

### 1️⃣ Pousser vers GitHub

```bash
cd "C:\Users\ebirot\Desktop\Cloud Field Campaign Scorecard"

# Si repo pas encore créé sur GitHub
git init
git add .
git commit -m "Ready for Heroku deployment"

# Créer repo sur GitHub et ajouter remote
git remote add origin https://github.com/VOTRE-USERNAME/salesforce-scorecard.git
git branch -M main
git push -u origin main
```

---

### 2️⃣ Créer l'App Heroku (via Dashboard)

1. Aller sur https://dashboard.heroku.com/
2. Cliquer **"New"** → **"Create new app"**
3. Nom de l'app : `salesforce-scorecard-emea`
4. Région : **Europe** ou **United States**
5. Cliquer **"Create app"**

---

### 3️⃣ Connecter GitHub à Heroku

1. Dans l'app Heroku, onglet **"Deploy"**
2. Section **"Deployment method"** → Cliquer **"GitHub"**
3. Cliquer **"Connect to GitHub"** (si pas déjà fait)
4. Chercher votre repo : `salesforce-scorecard`
5. Cliquer **"Connect"**

✅ **GitHub est maintenant connecté !**

---

### 4️⃣ Activer le Déploiement Automatique (Optionnel)

Dans la section **"Automatic deploys"** :
- Choisir la branche : `main`
- Cliquer **"Enable Automatic Deploys"**

**Maintenant, chaque push sur GitHub déploiera automatiquement sur Heroku !**

---

### 5️⃣ Déployer Manuellement (Première fois)

Dans la section **"Manual deploy"** :
- Choisir la branche : `main`
- Cliquer **"Deploy Branch"**

**Attendez quelques minutes...**

Vous verrez :
```
-----> Building on the Heroku-22 stack
-----> Using buildpack: heroku/python
-----> Python app detected
-----> Installing python-3.11.9
-----> Installing pip dependencies
-----> Discovering process types
       Procfile declares types -> web
-----> Compressing...
       Done: 52.3M
-----> Launching...
       Released v1
       https://salesforce-scorecard-emea.herokuapp.com/ deployed to Heroku
```

✅ **Déployé !**

---

## 🔄 Workflow Après Configuration

### Pour mettre à jour l'application :

```bash
# 1. Faire vos modifications dans le code
# 2. Commit
git add .
git commit -m "Description des changements"

# 3. Push vers GitHub
git push origin main

# 4. Heroku déploie automatiquement !
```

**C'est tout ! Pas besoin de `git push heroku main`**

---

## ⚙️ Configuration Variables d'Environnement

### Via Dashboard Heroku :
1. Onglet **"Settings"**
2. Section **"Config Vars"**
3. Cliquer **"Reveal Config Vars"**
4. Ajouter :
   - `CORS_ORIGINS` = `*`
   - `TABLEAU_SERVER_URL` = `https://...` (si nécessaire)
   - etc.

### Via CLI :
```bash
heroku config:set CORS_ORIGINS="*" --app salesforce-scorecard-emea
```

---

## 📊 Voir les Logs

### Via Dashboard :
1. Onglet **"More"** → **"View logs"**

### Via CLI :
```bash
heroku logs --tail --app salesforce-scorecard-emea
```

---

## 🌐 Accéder à l'App

**URL** : https://salesforce-scorecard-emea.herokuapp.com/

- Dashboard : `/`
- API Docs : `/docs`
- Health : `/health`
- Admin : `/admin`

---

## 🔧 Avantages de GitHub → Heroku

✅ **Auto-déploiement** : Chaque push → déploie automatiquement  
✅ **Review Apps** : Créer des apps temporaires pour chaque PR  
✅ **Pipeline CI/CD** : Intégration avec GitHub Actions  
✅ **Rollback facile** : Revenir à une version précédente en 1 clic  
✅ **Historique** : Voir tous les déploiements passés  

---

## 🎯 Checklist

- [x] Fichiers Heroku créés (Procfile, runtime.txt, requirements.txt)
- [ ] Code poussé sur GitHub
- [ ] App Heroku créée
- [ ] GitHub connecté à Heroku
- [ ] Branche `main` déployée
- [ ] Variables d'environnement configurées
- [ ] Application accessible et fonctionnelle
- [ ] Auto-déploiement activé (optionnel)

---

## 🐛 Troubleshooting

### App ne démarre pas
- Vérifier les logs : `heroku logs --tail`
- Vérifier que `Procfile` est à la racine
- Vérifier `runtime.txt` (Python 3.11.9)

### GitHub pas dans la liste des repos
- Reconnectez GitHub dans les paramètres Heroku
- Vérifiez les permissions de l'app GitHub

### Déploiement échoue
- Vérifier `requirements.txt` (pas d'erreurs de dépendances)
- Vérifier que le backend démarre en local

---

## ✨ C'est tout !

Votre workflow maintenant :
1. **Coder** 💻
2. **Commit** 📝
3. **Push vers GitHub** 🚀
4. **Heroku déploie automatiquement** ✅

**Plus simple que ça, impossible ! 🎉**
