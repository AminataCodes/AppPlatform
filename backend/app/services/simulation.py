"""Simulation d'un déploiement (démonstration uniquement).

Aucune infrastructure réelle n'est contactée : chaque étape écrit un log puis
attend un court instant. `run_simulation` est exécutée en arrière-plan
(BackgroundTasks), après l'envoi de la réponse 202 au client.
"""

import logging
import time

from sqlalchemy import update
from sqlalchemy.orm import Session

from app import config
from app.database import SessionLocal
from app.models import Execution, ExecutionLog, ExecutionStatus, LogLevel, utc_now

logger = logging.getLogger(__name__)

# Règle de démonstration uniquement, pas une règle métier réelle :
# ce couple (application, version) échoue toujours, pour montrer un échec de façon reproductible.
FAILING_DEMO_DEPLOYMENTS = {("customer-api", "1.4.0")}


def run_simulation(execution_id: int) -> None:
    """Point d'entrée de la tâche d'arrière-plan.

    Elle reçoit un identifiant, pas un objet : la session de la requête HTTP
    est déjà fermée, la tâche ouvre donc sa propre session.
    """
    with SessionLocal() as db:
        if not _claim_execution(db, execution_id):
            return
        try:
            _run_steps(db, execution_id)
        except Exception:
            logger.exception("Simulation de l'exécution %s interrompue par une erreur", execution_id)
            db.rollback()
            _fail_after_unexpected_error(db, execution_id)


def _claim_execution(db: Session, execution_id: int) -> bool:
    """Passe l'exécution de QUEUED à RUNNING, en une seule requête conditionnelle.

    Le UPDATE ne modifie la ligne que si elle est encore QUEUED : une exécution
    déjà prise en charge ou terminée n'est jamais traitée deux fois.
    """
    result = db.execute(
        update(Execution)
        .where(Execution.id == execution_id, Execution.status == ExecutionStatus.QUEUED)
        .values(status=ExecutionStatus.RUNNING, started_at=utc_now())
    )
    db.commit()
    return result.rowcount == 1


def _run_steps(db: Session, execution_id: int) -> None:
    execution = db.get(Execution, execution_id)
    application_name = execution.application.name
    environment = execution.environment
    environment_name = environment.name
    version = execution.requested_version

    steps = [
        f"Démarrage du déploiement simulé de {application_name} {version} vers {environment_name}.",
        "Validation de la configuration de l'application.",
        f"Préparation du paquet de déploiement {application_name}:{version}.",
        f"Déploiement de la version {version} sur l'environnement {environment_name}.",
        "Vérification de l'état de santé de l'application.",
    ]
    for message in steps:
        _add_log(db, execution, LogLevel.INFO, message)
        # Commit à chaque étape : le frontend voit les logs apparaître pendant le suivi.
        db.commit()
        _pause()

    if (application_name, version) in FAILING_DEMO_DEPLOYMENTS:
        _add_log(
            db,
            execution,
            LogLevel.ERROR,
            "Échec du contrôle de santé : l'application ne répond pas (échec simulé de démonstration).",
        )
        _add_log(
            db,
            execution,
            LogLevel.WARNING,
            f"Version inchangée : {environment_name} reste en {environment.deployed_version}.",
        )
        execution.status = ExecutionStatus.FAILED
    else:
        environment.deployed_version = version
        _add_log(db, execution, LogLevel.INFO, "Contrôle de santé réussi.")
        _add_log(db, execution, LogLevel.INFO, f"Déploiement terminé : {environment_name} est maintenant en {version}.")
        execution.status = ExecutionStatus.SUCCEEDED

    execution.completed_at = utc_now()
    # Un seul commit : la nouvelle version n'est enregistrée qu'avec le statut SUCCEEDED.
    db.commit()


def _fail_after_unexpected_error(db: Session, execution_id: int) -> None:
    """Termine l'exécution en FAILED après une erreur imprévue, si la base le permet."""
    try:
        execution = db.get(Execution, execution_id)
        _add_log(
            db,
            execution,
            LogLevel.ERROR,
            "Erreur inattendue pendant la simulation : le déploiement a été interrompu.",
        )
        execution.status = ExecutionStatus.FAILED
        execution.completed_at = utc_now()
        db.commit()
    except Exception:
        logger.exception("Impossible de marquer l'exécution %s en échec", execution_id)


def _add_log(db: Session, execution: Execution, level: LogLevel, message: str) -> None:
    db.add(ExecutionLog(execution=execution, level=level, message=message))


def _pause() -> None:
    time.sleep(config.SIMULATION_STEP_DELAY_SECONDS)
