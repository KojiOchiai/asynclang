from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from ...domain.value_objects.message_role import MessageRole


class MessageDto(BaseModel):
    id: UUID
    thread_id: UUID
    role: MessageRole
    content: str
    created_at: datetime
    parent_id: Optional[UUID] = None

    class Config:
        from_attributes = True


class ThreadDto(BaseModel):
    id: UUID
    title: str
    created_at: datetime
    updated_at: datetime
    messages: Optional[List[MessageDto]] = None

    class Config:
        from_attributes = True


class CreateThreadRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Title cannot be empty or only whitespace")
        return v


class CreateMessageRequest(BaseModel):
    role: MessageRole
    content: str = Field(min_length=1, max_length=8000)
    parent_id: Optional[UUID] = None

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Content cannot be empty or only whitespace")
        return v


class ThreadListResponse(BaseModel):
    threads: List[ThreadDto]


class MessageListResponse(BaseModel):
    messages: List[MessageDto]
