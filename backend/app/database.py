"""Connexion à SQLite, sessions SQLAlchemy et dépendance FastAPI."""

from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app import config

# check_same_thread=False : FastAPI peut traiter une requête dans un autre thread
# que celui qui a ouvert la connexion. Chaque requête garde sa propre session.
engine = create_engine(config.DATABASE_URL, connect_args={"check_same_thread": False})


@event.listens_for(engine, "connect")
def _enable_foreign_keys(dbapi_connection, _connection_record) -> None:
    # SQLite n'applique les clés étrangères que si on le demande explicitement.
    dbapi_connection.execute("PRAGMA foreign_keys=ON")


SessionLocal = sessionmaker(bind=engine, autoflush=False)


class Base(DeclarativeBase):
    """Classe parente de tous les modèles SQLAlchemy."""


def init_db() -> None:
    """Crée les tables manquantes (sans toucher aux tables existantes)."""
    from app import models  # noqa: F401  (enregistre les modèles dans Base.metadata)

    Base.metadata.create_all(bind=engine)


def get_db() -> Iterator[Session]:
    """Ouvre une session pour la durée d'une requête, puis la ferme."""
    with SessionLocal() as session:
        yield session


# Raccourci pour les routes : `db: DbSession` injecte une session.
DbSession = Annotated[Session, Depends(get_db)]
