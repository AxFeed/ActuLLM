# =============================================================================
#  MISE À JOUR — rebuild + redeploy
# =============================================================================

$ErrorActionPreference = "Stop"

$DOCKERHUB_USER       = "axfeed"
$AZURE_RESOURCE_GROUP = "llopezRG"
$AZURE_APP_NAME       = "actullmacr"
$IMAGE                = "$DOCKERHUB_USER/actullm:latest"

Write-Host "🐳 Rebuild et push..."
docker build -f Dockerfile -t $IMAGE .
docker push $IMAGE

Write-Host "🔄 Redémarrage de l'App Service..."
az webapp restart --name $AZURE_APP_NAME --resource-group $AZURE_RESOURCE_GROUP

Write-Host "✅ Mise à jour terminée"
