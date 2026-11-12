# AppPlatform

Portail interne de self-service (projet pédagogique) : catalogue d'applications,
environnements DEV / STAGING / PROD, demandes de déploiement **simulées**, logs et historique.

Aucun déploiement réel n'est effectué. Les spécifications sont dans [`docs/`](docs/).

## Architecture

```text
Angular (frontend/)  ──HTTP/JSON──▶  FastAPI (backend/)  ──▶  SQLite
```

Monolithe simple : le backend contient l'API, les règles métier et la simulation.

## Prérequis

| Outil | Version utilisée |
|---|---|
| Python | 3.13 |
| Node.js | 24.14 |
| npm | 11 |

Angular CLI n'a pas besoin d'être installé globalement : il est fourni par `frontend/node_modules`
et s'utilise via `npm run …` ou `npx ng …`.

## Backend (FastAPI)

Toutes les commandes se lancent depuis le dossier `backend/`.

### Première installation

```bash
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
```

### Lancer l'API

```bash
.venv\Scripts\python -m uvicorn app.main:app --reload
```

- API : <http://localhost:8000/api/health> → `{"status": "ok"}`
- Documentation automatique (Swagger) : <http://localhost:8000/docs>

`--reload` redémarre automatiquement le serveur à chaque modification du code.

Endpoints disponibles :

| Méthode | URL | Rôle |
|---|---|---|
| GET | `/api/health` | Vérifier que l'API répond |
| GET | `/api/applications` | Lister les applications, leurs environnements et versions disponibles |
| GET | `/api/applications/{id}` | Détail d'une application (404 si elle n'existe pas) |
| POST | `/api/deployments` | Demander un déploiement : vérifie les règles métier, crée une exécution `QUEUED` et lance la simulation en arrière-plan (202, ou 404 / 409 / 422) |
| GET | `/api/executions` | Historique des exécutions, de la plus récente à la plus ancienne |
| GET | `/api/executions/{id}` | Détail d'une exécution avec ses logs (404 si elle n'existe pas) |

### Déploiements simulés

Aucun déploiement n'est réellement effectué. Après une demande acceptée, une tâche d'arrière-plan
fait passer l'exécution de `QUEUED` à `RUNNING`, écrit un log à chaque étape (environ 5 secondes au
total), puis la termine en `SUCCEEDED` ou `FAILED`. La version déployée de l'environnement n'est mise
à jour qu'en cas de succès.

Pour la démonstration, le résultat est déterministe :

- `customer-api` en version `1.4.0` échoue toujours (règle de simulation uniquement) ;
- toute autre demande valide réussit.

La durée de chaque étape peut être changée avec la variable d'environnement
`APPPLATFORM_SIMULATION_STEP_DELAY_SECONDS` (1 seconde par défaut).

### Base de données

- Fichier SQLite : `backend/appplatform.db` (ignoré par Git).
- Au démarrage, l'API crée les tables manquantes puis ajoute les applications de démonstration
  absentes (`app/seed.py`). Les données existantes ne sont jamais écrasées.
- Pour repartir des données initiales : arrêter l'API, supprimer `appplatform.db`, relancer.

### Lancer les tests

```bash
.venv\Scripts\python -m pytest
```

Les tests utilisent une base SQLite temporaire, créée puis supprimée automatiquement :
ils ne touchent jamais `appplatform.db`.

> Astuce : après `.venv\Scripts\activate`, on peut écrire simplement `uvicorn …` et `pytest`.

## Frontend (Angular)

Toutes les commandes se lancent depuis le dossier `frontend/`.

### Première installation

```bash
npm install
```

### Lancer l'application

```bash
npm start
```

Ouvrir <http://localhost:4200>.

En développement, `proxy.conf.json` redirige toutes les requêtes `/api/...` vers
`http://localhost:8000`. Le frontend appelle donc `/api/...` sans connaître l'adresse du backend,
et il n'y a pas de configuration CORS à gérer. **Le backend doit être lancé** pour que les appels
API fonctionnent.

### Autres commandes

```bash
npm test            # tests unitaires (Vitest)
npm run build       # build de production dans dist/
```

## Structure

```text
AppPlatform/
├── docs/                  # spécifications fonctionnelles et techniques
├── backend/
│   ├── requirements.txt   # dépendances Python
│   ├── app/
│   │   ├── main.py        # point d'entrée FastAPI
│   │   ├── config.py      # configuration (nom, version, préfixe /api, base SQLite)
│   │   ├── database.py    # connexion SQLite, sessions, dépendance get_db
│   │   ├── models.py      # tables SQLAlchemy
│   │   ├── schemas.py     # forme du JSON renvoyé (Pydantic)
│   │   ├── seed.py        # données de démonstration
│   │   ├── api/           # routes HTTP
│   │   └── services/      # logique métier et simulation (phase 3)
│   └── tests/             # tests pytest
└── frontend/
    ├── proxy.conf.json    # redirection /api → backend en développement
    └── src/
        ├── styles.scss    # styles globaux
        ├── styles/        # design tokens (couleurs, espacements, typographie)
        └── app/
            ├── core/      # éléments uniques : layout, services API (phase 3)
            ├── shared/    # composants d'interface réutilisables
            └── features/  # une page par route
```
