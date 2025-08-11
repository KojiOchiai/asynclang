from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from pydantic_ai.messages import ModelMessage


@dataclass
class Thread:
    """Thread entity representing a conversation thread."""

    id: UUID
    title: str
    created_at: datetime
    updated_at: datetime
    messages: list[ModelMessage] = field(default_factory=list)
