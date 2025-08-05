from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Union
from uuid import UUID

from pydantic_ai.messages import ModelRequest, ModelResponse, Usage

from .message_parts import TextPart, ToolCallPart, ToolReturnPart, UserPromptPart


@dataclass
class Thread:
    """Thread entity representing a conversation thread."""

    id: UUID
    title: str
    created_at: datetime
    updated_at: datetime
    messages: List[Union["MessageRequest", "MessageResponse"]] = field(
        default_factory=list
    )

    def add_message(self, message: Union["MessageRequest", "MessageResponse"]) -> None:
        """Add a message to the thread."""
        if self.messages is None:
            self.messages = []
        self.messages.append(message)
        self.updated_at = datetime.now()

    def to_pydantic_ai_thread(self) -> list[ModelRequest | ModelResponse]:
        """Convert thread messages to PydanticAI format."""
        if not self.messages:
            return []

        pydantic_messages: list[ModelRequest | ModelResponse] = []
        for message in self.messages:
            if isinstance(message, MessageRequest):
                pydantic_messages.append(message.to_pydantic_ai_model_request())
            elif isinstance(message, MessageResponse):
                pydantic_messages.append(message.to_pydantic_ai_model_response())

        return pydantic_messages

    def get_last_message_path(self) -> list[Union["MessageRequest", "MessageResponse"]]:
        """Get the path to the last message following parent-child relationships."""
        if not self.messages:
            return []

        # Find the message with the latest created_at timestamp
        last_message = max(self.messages, key=lambda msg: msg.created_at)

        # Build path from root to last message
        path: list[MessageRequest | MessageResponse] = []
        current: MessageRequest | MessageResponse | None = last_message

        # Trace back to root following parent_id chain
        while current is not None:
            path.insert(0, current)  # Insert at beginning to build path from root
            if current.parent_id is None:
                break
            # Find parent message
            current = next(
                (msg for msg in self.messages if msg.id == current.parent_id), None
            )

        return path


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
    parts: list[UserPromptPart] = field(default_factory=list)

    def to_pydantic_ai_model_request(self) -> ModelRequest:
        """Convert to PydanticAI ModelRequest."""

        # Convert all parts to PydanticAI format
        pydantic_parts: list = [part.to_pydantic_ai_part() for part in self.parts]

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
    parts: list[ToolReturnPart | TextPart | ToolCallPart] = field(default_factory=list)

    def to_pydantic_ai_model_response(self) -> ModelResponse:
        """Convert to PydanticAI ModelResponse."""

        # Convert all parts to PydanticAI format
        pydantic_parts: list = [part.to_pydantic_ai_part() for part in self.parts]

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
