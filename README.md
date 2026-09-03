<p align="center">
  <img src="frontend/public/logo%20social%20insight.png" alt="Social Insight" width="420" />
</p>

# Social Insight Platform

Social Insight Platform est une application SaaS de demonstration qui ingere des publications sociales, analyse leur contenu avec un service NLP, stocke les resultats dans Google BigQuery et expose des tableaux de bord analytiques avec Vue 3.

Le projet a ete concu comme un projet portfolio professionnel pour montrer des competences en Python, FastAPI, Data Engineering, Google Cloud, BigQuery, NLP, Docker et Vue.js.

## Sommaire

- [Objectif du projet](#objectif-du-projet)
- [Fonctionnalites](#fonctionnalites)
- [Stack technique](#stack-technique)
- [Architecture globale](#architecture-globale)
- [Architecture backend](#architecture-backend)
- [Architecture frontend](#architecture-frontend)
- [Fonctionnement end-to-end](#fonctionnement-end-to-end)
- [BigQuery](#bigquery)
- [Modes de stockage](#modes-de-stockage)
- [Seed de donnees](#seed-de-donnees)
- [Installation avec Docker](#installation-avec-docker)
- [Deploiement VPS](#deploiement-vps)
- [Installation locale backend](#installation-locale-backend)
- [Installation locale frontend](#installation-locale-frontend)
- [Variables d'environnement](#variables-denvironnement)
- [Endpoints API](#endpoints-api)
- [Erreurs et logs](#erreurs-et-logs)
- [Tests](#tests)
- [CI GitHub Actions](#ci-github-actions)
- [Utilisation avec BigQuery Sandbox](#utilisation-avec-bigquery-sandbox)
- [Preparation Cloud Run](#preparation-cloud-run)
- [Securite](#securite)
- [Structure du projet](#structure-du-projet)
- [Commandes utiles](#commandes-utiles)

## Objectif du projet

L'objectif est de simuler une plateforme d'analyse de donnees sociales capable de :

- recevoir des publications textuelles issues de plateformes sociales ;
- analyser automatiquement la langue, le sentiment et les mots-cles ;
- persister les donnees analysees dans BigQuery ;
- exposer les donnees via une API REST FastAPI ;
- calculer des statistiques directement avec SQL BigQuery ;
- afficher les resultats dans une interface Vue 3 moderne.

Le projet ne cherche pas a etre un produit commercial complet. Il sert surtout a demontrer une architecture propre et realiste autour d'un cas Data Engineering et Cloud.

## Fonctionnalites

- Ingestion de posts sociaux via API et formulaire frontend.
- Analyse NLP :
  - detection de langue francais/anglais avec confiance ;
  - sentiment `positive`, `neutral`, `negative` avec confiance ;
  - negations et intensificateurs ;
  - normalisation des accents et extraction de mots-cles ;
  - version et statut de l'analyse.
- Stockage cloud dans Google BigQuery.
- Mode local `memory` pour tester sans Google Cloud.
- Authentification par jeton et espaces de travail isoles.
- Roles d'espace `owner`, `admin` et `member`.
- Dashboard analytique :
  - nombre total de posts ;
  - nombre d'auteurs ;
  - top keywords ;
  - repartition des sentiments.
- Page Posts :
  - filtres par plateforme, sentiment et keyword ;
  - pagination ;
  - acces au detail d'un post.
- Page Analytics avec graphiques Chart.js.
- Formulaire de creation de post.
- Seed de donnees local et seed BigQuery controle.
- Logs JSON et `X-Request-ID`.
- Tests Pytest.
- CI GitHub Actions.
- Docker Compose.
- Deploiement VPS documente avec Nginx, Certbot et BigQuery.

## Stack technique

### Backend

- Python 3.12
- FastAPI
- Pydantic v2
- Uvicorn
- spaCy
- google-cloud-bigquery
- Poetry
- Pytest
- Ruff

### Frontend

- Vue 3
- TypeScript
- Vite
- Pinia
- Vue Router
- Axios
- Chart.js
- Lucide icons

### Infrastructure

- Docker
- Docker Compose
- GitHub Actions
- Google Cloud BigQuery

## Architecture globale

```text
Frontend Vue 3
       |
       | HTTP / Axios
       v
API FastAPI
       |
       | Repository abstraction
       v
Google BigQuery
```

Le frontend ne communique jamais directement avec BigQuery. Toutes les lectures et ecritures passent par l'API FastAPI.

## Architecture backend

Le backend est organise par responsabilites :

```text
backend/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   ├── dependencies.py
│   │   └── router.py
│   ├── config/
│   │   └── settings.py
│   ├── core/
│   │   ├── error_handlers.py
│   │   ├── exceptions.py
│   │   └── logging.py
│   ├── repositories/
│   │   ├── base.py
│   │   ├── bigquery.py
│   │   └── memory.py
│   ├── schemas/
│   ├── scripts/
│   ├── services/
│   └── main.py
├── tests/
├── Dockerfile
├── poetry.lock
└── pyproject.toml
```

### Separation des responsabilites

- `api/routes` contient les endpoints HTTP.
- `services` contient la logique metier.
- `repositories` contient l'acces aux donnees.
- `schemas` contient les contrats Pydantic.
- `core` contient la gestion d'erreurs et les logs.
- `config` centralise les variables d'environnement.

Les routes ne contiennent pas de logique metier lourde. Elles valident la requete, appellent les services et retournent les schemas de reponse.

## Architecture frontend

```text
frontend/
├── public/
│   └── logo social insight.png
├── src/
│   ├── api/
│   ├── assets/
│   ├── components/
│   ├── router/
│   ├── stores/
│   ├── types/
│   ├── views/
│   ├── App.vue
│   └── main.ts
├── Dockerfile
├── package-lock.json
├── package.json
└── vite.config.ts
```

Le frontend utilise Pinia pour l'etat applicatif :

- `analytics` pour les statistiques ;
- `posts` pour les publications ;
- `toasts` pour les notifications utilisateur.

## Fonctionnement end-to-end

Exemple : creation d'un post.

1. L'utilisateur soumet un post depuis le frontend.
2. Vue appelle `POST /api/posts`.
3. FastAPI valide le body avec Pydantic.
4. `PostService` appelle le service NLP.
5. Le service NLP retourne :
   - langue ;
   - confiance de langue ;
   - sentiment ;
   - confiance du sentiment ;
   - keywords ;
   - version et statut du modele.
6. `PostService` construit un objet `PostRead`.
7. Le repository persiste le post :
   - en memoire en mode local ;
   - dans BigQuery en mode cloud.
8. Le frontend affiche un toast de succes.
9. Les pages Dashboard et Analytics relisent les stats via l'API.

## BigQuery

BigQuery est le datastore principal du projet.

Au demarrage, le backend cree automatiquement :

- dataset : `social_insight`
- tables : `posts`, `users`, `workspaces` et `workspace_memberships`

Schema :

| Colonne | Type BigQuery | Mode |
| --- | --- | --- |
| `id` | STRING | REQUIRED |
| `workspace_id` | STRING | NULLABLE |
| `platform` | STRING | REQUIRED |
| `author` | STRING | REQUIRED |
| `content` | STRING | REQUIRED |
| `language` | STRING | REQUIRED |
| `language_confidence` | FLOAT | NULLABLE |
| `sentiment` | STRING | REQUIRED |
| `sentiment_confidence` | FLOAT | NULLABLE |
| `keywords` | STRING | REPEATED |
| `model_version` | STRING | NULLABLE |
| `analysis_status` | STRING | NULLABLE |
| `analysis_error` | STRING | NULLABLE |
| `created_at` | TIMESTAMP | REQUIRED |
| `inserted_at` | TIMESTAMP | REQUIRED |

Lors de la premiere mise a jour d'une table existante, la colonne `workspace_id` est
ajoutee automatiquement. Les anciennes lignes sans espace restent masquees ; relancer
le seed avec `--workspace-id` permet de les remplacer par des donnees accessibles.

Les statistiques sont calculees directement avec SQL BigQuery dans `backend/app/repositories/bigquery.py`.

Exemple de requete :

```sql
SELECT
  sentiment,
  COUNT(*) AS count
FROM `social-insight-499111.social_insight.posts`
WHERE workspace_id = @workspace_id
GROUP BY sentiment;
```

## Modes de stockage

Le backend supporte deux modes.

### Mode memory

```env
SOCIAL_INSIGHT_STORAGE_BACKEND=memory
```

Utilise un repository en memoire. Ce mode sert aux tests et a la demo locale sans Google Cloud.

Avantages :

- demarrage rapide ;
- aucun compte cloud necessaire ;
- seed automatique possible.

Limite :

- les donnees disparaissent au redemarrage du conteneur.

### Mode bigquery

```env
SOCIAL_INSIGHT_STORAGE_BACKEND=bigquery
```

Utilise Google BigQuery comme stockage persistant.

Avantages :

- donnees persistantes ;
- statistiques SQL ;
- architecture proche d'un projet cloud reel.

## Seed de donnees

### Seed local memory

Dans `docker-compose.yml`, le mode local active :

```env
SOCIAL_INSIGHT_STORAGE_BACKEND=memory
SOCIAL_INSIGHT_SEED_ON_STARTUP=true
SOCIAL_INSIGHT_SEED_POSTS_COUNT=600
```

Au demarrage, l'API cree un compte de demonstration et remplit son espace si celui-ci est vide.

Identifiants locaux :

```text
demo@social-insight.local
demo-social-insight
```

### Seed controle BigQuery

Pour remplir BigQuery avec 1000 posts de demonstration :

```bash
cd backend
poetry run seed-bigquery --count 1000 --replace --workspace-id <workspace-id>
```

Avec Docker :

```bash
docker compose -f docker-compose.yml -f docker-compose.bigquery.local.yml run --rm backend \
  python -m app.scripts.seed_bigquery --count 1000 --replace --workspace-id <workspace-id>
```

`--replace` remplace le contenu de la table par les donnees generees.

L'identifiant de l'espace est retourne par `GET /api/auth/me` apres connexion.

Sans `--replace`, la commande ajoute les posts a la table existante.

Le seed BigQuery genere une distribution non uniforme :

- plus de posts positifs que neutres ;
- moins de posts negatifs ;
- plateformes avec poids differents ;
- keywords et topics varies.

## Installation avec Docker

### Demo locale sans BigQuery

```bash
docker compose up --build
```

URLs :

- Frontend : http://localhost:5173
- API : http://localhost:8000/api
- Swagger : http://localhost:8000/docs
- ReDoc : http://localhost:8000/redoc

### Mode BigQuery local

Copier le modele :

```bash
cp docker-compose.bigquery.example.yml docker-compose.bigquery.local.yml
```

Adapter :

```yaml
SOCIAL_INSIGHT_GOOGLE_CLOUD_PROJECT: social-insight-499111
GOOGLE_APPLICATION_CREDENTIALS: /secrets/social-insight-gcp-key.json
volumes:
  - C:/Users/bouch/gcp-keys/social-insight-499111-31925cd65113.json:/secrets/social-insight-gcp-key.json:ro
```

Lancer :

```bash
docker compose -f docker-compose.yml -f docker-compose.bigquery.local.yml up -d --build
```

Seeder BigQuery :

```bash
docker compose -f docker-compose.yml -f docker-compose.bigquery.local.yml exec backend \
  python -m app.scripts.seed_bigquery --count 1000 --replace --workspace-id <workspace-id>
```

Sur un VPS, l'ordre recommande est :

1. demarrer la stack ;
2. verifier que l'API repond ;
3. lancer le seed ;
4. ouvrir le frontend.

## Deploiement VPS

Le projet fournit une configuration production dediee :

- `docker-compose.prod.yml` pour lancer le frontend et le backend sur des ports lies a `127.0.0.1` ;
- `frontend/Dockerfile.prod` pour builder Vue et servir les fichiers statiques avec Nginx ;
- `.env.example` pour documenter les variables de production ;
- `deploy.md` pour reproduire le deploiement complet sur le VPS.

Commande principale :

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

Guide complet : [deploy.md](deploy.md).

## Installation locale backend

```bash
cd backend
poetry install
poetry run uvicorn app.main:app --reload
```

Si le backend est lance hors Docker avec BigQuery, verifier `backend/.env`.

## Installation locale frontend

```bash
cd frontend
npm install
npm run dev
```

Variable frontend :

```env
VITE_API_BASE_URL=http://localhost:8000/api
```

## Variables d'environnement

### Backend

| Variable | Description | Exemple |
| --- | --- | --- |
| `SOCIAL_INSIGHT_ENVIRONMENT` | Environnement courant | `local` |
| `SOCIAL_INSIGHT_STORAGE_BACKEND` | Repository utilise | `memory` ou `bigquery` |
| `SOCIAL_INSIGHT_GOOGLE_CLOUD_PROJECT` | ID du projet Google Cloud | `social-insight-499111` |
| `SOCIAL_INSIGHT_BIGQUERY_DATASET` | Dataset BigQuery | `social_insight` |
| `SOCIAL_INSIGHT_BIGQUERY_POSTS_TABLE` | Table BigQuery | `posts` |
| `SOCIAL_INSIGHT_BIGQUERY_USERS_TABLE` | Table des utilisateurs | `users` |
| `SOCIAL_INSIGHT_BIGQUERY_WORKSPACES_TABLE` | Table des espaces | `workspaces` |
| `SOCIAL_INSIGHT_BIGQUERY_MEMBERSHIPS_TABLE` | Table des appartenances | `workspace_memberships` |
| `SOCIAL_INSIGHT_BIGQUERY_LOCATION` | Region BigQuery | `EU` |
| `SOCIAL_INSIGHT_AUTH_SECRET_KEY` | Secret de signature des jetons, 32 caracteres minimum | valeur aleatoire |
| `SOCIAL_INSIGHT_AUTH_TOKEN_EXPIRE_MINUTES` | Duree de vie d'un jeton | `720` |
| `SOCIAL_INSIGHT_SEED_ON_STARTUP` | Seed automatique au demarrage | `true` ou `false` |
| `SOCIAL_INSIGHT_SEED_POSTS_COUNT` | Nombre de posts seedes | `600` |
| `SOCIAL_INSIGHT_LOG_LEVEL` | Niveau de logs | `INFO` |
| `GOOGLE_APPLICATION_CREDENTIALS` | Chemin vers la cle service account | `/secrets/key.json` |

### Frontend

| Variable | Description | Exemple |
| --- | --- | --- |
| `VITE_API_BASE_URL` | URL de l'API FastAPI | `http://localhost:8000/api` |

## Endpoints API

### Healthcheck

```http
GET /api/health
```

Reponse :

```json
{
  "status": "healthy"
}
```

### Analyse NLP

```http
POST /api/analyze
```

Body :

```json
{
  "text": "L'intelligence artificielle transforme les entreprises."
}
```

Reponse :

```json
{
  "language": "fr",
  "language_confidence": 1.0,
  "sentiment": "positive",
  "sentiment_confidence": 0.84,
  "keywords": ["intelligence artificielle", "entreprises"],
  "model_version": "spacy-rules-fr-en-v2",
  "analysis_status": "completed"
}
```

La version v2 reste locale et deterministe : elle utilise la tokenisation spaCy et des
regles explicables, sans appel a une API payante. Elle gere le francais et l'anglais,
les accents, les negations courtes comme `pas bon` et les intensificateurs comme
`tres utile` ou `really great`.

### Authentification

```http
POST /api/auth/register
POST /api/auth/login
GET /api/auth/me
```

L'inscription cree automatiquement un premier espace avec le role `owner`.

### Espaces de travail

```http
GET /api/workspaces
POST /api/workspaces
GET /api/workspaces/{workspace_id}/members
POST /api/workspaces/{workspace_id}/members
```

Un owner ou un admin peut ajouter un utilisateur deja inscrit. Seul l'owner peut
attribuer le role `admin`.

Toutes les routes NLP, posts et statistiques exigent ensuite :

```http
Authorization: Bearer <access-token>
X-Workspace-ID: <workspace-id>
```

### Creation d'un post

```http
POST /api/posts
```

Body :

```json
{
  "platform": "twitter",
  "author": "mehdi",
  "content": "L'intelligence artificielle transforme les entreprises."
}
```

### Liste des posts

```http
GET /api/posts?platform=twitter&sentiment=positive&keyword=ia&limit=10&offset=0
```

Filtres disponibles :

- `platform`
- `sentiment`
- `keyword`
- `limit`
- `offset`

### Detail d'un post

```http
GET /api/posts/{id}
```

### Top keywords

```http
GET /api/stats/top-keywords
```

### Distribution des sentiments

```http
GET /api/stats/sentiments
```

### Activite quotidienne

```http
GET /api/stats/activity
```

### Resume

```http
GET /api/stats/summary
```

## Erreurs et logs

Toutes les erreurs API utilisent un format stable :

```json
{
  "error": {
    "code": "post_not_found",
    "message": "Post not found",
    "request_id": "...",
    "details": {
      "id": "..."
    }
  }
}
```

Chaque reponse inclut :

```http
X-Request-ID: ...
```

Si le client fournit deja un `X-Request-ID`, l'API le propage.

Les logs backend sont structures en JSON :

```json
{
  "timestamp": "2026-06-11T12:11:37.805367+00:00",
  "level": "INFO",
  "logger": "app.main",
  "message": "request_completed",
  "request_id": "...",
  "method": "GET",
  "path": "/api/stats/summary",
  "status_code": 200,
  "duration_ms": 1038.24
}
```

## Tests

Lancer les tests backend :

```bash
cd backend
poetry run pytest
```

Lint backend :

```bash
cd backend
poetry run ruff check app tests
```

Les tests couvrent :

- healthcheck ;
- NLP ;
- creation de posts ;
- filtres ;
- pagination ;
- statistiques ;
- seed local ;
- seed BigQuery ;
- erreurs standardisees.

## CI GitHub Actions

Le workflow `.github/workflows/ci.yml` execute :

- `ruff check app tests` ;
- `pytest` ;
- `npm run build` ;
- `docker compose build`.

La CI se lance sur :

- push vers `main` ;
- pull request vers `main` ;
- lancement manuel `workflow_dispatch`.

## Utilisation avec BigQuery Sandbox

Le projet fonctionne avec BigQuery Sandbox.

Points importants :

- les tables sandbox expirent automatiquement apres environ 60 jours ;
- si les donnees disparaissent, relancer le seed BigQuery ;
- le streaming insert peut etre refuse en sandbox ;
- le projet utilise donc des BigQuery load jobs pour inserer les donnees.

Relancer le seed :

```bash
docker compose -f docker-compose.yml -f docker-compose.bigquery.local.yml exec backend \
  python -m app.scripts.seed_bigquery --count 1000 --replace --workspace-id <workspace-id>
```

## Preparation Cloud Run

Le backend est pret pour un futur deploiement Cloud Run :

- l'API est stateless ;
- les donnees sont dans BigQuery ;
- Docker expose Uvicorn sur le port `8000` ;
- les variables d'environnement peuvent etre injectees par Cloud Run ;
- un service account Cloud Run peut recevoir les roles :
  - `BigQuery Data Editor` ;
  - `BigQuery Job User`.

En production Cloud Run, il vaut mieux eviter les cles JSON et utiliser le service account attache au service Cloud Run.

## Securite

Les mots de passe sont derives avec PBKDF2-HMAC-SHA256, avec un sel unique. L'API ne
retourne jamais le hash. Les jetons sont signes et chaque requete de donnees verifie
l'appartenance de l'utilisateur a l'espace demande.

En production, remplacer obligatoirement `SOCIAL_INSIGHT_AUTH_SECRET_KEY` par une valeur
aleatoire longue et conserver cette valeur hors du depot.

Fichiers sensibles ignores par Git :

- `backend/.env`
- `docker-compose.bigquery.local.yml`
- cles JSON Google Cloud

Ne jamais committer :

- une cle service account ;
- un fichier `.env` reel ;
- un chemin local contenant des secrets.

Le fichier versionnable fourni est :

```text
docker-compose.bigquery.example.yml
```

## Structure du projet

```text
Social-Insight/
├── .github/
│   └── workflows/
│       └── ci.yml
├── backend/
│   ├── app/
│   ├── tests/
│   ├── Dockerfile
│   ├── poetry.lock
│   └── pyproject.toml
├── frontend/
│   ├── public/
│   ├── src/
│   ├── Dockerfile
│   ├── package-lock.json
│   └── package.json
├── docker-compose.yml
├── docker-compose.bigquery.example.yml
└── README.md
```

## Commandes utiles

Demo locale memory :

```bash
docker compose up --build
```

Mode BigQuery :

```bash
docker compose -f docker-compose.yml -f docker-compose.bigquery.local.yml up -d --build
```

Seed BigQuery :

```bash
docker compose -f docker-compose.yml -f docker-compose.bigquery.local.yml exec backend \
  python -m app.scripts.seed_bigquery --count 1000 --replace --workspace-id <workspace-id>
```

Tests backend :

```bash
cd backend
poetry run pytest
```

Build frontend :

```bash
cd frontend
npm run build
```

Build Docker :

```bash
docker compose build
```
