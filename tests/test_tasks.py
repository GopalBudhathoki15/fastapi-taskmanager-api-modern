# tests/test_tasks.py
import pytest
from fastapi import status


@pytest.fixture
def auth_header(test_client):
    # Register and login user for tasks
    test_client.post(
        "/auth/register",
        json={"username": "bob", "email": "bob@example.com", "password": "password123"},
    )
    login_resp = test_client.post(
        "/auth/login",
        data={"username": "bob", "password": "password123"},
    )
    token = login_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_create_task(test_client, auth_header):
    response = test_client.post(
        "/tasks",
        json={"title": "Test Task"},
        headers=auth_header,
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["title"] == "Test Task"
    assert data["is_completed"] is False
    assert "id" in data


def test_list_tasks(test_client, auth_header):
    response = test_client.get("/tasks", headers=auth_header)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_update_task(test_client, auth_header):
    # Get task ID
    tasks = test_client.get("/tasks", headers=auth_header).json()
    task_id = tasks[0]["id"]

    response = test_client.patch(
        f"/tasks/{task_id}",
        json={"title": "Updated Task", "is_completed": True},
        headers=auth_header,
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["title"] == "Updated Task"
    assert data["is_completed"] is True


def test_delete_task(test_client, auth_header):
    # Get task ID
    tasks = test_client.get("/tasks", headers=auth_header).json()
    task_id = tasks[0]["id"]

    response = test_client.delete(f"/tasks/{task_id}", headers=auth_header)
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Task should no longer exist
    response = test_client.get("/tasks", headers=auth_header)
    assert all(task["id"] != task_id for task in response.json())
