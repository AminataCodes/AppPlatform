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

### Example success logs

```text
[10:32:01] Deployment requested
[10:32:02] Validating application and version
[10:32:03] Preparing deployment
[10:32:05] Deploying customer-api:1.2.0
[10:32:07] Checking application health
[10:32:08] Deployment completed successfully
```

### Failure behaviour

An execution can fail because a simulated step reports an error. The execution must end with `FAILED`, retain its logs and not update the deployed version in the V1 data model.

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

- `QUEUED`: request accepted and waiting to be processed.
- `RUNNING`: simulated steps are being processed.
- `SUCCEEDED`: all simulated steps completed successfully.
- `FAILED`: at least one simulated step failed.

A simple synchronous or short-lived simulation is enough for the learning project. Do not build a distributed queue for V1.

## 6. Deterministic demonstration scenarios

Prefer deterministic outcomes so the demo can reliably show both cases. For example, configure a known demo version to fail, or provide a controlled demo-only failure option. Do not make outcomes random unless there is a clear reason.
