from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ...application.dtos import (
    CreateMessageRequest,
    CreateThreadRequest,
    MessageListResponse,
    ThreadDto,
    ThreadListResponse,
)
from ...application.services import ThreadService
from ...infrastructure.database import get_async_session
from ...infrastructure.repositories import MessageRepositoryImpl, ThreadRepositoryImpl

router = APIRouter(prefix="/threads", tags=["threads"])


async def get_thread_service(session: Annotated[AsyncSession, Depends(get_async_session)]) -> ThreadService:
    thread_repository = ThreadRepositoryImpl(session)
    message_repository = MessageRepositoryImpl(session)
    return ThreadService(thread_repository, message_repository)


@router.post("/", response_model=ThreadDto)
async def create_thread(
    request: CreateThreadRequest,
    service: Annotated[ThreadService, Depends(get_thread_service)],
):
    return await service.create_thread(request)


@router.get("/", response_model=ThreadListResponse)
async def get_all_threads(
    service: Annotated[ThreadService, Depends(get_thread_service)],
):
    return await service.get_all_threads()


@router.get("/{thread_id}", response_model=ThreadDto)
async def get_thread_by_id(
    thread_id: UUID,
    service: Annotated[ThreadService, Depends(get_thread_service)],
):
    thread = await service.get_thread_by_id(thread_id)
    if thread is None:
        raise HTTPException(status_code=404, detail="Thread not found")
    return thread


@router.delete("/{thread_id}")
async def delete_thread(
    thread_id: UUID,
    service: Annotated[ThreadService, Depends(get_thread_service)],
):
    success = await service.delete_thread(thread_id)
    if not success:
        raise HTTPException(status_code=404, detail="Thread not found")
    return {"message": "Thread deleted successfully"}


@router.post("/{thread_id}/messages", response_model=ThreadDto)
async def create_message(
    thread_id: UUID,
    request: CreateMessageRequest,
    service: Annotated[ThreadService, Depends(get_thread_service)],
):
    try:
        await service.create_message(thread_id, request)
        thread = await service.get_thread_by_id(thread_id)
        return thread
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{thread_id}/messages", response_model=MessageListResponse)
async def get_messages_by_thread_id(
    thread_id: UUID,
    service: Annotated[ThreadService, Depends(get_thread_service)],
):
    return await service.get_messages_by_thread_id(thread_id)
