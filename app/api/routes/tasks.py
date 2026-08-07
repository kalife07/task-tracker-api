from fastapi import APIRouter, HTTPException, Query, status

from app import storage
from app.business_rules import validate_status_transition
from app.models import TaskCreate, TaskPriority, TaskResponse, TaskStatus, TaskUpdate
from app.storage import add_task
from app.task_query import TaskQueryFilters

router = APIRouter()


@router.post(
    "/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a task",
    description="Create a new task with the provided details.",
)
def create_task(payload: TaskCreate) -> TaskResponse:
    """Create and persist a new task.

    Args:
        payload (TaskCreate): Task fields to create. ``title`` is
            required; ``status`` defaults to ``ToDo`` and ``priority``
            defaults to ``Medium`` when omitted. Unknown fields are
            rejected.

    Returns:
        TaskResponse: The newly created task, including its generated
        ``id``, ``created_at``/``updated_at`` timestamps, and computed
        ``is_overdue`` flag.

    Raises:
        None directly. FastAPI validates the request body against
        ``TaskCreate`` before this handler runs; an invalid payload (e.g.
        blank title, malformed due_date, too many tags) short-circuits
        with an HTTP 422 response and never reaches this function.

    Example:
        POST /tasks {"title": "Write docs"} -> 201 TaskResponse
    """
    return add_task(payload)


@router.get(
    "/tasks",
    response_model=list[TaskResponse],
    tags=["tasks"],
)
def list_tasks(
    status: TaskStatus | None = None,
    priority: TaskPriority | None = None,
    overdue: bool | None = Query(
        default=None,
        description=(
            "When true, return only tasks whose due_date is before today "
            "and status is not Done."
        ),
    ),
    tag: str | None = Query(
        default=None,
        description="Exact, case-insensitive match against a task tag.",
    ),
) -> list[TaskResponse]:
    """List tasks, optionally filtered by status, priority, overdue, and tag.

    Args:
        status (TaskStatus | None): Exact-match filter on task status.
        priority (TaskPriority | None): Exact-match filter on task
            priority.
        overdue (bool | None): When exactly ``True``, keep only tasks
            whose ``due_date`` is before today (UTC) and whose status is
            not ``Done``. A value of ``False`` is treated the same as
            omitting the parameter (no overdue-based filtering is
            applied).
        tag (str | None): Case-insensitive, exact-match filter against a
            single task tag. Blank/whitespace-only values are ignored.

    Returns:
        list[TaskResponse]: All tasks matching every supplied filter
        (filters are combined with AND). Returns all tasks when no
        filters are supplied.

    Example:
        GET /tasks?status=ToDo&priority=High&tag=backend
    """
    filters = TaskQueryFilters(
        status=status,
        priority=priority,
        overdue=overdue,
        tag=tag,
    )
    return storage.get_all_tasks(filters=filters)


@router.get(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    tags=["tasks"],
)
def get_task(task_id: str) -> TaskResponse:
    """Fetch a single task by id.

    Args:
        task_id (str): The task's unique id.

    Returns:
        TaskResponse: The matching task.

    Raises:
        HTTPException: 404 if no task with ``task_id`` exists.

    Example:
        GET /tasks/{task_id} -> 200 TaskResponse | 404
    """
    task = storage.get_task_by_id(task_id)
    if task is None:
        raise HTTPException(
            status_code=404,
            detail=f"Task with id {task_id} not found",
        )
    return task


@router.patch(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    tags=["tasks"],
)
def update_task(task_id: str, payload: TaskUpdate) -> TaskResponse:
    """Apply a partial update to an existing task.

    Only fields explicitly present in ``payload`` are changed; omitted
    fields are left as-is (partial-update / PATCH semantics).

    Args:
        task_id (str): The task's unique id.
        payload (TaskUpdate): Fields to update. Unknown fields are
            rejected.

    Returns:
        TaskResponse: The updated task.

    Raises:
        HTTPException: 404 if no task with ``task_id`` exists.
        HTTPException: 422 if ``payload.status`` is set and the transition
            from the task's current status to the new status is not one
            of the allowed transitions in
            ``app.business_rules.VALID_TRANSITIONS`` (enforced here, not
            in ``storage.update_task``).

    Example:
        PATCH /tasks/{task_id} {"status": "InProgress"} -> 200 TaskResponse
    """
    if payload.status is not None:
        existing = storage.get_task_by_id(task_id)
        if existing is None:
            raise HTTPException(
                status_code=404,
                detail=f"Task with id {task_id} not found",
            )
        validate_status_transition(existing.status, payload.status)

    task = storage.update_task(task_id, payload)
    if task is None:
        raise HTTPException(
            status_code=404,
            detail=f"Task with id {task_id} not found",
        )
    return task
