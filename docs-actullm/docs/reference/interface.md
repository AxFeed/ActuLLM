# Interface Streamlit

**Fichier :** `app.py`

L'interface web est construite avec **Streamlit** et accessible par défaut sur le port `8501`.

---

## Structure de l'interface

### La sidebar (panneau gauche)

La sidebar contient les outils d'administration :

- **Compteur d'articles indexés** — affiche en temps réel le nombre d'articles dans ChromaDB (via `GET /health`)
- **Modèle actif** — nom du déploiement Azure OpenAI configuré
- **Bouton "Mettre à jour les articles"** — déclenche `POST /ingest` et recharge la page

!!! warning "API non disponible"
    Si l'API FastAPI ne répond pas, un avertissement s'affiche à la place du compteur. Vérifiez que le service API est bien démarré.

### Le chat principal

La zone centrale est un **chat conversationnel** :

1. L'historique des messages est affiché dans l'ordre chronologique
2. L'utilisateur saisit sa question dans le champ en bas
3. La réponse s'affiche en **deux colonnes** :

| Colonne gauche ✅ | Colonne droite ❌ |
|-------------------|------------------|
| Réponse avec RAG | Réponse sans RAG |
| Basée sur les articles indexés | Basée sur la mémoire du LLM |
| Précise et sourcée | Peut être obsolète |

---

## Gestion de l'historique

L'historique de la conversation est stocké dans `st.session_state.messages` :

```python
# Structure d'un message
{
    "role": "user",      # ou "assistant"
    "content": "..."
}
```

À chaque nouvelle question, l'historique complet est envoyé à l'API pour maintenir le **contexte de la conversation**.

!!! note "Session Streamlit"
    L'historique est conservé tant que la page reste ouverte. Il est réinitialisé au rechargement de la page.

---

## Variable d'environnement

L'interface a besoin d'une seule variable :

| Variable | Description |
|----------|-------------|
| `API_URL` | URL de l'API FastAPI (ex: `http://localhost:8000` ou `http://api:8000` en Docker) |
