# ☁️ Cloud Field Campaign Scorecard

## Platform de Suivi des Campagnes Field Salesforce

Application web complète pour suivre et analyser les performances des campagnes marketing Field de Salesforce EMEA et AMER.

---

## 🚀 Fonctionnalités

### 📊 Dashboards Multiples
- **Health of Cloud** : Vue détaillée par Cloud (Agentforce, Sales, Service, etc.)
- **Email Scorecard** : Analyse des performances emails par région et produit
- **Lead Scorecard** : Suivi de la génération et qualification des leads
- **Webinar Scorecard** : Métriques de participation et engagement webinaires

### ⚙️ Administration Dynamique
- **Country Mapping** : Gestion des associations pays → Operating Units
- **Product Mapping** : Configuration des associations produits → Clouds
- **Interface Intuitive** : Modals avec dropdowns, recherche, statistiques
- **Hot Reload** : Changements pris en compte immédiatement

### 🔐 Sécurité
- Authentification admin avec modal élégant
- Gestion des permissions par onglet
- Protection des endpoints API

### 📈 Filtres Avancés
- Par Fiscal Quarter (Q1, Q2, Q3, Q4)
- Par Fiscal Year (FY2027 par défaut)
- Par Operating Unit (France, UKI, Central, etc.)
- Par Cloud/Produit
- Par Région (EMEA/AMER)

---

## 🛠️ Stack Technique

### Backend
- **FastAPI** (Python 3.11+)
- **Uvicorn** ASGI server
- **Pandas** pour l'analyse de données CSV
- **JSON** pour les mappings dynamiques

### Frontend
- **Vanilla JavaScript** (ES6+)
- **HTML5/CSS3**
- **Fetch API** pour les requêtes
- Design responsive

### Infrastructure
- **Heroku** pour l'hébergement
- **GitHub** pour le contrôle de version
- **Auto-deployment** via GitHub → Heroku

---

## 📁 Structure du Projet

```
salesforce-scorecard/
│
├── backend/
│   ├── app/
│   │   ├── main.py              # Point d'entrée FastAPI
│   │   ├── api/
│   │   │   ├── email.py         # Endpoint email scorecard
│   │   │   ├── health.py        # Endpoint health of cloud
│   │   │   ├── leads.py         # Endpoint lead scorecard
│   │   │   ├── webinar.py       # Endpoint webinar scorecard
│   │   │   └── mappings.py      # Endpoint admin mappings
│   │   └── services/
│   │       ├── email_parser.py  # Parser CSV emails
│   │       ├── health_parser.py # Parser health of cloud
│   │       ├── lead_parser.py   # Parser leads
│   │       └── webinar_parser.py# Parser webinars
│   └── data/
│       ├── mappings/            # Mappings JSON (country/product)
│       └── Email Datas/         # CSV data files
│
├── frontend/
│   ├── health_of_cloud_v2.html  # Dashboard principal
│   ├── js/
│   │   ├── health_of_cloud.js   # Logique principale
│   │   └── admin_mappings.js    # Admin interface
│   ├── css/
│   └── public/                  # Assets statiques
│
├── Procfile                     # Configuration Heroku
├── runtime.txt                  # Version Python
├── requirements.txt             # Dépendances Python
├── .gitignore                   # Fichiers exclus
├── .env.example                 # Template variables environnement
│
└── README.md                    # Ce fichier
```

---

## 📦 Installation Locale

### Prérequis
- Python 3.11+
- pip
- Git

### Étapes

```bash
# 1. Cloner le repo
git clone https://github.com/VOTRE-USERNAME/salesforce-scorecard.git
cd salesforce-scorecard

# 2. Créer environnement virtuel
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Installer dépendances
pip install -r requirements.txt

# 4. Lancer le serveur
cd backend
uvicorn app.main:app --reload

# 5. Accéder à l'app
# http://localhost:8000
```

---

## 🚀 Déploiement sur Heroku

### Méthode Recommandée : GitHub → Heroku

**📖 Guide complet** : Voir `START_HERE.md`

### Résumé Rapide

```bash
# 1. Pousser sur GitHub
git init
git add .
git commit -m "Deploy to Heroku"
git push origin main

# 2. Sur Heroku Dashboard
# → New app
# → Deploy → GitHub → Connect repo
# → Settings → Config Vars → CORS_ORIGINS = *
# → Deploy → Deploy Branch

# 3. C'est en ligne !
```

**Guides disponibles** :
- `START_HERE.md` - Commencez ici
- `DEPLOY_GITHUB_DESKTOP.md` - Avec GitHub Desktop
- `DEPLOY_VIA_GITHUB.md` - Avec Git CLI
- `HEROKU_DEPLOYMENT.md` - Guide complet

---

## 🌐 URLs de l'Application

