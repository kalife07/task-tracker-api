# Task Tracker — Architecture

## 1. What the app does

Task Tracker is a learning-focused REST API (FastAPI / Python) for Kanban-style tasks, plus a static vanilla-JS board UI. Users create, list, get, and partially update tasks. Persistence is an in-memory dict in `app/storage.py` (`_tasks`); data resets when the process restarts. The live UI is `frontend/index.html` with hardcoded `API_BASE = 'http://localhost:8000'`.

## 2. Data model

**Task** is the only domain entity. Important fields (from `app/models.py` / AGENTS.md): `id`, `title`, `description`, `status` (`ToDo` | `InProgress` | `Done`), `priority` (`Low` | `Medium` | `High`), `assignee`, `due_date`, `tags`, `created_at`, `updated_at`. Create defaults: status `ToDo`, priority `Medium`. `is_overdue` is computed at read time (due date before today UTC and status ≠ `Done`); it is not stored.

## 3. Request flow (create task)

1. Client sends `POST /tasks` with a JSON body (`frontend/index.html` uses `fetch` to `${API_BASE}/tasks`).
2. FastAPI binds/validates the body as `TaskCreate` (`app/models.py`, helpers in `app/validation.py`). Invalid payloads never reach the handler (HTTP 422).
3. `create_task` in `app/api/routes/tasks.py` calls `storage.add_task`.
4. `add_task` generates a UUID `id`, sets UTC timestamps, stores the task in `_tasks`, and returns `TaskResponse` with HTTP 201.

## 4. Key files

| File | Role |
|------|------|
| `app/main.py` | FastAPI entry; registers health, tasks, testing, version routers |
| `app/models.py` | Task schemas and field validators |
| `app/validation.py` | Shared due_date, tags, and overdue helpers |
| `app/business_rules.py` | Allowed status transitions for PATCH |
| `app/storage.py` | In-memory task store (`_tasks`) |
| `app/task_query.py` | List filter predicates for `GET /tasks` |
| `app/api/routes/tasks.py` | `/tasks` HTTP handlers |
| `app/api/routes/testing.py` | `POST /test/reset` when `APP_ENV=test` |
| `app/core/config.py` | `PORT` / `APP_ENV` settings |
| `frontend/index.html` | Live board UI |

## 5. Conventions

- **Validation:** `extra="forbid"` on create/update. Title: required on create, stripped, non-blank, max 200. Due date: optional ISO-8601 (`YYYY-MM-DD` or timestamp with `Z`); blank → `None`. Tags: trim, drop empties, max 10 tags, max 30 chars each.
- **Storage:** In-memory only in the inspected implementation. Status-transition rules are enforced in the PATCH route, not in `storage.update_task`.
- **Error handling:** Schema/validation failures and illegal status transitions → 422; missing task on get/update → 404. `/test/reset` returns 404 unless `APP_ENV=test`.
- **Frontend/backend:** Live UI talks to the API over HTTP with hardcoded base URL; create uses POST, edits use PATCH. React components under `frontend/src/components/` are not wired into `index.html`.

## 6. Not visible or assumptions

- README / FastAPI `description` mention JSON file storage; inspected `app/storage.py` is in-memory only.
- `storage.delete_task` exists and tests expect DELETE, but no `DELETE /tasks/{id}` route is registered.
- Exact Python minor version is not fully confirmed (README 3.12+ vs CI 3.11). `pytest` / `httpx` are used in tests/CI but not listed in `requirements.txt`.
- Auth, multi-tenancy, and durable production deployment are not described as present in AGENTS.md or the inspected app files.
