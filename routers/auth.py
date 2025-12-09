# routers.auth.py
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


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Annotated[Session, Depends(get_db)]):
    existing_user = db.execute(
        select(models.User).where(
            (models.User.username == user.username) | (models.User.email == user.email)
        )
    ).scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already in use.",
        )

    hashed_password = hash_password(user.password)
    db_user = models.User(
        **user.model_dump(exclude={"password"}), hashed_password=hashed_password
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


@router.post("/login", response_model=Token)
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
