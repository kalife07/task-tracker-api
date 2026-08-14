## Story 1: Set and Update Task Due Dates

> **Module:** Core Task Management  
> **Status:** `Ready for Development`  
> **Dependencies:** None

### User Story Statement
> **As a** team member,  
> **I want to** set an optional due date when creating or editing a task,  
> **So that** I can plan work against deadlines.

### Acceptance Criteria
* **AC 1 (UI Form Load):** Given I open the create or edit task modal, when the form loads, then I see an optional due date field (date picker or date input).
* **AC 2 (Optional Field Handling):** Given I leave the due date empty, when I save the task, then the task is created/updated successfully with no due date.
* **AC 3 (Persistence & API):** Given I select a valid date, when I save, then the task is persisted via `POST /tasks` or `PATCH /tasks/{id}` and returned in the response with `due_date`.
* **AC 4 (Validation Error Handling):** Given I submit an invalid due date (malformed or unparsable), when the API validates the payload, then it returns `422 Unprocessable Entity` with a clear validation error.
* **AC 5 (Kanban Display):** Given a task has a due date, when the task card renders on the Kanban board, then the due date is shown in a readable format (e.g., `"Due Apr 15, 2026"`).
* **AC 6 (Removal Handling):** Given I clear the due date on edit and save, when the update succeeds, then the task’s `due_date` is removed/set to `null` and the card no longer shows a due date.

> **Scope Note:** Covers the `due_date` field end-to-end (model, create/update validation, modal input, card display). Does **not** include overdue styling or filtering — those are covered in **Story 2**.

---

## Story 2: Identify and Filter Overdue Tasks

> **Module:** Filters & Visual Indicators  
> **Status:** `Ready for Development`  
> **Dependencies:** Story 1

### User Story Statement
> **As a** team member,  
> **I want to** see which tasks are overdue and filter the board to show only them,  
> **So that** I can focus on work that needs immediate attention.

### Acceptance Criteria
* **AC 1 (Overdue Calculation - True):** Given a task has a `due_date` before today and `status != Done`, when overdue status is computed (API or shared rule), then the task is marked as overdue.
* **AC 2 (Overdue Calculation - False):** Given a task has no due date, or its due date is today or in the future, when overdue status is computed, then the task is not overdue.
* **AC 3 (Done Exception):** Given a task is `Done`, when its due date is in the past, then it is **not** treated as overdue.
* **AC 4 (Visual Indicator):** Given a task is overdue, when its card renders, then it shows a visible overdue indicator (e.g., a red `"Overdue"` pill or highlighted due date text).
* **AC 5 (UI Filter):** Given I am on the board, when I enable an `"Overdue only"` filter control, then only overdue tasks are shown across all columns; non-overdue tasks are hidden.
* **AC 6 (Filter Reset):** Given the overdue filter is active, when I disable it, then all tasks are shown again.
* **AC 7 (API Query Parameter):** Given `GET /tasks?overdue=true` (or equivalent), when the API responds, then only tasks matching the overdue rules above are returned; existing filters (e.g., status, priority) still compose correctly when combined.

> **Scope Note:** Focused on overdue logic, visual indicators, and filter UI/API. Assumes Story 1’s `due_date` field exists. Keeps computation in one place (backend helper or shared rule) so frontend and API stay consistent.

---

## Story 3: Add Tags to Tasks

> **Module:** Core Task Management  
> **Status:** `Ready for Development`  
> **Dependencies:** None

### User Story Statement
> **As a** team member,  
> **I want to** add one or more tags when creating or editing a task,  
> **So that** I can categorize work and find related tasks later.

### Acceptance Criteria
* **AC 1 (UI Form Load):** Given I open the create or edit task modal, when the form loads, then I see a tags input (e.g., comma-separated text or chip-style input).
* **AC 2 (Sanitization & Storage):** Given I enter tags like `" frontend, bug "`, when I save, then tags are trimmed, empty segments are dropped, and stored as a list (or normalized comma-separated string) on the task.
* **AC 3 (Validation Restrictions):** Given I submit more tags than the allowed maximum (e.g., `> 10`) or a tag longer than the max length (e.g., `> 30 chars`), when the API validates, then it returns `422 Unprocessable Entity` with a clear error message.
* **AC 4 (API Schema):** Given I save a task with valid tags, when the API responds, then `tags` is included on `TaskResponse` for create, update, and list endpoints.
* **AC 5 (Kanban Rendering):** Given a task has tags, when its card renders, then each tag appears as a small chip/badge on the card.
* **AC 6 (Clear Tags):** Given I remove all tags on edit and save, when the update succeeds, then the task has an empty tags list and no chips are shown on the card.

> **Scope Note:** Covers tag storage, validation, modal input, and card rendering. Does **not** include tag-based filtering — that is covered in **Story 4**. Pick one storage approach (list in Pydantic vs. normalized string in storage) and stick to it for this story.

---

## Story 4: Filter Tasks by Tag

> **Module:** Filters & Visual Indicators  
> **Status:** `Ready for Development`  
> **Dependencies:** Story 3

### User Story Statement
> **As a** team member,  
> **I want to** filter the board by a specific tag,  
> **So that** I can view only tasks related to a specific topic or workstream.

### Acceptance Criteria
* **AC 1 (API Exact Match):** Given tasks exist with various tags, when I call `GET /tasks?tag=bug` (exact match, case-insensitive), then only tasks whose tags include `"bug"` are returned.
* **AC 2 (Empty Result Handling):** Given no tasks match the requested tag, when I filter, then the API returns an empty list and the board shows no matching cards.
* **AC 3 (UI Tag Picker):** Given I am on the board, when I open a tag filter control (dropdown, chip list, or search field), then I see available tags derived from current tasks (deduplicated and sorted).
* **AC 4 (Apply Filter UI):** Given I select a tag in the filter UI, when the filter applies, then only tasks with that tag are shown on the board; the active filter state is clearly indicated.
* **AC 5 (Reset Filter UI):** Given a tag filter is active, when I clear it, then all tasks are shown again.
* **AC 6 (Filter Composition):** Given a tag filter is combined with other filters (e.g., `overdue=true`, `status=IN_PROGRESS`), when both are active, then only tasks matching **all** active criteria are shown.

> **Scope Note:** Assumes Story 3’s `tags` exist on tasks. Reuses the existing query-param filter pattern (status, priority). Keeps "search" as an exact tag match for this story; free-text search across title/description can be a separate story later.