# AppPlatform — REST API Contract (Draft)

> Implemented endpoints are documented with their actual schemas. Endpoints marked "Planned" are still candidates: confirm their schemas during implementation.

## 1. General conventions

- Base path: `/api`
- Data format: JSON
- HTTP methods express the operation.
- The backend is authoritative for validation and business rules.
- The frontend must handle unsuccessful HTTP responses.

## 2. Endpoints

| Method | Endpoint | Purpose | Status |
|---|---|---|---|
| `GET` | `/api/applications` | List applications | Implemented |
| `GET` | `/api/applications/{id}` | Get application details and environments | Implemented |
| `POST` | `/api/deployments` | Request a deployment | Implemented |
| `GET` | `/api/executions` | List executions | Planned |
| `GET` | `/api/executions/{id}` | Get execution details and logs | Planned |

## 3. `POST /api/deployments`

Validates a deployment request and records it as an execution with status `QUEUED`. It does not run the deployment and does not change the environment's deployed version.

### Request body

| Field | Type | Required | Notes |
|---|---|---|---|
| `application_id` | integer | yes | |
| `environment_id` | integer | yes | Must belong to the application |
| `requested_version` | string | yes | 1–50 characters; must be in the application's `available_versions` |
| `confirm_production` | boolean | no (default `false`) | Must be `true` when the target environment is `PROD` |

Any other field (for example `status` or `created_at`) is rejected with `422`: status and timestamps are always set by the backend.

```json
{
  "application_id": 1,
  "environment_id": 3,
  "requested_version": "1.2.0",
  "confirm_production": true
}
```

### Response — `202 Accepted`

`202` means the request has been accepted and recorded, but the deployment has not been executed yet.

```json
{
  "id": 1,
  "application": { "id": 1, "name": "customer-api" },
  "environment": { "id": 3, "name": "PROD" },
  "requested_version": "1.2.0",
  "status": "QUEUED",
  "created_at": "2026-11-10T14:53:51.018452Z",
  "started_at": null,
  "completed_at": null
}
```

Timestamps are UTC (ISO 8601, `Z` suffix).

### Errors

| Code | When | Example `detail` |
|---|---|---|
| `404` | Application does not exist | `"Application 999 introuvable."` |
| `404` | Environment does not exist | `"Environnement 999 introuvable."` |
| `422` | Environment belongs to another application | `"L'environnement 4 n'appartient pas à l'application customer-api."` |
| `422` | Version not available for the application | `"La version 9.9.9 n'est pas disponible pour customer-api."` |
| `422` | `PROD` target without `confirm_production: true` | `"Un déploiement en PROD doit être explicitement confirmé."` |
| `409` | A `QUEUED` or `RUNNING` execution already exists on the target environment | `"Un déploiement est déjà en cours sur customer-api PROD (exécution 1)."` |
| `422` | Malformed body (missing field, wrong type, empty version, unknown field) | List of field errors (see §5) |

The rules and their order are described in `business-rules.md`. A rejected request never creates an execution.

## 4. Validation responsibilities

The backend verifies every rule listed above; the frontend may repeat them to guide the user, but cannot replace them.

Production confirmation is an explicit acknowledgement required both in the UI and by the backend (`confirm_production`). It is not proof of authorization: V1 has no authentication or role checks.

## 5. Error handling

Errors use FastAPI's format: a JSON object with a `detail` field.

- Business rule errors (`404`, `409`, and business `422`): `detail` is a human-readable string.
- Request validation errors (`422` from FastAPI/Pydantic): `detail` is a list of field errors, for example:

```json
{
  "detail": [
    { "type": "extra_forbidden", "loc": ["body", "status"], "msg": "Extra inputs are not permitted", "input": "SUCCEEDED" }
  ]
}
```

The frontend normalizes both shapes into a single user-facing message. It should distinguish:
- invalid request;
- missing application/environment/execution;
- business rule rejection;
- unexpected server error;
- network failure.

Do not expose stack traces or internal implementation details to the UI.
