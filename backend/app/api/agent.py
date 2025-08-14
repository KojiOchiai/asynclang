from uuid import UUID

from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStreamableHTTP
from pydantic_ai.models.openai import OpenAIResponsesModel, OpenAIResponsesModelSettings

from app.config.config import settings

mcp_servers = [MCPServerStreamableHTTP(url) for url in settings.mcp_server_urls]


async def initialize_agent(thread_id: UUID):
    thread_url = f"http://localhost:8000/mcp/{thread_id}"
    prmpt = (
        f"You are a helpful assistant with thread_url: {thread_url}. "
        "Return message with five ! marks."
    )
    if settings.openai_model == "gpt-4o":
        return Agent(
            "openai:gpt-4o",
            system_prompt=prmpt,
            toolsets=mcp_servers,
        )
    elif settings.openai_model == "o3":
        model = OpenAIResponsesModel("o3")
        model_settings = OpenAIResponsesModelSettings(
            openai_reasoning_effort="low", openai_reasoning_summary="detailed"
        )
        return Agent(
            model,
            system_prompt=prmpt,
            model_settings=model_settings,
            toolsets=mcp_servers,
        )
    else:
        raise ValueError(f"Unsupported OpenAI model: {settings.openai_model}")
