"""Tests for the JSON file behind ``app.storage``.

Storage is a dict cached in the process, so a "restart" is simulated by
dropping that cache (``_use_storage_path`` on the same file) and letting
the next call read the file back.
"""

import json
import os

import pytest

from app import storage
from app.models import TaskCreate, TaskUpdate


def _simulate_restart():
    """Drop the in-process cache so the next call reloads from disk."""
    path = storage._storage_path()
    storage._use_storage_path(path)


def _storage_file_contents():
    return json.loads(storage._storage_path().read_text(encoding="utf-8"))


def test_created_task_is_written_to_the_storage_file():
    task = storage.add_task(TaskCreate(title="write me", tags=["home"]))

    contents = _storage_file_contents()
    assert contents["version"] == 1
    assert [record["id"] for record in contents["tasks"]] == [task.id]
    assert contents["tasks"][0]["title"] == "write me"
    # is_overdue is derived at read time, so it is not persisted.
    assert "is_overdue" not in contents["tasks"][0]


def test_tasks_survive_a_restart():
    first = storage.add_task(TaskCreate(title="first", priority="High"))
    second = storage.add_task(TaskCreate(title="second", tags=["work"]))

    _simulate_restart()

    reloaded = storage.get_all_tasks()
    assert [task.id for task in reloaded] == [first.id, second.id]
    assert reloaded[0].model_dump() == first.model_dump()
    assert reloaded[1].tags == ["work"]


def test_update_and_delete_survive_a_restart():
    kept = storage.add_task(TaskCreate(title="kept"))
    doomed = storage.add_task(TaskCreate(title="doomed"))

    storage.update_task(kept.id, TaskUpdate(title="renamed"))
    assert storage.delete_task(doomed.id) is True

    _simulate_restart()

    assert storage.get_task_by_id(kept.id).title == "renamed"
    assert storage.get_task_by_id(doomed.id) is None
    assert len(storage.get_all_tasks()) == 1


def test_missing_storage_file_starts_empty():
    storage._storage_path().unlink(missing_ok=True)
    _simulate_restart()

    assert storage.get_all_tasks() == []


def test_corrupt_storage_file_is_moved_aside_instead_of_overwritten(capsys):
    path = storage._storage_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("{not valid json", encoding="utf-8")

    _simulate_restart()

    assert storage.get_all_tasks() == []
    backups = list(path.parent.glob(f"{path.name}.corrupt-*"))
    assert len(backups) == 1
    assert backups[0].read_text(encoding="utf-8") == "{not valid json"
    assert "could not read" in capsys.readouterr().out


def test_write_retries_a_transient_windows_file_lock(monkeypatch):
    # A scanner/indexer holding the file makes os.replace raise
    # PermissionError; the lock clears in milliseconds, so the write
    # should retry rather than fail the request.
    real_replace = os.replace
    calls = {"count": 0}

    def flaky_replace(source, destination):
        calls["count"] += 1
        if calls["count"] == 1:
            raise PermissionError(5, "Access is denied")
        return real_replace(source, destination)

    monkeypatch.setattr(storage.os, "replace", flaky_replace)
    task = storage.add_task(TaskCreate(title="locked file"))

    assert calls["count"] == 2
    assert [record["id"] for record in _storage_file_contents()["tasks"]] == [task.id]


def test_write_gives_up_after_repeated_lock_failures(monkeypatch):
    def always_locked(source, destination):
        raise PermissionError(5, "Access is denied")

    monkeypatch.setattr(storage.os, "replace", always_locked)

    with pytest.raises(PermissionError):
        storage.add_task(TaskCreate(title="never writable"))

    # The temp file is cleaned up rather than left beside the store.
    path = storage._storage_path()
    assert list(path.parent.glob(f"{path.name}.tmp")) == []


def test_tasks_persist_across_requests_through_the_api(client):
    created = client.post("/tasks", json={"title": "via api"}).json()

    _simulate_restart()

    response = client.get(f"/tasks/{created['id']}")
    assert response.status_code == 200
    assert response.json()["title"] == "via api"
