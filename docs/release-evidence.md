# Release Evidence

## Baseline

- Branch: final-project
- Date: 2026-08-10
- Local app run command: `uvicorn app.main:app --reload --port 8000`
- /health result: `{"status": "ok", "timestamp": "2026-08-10T13:58:11.204513+00:00"}` (HTTP 200)
- Frontend check: Opened the frontend locally and confirmed the Kanban board loads with existing tasks, and the create/edit task flow still works as expected.
- Test command: `pytest -v`
- Test result: 18 passed, 0 failed. Re-run after adding the `DELETE /tasks/{task_id}` route to `app/api/routes/tasks.py`; both previously-failing tests (`test_delete_existing_returns_204_no_body`, `test_delete_missing_returns_404`) now pass. Verified locally on 2026-08-14 after resolving an unrelated `ImportPathMismatchError` caused by a duplicated nested project folder — not a code or test issue.

## CI evidence

- Workflow file: `.github/workflows/ci.yml`
- Latest run link or note: **Confirmed green.** CI #13 ("Delete .env", commit `a03efff`) passed on the `final-project` branch in 17s, visible in the repo's Actions tab (`kalife07/task-tracker-api`, all workflow runs). This run includes both fixes: the `DELETE /tasks/{id}` route (`app/api/routes/tasks.py`) and the missing `pytest`/`httpx` entries in `requirements.txt` (CI #11, "fixed requirements", also green — the earlier CI #10, "fixed pytest", had failed with `pytest: command not found` before that fix). [REPLACE: paste the exact GitHub Actions run URL for CI #13 from the browser address bar]
- Test command used by CI: `pytest -v` (same command used for the local baseline above)
- Shortcut check: confirmed no `continue-on-error`, no `|| true`, pytest is not skipped, and the Python version (3.12) is explicitly pinned rather than left vague.

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
