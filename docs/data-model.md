# AppPlatform — Data Model

> Conceptual model for V1. Keep it small; refine only when implementation requires it.

## 1. Entities

### Application

Represents a software product or service tracked by the portal. It does not contain the application's source code.

Suggested fields:

| Field | Meaning |
|---|---|
| `id` | Unique identifier |
| `name` | Application name, e.g. `customer-api` |
| `description` | Short description |
| `owner_team` | Responsible team |

### Environment

Represents one installation/context of an application.

| Field | Meaning |
|---|---|
| `id` | Unique identifier |
| `application_id` | Parent application |
| `name` | `DEV`, `STAGING` or `PROD` |
| `deployed_version` | Version currently recorded as deployed |
| `status` | Simplified status for the demo |

A simple V1 model can store one environment row per application/environment pair.

### Execution

Represents one processed deployment request.

| Field | Meaning |
|---|---|
| `id` | Unique identifier |
| `application_id` | Application being deployed |
| `environment_id` | Target environment |
| `requested_version` | Version requested |
| `status` | `QUEUED`, `RUNNING`, `SUCCEEDED`, `FAILED` |
| `created_at` | Creation timestamp |
| `started_at` | Start timestamp |
| `completed_at` | Completion timestamp |

### ExecutionLog

Represents one message generated during an execution.

| Field | Meaning |
|---|---|
| `id` | Unique identifier |
| `execution_id` | Parent execution |
| `timestamp` | Time of log entry |
| `level` | `INFO`, `WARNING` or `ERROR` |
| `message` | Log text |

## 2. Relationships

- One Application has many Environments.
- One Environment belongs to one Application.
- One Application can have many Executions.
- One Environment can be targeted by many Executions over time.
- One Execution has many ExecutionLogs.

## 3. Version handling

For V1, available versions can be a small predefined list in demo data or configuration. A separate Version entity is not required unless it makes the implementation clearer.

The environment's `deployed_version` is the version currently recorded as deployed there. The `requested_version` on an execution is the version the user asked to deploy. They are not interchangeable.

## 4. Consistency rules

- A successful execution updates the target environment's `deployed_version`.
- A failed execution does not update it in the simplified V1 model.
- An execution retains its requested version and final status.
- Logs remain associated with their execution.
- An execution must reference an existing application and environment.
