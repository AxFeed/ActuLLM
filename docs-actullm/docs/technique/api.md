# api.py — Référence technique

**Rôle :** Expose les fonctionnalités d'ActuLLM via une API REST (FastAPI). Point central qui orchestre les appels vers `database`, `prompting` et `RSS`.

**Importe :** `fastapi`, `openai.AzureOpenAI`, `database`, `prompting`, `RSS`

**Importé par :** `app.py` (via HTTP, pas en import Python)

---

## Variables globales

| Variable | Type | Description |
|----------|------|-------------|
| `app` | `FastAPI` | Instance principale de l'application FastAPI |
| `azure_client` | `AzureOpenAI` | Client Azure OpenAI pour les appels LLM (chat) |

---

## Modèles Pydantic

### `QuestionRequest`

```python
class QuestionRequest(BaseModel):
    question: str
    history:  list[dict] = []
```

Modèle de validation pour les corps de requêtes des routes `/ask/*`.

| Champ | Type | Défaut | Description |
|-------|------|--------|-------------|
| `question` | `str` | — | La question posée par l'utilisateur |
| `history` | `list[dict]` | `[]` | Historique de la conversation au format `[{"role": "user"/"assistant", "content": "..."}]` |

---

## Fonctions internes

### `call(messages, system)`

```python
def call(messages: list[dict], system: str) -> str
```

Envoie un ensemble de messages au LLM Azure OpenAI et retourne la réponse.

| Paramètre | Type | Description |
|-----------|------|-------------|
| `messages` | `list[dict]` | Historique + message utilisateur courant |
| `system` | `str` | System prompt à placer en tête de la conversation |

**Séquence :**

```
full_messages = [{"role": "system", "content": system}] + messages
azure_client.chat.completions.create(
    model=AZURE_OPENAI_DEPLOYMENT,
    messages=full_messages
)
```

**Retourne :** `str` — contenu textuel de la réponse du LLM.

**Appelée par :** `ask_with_rag()`, `ask_without_rag()`

---

### `ask_with_rag(question, history)`

```python
def ask_with_rag(question: str, history: list[dict] = None) -> tuple[str, list[dict]]
```

Orchestre une réponse augmentée par les articles indexés.

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `question` | `str` | — | Question de l'utilisateur |
| `history` | `list[dict]` | `None` | Historique conversationnel |

**Séquence d'appels :**

```
database.search(question)             →  articles
prompting.build_rag_message(question, articles)  →  user_message
call(history + [user_message], SYSTEM_WITH_RAG)  →  answer
```

**Retourne :** `tuple[str, list[dict]]` — `(réponse_textuelle, articles_utilisés)`

**Appelée par :** route `POST /ask/rag`

---

### `ask_without_rag(question, history)`

```python
def ask_without_rag(question: str, history: list[dict] = None) -> str
```

Génère une réponse sans contexte d'articles (mémoire du LLM uniquement).

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `question` | `str` | — | Question de l'utilisateur |
| `history` | `list[dict]` | `None` | Historique conversationnel |

**Séquence :**

```
prompting.build_plain_message(question)  →  user_message
call(history + [user_message], SYSTEM_WITHOUT_RAG)  →  answer
```

**Retourne :** `str` — réponse textuelle du LLM.

**Appelée par :** route `POST /ask/plain`

---

## Routes HTTP

### `POST /ask/rag`

Réponse avec articles de contexte.

**Corps :** `QuestionRequest`

**Retourne :**

```json
{
  "answer": "string",
  "articles": [
    {
      "text": "string",
      "metadata": { "title": "...", "url": "...", "source": "...", "published_at": "..." },
      "distance": 0.08
    }
  ]
}
```

**Erreur :** `HTTP 500` avec `{"detail": "message d'erreur"}` en cas d'exception.

---

### `POST /ask/plain`

Réponse sans contexte.

**Corps :** `QuestionRequest`

**Retourne :**

```json
{
  "answer": "string"
}
```

---

### `POST /ingest`

Lance l'ingestion RSS.

**Paramètre query :** `reset: bool = False`

**Retourne :**

```json
{
  "ingest": true,
  "count": 142
}
```

---

### `GET /health`

Vérifie l'état du service.

**Retourne :**

```json
{
  "status": "ok",
  "deployment": "gpt-4o",
  "news_count": 142
}
```
