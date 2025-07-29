from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ...domain.entities import Message, Thread
from ...domain.repositories import MessageRepository, ThreadRepository
from ..database import MessageModel, ThreadModel


class ThreadRepositoryImpl(ThreadRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create_thread(self, thread: Thread) -> Thread:
        thread_model = ThreadModel(
            id=str(thread.id),
            title=thread.title,
            created_at=thread.created_at,
            updated_at=thread.updated_at,
        )
        self._session.add(thread_model)
        await self._session.commit()
        await self._session.refresh(thread_model)

        return self._model_to_entity(thread_model, include_messages=False)

    async def get_thread_by_id(self, thread_id: UUID) -> Optional[Thread]:
        result = await self._session.execute(
            select(ThreadModel)
            .options(selectinload(ThreadModel.messages))
            .where(ThreadModel.id == str(thread_id))
        )
        thread_model = result.scalar_one_or_none()

        if thread_model is None:
            return None

        return self._model_to_entity(thread_model, include_messages=True)

    async def get_all_threads(self) -> List[Thread]:
        result = await self._session.execute(
            select(ThreadModel).order_by(ThreadModel.updated_at.desc())
        )
        thread_models = result.scalars().all()

        return [
            self._model_to_entity(model, include_messages=False)
            for model in thread_models
        ]

    async def update_thread(self, thread: Thread) -> Thread:
        result = await self._session.execute(
            select(ThreadModel).where(ThreadModel.id == str(thread.id))
        )
        thread_model = result.scalar_one()

        thread_model.title = thread.title
        thread_model.updated_at = thread.updated_at

        await self._session.commit()
        await self._session.refresh(thread_model)

        return self._model_to_entity(thread_model, include_messages=False)

    async def delete_thread(self, thread_id: UUID) -> bool:
        result = await self._session.execute(
            select(ThreadModel).where(ThreadModel.id == str(thread_id))
        )
        thread_model = result.scalar_one_or_none()

        if thread_model is None:
            return False

        await self._session.delete(thread_model)
        await self._session.commit()
        return True

    def _model_to_entity(
        self, model: ThreadModel, include_messages: bool = False
    ) -> Thread:
        from uuid import UUID

        messages = []
        if include_messages and hasattr(model, "_sa_instance_state"):
            # Only access messages if they were explicitly loaded
            if "messages" in model.__dict__:
                messages = [
                    Message(
                        id=UUID(msg.id),
                        thread_id=UUID(msg.thread_id),
                        role=msg.role,
                        content=msg.content,
                        created_at=msg.created_at,
                    )
                    for msg in model.messages
                ]

        return Thread(
            id=UUID(model.id),
            title=model.title,
            created_at=model.created_at,
            updated_at=model.updated_at,
            messages=messages if include_messages else None,
        )


class MessageRepositoryImpl(MessageRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create_message(self, message: Message) -> Message:
        message_model = MessageModel(
            id=str(message.id),
            thread_id=str(message.thread_id),
            role=message.role,
            content=message.content,
            created_at=message.created_at,
        )
        self._session.add(message_model)
        await self._session.commit()
        await self._session.refresh(message_model)

        return self._model_to_entity(message_model)

    async def get_messages_by_thread_id(self, thread_id: UUID) -> List[Message]:
        result = await self._session.execute(
            select(MessageModel)
            .where(MessageModel.thread_id == str(thread_id))
            .order_by(MessageModel.created_at.asc())
        )
        message_models = result.scalars().all()

        return [self._model_to_entity(model) for model in message_models]

    async def get_message_by_id(self, message_id: UUID) -> Optional[Message]:
        result = await self._session.execute(
            select(MessageModel).where(MessageModel.id == str(message_id))
        )
        message_model = result.scalar_one_or_none()

        if message_model is None:
            return None

        return self._model_to_entity(message_model)

    def _model_to_entity(self, model: MessageModel) -> Message:
        from uuid import UUID

        return Message(
            id=UUID(model.id),
            thread_id=UUID(model.thread_id),
            role=model.role,
            content=model.content,
            created_at=model.created_at,
        )
