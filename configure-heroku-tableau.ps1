# 🚀 Script de Configuration Heroku - Tableau Refresh
# Configure automatiquement les Config Vars Tableau sur Heroku

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Configuration Heroku - Tableau Auto-Refresh  " -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Vérifier que Heroku CLI est installé
Write-Host "🔍 Vérification Heroku CLI..." -ForegroundColor Yellow
$herokuVersion = heroku --version 2>$null
if (-not $herokuVersion) {
    Write-Host "❌ ERREUR: Heroku CLI n'est pas installé" -ForegroundColor Red
    Write-Host "   Installer: https://devcenter.heroku.com/articles/heroku-cli" -ForegroundColor Yellow
    exit 1
}
Write-Host "✅ Heroku CLI détecté" -ForegroundColor Green
Write-Host ""

# Demander le nom de l'app
Write-Host "📱 Quel est le nom de ton app Heroku ?" -ForegroundColor Yellow
Write-Host "   (Ex: salesforce-scorecard-emea)" -ForegroundColor Gray
$appName = Read-Host "Nom de l'app"

if ([string]::IsNullOrWhiteSpace($appName)) {
    Write-Host "❌ Nom d'app requis" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🔐 Lecture des credentials depuis .env local..." -ForegroundColor Yellow

# Lire le fichier .env
$envFile = Join-Path $PSScriptRoot "backend\.env"
if (-not (Test-Path $envFile)) {
    Write-Host "❌ Fichier .env introuvable: $envFile" -ForegroundColor Red
    exit 1
}

# Parser le .env
$envVars = @{}
Get-Content $envFile | ForEach-Object {
    if ($_ -match '^([^#][^=]+)=(.*)$') {
        $key = $matches[1].Trim()
        $value = $matches[2].Trim()
        $envVars[$key] = $value
    }
}

# Extraire les valeurs Tableau
$tableauServerUrl = $envVars["TABLEAU_SERVER_URL"]
$tableauSiteId = $envVars["TABLEAU_SITE_ID"]
$tableauTokenName = $envVars["TABLEAU_TOKEN_NAME"]
$tableauTokenValue = $envVars["TABLEAU_TOKEN_VALUE"]
$tableauWorkbookId = $envVars["TABLEAU_WORKBOOK_MDP_SCORECARD"]
$tableauApiVersion = $envVars["TABLEAU_API_VERSION"]

Write-Host ""
Write-Host "📊 Credentials trouvés:" -ForegroundColor Green
Write-Host "   Server: $tableauServerUrl" -ForegroundColor Gray
Write-Host "   Site: $tableauSiteId" -ForegroundColor Gray
Write-Host "   Token Name: $tableauTokenName" -ForegroundColor Gray
Write-Host "   Token Value: $($tableauTokenValue.Substring(0, 10))..." -ForegroundColor Gray
Write-Host "   Workbook ID: $tableauWorkbookId" -ForegroundColor Gray
Write-Host "   API Version: $tableauApiVersion" -ForegroundColor Gray
Write-Host ""

# Confirmation
Write-Host "⚠️  Ces Config Vars vont être ajoutées sur Heroku app: $appName" -ForegroundColor Yellow
Write-Host "   Continuer ? (O/N)" -ForegroundColor Yellow
$confirm = Read-Host
if ($confirm -ne "O" -and $confirm -ne "o") {
    Write-Host "❌ Annulé" -ForegroundColor Red
    exit 0
}

Write-Host ""
Write-Host "🚀 Configuration de Heroku en cours..." -ForegroundColor Cyan
Write-Host ""

# Configurer Heroku
$configVars = @{
    "TABLEAU_SERVER_URL" = $tableauServerUrl
    "TABLEAU_SITE_ID" = $tableauSiteId
    "TABLEAU_TOKEN_NAME" = $tableauTokenName
    "TABLEAU_TOKEN_VALUE" = $tableauTokenValue
    "TABLEAU_WORKBOOK_MDP_SCORECARD" = $tableauWorkbookId
    "TABLEAU_API_VERSION" = $tableauApiVersion
}

$success = 0
$failed = 0

foreach ($key in $configVars.Keys) {
    $value = $configVars[$key]

    if ([string]::IsNullOrWhiteSpace($value)) {
        Write-Host "⚠️  $key : valeur manquante, ignoré" -ForegroundColor Yellow
        continue
    }

    Write-Host "📝 Configuration de $key..." -ForegroundColor Gray

    try {
        $result = heroku config:set "$key=$value" --app $appName 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   ✅ OK" -ForegroundColor Green
            $success++
        } else {
            Write-Host "   ❌ ERREUR: $result" -ForegroundColor Red
            $failed++
        }
    } catch {
        Write-Host "   ❌ ERREUR: $_" -ForegroundColor Red
        $failed++
    }
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "✅ Configuration terminée !" -ForegroundColor Green
Write-Host "   Succès: $success" -ForegroundColor Green
Write-Host "   Échecs: $failed" -ForegroundColor $(if ($failed -gt 0) { "Red" } else { "Gray" })
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Vérifier les Config Vars
Write-Host "🔍 Vérification des Config Vars sur Heroku..." -ForegroundColor Yellow
Write-Host ""
heroku config --app $appName | Select-String "TABLEAU"
Write-Host ""

# Instructions suivantes
Write-Host "📋 Prochaines Étapes:" -ForegroundColor Cyan
Write-Host "   1. Vérifier le déploiement:" -ForegroundColor Gray
Write-Host "      heroku logs --tail --app $appName" -ForegroundColor White
Write-Host ""
Write-Host "   2. Tester le scheduler:" -ForegroundColor Gray
Write-Host "      https://$appName.herokuapp.com/api/refresh/status" -ForegroundColor White
Write-Host ""
Write-Host "   3. Déclencher un refresh manuel:" -ForegroundColor Gray
Write-Host "      https://$appName.herokuapp.com/docs" -ForegroundColor White
Write-Host "      (Chercher: POST /api/refresh/trigger)" -ForegroundColor White
Write-Host ""

Write-Host "🎉 Le refresh automatique à 6h est ACTIF !" -ForegroundColor Green
Write-Host ""
