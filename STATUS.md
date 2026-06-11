# 📊 Cloud Field Campaign Scorecard - Status

**Date**: 2026-05-28
**Phase**: Backend MVP Setup

---

## ✅ ACCOMPLI AUJOURD'HUI

### 1. Structure Projet Complète
- ✅ Dossiers: backend/, frontend/, docs/, data/, scripts/
- ✅ README.md avec architecture détaillée
- ✅ PROJECT_PLAN.md (roadmap 6 semaines)
- ✅ NEXT_STEPS.md (actions immédiates)
- ✅ QUICK_START.md (guide setup)

### 2. Backend API (FastAPI)
- ✅ Structure complète app/
- ✅ Configuration management (Pydantic Settings)
- ✅ Service Tableau avec Personal Access Token auth
- ✅ Service Slack avec message parsing
- ✅ API endpoints:
  - `/api/tableau/*` - Extraction data
  - `/api/slack/*` - Updates campaign leaders
  - `/api/scorecard/*` - Scorecards combinés
  - `/api/export/*` - Export (placeholder)

### 3. Credentials Tableau Configurés
- ✅ Token Name: `Token_Claude_CFM_Scorecard`
- ✅ Connexion testée et fonctionnelle
- ✅ Accès à Tableau Server: `https://prod-uswest-c.online.tableau.com`
- ✅ Site: `salesforce`
- ✅ 100+ workbooks accessibles

### 4. Python Environment
- ✅ Virtual environment créé
- ✅ Dépendances installées:
  - FastAPI, Uvicorn
  - tableauserverclient
  - slack-sdk
  - Pydantic, python-dotenv

---

## 🔍 DÉCOUVERTES IMPORTANTES

### Tableau Access:
1. **Connexion réussie**: Token fonctionne parfaitement
2. **100+ workbooks** accessibles sur le serveur
3. **Workbook ID `1534752`** du deck n'est PAS un UUID valide
   - Les IDs Tableau sont des UUIDs (format: `636532f6-880f-4c56-aa6d-859a330ac7bb`)
   - Le numéro `1534752` fait probablement référence à autre chose (View ID? URL param?)

4. **Workbooks trouvés**:
   - Recherche "scorecard": 1 résultat (`Business Summary | Scorecard Overview`)
   - Recherche "MDP", "Field Campaign", "Lead", "Campaign": Aucun résultat

### Possible Raisons:
- **Permissions**: Les workbooks MDP peuvent ne pas être dans votre liste accessible
- **Noms différents**: Les workbooks ont peut-être des noms internes différents
- **Workbook vs Views**: Le ID `1534752` pourrait être un View ID, pas Workbook ID

---

## 🎯 ACTIONS REQUISES (URGENTES)

### 1. Identifier les Vrais Workbooks
Vous devez me fournir:

#### Option A: Via Tableau Web
1. Ouvrir le workbook MDP dans votre browser Tableau
2. URL ressemble à: `https://prod-uswest-c.online.tableau.com/#/site/salesforce/workbooks/[WORKBOOK_ID]`
3. Copier le UUID du workbook de l'URL

#### Option B: Via Script Python
Je peux créer un script qui liste TOUS vos workbooks (pas juste les 10 premiers).
Vous identifiez manuellement les bons.

#### Option C: Me donner accès temporaire
Si vous avez un admin Tableau, ils peuvent:
- Me montrer où sont les workbooks MDP/Lead/Campaign
- Ou extraire les données eux-mêmes en CSV que je peux ingérer

### 2. Configuration Slack
**À FAIRE**:
- [ ] Créer Slack App: https://api.slack.com/apps
- [ ] Obtenir Bot Token (commence par `xoxb-`)
- [ ] Identifier le channel broadcast (nom + ID)
- [ ] Inviter le bot dans le channel
- [ ] Me fournir: Channel ID + Bot Token

### 3. Format Updates Slack
**Questions**:
- Les campaign leaders postent déjà des updates mensuels?
- Si oui: quel format actuellement?
- Si non: besoin de créer un template + les former?

---

## 📊 OPTIONS POUR CONTINUER

### Option 1: Prototyping avec CSV (RECOMMANDÉ)
**Pourquoi**: Plus rapide, valide l'approche sans bloquer sur Tableau

**Actions**:
1. Vous exportez manuellement 1-2 mois de data depuis Tableau en CSV
2. Je crée le backend qui parse ces CSV
3. Je développe le frontend qui affiche les data
4. **Résultat**: Prototype fonctionnel en ~3-5 jours

