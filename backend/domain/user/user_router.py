from fastapi import APIRouter, HTTPException
from fastapi import Depends
from sqlalchemy.orm import Session
from starlette import status
from datetime import timedelta, datetime
from database import get_db
from domain.user.user_crud import (
    pwd_context,
    create_user,
    update_user,
    get_user_by_username,
    get_user_by_id,
    get_existing_user,
    check_login_attempts,
    update_login_attempts,
    remove_user,
    get_all_users,
    validate_user,
    get_current_user,
)
from domain.user.user_schema import (
    UserCreate,
    UserResponse,
    Token,
    UserUpdate,
)
from models import User
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt
from starlette.config import Config

config = Config(".env")
router = APIRouter(prefix="/peppermint/user")

ACCESS_TOKEN_EXPIRE_MINUTES = int(config("ACCESS_TOKEN_EXPIRE_MINUTES", default=1))
SECRET_KEY = config("SECRET_KEY", default="SECRET_KEY")
ALGORITHM = "HS512"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/peppermint/user/login")


@router.post("/register")
def register(
    user_create: UserCreate,
    db: Session = Depends(get_db),
) -> UserResponse:
    user = get_existing_user(db, user_create=user_create)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This user already exists.",
        )
    new_user = create_user(db=db, user_create=user_create)

    return UserResponse(
        id=new_user.id,
        username=new_user.username,
        email=new_user.email,
        first_name=new_user.first_name,
        last_name=new_user.last_name,
        created=new_user.created,
        modified=new_user.modified,
        last_login_attempt=new_user.last_login_attempt,
        login_attempts=new_user.login_attempts,
    )


@router.post("/login", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> Token:
    user = get_user_by_username(db, form_data.username)
    if not user or not pwd_context.verify(form_data.password, user.password):
        if user:
            check_login_attempts(db, user)
            update_login_attempts(db, user, 1, user.last_login_attempt)

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    check_login_attempts(db, user)
    data = {
        "sub": user.username,
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    access_token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    update_login_attempts(db, user, -(user.login_attempts), datetime.utcnow())
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user.username,
    }
