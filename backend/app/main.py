"""Point d'entrée de l'API FastAPI.

Lancement (depuis le dossier backend/) :
    uvicorn app.main:app --reload
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import config
from app.api import applications, deployments, executions, health
from app.database import SessionLocal, init_db
from app.seed import seed_database


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    # Exécuté une fois au démarrage : crée les tables puis ajoute les données manquantes.
    init_db()
    with SessionLocal() as session:
        seed_database(session)
    yield


app = FastAPI(title=config.APP_NAME, version=config.APP_VERSION, lifespan=lifespan)

app.include_router(health.router, prefix=config.API_PREFIX)
app.include_router(applications.router, prefix=config.API_PREFIX)
app.include_router(deployments.router, prefix=config.API_PREFIX)
app.include_router(executions.router, prefix=config.API_PREFIX)
