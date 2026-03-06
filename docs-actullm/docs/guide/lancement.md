# Lancer le projet

## Avec Docker (recommandé)

```bash
docker compose up --build
```

| Service | URL |
|---------|-----|
| Interface Streamlit | http://localhost:8501 |
| API FastAPI | http://localhost:8000 |
| Documentation API | http://localhost:8000/docs |

Pour arrêter :

```bash
docker compose down
```

---

## Sans Docker (développement local)

Lancez les deux services dans deux terminaux séparés.

**Terminal 1 — API :**

```bash
uvicorn api:app --reload --port 8000
```

**Terminal 2 — Interface :**

```bash
streamlit run app.py
```

---

## Première utilisation

Une fois les services démarrés, la base de données est **vide**. Il faut d'abord ingérer des articles.

### Via l'interface

1. Ouvrez http://localhost:8501
2. Dans la **sidebar gauche**, cliquez sur **"Mettre à jour les articles"**
3. Attendez la fin de l'ingestion (quelques secondes)
4. Le compteur d'articles indexés se met à jour

### Via l'API directement

```bash
curl -X POST http://localhost:8000/ingest
```

Réponse attendue :

```json
{
  "ingest": true,
  "count": 142
}
```

---

## Vérifier que tout fonctionne

```bash
curl http://localhost:8000/health
```

```json
{
  "status": "ok",
  "deployment": "gpt-4o",
  "news_count": 142
}
```

!!! success "Vous êtes prêt !"
    Si `news_count` est supérieur à 0, vous pouvez poser vos premières questions dans l'interface.
