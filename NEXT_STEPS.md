# 🚀 Next Steps - Cloud Field Campaign Scorecard

**Status**: Structure backend créée ✅
**Date**: 2026-05-28

---

## ✅ Ce qui est fait

### Structure Backend:
- [x] Architecture FastAPI complète
- [x] Service Tableau avec Personal Access Token auth
- [x] Service Slack avec message parsing
- [x] API endpoints (Tableau, Slack, Scorecard, Export)
- [x] Configuration management (Pydantic settings)
- [x] Requirements.txt avec toutes les dépendances

### Documentation:
- [x] README complet avec architecture
- [x] PROJECT_PLAN détaillé
- [x] Structure de dossiers claire

---

## 🔧 Actions Immédiates Requises

### 1. **Configuration Tableau** (URGENT)
Vous avez un Tableau token, il faut le configurer:

```bash
cd "C:\Users\ebirot\Desktop\Cloud Field Campaign Scorecard\backend"
copy .env.example .env
```

Puis éditez `.env` et ajoutez:
```env
TABLEAU_TOKEN_NAME=votre_token_name
TABLEAU_TOKEN_VALUE=votre_token_value_ici
```

### 2. **Configuration Slack**
Il faut créer une Slack App et obtenir les tokens:

**Étapes:**
1. Aller sur https://api.slack.com/apps
2. "Create New App" → "From scratch"
3. Nom: "Cloud Field Scorecard Bot"
4. Choisir votre workspace
5. Dans "OAuth & Permissions":
   - Ajouter scopes: `channels:history`, `channels:read`, `chat:write`
   - Install to workspace
   - Copier le "Bot User OAuth Token" (commence par `xoxb-`)
6. Inviter le bot dans votre channel broadcast: `/invite @Cloud Field Scorecard Bot`
7. Récupérer le Channel ID:
   - Clic droit sur le channel → "View channel details"
   - Tout en bas, copier le Channel ID

Ajouter dans `.env`:
```env
SLACK_BOT_TOKEN=xoxb-votre-token-ici
SLACK_CHANNEL_ID=C123456789
```

### 3. **Tester les connexions**

Installer les dépendances:
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Lancer le serveur:
```bash
uvicorn app.main:app --reload
```

Tester:
- API docs: http://localhost:8000/docs
- Test Tableau: http://localhost:8000/api/tableau/test
- Test Slack: http://localhost:8000/api/slack/test

---

## 📋 Prochaines Étapes de Développement

### Phase 1: Backend Data Pipeline (Semaine 1-2)

#### A. Tableau Integration - À FAIRE:
- [ ] **Identifier les workbooks exacts**:
  - Vous avez mentionné workbook ID `1534752` pour MDP
  - Besoin IDs pour Lead Performance et Campaign Performance
  - Pour chaque workbook, lister les views/dashboards pertinents

- [ ] **Mapper les données**:
  - Quels champs extraire de chaque view?
  - Structure des données (colonnes, formats)
  - Filtres à appliquer (date range, région)

- [ ] **Implémenter extraction**:
  - Compléter `tableau.py` méthodes d'extraction
  - Parser les CSV/données retournées
  - Transformer en structure JSON cohérente

#### B. Slack Integration - À FAIRE:
- [ ] **Définir template message**:
  - Format exact que les campaign leaders doivent suivre
  - Poster un exemple dans le channel
  - Créer un template message épinglé

- [ ] **Améliorer parsing**:
  - Tester avec messages réels du channel
  - Ajuster regex patterns si besoin
  - Gérer variations de format

#### C. Database Setup - À FAIRE:
- [ ] **Installer PostgreSQL** (ou utiliser Supabase)
- [ ] **Créer schema database**:
  ```sql
  -- Tables principales:
  -- scorecards, mdp_data, lead_data, campaign_data, slack_updates
  ```
- [ ] **SQLAlchemy models** dans `app/models/`
- [ ] **Alembic migrations** pour version control du schema

### Phase 2: Frontend React (Semaine 2-3)

```bash
cd frontend
npm create vite@latest . -- --template react-ts
npm install
npm install @tanstack/react-query zustand recharts tailwindcss
npm install -D @tailwindcss/forms @tailwindcss/typography
```

#### A. Setup de base:
- [ ] Vite + React + TypeScript
- [ ] TailwindCSS configuration
- [ ] React Query pour API calls
- [ ] Zustand pour state management
- [ ] React Router pour navigation

#### B. Composants principaux:
- [ ] Dashboard layout avec sidebar
- [ ] Filtres (Month, Region, OU, Cloud)
- [ ] Health of Cloud cards
- [ ] Lead Performance tables
- [ ] Campaign Performance charts
- [ ] Slack updates display (Highlights/Lowlights/Actions)

