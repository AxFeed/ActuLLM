# API FastAPI

**Fichier :** `api.py`

L'API expose les fonctionnalités d'ActuLLM via HTTP. Elle est construite avec **FastAPI** et accessible par défaut sur le port `8000`.

La documentation interactive (Swagger) est disponible à l'adresse : **http://localhost:8000/docs**

---

## Endpoints

### `GET /health` — État du service

Vérifie que l'API fonctionne et retourne des infos de base.

**Réponse :**

```json
{
  "status": "ok",
  "deployment": "gpt-4o",
  "news_count": 142
}
```

---

### `POST /ingest` — Ingérer les articles

Lance la récupération et l'indexation des articles RSS.

**Paramètre optionnel :**

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `reset` | bool | `false` | Si `true`, vide la base avant d'ingérer |

**Exemple :**

```bash
# Mise à jour normale
curl -X POST http://localhost:8000/ingest

# Remise à zéro complète
curl -X POST "http://localhost:8000/ingest?reset=true"
```

**Réponse :**

```json
{
  "ingest": true,
  "count": 142
}
```

---

### `POST /ask/rag` — Question avec RAG

Pose une question en utilisant les articles indexés comme contexte.

**Corps de la requête :**

```json
{
  "question": "Que se passe-t-il au Moyen-Orient ?",
  "history": [
    {"role": "user", "content": "Bonjour"},
    {"role": "assistant", "content": "Bonjour ! Comment puis-je vous aider ?"}
  ]
}
```

| Champ | Type | Description |
|-------|------|-------------|
| `question` | string | La question de l'utilisateur |
| `history` | list | Historique de la conversation (optionnel) |

**Réponse :**

```json
{
  "answer": "Selon les articles de France24 et LeMonde...",
  "articles": [
    {
      "text": "...",
      "metadata": { "title": "...", "url": "..." },
      "distance": 0.08
    }
  ]
}
```

---

### `POST /ask/plain` — Question sans RAG

Pose la même question directement au LLM, sans contexte d'articles.

**Corps de la requête :** identique à `/ask/rag`

**Réponse :**

```json
{
  "answer": "D'après mes connaissances jusqu'à ma date de coupure..."
}
```

---

## La fonction `call()`

Toutes les requêtes au LLM passent par cette fonction centrale :

```python
def call(messages: list[dict], system: str) -> str:
    full_messages = [{"role": "system", "content": system}] + messages
    response = azure_client.chat.completions.create(
        model=os.environ.get("AZURE_OPENAI_DEPLOYMENT"),
        messages=full_messages,
    )
    return response.choices[0].message.content
```

Elle assemble le message système + l'historique + la question, puis appelle Azure OpenAI.
