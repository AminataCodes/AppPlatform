import pytest
from sqlalchemy import func, inspect, select, text
from sqlalchemy.exc import IntegrityError

from app.database import SessionLocal, engine, init_db
from app.models import Application, Environment, EnvironmentName
from app.seed import SEED_APPLICATIONS, seed_database


def count(session, model) -> int:
    return session.scalar(select(func.count()).select_from(model))


def test_init_db_creates_tables(empty_database):
    assert inspect(engine).get_table_names() == []

    init_db()

    assert set(inspect(engine).get_table_names()) == {"applications", "environments"}


def test_seed_creates_three_applications_with_three_environments(session):
    created = seed_database(session)

    assert created == 3
    assert count(session, Application) == 3
    assert count(session, Environment) == 9


def test_seed_is_idempotent(session):
    seed_database(session)

    created_again = seed_database(session)

    assert created_again == 0
    assert count(session, Application) == 3
    assert count(session, Environment) == 9


def test_seed_does_not_overwrite_existing_deployed_versions(session):
    seed_database(session)
    environment = session.scalar(select(Environment).where(Environment.name == EnvironmentName.DEV))
    environment.deployed_version = "9.9.9"
    session.commit()

    seed_database(session)

    session.refresh(environment)
    assert environment.deployed_version == "9.9.9"


def test_data_read_back_from_sqlite_matches_seed(session):
    seed_database(session)
    session.close()

    # Nouvelle session : les objets sont relus depuis le fichier SQLite, pas depuis la mémoire.
    with SessionLocal() as new_session:
        applications = new_session.scalars(select(Application).order_by(Application.id)).all()

        assert [application.name for application in applications] == [
            data["name"] for data in SEED_APPLICATIONS
        ]
        for application, data in zip(applications, SEED_APPLICATIONS):
            assert application.description == data["description"]
            assert application.owner_team == data["owner_team"]
            assert application.available_versions == data["available_versions"]
            assert [env.name for env in application.environments] == ["DEV", "STAGING", "PROD"]
            for environment in application.environments:
                assert environment.deployed_version == data["deployed_versions"][environment.name]
                assert environment.deployed_version in application.available_versions


def test_database_rejects_duplicate_environment_for_same_application(session):
    seed_database(session)
    application = session.scalar(select(Application).limit(1))

    session.add(Environment(application_id=application.id, name=EnvironmentName.DEV, deployed_version="1.0.0"))

    with pytest.raises(IntegrityError):
        session.commit()


def test_database_rejects_unknown_environment_name(session):
    seed_database(session)
    application = session.scalar(select(Application).limit(1))

    with pytest.raises(IntegrityError):
        session.execute(
            text("INSERT INTO environments (application_id, name, deployed_version) VALUES (:app_id, 'QA', '1.0.0')"),
            {"app_id": application.id},
        )


def test_database_rejects_environment_without_existing_application(session):
    session.add(Environment(application_id=999, name=EnvironmentName.DEV, deployed_version="1.0.0"))

    with pytest.raises(IntegrityError):
        session.commit()
