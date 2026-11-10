# AppPlatform — Business Rules

## 1. Core rules

1. Each execution is associated with one application and one target environment.
2. The target environment must belong to the selected application.
3. A requested version must be present and valid.
4. Only supported environments can be selected.
5. Production deployment requires an explicit confirmation step in the UI.
6. Important validation must be repeated in the backend.
7. A successful execution updates the deployed version of the target environment.
8. A failed execution does not update the deployed version in the simplified V1 model.
9. Completed executions and their logs are retained for history.
10. The simulated engine must never claim to have changed a real server or infrastructure.

## 2. Frontend versus backend

The frontend may validate fields to help the user and prevent avoidable mistakes. It cannot be trusted as the only enforcement point because a user can bypass the UI and send HTTP requests directly.

The backend must validate request data and apply the business rules before processing the operation.

## 3. Failure semantics

A simulated failure means the deployment process did not complete successfully. The previous deployed version remains recorded in V1.

In real systems, failure may occur after partial changes. Real platforms may need health checks, rollback or recovery procedures. Those are outside V1.

## 4. State transitions

Allowed simplified execution path:

`QUEUED` → `RUNNING` → `SUCCEEDED`

or

`QUEUED` → `RUNNING` → `FAILED`

Do not allow a completed execution to silently change from `FAILED` to `SUCCEEDED` or vice versa.