### Phase 3: Combined EMEA+AMER (Semaine 3-4)

#### A. Backend logic:
- [ ] Fonction `merge_regions(emea_data, amer_data)`
- [ ] Agrégation metrics
- [ ] Calculs YoY avec données combinées

#### B. Frontend views:
- [ ] Toggle EMEA/AMER/Combined
- [ ] Comparative charts
- [ ] Side-by-side comparisons

### Phase 4: Google Slides Export (Semaine 4-5)

#### A. Google Cloud setup:
- [ ] Créer projet Google Cloud
- [ ] Activer Google Slides API
- [ ] Créer Service Account
- [ ] Télécharger credentials JSON
- [ ] Partager template slide avec service account email

#### B. Implementation:
- [ ] Service `slides.py` complet
- [ ] Template slide avec placeholders
- [ ] Logic de population automatique
- [ ] Génération charts as images
- [ ] Upload vers Google Drive

### Phase 5: Deployment (Semaine 5-6)

#### A. Backend deployment:
- [ ] Railway.app ou Render.com
- [ ] Variables d'environnement
- [ ] PostgreSQL managed instance

#### B. Frontend deployment:
- [ ] Vercel ou Netlify
- [ ] Environment variables
- [ ] Custom domain (optionnel)

#### C. Automation:
- [ ] GitHub Actions pour CI/CD
- [ ] Monthly scheduler (1er du mois)
- [ ] Email notifications

---

## 🤔 Questions Critiques en Attente

### Tableau:
1. **Workbook IDs exacts**:
   - Lead Performance workbook ID?
   - Campaign Performance workbook ID?
   - AMER workbooks: mêmes IDs ou différents?

2. **Structure data**:
   - Les views Tableau ont quels noms exactement?
   - Format des données retournées (CSV, JSON)?
   - Besoin de filtres spécifiques?

3. **AMER vs EMEA**:
   - Workbooks séparés ou même workbook avec filtre région?
   - Nomenclature identique (OUs, Clouds)?

### Slack:
1. **Channel broadcast**:
   - Quel est le nom du channel?
   - Les campaign leaders postent déjà dans un format structuré?
   - Besoin de créer un nouveau channel dédié?

2. **Format messages**:
   - Template actuel utilisé?
   - Fréquence des posts (chaque début de mois)?

### Google Slides:
1. **Template**:
   - Utiliser le deck Avril comme template de base?
   - Créer un nouveau template vierge?
   - Qui possède/gère le template?

### Accès & Permissions:
1. **Qui utilise l'app?**:
   - Campaign leaders only?
   - Leadership team?
   - Read-only stakeholders?

2. **Authentication**:
   - Login requis ou app publique?
   - SSO Salesforce integration?

---

## 💡 Recommandations Immédiates

### Option A: Démarrage Rapide (MVP en 2 semaines)
1. **Cette semaine**: 
   - Configurer Tableau + Slack tokens
   - Tester connexions
   - Extraire 1-2 mois de data en CSV pour prototyping
   
2. **Semaine prochaine**:
   - Backend: Parser les CSV et exposer via API
   - Frontend: Dashboard basique avec data statique
   - Demo fonctionnel pour validation

### Option B: Développement Complet (6 semaines)
- Suivre le roadmap complet phase par phase
- Database + automation + export slides
- Production-ready avec monitoring

**Je recommande Option A** pour valider l'approche rapidement, puis itérer.

---

## 🎯 Action Items MAINTENANT

**Vous devez faire:**

1. ✅ **Configurer `.env`** avec vos tokens Tableau et Slack
2. ✅ **Tester les connexions** API
3. ✅ **Me fournir**:
   - Workbook IDs manquants
   - Nom du Slack channel broadcast
   - 1-2 exemples de messages Slack du channel (anonymisé si besoin)
   - Export CSV d'un dashboard Tableau (1 mois de data exemple)

**Moi je peux faire:**

Une fois que j'ai vos tokens configurés et exemples de data:
- Compléter les méthodes d'extraction Tableau
- Améliorer le parsing Slack avec vrais messages
- Créer un prototype frontend qui consomme les APIs
- Vous montrer une démo en ~3-5 jours

---

## 📞 Questions?

Quelle approche préférez-vous:
- **Option A** (MVP rapide 2 semaines)?
- **Option B** (Complet 6 semaines)?

Et pouvez-vous fournir:
1. Tokens Tableau et Slack (via `.env`)
2. Workbook IDs manquants
3. Exemple data CSV ou screenshots Tableau?

On démarre dès que vous avez configuré les tokens! 🚀
