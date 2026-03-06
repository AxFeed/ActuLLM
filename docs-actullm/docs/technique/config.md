# config.py — Référence technique

**Rôle :** Centralise la configuration statique du projet, en particulier la liste des flux RSS.

**Importé par :** `RSS.py`

---

## Variables globales

### `RSS_FEEDS`

```python
RSS_FEEDS: list[dict]
```

Liste de dictionnaires décrivant chaque flux RSS à ingérer.

**Structure d'un élément :**

| Clé | Type | Obligatoire | Description |
|-----|------|-------------|-------------|
| `name` | `str` | ✅ | Nom affiché dans les réponses du LLM et les logs |
| `url` | `str` | ✅ | URL du flux RSS (format Atom ou RSS 2.0) |
| `language` | `str` | ✅ | Code langue : `"fr"` ou `"en"` |

**Valeur par défaut :**

```python
RSS_FEEDS = [
    {"name": "France24 FR", "url": "https://www.france24.com/fr/rss",    "language": "fr"},
    {"name": "LeMonde",     "url": "https://www.lemonde.fr/rss/une.xml", "language": "fr"},
    {"name": "HackerNews",  "url": "https://hnrss.org/frontpage",        "language": "en"},
]
```

---

## Notes

- Il n'y a pas de validation au démarrage : si une URL est invalide, `feedparser` échouera silencieusement lors de l'ingestion et l'erreur sera loguée par `RSS.py`.
- La valeur de `language` détermine le modèle **spaCy** utilisé pour la lemmatisation (`fr_core_news_sm` ou `en_core_web_sm`). Toute valeur autre que `"en"` utilisera le modèle français.
