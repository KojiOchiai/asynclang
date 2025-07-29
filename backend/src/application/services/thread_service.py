from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from ...domain.entities import Message, Thread
from ...domain.repositories import MessageRepository, ThreadRepository
from ..dtos import (
    CreateMessageRequest,
    CreateThreadRequest,
    MessageDto,
    MessageListResponse,
    ThreadDto,
    ThreadListResponse,
)


class ThreadService:
    def __init__(
        self,
        thread_repository: ThreadRepository,
        message_repository: MessageRepository,
    ):
        self._thread_repository = thread_repository
        self._message_repository = message_repository

    async def create_thread(self, request: CreateThreadRequest) -> ThreadDto:
        thread_id = uuid4()
        now = datetime.utcnow()

        thread = Thread(
            id=thread_id,
            title=request.title,
            created_at=now,
            updated_at=now,
        )

        created_thread = await self._thread_repository.create_thread(thread)
        return ThreadDto.model_validate(created_thread)

    async def get_thread_by_id(self, thread_id: UUID) -> Optional[ThreadDto]:
        thread = await self._thread_repository.get_thread_by_id(thread_id)
        if thread is None:
            return None

        messages = await self._message_repository.get_messages_by_thread_id(thread_id)
        thread.messages = messages

        return ThreadDto.model_validate(thread)

    async def get_all_threads(self) -> ThreadListResponse:
        threads = await self._thread_repository.get_all_threads()
        thread_dtos = [ThreadDto.model_validate(thread) for thread in threads]
        return ThreadListResponse(threads=thread_dtos)

    async def delete_thread(self, thread_id: UUID) -> bool:
        return await self._thread_repository.delete_thread(thread_id)

    async def create_message(
        self, thread_id: UUID, request: CreateMessageRequest
    ) -> MessageDto:
        thread = await self._thread_repository.get_thread_by_id(thread_id)
        if thread is None:
            raise ValueError(f"Thread with id {thread_id} not found")

        message_id = uuid4()
        now = datetime.utcnow()

        message = Message(
            id=message_id,
            thread_id=thread_id,
            role=request.role,
            content=request.content,
            created_at=now,
        )

        created_message = await self._message_repository.create_message(message)

        thread.updated_at = now
        await self._thread_repository.update_thread(thread)

        return MessageDto.model_validate(created_message)

    async def get_messages_by_thread_id(self, thread_id: UUID) -> MessageListResponse:
        messages = await self._message_repository.get_messages_by_thread_id(thread_id)
        message_dtos = [MessageDto.model_validate(message) for message in messages]
        return MessageListResponse(messages=message_dtos)
