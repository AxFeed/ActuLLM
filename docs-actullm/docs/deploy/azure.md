# Déploiement sur Azure App Service

Le projet inclut deux scripts PowerShell pour déployer sur Azure App Service.

---

## Prérequis

- **Azure CLI** installé et connecté (`az login`)
- **Docker** installé et démarré
- Une **Azure Container Registry (ACR)** ou l'accès à un registre Docker
- Un **Azure App Service Plan** (Linux, niveau B1 minimum recommandé)

---

## Premier déploiement : `deploy_appservice.ps1`

Ce script effectue le déploiement initial complet :

1. Build de l'image Docker
2. Push vers le registre de conteneurs
3. Création ou mise à jour de l'App Service
4. Configuration des variables d'environnement

```powershell
.\deploy_appservice.ps1
```

!!! info "Configuration du script"
    Avant d'exécuter, éditez le script pour renseigner vos paramètres Azure :
    
    - Nom du groupe de ressources
    - Nom de l'App Service
    - URL du registre de conteneurs

---

## Mise à jour : `update_appservice.ps1`

Pour les déploiements suivants (après modification du code) :

```powershell
.\update_appservice.ps1
```

Ce script plus rapide :

1. Rebuild l'image Docker
2. Push la nouvelle version
3. Redémarre l'App Service

---

## Variables d'environnement sur Azure

Sur Azure App Service, les variables du fichier `.env` doivent être configurées dans les **paramètres d'application** (Application Settings) :

1. Allez dans votre App Service → **Configuration** → **Paramètres d'application**
2. Ajoutez chaque variable de votre `.env`
3. Cliquez sur **Enregistrer** — l'App Service redémarre automatiquement

!!! warning "Ne pas commiter le .env"
    Le fichier `.env` contient des clés sensibles. Il est listé dans `.gitignore` et ne doit jamais être poussé sur Git.

---

## Vérifier le déploiement

Une fois déployé, vérifiez que l'API répond :

```bash
curl https://<votre-app>.azurewebsites.net/health
```

```json
{
  "status": "ok",
  "deployment": "gpt-4o",
  "news_count": 0
}
```

Puis lancez une première ingestion :

```bash
curl -X POST https://<votre-app>.azurewebsites.net/ingest
```
