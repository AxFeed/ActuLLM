# app.py — Référence technique

**Rôle :** Interface utilisateur web construite avec Streamlit. Communique exclusivement avec `api.py` via des requêtes HTTP.

**Importe :** `streamlit`, `requests`, `os`, `dotenv`

**Dépendance :** `API_URL` (variable d'environnement)

---

## Variables et état

| Variable | Portée | Description |
|----------|--------|-------------|
| `API_URL` | Module | URL de l'API FastAPI, lue depuis `.env` |
| `st.session_state.messages` | Session Streamlit | Historique de la conversation courante |

### Structure de `session_state.messages`

```python
[
    {"role": "user",      "content": "Question de l'utilisateur"},
    {"role": "assistant", "content": "**Avec RAG:** ...\n\n**Sans RAG:** ..."},
    ...
]
```

!!! warning "Durée de vie"
    `st.session_state` est réinitialisé à chaque rechargement de page (F5). L'historique n'est **pas persisté**.

---

## Composants de l'interface

### Sidebar

Chargée à chaque rendu de la page :

```
GET {API_URL}/health
    ├── succès → affiche st.metric("Articles indexés", count)
    │            et st.caption("Modèle actif : {deployment}")
    └── erreur  → st.warning("API non disponible")
```

**Bouton "Mettre à jour les articles" :**

```
POST {API_URL}/ingest
    ├── succès → st.success() + st.rerun()
    └── erreur  → st.error(detail)
```

---

### Zone de chat

**Affichage de l'historique :**

```python
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
```

**Traitement d'une nouvelle question :**

```
user_input saisi
    │
    ├── ajout à session_state.messages (role: "user")
    │
    ├── [Colonne gauche] POST {API_URL}/ask/rag
    │       body: {"question": user_input, "history": messages[:-1]}
    │       → affiche response["answer"]
    │
    ├── [Colonne droite] POST {API_URL}/ask/plain
    │       body: {"question": user_input, "history": messages[:-1]}
    │       → affiche response["answer"]
    │
    └── ajout à session_state.messages (role: "assistant")
            content: "**Avec RAG:** {rag}\n\n**Sans RAG:** {plain}"
```

!!! note "Historique envoyé à l'API"
    `messages[:-1]` est utilisé : le message de l'utilisateur courant est déjà inclus dans le corps de la requête via `question`. On n'envoie donc que les messages **précédents**.

---

## Gestion des erreurs

Chaque appel HTTP est entouré d'un `try/except`. En cas d'erreur réseau ou de réponse invalide :

- La réponse affichée est `f"Erreur : {e}"`
- Aucune exception n'est propagée vers Streamlit
- L'historique est quand même mis à jour avec le message d'erreur
