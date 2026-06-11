# 👁️ Indicateur Visuel de Refresh

## À Quoi Ça Ressemble

Dans le **header de l'application**, en haut à droite, tu verras un petit badge :

---

### ✅ Refresh Réussi (Fond Vert)

```
┌──────────────────────────────┐
│ ✅  Updated 11/06 at 06:00  │  ← Fond vert clair
└──────────────────────────────┘
```

**Signification** : Les données ont été téléchargées avec succès depuis Tableau.

---

### ⚠️ Refresh Échoué (Fond Rouge)

```
┌────────────────────────────────────┐
│ ⚠️  Last attempt 11/06 at 06:00   │  ← Fond rouge clair
└────────────────────────────────────┘
```

**Signification** : Le téléchargement a échoué (problème token, connexion, etc.)

---

### ⏳ Chargement (Fond Gris)

```
┌──────────────────────┐
│ ⏳  Loading...      │  ← Fond gris transparent
└──────────────────────┘
```

**Signification** : L'app charge le statut depuis l'API.

---

### 📍 Aucune Mise à Jour Encore

```
┌───────────────────────┐
│ ⏳  No update yet    │  ← Fond gris transparent
└───────────────────────┘
```

**Signification** : Le système n'a jamais fait de refresh (première installation).

---

## Comportement

- **Auto-refresh** : L'indicateur vérifie le statut toutes les **5 minutes**
- **Format date** : `DD/MM at HH:MM` (format français)
- **Timezone** : Heure française (Europe/Paris)
- **Position** : Entre le titre et les filtres Quarter

---

## Exemples Réels

### Matin Après le Refresh Automatique (6h05)

```
Health of the Cloud Scorecard   ✅ Updated 11/06 at 06:00   [Q1][Q2][YTD]
```

---

### Si le Refresh Échoue

```
Health of the Cloud Scorecard   ⚠️ Last attempt 11/06 at 06:00   [Q1][Q2][YTD]
```

Tu sauras immédiatement qu'il faut vérifier les logs Heroku.

---

## Comment Vérifier en Détail

Si tu veux plus d'infos que l'indicateur visuel :

### Option 1 : API Swagger

```
https://TON-APP.herokuapp.com/docs
```

Endpoint : **GET /api/refresh/status**

Réponse détaillée :
```json
{
  "last_update": {
    "last_updated": "2026-06-11T06:00:12.456789",
    "successful": 10,
    "total": 10,
    "elapsed_seconds": 8.3,
    "success": true,
    "error": null
  }
}
```

### Option 2 : Logs Heroku

```bash
heroku logs --tail --app TON-APP
```

Chercher :
```
✅ CSV refresh completed: 10/10 files in 8.3s
💾 Saved refresh status: 10/10 files
```

---

## Avantages

1. **📊 Transparence** : Tu sais toujours si tes données sont à jour
2. **⏱️ Temps réel** : Pas besoin de vérifier manuellement
3. **🚨 Alertes visuelles** : Fond rouge = problème immédiatement visible
4. **📅 Timestamp** : Tu sais exactement quand les données ont été mises à jour

---

## Cas d'Usage

### Scenario 1 : Tout Va Bien

```
Tu ouvres l'app à 9h00
→ Tu vois : ✅ Updated 11/06 at 06:00 (fond vert)
→ Tu sais que les données du matin sont fraîches
```

### Scenario 2 : Problème Détecté

```
Tu ouvres l'app à 9h00
→ Tu vois : ⚠️ Last attempt 11/06 at 06:00 (fond rouge)
→ Tu vérifies les logs Heroku
→ Tu découvres que le token Tableau a expiré
→ Tu renouvelles le token
```

### Scenario 3 : Première Installation

```
Tu viens de déployer l'app
→ Tu vois : ⏳ No update yet (fond gris)
→ Tu déclenches un refresh manuel via /docs
→ Quelques secondes plus tard : ✅ Updated 11/06 at 09:15
```

---

## 🎨 Design

L'indicateur s'intègre parfaitement dans le header bleu :

- **Taille** : Petite et discrète (12px font size)
- **Padding** : 6px 12px pour être lisible
- **Border-radius** : 6px pour un style moderne
- **Fond** : Semi-transparent pour ne pas surcharger
- **Animation** : Smooth transition entre les états

---

## 🔧 Personnalisation

Si tu veux changer l'apparence, édite dans `frontend/health_of_cloud_v2.html` :

```html
<div id="refreshStatus" style="...">
  <span id="refreshIcon">⏳</span>
  <span id="refreshText">Loading...</span>
</div>
```

Et dans le `<script>` en bas :

```javascript
// Changer les icônes
refreshIcon.textContent = '✅';  // ou '🟢', '✔️', etc.

// Changer les couleurs
refreshStatus.style.background = 'rgba(16, 185, 129, 0.2)';  // vert

// Changer le texte
refreshText.textContent = `Mis à jour le ${dateStr} à ${timeStr}`;
```

---

## ✅ Résumé

**L'indicateur te donne en un coup d'œil :**
- ✅ Si les données sont à jour
- 📅 Quand le dernier refresh a eu lieu
- ⚠️ Si un problème est survenu

**Sans jamais avoir à ouvrir les logs ou tester l'API manuellement !** 🎉
