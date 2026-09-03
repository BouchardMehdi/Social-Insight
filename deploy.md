# Deploiement VPS - Social Insight

Ce guide decrit le deploiement de Social Insight sur ton VPS Linux avec Docker, Nginx, Certbot et un sous-domaine Hostinger.

## Architecture de production

```text
Navigateur
  |
  v
https://social-insight.bouchard-mehdi.fr
  |
  v
Nginx VPS
  |-- /      -> frontend Docker, 127.0.0.1:8090
  |-- /api/  -> backend Docker, 127.0.0.1:3010
                 |
                 v
              Google BigQuery
```

Le VPS heberge uniquement l'application. Les donnees metier sont stockees dans BigQuery.

## 1. DNS Hostinger

Creer un sous-domaine, par exemple :

```text
Type: A
Name: social-insight
Points to: 185.98.138.157
TTL: 14400
```

Attendre la propagation DNS, puis verifier :

```bash
ping social-insight.bouchard-mehdi.fr
```

## 2. Cloner le projet

```bash
cd /home/projects
git clone <url-du-repo> social-insight
cd social-insight
```

## 3. Creer le fichier .env

```bash
cp .env.example .env
nano .env
```

Exemple de valeurs de production :

```env
SOCIAL_INSIGHT_ENVIRONMENT=production
SOCIAL_INSIGHT_STORAGE_BACKEND=bigquery
SOCIAL_INSIGHT_SEED_ON_STARTUP=false
SOCIAL_INSIGHT_ANALYSIS_WORKERS=2
SOCIAL_INSIGHT_ANALYSIS_RECOVERY_LIMIT=1000
SOCIAL_INSIGHT_GOOGLE_CLOUD_PROJECT=social-insight-499111
SOCIAL_INSIGHT_BIGQUERY_DATASET=social_insight
SOCIAL_INSIGHT_BIGQUERY_POSTS_TABLE=posts
SOCIAL_INSIGHT_BIGQUERY_USERS_TABLE=users
SOCIAL_INSIGHT_BIGQUERY_WORKSPACES_TABLE=workspaces
SOCIAL_INSIGHT_BIGQUERY_MEMBERSHIPS_TABLE=workspace_memberships
SOCIAL_INSIGHT_BIGQUERY_LOCATION=EU
SOCIAL_INSIGHT_CORS_ORIGINS=["https://social-insight.bouchard-mehdi.fr"]
SOCIAL_INSIGHT_AUTH_SECRET_KEY=replace-with-a-random-secret-of-at-least-32-characters
SOCIAL_INSIGHT_AUTH_TOKEN_EXPIRE_MINUTES=720

GOOGLE_SERVICE_ACCOUNT_KEY_FILE=social-insight-499111-31925cd65113.json
GOOGLE_APPLICATION_CREDENTIALS=/secrets/social-insight-gcp-key.json

VITE_API_BASE_URL=/api
FRONTEND_PORT=8090
BACKEND_PORT=3010
```

Generer une valeur aleatoire pour `SOCIAL_INSIGHT_AUTH_SECRET_KEY`, par exemple :

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(48))"
```

Ne jamais utiliser la valeur de demonstration en production.

## 4. Ajouter la cle Google Cloud

Creer le dossier local non versionne :

```bash
mkdir -p secrets
```

Placer la cle JSON dans :

```text
secrets/social-insight-499111-31925cd65113.json
```

Le fichier `.gitignore` ignore `secrets/`. Ne jamais committer cette cle.

Verifier que le nom correspond a la variable :

```env
GOOGLE_SERVICE_ACCOUNT_KEY_FILE=social-insight-499111-31925cd65113.json
```

Dans le conteneur backend, cette cle sera montee en lecture seule sous :

```text
/secrets/social-insight-gcp-key.json
```

## 5. Lancer Docker

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

Verifier :

```bash
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs --tail=100
```

Tester les ports locaux :

```bash
curl -I http://127.0.0.1:8090
curl -I http://127.0.0.1:3010/api/health
```

## 6. Initialiser BigQuery avec le seed

Lancer le seed apres avoir verifie que l'API demarre correctement :

```bash
docker compose -f docker-compose.prod.yml exec backend \
  python -m app.scripts.seed_bigquery --count 1000 --replace --workspace-id <workspace-id>
```

`--replace` remplace le contenu de la table `posts`. C'est pratique avec BigQuery Sandbox si les donnees expirent ou si tu veux repartir sur un dashboard propre.

## 7. Configurer Nginx sur le VPS

Creer le fichier :

```bash
sudo nano /etc/nginx/sites-available/social-insight
```

Contenu :

```nginx
server {
    listen 80;
    server_name social-insight.bouchard-mehdi.fr;

    location /api/ {
        proxy_pass http://127.0.0.1:3010/api/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }

    location / {
        proxy_pass http://127.0.0.1:8090;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }
}
```

Activer le site :

```bash
sudo ln -s /etc/nginx/sites-available/social-insight /etc/nginx/sites-enabled/social-insight
sudo nginx -t
sudo systemctl reload nginx
```

## 8. Activer HTTPS avec Certbot

```bash
sudo certbot --nginx -d social-insight.bouchard-mehdi.fr
```

Choisir la redirection HTTP vers HTTPS.

Tester :

```bash
curl -I https://social-insight.bouchard-mehdi.fr
curl -I https://social-insight.bouchard-mehdi.fr/api/health
```

## 9. Mise a jour du projet

```bash
cd /home/projects/social-insight
git pull
docker compose -f docker-compose.prod.yml up -d --build
docker compose -f docker-compose.prod.yml logs --tail=50
```

Eviter `docker compose down` sauf changement majeur de ports, reseaux ou volumes.

## 10. Commandes utiles

Voir les conteneurs :

```bash
docker compose -f docker-compose.prod.yml ps
```

Voir les logs backend :

```bash
docker compose -f docker-compose.prod.yml logs -f backend
```

Voir les logs frontend :

```bash
docker compose -f docker-compose.prod.yml logs -f frontend
```

Relancer uniquement le backend :

```bash
docker compose -f docker-compose.prod.yml up -d --build backend
```

Reseeder BigQuery :

```bash
docker compose -f docker-compose.prod.yml exec backend \
  python -m app.scripts.seed_bigquery --count 1000 --replace --workspace-id <workspace-id>
```
