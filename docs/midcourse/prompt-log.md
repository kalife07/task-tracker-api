## Feature 1: Due Dates + Overdue Filter

### Prompt 1.1 (Planning & Architecture)
* **Prompt:**
  > "I need to add a due date feature to my Task Tracker. The backend uses Express/Node and the frontend is React. Help me plan the schema changes and API design for adding `due_date`. Should the overdue status be calculated on the backend dynamically or stored in the database? Give me a concise breakdown of pros/cons."
* **AI Output Summary:** Suggested adding an optional ISO date string field `due_date` to the Task schema. Recommended calculating `isOverdue` dynamically on the fly during backend query / UI render rather than persisting it, as hardcoding `isOverdue` in DB creates stale state issues.
* **Evaluation:**
  * **Accepted:** Dynamic computation of overdue state to avoid stale database values.
  * **Edited:** Standardized all backend date validation to ISO 8601 strings UTC.

---

### Prompt 1.2 (Weak Prompt Rewritten into Stronger Prompt)
* **Weak Version (Original):**
  > "add date picker to my modal"
* **Strong Version (Rewritten):**
  > "Create a React date-picker component inside `TaskModal.jsx` for the `due_date` field. Ensure it validates that dates cannot be set before today's date for new tasks, updates local state, and styles overdue cards with a red badge pill on the Kanban view if `due_date < current_date` and task status is not 'DONE'."
* **AI Output Summary:** Provided the updated JSX code for `TaskModal.jsx` with HTML5 `<input type="date">`, dynamic state handlers, and a reusable `OverdueBadge` badge component for the Kanban card display.
* **Evaluation:**
  * **Accepted:** The `OverdueBadge` UI component and CSS classes.
  * **Edited:** Replaced native `<input type="date">` styles with the app's existing UI library styles for visual consistency.
  * **Rejected:** The restriction blocking past dates on task creation (users needed ability to backdate existing completed work).

---

### Prompt 1.3 (Backend Validation & Edge Cases)
* **Prompt:**
  > "Write express validator logic and controller handlers for `POST /tasks` and `PUT /tasks/:id` to support `due_date`. Handle invalid date formats, null/empty values (since due date is optional), and add a filter query parameter `GET /tasks?overdue=true`."
* **AI Output Summary:** Returned Express middleware checks for `isISO8601()`, controller code handling nullable inputs, and a query filter for filtering tasks where `due_date < NOW()` and `status != 'DONE'`.
* **Evaluation:**
  * **Accepted:** The Express controller logic and ISO validation rules.
  * **Edited:** Adjusted timezone edge case handling to ensure end-of-day (23:59:59) comparison rather than strict midnight comparison.

---

## Feature 2: Tags / Labels

### Prompt 2.1 (Weak Prompt Rewritten into Stronger Prompt)
* **Weak Version (Original):**
  > "how to add tags to tasks"
* **Strong Version (Rewritten):**
  > "Design the backend validation and frontend UI strategy for adding tags to a task. On the backend, tags should be an array of strings (max 5 tags per task, max 15 chars per tag, trimmed, no duplicates). On the frontend, show them as styled chips on Kanban cards and provide a multi-select filter above the board."
* **AI Output Summary:** Provided backend validation array schema, trimming utility functions, UI chip component styling using flexbox, and a state management snippet for tag-based filtering on the main board.
* **Evaluation:**
  * **Accepted:** Array validation rules, duplicate tag sanitization, and Tag Chip rendering logic.
  * **Edited:** Reduced max tag length from 15 characters to 12 characters to prevent cards from overflowing visually.

---

### Prompt 2.2 (Implementation - Tag Input Component)
* **Prompt:**
  > "Write a React `TagInput` component for our Task Modal. Users should be able to type a tag, hit 'Enter' or comma to add it, and click an 'x' button on a chip to remove it. Validate max 5 tags inline and display a helpful error message if exceeded."
* **AI Output Summary:** Generated a self-contained `TagInput.jsx` component using React state, keydown listener for 'Enter'/'Comma', and an inline error text banner.
* **Evaluation:**
  * **Accepted:** Keydown listener logic and tag chip rendering.
  * **Edited:** Fixed a bug where hitting 'Enter' submitted the entire modal form instead of just adding the tag chip.

---

### Prompt 2.3 (Testing & Refactoring)
* **Prompt:**
  > "Write 3 Jest/React Testing Library test cases for the `TagInput` component: 1) adding a valid tag, 2) preventing duplicate tags, and 3) enforcing the maximum limit of 5 tags."
* **AI Output Summary:** Produced complete unit test cases checking user events (`userEvent.type`, `userEvent.keyboard('{Enter}')`) and asserting DOM elements and validation message presence.
* **Evaluation:**
  * **Accepted:** Tests 1 and 3 without modifications.
  * **Edited:** Updated Test 2 assertion to match the exact error notification text used in our app UI.