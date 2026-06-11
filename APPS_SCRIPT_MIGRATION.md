# 🚀 Migration vers Google Apps Script

**Déployer le Scorecard comme Web App accessible à tous**

---

## 🎯 Pourquoi Apps Script?

### Avantages:
- ✅ **Gratuit** - Hébergement Google gratuit
- ✅ **URL partageable** - Accessible à toute l'équipe Salesforce
- ✅ **Pas de serveur** - Pas besoin de maintenir infrastructure
- ✅ **Google Sheets natif** - Refresh data automatique
- ✅ **Permissions Google** - Contrôle d'accès intégré
- ✅ **Claude API** - Génération insights automatique

### Architecture:
```
Google Sheets (Data Source)
    ↓
Apps Script Backend (remplace FastAPI Python)
    ↓
HTML Service (même frontend)
    ↓
Published Web App (URL publique)
```

---

## 📊 ÉTAPE 1: Setup Google Sheets

### 1.1 Créer le Spreadsheet

**Créez**: "Cloud Field Campaign Scorecard Data"

**Structure (3 sheets):**

#### Sheet 1: `MDP_Data`
```
| Leader | Cloud | Region | Month | MDP | YoY_Change | Contribution |
|--------|-------|--------|-------|-----|------------|--------------|
| Alexander Wallner | Service | EMEA | May 2026 | 38000000 | 0.37 | 0.31 |
| ... | ... | ... | ... | ... | ... | ... |
```

#### Sheet 2: `Horseman_Data`
```
| Source | MDP | YoY_Change | MDP_Share |
|--------|-----|------------|-----------|
| AE | 206725872 | 0.19 | 0.45 |
| BDR | 194697874 | -0.08 | 0.43 |
| ... | ... | ... | ... |
```

#### Sheet 3: `Traffic_Data`
```
| Source | MDP | YoY_Change |
|--------|-----|------------|
| Email (L1) | 747737 | -0.94 |
| Paid (L1) | ... | ... |
```

### 1.2 Import CSV Data

**Option A**: Copier-coller depuis Excel
**Option B**: Apps Script import automatique:

```javascript
// Code.gs
function importTableauCSV() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('MDP_Data');
  const csvUrl = 'YOUR_CSV_URL_OR_DRIVE_FILE';
  
  // Import and parse CSV
  // ... (code d'import)
}
```

---

## 📝 ÉTAPE 2: Apps Script Backend

### 2.1 Créer Apps Script Project

1. Dans Google Sheets → **Extensions** → **Apps Script**
2. Renommer projet: "Scorecard Backend"

### 2.2 Code Backend (Code.gs)

