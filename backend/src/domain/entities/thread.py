from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic_ai.messages import ModelRequest, ModelResponse, Usage

from .message_parts import RequestPart, ResponsePart


@dataclass
class Thread:
    """Thread entity representing a conversation thread."""

    id: UUID
    title: str
    created_at: datetime
    updated_at: datetime
    messages: Optional[List["Message"]] = None

    def add_message(self, message: "Message") -> None:
        """Add a message to the thread."""
        if self.messages is None:
            self.messages = []
        self.messages.append(message)
        self.updated_at = datetime.now()


@dataclass
class Message:
    """Base message entity supporting PydanticAI structure."""

    id: UUID
    thread_id: UUID
    created_at: datetime
    parent_id: Optional[UUID] = None  # Parent message ID for tree structure


@dataclass
class MessageRequest(Message):
    """Message request entity (ModelRequest in PydanticAI)."""

    instructions: Optional[str] = None
    parts: List[RequestPart] = field(default_factory=list)

    def to_pydantic_ai_model_request(self) -> ModelRequest:
        """Convert to PydanticAI ModelRequest."""

        # Convert all parts to PydanticAI format
        pydantic_parts = [part.to_pydantic_ai_part() for part in self.parts]

        return ModelRequest(
            parts=pydantic_parts, instructions=self.instructions, kind="request"
        )


@dataclass
class MessageResponse(Message):
    """Message response entity (ModelResponse in PydanticAI)."""

    model_name: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    usage_tokens: Optional[int] = None
    vendor_details: Optional[dict] = None
    parts: List[ResponsePart] = field(default_factory=list)

    def to_pydantic_ai_model_response(self) -> ModelResponse:
        """Convert to PydanticAI ModelResponse."""

        # Convert all parts to PydanticAI format
        pydantic_parts = [part.to_pydantic_ai_part() for part in self.parts]

        # Create usage object if token count is available
        usage = Usage(
            requests=1,
            request_tokens=self.usage_tokens if self.usage_tokens else 0,
            response_tokens=0,  # Would need to track separately
            total_tokens=self.usage_tokens,
        )

        return ModelResponse(
            parts=pydantic_parts,
            usage=usage,
            model_name=self.model_name,
            timestamp=self.timestamp,
            vendor_details=self.vendor_details,
        )
