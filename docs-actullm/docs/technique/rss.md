# RSS.py — Référence technique

**Rôle :** Récupère, nettoie, lemmatise et indexe les articles depuis les flux RSS configurés.

**Importe :** `feedparser`, `spacy`, `BeautifulSoup`, `config.RSS_FEEDS`, `database`

**Importé par :** `api.py` (route `/ingest`)

---

## Variables globales

| Variable | Type | Description |
|----------|------|-------------|
| `nlp_fr` | `spacy.Language` | Modèle spaCy chargé pour le français (`fr_core_news_sm`) |
| `nlp_en` | `spacy.Language` | Modèle spaCy chargé pour l'anglais (`en_core_web_sm`) |

!!! warning "Chargement au démarrage"
    Les deux modèles spaCy sont chargés **à l'import du module**, pas à chaque appel. Cela peut ralentir le démarrage de ~2 secondes mais optimise les ingestions répétées.

---

## Fonctions

### `get_nlp(language)`

```python
def get_nlp(language: str) -> spacy.Language
```

Sélectionne le modèle spaCy approprié selon la langue.

| Paramètre | Type | Description |
|-----------|------|-------------|
| `language` | `str` | Code langue : `"fr"` ou `"en"` |

**Retourne :** `nlp_en` si `language == "en"`, sinon `nlp_fr`.

**Appelée par :** `lemmatize()`

---

### `parse_date(entry)`

```python
def parse_date(entry) -> str
```

Extrait la date de publication d'une entrée RSS et la formate en ISO 8601.

| Paramètre | Type | Description |
|-----------|------|-------------|
| `entry` | `feedparser.FeedParserDict` | Entrée RSS parsée |

**Logique de fallback :**

1. Tente `entry.published_parsed` (champ RSS standard)
2. Si absent, tente `entry.updated_parsed`
3. Si absent, retourne `datetime.now().isoformat()`

**Retourne :** `str` — ex. `"2025-03-05T10:30:00"`

**Appelée par :** `fetch_articles()`

---

### `clean_html(text)`

```python
def clean_html(text: str) -> str
```

Supprime les balises HTML d'un texte et normalise les espaces.

| Paramètre | Type | Description |
|-----------|------|-------------|
| `text` | `str` | Texte brut pouvant contenir du HTML |

**Retourne :** `str` — texte sans balises HTML, espaces nettoyés.

**Appelée par :** `fetch_articles()`

---

### `lemmatize(text, language)`

```python
def lemmatize(text: str, language: str = "fr") -> str
```

Réduit le texte à ses lemmes en supprimant les stopwords et la ponctuation.

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `text` | `str` | — | Texte nettoyé à lemmatiser |
| `language` | `str` | `"fr"` | Code langue pour choisir le modèle spaCy |

**Retourne :** `str` — tokens lemmatisés séparés par des espaces.

**Exemple :**

```python
lemmatize("Les négociations se sont intensifiées hier", "fr")
# → "négociation intensifier hier"
```

**Appelée par :** `fetch_articles()`

---

### `make_id(url)`

```python
def make_id(url: str) -> str
```

Génère un identifiant unique pour un article à partir de son URL.

| Paramètre | Type | Description |
|-----------|------|-------------|
| `url` | `str` | URL de l'article |

**Retourne :** `str` — hash MD5 hexadécimal (32 caractères).

**Appelée par :** `fetch_articles()`

---

### `deduplicate(articles)`

```python
def deduplicate(articles: list[dict]) -> list[dict]
```

Élimine les doublons d'une liste d'articles en se basant sur l'`id`.

| Paramètre | Type | Description |
|-----------|------|-------------|
| `articles` | `list[dict]` | Liste brute pouvant contenir des doublons |

**Retourne :** `list[dict]` — liste sans doublons, ordre de première apparition préservé.

**Appelée par :** `ingest()`

---

### `fetch_articles(feed_config)`

```python
def fetch_articles(feed_config: dict) -> list[dict]
```

Récupère et prépare tous les articles d'un flux RSS.

| Paramètre | Type | Description |
|-----------|------|-------------|
| `feed_config` | `dict` | Dictionnaire avec `name`, `url`, `language` |

**Pipeline interne :**

```
feedparser.parse(url)
    └── pour chaque entry :
          ├── clean_html(title + summary)
          ├── lemmatize(raw_text, language)
          ├── make_id(url)
          └── parse_date(entry)
```

**Retourne :** `list[dict]` — liste d'articles au format :

```python
{
    "id":       str,           # hash MD5 de l'URL
    "text":     str,           # texte lemmatisé (pour l'embedding)
    "metadata": {
        "title":        str,
        "summary":      str,   # max 500 caractères
        "url":          str,
        "source":       str,   # feed_config["name"]
        "language":     str,
        "published_at": str,   # ISO 8601
    }
}
```

**Appelée par :** `ingest()`

---

### `ingest(reset)`

```python
def ingest(reset: bool = False) -> bool
```

Point d'entrée principal du module. Orchestre l'ingestion complète de tous les flux.

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `reset` | `bool` | `False` | Si `True`, vide la base avant d'ingérer |

**Séquence d'appels :**

```
ingest()
  ├── reset_collection()  [si reset=True]
  │   ou create_collection()  [si reset=False]
  ├── pour chaque feed dans RSS_FEEDS :
  │     └── fetch_articles(feed)
  ├── deduplicate(all_articles)
  └── database.upsert_articles(unique_articles)
```

**Retourne :** `bool` — `True` si tout s'est passé sans erreur, `False` si au moins un flux a échoué.

**Appelée par :** `api.py` (route `POST /ingest`)
