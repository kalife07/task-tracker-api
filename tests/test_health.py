def test_health_returns_200_with_status_ok(client):
    response = client.get("/health")
    assert response.status_code == 200

    body = response.json()
    assert body["status"] == "ok"
    assert body["timestamp"]


def test_root_serves_the_kanban_board(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")

    # The board itself, not the docs page or a redirect to them.
    assert "<title>Task Tracker" in response.text
    assert 'id="board"' in response.text


def test_favicon_returns_204_instead_of_404(client):
    assert client.get("/favicon.ico").status_code == 204


def test_unknown_path_still_returns_404(client):
    assert client.get("/not-a-route").status_code == 404
