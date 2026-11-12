"""Tests de bout en bout : POST /api/deployments + simulation + consultation des exécutions.

Le TestClient exécute les tâches d'arrière-plan juste après la réponse, avant de
rendre la main au test : après un POST accepté, la simulation est donc terminée.
"""

from datetime import datetime

import pytest

from app.api import deployments


@pytest.fixture
def catalog(client) -> dict:
    ids = {}
    for application in client.get("/api/applications").json():
        ids[application["name"]] = application["id"]
        for environment in application["environments"]:
            ids[(application["name"], environment["name"])] = environment["id"]
    return ids


def deploy(client, catalog, application: str, environment: str, version: str):
    return client.post(
        "/api/deployments",
        json={
            "application_id": catalog[application],
            "environment_id": catalog[(application, environment)],
            "requested_version": version,
            "confirm_production": environment == "PROD",
        },
    )


def deployed_version(client, catalog, application: str, environment: str) -> str:
    detail = client.get(f"/api/applications/{catalog[application]}").json()
    return next(env["deployed_version"] for env in detail["environments"] if env["name"] == environment)


# --- POST /api/deployments + BackgroundTasks ------------------------------------


def test_post_returns_202_with_queued_execution_then_simulation_succeeds(client, catalog):
    response = deploy(client, catalog, "customer-api", "PROD", "1.2.0")

    # La réponse décrit la demande acceptée, pas le résultat final.
    assert response.status_code == 202
    body = response.json()
    assert body["status"] == "QUEUED"
    assert body["started_at"] is None
    assert body["completed_at"] is None

    detail = client.get(f"/api/executions/{body['id']}").json()
    assert detail["status"] == "SUCCEEDED"
    assert detail["started_at"] is not None
    assert detail["completed_at"] is not None
    assert deployed_version(client, catalog, "customer-api", "PROD") == "1.2.0"


def test_post_schedules_simulation_through_background_tasks(client, catalog, monkeypatch):
    scheduled = []
    monkeypatch.setattr(deployments, "run_simulation", scheduled.append)

    response = deploy(client, catalog, "customer-api", "DEV", "1.2.0")

    assert scheduled == [response.json()["id"]]
    # La fonction de simulation a été remplacée : l'exécution est restée QUEUED.
    assert client.get(f"/api/executions/{response.json()['id']}").json()["status"] == "QUEUED"


def test_rejected_request_does_not_schedule_simulation(client, catalog, monkeypatch):
    scheduled = []
    monkeypatch.setattr(deployments, "run_simulation", scheduled.append)

    response = deploy(client, catalog, "customer-api", "DEV", "9.9.9")

    assert response.status_code == 422
    assert scheduled == []


def test_failed_simulation_through_api_keeps_previous_version(client, catalog):
    execution_id = deploy(client, catalog, "customer-api", "DEV", "1.4.0").json()["id"]

    detail = client.get(f"/api/executions/{execution_id}").json()

    assert detail["status"] == "FAILED"
    assert any(log["level"] == "ERROR" for log in detail["logs"])
    assert deployed_version(client, catalog, "customer-api", "DEV") == "1.3.0"


def test_finished_deployment_no_longer_blocks_the_environment(client, catalog):
    first = deploy(client, catalog, "customer-api", "DEV", "1.4.0")
    second = deploy(client, catalog, "customer-api", "DEV", "1.2.0")

    assert first.status_code == 202
    assert second.status_code == 202
    assert deployed_version(client, catalog, "customer-api", "DEV") == "1.2.0"


# --- GET /api/executions --------------------------------------------------------


def test_list_executions_is_empty_without_deployment(client):
    response = client.get("/api/executions")

    assert response.status_code == 200
    assert response.json() == []


def test_list_executions_returns_history_newest_first(client, catalog):
    first = deploy(client, catalog, "customer-api", "DEV", "1.2.0").json()["id"]
    second = deploy(client, catalog, "payment-api", "STAGING", "2.3.0").json()["id"]
    third = deploy(client, catalog, "customer-api", "PROD", "1.4.0").json()["id"]

    response = client.get("/api/executions")

    assert response.status_code == 200
    executions = response.json()
    assert [execution["id"] for execution in executions] == [third, second, first]
    created = [datetime.fromisoformat(execution["created_at"]) for execution in executions]
    assert created == sorted(created, reverse=True)

    newest = executions[0]
    assert newest["application"] == {"id": catalog["customer-api"], "name": "customer-api"}
    assert newest["environment"] == {"id": catalog[("customer-api", "PROD")], "name": "PROD"}
    assert newest["requested_version"] == "1.4.0"
    assert newest["status"] == "FAILED"
    assert set(newest) == {
        "id",
        "application",
        "environment",
        "requested_version",
        "status",
        "created_at",
        "started_at",
        "completed_at",
    }  # pas de logs dans la liste


# --- GET /api/executions/{id} ---------------------------------------------------


def test_get_execution_returns_details_and_ordered_logs(client, catalog):
    execution_id = deploy(client, catalog, "banking-portal", "STAGING", "3.6.0").json()["id"]

    response = client.get(f"/api/executions/{execution_id}")

    assert response.status_code == 200
    detail = response.json()
    assert detail["id"] == execution_id
    assert detail["application"]["name"] == "banking-portal"
    assert detail["environment"]["name"] == "STAGING"
    assert detail["requested_version"] == "3.6.0"
    assert detail["status"] == "SUCCEEDED"

    logs = detail["logs"]
    assert len(logs) == 7
    assert set(logs[0]) == {"id", "timestamp", "level", "message"}
    assert [log["id"] for log in logs] == sorted(log["id"] for log in logs)
    timestamps = [datetime.fromisoformat(log["timestamp"]) for log in logs]
    assert timestamps == sorted(timestamps)
    assert all(timestamp.utcoffset().total_seconds() == 0 for timestamp in timestamps)
    assert logs[0]["message"].startswith("Démarrage du déploiement simulé")
    assert logs[-1]["message"] == "Déploiement terminé : STAGING est maintenant en 3.6.0."


def test_get_unknown_execution_returns_404(client):
    response = client.get("/api/executions/9999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Exécution 9999 introuvable."}


def test_get_execution_with_invalid_id_returns_422(client):
    response = client.get("/api/executions/abc")

    assert response.status_code == 422
