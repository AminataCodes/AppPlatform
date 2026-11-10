# AppPlatform — Learning Objectives for the Interview

The project should be a learning artifact, not just generated code. Be able to explain the following concepts in your own words.

## 1. Frontend and Angular

- What is a component, and why split a page into components?
- What is the difference between interpolation, property binding and event binding?
- What are Angular services and dependency injection?
- Why use Angular routing?
- How does HttpClient communicate with a backend?
- How should loading, error, empty and success states be represented?
- How should a form validate user input?
- How do accessibility and responsive design affect implementation choices?

## 2. UI/UX

- Who is the user and what task are they trying to complete?
- Why is the information architecture organized this way?
- Which information needs the strongest visual hierarchy?
- How does the interface prevent accidental production deployment?
- How does the user know an operation is in progress or has failed?
- How are keyboard users and users who cannot distinguish colours supported?

## 3. Backend and API

- What is an API?
- What is REST, and why is it not a programming language?
- What do GET and POST mean in this project?
- What does FastAPI validate?
- Why must business rules be enforced by the backend?
- What is the difference between an HTTP request and a database query?

## 4. Platform and automation

- What is an application in an operations/platform context?
- Why can one application have several environments?
- What is a deployment?
- What do QUEUED, RUNNING, SUCCEEDED and FAILED represent?
- Why are logs and execution history useful?
- What would a real deployment engine replace in this prototype?
- What are Docker, Jenkins, Ansible and OpenShift used for?

## 5. End-to-end explanation

Be able to explain this sequence:

1. User submits an Angular form.
2. Angular service sends an HTTP request.
3. FastAPI receives and validates it.
4. Backend business logic creates an execution.
5. Simulation service processes the steps.
6. SQLite stores execution state and logs.
7. Angular retrieves and displays the result.

## 6. Minimum interview readiness

- [ ] Explain the purpose and limits of AppPlatform.
- [ ] Draw the architecture without looking at the README.
- [ ] Explain one complete deployment request.
- [ ] Explain why backend validation is necessary.
- [ ] Explain what happens on failure.
- [ ] Explain the main Angular components and services.
- [ ] Explain how the UI handles loading and errors.
- [ ] Explain what is simulated and what is actually implemented.
