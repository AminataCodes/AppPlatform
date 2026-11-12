"""Configuration commune des tests.

Les tests utilisent une base SQLite temporaire, jamais la base de développement.
La variable d'environnement doit être définie AVANT d'importer `app`, car le
moteur SQLAlchemy lit l'adresse de la base au moment de l'import.
"""

import os
import shutil
import tempfile
from pathlib import Path

TEST_DB_DIR = Path(tempfile.mkdtemp(prefix="appplatform-tests-"))
os.environ["APPPLATFORM_DATABASE_URL"] = f"sqlite:///{TEST_DB_DIR / 'test.db'}"
# Pas d'attente entre les étapes de la simulation pendant les tests.
os.environ["APPPLATFORM_SIMULATION_STEP_DELAY_SECONDS"] = "0"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app import models  # noqa: E402, F401  (enregistre les tables dans Base.metadata)
from app.database import Base, SessionLocal, engine  # noqa: E402
from app.main import app  # noqa: E402

# Garde-fou : on refuse de lancer les tests sur une autre base que la base temporaire.
assert engine.url.database == str(TEST_DB_DIR / "test.db"), "Les tests doivent utiliser la base de test"


@pytest.fixture(scope="session", autouse=True)
def remove_test_database():
    yield
    engine.dispose()
    shutil.rmtree(TEST_DB_DIR, ignore_errors=True)


@pytest.fixture
def empty_database():
    """Base de test sans aucune table : chaque test part de zéro."""
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def session(empty_database):
    """Session sur une base de test dont les tables existent mais sont vides."""
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db_session:
        yield db_session


@pytest.fixture
def client(empty_database):
    """Client HTTP de test. Le `with` déclenche le démarrage de l'app : tables + seed."""
    with TestClient(app) as test_client:
        yield test_client
