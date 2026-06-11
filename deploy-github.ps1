# Script de Déploiement via GitHub
# Cloud Field Campaign Scorecard

Write-Host "================================" -ForegroundColor Cyan
Write-Host " Déploiement GitHub → Heroku" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Ce script prépare votre code pour GitHub et vous guide vers Heroku" -ForegroundColor Yellow
Write-Host ""

# 1. Vérifier Git
Write-Host "[1/5] Vérification Git..." -ForegroundColor Yellow
if (-not (Test-Path .git)) {
    Write-Host "Initialisation Git..." -ForegroundColor Yellow
    git init
    Write-Host "✅ Git initialisé" -ForegroundColor Green
} else {
    Write-Host "✅ Git déjà initialisé" -ForegroundColor Green
}

# 2. Vérifier la branche
Write-Host ""
Write-Host "[2/5] Vérification branche..." -ForegroundColor Yellow
$currentBranch = git branch --show-current
if ([string]::IsNullOrWhiteSpace($currentBranch)) {
    Write-Host "Création de la branche 'main'..." -ForegroundColor Yellow
    git checkout -b main
    $currentBranch = "main"
}
Write-Host "✅ Branche actuelle: $currentBranch" -ForegroundColor Green

# 3. Ajouter et commiter
Write-Host ""
Write-Host "[3/5] Préparation des fichiers..." -ForegroundColor Yellow
git add .

$commitMsg = Read-Host "Message de commit (ou Enter pour 'Initial commit for Heroku')"
if ([string]::IsNullOrWhiteSpace($commitMsg)) {
    $commitMsg = "Initial commit for Heroku - $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
}
git commit -m "$commitMsg"
Write-Host "✅ Fichiers commités" -ForegroundColor Green

# 4. Vérifier remote GitHub
Write-Host ""
Write-Host "[4/5] Configuration GitHub..." -ForegroundColor Yellow
$remotes = git remote -v
$hasGitHub = $remotes -match "github.com"

if (-not $hasGitHub) {
    Write-Host ""
    Write-Host "⚠️ Aucun remote GitHub détecté" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Instructions:" -ForegroundColor Cyan
    Write-Host "1. Créez un nouveau repo sur https://github.com/new" -ForegroundColor White
    Write-Host "2. Copiez l'URL du repo (ex: https://github.com/username/salesforce-scorecard.git)" -ForegroundColor White
    Write-Host ""

    $githubUrl = Read-Host "Collez l'URL du repo GitHub (ou Enter pour passer)"

    if (-not [string]::IsNullOrWhiteSpace($githubUrl)) {
        git remote add origin $githubUrl
        Write-Host "✅ Remote GitHub ajouté: $githubUrl" -ForegroundColor Green
    } else {
        Write-Host "⏭️ Étape sautée" -ForegroundColor Yellow
    }
} else {
    Write-Host "✅ Remote GitHub déjà configuré" -ForegroundColor Green
    git remote -v | ForEach-Object { Write-Host "   $_" -ForegroundColor Gray }
}

# 5. Push vers GitHub
Write-Host ""
Write-Host "[5/5] Push vers GitHub..." -ForegroundColor Yellow

if ($hasGitHub -or -not [string]::IsNullOrWhiteSpace($githubUrl)) {
    $pushConfirm = Read-Host "Pousser vers GitHub maintenant? (Y/n)"

    if ($pushConfirm -ne "n") {
        git push -u origin $currentBranch

        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Code poussé vers GitHub!" -ForegroundColor Green
        } else {
            Write-Host "⚠️ Erreur lors du push. Vérifiez vos credentials GitHub." -ForegroundColor Yellow
        }
    }
} else {
    Write-Host "⏭️ Pas de remote GitHub configuré" -ForegroundColor Yellow
}

# 6. Instructions Heroku
Write-Host ""
Write-Host "================================" -ForegroundColor Green
Write-Host "  ✅ CODE PRÊT POUR HEROKU !" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host ""

Write-Host "📋 PROCHAINES ÉTAPES SUR HEROKU:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1️⃣  Aller sur https://dashboard.heroku.com/" -ForegroundColor White
Write-Host "2️⃣  Créer une nouvelle app (New → Create new app)" -ForegroundColor White
Write-Host "3️⃣  Dans l'onglet 'Deploy':" -ForegroundColor White
Write-Host "    - Choisir 'GitHub' comme deployment method" -ForegroundColor Gray
Write-Host "    - Connecter votre repo GitHub" -ForegroundColor Gray
Write-Host "    - Activer 'Automatic deploys' (optionnel)" -ForegroundColor Gray
Write-Host "    - Cliquer 'Deploy Branch'" -ForegroundColor Gray
Write-Host "4️⃣  Dans l'onglet 'Settings' → Config Vars:" -ForegroundColor White
Write-Host "    - Ajouter CORS_ORIGINS = *" -ForegroundColor Gray
Write-Host "5️⃣  Attendre le déploiement et ouvrir l'app!" -ForegroundColor White
Write-Host ""

Write-Host "📚 Documentation complète: DEPLOY_VIA_GITHUB.md" -ForegroundColor Yellow
Write-Host ""

$openHeroku = Read-Host "Ouvrir le Dashboard Heroku maintenant? (Y/n)"
if ($openHeroku -ne "n") {
    Start-Process "https://dashboard.heroku.com/"
}

$openGitHub = Read-Host "Ouvrir votre repo GitHub maintenant? (Y/n)"
if ($openGitHub -ne "n" -and $hasGitHub) {
    $repoUrl = git remote get-url origin
    $repoUrl = $repoUrl -replace "\.git$", ""
    Start-Process $repoUrl
}

Write-Host ""
Write-Host "✨ Bon déploiement!" -ForegroundColor Cyan
