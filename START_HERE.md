# 🎯 COMMENCEZ ICI !

## Déployer sur Heroku - Guide Simple

---

## 🤔 Quelle Méthode Choisir ?

### ✅ VOUS AVEZ GITHUB DESKTOP ? → **Option A**
### ✅ VOUS PRÉFÉREZ LA LIGNE DE COMMANDE ? → **Option B**
### ✅ VOUS VOULEZ DU 100% AUTOMATIQUE ? → **Option C**

---

## 🎯 OPTION A : GitHub Desktop (LE PLUS SIMPLE)

**📖 Guide complet** : `DEPLOY_GITHUB_DESKTOP.md`

### En 6 Étapes :

```
1. GitHub Desktop → Add local repository
   📂 Choisir : C:\Users\ebirot\Desktop\Cloud Field Campaign Scorecard

2. Commit → "Initial commit for Heroku"

3. Publish repository → GitHub

4. https://dashboard.heroku.com/ → New → Create app

5. Deploy tab → Connect GitHub → Votre repo

6. Settings tab → Config Vars → CORS_ORIGINS = *
   Deploy tab → Deploy Branch

✅ C'EST EN LIGNE !
```

**Temps estimé** : 10 minutes

---

## 🎯 OPTION B : Ligne de Commande

**📖 Guide complet** : `DEPLOY_VIA_GITHUB.md`

### En 3 Commandes :

```bash
# 1. Pousser sur GitHub
git init
git add .
git commit -m "Deploy to Heroku"
git remote add origin https://github.com/USERNAME/salesforce-scorecard.git
git push -u origin main

# 2. Connecter sur Heroku Dashboard
# https://dashboard.heroku.com/ → Deploy → GitHub → Connect

# 3. Configurer et déployer
# Settings → Config Vars → CORS_ORIGINS = *
# Deploy → Deploy Branch
```

**Temps estimé** : 5 minutes

---

## 🎯 OPTION C : Script Automatique

**📖 Guide complet** : `HEROKU_DEPLOYMENT.md`

### En 1 Commande :

```powershell
# Ouvrir PowerShell dans le dossier du projet
.\deploy-github.ps1

# Suivre les instructions à l'écran
```

**Temps estimé** : 3 minutes

---

## ⚠️ AVANT DE COMMENCER

### ✅ Vérifier que ces fichiers existent :
- [x] `Procfile`
- [x] `runtime.txt`
- [x] `requirements.txt`
- [x] `.gitignore`
- [x] `backend/` (dossier complet)
- [x] `frontend/` (dossier complet)

**TOUS LES FICHIERS SONT DÉJÀ PRÊTS ! ✅**

---

## 🗂️ Structure du Projet

```
Cloud Field Campaign Scorecard/
│
├── backend/                    ← Backend FastAPI
│   ├── app/
│   │   ├── main.py            ← Point d'entrée
│   │   ├── api/               ← Endpoints API
│   │   └── services/          ← Parsers
│   └── data/
│       └── mappings/          ← Mappings JSON
│
├── frontend/                   ← Frontend HTML/JS
│   ├── health_of_cloud_v2.html
│   ├── js/
│   └── css/
│
├── Procfile                    ← Commande Heroku ✅
├── runtime.txt                 ← Python version ✅
├── requirements.txt            ← Dépendances ✅
├── .gitignore                  ← Exclusions ✅
│
└── DEPLOY_*.md                 ← Guides 📚
```

---

## 🌐 APRÈS LE DÉPLOIEMENT

Votre app sera accessible sur :

**https://VOTRE-APP.herokuapp.com/**

- 🏠 Dashboard principal : `/`
- 📊 Documentation API : `/docs`
- 💚 Health check : `/health`
- ⚙️ Admin (mappings) : `/admin`

**Mot de passe admin** : `admin`

---

## 🔄 WORKFLOW QUOTIDIEN

Après le déploiement, pour mettre à jour :

