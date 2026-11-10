# AppPlatform — REST API Contract (Draft)

> Candidate endpoints only. Confirm exact schemas and status codes during implementation.

## 1. General conventions

- Base path: `/api`
- Data format: JSON
- HTTP methods express the operation.
- The backend is authoritative for validation and business rules.
- The frontend must handle unsuccessful HTTP responses.

## 2. Candidate endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/api/applications` | List applications |
| `GET` | `/api/applications/{id}` | Get application details and environments |
| `POST` | `/api/deployments` | Request a deployment |
| `GET` | `/api/executions` | List executions |
| `GET` | `/api/executions/{id}` | Get execution details and logs |

## 3. Example deployment request

```json
{
  "application_id": 1,
  "environment_id": 3,
  "version": "1.2.0"
}
```

## 4. Example accepted response

```json
{
  "id": 42,
  "application": "customer-api",
  "environment": "PROD",
  "requested_version": "1.2.0",
  "status": "QUEUED"
}
```

This is illustrative, not a finalized schema. Exact field names and response structure must be aligned with the actual backend implementation.

## 5. Validation responsibilities

The backend should verify:
- application exists;
- target environment exists and belongs to the application;
- requested version is valid and available for that application;
- target environment is supported;
- any applicable deployment rule is satisfied.

Production confirmation in the UI is a UX safeguard. It is not proof of authorization. Any actual authorization rule must be enforced by the backend.

## 6. Error handling

Return useful HTTP error responses and a consistent JSON error shape. The frontend should distinguish:
- invalid request;
- missing application/environment/execution;
- business rule rejection;
- unexpected server error;
- network failure.

Do not expose stack traces or internal implementation details to the UI.
