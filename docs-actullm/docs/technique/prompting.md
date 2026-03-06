# prompting.py — Référence technique

**Rôle :** Centralise la construction des messages envoyés au LLM (system prompts et messages utilisateur).

**Importe :** rien (module autonome)

**Importé par :** `api.py`

---

## Variables globales

### `EASTER_EGG_BLOCK`

```python
EASTER_EGG_BLOCK: str
```

Bloc de texte ajouté à la fin des deux system prompts. Il demande au LLM d'insérer discrètement une référence humoristique à des personnages fictifs d'une formation dans chaque réponse.

Chaque personnage est associé à un thème (Windows → Maxime, IA → Inès, etc.).

!!! note "Ceci est volontaire"
    Ce bloc est un easter egg pédagogique. Il illustre comment un system prompt peut influencer subtilement le ton du LLM sans que l'utilisateur final ne s'en rende compte.

---

### `SYSTEM_WITH_RAG`

```python
SYSTEM_WITH_RAG: str
```

System prompt utilisé quand des articles sont fournis en contexte.

**Contenu :** Demande au LLM de se comporter comme "Kévin", un assistant d'actualités qui :

- Utilise les articles fournis pour répondre
- Synthétise l'évolution chronologique si plusieurs articles couvrent le même sujet
- Cite toujours ses sources (nom du media + URL)
- Répond dans la langue de la question
- Applique le bloc easter egg

---

### `SYSTEM_WITHOUT_RAG`

```python
SYSTEM_WITHOUT_RAG: str
```

System prompt utilisé quand **aucun article** n'est fourni (mode plain).

**Contenu :** Version simplifiée — "Kévin" répond avec sa seule mémoire d'entraînement et doit être honnête sur ses incertitudes.

---

### `_USER_TEMPLATE`

```python
_USER_TEMPLATE: str
```

Template de message utilisateur pour le mode RAG. Contient deux placeholders :

- `{articles}` — remplacé par la liste formatée des articles
- `{question}` — remplacée par la question de l'utilisateur

---

## Fonctions

### `build_rag_message(question, articles)`

```python
def build_rag_message(question: str, articles: list[dict]) -> str
```

Construit le message utilisateur complet pour le mode RAG.

| Paramètre | Type | Description |
|-----------|------|-------------|
| `question` | `str` | Question posée par l'utilisateur |
| `articles` | `list[dict]` | Articles retournés par `database.search()` |

**Format de chaque article injecté :**

```
[Article N] YYYY-MM-DD — Nom de la source
Title: Titre de l'article
Summary: Résumé...
URL: https://...
```

Si `articles` est vide, la section est remplacée par `"No articles available."`.

**Retourne :** `str` — message complet prêt à être envoyé au LLM.

**Appelée par :** `api.ask_with_rag()`

---

### `build_plain_message(question)`

```python
def build_plain_message(question: str) -> str
```

Retourne la question telle quelle, sans enrichissement.

| Paramètre | Type | Description |
|-----------|------|-------------|
| `question` | `str` | Question posée par l'utilisateur |

**Retourne :** `str` — identique à `question`.

**Appelée par :** `api.ask_without_rag()`
