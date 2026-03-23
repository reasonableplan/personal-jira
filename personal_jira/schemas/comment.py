from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator

VALID_COMMENT_TYPES = {"general", "review", "feedback"}
DEFAULT_COMMENT_TYPE = "general"
MIN_CONTENT_LENGTH = 1
MIN_AUTHOR_LENGTH = 1


class CommentCreate(BaseModel):
    author: str
    content: str
    comment_type: str = DEFAULT_COMMENT_TYPE

    @field_validator("author")
    @classmethod
    def author_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("author must not be empty")
        return v

    @field_validator("content")
    @classmethod
    def content_not_empty(cls, v: str) -> str:
        if len(v) < MIN_CONTENT_LENGTH:
            raise ValueError("content must not be empty")
        return v

    @field_validator("comment_type")
    @classmethod
    def validate_comment_type(cls, v: str) -> str:
        if v not in VALID_COMMENT_TYPES:
            raise ValueError(f"comment_type must be one of {VALID_COMMENT_TYPES}")
        return v


class CommentUpdate(BaseModel):
    content: Optional[str] = None
    comment_type: Optional[str] = None

    @field_validator("content")
    @classmethod
    def content_not_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and len(v) < MIN_CONTENT_LENGTH:
            raise ValueError("content must not be empty")
        return v

    @field_validator("comment_type")
    @classmethod
    def validate_comment_type(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in VALID_COMMENT_TYPES:
            raise ValueError(f"comment_type must be one of {VALID_COMMENT_TYPES}")
        return v


class CommentResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    issue_id: uuid.UUID
    author: str
    content: str
    comment_type: str
    created_at: datetime
    updated_at: datetime
