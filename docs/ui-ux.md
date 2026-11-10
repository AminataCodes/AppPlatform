# AppPlatform — UI/UX Requirements

> The primary role target is Frontend UI/UX Angular developer. This document defines the interface requirements before implementation.

## 1. UX objective

Help a technical user answer three questions quickly:

1. Which applications are available?
2. What version is deployed in each environment?
3. What happened to a deployment request?

The interface should feel like a credible internal enterprise tool: clear, consistent, calm and efficient. Avoid decorative dashboards that obscure operational information.

## 2. Information architecture

Proposed main navigation:

- Dashboard
- Applications
- Executions / History

The deployment action should be reachable from an application's detail page. Execution details should be reachable from both the history list and the post-deployment result.

## 3. Screens

### Dashboard

Show a small set of useful indicators:
- number of applications;
- count of recent successful/failed executions;
- recent executions;
- quick access to applications.

Do not add metrics that have no meaning in the demo.

### Applications list

Show:
- application name;
- short description;
- owner team;
- concise status or environment summary;
- action to open details.

A simple search or filter is optional if time allows.

### Application details

Show:
- application identity and description;
- environment summary for DEV, STAGING and PROD;
- deployed version for each environment;
- deployment action.

Make it visually obvious that the environments belong to the same application.

### Deployment form

Fields:
- target environment;
- version to deploy.

Requirements:
- clear labels and helper text;
- required-field validation;
- disabled or blocked submit when input is invalid;
- review/confirmation before submission;
- stronger explicit confirmation for PROD;
- useful error messages if the API rejects the request.

### Execution details

Show:
- execution status;
- application and target environment;
- requested version;
- timestamps if available;
- ordered steps or logs;
- final success/failure explanation.

Logs should be readable and scannable, not styled as a dense wall of text.

### History

Show:
- application;
- environment;
- requested version;
- date;
- status;
- link to execution details.

Filtering is optional; clarity is more important than feature count.

## 4. UI states

Every data-driven screen should consider:

- loading;
- loaded with data;
- empty state;
- API/network error;
- invalid form;
- submission in progress;
- execution queued;
- execution running;
- execution succeeded;
- execution failed.

Do not leave blank panels when data is loading or unavailable.

## 5. Visual and interaction principles

- Establish clear hierarchy between page title, application identity, environment, version and status.
- Use consistent spacing, typography, buttons and form controls.
- Use status text or icons as well as colour; colour must not be the only signal.
- Make primary actions obvious and secondary actions quieter.
- Provide visible keyboard focus.
- Ensure adequate contrast.
- Use semantic headings and labels.
- Make tables usable at narrower viewport widths.
- Avoid unnecessary animation; status changes should be understandable.

## 6. Accessibility checklist

- All form controls have associated labels.
- Interactive elements are keyboard accessible.
- Focus indicator is visible.
- Text and controls have sufficient contrast.
- Status is not communicated by colour alone.
- Errors are described in text and associated with relevant fields.
- Heading levels follow a logical structure.

## 7. Angular concepts to demonstrate

- Components and templates.
- Interpolation, property binding and event binding.
- Conditional and repeated rendering.
- Reusable UI components.
- Services and dependency injection.
- Router and route parameters.
- HttpClient and typed request/response models.
- Form validation (Reactive Forms if appropriate).
- Loading, error and empty state handling.
- Separation of presentation from API communication.

## 8. Design decisions still open

See `open-questions.md` for theme, visual direction, language and demonstration-data choices. Do not assume these preferences before they are confirmed.
