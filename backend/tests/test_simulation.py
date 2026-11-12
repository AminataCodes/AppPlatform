"""Tests du service de simulation, appelé directement (sans HTTP)."""

import pytest
from sqlalchemy import select

from app.database import SessionLocal
from app.models import Application, Environment, EnvironmentName, Execution, ExecutionStatus, LogLevel
from app.seed import seed_database
from app.services import simulation
from app.services.simulation import run_simulation


@pytest.fixture
def create_execution(session):
    """Crée une exécution QUEUED pour (application, environnement, version) et renvoie son id."""
    seed_database(session)

    def _create(application_name: str, environment_name: str, version: str, status=ExecutionStatus.QUEUED) -> int:
        application = session.scalar(select(Application).where(Application.name == application_name))
        environment = next(env for env in application.environments if env.name == environment_name)
        execution = Execution(
            application=application, environment=environment, requested_version=version, status=status
        )
        session.add(execution)
        session.commit()
        return execution.id

    return _create


def load_execution(execution_id: int) -> Execution:
    """Relit l'exécution, ses logs et son environnement dans une nouvelle session."""
    with SessionLocal() as db:
        execution = db.get(Execution, execution_id)
        _ = execution.logs, execution.environment.deployed_version  # chargement avant fermeture
        return execution


def deployed_version(application_name: str, environment_name: str) -> str:
    with SessionLocal() as db:
        return db.scalar(
            select(Environment.deployed_version)
            .join(Application)
            .where(Application.name == application_name, Environment.name == environment_name)
        )


@pytest.fixture
def observed_states(monkeypatch):
    """Remplace la pause entre étapes par un relevé de l'état en base pendant la simulation."""
    states = []

    def record_state():
        with SessionLocal() as db:
            execution = db.scalars(select(Execution)).one()
            states.append((execution.status, execution.environment.deployed_version))

    monkeypatch.setattr(simulation, "_pause", record_state)
    return states


# --- Succès --------------------------------------------------------------------


def test_success_goes_through_running_then_succeeded(create_execution, observed_states):
    execution_id = create_execution("customer-api", "PROD", "1.2.0")

    run_simulation(execution_id)

    # Pendant toutes les étapes : RUNNING, et la version n'a pas encore changé.
    assert len(observed_states) == 5
    assert observed_states == [(ExecutionStatus.RUNNING, "1.1.0")] * 5
    execution = load_execution(execution_id)
    assert execution.status == ExecutionStatus.SUCCEEDED
    assert execution.started_at is not None
    assert execution.completed_at is not None
    assert execution.created_at <= execution.started_at <= execution.completed_at


def test_success_updates_deployed_version(create_execution):
    execution_id = create_execution("customer-api", "PROD", "1.2.0")

    run_simulation(execution_id)

    assert deployed_version("customer-api", "PROD") == "1.2.0"
    # Les autres environnements ne bougent pas.
    assert deployed_version("customer-api", "DEV") == "1.3.0"
    assert deployed_version("customer-api", "STAGING") == "1.2.0"


def test_success_generates_ordered_info_logs(create_execution):
    execution_id = create_execution("payment-api", "STAGING", "2.3.0")

    run_simulation(execution_id)

    logs = load_execution(execution_id).logs
    assert len(logs) == 7
    assert all(log.level == LogLevel.INFO for log in logs)
    assert logs[0].message.startswith("Démarrage du déploiement simulé de payment-api 2.3.0 vers STAGING")
    assert logs[-1].message == "Déploiement terminé : STAGING est maintenant en 2.3.0."
    timestamps = [log.timestamp for log in logs]
    assert timestamps == sorted(timestamps)


# --- Échec déterministe ----------------------------------------------------------


def test_customer_api_1_4_0_fails(create_execution, observed_states):
    execution_id = create_execution("customer-api", "DEV", "1.4.0")

    run_simulation(execution_id)

    execution = load_execution(execution_id)
    assert execution.status == ExecutionStatus.FAILED
    assert execution.started_at is not None
    assert execution.completed_at is not None
    assert all(status == ExecutionStatus.RUNNING for status, _ in observed_states)


def test_failure_generates_error_log_and_keeps_previous_version(create_execution):
    execution_id = create_execution("customer-api", "DEV", "1.4.0")

    run_simulation(execution_id)

    logs = load_execution(execution_id).logs
    error_logs = [log for log in logs if log.level == LogLevel.ERROR]
    assert len(error_logs) == 1
    assert "échec simulé de démonstration" in error_logs[0].message
    assert logs[-1].level == LogLevel.WARNING
    assert logs[-1].message == "Version inchangée : DEV reste en 1.3.0."
    assert deployed_version("customer-api", "DEV") == "1.3.0"


# --- Robustesse ------------------------------------------------------------------


def test_execution_is_not_processed_twice(create_execution):
    execution_id = create_execution("customer-api", "DEV", "1.2.0")
    run_simulation(execution_id)
    first_run = load_execution(execution_id)

    run_simulation(execution_id)

    second_run = load_execution(execution_id)
    assert len(second_run.logs) == len(first_run.logs)
    assert second_run.completed_at == first_run.completed_at


@pytest.mark.parametrize("status", [ExecutionStatus.RUNNING, ExecutionStatus.SUCCEEDED, ExecutionStatus.FAILED])
def test_execution_not_queued_is_ignored(create_execution, status):
    execution_id = create_execution("customer-api", "DEV", "1.2.0", status=status)

    run_simulation(execution_id)

    execution = load_execution(execution_id)
    assert execution.status == status
    assert execution.logs == []
    assert deployed_version("customer-api", "DEV") == "1.3.0"


def test_unknown_execution_is_ignored(session):
    run_simulation(9999)  # ne doit pas lever d'exception


def test_unexpected_error_marks_execution_failed(create_execution, monkeypatch):
    execution_id = create_execution("customer-api", "PROD", "1.2.0")

    def broken_pause():
        raise RuntimeError("panne simulée")

    monkeypatch.setattr(simulation, "_pause", broken_pause)

    run_simulation(execution_id)

    execution = load_execution(execution_id)
    assert execution.status == ExecutionStatus.FAILED
    assert execution.completed_at is not None
    assert execution.logs[-1].level == LogLevel.ERROR
    assert execution.logs[-1].message == "Erreur inattendue pendant la simulation : le déploiement a été interrompu."
    # Le détail technique de l'erreur n'est pas exposé dans les logs visibles.
    assert all("panne simulée" not in log.message for log in execution.logs)
    assert deployed_version("customer-api", "PROD") == "1.1.0"
