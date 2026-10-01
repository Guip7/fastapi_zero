from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_zero.database import get_session
from fastapi_zero.models import User
from fastapi_zero.schemas import FilterPage, UserList, UserPublic, UserSchema
from fastapi_zero.security import get_current_user, get_password_hash

router = APIRouter(prefix="/users", tags=["users"])

Session = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post("/", response_model=UserPublic)
async def create_user(user: UserSchema, session: Session):
    db_user = await session.scalar(
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
    await session.commit()
    await session.refresh(db_user)

    return db_user


@router.get(
    "/",
    status_code=HTTPStatus.OK,
    response_model=UserList,
)
async def read_users(
    session: Session, filter_user: Annotated[FilterPage, Query()]
):

    result = await session.scalars(
        select(User).limit(filter_user.limit).offset(filter_user.offset)
    )
    users = result.all()
    return {"users": users}


@router.put(
    "/{user_id}",
    status_code=HTTPStatus.OK,
    response_model=UserPublic,
)
async def update_user(
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

        await session.commit()
        await session.refresh(current_user)
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail="Email or username already exists",
        )

    return current_user


@router.delete("/{user_id}", status_code=HTTPStatus.NO_CONTENT)
async def delete_user(
    user_id: int, session: Session, current_user: CurrentUser
):

    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail="Not enough permission"
        )

    await session.delete(current_user)
    await session.commit()
