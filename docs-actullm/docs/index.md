# ActuLLM

**ActuLLM** est un assistant d'actualités intelligent qui répond à vos questions sur l'actualité en s'appuyant sur de vrais articles de presse récents — grâce à la technique **RAG** (Retrieval-Augmented Generation).

---

## 🎯 À quoi ça sert ?

Posez une question comme *"Que se passe-t-il en Ukraine ?"* et ActuLLM :

1. **Recherche** les articles de presse les plus pertinents dans sa base de données
2. **Génère** une réponse précise et sourcée à partir de ces articles
3. **Compare** avec une réponse sans RAG (basée uniquement sur la mémoire du modèle)

Cela vous permet de voir concrètement **l'apport du RAG** par rapport à un LLM classique.

---

## 🧱 Les composants

| Composant | Rôle |
|-----------|------|
| **RSS.py** | Récupère et prépare les articles depuis des flux RSS |
| **database.py** | Stocke et interroge les articles dans ChromaDB |
| **api.py** | Expose les fonctionnalités via une API REST (FastAPI) |
| **app.py** | Interface utilisateur web (Streamlit) |
| **prompting.py** | Prépare les messages envoyés au LLM |
| **config.py** | Liste des flux RSS configurés |

---

## ⚡ Démarrage rapide

```bash
# 1. Cloner et configurer
cp .env.example .env
# → Remplir les clés Azure dans .env

# 2. Lancer avec Docker
docker compose up --build

# 3. Ouvrir l'interface
# http://localhost:8501
```

!!! tip "Première utilisation"
    Après le lancement, cliquez sur **"Mettre à jour les articles"** dans la sidebar pour ingérer les actualités du jour.

---

## 🗺️ Navigation

- **[Installation](guide/installation.md)** — Prérequis et mise en place
- **[Configuration](guide/configuration.md)** — Variables d'environnement
- **[Comment ça marche](reference/architecture.md)** — Architecture technique
- **[Déploiement](deploy/docker.md)** — Mise en production
