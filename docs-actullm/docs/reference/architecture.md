# Vue d'ensemble de l'architecture

## Le principe du RAG

**RAG** signifie *Retrieval-Augmented Generation* — en français : génération augmentée par récupération.

L'idée est simple : plutôt que de demander au LLM de répondre de mémoire (ce qui peut produire des informations obsolètes ou inventées), on lui fournit **de vrais documents récents** en contexte.

```
Question utilisateur
       │
       ▼
┌─────────────────┐
│  Recherche dans │  ←── Articles indexés dans ChromaDB
│   ChromaDB      │
└────────┬────────┘
         │ Articles pertinents
         ▼
┌─────────────────┐
│  Construction   │
│  du prompt RAG  │
└────────┬────────┘
         │ Prompt enrichi
         ▼
┌─────────────────┐
│  Azure OpenAI   │
│  (LLM)          │
└────────┬────────┘
         │ Réponse sourcée
         ▼
    Utilisateur
```

---

## Les deux modes de réponse

ActuLLM affiche côte à côte deux réponses pour illustrer l'apport du RAG :

| Mode | Comment ça marche | Avantage |
|------|-------------------|----------|
| ✅ **Avec RAG** | Articles récents injectés dans le contexte | Réponses précises, sourcées, à jour |
| ❌ **Sans RAG** | Question posée directement au LLM | Réponses basées sur la mémoire d'entraînement |

---

## Flux de données complet

### 1. Ingestion (mise à jour des articles)

```
Flux RSS (France24, LeMonde, HackerNews...)
       │
       ▼
  feedparser (parsing XML)
       │
       ▼
  Nettoyage HTML (BeautifulSoup)
       │
       ▼
  Lemmatisation (spaCy fr/en)
       │
       ▼
  Déduplication par hash MD5 de l'URL
       │
       ▼
  Génération d'embeddings (Azure OpenAI)
       │
       ▼
  Stockage dans ChromaDB
```

### 2. Question utilisateur (mode RAG)

```
Question utilisateur (Streamlit)
       │
       ▼
  POST /ask/rag (FastAPI)
       │
       ▼
  Embedding de la question (Azure OpenAI)
       │
       ▼
  Recherche par similarité cosinus (ChromaDB)
  → Top 6 articles les plus proches
       │
       ▼
  Construction du prompt avec les articles
       │
       ▼
  Appel Azure OpenAI (GPT)
       │
       ▼
  Réponse avec sources citées
```

---

## Stack technique

| Couche | Technologie |
|--------|-------------|
| Interface | Streamlit |
| API | FastAPI |
| LLM | Azure OpenAI (GPT) |
| Embeddings | Azure OpenAI (text-embedding) |
| Base vectorielle | ChromaDB (persistant) |
| NLP | spaCy (fr + en) |
| Parsing RSS | feedparser |
| Conteneurisation | Docker + Docker Compose |
| Reverse proxy | Nginx |
| Supervision processus | Supervisor |
