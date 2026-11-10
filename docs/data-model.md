# AppPlatform — Data Model

> Conceptual model for V1. Keep it small; refine only when implementation requires it.

## 1. Entities

### Application

Represents a software product or service tracked by the portal. It does not contain the application's source code.

Suggested fields:

| Field | Meaning |
|---|---|
| `id` | Unique identifier |
| `name` | Application name, e.g. `customer-api` (unique) |
| `description` | Short description |
| `owner_team` | Responsible team |
| `available_versions` | Versions that can be requested for deployment, stored as a JSON list in a single column (see §3) |

### Environment

Represents one installation/context of an application.

| Field | Meaning |
|---|---|
| `id` | Unique identifier |
| `application_id` | Parent application |
| `name` | `DEV`, `STAGING` or `PROD` |
| `deployed_version` | Version currently recorded as deployed |

The V1 model stores one environment row per application/environment pair, enforced by a unique constraint on (`application_id`, `name`). The database also restricts `name` to `DEV`, `STAGING` and `PROD`.

An environment has no `status` field in V1: the state of a deployment is carried by its executions.

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

For V1, available versions are a small predefined list defined in the demo data (seed) and stored in the `available_versions` JSON column of each Application. There is no separate Version entity or table. Every environment's `deployed_version` is one of its application's available versions.

The environment's `deployed_version` is the version currently recorded as deployed there. The `requested_version` on an execution is the version the user asked to deploy. They are not interchangeable.

## 4. Consistency rules

- A successful execution updates the target environment's `deployed_version`.
- A failed execution does not update it in the simplified V1 model.
- An execution retains its requested version and final status.
- Logs remain associated with their execution.
- An execution must reference an existing application and environment.
