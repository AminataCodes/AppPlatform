# AppPlatform — Delivery Roadmap

> Target completion: 14 November 2026. The schedule is tight; protect the core workflow and reduce scope rather than adding features.

## Delivery priorities

### Must have

- Applications list and detail.
- Environment/version display.
- Deployment request form.
- Production confirmation UX.
- Backend validation.
- Simulated success and failure.
- Execution logs and history.
- Loading, empty and error states.
- A coherent visual system and responsive basics.

### Should have if time permits

- Dashboard summary cards.
- Simple search/filter.
- Docker Compose setup.
- A few automated tests beyond core business scenarios.

### Not in V1

- Real infrastructure integration.
- Jenkins/Ansible/OpenShift implementation.
- Full authentication.
- Additional operation types.
- Complex state management or distributed processing.

## Suggested schedule

| Date | Focus | Expected result |
|---|---|---|
| 10 Nov | Freeze scope, user journeys and UI structure | Approved screen list and data flow |
| 11 Nov | Minimal FastAPI API and SQLite persistence | Applications/environments can be read; execution can be stored |
| 12 Nov | Angular screens and API integration | Main screens work with real API data |
| 13 Nov | Deployment workflow, logs, history and tests | End-to-end happy path and failure path |
| 14 Nov | Polish, README, demo rehearsal and explanation | Stable project that can be presented |

## Working method

For each feature:

1. Understand and restate the requirement.
2. Ask the coding assistant to inspect the project and propose a plan before editing.
3. Implement one small feature at a time.
4. Review every changed file.
5. Trace the data flow from Angular to FastAPI to SQLite.
6. Test normal and error cases.
7. Explain the feature without AI before moving on.

## Risk management

If behind schedule:
1. Keep the application list and detail.
2. Keep one deployment workflow.
3. Keep both success and failure outcomes.
4. Keep execution logs and history if possible.
5. Simplify the dashboard and remove optional filters.
6. Defer Docker if the application is not yet stable.
