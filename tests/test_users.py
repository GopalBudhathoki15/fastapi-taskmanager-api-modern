# tests/test_users.py
from fastapi import status


def test_list_users(test_client, create_test_user):
    response = test_client.get("/users")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert any(user["username"] == "alice" for user in data)


def test_get_user_by_id(test_client, create_test_user):
    alice_id = create_test_user["id"]
    response = test_client.get(f"/users/{alice_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["username"] == "alice"


def test_get_nonexistent_user(test_client):
    response = test_client.get("/users/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_user(test_client):
    # Create temporary user
    response = test_client.post(
        "/auth/register",
        json={
            "username": "tempuser",
            "email": "temp@example.com",
            "password": "pass123",
        },
    )
    user_id = response.json()["id"]

    del_response = test_client.delete(f"/users/{user_id}")
    assert del_response.status_code == status.HTTP_204_NO_CONTENT

    # Check user deleted
    response = test_client.get(f"/users/{user_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
