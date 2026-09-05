import pytest
from fastapi.testclient import TestClient

from app import storage
from app.main import app


@pytest.fixture(autouse=True)
def _reset_storage(tmp_path):
    # Point the JSON storage file at a per-test temp file so tests never
    # read or delete real task data, then clear it before and after.
    storage._use_storage_path(tmp_path / "storage.json")
    storage._reset()
    yield
    storage._reset()
    storage._use_storage_path(None)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def created_task(client):
    response = client.post("/tasks", json={"title": "fixture task"})
    assert response.status_code == 201
    return response.json()
