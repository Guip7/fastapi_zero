from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from fastapi_zero.database import get_session
from fastapi_zero.models import User
from fastapi_zero.schemas import (
    UserList,
    UserPublic,
    UserSchema,
    FilterPage
)
from fastapi_zero.security import get_current_user, get_password_hash

router = APIRouter(prefix="/users", tags=["users"])

Session = Annotated[Session, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post("/", response_model=UserPublic)
def create_user(
    user: UserSchema,
    session: Session
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


@router.get(
    "/",
    status_code=HTTPStatus.OK,
    response_model=UserList,
)
def read_users(
    session: Session, 
    filter_user: Annotated[FilterPage, Query()] ):

    users = session.scalars(select(User).limit(filter_user.limit).offset(filter_user.offset)).all()
    return {"users": users}


@router.put(
    "/{user_id}",
    status_code=HTTPStatus.OK,
    response_model=UserPublic,
)
def update_user(
    user_id: int,
    user: UserSchema,
    session: Session,
    current_user: CurrentUser,
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail="Not enough permission"
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


@router.delete("/{user_id}", status_code=HTTPStatus.NO_CONTENT)
def delete_user(
    user_id: int,
    session: Session,
    current_user: CurrentUser
):

    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail="Not enough permission"
        )

    session.delete(current_user)
    session.commit()
