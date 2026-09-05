"""Task persistence.

Tasks live in the module-level ``_tasks`` dict, exactly as before, but
that dict is now a cache of a JSON file on disk (see
``app.core.config.Settings.storage_path``). The file is read once, lazily,
on the first storage call in a process, and rewritten after every
mutation, so task data survives a server restart.

Every public function keeps the signature and return values it had when
storage was purely in-memory; only the durability changes.
"""

import json
import os
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from uuid import uuid4

from pydantic import ValidationError

from app.core.config import settings
from app.models import TaskCreate, TaskResponse, TaskUpdate
from app.task_query import TaskQueryFilters, filter_tasks

_tasks: dict[str, TaskResponse] = {}

# Guards the _tasks cache and the file writes it triggers. Sync route
# handlers run in FastAPI's threadpool, so two requests can mutate
# storage concurrently.
_lock = threading.RLock()

# Whether the JSON file has been read into _tasks in this process yet.
_loaded = False

# Test-only override of the configured storage path (see _use_storage_path).
_path_override: Optional[Path] = None

# Version stamp written into the JSON file, so a future format change can
# be detected rather than guessed at.
_FILE_VERSION = 1

# How many times to retry the atomic rename in _save (see _replace_with_retry).
_REPLACE_ATTEMPTS = 6


def _replace_with_retry(source: Path, destination: Path) -> None:
    """Rename ``source`` over ``destination``, retrying transient locks.

    On Windows a virus scanner, backup agent (OneDrive) or search indexer
    can hold a brief handle on a file that was just written, which makes
    ``os.replace`` raise ``PermissionError``. The lock clears in
    milliseconds, so retry briefly before giving up.

    Args:
        source (Path): The temp file holding the new contents.
        destination (Path): The storage file to replace.

    Returns:
        None: The rename is performed as a side effect.

    Raises:
        OSError: If every attempt fails; ``source`` is removed first so a
            stale temp file is not left behind.
    """
    delay = 0.01
    for attempt in range(_REPLACE_ATTEMPTS):
        try:
            os.replace(source, destination)
            return
        except PermissionError:
            if attempt == _REPLACE_ATTEMPTS - 1:
                source.unlink(missing_ok=True)
                raise
            time.sleep(delay)
            delay *= 2


def _storage_path() -> Path:
    """The JSON file currently backing storage.

    Returns:
        Path: The test override when one is set (see
        ``_use_storage_path``), otherwise ``settings.storage_path``.
    """
    if _path_override is not None:
        return _path_override
    return settings.storage_path


def _quarantine_unreadable_file(path: Path, error: Exception) -> None:
    """Move a corrupt storage file aside instead of overwriting it.

    Args:
        path (Path): The storage file that could not be parsed.
        error (Exception): The parse/validation error that was raised.

    Returns:
        None: The file is renamed with a ``.corrupt-<timestamp>`` suffix
        and a warning is printed, so the next write starts from an empty
        file without destroying whatever was on disk.
    """
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    backup = path.with_name(f"{path.name}.corrupt-{stamp}")
    try:
        os.replace(path, backup)
    except OSError:
        backup = path
    print(f"[storage] could not read {path}: {error}")
    print(f"[storage] starting empty; previous file kept at {backup}")


def _load() -> None:
    """Read the JSON file into the ``_tasks`` cache.

    A missing file is treated as empty storage (first run). Both the
    ``{"version": 1, "tasks": [...]}`` object written by ``_save`` and a
    bare top-level list of task objects are accepted. An unknown
    ``is_overdue`` key is dropped from each record, since
    ``TaskResponse`` computes it at read time and forbids extra fields.

    Returns:
        None: Populates ``_tasks`` in place. If the file exists but
        cannot be parsed, it is moved aside by
        ``_quarantine_unreadable_file`` and storage starts empty rather
        than raising.
    """
    path = _storage_path()
    _tasks.clear()

    if not path.exists():
        return

    try:
        raw = json.loads(path.read_text(encoding="utf-8") or "{}")
        records = raw.get("tasks", []) if isinstance(raw, dict) else raw
        for record in records:
            record = {k: v for k, v in record.items() if k != "is_overdue"}
            task = TaskResponse.model_validate(record)
            _tasks[task.id] = task
    except (OSError, ValueError, ValidationError, AttributeError, TypeError) as error:
        _tasks.clear()
        _quarantine_unreadable_file(path, error)


