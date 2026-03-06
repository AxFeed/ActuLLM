# Configuration

Toute la configuration se fait via le fichier **`.env`** à la racine du projet.

---

## Variables requises

### Azure OpenAI — Modèle de chat

| Variable | Description | Exemple |
|----------|-------------|---------|
| `AZURE_OPENAI_ENDPOINT` | URL de votre ressource Azure OpenAI | `https://mon-instance.openai.azure.com/` |
| `AZURE_OPENAI_API_KEY` | Clé API Azure OpenAI | `abc123...` |
| `AZURE_OPENAI_API_VERSION` | Version de l'API | `2024-02-01` |
| `AZURE_OPENAI_DEPLOYMENT` | Nom du déploiement du modèle de chat | `gpt-4o` |

### Azure OpenAI — Embeddings

| Variable | Description | Exemple |
|----------|-------------|---------|
| `AZURE_EMBEDDING_ENDPOINT` | URL de la ressource pour les embeddings | `https://mon-instance.openai.azure.com/` |
| `AZURE_EMBEDDING_API_KEY` | Clé API pour les embeddings | `def456...` |
| `AZURE_EMBEDDING_API_VERSION` | Version de l'API embeddings | `2023-05-15` |
| `AZURE_EMBEDDING_DEPLOYMENT` | Nom du déploiement du modèle d'embeddings | `text-embedding-ada-002` |

!!! note "Même ressource ou ressources séparées ?"
    Le chat et les embeddings peuvent pointer vers la même ressource Azure ou des ressources différentes — il suffit d'ajuster les URLs et clés en conséquence.

---

## Variables optionnelles

| Variable | Description | Défaut |
|----------|-------------|--------|
| `CHROMA_PATH` | Chemin de stockage de la base ChromaDB | `./chroma_db` |
| `COLLECTION_NAME` | Nom de la collection ChromaDB | `actullm` |
| `BATCH_SIZE` | Nombre d'articles envoyés à l'API embeddings en une fois | `50` |
| `API_URL` | URL de l'API (utilisée par Streamlit) | — |

---

## Ajouter des flux RSS

Les flux RSS sont définis dans **`config.py`** :

```python
RSS_FEEDS = [
    {
        "name": "France24 FR",
        "url": "https://www.france24.com/fr/rss",
        "language": "fr",
    },
    {
        "name": "LeMonde",
        "url": "https://www.lemonde.fr/rss/une.xml",
        "language": "fr",
    },
    {
        "name": "HackerNews",
        "url": "https://hnrss.org/frontpage",
        "language": "en",
    }
]
```

Pour ajouter une source, ajoutez un dictionnaire avec :

- `name` : nom affiché dans les réponses du LLM
- `url` : URL du flux RSS
- `language` : `"fr"` ou `"en"` (détermine le modèle spaCy utilisé)

!!! warning "Langues supportées"
    Seuls `"fr"` et `"en"` sont supportés. Tout autre valeur utilisera le modèle français par défaut.
