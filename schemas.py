# schemas.py
from pydantic import BaseModel, EmailStr, ConfigDict


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserOut(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class TaskBase(BaseModel):
    title: str


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: str | None = None
    is_completed: bool | None = None


class TaskOut(TaskBase):
    id: int
    is_completed: bool
    user_id: int

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str
