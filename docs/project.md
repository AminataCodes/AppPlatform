# AppPlatform — Project Overview

> Version: 0.1  
> Target completion: 14 November 2026  
> Status: Initial scope; unresolved choices are listed in `open-questions.md`.

## 1. Purpose

AppPlatform is a small internal self-service portal concept for technical teams. It provides a simple place to:

- browse a catalogue of applications;
- inspect each application's environments and deployed versions;
- request a deployment to a target environment;
- follow the simulated execution;
- review previous executions and their logs.

This is a learning and demonstration project. It illustrates selected ideas found in application platforms; it does **not** reproduce BPCE's internal architecture and does not deploy to real infrastructure.

## 2. Primary objective

The primary objective is to demonstrate frontend UI/UX and Angular skills. The backend and infrastructure parts support the user experience and provide enough technical depth to explain how a platform workflow works.

### Priority order

1. Angular frontend, UI/UX, accessibility and clear user feedback.
2. A small REST API with FastAPI.
3. A simple simulated deployment workflow with persisted execution history.
4. Basic understanding of Docker and the place of CI/CD and automation tools.

## 3. Target user

A developer or technical team member who needs to inspect an application and request a standard deployment operation.

For V1, assume one implicit demo user. Full authentication and role management are out of scope unless the project owner explicitly changes the scope.

## 4. V1 features

- Dashboard summary.
- Applications list.
- Application details with DEV, STAGING and PROD.
- Deployment request form.
- Explicit confirmation for production deployments.
- Simulated deployment progress and logs.
- Execution result: `SUCCEEDED` or `FAILED`.
- Execution history and execution details.

## 5. Out of scope

- Real deployments or server access.
- Real Jenkins, Ansible, Kubernetes or OpenShift integrations.
- Full authentication and authorization system.
- Multiple user roles.
- Environment provisioning.
- Restart, rollback or other automation catalogue actions.
- Microservices, message brokers and advanced monitoring.

## 6. Definition of done

The V1 is complete when a user can inspect an application, request a simulated deployment, see its progress and logs, view a coherent success or failure result, and find the execution in history. The UI must handle loading, empty and error states. The project owner must be able to explain the data flow and the limits of the simulation without relying on AI.

## 7. Suggested demonstration

1. Open the applications page.
2. Select `customer-api`.
3. Show the deployed versions in each environment.
4. Request deployment of a new version to STAGING or PROD.
5. Confirm the production operation if PROD is selected.
6. Show the execution status and logs.
7. Return to history and open the completed execution.
8. Explain what would be replaced by a real automation integration in a production platform.
