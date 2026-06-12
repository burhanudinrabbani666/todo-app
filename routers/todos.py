from typing import Annotated, Any
from pydantic import BaseModel, Field
from starlette.responses import RedirectResponse

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Path,
    Request,
    Response,
)
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from ..database import Sessionlocal
from ..models import Todos
from .auth import get_current_user

router = APIRouter(prefix="/todos", tags=["Todos"])

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


def redirect_to_login():
    redirect_response = RedirectResponse(
        url="/auth/sign-in-page", status_code=status.HTTP_302_FOUND
    )
    redirect_response.delete_cookie(key="access_token")
    return redirect_response


"""
---------------------------------------------------------------------
DATA SHAPH 
---------------------------------------------------------------------

"""


class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool


@router.get("", status_code=status.HTTP_200_OK)
async def read_all(user: user_depedency, db: db_depedency):

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication Failed",
        )

    return (
        db.query(Todos)
        .filter(Todos.owner_id == user.get("id", ""))
        .all()
    )


@router.get("/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(
    user: user_depedency,
    db: db_depedency,
    todo_id: int = Path(gt=0),
):

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication Failed",
        )

    todo_model = (
        db.query(Todos)
        .filter(Todos.id == todo_id)
        .filter(Todos.owner_id == user.get("id"))
        .first()
    )

    if todo_model is not None:
        return todo_model

    raise HTTPException(status_code=404, detail="Todo not found")


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_todo(
    user: user_depedency,
    db: db_depedency,
    todo_request: TodoRequest,
):

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication Failed",
        )

    todo_model = Todos(
        **todo_request.model_dump(),
        owner_id=user.get("id"),
    )

    db.add(todo_model)
    db.commit()
    db.refresh(todo_model)

    return todo_model


@router.put("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(
    user: user_depedency,
    db: db_depedency,
    todo_request: TodoRequest,
    todo_id: int = Path(gt=0),
):

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication Failed",
        )

    todo_model = (
        db.query(Todos)
        .filter(Todos.id == todo_id)
        .filter(Todos.owner_id == user.get("id"))
        .first()
    )
    if todo_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found",
        )

    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.complete = todo_request.complete

    db.add(todo_model)
    db.commit()


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    user: user_depedency,
    db: db_depedency,
    todo_id: int = Path(gt=0),
):
    print(user)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication Failed",
        )

    result = (
        db.query(Todos)
        .filter(Todos.id == todo_id)
        .filter(Todos.owner_id == user.get("id"))
        .delete()
    )

    if result == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found",
        )

    db.commit()


"""
---------------------------------------------------------------------
PAGES
---------------------------------------------------------------------
"""

templates = Jinja2Templates(directory="TodoApp/templates")


@router.get("/todo/page/")
async def get_todo_page(
    request: Request, db: db_depedency
) -> Response:
    try:
        token = request.cookies.get("access_token")
        if token is None:
            return redirect_to_login()

        user = await get_current_user(token=token)

        if user.get("username") == None:
            return redirect_to_login()

        todos = (
            db.query(Todos)
            .filter(Todos.owner_id == user.get("id"))
            .all()
        )

        return templates.TemplateResponse(
            request=request,
            name="todo.html",
            context={"todos": todos, "user": user},
        )
    except:
        return redirect_to_login()


@router.get("/add-todo/page")
async def get_add_todo_page(request: Request) -> Response:
    try:
        token = request.cookies.get("access_token")
        if token is None:
            return redirect_to_login()

        user = await get_current_user(token=token)
        if user.get("username") == None:
            return redirect_to_login()

        return templates.TemplateResponse(
            request=request,
            name="add-todo.html",
            context={"user": user},
        )

    except:
        return redirect_to_login()


@router.get("/edit-todo/page/{todo_id}")
async def get_edit_todo_page(
    request: Request, todo_id: int, db: db_depedency
) -> Response:
    try:
        print(todo_id)

        token = request.cookies.get("access_token")

        if token is None:
            return redirect_to_login()

        user = await get_current_user(token=token)

        if user.get("username") == None:
            return redirect_to_login()

        todo = db.query(Todos).filter(Todos.id == todo_id).first()

        if todo is None:
            return redirect_to_login()

        return templates.TemplateResponse(
            request=request,
            name="edit-todo.html",
            context={"todo": todo, "user": user},
        )

    except:
        return redirect_to_login()
