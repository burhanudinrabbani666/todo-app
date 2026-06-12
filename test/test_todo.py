from typing import Any

from fastapi import status


from .utils import *
from ..routers.todos import get_db
from ..routers.auth import get_current_user
from ..models import Todos
from ..main import app

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_current_user


def test_read_all_authenticated(test_todo):  # type: ignore
    response = client.get("/todos")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {
            "title": "Learn Code",
            "complete": True,
            "description": "Need to learn everyday",
            "id": 1,
            "priority": 5,
            "owner_id": 1,
        }
    ]


def test_read_one_valid_id(test_todo):  # type: ignore
    response = client.get("/todos/1")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "title": "Learn Code",
        "complete": True,
        "description": "Need to learn everyday",
        "id": 1,
        "priority": 5,
        "owner_id": 1,
    }


def test_read_one_not_found(test_todo):  # type: ignore
    response = client.get("/todos/5")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Todo not found"}


def test_create_todo(test_todo):  # type: ignore
    request_data: dict[str, Any] = {
        "title": "new todo",
        "description": "new todo description",
        "priority": 5,
        "complete": False,
    }

    response = client.post("/todos", json=request_data)
    assert response.status_code == status.HTTP_201_CREATED

    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 2).first()

    if model:
        assert model.title == request_data.get("title")
        assert model.description == request_data.get("description")
        assert model.priority == request_data.get("priority")
        assert model.complete == request_data.get("complete")


def test_update_todo(test_todo):  # type: ignore
    request_data: dict[str, Any] = {
        "title": "Chage the title of the code already save",
        "description": "Need to learn everyday",
        "priority": 5,
        "complete": False,
    }

    respone = client.put("/todos/1", json=request_data)
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()

    assert respone.status_code == status.HTTP_204_NO_CONTENT

    if model:
        assert model.title == request_data.get("title")
        assert model.description == request_data.get("description")
        assert model.priority == request_data.get("priority")
        assert model.complete == request_data.get("complete")


def test_update_todo_not_found(test_todo):  # type: ignore
    request_data: dict[str, Any] = {
        "title": "Chage the title of the code already save",
        "description": "Need to learn everyday",
        "priority": 5,
        "complete": False,
    }

    respone = client.put("/todos/999", json=request_data)

    assert respone.status_code == status.HTTP_404_NOT_FOUND
    assert respone.json() == {"detail": "Todo not found"}


def test_delete_todo(test_todo):  # type: ignore
    respone = client.delete("/todos/1")
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()

    assert respone.status_code == status.HTTP_204_NO_CONTENT
    assert model is None


def test_delete_todo_not_found():
    respone = client.delete("/todos/999")
    assert respone.status_code == status.HTTP_404_NOT_FOUND
    assert respone.json() == {"detail": "Todo not found"}
