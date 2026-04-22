"""Pydantic v2 schemas for User-related requests and responses."""

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    """Request body for user registration."""

    email: EmailStr
    password: str = Field(min_length=8)


class UserLogin(BaseModel):
    """Request body for user login."""

    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """User data returned to the client (never exposes hashed_password)."""

    id: uuid.UUID
    email: EmailStr
    is_active: bool
    free_analyses_used: int
    stripe_customer_id: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    """JWT token response."""

    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Payload decoded from a JWT."""

    user_id: uuid.UUID | None = None
