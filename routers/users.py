from typing import Annotated, Any
from pydantic import BaseModel

from passlib.context import CryptContext
from fastapi import (
    APIRouter,
    Body,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from ..database import Sessionlocal
from ..models import Users
from .auth import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class NewPasswordRequest(BaseModel):
    password: str
    new_password: str


class NewPhoneRequest(BaseModel):
    phone: int
    new_phone_number: int


"""
---------------------------------------------------------------------
FUNCTION
---------------------------------------------------------------------

"""


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


def get_user_from_database(id: Any, db: db_depedency) -> Users | None:
    return db.query(Users).filter(Users.id == id).first()


"""
---------------------------------------------------------------------
ROUTE
---------------------------------------------------------------------

"""


@router.get("", status_code=status.HTTP_200_OK)
async def get_user(user: user_depedency, db: db_depedency):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication Failed",
        )

    current_user = (
        db.query(Users).filter(Users.id == user.get("id")).first()
    )

    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return current_user


@router.post(
    "/new-password",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def new_password(
    user: user_depedency,
    db: db_depedency,
    new_password_request: NewPasswordRequest = Body(),
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication Failed",
        )

    current_user = get_user_from_database(user.get("id"), db)
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Verify old password
    if not bcrypt_context.verify(
        new_password_request.password, current_user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication Failed",
        )

    current_user.hashed_password = bcrypt_context.hash(
        new_password_request.new_password
    )

    db.add(current_user)
    db.commit()


@router.post(
    "/new-phone-number",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def new_phone_number(
    user: user_depedency,
    db: db_depedency,
    new_phone_request: NewPhoneRequest = Body(),
):
    print(new_phone_request)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication Failed",
        )

    current_user = get_user_from_database(user.get("id"), db)
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    current_user.phone_number = new_phone_request.new_phone_number

    db.add(current_user)
    db.commit()
