## Baseline Check
* **Objective:** Ensure existing codebase tests and initial state pass before starting feature development.
* **Environment:** Node v20.x, React v18.x, Express v4.x
* **Command:** `npm test`

```text
  GET /api/health
    ✓ returns 200 OK
  GET /tasks
    ✓ fetches existing task list
  POST /tasks
    ✓ creates task with default parameters
    
Test Suites: 3 passed, 3 total
Tests:       8 passed, 8 total
Snapshots:   0 total
Time:        1.142 s