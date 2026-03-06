# Ingestion RSS

**Fichier :** `RSS.py`

Ce module est responsable de récupérer les articles depuis les flux RSS configurés, de les nettoyer, et de les stocker dans ChromaDB.

---

## La fonction principale : `ingest()`

```python
ingest(reset: bool = False) -> bool
```

Lance le pipeline complet d'ingestion.

- Si `reset=True` : supprime tous les articles existants avant d'ingérer
- Si `reset=False` (défaut) : ajoute ou met à jour les articles (upsert)

**Retourne** `True` si l'ingestion s'est bien passée, `False` en cas d'erreur sur un flux.

---

## Le pipeline étape par étape

### Étape 1 — Parsing du flux RSS

```python
feedparser.parse(feed_config["url"])
```

`feedparser` lit le XML du flux RSS et extrait les entrées (titre, résumé, lien, date...).

### Étape 2 — Nettoyage HTML

```python
def clean_html(text: str) -> str:
    return BeautifulSoup(text, "html.parser").get_text(separator=" ").strip()
```

Les résumés RSS contiennent souvent des balises HTML (`<p>`, `<b>`, etc.). Cette fonction les supprime pour ne garder que le texte brut.

### Étape 3 — Lemmatisation

```python
def lemmatize(text: str, language: str = "fr") -> str:
    nlp = get_nlp(language)
    doc = nlp(text)
    return " ".join([token.lemma_ for token in doc if not token.is_stop and not token.is_punct])
```

Le texte est transformé en **tokens lemmatisés** : chaque mot est réduit à sa forme de base, les mots vides (stopwords) et la ponctuation sont supprimés.

!!! example "Exemple de lemmatisation"
    Texte original : `"Les négociations se sont intensifiées hier"`
    
    Après lemmatisation : `"négociation intensifier hier"`
    
    Cela améliore la précision des recherches sémantiques.

### Étape 4 — Génération d'un identifiant unique

```python
def make_id(url: str) -> str:
    return hashlib.md5(url.encode()).hexdigest()
```

Chaque article est identifié par le **hash MD5 de son URL**. Cela permet de mettre à jour un article déjà indexé sans créer de doublon.

### Étape 5 — Déduplication

```python
def deduplicate(articles: list[dict]) -> list[dict]
```

Si plusieurs flux RSS pointent vers le même article (même URL), un seul exemplaire est conservé.

### Étape 6 — Upsert dans ChromaDB

Les articles dédupliqués sont envoyés à `database.upsert_articles()` qui génère les embeddings et les stocke.

---

## Structure d'un article

Chaque article est stocké avec les champs suivants :

| Champ | Description |
|-------|-------------|
| `id` | Hash MD5 de l'URL |
| `text` | Texte lemmatisé (utilisé pour l'embedding) |
| `metadata.title` | Titre original |
| `metadata.summary` | Résumé (max 500 caractères) |
| `metadata.url` | URL de l'article |
| `metadata.source` | Nom du flux source |
| `metadata.language` | `fr` ou `en` |
| `metadata.published_at` | Date de publication (ISO 8601) |