### Avec GitHub Desktop :
```
1. Modifier le code
2. GitHub Desktop → Commit
3. Push origin
4. Heroku déploie automatiquement ✅
```

### Avec Git CLI :
```bash
git add .
git commit -m "Description du changement"
git push origin main
# Heroku déploie automatiquement ✅
```

---

## 🎯 CONFIGURATION HEROKU

### Variables d'Environnement à Ajouter

**OBLIGATOIRE** :
- `CORS_ORIGINS` = `*`

**Optionnel** (si vous avez Tableau API) :
- `TABLEAU_SERVER_URL` = `https://prod-uswest-c.online.tableau.com`
- `TABLEAU_SITE_ID` = `salesforce`
- `TABLEAU_TOKEN_NAME` = `votre_token`
- `TABLEAU_TOKEN_VALUE` = `votre_valeur`

**Voir** : `.env.example` pour toutes les variables

---

## ⚠️ IMPORTANT : Données CSV

Les fichiers CSV **NE SONT PAS** uploadés sur Heroku.

**Pourquoi ?**
- Trop volumineux (plusieurs Go)
- Git n'est pas fait pour ça
- `.gitignore` les exclut automatiquement

**Solution Recommandée** :
1. Stocker sur **Google Cloud Storage** ou **AWS S3**
2. Modifier le code pour lire depuis l'URL
3. OU utiliser l'API Tableau directement

**Solution Temporaire** (pour tester) :
```bash
heroku run bash --app votre-app
cd data
# Uploader manuellement
```

---

## 🐛 PROBLÈMES COURANTS

### L'app ne démarre pas
```bash
heroku logs --tail --app votre-app
```
Vérifier les erreurs dans les logs.

### Données ne s'affichent pas
→ Les CSV ne sont pas sur Heroku (voir ci-dessus)

### GitHub ne connecte pas
→ Vérifier que le repo est public ou que Heroku a les permissions

---

## 📚 GUIDES DÉTAILLÉS

Choisissez selon votre méthode :

| Guide | Pour Qui | Temps |
|-------|----------|-------|
| **DEPLOY_GITHUB_DESKTOP.md** | GitHub Desktop | 10 min |
| **DEPLOY_VIA_GITHUB.md** | Git CLI + GitHub | 5 min |
| **HEROKU_DEPLOYMENT.md** | Guide complet détaillé | 20 min |
| **DEPLOY_QUICK_START.md** | Résumé ultra-rapide | 3 min |

---

## 💰 COÛTS HEROKU

### 🆓 Gratuit (Eco Dynos)
- 1000 heures/mois
- App s'endort après 30 min d'inactivité
- Parfait pour tester

### 💵 Hobby ($7/mois)
- Pas de sleep
- Custom domain
- Recommandé pour production

---

## ✅ CHECKLIST

Avant de déployer :
- [ ] Code testé en local (http://localhost:8000)
- [ ] Fichiers Heroku prêts (Procfile, runtime.txt, requirements.txt)
- [ ] Compte GitHub créé
- [ ] Compte Heroku créé
- [ ] Guide choisi

Pendant le déploiement :
- [ ] Code sur GitHub
- [ ] App Heroku créée
- [ ] GitHub connecté à Heroku
- [ ] Variables d'environnement configurées
- [ ] Deploy Branch cliqué

Après le déploiement :
- [ ] App accessible via l'URL
- [ ] API Docs fonctionne (/docs)
- [ ] Admin accessible (/admin)
- [ ] Auto-deploy activé

---

## 🚀 PRÊT ? C'EST PARTI !

### Recommandation :

**🎯 Méthode la plus simple** : GitHub Desktop
→ Ouvrir `DEPLOY_GITHUB_DESKTOP.md`

**💡 Déjà à l'aise avec Git** : Git CLI
→ Ouvrir `DEPLOY_VIA_GITHUB.md`

**⚡ Vite fait bien fait** : Script auto
→ Lancer `.\deploy-github.ps1`

---

**Bon déploiement ! 🎉**

*Des questions ? Tous les guides sont dans le dossier du projet.*
