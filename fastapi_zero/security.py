from datetime import datetime, timedelta
from http import HTTPStatus
from typing import Dict
from zoneinfo import ZoneInfo

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import DecodeError, decode, encode
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.orm import Session
from .settings import Settings
from fastapi_zero.database import get_session
from fastapi_zero.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


pwd_context = PasswordHash.recommended()
settings = Settings()

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    return pwd_context.verify(
        plain_password,
        hashed_password,
    )


def create_access_token(data: Dict) -> str:
    to_encode = data.copy()

    expire = datetime.now(tz=ZoneInfo("UTC")) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({"exp": expire})

    encoded_jwt = encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )

    return encoded_jwt


def get_current_user(
    session: Session = Depends(get_session),
    token: str = Depends(oauth2_scheme),
):
    credencial_exception = HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED,
        detail="could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode(token, settings.SECRET_KEY, algorithms=settings.ALGORITHM)
        subject_email = payload.get("sub")
        if not subject_email:
            raise credencial_exception
    except DecodeError:
        raise credencial_exception
    user = Session.scalar(select(User).where(User.email == subject_email))

    if not user:
        raise credencial_exception

    return user
