from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional
from uuid import UUID

# Import specific PydanticAI types
from pydantic_ai.messages import SystemPromptPart as PydanticSystemPromptPart
from pydantic_ai.messages import TextPart as PydanticTextPart
from pydantic_ai.messages import ThinkingPart as PydanticThinkingPart
from pydantic_ai.messages import ToolCallPart as PydanticToolCallPart
from pydantic_ai.messages import ToolReturnPart as PydanticToolReturnPart
from pydantic_ai.messages import UserPromptPart as PydanticUserPromptPart


@dataclass
class RequestPart(ABC):
    """Base class for all request message parts."""

    id: UUID
    order_index: int
    created_at: datetime
    content: str

    @abstractmethod
    def to_pydantic_ai_part(self) -> Any:
        """Convert to PydanticAI part format."""
        pass


@dataclass
class SystemPromptPart(RequestPart):
    """System prompt part for model requests."""

    dynamic_ref: Optional[str] = None

    def to_pydantic_ai_part(self) -> PydanticSystemPromptPart:
        """Convert to PydanticAI SystemPromptPart."""
        return PydanticSystemPromptPart(content=self.content)


@dataclass
class UserPromptPart(RequestPart):
    """User prompt part for model requests."""

    metadata: Optional[dict] = None

    def to_pydantic_ai_part(self) -> PydanticUserPromptPart:
        """Convert to PydanticAI UserPromptPart."""
        return PydanticUserPromptPart(content=self.content)


@dataclass
class ResponsePart(ABC):
    """Base class for all response message parts."""

    id: UUID
    order_index: int
    created_at: datetime

    @abstractmethod
    def to_pydantic_ai_part(self) -> Any:
        """Convert to PydanticAI part format."""
        pass


@dataclass
class TextPart(ResponsePart):
    """Text response part from model."""

    content: str

    def to_pydantic_ai_part(self) -> PydanticTextPart:
        """Convert to PydanticAI TextPart."""
        return PydanticTextPart(content=self.content)


@dataclass
class ToolCallPart(ResponsePart):
    """Tool call part in model response."""

    tool_name: str
    args: dict
    tool_call_id: str

    def to_pydantic_ai_part(self) -> PydanticToolCallPart:
        """Convert to PydanticAI ToolCallPart."""
        return PydanticToolCallPart(
            tool_name=self.tool_name, args=self.args, tool_call_id=self.tool_call_id
        )


@dataclass
class ToolReturnPart(ResponsePart):
    """Tool execution result part."""

    tool_name: str
    content: str
    tool_call_id: str
    metadata: Optional[dict] = None

    def to_pydantic_ai_part(self) -> PydanticToolReturnPart:
        """Convert to PydanticAI ToolReturnPart."""
        return PydanticToolReturnPart(
            tool_name=self.tool_name,
            content=self.content,
            tool_call_id=self.tool_call_id,
        )


@dataclass
class ThinkingPart(ResponsePart):
    """Model's thinking process part."""

    content: str

    def to_pydantic_ai_part(self) -> PydanticThinkingPart:
        """Convert to PydanticAI ThinkingPart."""
        return PydanticThinkingPart(content=self.content)
