"""Schémas Pydantic : la forme du JSON reçu et renvoyé par l'API.

Ils sont distincts des modèles SQLAlchemy : on choisit explicitement
ce qui entre et sort de l'API, indépendamment de la structure des tables.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models import EnvironmentName, ExecutionStatus, LogLevel


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


class DeploymentRequest(BaseModel):
    """Corps de POST /api/deployments.

    extra="forbid" : tout champ non prévu (status, created_at...) est refusé.
    Le statut et les dates sont décidés par le backend, jamais par le client.
    """

    model_config = ConfigDict(extra="forbid")

    application_id: int
    environment_id: int
    requested_version: str = Field(min_length=1, max_length=50)
    confirm_production: bool = False


class ApplicationRef(BaseModel):
    """Référence courte à une application : identifiant + nom pour l'affichage."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class EnvironmentRef(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: EnvironmentName


class ExecutionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    application: ApplicationRef
    environment: EnvironmentRef
    requested_version: str
    status: ExecutionStatus
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None


class ExecutionLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    timestamp: datetime
    level: LogLevel
    message: str


class ExecutionDetail(ExecutionRead):
    """Détail d'une exécution : les champs de la liste, plus ses logs."""

    logs: list[ExecutionLogRead]
