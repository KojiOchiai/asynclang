from enum import Enum


class MessageRole(str, Enum):
    """Enumeration for message roles in the chat system."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
