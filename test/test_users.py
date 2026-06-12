from fastapi import status

from .utils import *
from routers.users import get_db, get_current_user

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_current_user


def test_return_user(test_user):  # type: ignore
    response = client.get("/users")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["username"] == "bani123"
    assert response.json()["first_name"] == "bani"
    assert response.json()["last_name"] == "bani"
    assert response.json()["email"] == "bani@bani1234"
    assert response.json()["role"] == "admin"
    assert response.json()["phone_number"] == 123445
    assert response.json()["is_active"] == True


def test_change_password_success(test_user):  # type: ignore
    response = client.post(
        "/users/new-password",
        json={"password": "bani", "new_password": "bani123"},
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_change_password_failed(test_user):  # type: ignore
    response = client.post(
        "/users/new-password",
        json={"password": "wrongpassword", "new_password": "bani123"},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Authentication Failed"}


def test_change_phone_number(test_user):  # type: ignore
    response = client.post(
        "/users/new-phone-number",
        json={"phone": 123445, "new_phone_number": 121212},
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT
