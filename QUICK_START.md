# 🚀 Quick Start Guide

**Cloud Field Campaign Scorecard Platform**

---

## ✅ Status Actuel

- [x] Tableau credentials configurés
- [x] Structure backend créée
- [ ] Installation dépendances Python (en cours...)
- [ ] Test connexion Tableau
- [ ] Configuration Slack

---

## 📝 Étape 1: Installation (EN COURS)

```bash
cd "C:\Users\ebirot\Desktop\Cloud Field Campaign Scorecard\backend"

# Virtual environment déjà créé
# Installation en cours...
```

---

## 🔍 Étape 2: Test Connexion Tableau

Une fois l'installation terminée:

```bash
cd "C:\Users\ebirot\Desktop\Cloud Field Campaign Scorecard\backend"
venv\Scripts\python test_tableau.py
```

Ce script va:
- ✅ Tester la connexion avec votre token
- 📊 Lister les workbooks disponibles
- 📈 Montrer les views du workbook MDP (ID: 1534752)

---

## 🎯 Résultats Attendus

Si tout fonctionne, vous verrez:

```
🔍 Testing Tableau Connection...
============================================================
✅ Connected successfully. Found XX workbooks

📊 Available Workbooks (first 10):
------------------------------------------------------------
  ID: 1534752
  Name: FY27 MDP Scorecard Builder
  Project: Field Campaigns
------------------------------------------------------------

🔍 Testing Workbook Access...
============================================================
✅ Workbook Found: FY27 MDP Scorecard Builder
   
📈 Views in this workbook:
   1. Q1 Overview - Service
   2. Q1 Overview - Sales
   3. MDP by Region
   ...
```

---

## 📊 Étape 3: Explorer les Workbooks

Une fois la connexion validée, nous devons identifier:

### A. Workbooks Nécessaires:
- ✅ **MDP Scorecard**: ID `1534752` (confirmé)
- ❓ **Lead Performance**: ID = ?
- ❓ **Campaign Performance**: ID = ?

### B. Views à Extraire:

Pour chaque workbook, noter les views importantes:
- Health of Cloud par Cloud
- Lead Performance par OU
- Campaign Performance (Webinar, Email)

---

## 🔧 Étape 4: Configuration Slack (À FAIRE)

### Créer Slack App:

1. **Aller sur**: https://api.slack.com/apps
2. **Create New App** → "From scratch"
3. **Nom**: "Cloud Field Scorecard Bot"
4. **Workspace**: Choisir votre workspace Salesforce

### Configurer Permissions:

5. Dans **OAuth & Permissions** → Scopes:
   - `channels:history` - Lire messages du channel
   - `channels:read` - Info sur les channels
   - `chat:write` - (optionnel) Poster des messages

6. **Install to Workspace**

7. **Copier le token** (commence par `xoxb-...`)

### Inviter le Bot:

8. Dans votre channel broadcast Slack:
   ```
   /invite @Cloud Field Scorecard Bot
   ```

9. **Récupérer Channel ID**:
   - Clic droit sur le channel → View channel details
   - En bas: copier le Channel ID (format: C123456789)

### Ajouter au .env:

10. Éditer `backend\.env`:
    ```env
    SLACK_BOT_TOKEN=xoxb-votre-token-ici
    SLACK_CHANNEL_ID=C123456789
    ```

---

## 🌐 Étape 5: Lancer le Backend API

```bash
cd "C:\Users\ebirot\Desktop\Cloud Field Campaign Scorecard\backend"
venv\Scripts\uvicorn app.main:app --reload
```

Accéder:
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### Tester les Endpoints:

Dans la doc Swagger (http://localhost:8000/docs):

1. **Test Tableau**: 
   - `GET /api/tableau/test`
   - Devrait retourner liste de workbooks

2. **Test Slack** (après config):
   - `GET /api/slack/test`
   - Devrait confirmer connexion

3. **Get MDP Data**:
   - `GET /api/tableau/mdp?region=EMEA&month=2026-04`

---

## 📋 Informations Manquantes

### Tableau:
- [ ] Workbook ID pour **Lead Performance**
- [ ] Workbook ID pour **Campaign Performance**
- [ ] Noms exacts des **views** à extraire
- [ ] AMER data: même workbooks ou séparés?

### Slack:
- [ ] Nom du **channel broadcast** actuel
- [ ] Les campaign leaders postent déjà? Format?
- [ ] Besoin de créer nouveau channel dédié?

### Google Slides:
- [ ] Template slide à utiliser (nouveau ou existant?)
- [ ] Qui gère le template?

---

## 🎯 Next Actions

**Maintenant:**
1. ✅ Attendre fin installation pip
2. ✅ Lancer `test_tableau.py`
3. ✅ Noter les workbooks disponibles

**Après:**
4. Identifier workbook IDs manquants
5. Configurer Slack app
6. Extraire sample data d'un workbook

**Plus tard:**
7. Développer frontend React
8. Implémenter export Google Slides
9. Déployer en production

---

## 🆘 Troubleshooting

### Erreur: "Failed to connect to Tableau"
- Vérifier token dans `.env` (pas d'espaces)
- Vérifier token pas expiré (expire May 28, 2027)
- Vérifier server URL correct

### Erreur: Module not found
- Vérifier virtual env activé: `venv\Scripts\activate`
- Réinstaller: `pip install -r requirements-minimal.txt`

### Erreur Slack
- Token commence bien par `xoxb-`?
- Bot invité dans le channel?
- Permissions correctes?

---

## 📞 Questions?

Postez dans le chat si:
- Erreurs lors de l'installation
- Connexion Tableau ne fonctionne pas
- Besoin d'aide pour identifier workbooks
