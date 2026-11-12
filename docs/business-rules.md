# AppPlatform — Business Rules

## 1. Core rules

1. Each execution is associated with one application and one target environment.
2. The target environment must belong to the selected application.
3. A requested version must be present and valid.
4. Only supported environments can be selected.
5. Production deployment requires an explicit confirmation step in the UI, and the backend requires `confirm_production: true` for every `PROD` request.
6. Important validation must be repeated in the backend.
7. A successful execution updates the deployed version of the target environment.
8. A failed execution does not update the deployed version in the simplified V1 model.
9. Completed executions and their logs are retained for history.
10. The simulated engine must never claim to have changed a real server or infrastructure.

## 2. Frontend versus backend

The frontend may validate fields to help the user and prevent avoidable mistakes. It cannot be trusted as the only enforcement point because a user can bypass the UI and send HTTP requests directly.

The backend must validate request data and apply the business rules before processing the operation.

## 3. Deployment request validation

`POST /api/deployments` first checks the request structure (Pydantic), then applies the following rules in the backend service layer, in this order. The first rule that fails stops the request; a rejected request never creates an execution.

| Rule | Check | Response if not met |
|---|---|---|
| A | The application exists | `404 Not Found` |
| B | The environment exists | `404 Not Found` |
| C | The environment belongs to the requested application | `422 Unprocessable Content` |
| D | `requested_version` is in the application's `available_versions` | `422 Unprocessable Content` |
| E | If the environment is `PROD`, `confirm_production` is `true` (not required for `DEV` and `STAGING`) | `422 Unprocessable Content` |
| F | No execution with status `QUEUED` or `RUNNING` exists for the same environment | `409 Conflict` |

Additional points:

- Rule F is scoped to the target environment: an active execution on another environment, or on another application, does not block the request. `SUCCEEDED` and `FAILED` executions never block.
- Redeploying the version already deployed in the environment is allowed; the UI should warn the user.
- The client cannot set the execution status or timestamps: unknown fields are rejected.
- When all rules pass, the backend creates an execution with status `QUEUED`, `created_at` set to the current UTC time, and empty `started_at` / `completed_at`, then schedules the simulated deployment. The environment's `deployed_version` is not changed at this stage.

## 4. Deployed version update

The environment's `deployed_version` changes in exactly one situation: when a simulated deployment ends with `SUCCEEDED`. It then becomes the execution's `requested_version`.

- It is never changed when a request is accepted, while the execution is `QUEUED` or `RUNNING`, or when the execution ends with `FAILED`.
- The new version and the `SUCCEEDED` status are saved in the same database transaction: the version can never be observed as updated for an execution that did not succeed.
- Only the target environment changes; the application's other environments keep their versions.

## 5. Deterministic failure scenario (demonstration only)

To demonstrate both outcomes reliably, the simulation applies one fixed rule:

- `customer-api` with `requested_version` `1.4.0` always ends with `FAILED`, whatever the target environment. The execution records an `ERROR` log explaining the simulated health-check failure, and the environment keeps its previous version.
- Every other valid request ends with `SUCCEEDED`, unless an unexpected error interrupts the simulation.

This is **not a business rule** of AppPlatform or of `customer-api`: it is a simulation-only demonstration rule. Version `1.4.0` is accepted by the request validation like any other available version; it only fails during the simulated deployment.

## 6. Failure semantics

A simulated failure means the deployment process did not complete successfully. The previous deployed version remains recorded in V1.

In real systems, failure may occur after partial changes. Real platforms may need health checks, rollback or recovery procedures. Those are outside V1.

## 7. State transitions

Allowed simplified execution path:

`QUEUED` → `RUNNING` → `SUCCEEDED`

or

`QUEUED` → `RUNNING` → `FAILED`

Do not allow a completed execution to silently change from `FAILED` to `SUCCEEDED` or vice versa.

The simulation enforces this: it only starts an execution that is still `QUEUED` (atomic conditional update to `RUNNING`), so a `RUNNING`, `SUCCEEDED` or `FAILED` execution is never processed again.
