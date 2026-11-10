"""Règles métier d'une demande de déploiement.

Ce module ne connaît pas HTTP : il lève des exceptions métier, et c'est la
route qui choisit le code HTTP correspondant. Les règles sont vérifiées dans
l'ordre A → F ; la première règle non respectée arrête la demande.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Application, Environment, EnvironmentName, Execution, ExecutionStatus
from app.schemas import DeploymentRequest

# Statuts d'une exécution qui n'est pas encore terminée.
ACTIVE_STATUSES = (ExecutionStatus.QUEUED, ExecutionStatus.RUNNING)


class NotFoundError(Exception):
    """L'application ou l'environnement demandé n'existe pas."""


class DeploymentRejectedError(Exception):
    """La demande est bien formée mais ne respecte pas une règle métier."""


class DeploymentConflictError(Exception):
    """Un déploiement est déjà en cours sur l'environnement cible."""


def request_deployment(db: Session, request: DeploymentRequest) -> Execution:
    """Valide la demande puis crée une exécution au statut QUEUED."""
    # Règle A : l'application existe.
    application = db.get(Application, request.application_id)
    if application is None:
        raise NotFoundError(f"Application {request.application_id} introuvable.")

    # Règle B : l'environnement existe.
    environment = db.get(Environment, request.environment_id)
    if environment is None:
        raise NotFoundError(f"Environnement {request.environment_id} introuvable.")

    # Règle C : l'environnement appartient à l'application.
    if environment.application_id != application.id:
        raise DeploymentRejectedError(
            f"L'environnement {environment.id} n'appartient pas à l'application {application.name}."
        )

    # Règle D : la version fait partie des versions disponibles.
    if request.requested_version not in application.available_versions:
        raise DeploymentRejectedError(
            f"La version {request.requested_version} n'est pas disponible pour {application.name}."
        )

    # Règle E : confirmation explicite obligatoire pour la production.
    if environment.name == EnvironmentName.PROD and not request.confirm_production:
        raise DeploymentRejectedError("Un déploiement en PROD doit être explicitement confirmé.")

    # Règle F : pas de deuxième déploiement en cours sur le même environnement.
    active_execution_id = db.scalar(
        select(Execution.id)
        .where(Execution.environment_id == environment.id, Execution.status.in_(ACTIVE_STATUSES))
        .limit(1)
    )
    if active_execution_id is not None:
        raise DeploymentConflictError(
            f"Un déploiement est déjà en cours sur {application.name} {environment.name} "
            f"(exécution {active_execution_id})."
        )

    # Statut (QUEUED) et date de création sont fixés par les valeurs par défaut du modèle.
    execution = Execution(
        application=application,
        environment=environment,
        requested_version=request.requested_version,
    )
    db.add(execution)
    db.commit()
    return execution
