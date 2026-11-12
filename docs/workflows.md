# AppPlatform — Workflows

## 1. Scope

V1 has three user workflows. The deployment workflow is the primary operational journey.

## 2. Workflow A — Browse an application

**Goal:** understand an application's current state across environments.

1. User opens the applications list.
2. User selects an application, for example `customer-api`.
3. AppPlatform displays its description and owner team.
4. AppPlatform displays DEV, STAGING and PROD.
5. Each environment shows its currently deployed version and simplified status.

Example:

| Application | Environment | Deployed version |
|---|---|---|
| customer-api | DEV | 1.3.0 |
| customer-api | STAGING | 1.2.0 |
| customer-api | PROD | 1.1.0 |

This is one logical application with different deployments in different environments.

## 3. Workflow B — Request and follow a deployment

**Goal:** request a deployment and understand its outcome.

1. User opens an application's detail page.
2. User selects `Deploy application`.
3. User chooses a target environment.
4. User chooses an available version.
5. UI displays a review/summary step.
6. If the target is PROD, the UI requires explicit confirmation.
7. Angular sends the request to FastAPI.
8. Backend validates the application, environment, version and applicable rules.
9. Backend creates an execution record.
10. Simulated deployment service runs its steps and creates logs.
11. Backend stores the final status and logs.
12. On success, the target environment's deployed version is updated.
13. On failure, the previous deployed version remains unchanged in the simplified V1 model.
14. UI displays the result.

### Backend deployment lifecycle

Steps 7 to 13 are implemented in the backend as follows:

1. `POST /api/deployments` validates the request (rules A–F in `business-rules.md`).
2. The backend creates the execution with status `QUEUED` and schedules the simulation with FastAPI `BackgroundTasks`.
3. The backend responds `202 Accepted` immediately, with the `QUEUED` execution. The response does not depend on the outcome.
4. After the response, the background task opens its own database session and claims the execution: a single conditional update switches it from `QUEUED` to `RUNNING` and sets `started_at`. If the execution is no longer `QUEUED`, the task stops; an execution is never processed twice.
5. The simulation runs five steps. Each step writes an `INFO` log, is saved immediately, then waits a short delay (1 second by default), so a client polling `GET /api/executions/{id}` sees progress.
6. The simulation ends with `SUCCEEDED` or `FAILED` and sets `completed_at`. On success, the environment's `deployed_version` is updated **in the same database transaction** as the final status.

The whole simulation takes about 5 seconds. It never contacts any real infrastructure.

### Example success logs

```text
[15:19:47] INFO    Démarrage du déploiement simulé de customer-api 1.2.0 vers PROD.
[15:19:48] INFO    Validation de la configuration de l'application.
[15:19:49] INFO    Préparation du paquet de déploiement customer-api:1.2.0.
[15:19:50] INFO    Déploiement de la version 1.2.0 sur l'environnement PROD.
[15:19:51] INFO    Vérification de l'état de santé de l'application.
[15:19:52] INFO    Contrôle de santé réussi.
[15:19:52] INFO    Déploiement terminé : PROD est maintenant en 1.2.0.
```

### Failure behaviour

An execution can fail because a simulated step reports an error. The execution ends with `FAILED`, retains its logs and does not update the deployed version in the V1 data model.

```text
[15:20:02] INFO    Vérification de l'état de santé de l'application.
[15:20:03] ERROR   Échec du contrôle de santé : l'application ne répond pas (échec simulé de démonstration).
[15:20:03] WARNING Version inchangée : DEV reste en 1.3.0.
```

If an unexpected error interrupts the simulation, pending changes are cancelled, an `ERROR` log ("Erreur inattendue pendant la simulation…") is recorded and the execution ends with `FAILED`. Technical details are written to the server logs only, never to the execution logs.

In a real deployment, an operation can fail after partially changing infrastructure. Recovery or rollback may then be needed. V1 intentionally does not implement real rollback.

## 4. Workflow C — Review execution history

1. User opens the history page.
2. AppPlatform lists previous executions.
3. Each row shows application, environment, requested version, date and status.
4. User opens an execution.
5. AppPlatform displays its details and logs.

History is read-only in V1; it does not trigger another deployment.

## 5. Execution state machine

```text
QUEUED
   |
   v
RUNNING
   |
   +------> SUCCEEDED
   |
   +------> FAILED
```

- `QUEUED`: request accepted and waiting to be processed. `started_at` and `completed_at` are empty.
- `RUNNING`: simulated steps are being processed. `started_at` is set.
- `SUCCEEDED`: all simulated steps completed successfully. `completed_at` is set and the environment's version is updated.
- `FAILED`: a simulated step failed or an unexpected error occurred. `completed_at` is set and the environment's version is unchanged.

`SUCCEEDED` and `FAILED` are final: a finished execution is never processed again. While an execution is `QUEUED` or `RUNNING`, no other deployment can be requested on the same environment (`409 Conflict`).

The simulation is a short-lived background task inside the FastAPI process. There is no distributed queue in V1.

## 6. Deterministic demonstration scenarios

Outcomes are deterministic, never random, so the demo can reliably show both cases:

| Request | Outcome |
|---|---|
| `customer-api`, version `1.4.0`, any environment | Always `FAILED` (health check failure) |
| Any other valid request | `SUCCEEDED` |

This is a **simulation-only demonstration rule**, defined in `backend/app/services/simulation.py`. It does not reflect any real property of the application or of version `1.4.0`.
