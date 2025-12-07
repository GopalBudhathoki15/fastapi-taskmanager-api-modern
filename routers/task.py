from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Annotated
from schemas import TaskCreate, TaskOut, TaskUpdate
from database import get_db
from security import get_current_user
import models

router = APIRouter()


@router.get("", response_model=list[TaskOut])
def list_tasks(
    current_user: Annotated[models.User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    stmt = select(models.Task).where(models.Task.user_id == current_user.id)
    db_tasks = db.execute(stmt).scalars().all()

    return db_tasks


@router.post("", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
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


@router.patch("/{task_id}", response_model=TaskOut)
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


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
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
