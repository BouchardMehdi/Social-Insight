# Social Insight Platform

Plateforme SaaS d'analyse de publications sociales avec ingestion texte, NLP, API FastAPI, stockage BigQuery et dashboard Vue 3.

## Architecture

```text
Frontend Vue 3 + TypeScript
        |
        v
API FastAPI + services Python
        |
        v
Google BigQuery
```

Le backend est découpé en routes, services, repositories, schémas et configuration. Les routes ne contiennent pas de logique métier : elles délèguent aux services, qui utilisent un repository abstrait. Le repository BigQuery est la couche officielle de persistance.

## Stack

- Backend : Python 3.12, FastAPI, Pydantic v2, Uvicorn, spaCy, google-cloud-bigquery, Poetry, Pytest
- Frontend : Vue 3, TypeScript, Vite, Pinia, Vue Router, Axios, Chart.js
- Infrastructure : Docker, Docker Compose, Git

## BigQuery

Au démarrage, le backend crée automatiquement :

- Dataset : `social_insight`
- Table : `posts`

Schéma de la table :

| Colonne | Type |
| --- | --- |
| `id` | STRING |
| `platform` | STRING |
| `author` | STRING |
| `content` | STRING |
| `language` | STRING |
| `sentiment` | STRING |
| `keywords` | ARRAY<STRING> |
| `created_at` | TIMESTAMP |
| `inserted_at` | TIMESTAMP |

Les endpoints analytics utilisent des requêtes SQL BigQuery directement dans `backend/app/repositories/bigquery.py`.

## Lancement avec Docker

```bash
docker compose up --build
```

Par défaut, Docker Compose utilise `SOCIAL_INSIGHT_STORAGE_BACKEND=memory` pour permettre une démo locale sans compte Google Cloud. Pour utiliser BigQuery, remplacez cette variable par `bigquery`, ajoutez `SOCIAL_INSIGHT_GOOGLE_CLOUD_PROJECT`, puis montez vos credentials Google via `GOOGLE_APPLICATION_CREDENTIALS`.

URLs locales :

- Frontend : http://localhost:5173
- API : http://localhost:8000/api
- Swagger : http://localhost:8000/docs
- ReDoc : http://localhost:8000/redoc

## Lancement backend local

```bash
cd backend
poetry install
poetry run uvicorn app.main:app --reload
```

Variables principales :

```bash
SOCIAL_INSIGHT_STORAGE_BACKEND=bigquery
SOCIAL_INSIGHT_GOOGLE_CLOUD_PROJECT=your-gcp-project-id
SOCIAL_INSIGHT_BIGQUERY_DATASET=social_insight
SOCIAL_INSIGHT_BIGQUERY_POSTS_TABLE=posts
SOCIAL_INSIGHT_BIGQUERY_LOCATION=EU
```

## Lancement frontend local

```bash
cd frontend
npm install
npm run dev
```

Configurez l'URL API avec :

```bash
VITE_API_BASE_URL=http://localhost:8000/api
```

## Endpoints API

Healthcheck :

```bash
curl http://localhost:8000/api/health
```

Analyse NLP :

```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d "{\"text\":\"L'intelligence artificielle transforme les entreprises.\"}"
```

Création d'un post :

```bash
curl -X POST http://localhost:8000/api/posts \
  -H "Content-Type: application/json" \
  -d "{\"platform\":\"twitter\",\"author\":\"mehdi\",\"content\":\"L'intelligence artificielle transforme les entreprises.\"}"
```

Liste paginée :

```bash
curl "http://localhost:8000/api/posts?platform=twitter&limit=10&offset=0"
```

Analytics :

```bash
curl http://localhost:8000/api/stats/top-keywords
curl http://localhost:8000/api/stats/sentiments
curl http://localhost:8000/api/stats/activity
curl http://localhost:8000/api/stats/summary
```

## NLP

Le service `SpacyNLPAnalyzer` fournit une première implémentation :

- détection de langue simple ;
- extraction de mots-clés à partir de tokens spaCy ;
- sentiment `positive`, `neutral` ou `negative` via lexiques.

L'interface `NLPAnalyzer` permet de remplacer cette implémentation par un modèle HuggingFace, un LLM ou une API ML sans modifier les routes.

## Tests

```bash
cd backend
poetry run pytest
```

Les tests utilisent le repository mémoire pour éviter de dépendre d'un compte Google Cloud.

## Préparation Cloud Run

L'API FastAPI est prête pour un futur déploiement sur Cloud Run :

- le backend est stateless ;
- les données métier sont externalisées dans BigQuery ;
- l'image Docker expose Uvicorn sur le port `8000` ;
- Cloud Run peut injecter les variables d'environnement nécessaires ;
- un Service Account Google attaché au service Cloud Run peut recevoir les rôles BigQuery adaptés, par exemple `BigQuery Data Editor` et `BigQuery Job User` ;
- le scaling horizontal est naturel, car plusieurs instances FastAPI peuvent écrire et lire dans BigQuery sans état local partagé.

Le frontend peut ensuite être servi par Cloud Run, Cloud Storage + CDN, Firebase Hosting ou tout autre hébergement statique compatible Vite.
