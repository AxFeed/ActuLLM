# database.py — Référence technique

**Rôle :** Gère la persistance des articles dans ChromaDB et la génération des embeddings via Azure OpenAI.

**Importe :** `chromadb`, `openai.AzureOpenAI`, `dotenv`

**Importé par :** `api.py` (`search`, `count`), `RSS.py` (`create_collection`, `upsert_articles`, `reset_collection`)

---

## Variables globales

| Variable | Type | Description |
|----------|------|-------------|
| `azure_client` | `AzureOpenAI` | Client OpenAI pour le chat (non utilisé directement ici) |
| `embedding_client` | `AzureOpenAI` | Client OpenAI pour générer les embeddings |
| `N_RESULTS` | `int` | Nombre de résultats par défaut lors d'une recherche (`6`) |

---

## Fonctions

### `embed(texts)`

```python
def embed(texts: list[str]) -> list[list[float]]
```

Génère les représentations vectorielles (embeddings) d'une liste de textes.

| Paramètre | Type | Description |
|-----------|------|-------------|
| `texts` | `list[str]` | Liste de textes à vectoriser |

**Appel externe :** `embedding_client.embeddings.create(model=AZURE_EMBEDDING_DEPLOYMENT, input=texts)`

**Retourne :** `list[list[float]]` — un vecteur par texte en entrée.

**Appelée par :** `upsert_articles()`, `search()`

---

### `_get_collection()`

```python
def _get_collection() -> chromadb.Collection
```

Retourne (ou crée) la collection ChromaDB configurée.

**Comportement :** Ouvre le client persistant pointant vers `CHROMA_PATH`, puis appelle `get_or_create_collection` avec le nom `COLLECTION_NAME` et la distance cosinus.

**Retourne :** `chromadb.Collection`

**Appelée par :** toutes les autres fonctions du module.

!!! note "Fonction privée"
    Le préfixe `_` indique que cette fonction est interne au module. Elle n'est pas importée directement par les autres modules.

---

### `create_collection()`

```python
def create_collection() -> chromadb.Collection
```

S'assure que la collection existe et affiche le nombre de documents en log.

**Retourne :** `chromadb.Collection`

**Appelée par :** `RSS.ingest()` (quand `reset=False`)

---

### `reset_collection()`

```python
def reset_collection() -> None
```

Supprime la collection existante puis la recrée vide.

**Séquence :**

```
chroma.delete_collection(COLLECTION_NAME)
    └── create_collection()
```

**Appelée par :** `RSS.ingest()` (quand `reset=True`)

---

### `upsert_articles(articles)`

```python
def upsert_articles(articles: list[dict]) -> int
```

Stocke ou met à jour les articles dans ChromaDB, par lots.

| Paramètre | Type | Description |
|-----------|------|-------------|
| `articles` | `list[dict]` | Articles au format produit par `RSS.fetch_articles()` |

**Séquence interne :**

```
pour chaque lot de BATCH_SIZE articles :
    ├── extraire les textes lemmatisés
    ├── embed(textes)  →  vecteurs
    └── collection.upsert(ids, embeddings, documents, metadatas)
```

**Retourne :** `int` — nombre total d'articles traités.

**Appelée par :** `RSS.ingest()`

---

### `search(query, n_results)`

```python
def search(query: str, n_results: int = N_RESULTS) -> list[dict]
```

Recherche les articles les plus sémantiquement proches d'une question.

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `query` | `str` | — | Question ou texte de recherche |
| `n_results` | `int` | `6` | Nombre maximum de résultats à retourner |

**Séquence :**

```
embed([query])  →  query_vector
collection.query(query_embeddings=[query_vector], n_results=n_results)
    └── tri des résultats par metadata.published_at (chronologique)
```

**Retourne :** `list[dict]` au format :

```python
[
    {
        "text": str,           # texte lemmatisé de l'article
        "metadata": {
            "title": str,
            "summary": str,
            "url": str,
            "source": str,
            "language": str,
            "published_at": str,
        },
        "distance": float,     # 0 = identique, 1 = opposé (cosinus)
    }
]
```

!!! tip "Distance cosinus"
    Une `distance` proche de **0** indique un article très pertinent. Une `distance` proche de **1** indique un article peu lié à la question.

**Appelée par :** `api.ask_with_rag()`

---

### `count()`

```python
def count() -> int
```

Retourne le nombre total d'articles dans la collection.

**Retourne :** `int`

**Appelée par :** `api.py` (routes `/ingest` et `/health`)
