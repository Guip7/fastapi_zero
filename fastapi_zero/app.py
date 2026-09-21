from http import HTTPStatus

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from fastapi_zero.database import get_session
from fastapi_zero.models import User
from fastapi_zero.schemas import (
    Message,
    Token,
    UserList,
    UserPublic,
    UserSchema,
)
from fastapi_zero.security import (
    create_access_token,
    get_current_user,
    get_password_hash,
    verify_password,
)

app = FastAPI()

database = []


@app.get(
    "/",
    status_code=HTTPStatus.OK,
    response_model=Message,
    current_user=Depends(get_current_user),
)
def read_root():
    return {"message": "Olá mundo"}


@app.get(
    "/html",
    status_code=HTTPStatus.OK,
    response_class=HTMLResponse,
)
def html_helloworld():
    return """
    <html>
        <head>
            <title>Nosso olá mundo!</title>
        </head>
        <body>
            <h1> Olá Mundo </h1>
        </body>
    </html>
    """


@app.post(
    "/users/",
    status_code=HTTPStatus.CREATED,
    response_model=UserPublic,
)
@app.post("/users/", response_model=UserPublic)
def create_user(
    user: UserSchema,
    session: Session = Depends(get_session),
):
    db_user = session.scalar(
        select(User).where(
            or_(
                User.username == user.username,
                User.email == user.email,
            )
        )
    )

    if db_user:
        if db_user.username == user.username:
            raise HTTPException(
                detail="Username already exists",
                status_code=HTTPStatus.CONFLICT,
            )
        elif db_user.email == user.email:
            raise HTTPException(
                detail="Email already exists",
                status_code=HTTPStatus.CONFLICT,
            )

    user_data = user.model_dump()

    user_data["password"] = get_password_hash(user_data["password"])

    db_user = User(**user_data)

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


@app.get(
    "/users/",
    status_code=HTTPStatus.OK,
    response_model=UserList,
)
def read_users(
    limit: int = 10, offset: int = 0, session: Session = Depends(get_session)
):

    users = session.scalars(select(User).limit(limit).offset(offset)).all()
    return {"users": users}


@app.put(
    "/users/{user_id}",
    status_code=HTTPStatus.OK,
    response_model=UserPublic,
)
def update_user(
    user_id: int,
    user: UserSchema,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Not enough permission'
        )

    try:
        current_user.email = user.email
        current_user.username = user.username
        current_user.password = user.password

        session.commit()
        session.refresh(current_user)
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail="Email or username already exists",
        )

    return current_user


@app.delete("/users/{user_id}", status_code=HTTPStatus.NO_CONTENT)
def delete_user(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):

    if current_user.id != user_id:
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN,
                detail='Not enough permission'
            )

    session.delete(current_user)
    session.commit()


@app.post("/token", response_model=Token)
def login_for_acess_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    user = session.scalar(select(User).where(User.email == form_data.username))
    if not user:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="Incorret password or email",
        )

    if not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="Incorret password or email",
        )

    access_token = create_access_token(data={"sub": user.email})

    return {
        "access_token": access_token,
        "token_type": "Bearer",
    }
