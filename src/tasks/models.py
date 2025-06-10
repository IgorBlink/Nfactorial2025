from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, ConfigDict


# User models
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserInDB(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    username: str
    email: str
    is_active: bool
    created_at: datetime


class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    username: str
    email: str
    is_active: bool


# Task models
class TaskCreate(BaseModel):
    title: str
    description: str
    deadline: Optional[datetime] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
    deadline: Optional[datetime] = None


class Task(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    title: str
    description: str
    completed: bool
    deadline: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    owner_id: int


# Auth models
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
