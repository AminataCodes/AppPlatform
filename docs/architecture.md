# AppPlatform — Architecture

> Version: 0.1 — proposed architecture for a small learning project.

## 1. Architectural goal

Keep the architecture understandable and deliberately small. The frontend must be the main focus; the backend exists to expose a realistic API boundary, apply business rules and persist the simulated workflow.

## 2. High-level architecture

```text
┌────────────────────────────────────────────┐
│              Angular Frontend              │
│ Pages, components, routing, forms, UX       │
└─────────────────────┬──────────────────────┘
                      │ HTTP / JSON
                      ▼
┌────────────────────────────────────────────┐
│                FastAPI Backend              │
│ API routes, validation, business services   │
└─────────────────────┬──────────────────────┘
                      │
                      ▼
┌────────────────────────────────────────────┐
│       Simulated Deployment Service          │
│ Steps, outcome and execution logs           │
└─────────────────────┬──────────────────────┘
                      │
                      ▼
┌────────────────────────────────────────────┐
│                  SQLite                     │
│ Applications, environments, executions     │
└────────────────────────────────────────────┘
```

The simulated deployment service is an internal backend service/module in V1, not a separately deployed microservice.

## 3. Component responsibilities

### Angular frontend

- Render application and environment data.
- Collect deployment parameters.
- Guide the user through confirmation.
- Call the backend through HTTP.
- Present loading, success, failure and empty states.
- Keep UI components focused on presentation and interaction.

Angular must not be treated as a security boundary. Client-side validation improves usability, but the backend must repeat all important validation.

### FastAPI backend

- Expose REST endpoints.
- Validate request payloads.
- Apply business rules.
- Create execution records.
- Coordinate the simulation service.
- Persist execution state and logs.
- Return clear HTTP responses.

### Simulated deployment service

- Represent a small sequence of deployment steps.
- Produce log entries.
- Determine a controlled success or failure result.
- Update the environment's deployed version only after simulated success.
- Never connect to or modify real infrastructure.

### SQLite

Persist the catalogue, environment state and execution history. SQLite is sufficient for this single-user demonstration; a production platform might use a managed relational database.

## 4. Suggested backend layering

A simple structure is sufficient:

- `api/`: HTTP routes and request/response schemas.
- `services/`: business operations and deployment simulation.
- `models/`: database models.
- `repositories/` (optional): database access if it improves clarity.
- `database/`: connection and initialization.

Do not add layers merely to imitate enterprise architecture. Each layer should have a clear responsibility.

## 5. Main request flow

1. The user submits a deployment form in Angular.
2. An Angular service sends an HTTP POST request.
3. FastAPI validates the payload.
4. The backend verifies that the application and target environment exist.
5. The backend creates an execution.
6. The simulation service processes its steps and creates logs.
7. On success, the environment's deployed version is updated.
8. On failure, the previous deployed version remains unchanged in the V1 model.
9. Angular displays the result and can load the execution detail.

## 6. Important architecture principles

- Separate UI responsibilities from business rules.
- Keep the backend authoritative for validation.
- Make the execution state explicit.
- Persist outcomes and logs so history survives page refreshes.
- Prefer a predictable, testable simulation over random behaviour.
- Do not claim that a simulated deployment changes real infrastructure.

## 7. Future evolution (not V1)

A real platform might replace the simulated service with an adapter that triggers a CI/CD pipeline or an automation tool. Jenkins, Ansible or an OpenShift/Kubernetes deployment mechanism are examples of possible integrations, not components that V1 must implement.