Une fois validé, on connecte la vraie API Tableau.

### Option 2: Identifier Workbooks d'abord
**Pourquoi**: Solution complète end-to-end

**Actions**:
1. Identifier les vrais workbook UUIDs
2. Extraire via API Tableau directement
3. Développer frontend

**Résultat**: Solution complète en ~2 semaines

### Option 3: MVP Web App Statique
**Pourquoi**: Démo rapide pour stakeholders

**Actions**:
1. Je crée une web app React avec données mockées basées sur le deck Avril
2. Design et UX parfaits
3. Vous validez l'interface
4. Après validation, on connecte les vraies données

**Résultat**: Interface validée en ~1 semaine, data après

---

## 💡 MA RECOMMANDATION

**Faire Option 1 + Option 3 en parallèle:**

### Cette semaine:
1. **Vous**: Exporter 2 mois de data Tableau en CSV (Avril + Mai)
2. **Moi**: Créer frontend React avec interface complète
3. **Résultat**: Prototype avec vraies données fin de semaine

### Semaine prochaine:
4. **Configurer Slack** (bot + channel)
5. **Parser les CSV** et alimenter la web app
6. **Démo fonctionnelle** aux stakeholders

### Après validation:
7. Identifier vrais workbooks Tableau
8. Connecter API Tableau en remplacement des CSV
9. Ajouter export Google Slides
10. Déployer en production

---

## 🔧 COMMANDES UTILES

### Tester Tableau:
```bash
cd "C:\Users\ebirot\Desktop\Cloud Field Campaign Scorecard\backend"
venv\Scripts\python test_tableau_simple.py
```

### Chercher workbooks:
```bash
venv\Scripts\python search_workbooks.py
```

### Lancer l'API:
```bash
venv\Scripts\uvicorn app.main:app --reload
```
Puis ouvrir: http://localhost:8000/docs

---

## 📞 QUESTIONS POUR VOUS

1. **Workbooks Tableau**:
   - Pouvez-vous me fournir les URLs ou UUIDs des workbooks?
   - Ou préférez-vous exporter en CSV pour commencer?

2. **Slack**:
   - Nom du channel broadcast actuel?
   - Les leaders postent déjà des updates?

3. **Timeline**:
   - Besoin pour juin (dans ~10 jours)?
   - Ou plus de temps disponible?

4. **Approche préférée**:
   - Option 1 (CSV + prototype rapide)?
   - Option 2 (API Tableau d'abord)?
   - Option 3 (Frontend mockup d'abord)?
   - Ou combinaison?

---

## 📝 FICHIERS CRÉÉS AUJOURD'HUI

```
Cloud Field Campaign Scorecard/
├── README.md                    # Vue d'ensemble projet
├── PROJECT_PLAN.md              # Roadmap 6 semaines
├── NEXT_STEPS.md                # Actions immédiates
├── QUICK_START.md               # Guide setup
├── STATUS.md                    # Ce fichier
│
├── backend/
│   ├── .env                     # Credentials (Tableau configuré)
│   ├── requirements.txt         # Toutes dépendances
│   ├── requirements-minimal.txt # Dépendances core (installées)
│   ├── test_tableau_simple.py   # Test connexion Tableau
│   ├── search_workbooks.py      # Chercher workbooks
│   │
│   └── app/
│       ├── main.py              # FastAPI app
│       ├── core/
│       │   └── config.py        # Configuration settings
│       ├── services/
│       │   ├── tableau.py       # Service Tableau
│       │   └── slack.py         # Service Slack
│       └── api/
│           ├── tableau.py       # Endpoints Tableau
│           ├── slack.py         # Endpoints Slack
│           ├── scorecard.py     # Endpoints scorecards
│           └── export.py        # Endpoints export
│
└── FY27 QTD April - EMEA Cloud Field Campaign Scorecard Deck.txt
    # Deck exemple analysé
```

---

## 🎯 NEXT ACTIONS

**POUR VOUS:**
1. Décider quelle option préférez-vous (CSV vs API vs mockup)
2. Si CSV: exporter 1-2 mois de data
3. Me fournir workbook URLs/IDs si disponibles
4. Configuration Slack (créer app + bot token)

**POUR MOI:**
1. Attendre votre choix d'approche
2. Soit: parser CSV + build frontend
3. Soit: identifier workbooks + API Tableau
4. Soit: mockup frontend d'abord

**Dites-moi quelle approche vous voulez et on démarre! 🚀**
