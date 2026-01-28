import uuid
from datetime import datetime
from sqlmodel import SQLModel, Field
from typing import Optional


class UserBase(SQLModel):
    """Base user model with shared fields."""

    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)
    full_name: Optional[str] = None
    disabled: bool = Field(default=False)


class User(UserBase, table=True):
    """Database model for users table."""

    __tablename__ = "users"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class UserCreate(SQLModel):
    """Schema for creating a new user."""

    username: str
    email: str
    password: str
    full_name: Optional[str] = None


class UserRead(UserBase):
    """Schema for reading user data (excludes password)."""

    id: uuid.UUID
    created_at: datetime
