from datetime import datetime

import pytest
from sqlalchemy import func, select

from app.api import deployments
from app.database import SessionLocal
from app.models import Execution, ExecutionStatus

# Données du seed utilisées ici :
#   customer-api : DEV 1.3.0, STAGING 1.2.0, PROD 1.1.0, versions 1.0.0 → 1.4.0
#   payment-api  : versions 2.0.0 → 2.3.0


@pytest.fixture(autouse=True)
def disable_simulation(monkeypatch):
    """Ces tests portent sur la validation de la demande, pas sur la simulation.

    Le TestClient exécute les tâches d'arrière-plan avant de rendre la main :
    on neutralise la simulation pour que les exécutions restent QUEUED, comme
    au moment de la réponse. La simulation est testée dans test_simulation.py.
    """
    monkeypatch.setattr(deployments, "run_simulation", lambda execution_id: None)


@pytest.fixture
def catalog(client) -> dict:
    """Associe (application, environnement) à leurs ids, lus depuis l'API."""
    ids = {}
    for application in client.get("/api/applications").json():
        ids[application["name"]] = application["id"]
        for environment in application["environments"]:
            ids[(application["name"], environment["name"])] = environment["id"]
    return ids


def deployment_payload(catalog, application="customer-api", environment="DEV", version="1.4.0", **extra) -> dict:
    return {
        "application_id": catalog[application],
        "environment_id": catalog[(application, environment)],
        "requested_version": version,
        **extra,
    }


def execution_count() -> int:
    with SessionLocal() as session:
        return session.scalar(select(func.count()).select_from(Execution))


def add_execution(catalog, environment: str, status: ExecutionStatus, application="customer-api") -> None:
    with SessionLocal() as session:
        session.add(
            Execution(
                application_id=catalog[application],
                environment_id=catalog[(application, environment)],
                requested_version="1.4.0",
                status=status,
            )
        )
        session.commit()


# --- Demandes acceptées -------------------------------------------------------


@pytest.mark.parametrize(
    ("environment", "extra"),
    [
        ("DEV", {}),
        ("STAGING", {}),
        ("PROD", {"confirm_production": True}),
    ],
)
def test_valid_request_creates_queued_execution(client, catalog, environment, extra):
    response = client.post("/api/deployments", json=deployment_payload(catalog, environment=environment, **extra))

    assert response.status_code == 202
    body = response.json()
    assert body["application"] == {"id": catalog["customer-api"], "name": "customer-api"}
    assert body["environment"] == {"id": catalog[("customer-api", environment)], "name": environment}
    assert body["requested_version"] == "1.4.0"
    assert body["status"] == "QUEUED"
    assert datetime.fromisoformat(body["created_at"]).utcoffset().total_seconds() == 0
    assert body["started_at"] is None
    assert body["completed_at"] is None
    assert execution_count() == 1


def test_valid_request_is_persisted_in_sqlite(client, catalog):
    execution_id = client.post("/api/deployments", json=deployment_payload(catalog)).json()["id"]

    with SessionLocal() as session:
        execution = session.get(Execution, execution_id)
        assert execution.application_id == catalog["customer-api"]
        assert execution.environment_id == catalog[("customer-api", "DEV")]
        assert execution.requested_version == "1.4.0"
        assert execution.status == ExecutionStatus.QUEUED


def test_redeploying_the_currently_deployed_version_is_allowed(client, catalog):
    response = client.post("/api/deployments", json=deployment_payload(catalog, environment="DEV", version="1.3.0"))

    assert response.status_code == 202


def test_successful_request_does_not_change_deployed_version(client, catalog):
    client.post("/api/deployments", json=deployment_payload(catalog, environment="PROD", confirm_production=True))

    customer_api = client.get(f"/api/applications/{catalog['customer-api']}").json()
    prod = next(env for env in customer_api["environments"] if env["name"] == "PROD")
    assert prod["deployed_version"] == "1.1.0"


# --- Règles métier : demandes refusées sans créer d'exécution -----------------


