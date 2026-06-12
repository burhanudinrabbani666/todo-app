from fastapi import status

from .utils import *
from routers.admin import get_db, get_current_user
from models import Todos

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_current_user


def test_admin_read_all_authenticated(test_todo):  # type: ignore
    response = client.get("/admin/todos")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {
            "complete": True,
            "description": "Need to learn everyday",
            "title": "Learn Code",
            "id": 1,
            "priority": 5,
            "owner_id": 1,
        }
    ]


def test_admin_delete_todo(test_todo):  # type: ignore
    respone = client.delete("/admin/todos/1")
    assert respone.status_code == status.HTTP_204_NO_CONTENT

    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()

    assert model is None


def test_admin_delete_todo_not_found(test_todo):  # type: ignore
    respone = client.delete("/admin/todos/999")
    assert respone.status_code == status.HTTP_404_NOT_FOUND
    assert respone.json() == {"detail": "Todo not found"}
