from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel


class MessageDto(BaseModel):
    id: UUID
    thread_id: UUID
    role: str
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
    title: str


class CreateMessageRequest(BaseModel):
    role: str
    content: str
    parent_id: Optional[UUID] = None


class ThreadListResponse(BaseModel):
    threads: List[ThreadDto]


class MessageListResponse(BaseModel):
    messages: List[MessageDto]
