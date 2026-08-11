# [AGENTS.md](http://AGENTS.md)

Guidance for AI coding agents working in the Task Tracker repository.

## 1. Project summary

Task Tracker is a learning-focused REST API (FastAPI / Python) for Kanban-style tasks, plus a static vanilla-JS board UI.

- API entry: `app/main.py` (`uvicorn app.main:app`).
- Persistence: in-memory dict in `app/storage.py` (`_tasks`). Data resets when the process restarts.
- Note: `README.md` and the FastAPI `description` in `app/main.py` mention "JSON file storage"; the inspected implementation in `app/storage.py` is in-memory, not a JSON file store.
- Live frontend: open `frontend/index.html` (hardcoded `API_BASE = 'http://localhost:8000'`).
- React components under `frontend/src/components/` exist with Jest tests; they are not wired into `index.html` (treat as in-progress, not the live UI).
- Test-only reset: `POST /test/reset` in `app/api/routes/testing.py` works only when `APP_ENV=test` (otherwise 404).

## 2. Tech stack and supported commands

### Stack (from inspected files)


| Layer                                                                     | Confirmed from                                                     |
| ------------------------------------------------------------------------- | ------------------------------------------------------------------ |
| Python / FastAPI / Uvicorn / Pydantic / pydantic-settings / python-dotenv | `requirements.txt`, `app/main.py`                                  |
| In-memory task store                                                      | `app/storage.py`                                                   |
| Jest + Supertest (API black-box)                                          | `package.json`, `tests/*.test.js`, `tests/globalSetup.js`          |
| Jest + Testing Library + jsdom (frontend components)                      | `package.json`, `frontend/**/*.test.jsx`                           |
| Pytest + FastAPI `TestClient`                                             | `tests/conftest.py`, `tests/test_*.py`, `.github/workflows/ci.yml` |
| Env config (`PORT`, `APP_ENV`)                                            | `.env.example`, `app/core/config.py`                               |


**Not confirmed as declared dependencies:** `pytest` and `httpx` are used by Python tests / CI but are **not** listed in `requirements.txt`. Local `pytest` success depends on an environment that has them installed.

**Version note:** `README.md` requires Python 3.12+, and `.github/workflows/ci.yml` is pinned to Python 3.12 — these are now consistent as of the final-project branch.

### Setup / run (documented and consistent with layout)

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
npm install
uvicorn app.main:app --reload --port 8000

```

- API: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`
- Health check (README): `GET /health`

### Tests (scripts present in repo)

```powershell
npm test              # Jest api + frontend projects, --runInBand
npm run test:api      # tests/**/*.test.js (spawns uvicorn with APP_ENV=test)
npm run test:frontend # frontend/**/*.test.jsx
npm run test:watch
pytest -v            # used in CI (.github/workflows/ci.yml) and locally per README; deps not in requirements.txt

```

Jest API tests spawn a real server (`tests/globalSetup.js`) and reset via `POST /test/reset`. Do not rely on `/test/reset` against a normal development server.

## 3. Business rules visible in code

### Statuses (`app/models.py`)

- `ToDo`, `InProgress`, `Done`
- Create default: `ToDo`

### Priorities (`app/models.py`)

- `Low`, `Medium`, `High`
- Create default: `Medium`

### Allowed status transitions (`app/business_rules.py`, enforced in `PATCH /tasks/{id}` in `app/api/routes/tasks.py`)

- `ToDo` → `InProgress`
- `InProgress` → `Done`
- `Done` → `InProgress`
- Other transitions (including `ToDo` → `Done` and same-status) → HTTP 422
- Not enforced inside `storage.update_task`

### Validation (`app/models.py`, `app/validation.py`)

- Unknown fields forbidden on create/update (`extra="forbid"`).
- `title`: required on create; strip whitespace; non-blank; max 200 characters.
- `due_date`: optional; ISO-8601 `YYYY-MM-DD` or full timestamp (`Z` allowed); blank → `None`.
- `tags`: trim; drop empties; max 10 tags; max 30 chars each.
- `is_overdue`: computed at read time — due date before today (UTC) and status ≠ `Done`; not stored.

### List filters (`GET /tasks` — `app/api/routes/tasks.py`, `app/task_query.py`)

- Query params: `status`, `priority`, `overdue`, `tag` (AND semantics).
- `overdue=true` keeps overdue tasks only; `overdue=false` is treated like omitting the filter.
- `tag`: exact match, case-insensitive (not substring).

### Confirmed HTTP surface (from routers)

- `GET /health`
- `GET /version`
- `POST /tasks`, `GET /tasks`, `GET /tasks/{id}`, `PATCH /tasks/{id}`
- `POST /test/reset` (test env only; hidden from OpenAPI schema)

### Not confirmed as a public API

- `DELETE /tasks/{id}`: `storage.delete_task` exists, and `tests/test_tasks.py` expects DELETE behavior, but **no delete route** is registered in `app/api/routes/tasks.py`. Do not claim DELETE is supported unless a route is added and verified.

## 4. Module 5 guardrails

This module is about grading and governing AI-assisted work, not building new product features by default.

- Prefer **read-only analysis** first.
- Edit `docs/` **only**, unless the human explicitly approves a different path.
- Do **not** modify `app/` unless the human asks for one specific minimal fix.
- Use **one bounded task per thread**.
- When making claims about the repo, **cite files actually inspected**.
- If uncertain or a file is not visible, say so — **do not invent findings**.

## 5. Final project guardrails (docs-first / read-first)

- **Read before writing.** Before proposing or making any change, read `README.md`, this file (`AGENTS.md`), and the relevant file(s) under `docs/` first. Do not assume repo state from memory or from a prior session.
- **Branch:** all final-project work happens on `final-project`. Do not commit directly to `main`.
- **No new product features.** Do not add comments, authentication, a production database, notifications, or unrelated UI changes.
- `app/` **and** `frontend/` **are protected.** Only touch these for a small, explainable bug fix, security fix, or documentation-supported correction — and log the reason in `docs/final-ai-review.md`.
- **One bounded task per thread**, same as Module 5.
- **Cite files actually inspected** when making claims about the repo; do not invent findings, test results, or business rules that weren't verified.

## 6. Security and governance reminders

- Do not paste, commit, or expose secrets (`.env`, tokens, credentials) or real personal/customer data. Use `.env.example` as the safe template.
- Do not run destructive or irreversible git/system commands unless explicitly requested.
- Do not invent test results, business rules, or "findings" that were not verified in the repo.
- Prefer citing concrete paths (for example `app/business_rules.py`) over memory or assumptions.
- Keep changes minimal and task-scoped; do not refactor unrelated code during final-project work.

