# Task Tracker — Architecture

## 1. What the app does

Task Tracker is a learning-focused Kanban-style task API (FastAPI) with a static vanilla-JS board UI. Users create, list, view, and partially update tasks with status, priority, assignee, due date, and tags. Persistence is an in-memory dict that resets when the process restarts. Live UI: `frontend/index.html` calling `http://localhost:8000`.

## 2. Data model

**Task** (only entity). Fields: `id` (UUID string), `title`, `description`, `status` (`ToDo` | `InProgress` | `Done`), `priority` (`Low` | `Medium` | `High`), `assignee`, `due_date` (optional ISO-8601), `tags` (list), `created_at` / `updated_at` (UTC). Create defaults: status `ToDo`, priority `Medium`. `is_overdue` is computed at read time (due before today UTC and status ≠ `Done`), not stored.

## 3. Request flow (create task)

1. Client `POST /tasks` with JSON body (UI: modal in `frontend/index.html`).
2. FastAPI validates body as `TaskCreate` (Pydantic + `app/validation.py`); invalid → HTTP 422 before the handler.
3. `create_task` in `app/api/routes/tasks.py` calls `storage.add_task`.
4. Storage assigns UUID `id`, sets timestamps, stores in `_tasks`, returns `TaskResponse` (includes computed `is_overdue`) with HTTP 201.

## 4. Key files

| File | Role |
|------|------|
| `app/main.py` | FastAPI app; registers health, tasks, testing, version routers |
| `app/models.py` | Pydantic schemas (`TaskCreate` / `TaskUpdate` / `TaskResponse`) and field validators |
| `app/validation.py` | Shared due_date / tags / overdue helpers |
| `app/business_rules.py` | Allowed status transitions for PATCH |
| `app/storage.py` | In-memory CRUD (`_tasks` dict) |
| `app/task_query.py` | List filters (`status`, `priority`, `overdue`, `tag`) |
| `app/api/routes/tasks.py` | HTTP handlers for `/tasks*` |
| `app/api/routes/testing.py` | `POST /test/reset` when `APP_ENV=test` |
| `app/core/config.py` | Settings (`PORT`, `APP_ENV`) from env / `.env` |
| `frontend/index.html` | Live Kanban UI (hardcoded API base) |

## 5. Conventions

- **Validation:** Unknown fields forbidden (`extra="forbid"`). Title required, stripped, non-blank, max 200. Tags trimmed, empties dropped, max 10 × 30 chars. Due date ISO-8601 or blank → `None`.
- **Storage:** Module-level `_tasks`; no DB/file write in the inspected implementation. Status rules enforced in the PATCH route, not in `storage.update_task`.
- **Errors:** Validation / illegal transitions → 422; missing task → 404. FastAPI handles schema failures automatically.
- **Frontend/backend:** Browser `fetch` to hardcoded `API_BASE`; create via POST, updates via PATCH (including drag-and-drop status changes). React under `frontend/src/components/` is tested but not wired into `index.html`.

## 6. Not visible or assumptions

- README / FastAPI description mention “JSON file storage”; `app/storage.py` is in-memory only — file persistence not confirmed.
- `storage.delete_task` exists and some tests expect DELETE, but no `DELETE /tasks/{id}` route is registered.
- Exact supported Python minor is unclear (README says 3.12+; CI uses 3.11). `pytest` / `httpx` used in tests/CI but not listed in `requirements.txt`.
- Auth, multi-user tenancy, and durable production deployment were not inspected as present.
