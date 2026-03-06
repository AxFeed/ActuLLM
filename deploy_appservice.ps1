# =============================================================================
#  DEPLOY ACTULLM → AZURE APP SERVICE (conteneur unique)
#  Place ce script dans le même dossier que ton .env et lance-le.
#
#  Prérequis :
#    - Docker Desktop installé et lancé
#    - Azure CLI installé  (az login déjà fait)
#    - docker login déjà fait
# =============================================================================

$ErrorActionPreference = "Stop"

# -----------------------------------------------------------------------------
# CONFIG — à remplir
# -----------------------------------------------------------------------------
$DOCKERHUB_USER       = "axfeed"    # ex: axfeed
$AZURE_RESOURCE_GROUP = "llopezRG"               # ton RG existant
$AZURE_APP_NAME       = "actullmacr"             # ton App Service existant
$IMAGE                = "$DOCKERHUB_USER/actullm:latest"

# -----------------------------------------------------------------------------
# Chargement du .env
# -----------------------------------------------------------------------------
if (-Not (Test-Path ".env")) {
    Write-Error "❌ Fichier .env introuvable. Lance ce script depuis le dossier de ton projet."
    exit 1
}

$envVars = @{}
Get-Content ".env" | Where-Object { $_ -notmatch '^\s*#' -and $_ -match '=' } | ForEach-Object {
    $parts = $_ -split '=', 2
    $envVars[$parts[0].Trim()] = $parts[1].Trim()
}
Write-Host "✅ .env chargé ($($envVars.Count) variables)"

# -----------------------------------------------------------------------------
# ÉTAPE 1 — Build & push Docker Hub
# -----------------------------------------------------------------------------
Write-Host "🐳 Build et push de l'image unifiée..."

docker build -f Dockerfile -t $IMAGE .
docker push $IMAGE

Write-Host "✅ Image poussée : $IMAGE"

# -----------------------------------------------------------------------------
# ÉTAPE 2 — Configurer l'App Service pour utiliser l'image Docker Hub
# -----------------------------------------------------------------------------
Write-Host "⚙️  Configuration de l'App Service..."

az webapp config container set `
    --name $AZURE_APP_NAME `
    --resource-group $AZURE_RESOURCE_GROUP `
    --container-image-name $IMAGE `
    --container-registry-url "https://index.docker.io"

# -----------------------------------------------------------------------------
# ÉTAPE 3 — Injecter les variables d'environnement depuis le .env
# -----------------------------------------------------------------------------
Write-Host "🔐 Injection des variables d'environnement..."

# Ajouter API_URL (interne au conteneur) + toutes les vars du .env
$settings = @("API_URL=http://localhost:8000")
foreach ($key in $envVars.Keys) {
    $settings += "$key=$($envVars[$key])"
}

az webapp config appsettings set `
    --name $AZURE_APP_NAME `
    --resource-group $AZURE_RESOURCE_GROUP `
    --settings @settings

# -----------------------------------------------------------------------------
# ÉTAPE 4 — Démarrer l'app
# -----------------------------------------------------------------------------
Write-Host "🚀 Démarrage de l'App Service..."

az webapp start `
    --name $AZURE_APP_NAME `
    --resource-group $AZURE_RESOURCE_GROUP

$APP_URL = az webapp show `
    --name $AZURE_APP_NAME `
    --resource-group $AZURE_RESOURCE_GROUP `
    --query "defaultHostName" -o tsv

Write-Host ""
Write-Host "============================================"
Write-Host "✅ DÉPLOIEMENT TERMINÉ"
Write-Host "🌐 App accessible sur :"
Write-Host "   https://$APP_URL"
Write-Host "============================================"
