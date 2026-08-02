## 1. Feature 1: Due Dates & Overdue Filter

### Final Implementation Approach
* **Backend:** Stored `due_date` as an optional UTC ISO-8601 string field (`YYYY-MM-DD`) on the task model with validation on `POST /tasks` and `PATCH /tasks/{id}`. The backend dynamically evaluates the `is_overdue` state during query execution (`GET /tasks?overdue=true`) by comparing `due_date < CURRENT_DATE` where `status != 'DONE'`.
* **Frontend:** Integrated an HTML5 date input inside `TaskModal.jsx`. Cards render a human-readable date tag (e.g., "Due Apr 15, 2026") alongside a dynamic red pill indicator for overdue items.

### AI Alternatives Suggested
1. **Database Persistence of Overdue Flag:** AI initially suggested storing a boolean `is_overdue` column directly in the database table and updating it via a nightly background cron job or scheduled worker process.
2. **Strict Future-Date Validation:** AI suggested adding backend validation to reject any incoming `due_date` values prior to the current timestamp.

### Rejected Suggestions & Trade-Off Reasons
* **Rejected Stored Overdue State:** Storing `is_overdue` in the database introduces a risk of state staleness (a task becoming overdue at midnight without a database update). Computing `is_overdue` dynamically at query time or in UI display logic ensures data integrity without relying on background cron jobs, keeping the deployment simple and maintenance-free.
* **Rejected Strict Creation Date Restrictions:** Blocking past date inputs prevents users from logging tasks historically or backdating work already in progress.

---

## 2. Feature 2: Tags / Labels

### Final Implementation Approach
* **Backend:** Modelled tags as a list of trimmed strings stored on the task document. Input arrays are sanitized by stripping whitespace, removing empty strings, and enforcing duplicate removal. API limits are enforced at a maximum of 10 tags per task and 30 characters per tag.
* **Frontend:** Created a dedicated `TagInput.jsx` control supporting chip creation via comma/enter keys and removal via chip buttons. Cards display individual styled badges, and the top toolbar features a multi-select filter dropdown for tag filtering (`GET /tasks?tag=name`).

### AI Alternatives Suggested
1. **Normalized Database Relation / Separate Tag Table:** AI suggested building a dedicated relational `tags` table with a join table (`task_tags`) for full normalization and referential integrity.
2. **Fuzzy Text Search Integration:** AI suggested using full-text database indexing to search tags, titles, and descriptions simultaneously via a single search endpoint.

### Rejected Suggestions & Trade-Off Reasons
* **Rejected Separate Tag Table:** Creating a join table and separate foreign key relationships adds overhead (complex joins, migration management) that is excessive for an array of simple string labels. Storing tags as an inline list directly on the task payload satisfies all requirements while maintaining fast read/write operations.
* **Rejected Fuzzy Search Engine:** Introducing full-text search across arbitrary fields exceeds the scope of exact tag filtering. Sticking to exact, case-insensitive string matching (`GET /tasks?tag=bug`) leverages existing query parameter patterns and prevents unnecessary indexing complexity.