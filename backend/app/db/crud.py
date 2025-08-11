from datetime import datetime
from uuid import UUID, uuid4

from pydantic_ai.messages import ModelMessage, ModelMessagesTypeAdapter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.entities.thread import Thread

from .models import MessageModel, ThreadModel


class ThreadCRUD:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create_thread(self, title: str) -> Thread:
        now = datetime.now()
        thread_model = ThreadModel(
            id=str(uuid4()),
            title=title,
            created_at=now,
            updated_at=now,
        )
        self._session.add(thread_model)
        await self._session.commit()
        await self._session.refresh(thread_model)

        return self._model_to_entity(thread_model, include_messages=False)

    async def get_thread_by_id(self, thread_id: UUID) -> Thread | None:
        result = await self._session.execute(
            select(ThreadModel)
            .options(selectinload(ThreadModel.messages))
            .where(ThreadModel.id == str(thread_id))
        )
        thread_model = result.scalar_one_or_none()

        if thread_model is None:
            return None

        return self._model_to_entity(thread_model, include_messages=True)

    async def get_all_threads(self) -> list[Thread]:
        result = await self._session.execute(
            select(ThreadModel)
            .options(selectinload(ThreadModel.messages).defer("*"))
            .order_by(ThreadModel.updated_at.desc())
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

    async def add_messages_to_thread(
        self, thread_id: UUID, messages: list[ModelMessage]
    ) -> Thread:
        result = await self._session.execute(
            select(ThreadModel).where(ThreadModel.id == str(thread_id))
        )
        thread_model = result.scalar_one_or_none()

        if thread_model is None:
            raise ValueError(f"Thread with id {thread_id} does not exist.")

        content = ModelMessagesTypeAdapter.dump_json(messages)

        message_model = MessageModel(
            id=str(uuid4()),
            thread_id=str(thread_id),
            content=content,
            created_at=datetime.now(),
        )
        thread_model.messages.append(message_model)

        await self._session.commit()
        await self._session.refresh(thread_model)

        return self._model_to_entity(thread_model, include_messages=True)

    def _model_to_entity(
        self, model: ThreadModel, include_messages: bool = False
    ) -> Thread:
        messages: list[ModelMessage] = []
        if include_messages and hasattr(model, "_sa_instance_state"):
            # Only access messages if they were explicitly loaded
            for message_model in model.messages:
                message = ModelMessagesTypeAdapter.validate_json(message_model.content)
                messages.extend(message)

        return Thread(
            id=UUID(model.id),
            title=model.title,
            created_at=model.created_at,
            updated_at=model.updated_at,
            messages=messages,
        )
