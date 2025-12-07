from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import timedelta
from typing import Annotated
from schemas import Token, UserOut, UserCreate
from database import get_db
from security import verify_password, create_access_token, hash_password
from config import settings
import models

router = APIRouter()


@router.post("", response_model=Token)
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)],
):
    stmt = select(models.User).where(models.User.username == form_data.username)
    db_user = db.execute(stmt).scalar_one_or_none()

    if db_user is None or not verify_password(
        form_data.password, db_user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": db_user.username},
        expire_delta=timedelta(minutes=settings.access_token_expires_minutes),
    )

    return Token(access_token=access_token, token_type="bearer")
