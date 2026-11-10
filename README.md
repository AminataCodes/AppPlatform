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

### Lancer les tests

```bash
.venv\Scripts\python -m pytest
```

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
│   │   ├── config.py      # configuration (nom, version, préfixe /api)
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
