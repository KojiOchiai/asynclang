from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from ..entities import Message, Thread


class ThreadRepository(ABC):
    @abstractmethod
    async def create_thread(self, thread: Thread) -> Thread:
        pass

    @abstractmethod
    async def get_thread_by_id(self, thread_id: UUID) -> Optional[Thread]:
        pass

    @abstractmethod
    async def get_all_threads(self) -> List[Thread]:
        pass

    @abstractmethod
    async def update_thread(self, thread: Thread) -> Thread:
        pass

    @abstractmethod
    async def delete_thread(self, thread_id: UUID) -> bool:
        pass


class MessageRepository(ABC):
    @abstractmethod
    async def create_message(self, message: Message) -> Message:
        pass

    @abstractmethod
    async def get_messages_by_thread_id(self, thread_id: UUID) -> List[Message]:
        pass

    @abstractmethod
    async def get_message_by_id(self, message_id: UUID) -> Optional[Message]:
        pass
