const PRIORITY_CLASSES = {
  High: "chip-high",
  Medium: "chip-medium",
  Low: "chip-low",
};

const STATUS_LABELS = {
  ToDo: "To Do",
  InProgress: "In Progress",
  Done: "Done",
};

function toDateInputValue(dueDate) {
  if (!dueDate) {
    return "";
  }
  return dueDate.length >= 10 ? dueDate.slice(0, 10) : dueDate;
}

export function formatDueDateLabel(dueDate) {
  const value = toDateInputValue(dueDate);
  if (!value) {
    return "";
  }

  const parsed = new Date(`${value}T00:00:00`);
  return parsed.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

export function isTaskOverdue(task) {
  if (task.is_overdue === true) {
    return true;
  }

  if (!task.due_date || task.status === "Done") {
    return false;
  }

  const dueValue = toDateInputValue(task.due_date);
  const dueDate = new Date(`${dueValue}T00:00:00`);
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  return dueDate < today;
}

export default function TaskCard({ task, onEdit, onDragStart, onDragEnd }) {
  const overdue = isTaskOverdue(task);
  const dueDateLabel = formatDueDateLabel(task.due_date);
  const tags = Array.isArray(task.tags) ? task.tags : [];

  return (
    <article
      className="card"
      draggable
      data-task-id={task.id}
      onDragStart={onDragStart}
      onDragEnd={onDragEnd}
    >
      <div className="card-header">
        <p className={`card-chip ${PRIORITY_CLASSES[task.priority] ?? ""}`}>{task.priority}</p>
        <button className="card-action" type="button" onClick={() => onEdit(task)}>
          Edit
        </button>
      </div>

      <h3 className="card-title">{task.title}</h3>
      <p className="card-description">{task.description || ""}</p>

      {dueDateLabel ? (
        <div className="card-meta">
          <div className="card-due-row">
            <span className={`card-due-label${overdue ? " overdue" : ""}`}>
              Due {dueDateLabel}
            </span>
            {overdue ? <span className="card-overdue-badge">Overdue</span> : null}
          </div>
        </div>
      ) : null}

      {tags.length > 0 ? (
        <div className="card-tags" aria-label="Task tags">
          {tags.map((tag) => (
            <span className="card-tag" key={`${task.id}-${tag}`}>
              {tag}
            </span>
          ))}
        </div>
      ) : null}

      <div className="card-footer">
        <span className="card-footer-tag">{task.assignee || "Unassigned"}</span>
        <span className="card-footer-tag">{STATUS_LABELS[task.status] ?? task.status}</span>
      </div>
    </article>
  );
}