```javascript
/**
 * Cloud Field Campaign Scorecard - Apps Script Backend
 */

// Main entry point for web app
function doGet(e) {
  return HtmlService.createHtmlOutputFromFile('index')
    .setTitle('Cloud Field Campaign Scorecard')
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
}

// API Functions

/**
 * Get summary statistics
 */
function getSummary() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const mdpSheet = ss.getSheetByName('MDP_Data');
  
  const data = mdpSheet.getDataRange().getValues();
  const headers = data[0];
  const rows = data.slice(1);
  
  // Calculate totals
  const mdpColIndex = headers.indexOf('MDP');
  const cloudColIndex = headers.indexOf('Cloud');
  
  let totalMDP = 0;
  const cloudBreakdown = {};
  
  rows.forEach(row => {
    const mdp = parseFloat(row[mdpColIndex]) || 0;
    const cloud = row[cloudColIndex];
    
    totalMDP += mdp;
    
    if (!cloudBreakdown[cloud]) {
      cloudBreakdown[cloud] = { mdp: 0, count: 0 };
    }
    cloudBreakdown[cloud].mdp += mdp;
    cloudBreakdown[cloud].count += 1;
  });
  
  return {
    total_mdp: totalMDP,
    cloud_breakdown: cloudBreakdown,
    regional_count: rows.length
  };
}

/**
 * Get regional data
 */
function getRegionalData(cloud = null) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName('MDP_Data');
  
  const data = sheet.getDataRange().getValues();
  const headers = data[0];
  const rows = data.slice(1);
  
  // Convert to objects
  const result = rows.map(row => {
    const obj = {};
    headers.forEach((header, i) => {
      obj[header.toLowerCase().replace(/ /g, '_')] = row[i];
    });
    return obj;
  });
  
  // Filter by cloud if specified
  if (cloud) {
    return result.filter(item => item.cloud === cloud);
  }
  
  return result;
}

/**
 * Get horseman data
 */
function getHorsemanData() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName('Horseman_Data');
  
  const data = sheet.getDataRange().getValues();
  const headers = data[0];
  const rows = data.slice(1);
  
  const horseman = {};
  
  rows.forEach(row => {
    const source = row[0];
    horseman[source] = {
      mdp: row[1],
      yoy_change: row[2],
      mdp_share: row[3]
    };
  });
  
  return {
    total: horseman['All'] || {},
    breakdown: Object.entries(horseman)
      .filter(([key]) => key !== 'All')
      .map(([source, data]) => ({ source, ...data }))
      .sort((a, b) => b.mdp - a.mdp)
  };
}

/**
 * Get traffic source data
 */
function getTrafficData() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName('Traffic_Data');
  
  const data = sheet.getDataRange().getValues();
  const rows = data.slice(1);
  
  const traffic = {};
  
  rows.forEach(row => {
    const source = row[0];
    traffic[source] = {
      mdp: row[1],
      yoy_change: row[2]
    };
  });
  
  return {
    total: traffic['All'] || {},
    breakdown: Object.entries(traffic)
      .filter(([key]) => key !== 'All')
      .map(([source, data]) => ({ source, ...data }))
      .sort((a, b) => b.mdp - a.mdp)
  };
}

/**
 * Get cloud breakdown
 */
function getClouds() {
  const regional = getRegionalData();
  
  const clouds = {};
  
  regional.forEach(item => {
    const cloud = item.cloud;
    if (!clouds[cloud]) {
      clouds[cloud] = {
        cloud,
        mdp: 0,
        count: 0,
        yoy_changes: []
      };
    }
    
    clouds[cloud].mdp += parseFloat(item.mdp) || 0;
    clouds[cloud].count += 1;
    
    if (item.yoy_change !== null && item.yoy_change !== '') {
      clouds[cloud].yoy_changes.push(parseFloat(item.yoy_change));
    }
  });
  
  // Calculate averages
  const formatted = Object.values(clouds).map(cloud => {
    const avgYoy = cloud.yoy_changes.length > 0
      ? cloud.yoy_changes.reduce((a, b) => a + b, 0) / cloud.yoy_changes.length
      : null;
    
    return {
      cloud: cloud.cloud,
      mdp: cloud.mdp,
      avg_yoy_change: avgYoy,
      leaders_count: cloud.count
    };
  });
  
  // Sort by MDP
  formatted.sort((a, b) => b.mdp - a.mdp);
  
  return {
    clouds: formatted,
    total_clouds: formatted.length
  };
}

/**
 * Generate AI insights using Claude API
 */
function generateInsights(cloud, region = 'All') {
  // Get API key from Script Properties
  const apiKey = PropertiesService.getScriptProperties().getProperty('ANTHROPIC_API_KEY');
  
  if (!apiKey) {
    return {
      error: 'Claude API key not configured',
      insights: getFallbackInsights()
    };
  }
  
  // Get data for this cloud
  const regional = getRegionalData(cloud);
  const horseman = getHorsemanData();
  const traffic = getTrafficData();
  
  // Calculate metrics
  const totalMDP = regional.reduce((sum, item) => sum + (parseFloat(item.mdp) || 0), 0);
  const yoyChanges = regional
    .map(item => parseFloat(item.yoy_change))
    .filter(val => !isNaN(val));
  const avgYoy = yoyChanges.reduce((a, b) => a + b, 0) / yoyChanges.length;
  
  // Build prompt
  const prompt = buildClaudePrompt(cloud, region, {
    mdp_total: totalMDP,
    yoy_change: avgYoy,
    leaders_count: regional.length
  }, horseman, traffic);
  
  // Call Claude API
  try {
    const response = UrlFetchApp.fetch('https://api.anthropic.com/v1/messages', {
      method: 'post',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': apiKey,
        'anthropic-version': '2023-06-01'
      },
      payload: JSON.stringify({
        model: 'claude-sonnet-4-20250514',
        max_tokens: 1024,
        messages: [{
          role: 'user',
          content: prompt
        }]
      })
    });
    
    const result = JSON.parse(response.getContentText());
    const text = result.content[0].text;
    
    // Extract JSON from response
    let jsonText = text;
    if (text.includes('```json')) {
      const start = text.indexOf('```json') + 7;
      const end = text.indexOf('```', start);
      jsonText = text.substring(start, end).trim();
    }
    
    const insights = JSON.parse(jsonText);
    
    return {
      cloud,
      region,
      insights,
      data_summary: {
        mdp_total: totalMDP,
        yoy_change: avgYoy
      }
    };
    
  } catch (e) {
    Logger.log('Claude API error: ' + e);
    return {
      error: e.toString(),
      insights: getFallbackInsights()
    };
  }
}

function buildClaudePrompt(cloud, region, mdpData, horsemanData, trafficData) {
  return `You are a marketing analytics expert analyzing Cloud Field Campaign performance.

Generate a concise scorecard analysis for:
- Cloud: ${cloud}
- Region: ${region}

Performance Data:
- Total MDP: $${mdpData.mdp_total.toLocaleString()}
- YoY Change: ${(mdpData.yoy_change * 100).toFixed(1)}%
- Leaders: ${mdpData.leaders_count}

Generate exactly:
1. 🟢 Highlights (2-3 bullet points) - positive trends
2. 🔴 Areas to Watch (2-3 bullet points) - concerns
3. 📋 Next Steps (2-3 bullet points) - actions

Output as JSON:
{
  "highlights": ["...", "...", "..."],
  "areas_to_watch": ["...", "...", "..."],
  "next_steps": ["...", "...", "..."]
}`;
}

