from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.agent import Agent, initialize_agent
from app.api.dtos import ThreadDto
from app.db.crud import ThreadCRUD
from app.db.database import get_async_session
from app.entities.thread import Thread

router = APIRouter(prefix="/threads", tags=["threads"])


async def get_thread_crud(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> ThreadCRUD:
    return ThreadCRUD(session)


@router.post("/", response_model=ThreadDto)
async def create_thread(
    title: Annotated[str, Field(min_length=1, max_length=100)],
    service: Annotated[ThreadCRUD, Depends(get_thread_crud)],
):
    thread = await service.create_thread(title)
    return ThreadDto.from_model(thread)


@router.get("/", response_model=list[ThreadDto])
async def get_all_threads(
    service: Annotated[ThreadCRUD, Depends(get_thread_crud)],
):
    threads = await service.get_all_threads()
    return [ThreadDto.from_model(thread) for thread in threads]


@router.get("/{thread_id}", response_model=ThreadDto)
async def get_thread_by_id(
    thread_id: UUID,
    service: Annotated[ThreadCRUD, Depends(get_thread_crud)],
):
    thread = await service.get_thread_by_id(thread_id)
    if thread is None:
        raise HTTPException(status_code=404, detail="Thread not found")
    return ThreadDto.from_model(thread)


@router.delete("/{thread_id}")
async def delete_thread(
    thread_id: UUID,
    service: Annotated[ThreadCRUD, Depends(get_thread_crud)],
):
    success = await service.delete_thread(thread_id)
    if not success:
        raise HTTPException(status_code=404, detail="Thread not found")
    return {"message": "Thread deleted successfully"}


async def run_agent_with_thread(
    agent: Agent,
    thread_id: UUID,
    user_prompt: str,
    thread: Thread,
    service: ThreadCRUD,
):
    # overwrite system prompt
    system_prompt = agent._system_prompts[0]
    for message in thread.messages:
        if message.kind == "request":
            for part in message.parts:
                if part.part_kind == "system-prompt":
                    part.content = system_prompt
                    break

    result = await agent.run(user_prompt, message_history=thread.messages)
    await service.add_messages_to_thread(thread_id, result.new_messages())
    return result.output


@router.post("/{thread_id}/messages")
async def create_message(
    thread_id: UUID,
    user_prompt: str,
    service: Annotated[ThreadCRUD, Depends(get_thread_crud)],
    background_tasks: BackgroundTasks,
):
    thread = await service.get_thread_by_id(thread_id)
    if thread is None:
        raise HTTPException(status_code=404, detail="Thread not found")
    try:
        agent = await initialize_agent(thread_id)
        background_tasks.add_task(
            run_agent_with_thread, agent, thread_id, user_prompt, thread, service
        )
        return {"message": "Request is being processed in the background"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("webhook/mcp")
async def webhook_handler(
    thread_id: UUID,
    mcp_name: str,
    content: str,
    service: Annotated[ThreadCRUD, Depends(get_thread_crud)],
    background_tasks: BackgroundTasks,
):
    thread = await service.get_thread_by_id(thread_id)
    if thread is None:
        raise HTTPException(status_code=404, detail="Thread not found")
    try:
        agent = await initialize_agent(thread_id)
        prompt_json = f"{{'mcp_name': '{mcp_name}', 'content': '{content}'}}"
        background_tasks.add_task(
            run_agent_with_thread, agent, thread_id, prompt_json, thread, service
        )
        return {"message": "Request is being processed in the background"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