### Production (Heroku)
- **Dashboard** : `https://votre-app.herokuapp.com/`
- **API Docs** : `https://votre-app.herokuapp.com/docs`
- **Health Check** : `https://votre-app.herokuapp.com/health`
- **Admin** : `https://votre-app.herokuapp.com/admin`

### Local
- **Dashboard** : `http://localhost:8000/`
- **API Docs** : `http://localhost:8000/docs`
- **Health Check** : `http://localhost:8000/health`
- **Admin** : `http://localhost:8000/admin`

**Credentials Admin** : `admin` / `admin`

---

## ⚙️ Configuration

### Variables d'Environnement

Créer un fichier `.env` (local) ou Config Vars (Heroku) :

```bash
# CORS (obligatoire)
CORS_ORIGINS=*

# Tableau API (optionnel)
TABLEAU_SERVER_URL=https://prod-uswest-c.online.tableau.com
TABLEAU_SITE_ID=salesforce
TABLEAU_TOKEN_NAME=your_token
TABLEAU_TOKEN_VALUE=your_value

# Slack (optionnel)
SLACK_BOT_TOKEN=xoxb-your-token
SLACK_CHANNEL_ID=C123456789
```

Voir `.env.example` pour la liste complète.

---

## 🎯 Utilisation

### 1. Accéder au Dashboard
Ouvrir l'URL de l'application dans votre navigateur.

### 2. Naviguer entre les Onglets
- **Health of Cloud** : Performances par Cloud
- **Email** : Analyse emails par région
- **Leads** : Génération de leads
- **Webinar** : Engagement webinaires

### 3. Filtrer les Données
- Sélectionner **Fiscal Quarter** (Q1, Q2, Q3, Q4)
- Sélectionner **Operating Unit** (France, UKI, etc.)
- Les données se rechargent automatiquement

### 4. Mode Admin
1. Cliquer sur **Admin Settings** dans la sidebar
2. Entrer le mot de passe : `admin`
3. Gérer les mappings :
   - **Country Mapping** : Pays → OU
   - **Product Mapping** : Produits → Clouds
4. Sauvegarder les modifications

---

## 🔄 Workflow de Développement

### Faire des Modifications

```bash
# 1. Créer une branche (optionnel)
git checkout -b feature-nouvelle-fonction

# 2. Modifier le code
# ...

# 3. Tester en local
cd backend
uvicorn app.main:app --reload

# 4. Commit et push
git add .
git commit -m "Description des changements"
git push origin main

# 5. Heroku déploie automatiquement (si auto-deploy activé)
```

### Voir les Logs Heroku

```bash
heroku logs --tail --app votre-app
```

### Redémarrer l'App

```bash
heroku restart --app votre-app
```

---

## ⚠️ Important : Données CSV

Les fichiers CSV ne sont **pas** inclus dans le repo Git (exclus par `.gitignore`).

**Pour Production** :
- Utiliser **Google Cloud Storage** ou **AWS S3**
- Modifier le parser pour lire depuis l'URL

**Pour Test Local** :
- Placer les CSV dans `backend/data/Email Datas/`

---

## 🐛 Troubleshooting

### App ne démarre pas
```bash
# Vérifier les logs
heroku logs --tail

# Vérifier Procfile
cat Procfile
# Doit contenir : web: cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT

# Vérifier runtime
cat runtime.txt
# Doit contenir : python-3.11.9
```

### CORS Errors
```bash
# Vérifier Config Vars
heroku config --app votre-app

# Ajouter CORS_ORIGINS si manquant
heroku config:set CORS_ORIGINS="*" --app votre-app
```

### Données ne s'affichent pas
→ Vérifier que les CSV sont accessibles (voir section "Données CSV")

---

## 📊 API Endpoints

### Health Check
```
GET /health
```

### Email Scorecard
```
GET /api/email-scorecard?quarters=Q1&fiscal_years=FY2027&ous=FRANCE
```

### Health of Cloud
```
GET /api/health-of-cloud?quarters=Q1&regions=EMEA
```

### Mappings
```
GET /api/mappings/countries
GET /api/mappings/products
POST /api/mappings/countries
POST /api/mappings/products
POST /api/mappings/reload
```

**Documentation interactive** : `/docs`

---

## 🤝 Contribution

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit vos changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

---

## 📝 License

Ce projet est propriétaire Salesforce EMEA.

---

## 👥 Contact

**Directeur Marketing Ops Salesforce**

- GitHub : [@VOTRE-USERNAME](https://github.com/VOTRE-USERNAME)
- Project : [Cloud Field Campaign Scorecard](https://github.com/VOTRE-USERNAME/salesforce-scorecard)

---

## 🎉 Remerciements

- Équipe Salesforce EMEA Marketing Ops
- Équipe Field Campaign
- Tous les contributeurs

---

**Fait avec ❤️ pour Salesforce Field Campaigns**
