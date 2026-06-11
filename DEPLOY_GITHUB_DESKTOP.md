# 🚀 Déploiement avec GitHub Desktop

## Guide Simple pour GitHub Desktop → Heroku

---

## 📂 Étape 1 : Préparer le Projet

### Option A : Copier le projet dans le dossier GitHub
1. Copier le dossier **"Cloud Field Campaign Scorecard"**
2. Coller dans votre dossier GitHub (ex: `C:\Users\ebirot\Documents\GitHub\`)
3. Renommer si besoin : `salesforce-scorecard`

### Option B : Utiliser l'emplacement actuel
Vous pouvez laisser le projet où il est actuellement et l'ajouter à GitHub Desktop.

---

## 🎯 Étape 2 : Ajouter le Projet dans GitHub Desktop

### 2.1 Ouvrir GitHub Desktop
Lancez **GitHub Desktop**

### 2.2 Ajouter le Repository
1. Cliquer **File** → **Add local repository**
2. Ou cliquer **Current Repository** (en haut à gauche) → **Add** → **Add existing repository**

### 2.3 Sélectionner le Dossier
- Cliquer **Choose...**
- Naviguer vers votre projet :
  ```
  C:\Users\ebirot\Desktop\Cloud Field Campaign Scorecard
  ```
  ou
  ```
  C:\Users\ebirot\Documents\GitHub\salesforce-scorecard
  ```

### 2.4 Initialiser Git (si besoin)
Si GitHub Desktop dit "This directory does not appear to be a Git repository":
- Cliquer **Create a repository**
- OU dans le terminal :
  ```bash
  cd "C:\Users\ebirot\Desktop\Cloud Field Campaign Scorecard"
  git init
  ```

---

## 📤 Étape 3 : Publier sur GitHub

### 3.1 Vérifier les Fichiers
Dans GitHub Desktop, vous verrez tous les fichiers à ajouter dans la liste de gauche.

**Fichiers importants qui DOIVENT être inclus :**
- ✅ `Procfile`
- ✅ `runtime.txt`
- ✅ `requirements.txt`
- ✅ `.gitignore`
- ✅ `backend/` (tout le dossier)
- ✅ `frontend/` (tout le dossier)

**Fichiers qui NE DOIVENT PAS être inclus** (déjà exclus par .gitignore):
- ❌ `venv/`
- ❌ `__pycache__/`
- ❌ `*.csv`
- ❌ `.env`

### 3.2 Premier Commit
En bas à gauche de GitHub Desktop :
1. **Summary** : `Initial commit for Heroku deployment`
2. **Description** (optionnel) : `Ready to deploy to Heroku via GitHub`
3. Cliquer **Commit to main**

### 3.3 Publier sur GitHub
1. Cliquer **Publish repository** (en haut)
2. Une fenêtre s'ouvre :
   - **Name** : `salesforce-scorecard` (ou autre nom)
   - **Description** : `Cloud Field Campaign Scorecard Platform`
   - ⚠️ **Décocher** "Keep this code private" (si vous voulez public)
   - OU **Cocher** si vous voulez garder privé
3. Cliquer **Publish repository**

✅ **Votre code est maintenant sur GitHub !**

---

## 🔗 Étape 4 : Connecter GitHub à Heroku

### 4.1 Ouvrir Heroku Dashboard
Aller sur https://dashboard.heroku.com/

### 4.2 Créer une Nouvelle App
1. Cliquer **New** → **Create new app**
2. **App name** : `salesforce-scorecard-emea` (doit être unique)
3. **Region** : **Europe** (recommandé) ou United States
4. Cliquer **Create app**

### 4.3 Connecter GitHub
1. Dans l'onglet **Deploy**
2. Section **Deployment method**
3. Cliquer sur l'icône **GitHub**
4. Cliquer **Connect to GitHub** (si pas déjà connecté)
5. Autoriser Heroku à accéder à GitHub (si demandé)

### 4.4 Chercher votre Repo
1. Dans le champ de recherche, taper : `salesforce-scorecard`
2. Cliquer **Search**
3. Votre repo apparaît → Cliquer **Connect**

✅ **GitHub et Heroku sont maintenant connectés !**

---

## 🚀 Étape 5 : Déployer l'Application

### 5.1 Configuration Variables d'Environnement (Important !)
Avant de déployer, configurer les variables :

1. Aller dans l'onglet **Settings**
2. Section **Config Vars**
3. Cliquer **Reveal Config Vars**
4. Ajouter :
   | KEY | VALUE |
   |-----|-------|
   | `CORS_ORIGINS` | `*` |

5. Cliquer **Add** pour chaque variable

### 5.2 Déploiement Manuel (Première fois)
1. Retourner dans l'onglet **Deploy**
2. Section **Manual deploy**
3. Choisir la branche : **main**
4. Cliquer **Deploy Branch**

**Attendez 2-3 minutes...**

Vous verrez :
```
-----> Building on the Heroku-22 stack
-----> Using buildpack: heroku/python
-----> Python app detected
-----> Installing python-3.11.9
-----> Installing pip dependencies
       Collecting fastapi
       ...
-----> Discovering process types
       Procfile declares types -> web
-----> Launching...
       Released v1
       https://salesforce-scorecard-emea.herokuapp.com/ deployed to Heroku
```

✅ **Déployé !**

### 5.3 Activer le Déploiement Automatique (Optionnel mais Recommandé)
1. Section **Automatic deploys**
2. Choisir la branche : **main**
3. Cliquer **Enable Automatic Deploys**

**Maintenant, chaque fois que vous faites un push sur GitHub, Heroku déploie automatiquement !**

---

## 🔄 Étape 6 : Workflow Quotidien

### Quand vous modifiez du code :

**Dans GitHub Desktop :**

1. **Modifier votre code** (VS Code, Notepad++, etc.)
2. **Ouvrir GitHub Desktop**
   - Les modifications apparaissent automatiquement dans la liste
3. **Commit** (en bas à gauche) :
   - Summary : `Fix bug in email parser` (par exemple)
   - Cliquer **Commit to main**
4. **Push** (en haut) :
   - Cliquer **Push origin**

**Sur Heroku :**
- Si auto-deploy activé → **Déploiement automatique !**
- Sinon → Aller dans Deploy tab → Deploy Branch

---

## 🌐 Accéder à votre Application

**URL** : https://salesforce-scorecard-emea.herokuapp.com/

- 🏠 **Dashboard** : `/`
- 📊 **API Docs** : `/docs`
- 💚 **Health Check** : `/health`
- ⚙️ **Admin** : `/admin`

---

## 📊 Voir les Logs

### Méthode 1 : Heroku Dashboard
1. Onglet **More** → **View logs**

### Méthode 2 : Heroku CLI (si installé)
```bash
heroku logs --tail --app salesforce-scorecard-emea
```

---

## 🎯 Checklist Complète

### Préparation
- [x] Fichiers Heroku créés (Procfile, runtime.txt, requirements.txt)
- [ ] Projet dans un dossier accessible

### GitHub Desktop
- [ ] Projet ajouté dans GitHub Desktop
- [ ] Premier commit fait
- [ ] Publié sur GitHub

### Heroku
- [ ] App Heroku créée
- [ ] GitHub connecté à Heroku
- [ ] Variables d'environnement configurées (CORS_ORIGINS)
- [ ] Première déploiement manuel fait
- [ ] Auto-deploy activé (optionnel)
- [ ] Application testée et fonctionnelle

---

## 🐛 Problèmes Courants

### GitHub Desktop ne trouve pas le repo
**Solution** : Initialiser Git d'abord
```bash
cd "C:\Users\ebirot\Desktop\Cloud Field Campaign Scorecard"
git init
```
Puis rouvrir GitHub Desktop.

### Heroku ne trouve pas mon repo GitHub
**Solutions** :
1. Vérifier que le repo est bien publié (visible sur github.com)
2. Reconnecter GitHub dans Heroku Settings
3. Vérifier les permissions GitHub

### Application Heroku crash au démarrage
**Solutions** :
1. Vérifier les logs : Heroku Dashboard → More → View logs
2. Vérifier que `Procfile` est à la racine du projet
3. Vérifier `runtime.txt` (Python 3.11.9)
4. Vérifier que CORS_ORIGINS est configuré

### Données ne s'affichent pas
**Cause** : Les fichiers CSV ne sont pas sur Heroku (.gitignore les exclut)
**Solutions** :
1. Utiliser Google Cloud Storage / AWS S3
2. Configurer l'app pour lire depuis une URL externe
3. Pour tester : uploader manuellement via `heroku run bash`

---

## 💡 Conseils

### Messages de Commit Clairs
❌ `update`
✅ `Fix email parser FY2027 filtering`

❌ `changes`
✅ `Add admin password validation`

### Tester en Local d'Abord
Avant de push sur GitHub :
```bash
cd backend
uvicorn app.main:app --reload
```
Vérifier que tout fonctionne à http://localhost:8000

### Branches pour Features (Optionnel)
Pour des gros changements :
1. GitHub Desktop → **Current Branch** → **New Branch**
2. Nom : `feature-add-export`
3. Travailler sur la feature
4. Merger dans `main` quand terminé

---

## ✨ Résumé Ultra-Rapide

1. **GitHub Desktop** → Add local repository → Votre projet
2. **Commit** → "Initial commit"
3. **Publish repository** → GitHub
4. **Heroku Dashboard** → New app
5. **Deploy tab** → Connect GitHub → Votre repo
6. **Settings tab** → Config Vars → CORS_ORIGINS = *
7. **Deploy tab** → Deploy Branch
8. **C'est en ligne !** 🎉

---

## 📞 Liens Utiles

- GitHub Desktop : https://desktop.github.com/
- Heroku Dashboard : https://dashboard.heroku.com/
- Votre code sur GitHub : https://github.com/USERNAME/salesforce-scorecard

---

**Vous êtes prêt ! 🚀**
