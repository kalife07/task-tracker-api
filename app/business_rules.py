from fastapi import HTTPException, status

from app.models import TaskStatus

VALID_TRANSITIONS: frozenset[tuple[TaskStatus, TaskStatus]] = frozenset({
    (TaskStatus.TODO, TaskStatus.IN_PROGRESS),
    (TaskStatus.IN_PROGRESS, TaskStatus.DONE),
    (TaskStatus.DONE, TaskStatus.IN_PROGRESS),
})


def validate_status_transition(current: TaskStatus, new: TaskStatus) -> None:
    """Validate that a task status change is an allowed transition.

    Args:
        current (TaskStatus): The task's existing status.
        new (TaskStatus): The requested new status.

    Returns:
        None: Returns silently when the transition is allowed.

    Raises:
        HTTPException: 422 if ``(current, new)`` is not a member of
            ``VALID_TRANSITIONS`` (``ToDo->InProgress``,
            ``InProgress->Done``, ``Done->InProgress``). This also rejects
            same-status "transitions" such as ``ToDo->ToDo``, since those
            are not in the allowed set.
    """
    if (current, new) not in VALID_TRANSITIONS:
        allowed = sorted({f"{f.value}->{t.value}" for f, t in VALID_TRANSITIONS})
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid status transition from {current.value} to {new.value}. Allowed transitions: {allowed}",
        )
