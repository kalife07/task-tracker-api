def test_get_version_returns_200_with_version_string(client):
    response = client.get("/version")
    assert response.status_code == 200
    assert response.json()["version"] == "0.1.0"
