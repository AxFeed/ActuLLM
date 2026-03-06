# Déploiement avec Docker

## Architecture Docker

Le projet utilise **deux modes Docker** selon le contexte :

### Mode Docker Compose (développement / serveur simple)

`docker-compose.yml` définit deux services indépendants :

| Service | Conteneur | Port |
|---------|-----------|------|
| `api` | `actullm_api` | 8000 |
| `app` | `actullm_app` | 8501 |

Les données ChromaDB sont persistées dans le volume nommé `chroma_data`.

### Mode Dockerfile unique (Azure App Service)

Le `Dockerfile` principal fusionne les deux services dans un seul conteneur :

- **Nginx** joue le rôle de reverse proxy sur le port 80
- **Supervisor** gère les deux processus (FastAPI + Streamlit) simultanément
- **Nginx** redirige les requêtes vers le bon service selon le chemin

---

## Commandes Docker Compose

```bash
# Démarrer les services (en arrière-plan)
docker compose up -d --build

# Voir les logs en temps réel
docker compose logs -f

# Arrêter les services
docker compose down

# Vider et recréer les données ChromaDB
docker compose down -v
docker compose up -d --build
```

---

## Configuration Nginx

`nginx.conf` configure le reverse proxy :

- Les requêtes vers `/` sont redirigées vers Streamlit (port 8501)
- Les requêtes vers `/api/` sont redirigées vers FastAPI (port 8000)

---

## Configuration Supervisor

`supervisord.conf` démarre et supervise les deux processus :

```ini
[program:api]
command=uvicorn api:app --host 0.0.0.0 --port 8000

[program:app]
command=streamlit run app.py --server.port 8501
```

Si l'un des processus plante, Supervisor le redémarre automatiquement.

---

## Volume de données

```yaml
volumes:
  chroma_data:
```

Le volume `chroma_data` est monté dans `/app/chroma_db` du conteneur `api`. Les articles indexés survivent aux redémarrages des conteneurs.

!!! danger "Attention"
    `docker compose down -v` supprime le volume et **efface tous les articles indexés**. Il faudra relancer une ingestion.
