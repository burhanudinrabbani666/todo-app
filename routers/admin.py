from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.orm import Session

from ..database import Sessionlocal
from ..models import Todos
from .auth import get_current_user

router = APIRouter(prefix="/admin", tags=["Admin"])


def get_db():
    db = Sessionlocal()
    try:
        yield db
    finally:
        db.close()


db_depedency = Annotated[Session, Depends(get_db)]
user_depedency = Annotated[
    dict[str, Any] | None, Depends(get_current_user)
]


@router.get("/todos", status_code=status.HTTP_200_OK)
async def read_all(user: user_depedency, db: db_depedency):
    if user is None or user.get("user_role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication Failed",
        )

    return db.query(Todos).all()


@router.delete(
    "/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_todo(
    user: user_depedency,
    db: db_depedency,
    todo_id: int = Path(gt=0),
):
    if user is None or user.get("user_role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication Failed",
        )

    result = db.query(Todos).filter(Todos.id == todo_id).delete()

    if result == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found",
        )

    db.commit()
