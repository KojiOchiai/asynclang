from abc import ABC, abstractmethod

from ..entities.thread import MessageRequest, MessageResponse


class LLMService(ABC):
    """Abstract interface for LLM communication services."""

    @abstractmethod
    async def generate_assistant_response(
        self, messages: list[MessageRequest | MessageResponse]
    ) -> MessageResponse:
        """
        Generate an assistant response based on conversation history.

        Args:
            messages: List of conversation messages (requests and responses)

        Returns:
            Generated assistant response as MessageResponse entity
        """
        pass
