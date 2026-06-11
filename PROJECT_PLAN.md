# Cloud Field Campaign Scorecard - Plan de Projet
**Date**: 2026-05-28
**Owner**: Directeur Marketing Strategy & Ops

## 🎯 Objectif
Automatiser la production mensuelle des scorecards combinés EMEA + AMER avec:
- Extraction automatique data Tableau
- Intégration updates Slack des campaign leaders
- Génération automatique Google Slides OU web app interactive
- Publication stakeholders simplifiée

---

## 📋 Structure Actuelle des Scorecards

### Slides Types (basé sur deck Avril EMEA):
1. **Health of Cloud Scorecards** (par Cloud)
   - Service, Field Service, Sales, Marketing, Commerce, AI & Data
   - Metrics: MDP par région/horseman/traffic/offer
   - 🟢 Highlights + 🔴 Areas to watch + Actions/Next Steps

2. **Lead Performance Scorecards** (par OU + par Cloud)
   - OUs: UKI, France, South, Central, North
   - Metrics: Valid Leads, Core/Non-Core, Lead Score, Top Sources
   - Conversion rates

3. **Campaign Performance Scorecards**
   - Webinar channel performance
   - Email performance (DSE coverage, CTR, U:CR)
   - Asset-level analysis par Cloud

---

## 🏗️ Architecture Technique Proposée

### **PHASE 1: Data Pipeline** (Backend)
```
Tableau API → ETL Script → Structured Database → API endpoints
     ↓
Slack API → Parse highs/lows/next steps → Database
```

**Composants:**
- **Tableau Integration**: API REST pour extract datasets
  - MDP Campaigns Dataset
  - MDP Oppties Dataset
  - Lead Performance datasets
  - FY27 Scorecard Builder workbook
  
- **Slack Integration**: Slack API + Skills
  - Canal dédié: `#scorecard-monthly-updates`
  - Format template pour campaign leaders (structured input)
  - Auto-parsing des messages en sections: Highlights/Lowlights/Actions

- **Database**: PostgreSQL ou Google Sheets backend
  - Tables: mdp_data, lead_data, campaign_updates, slack_inputs
  - Schema normalisé par: month, region (EMEA/AMER), OU, Cloud

### **PHASE 2A: Auto-generation Google Slides** (Option classique)
```
Python Script → Google Slides API → Template population → Export final deck
```

**Composants:**
- Master template Google Slides avec placeholders
- Script Python utilisant `python-pptx` ou Google Slides API
- Automation mensuelle via Cloud Functions/GitHub Actions
- Output: Deck prêt à partager avec stakeholders

### **PHASE 2B: Web App Interactive** (Option moderne - RECOMMANDÉ)
```
React Frontend ↔ Node.js API ↔ Database
```

**Composants:**
- **Frontend**: React + TailwindCSS
  - Filtres: Month, Region (EMEA/AMER/Combined), OU, Cloud
  - Visualizations: Chart.js / Recharts
  - Export PDF/PPT on-demand
  
- **Backend**: Node.js/Express API
  - Endpoints REST pour data queries
  - Caching pour performance
  
- **Hosting**: Vercel/Netlify (frontend) + Railway/Render (backend)

### **PHASE 3: Automation & Publishing**
- Scheduler mensuel (1er jour du mois)
- Email notifications aux stakeholders
- Version control (historique des scorecards)
- Access control (qui voit quoi)

---

## 🔧 Tech Stack Recommandé

### Backend:
- **Language**: Python 3.11+
- **Frameworks**: 
  - FastAPI (API backend)
  - Pandas (data processing)
  - SQLAlchemy (ORM)
- **APIs**:
  - Tableau REST API
  - Slack Web API / Slack SDK
  - Google Slides API (si option 2A)

### Frontend (si web app):
- **Framework**: React 18 + TypeScript
- **UI**: TailwindCSS + shadcn/ui
- **Charts**: Recharts
- **State**: React Query + Zustand

### Infrastructure:
- **Database**: PostgreSQL (Supabase ou RailwayApp)
- **Hosting**: 
  - Frontend: Vercel
  - Backend: Railway ou Google Cloud Run
- **CI/CD**: GitHub Actions
- **Scheduler**: GitHub Actions cron ou Cloud Scheduler

---

## 📅 Timeline Estimation

