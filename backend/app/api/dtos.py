from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel
from pydantic_ai.messages import ModelRequestPart, ModelResponsePart

from app.entities.thread import Thread


class MessageRole(str, Enum):
    """Enumeration for message roles in the chat system."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    THINKING = "thinking"
    TOOLCALL = "tool-call"
    TOOLRETURN = "tool-return"
    RETRY = "retry"


class MessageDto(BaseModel):
    role: MessageRole
    content: str | None = None

    class Config:
        from_attributes = True

    @classmethod
    def from_part(cls, part: ModelRequestPart | ModelResponsePart) -> "MessageDto":
        """Create a MessageDto from a Pydantic AI message part."""
        if part.part_kind == "system-prompt":
            role = MessageRole.SYSTEM
        elif part.part_kind == "user-prompt":
            role = MessageRole.USER
        elif part.part_kind == "text":
            role = MessageRole.ASSISTANT
        elif part.part_kind == "thinking":
            role = MessageRole.THINKING
        elif part.part_kind == "tool-call":
            role = MessageRole.TOOLCALL
        elif part.part_kind == "tool-return":
            role = MessageRole.TOOLRETURN
        elif part.part_kind == "retry-prompt":
            role = MessageRole.RETRY

        content = None
        if part.part_kind == "tool-call":
            content = f"Tool call: {part.tool_name} with args {part.args}"
        elif part.part_kind == "tool-return":
            content = f"{part.tool_name}: {part.content}"
        elif hasattr(part, "content") and part.content is not None:
            content = str(part.content)

        return cls(
            role=role,
            content=content,
        )


class ThreadDto(BaseModel):
    id: UUID
    title: str
    created_at: datetime
    updated_at: datetime
    messages: Optional[List[MessageDto]] = None

    class Config:
        from_attributes = True

    @classmethod
    def from_model(cls, thread: Thread) -> "ThreadDto":
        """Create a ThreadDto from a Thread entity."""
        messages = []
        for message in thread.messages:
            for part in message.parts:
                messages.append(MessageDto.from_part(part))
        return cls(
            id=thread.id,
            title=thread.title,
            created_at=thread.created_at,
            updated_at=thread.updated_at,
            messages=messages,
        )