def _save() -> None:
    """Write the ``_tasks`` cache back to the JSON file.

    The file is written to a sibling ``.tmp`` file first and then moved
    into place (see ``_replace_with_retry``), so a crash mid-write cannot
    leave a half-written storage file behind. ``is_overdue`` is excluded
    because it is derived at read time, not stored.

    Returns:
        None: Writes to disk as a side effect.
    """
    path = _storage_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "version": _FILE_VERSION,
        "tasks": [
            task.model_dump(mode="json", exclude={"is_overdue"})
            for task in _tasks.values()
        ],
    }

    tmp_path = path.with_name(f"{path.name}.tmp")
    tmp_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    _replace_with_retry(tmp_path, path)


def _ensure_loaded() -> None:
    """Load the JSON file into ``_tasks`` once per process.

    Returns:
        None: Does nothing after the first call (or after ``_reset``,
        which leaves storage loaded and empty).
    """
    global _loaded
    with _lock:
        if not _loaded:
            _load()
            _loaded = True


def add_task(payload: TaskCreate) -> TaskResponse:
    """Create a new task record and store it.

    Args:
        payload (TaskCreate): The already-validated task data to persist.

    Returns:
        TaskResponse: The stored task, with a generated UUID ``id`` and
        ``created_at``/``updated_at`` both set to the current UTC time.
        ``description`` falls back to ``""`` if ``payload.description``
        is falsy (``None`` or empty). The task is written to the JSON
        storage file before this returns.
    """
    _ensure_loaded()
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
    with _lock:
        _tasks[task_id] = task
        _save()
    return task


def get_all_tasks(filters: TaskQueryFilters | None = None) -> list[TaskResponse]:
    """Return all stored tasks, optionally filtered.

    Args:
        filters (TaskQueryFilters | None): When provided, only tasks
            matching every active filter are returned (see
            ``app.task_query.filter_tasks``). When ``None``, all tasks
            are returned unfiltered.

    Returns:
        list[TaskResponse]: The matching tasks, in the cache's iteration
        order — insertion order within a process, and the file's order
        after a restart, which is the order they were created in.
    """
    _ensure_loaded()
    with _lock:
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
    _ensure_loaded()
    with _lock:
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
        returned unchanged (``updated_at`` is not bumped and nothing is
        written to disk). Otherwise, the updated task is returned with
        ``updated_at`` set to the current UTC time, after the JSON
        storage file has been rewritten.
    """
    _ensure_loaded()
    with _lock:
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
        _save()
    return updated_task


def delete_task(task_id: str) -> bool:
    """Delete a stored task by id.

    Args:
        task_id (str): The task's unique id.

    Returns:
        bool: True if a task was found and deleted (and the JSON storage
        file rewritten), False if no task with ``task_id`` existed.
    """
    _ensure_loaded()
    with _lock:
        if task_id in _tasks:
            del _tasks[task_id]
            _save()
            return True
    return False


def _reset() -> None:
    """Clear storage, in memory and on disk. Test-only plumbing.

    Deletes the backing JSON file as well as the cache, so a test run
    starts from a genuinely empty store. Under ``APP_ENV=test`` the
    configured path defaults to a separate ``storage.test.json``, and the
    pytest suite points it at a ``tmp_path`` file, so this never touches
    real task data.

    Returns:
        None: Leaves storage loaded and empty.
    """
    global _loaded
    with _lock:
        _tasks.clear()
        path = _storage_path()
        try:
            path.unlink(missing_ok=True)
        except OSError as error:
            print(f"[storage] could not delete {path}: {error}")
        _loaded = True


def _use_storage_path(path: Optional[Path]) -> None:
    """Point storage at a different JSON file. Test-only plumbing.

    Args:
        path (Optional[Path]): The file to use, or ``None`` to fall back
            to ``settings.storage_path``.

    Returns:
        None: Drops the cached tasks so the next call reloads from the
        newly configured file.
    """
    global _path_override, _loaded
    with _lock:
        _path_override = Path(path) if path is not None else None
        _tasks.clear()
        _loaded = False
