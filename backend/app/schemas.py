"""Schémas Pydantic : la forme du JSON renvoyé par l'API.

Ils sont distincts des modèles SQLAlchemy : on choisit explicitement
ce qui sort de l'API, indépendamment de la structure des tables.
"""

from pydantic import BaseModel, ConfigDict

from app.models import EnvironmentName


class EnvironmentRead(BaseModel):
    # from_attributes : permet de construire le schéma à partir d'un objet SQLAlchemy.
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: EnvironmentName
    deployed_version: str


class ApplicationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str
    owner_team: str
    environments: list[EnvironmentRead]
    available_versions: list[str]
