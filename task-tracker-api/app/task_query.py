from dataclasses import dataclass
from typing import Callable, Optional

from app.models import TaskPriority, TaskResponse, TaskStatus
from app.validation import is_task_overdue


@dataclass(frozen=True)
class TaskQueryFilters:
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    overdue: Optional[bool] = None
    tag: Optional[str] = None


def _matches_status(task: TaskResponse, status: TaskStatus) -> bool:
    return task.status == status


def _matches_priority(task: TaskResponse, priority: TaskPriority) -> bool:
    return task.priority == priority


def _matches_overdue(task: TaskResponse) -> bool:
    return is_task_overdue(task.due_date, task.status.value)


def _matches_tag(task: TaskResponse, tag: str) -> bool:
    normalized_tag = tag.casefold()
    return any(stored_tag.casefold() == normalized_tag for stored_tag in task.tags)


def build_task_predicates(
    filters: TaskQueryFilters,
) -> list[Callable[[TaskResponse], bool]]:
    """Build composable predicates from query filters.

    Args:
        filters (TaskQueryFilters): The filter values to compile into
            predicates. ``status``/``priority``/``tag`` each add a
            predicate when not ``None``. ``overdue`` adds a predicate only
            when it is exactly ``True``; ``False`` behaves the same as
            ``None`` (no overdue-based predicate is added). A blank or
            whitespace-only ``tag`` is ignored (no predicate is added).

    Returns:
        list[Callable[[TaskResponse], bool]]: One predicate per active
        filter, each returning True when a given task matches that
        filter. Empty when no filters are active.
    """
    predicates: list[Callable[[TaskResponse], bool]] = []

    if filters.status is not None:
        status = filters.status
        predicates.append(lambda task, status=status: _matches_status(task, status))

    if filters.priority is not None:
        priority = filters.priority
        predicates.append(
            lambda task, priority=priority: _matches_priority(task, priority)
        )

    if filters.overdue is True:
        predicates.append(_matches_overdue)

    if filters.tag is not None:
        tag = filters.tag.strip()
        if tag:
            predicates.append(lambda task, tag=tag: _matches_tag(task, tag))

    return predicates


def filter_tasks(
    tasks: list[TaskResponse],
    filters: TaskQueryFilters,
) -> list[TaskResponse]:
    """Apply all active query filters to a task list.

    Args:
        tasks (list[TaskResponse]): The tasks to filter.
        filters (TaskQueryFilters): The filter values; see
            ``build_task_predicates`` for how each field is interpreted.

    Returns:
        list[TaskResponse]: Tasks matching every active filter (AND
        semantics, i.e. a task must satisfy all predicates). Returns
        ``tasks`` unchanged when no filters are active.
    """
    predicates = build_task_predicates(filters)
    if not predicates:
        return tasks

    return [
        task
        for task in tasks
        if all(predicate(task) for predicate in predicates)
    ]
