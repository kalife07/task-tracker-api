import { useEffect, useState } from "react";

import TagInput from "./TagInput";

const STATUS_OPTIONS = ["ToDo", "InProgress", "Done"];
const PRIORITY_OPTIONS = ["High", "Medium", "Low"];
const STATUS_LABELS = {
  ToDo: "To Do",
  InProgress: "In Progress",
  Done: "Done",
};

const EMPTY_FORM = {
  title: "",
  description: "",
  assignee: "",
  status: "ToDo",
  priority: "Medium",
  due_date: "",
  tags: [],
};

function toDateInputValue(dueDate) {
  if (!dueDate) {
    return "";
  }
  return dueDate.length >= 10 ? dueDate.slice(0, 10) : dueDate;
}

export default function TaskModal({ isOpen, mode = "create", task = null, onClose, onSave }) {
  const [form, setForm] = useState(EMPTY_FORM);
  const [formError, setFormError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (!isOpen) {
      return;
    }

    if (mode === "edit" && task) {
      setForm({
        title: task.title ?? "",
        description: task.description ?? "",
        assignee: task.assignee ?? "",
        status: task.status ?? "ToDo",
        priority: task.priority ?? "Medium",
        due_date: toDateInputValue(task.due_date),
        tags: Array.isArray(task.tags) ? [...task.tags] : [],
      });
    } else {
      setForm(EMPTY_FORM);
    }

    setFormError("");
  }, [isOpen, mode, task]);

  if (!isOpen) {
    return null;
  }

  function updateField(field, value) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  function buildPayload() {
    const title = form.title.trim();
    if (!title) {
      throw new Error("Title is required");
    }

    const payload = {
      title,
      description: form.description.trim(),
      assignee: form.assignee.trim() || null,
      status: form.status,
      priority: form.priority,
      tags: form.tags,
    };

    if (form.due_date) {
      payload.due_date = form.due_date;
    } else if (mode === "edit") {
      payload.due_date = null;
    }

    return payload;
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setFormError("");

    let payload;
    try {
      payload = buildPayload();
    } catch (error) {
      setFormError(error.message);
      return;
    }

    setIsSubmitting(true);
    try {
      await onSave(payload, { mode, taskId: task?.id ?? null });
      onClose();
    } catch (error) {
      setFormError(error.message || "Unable to save task.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="modal-backdrop active" onClick={onClose}>
      <section
        className="modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="modalTitle"
        onClick={(event) => event.stopPropagation()}
      >
        <div className="modal-header">
          <h3 id="modalTitle">{mode === "create" ? "New task" : "Edit task"}</h3>
          <button type="button" className="modal-close" aria-label="Close modal" onClick={onClose}>
            ×
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="field">
            <label htmlFor="titleInput">Title</label>
            <input
              id="titleInput"
              type="text"
              value={form.title}
              maxLength={200}
              required
              autoComplete="off"
              onChange={(event) => updateField("title", event.target.value)}
            />
          </div>

          <div className="field">
            <label htmlFor="descriptionInput">Description</label>
            <textarea
              id="descriptionInput"
              value={form.description}
              onChange={(event) => updateField("description", event.target.value)}
            />
          </div>

          <div className="field">
            <label htmlFor="assigneeInput">Assignee</label>
            <input
              id="assigneeInput"
              type="text"
              value={form.assignee}
              autoComplete="off"
              onChange={(event) => updateField("assignee", event.target.value)}
            />
          </div>

          <div className="field">
            <label htmlFor="dueDateInput">Due date</label>
            <div className="due-date-row">
              <input
                id="dueDateInput"
                type="date"
                value={form.due_date}
                onChange={(event) => updateField("due_date", event.target.value)}
              />
              {form.due_date ? (
                <button
                  type="button"
                  className="button cancel due-date-clear"
                  onClick={() => updateField("due_date", "")}
                >
                  Clear
                </button>
              ) : null}
            </div>
          </div>

          <div className="field">
            <label htmlFor="tagsInput">Tags</label>
            <TagInput
              tags={form.tags}
              onChange={(nextTags) => updateField("tags", nextTags)}
              disabled={isSubmitting}
            />
          </div>

          <div className="field">
            <label htmlFor="statusSelect">Status</label>
            <select
              id="statusSelect"
              value={form.status}
              onChange={(event) => updateField("status", event.target.value)}
            >
              {STATUS_OPTIONS.map((status) => (
                <option key={status} value={status}>
                  {STATUS_LABELS[status]}
                </option>
              ))}
            </select>
          </div>

          <div className="field">
            <label htmlFor="prioritySelect">Priority</label>
            <select
              id="prioritySelect"
              value={form.priority}
              onChange={(event) => updateField("priority", event.target.value)}
            >
              {PRIORITY_OPTIONS.map((priority) => (
                <option key={priority} value={priority}>
                  {priority}
                </option>
              ))}
            </select>
          </div>

          {formError ? (
            <p className="error-text" role="alert">
              {formError}
            </p>
          ) : null}

          <div className="actions">
            <button type="button" className="button cancel" onClick={onClose} disabled={isSubmitting}>
              Cancel
            </button>
            <button type="submit" className="button" disabled={isSubmitting}>
              {isSubmitting ? "Saving..." : "Save task"}
            </button>
          </div>
        </form>
      </section>
    </div>
  );
}
