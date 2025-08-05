import asyncio
from datetime import datetime
from uuid import uuid4

from src.domain.entities.message_parts import (
    TextPart,
    ToolCallPart,
    ToolReturnPart,
    UserPromptPart,
)
from src.domain.entities.thread import MessageRequest, MessageResponse, Thread
from src.infrastructure.services.pydantic_ai_service import PydanticAIOpenAIService


async def main():
    # Create a Thread instance
    thread = Thread(
        id=uuid4(),
        title="Test Thread",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    # Create a message request
    message_request = MessageRequest(
        id=uuid4(),
        thread_id=thread.id,
        created_at=datetime.now(),
        parts=[
            UserPromptPart(
                id=uuid4(),
                order_index=0,
                created_at=datetime.now(),
                content="Hello, how are you today?",
            )
        ],
    )

    # Add message to thread
    thread.add_message(message_request)

    # Create PydanticAI service instance
    llm_service = PydanticAIOpenAIService()

    # Generate response
    response = await llm_service.generate_assistant_response(
        thread.get_last_message_path()
    )

    # Add response to thread
    thread.add_message(response)

    print(f"Thread ID: {thread.id}")
    for message in thread.messages:
        if isinstance(message, MessageRequest):
            print(f"Request: {message.parts[0].content}")
        elif isinstance(message, MessageResponse):
            for part in message.parts:
                if isinstance(part, TextPart):
                    print(f"Response: {part.content}")
                elif isinstance(part, ToolCallPart):
                    print(f"Tool Call: {part.tool_name} with args {part.args}")
                elif isinstance(part, ToolReturnPart):
                    print(f"Tool Return: {part.content}")


if __name__ == "__main__":
    asyncio.run(main())
