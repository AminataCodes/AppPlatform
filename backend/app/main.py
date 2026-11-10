"""Point d'entrée de l'API FastAPI.

Lancement (depuis le dossier backend/) :
    uvicorn app.main:app --reload
"""

from fastapi import FastAPI

from app import config
from app.api import health

app = FastAPI(title=config.APP_NAME, version=config.APP_VERSION)

app.include_router(health.router, prefix=config.API_PREFIX)
