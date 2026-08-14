# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A learning-focused REST API (FastAPI, Python) for tracking tasks on a Kanban-style board, backed by **in-memory storage** (not a database, despite the `app/storage.py` name — `_tasks` is a plain dict that resets on process restart). There is a standalone vanilla-JS frontend (`frontend/index.html`) that talks to the API directly, plus a set of React components under `frontend/src/components/` that are unit-tested with Jest but are **not currently wired into `index.html`** — treat them as an in-progress port, not the live UI.

## Setup

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
npm install
```

## Running the app

```powershell
uvicorn app.main:app --reload --port 8000
```

API at `http://localhost:8000`, Swagger UI at `http://localhost:8000/docs`. The frontend is a static file — open `frontend/index.html` directly in a browser (it calls the API at `http://localhost:8000` via a hardcoded `API_BASE`).

## Tests

Two independent suites, both run through Jest via `package.json`, plus the underlying pytest suite:

```powershell
npm test                # everything (api + frontend jest projects), --runInBand
npm run test:api        # tests/*.test.js — black-box HTTP tests against a real running server
npm run test:frontend   # frontend/**/*.test.jsx — React component tests (jsdom)
npm run test:watch
```

- `test:api` uses `tests/globalSetup.js` / `globalTeardown.js`, which **spawn a real `uvicorn` process** (via `venv/Scripts/python.exe` if present, else `python`) with `APP_ENV=test`, wait for `/health`, and kill it after the run. It talks to the server over HTTP with `supertest`, not by importing the app.
- Each JS test calls `POST /test/reset` in `beforeEach`/`afterEach` to clear task storage between tests. That route (`app/api/routes/testing.py`) only works when `APP_ENV=test` — returns 404 otherwise. Never rely on it against a dev/prod server.
- Python tests run directly against the FastAPI app with `TestClient` (no server process):
  ```powershell
  pytest
  pytest tests/test_tasks.py::test_create_task_valid_returns_201_with_full_body
  ```
  `tests/conftest.py` has an autouse fixture that calls `storage._reset()` before/after every test, plus `client` and `created_task` fixtures.
- To run a single JS test: `npx jest -t "test name"` or `npx jest tests/tasks.test.js`.

## Architecture

Request flow: `app/api/routes/*.py` (FastAPI routers, registered in `app/main.py`) → `app/storage.py` (in-memory CRUD) → `app/task_query.py` (filter predicates for `GET /tasks`) and `app/business_rules.py` (status-transition rules), with cross-cutting field validation in `app/validation.py` used from Pydantic validators in `app/models.py`.

- **`app/models.py`** — the Pydantic schemas (`TaskCreate`, `TaskUpdate`, `TaskResponse`) *and* validation. `TaskCreate`/`TaskUpdate` reject unknown fields (`extra="forbid"`). `TaskResponse.is_overdue` is a `@computed_field`, derived at read time, not stored — there is no background job or stored overdue flag by design (see `docs/midcourse/mini-adr.md`).
- **`app/validation.py`** — free functions for `due_date` (ISO-8601, `YYYY-MM-DD` or full timestamp) and `tags` (trim, drop empties, max 10 tags, max 30 chars each — `MAX_TAGS_PER_TASK` / `MAX_TAG_LENGTH`) normalization, plus `is_task_overdue`, shared by both `models.py` and `task_query.py`.
- **`app/business_rules.py`** — `VALID_TRANSITIONS` is the only allowed status graph: `ToDo→InProgress`, `InProgress→Done`, `Done→InProgress`. Any other transition (including skipping straight `ToDo→Done`) raises 422. Enforced only in the `PATCH /tasks/{id}` route, not in `storage.update_task`.
- **`app/task_query.py`** — `TaskQueryFilters` dataclass + predicate builder for `GET /tasks?status=&priority=&overdue=&tag=`. Tag filtering is exact-match, case-insensitive (not substring/fuzzy — rejected by design, see mini-adr).
- **`app/storage.py`** — module-level `_tasks` dict is the entire persistence layer. `_reset()` is test-only plumbing, exposed over HTTP by `app/api/routes/testing.py` when `APP_ENV=test`.
- **`app/core/config.py`** — `Settings` (pydantic-settings) reads `.env` / process env; `port`, `app_env`. Import the shared `settings` instance rather than constructing a new one.
- **Route split**: `health.py` (`/health`), `tasks.py` (`/tasks*`), `testing.py` (`/test/reset`, hidden from OpenAPI via `include_in_schema=False`). Add new resources as a new module under `app/api/routes/` and register the router in `app/main.py`.

### Frontend

- `frontend/index.html` is a single self-contained file: inline `<style>` + inline `<script>` vanilla JS Kanban board (drag-and-drop between status columns, task modal, tag/overdue filtering). It duplicates logic (date formatting, overdue calc, tag collection) that also exists in the React components — when changing task-card/filter behavior, check whether both need updating.
- `frontend/src/components/*.jsx` — React ports of the same pieces (`TaskCard`, `TaskModal`, `TagInput`, `BoardToolbar`), covered by colocated `*.test.jsx` files under `testing-library/react` + jsdom. No app entry point wires these together yet.
