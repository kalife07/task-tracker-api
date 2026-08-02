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
    """Create and persist a new task."""
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
