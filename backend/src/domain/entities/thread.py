from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from ..value_objects.message_role import MessageRole


@dataclass
class Thread:
    id: UUID
    title: str
    created_at: datetime
    updated_at: datetime
    messages: Optional[List["Message"]] = None

    def add_message(self, message: "Message") -> None:
        if self.messages is None:
            self.messages = []
        self.messages.append(message)
        self.updated_at = datetime.utcnow()


@dataclass
class Message:
    id: UUID
    thread_id: UUID
    role: MessageRole
    content: str
    created_at: datetime
    parent_id: Optional[UUID] = None  # Parent message ID for tree structure
