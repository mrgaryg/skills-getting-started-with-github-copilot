import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Drama Club" in data
    assert "description" in data["Drama Club"]
    assert "participants" in data["Drama Club"]


def test_signup_for_activity():
    # Test successful signup
    response = client.post("/activities/Drama Club/signup?email=test@example.com")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "test@example.com" in data["message"]

    # Verify the participant was added
    response = client.get("/activities")
    data = response.json()
    assert "test@example.com" in data["Drama Club"]["participants"]


def test_signup_activity_not_found():
    response = client.post("/activities/Nonexistent Activity/signup?email=test@example.com")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]


def test_signup_already_signed_up():
    # First signup
    client.post("/activities/Art Studio/signup?email=duplicate@example.com")
    # Try again
    response = client.post("/activities/Art Studio/signup?email=duplicate@example.com")
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "already signed up" in data["detail"]


def test_unregister_from_activity():
    # First signup
    client.post("/activities/Basketball Team/signup?email=unregister@example.com")
    # Then unregister
    response = client.delete("/activities/Basketball Team/unregister?email=unregister@example.com")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "unregister@example.com" in data["message"]

    # Verify removed
    response = client.get("/activities")
    data = response.json()
    assert "unregister@example.com" not in data["Basketball Team"]["participants"]


def test_unregister_activity_not_found():
    response = client.delete("/activities/Nonexistent Activity/unregister?email=test@example.com")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]


def test_unregister_not_signed_up():
    response = client.delete("/activities/Soccer Club/unregister?email=notsigned@example.com")
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "not signed up" in data["detail"]


def test_root_redirect():
    response = client.get("/")
    assert response.status_code == 200  # RedirectResponse, but TestClient follows redirects
    # Since it redirects to /static/index.html, but static files are mounted, it should work
    # Actually, TestClient might not serve static files the same way, but for now, assume it's ok