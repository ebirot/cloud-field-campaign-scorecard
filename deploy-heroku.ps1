# Script de Déploiement Heroku
# Cloud Field Campaign Scorecard

Write-Host "================================" -ForegroundColor Cyan
Write-Host " Déploiement Heroku - Scorecard" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# 1. Vérifier que Heroku CLI est installé
Write-Host "[1/6] Vérification Heroku CLI..." -ForegroundColor Yellow
$herokuVersion = heroku --version 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Heroku CLI n'est pas installé!" -ForegroundColor Red
    Write-Host "Installer avec: winget install Heroku.HerokuCLI" -ForegroundColor Yellow
    exit 1
}
Write-Host "✅ Heroku CLI installé: $herokuVersion" -ForegroundColor Green

# 2. Vérifier que Git est initialisé
Write-Host "[2/6] Vérification Git..." -ForegroundColor Yellow
if (-not (Test-Path .git)) {
    Write-Host "Initialisation Git..." -ForegroundColor Yellow
    git init
    Write-Host "✅ Git initialisé" -ForegroundColor Green
} else {
    Write-Host "✅ Git déjà initialisé" -ForegroundColor Green
}

# 3. Ajouter les fichiers
Write-Host "[3/6] Ajout des fichiers..." -ForegroundColor Yellow
git add .
git status --short

# 4. Commit
Write-Host "[4/6] Commit des changements..." -ForegroundColor Yellow
$commitMsg = Read-Host "Message de commit (ou Enter pour 'Deploy to Heroku')"
if ([string]::IsNullOrWhiteSpace($commitMsg)) {
    $commitMsg = "Deploy to Heroku - $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
}
git commit -m "$commitMsg"

# 5. Vérifier si l'app Heroku existe
Write-Host "[5/6] Vérification app Heroku..." -ForegroundColor Yellow
$appName = Read-Host "Nom de l'app Heroku (ou Enter pour 'salesforce-scorecard')"
if ([string]::IsNullOrWhiteSpace($appName)) {
    $appName = "salesforce-scorecard"
}

$herokuApps = heroku apps --json | ConvertFrom-Json
$appExists = $herokuApps | Where-Object { $_.name -eq $appName }

if (-not $appExists) {
    Write-Host "L'app '$appName' n'existe pas. Création..." -ForegroundColor Yellow
    heroku create $appName
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ App créée: https://$appName.herokuapp.com" -ForegroundColor Green
    } else {
        Write-Host "❌ Erreur lors de la création de l'app" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "✅ App '$appName' existe déjà" -ForegroundColor Green
    # Vérifier si le remote existe
    $remoteExists = git remote | Where-Object { $_ -eq "heroku" }
    if (-not $remoteExists) {
        heroku git:remote -a $appName
        Write-Host "✅ Remote Heroku ajouté" -ForegroundColor Green
    }
}

# 6. Déployer
Write-Host "[6/6] Déploiement vers Heroku..." -ForegroundColor Yellow
Write-Host "Push vers heroku main..." -ForegroundColor Cyan

git push heroku main -f

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "================================" -ForegroundColor Green
    Write-Host "  ✅ DÉPLOIEMENT RÉUSSI !" -ForegroundColor Green
    Write-Host "================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "🌐 URL: https://$appName.herokuapp.com/" -ForegroundColor Cyan
    Write-Host "📊 Dashboard: https://$appName.herokuapp.com/" -ForegroundColor Cyan
    Write-Host "📚 API Docs: https://$appName.herokuapp.com/docs" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Voir les logs: heroku logs --tail" -ForegroundColor Yellow
    Write-Host "Ouvrir l'app: heroku open" -ForegroundColor Yellow
    Write-Host ""

    $openApp = Read-Host "Ouvrir l'application maintenant? (Y/n)"
    if ($openApp -ne "n") {
        heroku open
    }
} else {
    Write-Host ""
    Write-Host "❌ ÉCHEC DU DÉPLOIEMENT" -ForegroundColor Red
    Write-Host ""
    Write-Host "Voir les logs: heroku logs --tail" -ForegroundColor Yellow
}
