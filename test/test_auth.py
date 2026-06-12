import pytest

from fastapi import HTTPException
from jose import jwt
from datetime import timedelta

from .utils import *
from ..routers.auth import (
    get_db,
    authenticate_user,
    create_access_token,
    get_current_user,
    SECRET_KEY,
    ALGHORITHM,
)

app.dependency_overrides[get_db] = override_get_db


def test_auth_user(test_user):  # type: ignore
    db = TestingSessionLocal()

    authenticated_user = authenticate_user(
        test_user.username, "bani", db  # type: ignore
    )

    if authenticated_user:
        assert authenticated_user is not None
        assert authenticated_user.username == test_user.username  # type: ignore

    non_auth_user = authenticate_user("WrongUsername", "bani", db)
    assert non_auth_user is False

    wrong_password = authenticate_user(test_user.username, "bani123", db)  # type: ignore
    assert wrong_password is False


def test_create_access_token():
    username = "testuser"
    user_id = 1
    role = "user"
    expires_delta = timedelta(days=1)

    token = create_access_token(
        username,
        user_id,
        role,
        expires_delta,
    )

    decode_token = jwt.decode(
        token,
        SECRET_KEY,
        algorithms=ALGHORITHM,
        options={"verify_signature": False},
    )

    assert decode_token["sub"] == username
    assert decode_token["id"] == user_id
    assert decode_token["role"] == role


@pytest.mark.asyncio
async def test_get_current_user_valid_token():
    encode: dict[str, Any] = {
        "sub": "testuser",
        "id": 1,
        "role": "admin",
    }
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGHORITHM)

    user = await get_current_user(token)
    assert user == {
        "username": "testuser",
        "id": 1,
        "user_role": "admin",
    }


@pytest.mark.asyncio
async def test_get_current_user_missing_payload():
    encode = {"role": "user"}
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGHORITHM)

    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(token=token)

    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == "Could validate user"
