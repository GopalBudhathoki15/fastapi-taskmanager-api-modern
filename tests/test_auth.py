# tests/test_auth.py
import pytest
from fastapi import status


@pytest.mark.parametrize(
    "username,email,password", [("alice", "alice@example.com", "password123")]
)
def test_register_user(test_client, username, email, password):
    response = test_client.post(
        "/auth/register",
        json={"username": username, "email": email, "password": password},
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["username"] == username
    assert data["email"] == email
    assert "id" in data


def test_register_duplicate_user(test_client):
    # Attempt to register same user again
    response = test_client.post(
        "/auth/register",
        json={
            "username": "alice",
            "email": "alice@example.com",
            "password": "password123",
        },
    )
    assert response.status_code == status.HTTP_409_CONFLICT


def test_login_user(test_client):
    response = test_client.post(
        "/auth/login",
        data={"username": "alice", "password": "password123"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_credentials(test_client):
    response = test_client.post(
        "/auth/login",
        data={"username": "alice", "password": "wrongpassword"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
