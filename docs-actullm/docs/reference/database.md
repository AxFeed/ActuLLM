# Base vectorielle (ChromaDB)

**Fichier :** `database.py`

Ce module gère le stockage et la recherche des articles dans **ChromaDB**, une base de données vectorielle persistante.

---

## Qu'est-ce qu'une base vectorielle ?

Contrairement à une base SQL qui cherche des correspondances exactes, une base vectorielle cherche des **similarités sémantiques**.

Chaque article est converti en un vecteur numérique (embedding) de plusieurs centaines de dimensions. Quand vous posez une question, elle est aussi convertie en vecteur — et ChromaDB trouve les articles dont le vecteur est le plus "proche" du vôtre.

!!! info "Distance cosinus"
    ActuLLM utilise la **similarité cosinus** (`hnsw:space: cosine`) : deux vecteurs sont proches si leur angle est petit, indépendamment de leur magnitude.

---

## Les fonctions disponibles

### `embed(texts)` — Générer des embeddings

```python
embed(texts: list[str]) -> list[list[float]]
```

Envoie une liste de textes à Azure OpenAI et retourne leurs embeddings (vecteurs).

---

### `upsert_articles(articles)` — Stocker des articles

```python
upsert_articles(articles: list[dict]) -> int
```

Stocke ou met à jour une liste d'articles dans ChromaDB.

- Les articles sont traités par **lots** (taille configurable via `BATCH_SIZE`, défaut : 50)
- Si un article avec le même `id` existe déjà, il est **mis à jour** (upsert)
- Retourne le nombre d'articles traités

---

### `search(query, n_results)` — Rechercher des articles

```python
search(query: str, n_results: int = 6) -> list[dict]
```

Recherche les articles les plus pertinents pour une question donnée.

**Étapes :**

1. La `query` est convertie en embedding
2. ChromaDB trouve les `n_results` vecteurs les plus proches
3. Les résultats sont triés par **date de publication** (du plus ancien au plus récent)

**Résultat retourné :**

```python
[
    {
        "text": "texte lemmatisé de l'article",
        "metadata": {
            "title": "Titre de l'article",
            "summary": "Résumé...",
            "url": "https://...",
            "source": "LeMonde",
            "published_at": "2025-03-05T10:30:00"
        },
        "distance": 0.12  # plus proche de 0 = plus pertinent
    },
    ...
]
```

!!! tip "Pourquoi trier par date ?"
    Les articles sont triés chronologiquement avant d'être envoyés au LLM. Cela lui permet de reconstituer l'évolution d'un événement dans le temps.

---

### `count()` — Compter les articles

```python
count() -> int
```

Retourne le nombre total d'articles dans la base.

---

### `reset_collection()` — Vider la base

```python
reset_collection()
```

Supprime et recrée la collection ChromaDB. Utile pour repartir de zéro.

---

## Persistance des données

ChromaDB stocke ses données sur disque dans le dossier défini par `CHROMA_PATH` (défaut : `./chroma_db`).

Avec Docker, ce dossier est monté dans un **volume nommé** (`chroma_data`) pour survivre aux redémarrages des conteneurs.
