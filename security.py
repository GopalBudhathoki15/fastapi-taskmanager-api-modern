from pwdlib import PasswordHash
from datetime import datetime, timedelta, timezone
from config import settings
import jwt
from jwt.exceptions import InvalidTokenError
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy import select
import models
from database import get_db


ph = PasswordHash.recommended()

oauth_scheme = OAuth2PasswordBearer(tokenUrl="login")


def hash_password(plain_password: str) -> str:
    return ph.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return ph.verify(plain_password, hashed_password)


def create_access_token(data: dict, expire_delta: timedelta | None = None) -> str:
    to_encode = data.copy()

    if expire_delta:
        expires = datetime.now(timezone.utc) + expire_delta
    else:
        expires = datetime.now(timezone.utc) + timedelta(
            minutes=settings.access_token_expires_minutes
        )

    to_encode.update({"exp": expires})

    encoded_token = jwt.encode(
        to_encode, settings.secret_key, algorithm=settings.algorithm
    )

    return encoded_token


def get_current_user(
    token: Annotated[str, Depends(oauth_scheme)],
    db: Annotated[Session, Depends(get_db)],
):
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        username = payload.get("sub")

        if username is None:
            raise credential_exception

    except InvalidTokenError:
        raise credential_exception

    stmt = select(models.User).where(models.User.username == username)

    db_user = db.execute(stmt).scalar_one_or_none()

    if db_user is None:
        raise credential_exception

    return db_user
