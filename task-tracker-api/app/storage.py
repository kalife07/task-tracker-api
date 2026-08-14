from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from app.models import TaskCreate, TaskResponse, TaskUpdate
from app.task_query import TaskQueryFilters, filter_tasks

_tasks: dict[str, TaskResponse] = {}


def add_task(payload: TaskCreate) -> TaskResponse:
    """Create a new task record and store it in memory.

    Args:
        payload (TaskCreate): The already-validated task data to persist.

    Returns:
        TaskResponse: The stored task, with a generated UUID ``id`` and
        ``created_at``/``updated_at`` both set to the current UTC time.
        ``description`` falls back to ``""`` if ``payload.description``
        is falsy (``None`` or empty).
    """
    now = datetime.now(timezone.utc)
    task_id = str(uuid4())
    task = TaskResponse(
        id=task_id,
        title=payload.title,
        description=payload.description or "",
        status=payload.status,
        priority=payload.priority,
        assignee=payload.assignee,
        due_date=payload.due_date,
        tags=payload.tags,
        created_at=now,
        updated_at=now,
    )
    _tasks[task_id] = task
    return task


def get_all_tasks(filters: TaskQueryFilters | None = None) -> list[TaskResponse]:
    """Return all stored tasks, optionally filtered.

    Args:
        filters (TaskQueryFilters | None): When provided, only tasks
            matching every active filter are returned (see
            ``app.task_query.filter_tasks``). When ``None``, all tasks
            are returned unfiltered.

    Returns:
        list[TaskResponse]: The matching tasks, in the in-memory dict's
        iteration order (insertion order).
    """
    tasks = list(_tasks.values())
    if filters is None:
        return tasks
    return filter_tasks(tasks, filters)


def get_task_by_id(task_id: str) -> Optional[TaskResponse]:
    """Look up a single task by its id.

    Args:
        task_id (str): The task's unique id.

    Returns:
        Optional[TaskResponse]: The task if found, otherwise ``None``.
    """
    return _tasks.get(task_id)


def update_task(task_id: str, payload: TaskUpdate) -> Optional[TaskResponse]:
    """Apply a partial update to a stored task.

    Only fields explicitly set on ``payload`` are applied
    (``model_dump(exclude_unset=True)``); omitted fields are left as-is.
    Status-transition validity is not checked here — see
    ``app.business_rules.validate_status_transition``, which the
    ``PATCH /tasks/{id}`` route calls separately before invoking this
    function.

    Args:
        task_id (str): The task's unique id.
        payload (TaskUpdate): The fields to update.

    Returns:
        Optional[TaskResponse]: ``None`` if no task with ``task_id``
        exists. If ``payload`` has no fields set, the existing task is
        returned unchanged (``updated_at`` is not bumped). Otherwise, the
        updated task is returned with ``updated_at`` set to the current
        UTC time.
    """
    task = _tasks.get(task_id)
    if task is None:
        return None

    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        return task

    updated_task = task.model_copy(
        update={**updates, "updated_at": datetime.now(timezone.utc)}
    )
    _tasks[task_id] = updated_task
    return updated_task


def delete_task(task_id: str) -> bool:
    """Delete a stored task by id.

    Args:
        task_id (str): The task's unique id.

    Returns:
        bool: True if a task was found and deleted, False if no task
        with ``task_id`` existed.

    [VERIFY]: No route currently calls this function — there is no
    ``DELETE /tasks/{id}`` route in ``app/api/routes/tasks.py``, even
    though ``tests/test_tasks.py`` has tests that expect one (they
    currently fail with 405). Confirm whether a delete route is still
    expected, or whether this function is intentionally unused for now.
    """
    if task_id in _tasks:
        del _tasks[task_id]
        return True
    return False


def _reset() -> None:
    _tasks.clear()
