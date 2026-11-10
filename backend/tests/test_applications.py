def test_list_applications_returns_the_three_seeded_applications(client):
    response = client.get("/api/applications")

    assert response.status_code == 200
    assert [application["name"] for application in response.json()] == [
        "customer-api",
        "payment-api",
        "banking-portal",
    ]


def test_each_application_has_dev_staging_and_prod(client):
    applications = client.get("/api/applications").json()

    for application in applications:
        assert [env["name"] for env in application["environments"]] == ["DEV", "STAGING", "PROD"]


def test_each_application_exposes_available_versions(client):
    applications = client.get("/api/applications").json()

    for application in applications:
        assert len(application["available_versions"]) > 1
        for environment in application["environments"]:
            assert environment["deployed_version"] in application["available_versions"]


def test_get_application_returns_its_detail(client):
    applications = client.get("/api/applications").json()
    customer_api = next(application for application in applications if application["name"] == "customer-api")

    response = client.get(f"/api/applications/{customer_api['id']}")

    assert response.status_code == 200
    detail = response.json()
    assert detail == customer_api
    assert detail["owner_team"] == "Équipe Clients"
    assert {env["name"]: env["deployed_version"] for env in detail["environments"]} == {
        "DEV": "1.3.0",
        "STAGING": "1.2.0",
        "PROD": "1.1.0",
    }
    assert detail["available_versions"] == ["1.0.0", "1.1.0", "1.2.0", "1.3.0", "1.4.0"]


def test_get_unknown_application_returns_404(client):
    response = client.get("/api/applications/9999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Application 9999 introuvable."}


def test_get_application_with_invalid_id_returns_422(client):
    response = client.get("/api/applications/abc")

    assert response.status_code == 422