### Sprint 1 (2 semaines): Data Pipeline
- [ ] Tableau API setup + extraction MDP/Leads data
- [ ] Slack API integration + message parsing
- [ ] Database schema design + setup
- [ ] ETL scripts development

### Sprint 2 (2 semaines): Génération Slides OU Web App MVP
**Option A** (Slides automation):
- [ ] Template Google Slides master
- [ ] Script population automatique
- [ ] Tests avec data Avril

**Option B** (Web app - RECOMMANDÉ):
- [ ] API backend avec endpoints principaux
- [ ] Frontend MVP avec filtres région/OU/Cloud
- [ ] Visualizations basiques (MDP trends, Lead perf)

### Sprint 3 (1 semaine): EMEA + AMER Combined Logic
- [ ] Merge logic pour data EMEA + AMER
- [ ] Comparative views
- [ ] Combined scorecards generation

### Sprint 4 (1 semaine): Automation & Polish
- [ ] Scheduler setup
- [ ] Email notifications
- [ ] Documentation utilisateur
- [ ] User testing avec campaign leaders

**Total**: 6 semaines pour MVP complet

---

## 📊 Sources de Données à Connecter

### Tableau Workbooks:
1. **MDP Scorecards**:
   - `EMEA Field Campaign - EMAIL Scorecard Builder [Light Version]`
   - `FY27 MDP Scorecard Builder`
   - URL: `https://prod-uswest-c.online.tableau.com/#/site/salesforce/workbooks/1534752`

2. **Lead Performance**:
   - Lead Scorecard datasets (par OU)

3. **Campaign Performance**:
   - Webinar MDP by Cloud
   - Email Performance (DSE Coverage, CTR)

### Slack Channels:
- À définir: créer `#emea-amer-scorecard-updates` ?
- Template mensuel pour campaign leaders
- Format structuré: 🟢 Highlights | 🔴 Lowlights | 📋 Next Steps

---

## 🤔 Questions Critiques à Répondre

### 1. **Choix d'output**:
   - [ ] **Option A**: Auto-generate Google Slides (traditionnel)
   - [ ] **Option B**: Web app interactive (moderne, meilleure UX)
   - [ ] **Option C**: Les deux (web app + export slides)

### 2. **Tableau Access**:
   - Avez-vous accès API Tableau? (credentials admin requis)
   - Les workbooks listés sont-ils les bons?
   - Autres dashboards nécessaires?

### 3. **Slack Process**:
   - Les campaign leaders postent déjà quelque part?
   - Quel format actuellement? (texte libre? bullets?)
   - Besoin de créer nouveau canal ou utiliser existant?

### 4. **AMER Data**:
   - Même structure Tableau que EMEA?
   - Workbooks séparés ou integrated?
   - Campaign leaders AMER: qui sont-ils?

### 5. **Stakeholders**:
   - Qui reçoit les scorecards? (emails? Slack?)
   - Fréquence: mensuel uniquement ou ad-hoc aussi?
   - Read-only ou besoin de commenter/edit?

---

## 💡 Recommandation Immédiate

**Je recommande Option B: Web App Interactive** parce que:

✅ **Meilleure UX**: 
- Filtres dynamiques (month/region/OU/Cloud)
- Drill-down interactif
- Toujours à jour en temps réel

✅ **Scalabilité**: 
- Facile d'ajouter nouvelles metrics
- Pas de limite de slides
- Historical comparisons faciles

✅ **Collaboration**: 
- Stakeholders accèdent via URL
- Pas besoin d'envoyer decks multiples
- Export PDF/PPT on-demand si besoin

✅ **Maintenance**: 
- Pas de templates slides à maintenir
- Data refresh automatique
- Updates code déployées en minutes

❌ **Trade-off**: 
- Développement initial ~2 semaines de plus
- Besoin hosting (coût ~$20-50/mois)

---

## 🚀 Next Steps Immédiats

1. **Répondre aux questions critiques** ci-dessus
2. **Confirmer choix**: Slides automation vs Web app
3. **Accès Tableau**: me fournir credentials API ou workspace access
4. **Slack setup**: confirmer canal et format des updates
5. **Sample data**: exporter 1-2 mois de Tableau data en CSV pour prototyping

Une fois confirmé, je commence par Sprint 1 (Data Pipeline).
