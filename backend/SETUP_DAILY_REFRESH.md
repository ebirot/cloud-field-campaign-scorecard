# Configuration du Refresh Automatique Quotidien

## 📅 Schedule: Tous les jours à **23h00 heure française (CET/CEST)**

---

## Option 1: Windows Task Scheduler (Recommandé pour Windows)

### Étapes:

1. **Ouvrir Task Scheduler**
   - Appuyer sur `Windows + R`
   - Taper `taskschd.msc`
   - Appuyer sur Entrée

2. **Créer une nouvelle tâche**
   - Cliquer sur "Create Basic Task" (à droite)
   - Nom: `Tableau Scorecard Daily Refresh`
   - Description: `Export automatique des données Tableau à 23h00`
   - Cliquer sur "Next"

3. **Trigger (Déclencheur)**
   - Sélectionner: **Daily** (Quotidien)
   - Cliquer sur "Next"
   - Heure: **23:00**
   - Récurrence: **Every 1 day**
   - Cliquer sur "Next"

4. **Action**
   - Sélectionner: **Start a program** (Démarrer un programme)
   - Cliquer sur "Next"
   - Programme: `C:\Users\ebirot\Desktop\Cloud Field Campaign Scorecard\backend\venv\Scripts\python.exe`
   - Arguments: `daily_refresh.py`
   - Dossier de départ: `C:\Users\ebirot\Desktop\Cloud Field Campaign Scorecard\backend`
   - Cliquer sur "Next"

5. **Finaliser**
   - Cocher "Open the Properties dialog for this task when I click Finish"
   - Cliquer sur "Finish"

6. **Configuration avancée** (dans Properties)
   - Onglet **General**:
     - Cocher "Run whether user is logged on or not"
     - Cocher "Run with highest privileges"
   - Onglet **Conditions**:
     - Décocher "Start the task only if the computer is on AC power"
     - Cocher "Wake the computer to run this task"
   - Onglet **Settings**:
     - Cocher "Run task as soon as possible after a scheduled start is missed"
   - Cliquer sur "OK"

7. **Tester manuellement**
   - Clic droit sur la tâche → "Run"
   - Vérifier les logs dans: `C:\Users\ebirot\Desktop\Cloud Field Campaign Scorecard\backend\data\`

---

## Option 2: Script Batch pour lancer manuellement

Créer un fichier `run_refresh.bat` avec:

```batch
@echo off
cd "C:\Users\ebirot\Desktop\Cloud Field Campaign Scorecard\backend"
call venv\Scripts\activate.bat
python daily_refresh.py
pause
```

Double-cliquer sur `run_refresh.bat` pour tester!

---

## Option 3: Python Scheduler (Alternative)

Si tu préfères garder l'app Python toujours ouverte avec un scheduler intégré:

```python
# Dans backend/scheduler.py
import schedule
import time
from daily_refresh import export_all_views

# Schedule pour 23h00
schedule.every().day.at("23:00").do(export_all_views)

print("Scheduler started! Waiting for 23:00...")
while True:
    schedule.run_pending()
    time.sleep(60)  # Check every minute
```

Lancer avec: `python scheduler.py`

---

## 📊 Vérification

Après le premier run, vérifier:

1. **Fichiers CSV mis à jour** dans `/backend/data/`
   - Dates de modification = aujourd'hui 23h00+

2. **Timestamp file**: `/backend/data/last_refresh.txt`
   - Contient la date/heure du dernier refresh

3. **L'app affiche** la nouvelle date dans le header

---

## 🐛 Troubleshooting

**La tâche ne se lance pas:**
- Vérifier que le chemin Python est correct
- Vérifier les permissions (Run as Administrator)
- Vérifier que l'ordinateur ne se met pas en veille

**Erreur de connexion Tableau:**
- Vérifier les credentials dans `.env`
- Vérifier que le token n'a pas expiré (expire: May 28, 2027)

**Logs:**
- Les logs s'affichent dans la console
- Pour sauvegarder les logs: Rediriger vers un fichier dans Task Scheduler:
  - Arguments: `daily_refresh.py >> logs/refresh.log 2>&1`

---

## ✅ Configuration terminée!

Une fois configuré, le système:
- ✅ Exporte automatiquement les CSVs chaque soir à 23h00
- ✅ L'app affiche toujours les données les plus récentes
- ✅ Pas besoin d'intervention manuelle!
