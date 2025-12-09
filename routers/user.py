# routers.user.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Annotated
from schemas import UserOut, UserCreate
from database import get_db
import models

router = APIRouter()


@router.get("", response_model=list[UserOut])
def list_users(db: Annotated[Session, Depends(get_db)]):
    db_users = db.execute(select(models.User)).scalars().all()

    return db_users


@router.get("/{user_id}", response_model=UserOut)
def get_user_by_id(user_id: int, db: Annotated[Session, Depends(get_db)]):
    db_user = db.execute(
        select(models.User).where(models.User.id == user_id)
    ).scalar_one_or_none()

    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return db_user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Annotated[Session, Depends(get_db)]):
    db_user = db.execute(
        select(models.User).where(models.User.id == user_id)
    ).scalar_one_or_none()

    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    db.delete(db_user)
    db.commit()
    return None