@pytest.mark.parametrize("extra", [{}, {"confirm_production": False}])
def test_prod_request_without_confirmation_is_rejected(client, catalog, extra):
    response = client.post("/api/deployments", json=deployment_payload(catalog, environment="PROD", **extra))

    assert response.status_code == 422
    assert response.json() == {"detail": "Un déploiement en PROD doit être explicitement confirmé."}
    assert execution_count() == 0


def test_unknown_application_returns_404(client, catalog):
    payload = deployment_payload(catalog) | {"application_id": 9999}

    response = client.post("/api/deployments", json=payload)

    assert response.status_code == 404
    assert response.json() == {"detail": "Application 9999 introuvable."}
    assert execution_count() == 0


def test_unknown_environment_returns_404(client, catalog):
    payload = deployment_payload(catalog) | {"environment_id": 9999}

    response = client.post("/api/deployments", json=payload)

    assert response.status_code == 404
    assert response.json() == {"detail": "Environnement 9999 introuvable."}
    assert execution_count() == 0


def test_environment_of_another_application_is_rejected(client, catalog):
    payload = deployment_payload(catalog) | {"environment_id": catalog[("payment-api", "DEV")]}

    response = client.post("/api/deployments", json=payload)

    assert response.status_code == 422
    assert "n'appartient pas à l'application customer-api" in response.json()["detail"]
    assert execution_count() == 0


def test_unavailable_version_is_rejected(client, catalog):
    # 2.0.0 existe pour payment-api, mais pas pour customer-api.
    response = client.post("/api/deployments", json=deployment_payload(catalog, version="2.0.0"))

    assert response.status_code == 422
    assert response.json() == {"detail": "La version 2.0.0 n'est pas disponible pour customer-api."}
    assert execution_count() == 0


@pytest.mark.parametrize("active_status", [ExecutionStatus.QUEUED, ExecutionStatus.RUNNING])
def test_active_execution_on_same_environment_returns_409(client, catalog, active_status):
    add_execution(catalog, "DEV", active_status)

    response = client.post("/api/deployments", json=deployment_payload(catalog, environment="DEV"))

    assert response.status_code == 409
    assert "déjà en cours sur customer-api DEV" in response.json()["detail"]
    assert execution_count() == 1


def test_second_request_on_same_environment_through_api_returns_409(client, catalog):
    first = client.post("/api/deployments", json=deployment_payload(catalog))
    second = client.post("/api/deployments", json=deployment_payload(catalog))

    assert first.status_code == 202
    assert second.status_code == 409
    assert execution_count() == 1


# --- Exécutions qui ne doivent pas bloquer ------------------------------------


def test_active_execution_on_another_environment_does_not_block(client, catalog):
    add_execution(catalog, "STAGING", ExecutionStatus.RUNNING)
    add_execution(catalog, "DEV", ExecutionStatus.RUNNING, application="payment-api")

    response = client.post("/api/deployments", json=deployment_payload(catalog, environment="DEV"))

    assert response.status_code == 202
    assert execution_count() == 3


@pytest.mark.parametrize("finished_status", [ExecutionStatus.SUCCEEDED, ExecutionStatus.FAILED])
def test_finished_execution_does_not_block(client, catalog, finished_status):
    add_execution(catalog, "DEV", finished_status)

    response = client.post("/api/deployments", json=deployment_payload(catalog, environment="DEV"))

    assert response.status_code == 202
    assert execution_count() == 2


# --- Validation de la structure de la requête (Pydantic) ----------------------


@pytest.mark.parametrize(
    "change",
    [
        {"application_id": None},  # champ obligatoire absent (retiré ci-dessous)
        {"application_id": "abc"},  # mauvais type
        {"requested_version": ""},  # version vide
        {"confirm_production": "peut-être"},  # booléen invalide
        {"status": "SUCCEEDED"},  # champ contrôlé par le backend
        {"created_at": "2026-01-01T00:00:00Z"},  # champ contrôlé par le backend
    ],
)
def test_invalid_request_body_returns_422(client, catalog, change):
    payload = deployment_payload(catalog) | change
    payload = {key: value for key, value in payload.items() if value is not None}

    response = client.post("/api/deployments", json=payload)

    assert response.status_code == 422
    # Erreur de validation FastAPI : `detail` est une liste d'erreurs par champ.
    assert isinstance(response.json()["detail"], list)
    assert execution_count() == 0
