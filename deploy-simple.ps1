# Script Simple de Deploiement GitHub
# Cloud Field Campaign Scorecard

Write-Host "================================" -ForegroundColor Cyan
Write-Host " Deploiement GitHub -> Heroku" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# 1. Git init
Write-Host "[1/4] Initialisation Git..." -ForegroundColor Yellow
if (-not (Test-Path .git)) {
    git init
    Write-Host "OK Git initialise" -ForegroundColor Green
} else {
    Write-Host "OK Git deja initialise" -ForegroundColor Green
}

# 2. Branche main
Write-Host ""
Write-Host "[2/4] Verification branche..." -ForegroundColor Yellow
$currentBranch = git branch --show-current
if ([string]::IsNullOrWhiteSpace($currentBranch)) {
    git checkout -b main
    $currentBranch = "main"
}
Write-Host "OK Branche: $currentBranch" -ForegroundColor Green

# 3. Commit
Write-Host ""
Write-Host "[3/4] Commit des fichiers..." -ForegroundColor Yellow
git add .
git commit -m "Deploy to Heroku - Ready for production"
Write-Host "OK Fichiers commites" -ForegroundColor Green

# 4. Remote GitHub
Write-Host ""
Write-Host "[4/4] Configuration GitHub..." -ForegroundColor Yellow
$remotes = git remote -v
$hasGitHub = $remotes -match "github.com"

if (-not $hasGitHub) {
    Write-Host ""
    Write-Host "Aucun remote GitHub detecte" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "1. Allez sur https://github.com/new" -ForegroundColor White
    Write-Host "2. Creez un repo: salesforce-scorecard" -ForegroundColor White
    Write-Host "3. Copiez l'URL du repo" -ForegroundColor White
    Write-Host ""

    $githubUrl = Read-Host "URL du repo GitHub (ou Enter pour passer)"

    if (-not [string]::IsNullOrWhiteSpace($githubUrl)) {
        git remote add origin $githubUrl
        Write-Host "OK Remote GitHub ajoute" -ForegroundColor Green

        $doPush = Read-Host "Pousser vers GitHub maintenant? (Y/n)"
        if ($doPush -ne "n") {
            git push -u origin $currentBranch
            Write-Host "OK Code pousse sur GitHub!" -ForegroundColor Green
        }
    }
} else {
    Write-Host "OK Remote GitHub deja configure" -ForegroundColor Green
    git remote -v

    $doPush = Read-Host "Pousser vers GitHub maintenant? (Y/n)"
    if ($doPush -ne "n") {
        git push -u origin $currentBranch
        Write-Host "OK Code pousse sur GitHub!" -ForegroundColor Green
    }
}

# Instructions finales
Write-Host ""
Write-Host "================================" -ForegroundColor Green
Write-Host "  CODE PRET POUR HEROKU" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host ""
Write-Host "PROCHAINES ETAPES:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Aller sur https://dashboard.heroku.com/" -ForegroundColor White
Write-Host "2. New -> Create new app" -ForegroundColor White
Write-Host "3. Deploy tab -> GitHub -> Connect repo" -ForegroundColor White
Write-Host "4. Settings tab -> Config Vars -> CORS_ORIGINS = *" -ForegroundColor White
Write-Host "5. Deploy tab -> Deploy Branch" -ForegroundColor White
Write-Host ""

$openHeroku = Read-Host "Ouvrir Heroku Dashboard? (Y/n)"
if ($openHeroku -ne "n") {
    Start-Process "https://dashboard.heroku.com/"
}

Write-Host ""
Write-Host "Documentation: DEPLOY_GITHUB_DESKTOP.md" -ForegroundColor Yellow
Write-Host "Bon deploiement!" -ForegroundColor Cyan
