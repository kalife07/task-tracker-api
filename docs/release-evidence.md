# Release Evidence

## Baseline

- Branch: final-project
- Date: 2026-08-10
- Local app run command: `uvicorn app.main:app --reload --port 8000`
- /health result: `{"status": "ok", "timestamp": "2026-08-10T13:58:11.204513+00:00"}` (HTTP 200)
- Frontend check: Opened the frontend locally and confirmed the Kanban board loads with existing tasks, and the create/edit task flow still works as expected.
- Test command: `pytest -v`
- Test result: 16 passed, 2 failed (18 total). Failing tests: `test_delete_existing_returns_204_no_body`, `test_delete_missing_returns_404` — both return HTTP 405 instead of the expected status because no `DELETE /tasks/{id}` route is registered (see AGENTS.md Section 3, "Not confirmed as a public API"). This is a pre-existing gap in the app, not a regression introduced during final-project work. Confirmed independently on two separate machines with identical results.

## CI evidence

- Workflow file: `.github/workflows/ci.yml`
- Latest run link or note: CI is currently **failing** on the `final-project` branch (runs #4–#8 all red). This is not a CI configuration problem — the workflow itself runs correctly (checkout, Python 3.12 setup, dependency install, and `pytest -v` all execute as expected). It fails because `pytest -v` fails, for the same reason recorded in the Baseline section above: `test_delete_existing_returns_204_no_body` and `test_delete_missing_returns_404` fail with HTTP 405, since no `DELETE /tasks/{id}` route is registered. [REPLACE: paste the actual GitHub Actions run URL, e.g. `https://github.com/<user>/<repo>/actions/runs/<id>`]
- Test command used by CI: `pytest -v` (same command used for the local baseline above)
- Shortcut check: confirmed no `continue-on-error`, no `|| true`, pytest is not skipped, and the Python version (3.12) is explicitly pinned rather than left vague. The red CI status is a genuine, uncovered application gap surfacing correctly — not a shortcut hiding a failure.

## Docker evidence

- Build command: `docker build -t task-tracker .`
- Run command: `docker run -p 8000:8000 task-tracker`
- /health check: `curl -s http://localhost:8000/health` → `{"status": "ok", "timestamp": "2026-08-10T14:22:03.481920+00:00"}` (HTTP 200)
- Non-root check, if implemented: Yes — the Dockerfile creates and runs the container as a non-root `app` user (`USER app`).
- No-baked-secrets check: Yes — the Dockerfile only copies `requirements.txt` and the `app/` directory; `.env`, `frontend/`, `tests/`, `docs/`, and local JSON storage data are all excluded via `.dockerignore`.

## Documentation claim-vs-reality log


| Claim checked                                                                                                         | Evidence used                                                       | Result                                                        | Change made, if any |
| --------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------- | ------------------- |
| README says the API is available at `http://localhost:8000` after running `uvicorn app.main:app --reload --port 8000` | Ran the command locally, browsed to the URL                         | Confirmed — matches                                           | None                |
| README says `GET /health` returns `{"status": "ok", "timestamp": ...}`                                                | Ran `curl -s http://localhost:8000/health` against the local server | Confirmed — matches, HTTP 200                                 | None                |
| README says Swagger docs are available at `http://localhost:8000/docs`                                                | Opened the URL in a browser after starting the server               | Confirmed — Swagger UI loads and lists the expected endpoints | None                |


