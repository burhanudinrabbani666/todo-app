from datetime import datetime, timedelta, timezone
from typing import Annotated, Any
from pydantic import BaseModel

from fastapi import (
    APIRouter,
    Depends,
    status,
    HTTPException,
    Request,
    Response,
)
from fastapi.templating import Jinja2Templates


from fastapi.security import (
    OAuth2PasswordRequestForm,
    OAuth2PasswordBearer,
)
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from database import Sessionlocal
from models import Users

router = APIRouter(prefix="/auth", tags=["Auth"])

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oath2_bearer = OAuth2PasswordBearer(
    tokenUrl="auth/sign-in"
)  # This is like redirect after this opration happend

SECRET_KEY = (
    "1374ebf61b49930e570332f429da67aa81066943b89a6abddfe58df4cf83b0e2"
)
ALGHORITHM = "HS256"

"""
---------------------------------------------------------------------
FUNCTION
---------------------------------------------------------------------

"""

# --------------------------------------------------------------------
# DATABASE


def get_db():
    db = Sessionlocal()
    try:
        yield db
    finally:
        db.close()


db_depedency = Annotated[Session, Depends(get_db)]


# --------------------------------------------------------------------
# AUTHENTICATION


def authenticate_user(username: str, password: str, db: Session):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False

    if not bcrypt_context.verify(password, user.hashed_password):
        return False

    return user


def create_access_token(
    username: str, user_id: int, role: str, expires_delta: timedelta
):
    encode: dict[str, Any] = {
        "sub": username,
        "id": user_id,
        "role": role,
    }

    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({"exp": expires})

    return jwt.encode(encode, SECRET_KEY, algorithm=ALGHORITHM)


async def get_current_user(
    token: Annotated[str, Depends(oath2_bearer)],
) -> dict[str, Any]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGHORITHM)
        username = payload.get("sub")
        user_id = payload.get("id")
        user_role = payload.get("role")

        if username is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could validate user",
            )

        return {
            "username": username,
            "id": user_id,
            "user_role": user_role,
        }

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could validate user",
        )


"""
---------------------------------------------------------------------
DATA VALIDATION REQUEST AND RESPONSE
---------------------------------------------------------------------

"""


class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str
    phone_number: int


class Token(BaseModel):
    access_token: str
    token_type: str


"""
---------------------------------------------------------------------
ROUTES
---------------------------------------------------------------------

"""


@router.post("/sign-up", status_code=status.HTTP_201_CREATED)
async def register_user(
    db: db_depedency,
    create_user_request: CreateUserRequest,
):

    create_user_model = Users(
        email=create_user_request.email,
        username=create_user_request.username,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        role=create_user_request.role,
        hashed_password=bcrypt_context.hash(
            create_user_request.password
        ),
        is_active=True,
        phone_number=create_user_request.phone_number,
    )

    db.add(create_user_model)
    db.commit()


@router.post(
    "/sign-in", status_code=status.HTTP_200_OK, response_model=Token
)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: db_depedency,
):

    user = authenticate_user(
        form_data.username,
        form_data.password,
        db,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could validate user",
        )

    token = create_access_token(
        user.username,
        user.id,
        user.role,
        timedelta(minutes=20),
    )

    return {"access_token": token, "token_type": "bearer"}


"""
---------------------------------------------------------------------
PAGES
---------------------------------------------------------------------
"""

templates = Jinja2Templates(directory="./templates")


@router.get("/sign-in-page")
def render_sign_in_page(request: Request) -> Response:
    return templates.TemplateResponse(
        request=request, name="sign-in.html"
    )


@router.get("/sign-up-page")
def render_sign_up_page(request: Request) -> Response:
    return templates.TemplateResponse(
        request=request, name="sign-up.html"
    )
