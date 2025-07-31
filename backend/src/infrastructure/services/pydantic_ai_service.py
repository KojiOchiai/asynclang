from datetime import datetime
from typing import List, Union
from uuid import uuid4

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel

from ...domain.entities.message_parts import TextPart
from ...domain.entities.thread import MessageRequest, MessageResponse
from ...domain.services.llm_service import LLMService
from ..config.settings import settings


class PydanticAIService(LLMService):
    """PydanticAI implementation of LLM service using OpenAI."""

    def __init__(self):
        self.agent = Agent(
            model=OpenAIModel(settings.openai_model),
            system_prompt=(
                "You are a helpful AI assistant. "
                "Provide clear, concise, and helpful responses."
            ),
        )

    async def generate_assistant_response(
        self, messages: List[Union[MessageRequest, MessageResponse]]
    ) -> MessageResponse:
        """Generate assistant response using PydanticAI."""

        if not messages:
            raise ValueError("No messages provided")

        # Check if the last message is a request
        if not isinstance(messages[-1], MessageRequest):
            raise ValueError("Last message must be a MessageRequest")

        last_request = messages[-1]

        # Convert all messages to PydanticAI format for history
        pydantic_messages = []
        for msg in messages[:-1]:  # All except the last request
            if isinstance(msg, MessageRequest):
                pydantic_messages.append(msg.to_pydantic_ai_model_request())
            elif isinstance(msg, MessageResponse):
                pydantic_messages.append(msg.to_pydantic_ai_model_response())

        # Convert the last request to get user prompt
        last_pydantic_request = last_request.to_pydantic_ai_model_request()

        # Extract user prompt from the last request's parts
        user_prompt = ""
        for part in last_pydantic_request.parts:
            if hasattr(part, "content") and part.content:
                user_prompt = part.content
                break

        if not user_prompt:
            raise ValueError("No user prompt found in the last message")

        # Generate response
        result = await self.agent.run(user_prompt, message_history=pydantic_messages)

        # Create MessageResponse entity
        response = MessageResponse(
            id=uuid4(),
            thread_id=last_request.thread_id,
            created_at=datetime.now(),
            parent_id=last_request.id,
            model_name=settings.openai_model,
            timestamp=datetime.now(),
            parts=[
                TextPart(
                    id=uuid4(),
                    order_index=0,
                    created_at=datetime.now(),
                    content=result.output,
                )
            ],
        )

        return response
