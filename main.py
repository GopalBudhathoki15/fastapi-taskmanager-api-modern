from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Annotated
from schemas import Token, UserOut, UserCreate, TaskCreate, TaskUpdate, TaskOut
from database import get_db
import models
from sqlalchemy import select
from security import (
    verify_password,
    create_access_token,
    hash_password,
    get_current_user,
)
from config import settings
from datetime import timedelta

app = FastAPI()


@app.post("/login", response_model=Token)
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


@app.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
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


@app.get("/tasks", response_model=list[TaskOut])
def list_tasks(
    current_user: Annotated[models.User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    stmt = select(models.Task).where(models.Task.user_id == current_user.id)
    db_tasks = db.execute(stmt).scalars().all()

    return db_tasks


@app.post("/tasks", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(
    current_user: Annotated[models.User, Depends(get_current_user)],
    task: TaskCreate,
    db: Annotated[Session, Depends(get_db)],
):
    db_task = models.Task(**task.model_dump(), user_id=current_user.id)

    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    return db_task


@app.patch("/tasks/{task_id}", response_model=TaskOut)
def update_task(
    current_user: Annotated[models.User, Depends(get_current_user)],
    task_id: int,
    task: TaskUpdate,
    db: Annotated[Session, Depends(get_db)],
):
    db_task = db.execute(
        select(models.Task).where(
            models.Task.id == task_id, models.Task.user_id == current_user.id
        )
    ).scalar_one_or_none()

    if db_task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    update_data = task.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_task, key, value)

    db.commit()
    db.refresh(db_task)

    return db_task


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    current_user: Annotated[models.User, Depends(get_current_user)],
    task_id: int,
    db: Annotated[Session, Depends(get_db)],
):
    db_task = db.execute(
        select(models.Task).where(
            models.Task.id == task_id, models.Task.user_id == current_user.id
        )
    ).scalar_one_or_none()

    if db_task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    db.delete(db_task)
    db.commit()

    return None