function getFallbackInsights() {
  return {
    highlights: [
      "Performance tracking enabled across all regions",
      "Key metrics captured for decision making"
    ],
    areas_to_watch: [
      "Monitor trends for optimization opportunities"
    ],
    next_steps: [
      "Configure Claude API key for AI-powered insights"
    ]
  };
}
```

### 2.3 Frontend HTML (index.html)

Créez un fichier `index.html` dans Apps Script:
- Copiez le contenu de `frontend/index.html`
- Remplacez les calls `fetch('http://localhost:8000/api/...')` par:

```javascript
// Au lieu de fetch
const summary = await fetch('/api/data/summary');

// Utilisez google.script.run
google.script.run
  .withSuccessHandler(renderSummary)
  .getSummary();
```

---

## 🚀 ÉTAPE 3: Déploiement

### 3.1 Tester localement

1. Dans Apps Script Editor: **Run** → `doGet`
2. Authoriser les permissions
3. **Deploy** → **Test deployments**

### 3.2 Publier comme Web App

1. **Deploy** → **New deployment**
2. **Type**: Web app
3. **Description**: "Cloud Field Campaign Scorecard v1.0"
4. **Execute as**: Me
5. **Who has access**: 
   - "Anyone at Salesforce" (recommandé)
   - OU "Anyone" (public)
6. **Deploy**

### 3.3 Obtenir URL

```
https://script.google.com/macros/s/YOUR_DEPLOYMENT_ID/exec
```

**Partagez cette URL** avec toute l'équipe!

---

## 🤖 ÉTAPE 4: Configurer Claude API

### 4.1 Obtenir API Key

1. Aller sur https://console.anthropic.com
2. Créer API key
3. Copier la clé

### 4.2 Stocker dans Apps Script

```javascript
// Run once to set API key
function setupAPIKey() {
  const apiKey = 'sk-ant-...'; // Your key
  PropertiesService.getScriptProperties()
    .setProperty('ANTHROPIC_API_KEY', apiKey);
}
```

### 4.3 Tester Insights

Dans l'app, cliquez "Generate Insights" → Claude analyse et génère automatiquement!

---

## 🔄 ÉTAPE 5: Auto-refresh Data

### Option A: Manual Refresh

Button dans l'app:
```javascript
function refreshTableauData() {
  // Re-run export_all_views.py
  // Upload new CSVs to Google Sheets
}
```

### Option B: Scheduled Trigger

Apps Script peut s'exécuter automatiquement:

```javascript
function scheduledDataRefresh() {
  // Code to refresh from Tableau API
  // Or import from shared Drive folder
}
```

**Setup**:
1. Apps Script Editor → **Triggers** (clock icon)
2. **Add Trigger**:
   - Function: `scheduledDataRefresh`
   - Event: Time-driven
   - Type: Day timer
   - Time: 6am daily

---

## 📱 ÉTAPE 6: Features Bonus

### 6.1 Export to Google Slides

```javascript
function exportToSlides(data) {
  const presentation = SlidesApp.create('Scorecard - ' + new Date().toISOString());
  
  // Add slides programmatically
  // ... populate with data
  
  return presentation.getUrl();
}
```

### 6.2 Email Notifications

```javascript
function sendScorecardEmail() {
  const insights = generateInsights('Service');
  
  GmailApp.sendEmail(
    'stakeholders@salesforce.com',
    'Monthly Scorecard - Service Cloud',
    'See insights...',
    {
      htmlBody: formatEmailHTML(insights)
    }
  );
}
```

### 6.3 Slack Integration

```javascript
function postToSlack(insights) {
  const webhookUrl = 'https://hooks.slack.com/...';
  
  UrlFetchApp.fetch(webhookUrl, {
    method: 'post',
    payload: JSON.stringify({
      text: formatSlackMessage(insights)
    })
  });
}
```

---

## 📊 Résumé Migration

| Feature | Local (Now) | Apps Script (After) |
|---------|-------------|---------------------|
| **Hosting** | localhost:3000 | Google URL publique |
| **Backend** | Python FastAPI | Apps Script (JS) |
| **Data** | CSV files | Google Sheets |
| **Access** | Vous seulement | Toute l'équipe |
| **Cost** | Gratuit | Gratuit |
| **Maintenance** | Vous (manuel) | Google (auto) |
| **Claude API** | ✅ Possible | ✅ Intégré |

---

## 🎯 Timeline Migration

**Option Rapide** (2-3 heures):
1. Créer Google Sheet (30 min)
2. Copier data CSV → Sheets (15 min)
3. Code Apps Script backend (1h)
4. Adapter frontend HTML (30 min)
5. Deploy + test (30 min)

**Option Complète** (1 jour):
- Tout ci-dessus
- + Claude API integration
- + Auto-refresh scheduled
- + Export Google Slides
- + Email notifications

---

## ✅ Next Steps

**Voulez-vous que je:**
1. ✅ **Code complet Apps Script** ready to deploy?
2. ✅ **Script d'import CSV** → Google Sheets automatique?
3. ✅ **Template email** pour notifications?

**Dites-moi et je le code maintenant!** 🚀
