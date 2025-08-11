from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStreamableHTTP
from pydantic_ai.models.openai import OpenAIResponsesModel, OpenAIResponsesModelSettings

from app.config.config import settings

server = MCPServerStreamableHTTP("http://localhost:8000/mcp")

if settings.openai_model == "gpt-4o":
    agent = Agent(
        "openai:gpt-4o",
        system_prompt="You are a helpful assistant. Return message with three ! marks.",
        toolsets=[server],
    )
elif settings.openai_model == "o3":
    model = OpenAIResponsesModel("o3")
    model_settings = OpenAIResponsesModelSettings(
        openai_reasoning_effort="low", openai_reasoning_summary="detailed"
    )
    agent = Agent(
        model,
        system_prompt="You are a helpful assistant. Return message with three ! marks.",
        model_settings=model_settings,
        toolsets=[server],
    )
else:
    raise ValueError(f"Unsupported OpenAI model: {settings.openai_model}")
