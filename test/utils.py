from typing import Any

from sqlalchemy import StaticPool, create_engine, orm, text
from fastapi.testclient import TestClient

import pytest

from database import Base
from main import app
from models import Todos, Users
from routers.auth import bcrypt_context

SQLALCHEMY_DATABASE_URL = "sqlite:///./testdb.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


TestingSessionLocal = orm.sessionmaker(autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():
    print("OVERRIDE DB CALLED")
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


client = TestClient(app)


def override_current_user() -> dict[str, Any]:
    return {"username": "bani123", "id": 1, "user_role": "admin"}


@pytest.fixture
def test_todo():
    todo = Todos(
        title="Learn Code",
        description="Need to learn everyday",
        priority=5,
        complete=True,
        owner_id=1,
    )

    db = TestingSessionLocal()
    db.add(todo)
    db.commit()

    yield todo
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM todos;"))
        connection.commit()


@pytest.fixture
def test_user():
    user = Users(
        username="bani123",
        first_name="bani",
        last_name="bani",
        email="bani@bani1234",
        hashed_password=bcrypt_context.hash("bani"),
        role="admin",
        phone_number=123445,
        is_active=True,
    )

    db = TestingSessionLocal()
    db.add(user)
    db.commit()

    yield user
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM users;"))
        connection.commit()
