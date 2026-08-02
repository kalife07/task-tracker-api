export default function BoardToolbar({
  overdueOnly,
  selectedTag,
  availableTags,
  onOverdueChange,
  onTagChange,
  onClearFilters,
}) {
  const hasActiveFilters = overdueOnly || Boolean(selectedTag);

  return (
    <section className="board-toolbar" aria-label="Board filters">
      <div className="board-toolbar-controls">
        <label className="toolbar-toggle">
          <input
            type="checkbox"
            checked={overdueOnly}
            onChange={(event) => onOverdueChange(event.target.checked)}
          />
          <span>Overdue Only</span>
        </label>

        <div className="toolbar-field">
          <label htmlFor="tagFilterSelect">Filter by tag</label>
          <select
            id="tagFilterSelect"
            value={selectedTag}
            onChange={(event) => onTagChange(event.target.value)}
          >
            <option value="">All tags</option>
            {availableTags.map((tag) => (
              <option key={tag} value={tag}>
                {tag}
              </option>
            ))}
          </select>
        </div>
      </div>

      {hasActiveFilters ? (
        <div className="active-filters" aria-live="polite">
          <span className="active-filters-label">Active filters:</span>
          {overdueOnly ? <span className="filter-chip">Overdue only</span> : null}
          {selectedTag ? <span className="filter-chip">Tag: {selectedTag}</span> : null}
          <button type="button" className="filter-clear-button" onClick={onClearFilters}>
            Clear filters
          </button>
        </div>
      ) : null}
    </section>
  );
}

export function collectAvailableTags(taskList) {
  const tagMap = new Map();

  taskList.forEach((task) => {
    if (!Array.isArray(task.tags)) {
      return;
    }

    task.tags.forEach((tag) => {
      const trimmed = tag.trim();
      if (!trimmed) {
        return;
      }

      const key = trimmed.toLowerCase();
      if (!tagMap.has(key)) {
        tagMap.set(key, trimmed);
      }
    });
  });

  return Array.from(tagMap.values()).sort((a, b) =>
    a.localeCompare(b, undefined, { sensitivity: "base" })
  );
}

export function buildTasksQuery(filters) {
  const params = new URLSearchParams();

  if (filters.overdueOnly) {
    params.set("overdue", "true");
  }

  if (filters.tag) {
    params.set("tag", filters.tag);
  }

  const query = params.toString();
  return query ? `/tasks?${query}` : "/tasks";
}
