# Installation

## Prérequis

Avant de commencer, assurez-vous d'avoir :

- **Python 3.11+** installé
- **Docker** et **Docker Compose** (recommandé pour la production)
- Un compte **Azure OpenAI** avec deux déploiements :
    - Un modèle de chat (ex. `gpt-4o`)
    - Un modèle d'embeddings (ex. `text-embedding-ada-002`)

---

## Installation locale (sans Docker)

### 1. Cloner le projet

```bash
git clone <url-du-repo>
cd actullm
```

### 2. Créer un environnement virtuel

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Télécharger les modèles spaCy

Le projet utilise spaCy pour la lemmatisation des articles (français et anglais) :

```bash
python -m spacy download fr_core_news_sm
python -m spacy download en_core_web_sm
```

!!! info "Pourquoi spaCy ?"
    Avant de stocker un article, le texte est **lemmatisé** : on réduit chaque mot à sa forme de base (ex. "courait" → "courir"). Cela améliore la qualité des recherches sémantiques.

### 5. Configurer les variables d'environnement

Copiez le fichier `.env` et remplissez vos clés :

```bash
cp .env.example .env
```

→ Voir la page [Configuration](configuration.md) pour le détail de chaque variable.

---

## Installation avec Docker (recommandé)

```bash
# Configurer l'environnement
cp .env.example .env
# Éditer .env avec vos clés

# Lancer les services
docker compose up --build
```

Les deux services démarrent automatiquement :

- **API** disponible sur `http://localhost:8000`
- **Interface** disponible sur `http://localhost:8501`
