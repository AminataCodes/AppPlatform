from datetime import UTC, datetime, timedelta, timezone

import pytest
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError

from app.database import SessionLocal
from app.models import (
    Application,
    Environment,
    EnvironmentName,
    Execution,
    ExecutionLog,
    ExecutionStatus,
    LogLevel,
)
from app.seed import seed_database


@pytest.fixture
def customer_api(session) -> Application:
    seed_database(session)
    return session.scalar(select(Application).where(Application.name == "customer-api"))


@pytest.fixture
def dev_environment(customer_api) -> Environment:
    return next(env for env in customer_api.environments if env.name == EnvironmentName.DEV)


@pytest.fixture
def execution(session, customer_api, dev_environment) -> Execution:
    execution = Execution(application=customer_api, environment=dev_environment, requested_version="1.4.0")
    session.add(execution)
    session.commit()
    return execution


def test_create_execution_with_default_values(execution):
    assert execution.id is not None
    assert execution.requested_version == "1.4.0"
    assert execution.status == ExecutionStatus.QUEUED
    assert execution.created_at.tzinfo == UTC
    assert execution.started_at is None
    assert execution.completed_at is None


def test_execution_dates_are_stored_and_read_back_in_utc(session, execution):
    paris_time = datetime(2026, 11, 10, 14, 30, tzinfo=timezone(timedelta(hours=1)))
    execution.started_at = paris_time
    session.commit()

    with SessionLocal() as new_session:
        started_at = new_session.get(Execution, execution.id).started_at

    assert started_at.tzinfo == UTC
    assert started_at == paris_time
    assert started_at.hour == 13


def test_create_execution_log_with_default_values(session, execution):
    log = ExecutionLog(execution=execution, message="Deployment requested")
    session.add(log)
    session.commit()

    assert log.id is not None
    assert log.execution_id == execution.id
    assert log.level == LogLevel.INFO
    assert log.timestamp.tzinfo == UTC
    assert log.message == "Deployment requested"


@pytest.mark.parametrize("status", list(ExecutionStatus))
def test_execution_accepts_every_valid_status(session, execution, status):
    execution.status = status
    session.commit()

    with SessionLocal() as new_session:
        assert new_session.get(Execution, execution.id).status == status


@pytest.mark.parametrize("level", list(LogLevel))
def test_execution_log_accepts_every_valid_level(session, execution, level):
    log = ExecutionLog(execution=execution, level=level, message="Message")
    session.add(log)
    session.commit()

    with SessionLocal() as new_session:
        assert new_session.get(ExecutionLog, log.id).level == level


def test_database_rejects_unknown_execution_status(session, customer_api, dev_environment):
    with pytest.raises(IntegrityError):
        session.execute(
            text(
                "INSERT INTO executions (application_id, environment_id, requested_version, status, created_at) "
                "VALUES (:app_id, :env_id, '1.4.0', 'CANCELLED', '2026-11-10 13:00:00')"
            ),
            {"app_id": customer_api.id, "env_id": dev_environment.id},
        )


def test_database_rejects_unknown_log_level(session, execution):
    with pytest.raises(IntegrityError):
        session.execute(
            text(
                "INSERT INTO execution_logs (execution_id, timestamp, level, message) "
                "VALUES (:execution_id, '2026-11-10 13:00:00', 'DEBUG', 'Message')"
            ),
            {"execution_id": execution.id},
        )


def test_database_rejects_execution_with_unknown_application(session, dev_environment):
    session.add(Execution(application_id=999, environment_id=dev_environment.id, requested_version="1.4.0"))

    with pytest.raises(IntegrityError):
        session.commit()


def test_database_rejects_execution_with_unknown_environment(session, customer_api):
    session.add(Execution(application_id=customer_api.id, environment_id=999, requested_version="1.4.0"))

    with pytest.raises(IntegrityError):
        session.commit()


def test_database_rejects_log_with_unknown_execution(session):
    session.add(ExecutionLog(execution_id=999, message="Orphan log"))

    with pytest.raises(IntegrityError):
        session.commit()


def test_execution_is_linked_to_its_application_and_environment(execution):
    with SessionLocal() as new_session:
        stored = new_session.get(Execution, execution.id)

        assert stored.application.name == "customer-api"
        assert stored.environment.name == EnvironmentName.DEV
        assert stored.environment.application_id == stored.application_id
        assert [e.id for e in stored.application.executions] == [execution.id]
        assert [e.id for e in stored.environment.executions] == [execution.id]


def test_execution_logs_are_linked_and_ordered(session, execution):
    for message in ["Deployment requested", "Preparing deployment", "Deployment completed"]:
        session.add(ExecutionLog(execution=execution, message=message))
    session.commit()

    with SessionLocal() as new_session:
        stored = new_session.get(Execution, execution.id)

        assert [log.message for log in stored.logs] == [
            "Deployment requested",
            "Preparing deployment",
            "Deployment completed",
        ]
        assert all(log.execution_id == execution.id for log in stored.logs)


def test_deleting_execution_deletes_its_logs(session, execution):
    session.add(ExecutionLog(execution=execution, message="Deployment requested"))
    session.commit()

    session.delete(execution)
    session.commit()

    assert session.scalars(select(ExecutionLog)).all() == []
